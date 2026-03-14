import sys
import traceback
from pathlib import Path


def _smoke_trace_path(argv: list[str]) -> Path | None:
    if "--smoke-test" not in argv or "--smoke-output" not in argv:
        return None
    try:
        output_index = argv.index("--smoke-output")
        output_value = argv[output_index + 1]
    except (ValueError, IndexError):
        return None
    return Path(output_value).with_name("smoke-trace.log")


def _append_trace(trace_path: Path | None, message: str) -> None:
    if trace_path is None:
        return
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


trace_path = _smoke_trace_path(sys.argv)
_append_trace(trace_path, "desktop-entry:start")

project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
_append_trace(trace_path, f"desktop-entry:src-path={src_path}")

try:
    _append_trace(trace_path, "desktop-entry:import-main")
    from market_data_recorder_desktop.main import main
    _append_trace(trace_path, "desktop-entry:import-main-done")
except Exception as exc:
    _append_trace(trace_path, f"desktop-entry:import-error:{exc}")
    _append_trace(trace_path, traceback.format_exc())
    raise

_append_trace(trace_path, "desktop-entry:call-main")

raise SystemExit(main())
