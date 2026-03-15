from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke-test a packaged Superior Windows app bundle.")
    parser.add_argument(
        "--bundle-exe",
        required=True,
        help="Path to the packaged market-data-recorder-app.exe file.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Maximum time to wait for the packaged app smoke test to complete.",
    )
    parser.add_argument(
        "--qt-platform",
        default=None,
        help="Optional QT_QPA_PLATFORM value for the smoke run. Leave unset for normal packaged Windows startup.",
    )
    return parser


def _stop_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/F", "/T"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        pass
    try:
        process.kill()
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    bundle_exe = Path(args.bundle_exe).resolve()
    if not bundle_exe.exists():
        raise FileNotFoundError(f"Packaged executable was not found: {bundle_exe}")

    temp_dir = Path(tempfile.mkdtemp(prefix="superior-smoke-"))
    smoke_output = temp_dir / "smoke-report.json"
    env = os.environ.copy()
    if args.qt_platform:
        env["QT_QPA_PLATFORM"] = args.qt_platform

    process = subprocess.Popen(
        [str(bundle_exe), "--smoke-test", "--smoke-output", str(smoke_output)],
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.monotonic() + args.timeout_seconds
        while time.monotonic() < deadline:
            if smoke_output.exists():
                break
            if process.poll() is not None:
                break
            time.sleep(0.2)

        if process.poll() is None and not smoke_output.exists():
            _stop_process_tree(process)
            raise RuntimeError(
                f"Packaged app smoke test timed out after {args.timeout_seconds} seconds."
            )

        if smoke_output.exists():
            _stop_process_tree(process)
        elif process.returncode != 0:
            raise RuntimeError(
                "Packaged app smoke test failed.\n"
                f"Exit code: {process.returncode}"
            )

        if not smoke_output.exists():
            raise RuntimeError("Packaged app exited successfully but did not write a smoke report.")

        report = json.loads(smoke_output.read_text(encoding="utf-8"))
        expected = {
            "app_name": "Superior",
            "display_name": "Superior",
            "window_title": "Superior",
        }
        mismatches = {key: value for key, value in expected.items() if report.get(key) != value}
        if mismatches:
            raise RuntimeError(f"Unexpected smoke report values: {mismatches}\nReport: {json.dumps(report, indent=2)}")
        if not report.get("app_icon_present") or not report.get("window_icon_present"):
            raise RuntimeError(f"Smoke report indicates the Superior icon is missing.\nReport: {json.dumps(report, indent=2)}")

        print(json.dumps(report, indent=2))
    finally:
        _stop_process_tree(process)
        shutil.rmtree(temp_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
