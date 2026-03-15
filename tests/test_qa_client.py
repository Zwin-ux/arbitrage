from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QLabel

from market_data_recorder_desktop.qa_client import QAClientWindow, main, run_suite


def test_qa_suite_headless_report_passes(tmp_path: Path) -> None:
    workspace = tmp_path / "qa-suite"
    report = run_suite(workspace)

    assert report.failed == 0
    assert report.passed == len(report.scenarios)
    assert any(result.id == "scanner-fixture-detects-edge" for result in report.scenarios)
    assert (workspace / "scanner-fixture-detects-edge" / "exports" / "top-candidate.json").exists()


def test_qa_suite_can_target_single_scenario(tmp_path: Path) -> None:
    report = run_suite(tmp_path / "qa-single", scenario_ids=["scanner-fixture-detects-edge"])

    assert len(report.scenarios) == 1
    assert report.scenarios[0].status == "passed"
    assert any("net edge" in evidence.lower() for evidence in report.scenarios[0].evidence)


def test_qa_suite_supports_first_paper_loop_without_credentials(tmp_path: Path) -> None:
    report = run_suite(
        tmp_path / "qa-first-loop",
        scenario_ids=["first-paper-loop-without-credentials"],
    )

    assert len(report.scenarios) == 1
    assert report.scenarios[0].status == "passed"
    text = "\n".join([report.scenarios[0].summary, *report.scenarios[0].evidence]).lower()
    assert "no keys" in text or "no polymarket credentials" in text


def test_qa_client_window_renders_report(qtbot: Any, tmp_path: Path) -> None:
    report = run_suite(tmp_path / "qa-window", scenario_ids=["guided-profile-bootstrap"])
    window = QAClientWindow(workspace=tmp_path / "qa-window", scenario_ids=["guided-profile-bootstrap"])
    qtbot.addWidget(window)
    window.set_report(report)
    window.show()

    assert window.windowTitle() == "Superior QA Client"
    assert window.scenario_list.count() == 1
    health_label = window.health_card["value"]
    assert isinstance(health_label, QLabel)
    assert "Passing" in health_label.text()


def test_qa_client_main_headless_returns_zero(tmp_path: Path) -> None:
    output_path = tmp_path / "qa-report.json"
    exit_code = main(
        [
            "--headless",
            "--workspace",
            str(tmp_path / "qa-main"),
            "--scenario",
            "guided-profile-bootstrap",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
