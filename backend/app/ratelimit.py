import time
from collections import defaultdict, deque

from app.config import settings


class LoginRateLimiter:
    def __init__(self, max_failures: int, window_s: int):
        self.max_failures = max_failures
        self.window_s = window_s
        self._failures: dict[str, deque[float]] = defaultdict(deque)

    def _recent(self, key: str) -> deque[float]:
        now = time.monotonic()
        attempts = self._failures[key]
        while attempts and now - attempts[0] > self.window_s:
            attempts.popleft()
        return attempts

    def is_blocked(self, key: str) -> bool:
        return len(self._recent(key)) >= self.max_failures

    def record_failure(self, key: str) -> None:
        self._recent(key).append(time.monotonic())

    def reset(self, key: str | None = None) -> None:
        if key is None:
            self._failures.clear()
        else:
            self._failures.pop(key, None)


login_limiter = LoginRateLimiter(settings.login_max_failures, settings.login_window_s)