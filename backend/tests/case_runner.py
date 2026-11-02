"""Runs authored programs against a browser check's cases, the way the browser worker does (TESTS ONLY).

The app never runs learner code on the server: in production, public/python-worker.js runs each case in
the learner's browser and the API only compares the reports. These tests need the same reports for the
lesson samples, hints and reference solutions written in the content files, so this module plays the
worker's part in a separate Python process, with the same rules:

- each case runs in a fresh namespace, with input() replaced by that case's replies, in order;
  input() prints no prompt, and asks for one reply too many with the worker's EOFError
- the learner's file is "<exec>", so an error reports the line in the program
- output is capped at the check's limit, and a run past the time limit is a timeout; as in the
  browser, the cases after a timeout are not run (the runner has stopped the worker)

Python here is the backend's 3.12, the same version Pyodide 0.27 runs in the browser.
"""
import json
import subprocess
import sys

from app.browser_checks import CaseRun

RUNNER = r'''
import builtins, contextlib, io, json, signal, sys, traceback
jobs = json.load(sys.stdin)

class TimeLimit(BaseException):
    pass

def alarm(signum, frame):
    raise TimeLimit()

signal.signal(signal.SIGALRM, alarm)
results = []

class Capped(io.StringIO):
    def __init__(self, limit):
        super().__init__()
        self.limit, self.capped = limit, False
    def write(self, text):
        if self.tell() + len(text) > self.limit:
            super().write(text[:self.limit - self.tell()])
            self.capped = True
            raise OSError('output limit')
        return super().write(text)

for job in jobs:
    reports = []
    stopped = False
    for case in job['cases']:
        if stopped:
            reports.append({'id': case['id'], 'status': 'not_run', 'error_type': None, 'line': None, 'output': ''})
            continue
        replies = iter(case['inputs'])
        def fake_input(prompt=''):
            try:
                return next(replies)
            except StopIteration:
                raise EOFError('Add a player reply for each input() call, in order.')
        builtins.input = fake_input
        out = Capped(job['limit'])
        report = {'id': case['id'], 'status': 'ok', 'error_type': None, 'line': None}
        try:
            signal.setitimer(signal.ITIMER_REAL, job['seconds'])
            with contextlib.redirect_stdout(out):
                exec(compile(job['code'], '<exec>', 'exec'), {'__name__': '__main__'})
        except TimeLimit:
            report['status'] = 'timeout'
            stopped = True
        except BaseException as error:
            if out.capped:
                report['status'] = 'output_limit'
            else:
                report['status'] = 'error'
                report['error_type'] = type(error).__name__
                if isinstance(error, SyntaxError):
                    report['line'] = error.lineno
                else:
                    frames = [f.lineno for f in traceback.extract_tb(error.__traceback__) if f.filename == '<exec>']
                    report['line'] = frames[-1] if frames else None
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        # The browser never hears back from a case it stopped, so it reports no output for it.
        report['output'] = '' if report['status'] == 'timeout' else out.getvalue()
        reports.append(report)
    results.append(reports)
json.dump(results, sys.__stdout__)
'''


# A loop that never ends is stopped here after this many seconds, not the check's 3, to keep the tests
# fast; the judge only sees that the case timed out, as it would in the browser.
SECONDS = 0.5


def reports(lesson, programs, timeout=120):
    """For each program, one report per check case, as the browser would send them (no error message)."""
    check = lesson.task('challenge').check
    jobs = [{'code': code, 'limit': 10_000, 'seconds': SECONDS, 'cases': [{'id': c.id, 'inputs': c.inputs} for c in check.cases]} for code in programs]
    done = subprocess.run([sys.executable, '-I', '-c', RUNNER], input=json.dumps(jobs), capture_output=True, text=True, timeout=timeout, check=True)
    return [[CaseRun(**report) for report in program] for program in json.loads(done.stdout)]


def run(lesson, code, *more):
    """Run one program (or several) against the lesson's cases; returns the reports, or a list of them."""
    found = reports(lesson, [code, *more])
    return found if more else found[0]


def run_program(code, inputs):
    """Run a short program once with these replies, the way the "Try it" card does: (output, error type)."""
    from types import SimpleNamespace
    case = SimpleNamespace(id='once', inputs=list(inputs))
    lesson = SimpleNamespace(task=lambda kind: SimpleNamespace(check=SimpleNamespace(cases=[case])))
    report = reports(lesson, [code])[0][0]
    return report.output, report.error_type
