from __future__ import annotations

from dataclasses import dataclass, field

from market_data_recorder_desktop.app_types import SemanticStateColor, SurfaceTier, TypeRamp


@dataclass(frozen=True)
class ThemeTokens:
    colors: dict[str, str] = field(default_factory=dict)
    spacing: tuple[int, ...] = (8, 12, 16, 24, 32, 48, 64)
    type_ramp: dict[TypeRamp, int] = field(default_factory=dict)
    surface_tones: dict[SurfaceTier, str] = field(default_factory=dict)
    semantic_colors: dict[SemanticStateColor, str] = field(default_factory=dict)


SUPERIOR_THEME = ThemeTokens(
    colors={
        "bg_main": "#08132a",
        "bg_panel": "#0e2248",
        "bg_panel_2": "#102958",
        "bg_inset": "#050b18",
        "accent_cyan": "#00eaff",
        "accent_magenta": "#ff3ed2",
        "accent_yellow": "#ffd84a",
        "accent_red": "#ff5c7a",
        "accent_green": "#5cffb2",
        "text_primary": "#e6f1ff",
        "text_secondary": "#9fb3d1",
        "text_muted": "#6f86a8",
        "stroke_soft": "#294a80",
        "stroke_active": "#19d5ff",
        "stroke_subtle": "#22365d",
    },
    type_ramp={
        "label": 10,
        "body": 12,
        "title": 15,
        "display": 26,
        "console": 11,
    },
    surface_tones={
        "shell": "#08132a",
        "primary": "#102958",
        "secondary": "#0e2248",
        "inset": "#050b18",
    },
    semantic_colors={
        "active": "#00eaff",
        "warning": "#ffd84a",
        "locked": "#ff5c7a",
        "idle": "#6f86a8",
        "error": "#ff5c7a",
        "success": "#5cffb2",
    },
)


def build_desktop_stylesheet(tokens: ThemeTokens = SUPERIOR_THEME) -> str:
    c = tokens.colors
    type_ramp = tokens.type_ramp
    return f"""
    QWidget {{
      color: {c["text_primary"]};
      font-family: "Segoe UI Variable Text", "Segoe UI", "IBM Plex Sans";
      font-size: {type_ramp["body"]}px;
    }}
    QMainWindow {{
      background: {c["bg_main"]};
      color: {c["text_primary"]};
    }}
    QWidget#DesktopShell,
    QWidget#ContentFrame,
    QWidget#PageFrame,
    QWidget#ShellPanel,
    QWizard,
    QWizardPage {{
      background: {c["bg_main"]};
    }}
    QTabWidget::pane {{
      border: 1px solid {c["stroke_soft"]};
      border-radius: 4px;
      background: {c["bg_panel"]};
      top: -1px;
    }}
    QTabBar::tab {{
      background: {c["bg_panel"]};
      color: {c["text_secondary"]};
      padding: 7px 12px;
      min-height: 18px;
      border-top-left-radius: 3px;
      border-top-right-radius: 3px;
      margin-right: 4px;
      border: 1px solid {c["stroke_subtle"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
    }}
    QTabBar::tab:selected {{
      background: {c["bg_panel_2"]};
      color: {c["text_primary"]};
      border-color: {c["stroke_active"]};
    }}
    QTabBar::tab:hover:!selected {{
      background: {c["bg_panel_2"]};
    }}
    QLabel#heroTitle {{
      font-size: {type_ramp["display"]}px;
      font-weight: 700;
      color: {c["text_primary"]};
    }}
    QLabel#heroText {{
      font-size: {type_ramp["body"]}px;
      color: {c["text_secondary"]};
    }}
    QLabel[sectionLabel="true"] {{
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      color: {c["accent_yellow"]};
      text-transform: uppercase;
      letter-spacing: 2px;
    }}
    QLabel[muted="true"] {{
      color: {c["text_muted"]};
    }}
    QPushButton {{
      background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c["accent_cyan"]}, stop:1 #73b5ff);
      color: {c["bg_inset"]};
      border: 1px solid rgba(230, 241, 255, 0.85);
      padding: 9px 14px;
      border-radius: 4px;
      font-weight: 700;
      min-height: 18px;
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
    }}
    QPushButton:hover {{
      background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #61f2ff, stop:1 #9accff);
    }}
    QPushButton[buttonRole="secondary"] {{
      background: {c["bg_panel"]};
      color: {c["text_primary"]};
      border: 1px solid {c["stroke_soft"]};
    }}
    QPushButton[buttonRole="ghost"] {{
      background: transparent;
      color: {c["text_secondary"]};
      border: 1px solid {c["stroke_subtle"]};
    }}
    QPushButton[buttonRole="secondary"]:hover,
    QPushButton[buttonRole="ghost"]:hover {{
      background: {c["bg_panel_2"]};
      border-color: {c["accent_magenta"]};
      color: {c["text_primary"]};
    }}
    QPushButton:disabled {{
      background: {c["bg_inset"]};
      color: {c["text_muted"]};
      border: 1px dashed {c["stroke_subtle"]};
    }}
    QGroupBox {{
      border: 1px solid {c["stroke_soft"]};
      border-radius: 4px;
      margin-top: 14px;
      padding: 10px 10px 12px 10px;
      background: {c["bg_panel"]};
      font-weight: 600;
    }}
    QGroupBox::title {{
      subcontrol-origin: margin;
      left: 10px;
      padding: 0 4px;
      color: {c["accent_yellow"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      letter-spacing: 1px;
    }}
    QGroupBox[panelTone="primary"] {{
      border-color: {c["stroke_active"]};
      background: {c["bg_panel_2"]};
    }}
    QGroupBox[panelTone="normal"] {{
      border-color: {c["stroke_soft"]};
      background: {c["bg_panel"]};
    }}
    QGroupBox[panelTone="subtle"] {{
      border-color: {c["stroke_subtle"]};
      background: #0b1b3a;
    }}
    QGroupBox[panelTone="ghost"] {{
      border-color: #1a2844;
      background: #09152d;
    }}
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget {{
      border: 1px solid {c["stroke_subtle"]};
      border-radius: 3px;
      padding: 8px;
      background: {c["bg_inset"]};
      color: {c["text_primary"]};
      selection-background-color: {c["accent_magenta"]};
    }}
    QPlainTextEdit[consoleRole="system"],
    QListWidget[consoleRole="system"] {{
      background: {c["bg_inset"]};
      border-color: {c["stroke_soft"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["console"]}px;
      line-height: 1.45;
    }}
    QListWidget::item {{
      padding: 6px 4px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }}
    QListWidget::item:selected {{
      background: {c["bg_panel_2"]};
      color: {c["text_primary"]};
    }}
    QFrame[signalBadge="true"],
    QFrame[statusTile="true"],
    QFrame[stateCard="true"],
    QFrame[statCell="true"] {{
      border: 1px solid {c["stroke_soft"]};
      border-radius: 3px;
      background: {c["bg_panel"]};
    }}
    QFrame[signalBadge="true"][tone="active"],
    QFrame[statusTile="true"][tone="active"],
    QFrame[stateCard="true"][tone="active"],
    QFrame[statCell="true"][tone="active"] {{
      border-color: {c["accent_cyan"]};
    }}
    QFrame[signalBadge="true"][tone="warning"],
    QFrame[statusTile="true"][tone="warning"],
    QFrame[stateCard="true"][tone="warning"],
    QFrame[statCell="true"][tone="warning"] {{
      border-color: {c["accent_yellow"]};
    }}
    QFrame[signalBadge="true"][tone="locked"],
    QFrame[statusTile="true"][tone="locked"],
    QFrame[stateCard="true"][tone="locked"],
    QFrame[statCell="true"][tone="locked"] {{
      border-color: {c["accent_red"]};
    }}
    QLabel[signalTitle="true"],
    QLabel[statusTitle="true"],
    QLabel[stateCardTitle="true"],
    QLabel[statCellTitle="true"] {{
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      color: {c["text_muted"]};
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    QLabel[signalValue="true"],
    QLabel[statusValue="true"],
    QLabel[stateCardValue="true"],
    QLabel[statCellValue="true"] {{
      font-size: {type_ramp["title"]}px;
      font-weight: 700;
      color: {c["text_primary"]};
    }}
    QLabel[signalValue="true"][tone="active"],
    QLabel[statusValue="true"][tone="active"],
    QLabel[stateCardValue="true"][tone="active"],
    QLabel[statCellValue="true"][tone="active"] {{
      color: {c["accent_cyan"]};
    }}
    QLabel[signalValue="true"][tone="warning"],
    QLabel[statusValue="true"][tone="warning"],
    QLabel[stateCardValue="true"][tone="warning"],
    QLabel[statCellValue="true"][tone="warning"] {{
      color: {c["accent_yellow"]};
    }}
    QLabel[signalValue="true"][tone="locked"],
    QLabel[statusValue="true"][tone="locked"],
    QLabel[stateCardValue="true"][tone="locked"],
    QLabel[statCellValue="true"][tone="locked"] {{
      color: {c["accent_red"]};
    }}
    QLabel[statusDetail="true"],
    QLabel[stateCardDetail="true"],
    QLabel[statCellDetail="true"] {{
      color: {c["text_secondary"]};
    }}
    QWidget#OverlayHost {{
      background: transparent;
    }}
    QFrame[stateOverlay="true"] {{
      border: 1px solid {c["stroke_soft"]};
      border-radius: 4px;
      background: rgba(5, 11, 24, 0.9);
    }}
    QStatusBar {{
      background: {c["bg_inset"]};
      color: {c["text_secondary"]};
      border-top: 1px solid {c["stroke_subtle"]};
    }}
    QCheckBox {{
      spacing: 8px;
      color: {c["text_primary"]};
    }}
    QCheckBox::indicator {{
      width: 15px;
      height: 15px;
      border: 1px solid {c["stroke_soft"]};
      background: {c["bg_inset"]};
    }}
    QCheckBox::indicator:checked {{
      background: {c["accent_cyan"]};
      border-color: {c["accent_cyan"]};
    }}
    """
