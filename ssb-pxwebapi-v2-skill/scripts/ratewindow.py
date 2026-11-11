"""A sliding rate window for the checkers, shared by all threads in a process.

Modelled on _claimRateSlots in statistikkportalen-pxwebapi (js/api.js). Every
request takes a slot, and a slot stays taken for window_s + margin_s: a request
reaches the server a little after its slot is taken, so the server can see two
requests closer together than their slots were. The budget is a share of the
installation's limit, half by default, because the quota is per IP address
(maintainer's rule, for tests too). Two processes don't share a window, so run
two checkers one window apart. The SCB copy of this file is identical.
"""
from __future__ import annotations

import threading
import time


class RateWindow:
    def __init__(self, calls: int, window_s: float, share: float = 0.5,
                 margin_s: float = 1.0) -> None:
        self.window_s = window_s
        self.budget = max(1, int(calls * share))
        self.held_s = window_s + margin_s
        self.sent: list[float] = []  # every send time, oldest first
        self._lock = threading.Lock()

    def take(self) -> None:
        """Block until a slot is free, then take it."""
        while True:
            with self._lock:
                now = time.monotonic()
                if (len(self.sent) < self.budget
                        or now - self.sent[-self.budget] >= self.held_s):
                    self.sent.append(now)
                    return
                wait = self.sent[-self.budget] + self.held_s - now
            time.sleep(wait)

    def densest(self, window_s: float | None = None) -> int:
        """The most sends inside any window of window_s (default: the limit's)."""
        span = self.window_s if window_s is None else window_s
        best = start = 0
        for end, t in enumerate(self.sent):
            while t - self.sent[start] >= span:
                start += 1
            best = max(best, end - start + 1)
        return best

    def summary(self) -> str:
        return (f"{len(self.sent)} kall, høyst {self.densest()} per "
                f"{self.window_s:g} s (budsjett {self.budget})")
