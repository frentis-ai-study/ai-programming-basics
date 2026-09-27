"""실제 예제 명령의 결과를 확인합니다 (Python 표준 unittest)."""

import csv
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeatherExampleTests(unittest.TestCase):
    def test_fixture_values_match_included_archived_csv(self):
        with (ROOT / "fixtures/weather-archived.csv").open(newline="", encoding="utf-8") as fp:
            archived = list(csv.DictReader(fp))
        daily = json.loads(
            (ROOT / "fixtures/weather-daily-example.json").read_text(encoding="utf-8")
        )["daily"]
        self.assertEqual(len(archived), len(daily["time"]))
        self.assertEqual(len(archived), len(daily["temperature_2m_max"]))
        self.assertEqual(len(archived), len(daily["temperature_2m_min"]))
        for row, day, high, low in zip(
            archived, daily["time"], daily["temperature_2m_max"], daily["temperature_2m_min"]
        ):
            self.assertEqual(row["date"], day)
            self.assertEqual(float(row["max_temp"]), high)
            self.assertEqual(float(row["min_temp"]), low)

    def test_archived_fixture_creates_matching_csv_and_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "weather.py"),
                    "--fixture",
                    str(ROOT / "fixtures/weather-daily-example.json"),
                    "--output-dir",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("보관 예제 입력", result.stdout)
            with (output / "weather.csv").open(newline="", encoding="utf-8") as fp:
                rows = list(csv.DictReader(fp))
            self.assertEqual(len(rows), 8)
            with (ROOT / "fixtures/weather-archived.csv").open(newline="", encoding="utf-8") as fp:
                expected = list(csv.DictReader(fp))
            self.assertEqual(rows, expected)
            png = (output / "weather.png").read_bytes()
            self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(len(png), 1000)
            width, height = struct.unpack(">II", png[16:24])
            self.assertGreater(width, 1000)
            self.assertGreater(height, 500)

    def test_nonfinite_temperatures_rejected_before_writing_files(self):
        for label, high, low in (
            ("NaN high", float("nan"), 20.0),
            ("Infinity high", float("inf"), 20.0),
            ("Infinity low", 30.0, float("-inf")),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                fixture = Path(tmp) / "invalid.json"
                fixture.write_text(json.dumps({"daily": {
                    "time": ["2026-08-07"],
                    "temperature_2m_max": [high],
                    "temperature_2m_min": [low],
                }}), encoding="utf-8")
                output = Path(tmp) / "output"
                result = subprocess.run(
                    [sys.executable, str(ROOT / "weather.py"), "--fixture", str(fixture),
                     "--output-dir", str(output)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("기온", result.stderr)
                self.assertFalse(output.exists())

    def test_duplicate_dates_are_rejected_before_writing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "duplicate.json"
            fixture.write_text(json.dumps({"daily": {
                "time": ["2026-08-07", "2026-08-07"],
                "temperature_2m_max": [35.7, 32.8],
                "temperature_2m_min": [24.8, 24.8],
            }}), encoding="utf-8")
            output = Path(tmp) / "output"
            result = subprocess.run(
                [sys.executable, str(ROOT / "weather.py"), "--fixture", str(fixture),
                 "--output-dir", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("중복", result.stderr)
            self.assertFalse(output.exists())

    def test_local_http_503_leaves_existing_outputs_unchanged(self):
        """실제 API 장애가 아니라, 로컬 서버의 503 응답을 이용한 통제 시험입니다."""
        class Unavailable(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"unavailable")

            def log_message(self, format, *args):
                pass

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "previous"
            output.mkdir()
            paths = [output / "weather.csv", output / "weather.png"]
            for path in paths:
                path.write_bytes(b"older successful run")
            before = [hashlib.sha256(path.read_bytes()).digest() for path in paths]
            server = HTTPServer(("127.0.0.1", 0), Unavailable)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "weather.py"), "--live", "--endpoint",
                     "http://127.0.0.1:{}/forecast".format(server.server_port),
                     "--output-dir", str(output)],
                    capture_output=True, text=True, check=False, timeout=20,
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("503", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(
                [hashlib.sha256(path.read_bytes()).digest() for path in paths], before
            )


if __name__ == "__main__":
    unittest.main()
