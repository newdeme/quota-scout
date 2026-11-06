import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import alert  # noqa: E402
import changes  # noqa: E402
import digest  # noqa: E402


class AlertTest(unittest.TestCase):
    def test_classify(self):
        S = lambda *xs: [{"state": x} for x in xs]
        self.assertEqual(alert.classify(S("ok", "no_key")), "healthy")
        self.assertEqual(alert.classify(S("rate_limited", "down")), "healthy")
        self.assertEqual(alert.classify(S("down", "auth_invalid", "no_key")), "degraded")
        self.assertEqual(alert.classify(S("no_key", "retired", "no_probe")), "empty")


class ChangesTest(unittest.TestCase):
    def test_last_state_uses_strictly_before(self):
        rows = [{"id": "a", "ts": "2026-10-01T00:00:00Z", "state": "ok"},
                {"id": "a", "ts": "2026-10-20T00:00:00Z", "state": "down"}]
        self.assertEqual(changes.last_state(rows, "2026-10-01T00:00:00Z"), {})
        self.assertEqual(changes.last_state(rows, "2026-10-02"), {"a": "ok"})
        self.assertEqual(changes.last_state(rows, "2026-11-01"), {"a": "down"})


class DigestTest(unittest.TestCase):
    def test_windows(self):
        self.assertEqual(digest.month_window("2026-12"), ("2026-12-01", "2027-01-01"))
        self.assertEqual(digest.month_window("2026-10"), ("2026-10-01", "2026-11-01"))
        from datetime import date
        self.assertEqual(digest.prev_month(date(2027, 1, 1)), "2026-12")
        self.assertEqual(digest.prev_month(date(2026, 11, 1)), "2026-10")


if __name__ == "__main__":
    unittest.main()
