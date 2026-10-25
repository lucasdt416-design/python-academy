"""Rate limits for write endpoints and sign-in (backlog SEC-01).

Counters live in this process's memory: one entry per (rule, who, window) holding only a keyed
hash of the user ID or IP address, the window's start and a count. They never hold request
bodies, learner code or message text, and they are not written to disk or the database, so they
reset when the API restarts or redeploys. That is acceptable for a speed bump against abuse on a
single Render instance; see docs/handoffs/2026-10-25-06-rate-limits-and-headers.md for the
trade-off and what changes if the API ever runs on more than one instance.
"""
import hashlib
import hmac
import ipaddress
import logging
import math
import secrets
import threading
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request

log = logging.getLogger('uvicorn.error')

# Fixed windows: (most requests, window length in seconds). Every window must have room.
@dataclass(frozen=True)
class Rule:
    what: str                                   # finishes "Too many … for now."
    user: tuple[tuple[int, int], ...] = ()      # applied when signed in
    ip: tuple[tuple[int, int], ...] = ()        # applied when signed out, or always if per_ip
    per_ip: bool = False                        # sign-in has no user yet, so it is always per IP
    note: str = ''                              # added after the wait, e.g. that code is unchanged

MINUTE, HOUR, DAY = 60, 3600, 86400
# Signed-out limits are per IP and looser, because a school or family can share one address.
RULES = {
    'check': Rule('checks', user=((20, MINUTE), (300, HOUR)), ip=((60, MINUTE), (600, HOUR)), note='Your code is unchanged.'),
    'attempts': Rule('checks', user=((20, MINUTE), (300, HOUR)), ip=((60, MINUTE), (600, HOUR)), note='Your code is unchanged.'),
    'invitations': Rule('invitations', user=((10, HOUR), (30, DAY)), ip=((10, HOUR),)),
    'enroll': Rule('registration attempts', user=((10, 15 * MINUTE),), ip=((30, 15 * MINUTE),)),
    'goal': Rule('goal changes', user=((10, MINUTE), (50, DAY)), ip=((30, MINUTE),)),
    'signin': Rule('sign-in attempts', ip=((60, 10 * MINUTE),), per_ip=True),
    'signin_callback': Rule('sign-in attempts', ip=((60, 10 * MINUTE),), per_ip=True),
}
MAX_KEYS = 50_000


class Limiter:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.Lock()
        self.counts: dict[str, tuple[float, int]] = {}  # hashed key -> (window start, count)
        self.secret = secrets.token_bytes(32)           # new per process; hashes mean nothing elsewhere

    def reset(self):
        with self.lock:
            self.counts.clear()

    def key(self, rule: str, who: str, window: int) -> str:
        return hmac.new(self.secret, f'{rule}|{window}|{who}'.encode(), hashlib.sha256).hexdigest()[:32]

    def hit(self, rule: str, who: str, windows) -> int:
        """Count one request. Returns 0 if allowed, else seconds until the fullest window resets."""
        now, wait = self.clock(), 0
        with self.lock:
            if len(self.counts) > MAX_KEYS:
                self._prune(now)
            for limit, length in windows:
                k = self.key(rule, who, length)
                start, count = self.counts.get(k, (now, 0))
                if now - start >= length:
                    start, count = now, 0
                if count >= limit:
                    wait = max(wait, math.ceil(start + length - now))
                self.counts[k] = (start, count + 1)
        return max(wait, 1) if wait else 0

    def _prune(self, now):
        longest = max(length for r in RULES.values() for _, length in r.user + r.ip)
        for k, (start, _) in list(self.counts.items()):
            if now - start >= longest:
                del self.counts[k]
        # Still full (for example many addresses in a short time): drop the oldest windows.
        for k in list(self.counts)[:max(0, len(self.counts) - MAX_KEYS // 2)]:
            del self.counts[k]


LIMITER = Limiter()


def client_ip(request: Request) -> str:
    """The visitor's address, grouped to /64 for IPv6.

    Render's proxy appends to X-Forwarded-For and the Next.js proxy passes it through unchanged,
    so anything a visitor puts in that header sits to the left of what the proxies add. Taking the
    rightmost public address means a made-up header cannot pick someone else's counter.
    """
    candidates = [part.strip() for part in request.headers.get('x-forwarded-for', '').split(',')]
    candidates.append(request.client.host if request.client else '')
    chosen = None
    for value in reversed(candidates):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        chosen = chosen or address
        if address.is_global:
            chosen = address
            break
    if chosen is None:
        return 'unknown'
    if chosen.version == 6:
        return str(ipaddress.ip_network(f'{chosen}/64', strict=False))
    return str(chosen)


def wait_text(seconds: int) -> str:
    if seconds < 60:
        return f'{seconds} seconds' if seconds != 1 else '1 second'
    minutes = math.ceil(seconds / 60)
    return f'{minutes} minutes' if minutes != 1 else '1 minute'


def limit(name: str):
    """FastAPI dependency: count this request against RULES[name], or raise 429."""
    rule = RULES[name]

    def check(request: Request):
        uid = None if rule.per_ip else request.session.get('uid')
        who, windows = (f'u:{uid}', rule.user) if uid is not None else (f'ip:{client_ip(request)}', rule.ip)
        wait = LIMITER.hit(name, who, windows)
        if wait:
            # Rule and scope only: no user ID, address, code or message text.
            log.info('Rate limited: rule=%s scope=%s', name, 'user' if uid is not None else 'ip')
            message = f'Too many {rule.what} for now. Please wait {wait_text(wait)} and try again.'
            raise HTTPException(429, f'{message} {rule.note}'.strip(), headers={'Retry-After': str(wait)})

    return check
