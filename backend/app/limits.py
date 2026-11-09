"""Rate limits for write endpoints and sign-in (backlog SEC-01).

Counters live in the database (ENG-11), so every API instance shares them and a restart doesn't
reset them: one row per (rule, who, window) holding only a keyed hash of the rule, the window and
the user ID or IP address, the window's start and a count. They never hold request bodies, learner
code or message text. The hash key comes from SESSION_SECRET, so it is the same on every instance.

Two exceptions stay in this process's memory, as all counters did before ENG-11:
- a rule marked private: tester feedback's per-tester counters, so that the database can never show
  who sent feedback when, even to someone who also has SESSION_SECRET (feedback-security.md);
- any request when the database can't be reached. The limit still applies, per instance, and the
  log says so (rule name only).
Old rows are deleted once no window could still be using them.
"""
import hashlib
import hmac
import ipaddress
import logging
import math
import os
import secrets
import threading
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request
from sqlalchemy import case, delete
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError

from . import db, sessions

log = logging.getLogger('uvicorn.error')

# Fixed windows: (most requests, window length in seconds). Every window must have room.
@dataclass(frozen=True)
class Rule:
    what: str                                   # finishes "Too many … for now."
    user: tuple[tuple[int, int], ...] = ()      # applied when signed in
    ip: tuple[tuple[int, int], ...] = ()        # applied when signed out, or always if per_ip
    per_ip: bool = False                        # sign-in has no user yet, so it is always per IP
    note: str = ''                              # added after the wait, e.g. that code is unchanged
    everyone: tuple[tuple[int, int], ...] = ()  # one shared counter for all callers together
    private: bool = False                       # per-caller counters stay in memory (see above)

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
    # Admin routes refuse signed-out callers before this counts; the limit is a backstop.
    'admin': Rule('admin changes', user=((60, MINUTE),), ip=((60, MINUTE),)),
    # Tester feedback (FB-02): per tester, and a total for everyone that protects the 90-item inbox
    # even if one account is misused. Signed-out callers are refused before this counts.
    'feedback': Rule('feedback messages', user=((5, HOUR), (20, DAY)), ip=((5, HOUR),), everyone=((60, DAY),), private=True),
}
MAX_KEYS = 50_000


LONGEST = max(length for r in RULES.values() for _, length in r.user + r.ip + r.everyone)
PRUNE_EVERY = 200


def shared_secret() -> bytes:
    """The same on every instance, and useless without SESSION_SECRET (main.py requires it)."""
    return hmac.new(os.getenv('SESSION_SECRET', '').encode(), b'rate-limit keys', hashlib.sha256).digest()


class Limiter:
    def __init__(self, clock=time.time, engine=None):
        # Wall-clock time, not monotonic: every instance has to agree when a window started.
        self.clock = clock
        self.engine = engine or db.engine
        self.lock = threading.Lock()
        self.counts: dict[str, tuple[float, int]] = {}  # memory counters: hashed key -> (window start, count)
        self.local = secrets.token_bytes(32)            # memory counters' own key: new per process
        self.hits = 0

    @property
    def secret(self) -> bytes:
        # Read when used, not at import, so it never comes from a SESSION_SECRET that wasn't set yet.
        return shared_secret()

    def reset(self):
        with self.lock:
            self.counts.clear()
        try:
            with self.engine.begin() as connection:
                connection.execute(delete(db.RateCount))
        except SQLAlchemyError:
            pass

    def key(self, rule: str, who: str, window: int, secret: bytes | None = None) -> str:
        return hmac.new(secret or self.secret, f'{rule}|{window}|{who}'.encode(), hashlib.sha256).hexdigest()[:32]

    def hit(self, rule: str, who: str, windows, private: bool = False) -> int:
        """Count one request. Returns 0 if allowed, else seconds until the fullest window resets."""
        now = self.clock()
        if private:
            return self._memory(rule, who, windows, now)
        try:
            return self._database(rule, who, windows, now)
        except SQLAlchemyError:
            log.warning('Rate limits: database unavailable, counting in memory: rule=%s', rule)
            return self._memory(rule, who, windows, now)

    def _database(self, rule, who, windows, now):
        wait, at = 0, int(now * 1000)
        with self.engine.begin() as connection:
            insert = postgresql_insert if connection.dialect.name == 'postgresql' else sqlite_insert
            table = db.RateCount.__table__
            for limit, length in windows:
                # One statement per window, so two instances counting at once can't both miss a request.
                stale = table.c.window_start <= at - length * 1000
                statement = insert(table).values(key=self.key(rule, who, length), window_start=at, count=1)
                statement = statement.on_conflict_do_update(index_elements=['key'], set_={
                    'window_start': case((stale, at), else_=table.c.window_start),
                    'count': case((stale, 1), else_=table.c.count + 1),
                }).returning(table.c.window_start, table.c.count)
                start, count = connection.execute(statement).one()
                if count - 1 >= limit:
                    wait = max(wait, math.ceil((start + length * 1000 - at) / 1000))
            self.hits += 1
            if self.hits % PRUNE_EVERY == 0:
                connection.execute(delete(table).where(table.c.window_start <= at - LONGEST * 1000))
        return max(wait, 1) if wait else 0

    def _memory(self, rule, who, windows, now):
        wait = 0
        with self.lock:
            if len(self.counts) > MAX_KEYS:
                self._prune(now)
            for limit, length in windows:
                k = self.key(rule, who, length, self.local)
                start, count = self.counts.get(k, (now, 0))
                if now - start >= length:
                    start, count = now, 0
                if count >= limit:
                    wait = max(wait, math.ceil(start + length - now))
                self.counts[k] = (start, count + 1)
        return max(wait, 1) if wait else 0

    def _prune(self, now):
        for k, (start, _) in list(self.counts.items()):
            if now - start >= LONGEST:
                del self.counts[k]
        # Still full (for example many addresses in a short time): drop the oldest windows.
        for k in list(self.counts)[:max(0, len(self.counts) - MAX_KEYS // 2)]:
            del self.counts[k]


LIMITER = Limiter()


# Where a signed-out visitor's address comes from. Both settings are off by default, and then every
# signed-out visitor shares one counter: too strict, but nothing a caller sends can change it.
# Set at most one, and only after the diagnostic below shows it is safe (handoff 06 section 13):
#   CLIENT_IP_HEADER   a header the edge sets and overwrites, for example cf-connecting-ip
#   TRUSTED_PROXY_HOPS the number of X-Forwarded-For entries our own proxies add on the right
CLIENT_IP_HEADER = os.getenv('CLIENT_IP_HEADER', '').strip().lower()
TRUSTED_PROXY_HOPS = int(os.getenv('TRUSTED_PROXY_HOPS', '0') or 0)
# Temporary (SEC-01 live check): log how the address was found. Off unless set to 1.
DIAGNOSTIC = os.getenv('RATE_LIMIT_DIAGNOSTIC') == '1'
FORWARDING_PREFIXES = ('x-forwarded-', 'x-real-', 'x-client-', 'cf-', 'true-client-', 'forwarded', 'rndr-', 'x-render-', 'via', 'cdn-loop')
SHARED = 'shared'


def _address(value: str) -> str | None:
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError:
        return None
    # IPv6 users usually get a whole /64, so it counts as one address.
    return str(ipaddress.ip_network(f'{address}/64', strict=False)) if address.version == 6 else str(address)


def client_ip(request: Request) -> tuple[str, str]:
    """The visitor's address for per-address limits, and which source it came from.

    Never uses the leftmost or "first public" X-Forwarded-For entry, or any header a caller can
    set: a value the caller sends can only land where these rules do not look.
    """
    if CLIENT_IP_HEADER:
        found = _address(request.headers.get(CLIENT_IP_HEADER, ''))
        return (found, 'header') if found else (SHARED, 'shared')
    if TRUSTED_PROXY_HOPS > 0:
        entries = [part for part in request.headers.get('x-forwarded-for', '').split(',') if part.strip()]
        found = _address(entries[-TRUSTED_PROXY_HOPS]) if len(entries) >= TRUSTED_PROXY_HOPS else None
        return (found, 'hops') if found else (SHARED, 'shared')
    return SHARED, 'shared'


def log_diagnostic(request: Request, rule: str, chosen: str, source: str):
    """Counts, header names and a short keyed hash only: never an address, user ID, code or text."""
    forwarded = request.headers.get('x-forwarded-for')
    entries = len([part for part in forwarded.split(',') if part.strip()]) if forwarded is not None else 0
    names = sorted({name.lower() for name in request.headers.keys() if name.lower().startswith(FORWARDING_PREFIXES)})
    digest = hmac.new(LIMITER.local, chosen.encode(), hashlib.sha256).hexdigest()[:8]
    log.info('Client address diagnostic: rule=%s xff_entries=%d headers=%s source=%s chosen=%s', rule, entries, ','.join(names) or '-', source, digest)


def wait_text(seconds: int) -> str:
    if seconds < 60:
        return f'{seconds} seconds' if seconds != 1 else '1 second'
    minutes = math.ceil(seconds / 60)
    return f'{minutes} minutes' if minutes != 1 else '1 minute'


def limit(name: str):
    """FastAPI dependency: count this request against RULES[name], or raise 429."""
    rule = RULES[name]

    def check(request: Request):
        uid = None if rule.per_ip else sessions.user_id(request)
        if uid is not None:
            who, windows = f'u:{uid}', rule.user
        else:
            address, source = client_ip(request)
            if DIAGNOSTIC:
                log_diagnostic(request, name, address, source)
            who, windows = f'ip:{address}', rule.ip
        wait = LIMITER.hit(name, who, windows, private=rule.private)
        # The shared counter only counts requests that got past this caller's own limit.
        if not wait and rule.everyone:
            wait = LIMITER.hit(name, 'everyone', rule.everyone)
        if wait:
            # Rule and scope only: no user ID, address, code or message text.
            log.info('Rate limited: rule=%s scope=%s', name, 'user' if uid is not None else 'ip')
            message = f'Too many {rule.what} for now. Please wait {wait_text(wait)} and try again.'
            raise HTTPException(429, f'{message} {rule.note}'.strip(), headers={'Retry-After': str(wait)})

    return check
