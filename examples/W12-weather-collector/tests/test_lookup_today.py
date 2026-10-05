"""조회 전용 예제: 한 날짜의 실제 응답/보관 발췌를 화면에 표시한다."""
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]


class LookupTodayTests(unittest.TestCase):
    def test_archived_response_prints_one_day_without_writing_files(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["2026-09-28"],
                "temperature_2m_max": [23.9],
                "temperature_2m_min": [17.1],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            input_file = folder / "response.json"
            input_file.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(input_file)],
                cwd=folder, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "보관 응답 예시 · 현재 예보 아님\n서울 · 2026-09-28\n최고 23.9°C · 최저 17.1°C\n")
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ["response.json"])

    def test_missing_daily_fails_without_success_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            path.write_text('{"timezone": "Asia/Seoul"}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("오류:", result.stderr)
            self.assertIn("날짜", result.stderr)

    def test_two_day_response_is_not_mislabeled_as_one_day(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["2026-09-28", "2026-09-29"],
                "temperature_2m_max": [23.9, 24.5],
                "temperature_2m_min": [17.1, 16.4],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "two-days.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("한 날짜", result.stderr)

    def test_fahrenheit_is_not_mislabeled_as_celsius(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°F", "temperature_2m_min": "°F"},
            "daily": {
                "time": ["2026-09-29"],
                "temperature_2m_max": [75],
                "temperature_2m_min": [61],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fahrenheit.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("°C", result.stderr)

    def test_non_seoul_timezone_is_not_labeled_seoul_day(self):
        payload = {
            "timezone": "Europe/London",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["2026-09-29"],
                "temperature_2m_max": [21.0],
                "temperature_2m_min": [15.0],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "timezone.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("Asia/Seoul", result.stderr)

    def test_nonfinite_temperature_is_not_printed_as_forecast(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["2026-09-29"],
                "temperature_2m_max": [float("nan")],
                "temperature_2m_min": [16.4],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid-temperature.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("기온", result.stderr)

    def test_invalid_date_is_not_printed_as_a_forecast_day(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["not-a-day"],
                "temperature_2m_max": [24.5],
                "temperature_2m_min": [16.4],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid-day.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("날짜", result.stderr)

    def test_high_below_low_is_not_printed_as_success(self):
        payload = {
            "timezone": "Asia/Seoul",
            "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
            "daily": {
                "time": ["2026-09-29"],
                "temperature_2m_max": [10.0],
                "temperature_2m_min": [20.0],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reversed.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "lookup_today.py"), "--fixture", str(path)],
                cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("최고기온", result.stderr)

    def test_live_request_has_seoul_one_day_conditions_and_prints_response(self):
        seen_paths = []

        class OneDayForecast(BaseHTTPRequestHandler):
            def do_GET(self):
                seen_paths.append(self.path)
                body = json.dumps({
                    "timezone": "Asia/Seoul",
                    "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C"},
                    "daily": {
                        "time": ["2026-09-29"],
                        "temperature_2m_max": [24.5],
                        "temperature_2m_min": [16.4],
                    },
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), OneDayForecast)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "lookup_today.py"), "--endpoint",
                     f"http://127.0.0.1:{server.server_port}/forecast"],
                    cwd=tmp, text=True, capture_output=True, timeout=20, check=False,
                )
                self.assertEqual(list(Path(tmp).iterdir()), [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "서울 · 2026-09-29\n최고 24.5°C · 최저 16.4°C\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(len(seen_paths), 1)
        url = urlparse(seen_paths[0])
        self.assertEqual(url.path, "/forecast")
        self.assertEqual(parse_qs(url.query), {
            "latitude": ["37.57"], "longitude": ["126.98"],
            "daily": ["temperature_2m_max,temperature_2m_min"],
            "forecast_days": ["1"], "timezone": ["Asia/Seoul"],
        })


if __name__ == "__main__":
    unittest.main()
