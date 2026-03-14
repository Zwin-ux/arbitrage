from pathlib import Path
import sys


project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from market_data_recorder_desktop.main import main


args = sys.argv[1:]
if "--smoke-test" not in args:
    args = ["--smoke-test", *args]

raise SystemExit(main(args))
