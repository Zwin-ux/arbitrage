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
        "bg_main": "#0a1230",
        "bg_panel": "#121d52",
        "bg_panel_2": "#18245e",
        "bg_inset": "#09102a",
        "accent_cyan": "#19dcff",
        "accent_magenta": "#ff33cc",
        "accent_yellow": "#ffd84a",
        "accent_red": "#ff5c7a",
        "accent_green": "#5cffb2",
        "text_primary": "#f4f7ff",
        "text_secondary": "#c5d3f2",
        "text_muted": "#8194c9",
        "stroke_soft": "#2c4692",
        "stroke_active": "#19dcff",
        "stroke_subtle": "#24376f",
        "lamp_off": "#31436e",
    },
    type_ramp={
        "label": 10,
        "body": 12,
        "title": 15,
        "display": 24,
        "console": 11,
    },
    surface_tones={
        "shell": "#0a1230",
        "primary": "#18245e",
        "secondary": "#121d52",
        "inset": "#09102a",
    },
    semantic_colors={
        "active": "#19dcff",
        "warning": "#ffd84a",
        "locked": "#ff5c7a",
        "idle": "#8194c9",
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
      outline: none;
    }}
    QMainWindow {{
      background: {c["bg_main"]};
      color: {c["text_primary"]};
    }}
    QWidget#DesktopShell,
    QWidget#ContentFrame,
    QWidget#PageFrame,
    QWizard,
    QWizardPage {{
      background: {c["bg_main"]};
    }}
    QWidget#DesktopShell {{
      background: {c["bg_main"]};
    }}
    QFrame#ShellHeader,
    QFrame#ProfileBar,
    QFrame#RuntimeDeck,
    QFrame#ShellMarquee,
    QFrame#ContentFrame,
    QFrame#NavFrame,
    QWidget#ShellPanel {{
      background: {c["bg_panel"]};
      border: 3px solid {c["accent_cyan"]};
    }}
    QFrame#ContentFrame {{
      background: #0c173d;
      border-color: {c["stroke_soft"]};
    }}
    QFrame#NavFrame {{
      background: #0d1842;
      border-color: {c["accent_cyan"]};
    }}
    QTabWidget#PrimaryNav::pane {{
      border: 3px solid {c["accent_cyan"]};
      background: {c["bg_panel"]};
      top: -3px;
    }}
    QTabBar::tab {{
      background: #101948;
      color: {c["text_secondary"]};
      padding: 5px 12px;
      min-height: 14px;
      margin-right: 6px;
      border: 3px solid {c["stroke_subtle"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    QTabBar::tab:selected {{
      background: #18245e;
      color: {c["text_primary"]};
      border-color: {c["accent_cyan"]};
    }}
    QTabBar::tab:hover:!selected {{
      background: {c["bg_panel_2"]};
      border-color: {c["stroke_soft"]};
    }}
    QLabel#MarqueeEyebrow {{
      color: {c["text_secondary"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    QLabel#MarqueeTitle {{
      color: {c["accent_cyan"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["display"]}px;
      font-weight: 900;
      letter-spacing: 3px;
      text-transform: uppercase;
    }}
    QLabel#MarqueeTitle[flickerPhase="dim"] {{
      color: {c["text_secondary"]};
    }}
    QLabel#MarqueeSubtitle {{
      color: {c["accent_yellow"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    QLabel#MachineHint {{
      color: {c["text_muted"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    QLabel#heroTitle {{
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["display"]}px;
      font-weight: 800;
      color: {c["text_primary"]};
      letter-spacing: 2px;
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
      background: {c["accent_cyan"]};
      color: {c["bg_inset"]};
      border: 3px solid {c["accent_cyan"]};
      padding: 8px 14px 7px 14px;
      font-weight: 800;
      min-height: 18px;
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      text-transform: uppercase;
    }}
    QPushButton:hover {{
      background: #57e7ff;
      border-color: #57e7ff;
    }}
    QPushButton[buttonRole="secondary"] {{
      background: {c["bg_panel"]};
      color: {c["text_primary"]};
      border: 3px solid {c["accent_magenta"]};
    }}
    QPushButton[buttonRole="ghost"] {{
      background: transparent;
      color: {c["text_secondary"]};
      border: 3px solid {c["stroke_subtle"]};
    }}
    QPushButton[buttonRole="secondary"]:hover,
    QPushButton[buttonRole="ghost"]:hover {{
      background: {c["bg_panel_2"]};
      color: {c["text_primary"]};
    }}
    QPushButton:disabled {{
      background: {c["bg_inset"]};
      color: {c["text_muted"]};
      border: 3px solid {c["stroke_subtle"]};
    }}
    QPushButton:focus {{
      border-color: {c["accent_yellow"]};
    }}
    QGroupBox {{
      border: 3px solid {c["stroke_soft"]};
      margin-top: 16px;
      padding: 12px 12px 14px 12px;
      background: #121b4a;
      font-weight: 600;
    }}
    QGroupBox::title {{
      subcontrol-origin: margin;
      left: 10px;
      padding: 0 6px;
      color: {c["accent_yellow"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
      font-size: {type_ramp["label"]}px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    QGroupBox[panelTone="primary"] {{
      border-color: {c["accent_cyan"]};
      background: {c["bg_panel_2"]};
    }}
    QGroupBox[panelTone="normal"] {{
      border-color: {c["stroke_soft"]};
      background: {c["bg_panel"]};
    }}
    QGroupBox[panelTone="subtle"] {{
      border-color: {c["stroke_subtle"]};
      background: #0f173f;
    }}
    QGroupBox[panelTone="ghost"] {{
      border-color: #20325e;
      background: #0b1434;
    }}
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget {{
      border: 3px solid {c["stroke_subtle"]};
      padding: 8px;
      background: {c["bg_inset"]};
      color: {c["text_primary"]};
      selection-background-color: {c["accent_magenta"]};
    }}
    QComboBox::drop-down {{
      border: 0;
      width: 24px;
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
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    QListWidget::item:selected {{
      background: {c["bg_panel_2"]};
      color: {c["text_primary"]};
    }}
    QFrame[signalBadge="true"],
    QFrame[statusTile="true"],
    QFrame[stateCard="true"],
    QFrame[statCell="true"],
    QFrame[signalLamp="true"] {{
      border: 3px solid {c["stroke_soft"]};
      background: #111a47;
    }}
    QFrame[signalBadge="true"][tone="active"],
    QFrame[statusTile="true"][tone="active"],
    QFrame[stateCard="true"][tone="active"],
    QFrame[statCell="true"][tone="active"],
    QFrame[signalLamp="true"][tone="active"] {{
      border-color: {c["accent_cyan"]};
    }}
    QFrame[signalBadge="true"][tone="warning"],
    QFrame[statusTile="true"][tone="warning"],
    QFrame[stateCard="true"][tone="warning"],
    QFrame[statCell="true"][tone="warning"],
    QFrame[signalLamp="true"][tone="warning"] {{
      border-color: {c["accent_yellow"]};
    }}
    QFrame[signalBadge="true"][tone="locked"],
    QFrame[statusTile="true"][tone="locked"],
    QFrame[stateCard="true"][tone="locked"],
    QFrame[statCell="true"][tone="locked"],
    QFrame[signalLamp="true"][tone="locked"] {{
      border-color: {c["accent_red"]};
    }}
    QFrame[signalBadge="true"][tone="success"],
    QFrame[statusTile="true"][tone="success"],
    QFrame[stateCard="true"][tone="success"],
    QFrame[statCell="true"][tone="success"],
    QFrame[signalLamp="true"][tone="success"] {{
      border-color: {c["accent_green"]};
    }}
    QLabel[signalTitle="true"],
    QLabel[statusTitle="true"],
    QLabel[stateCardTitle="true"],
    QLabel[statCellTitle="true"],
    QLabel[signalLampTitle="true"] {{
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
    QLabel[statCellValue="true"],
    QLabel[signalLampValue="true"] {{
      font-size: {type_ramp["title"]}px;
      font-weight: 800;
      color: {c["text_primary"]};
    }}
    QLabel[signalValue="true"][tone="active"],
    QLabel[statusValue="true"][tone="active"],
    QLabel[stateCardValue="true"][tone="active"],
    QLabel[statCellValue="true"][tone="active"],
    QLabel[signalLampValue="true"][tone="active"] {{
      color: {c["accent_cyan"]};
    }}
    QLabel[signalValue="true"][tone="warning"],
    QLabel[statusValue="true"][tone="warning"],
    QLabel[stateCardValue="true"][tone="warning"],
    QLabel[statCellValue="true"][tone="warning"],
    QLabel[signalLampValue="true"][tone="warning"] {{
      color: {c["accent_yellow"]};
    }}
    QLabel[signalValue="true"][tone="locked"],
    QLabel[statusValue="true"][tone="locked"],
    QLabel[stateCardValue="true"][tone="locked"],
    QLabel[statCellValue="true"][tone="locked"],
    QLabel[signalLampValue="true"][tone="locked"] {{
      color: {c["accent_red"]};
    }}
    QLabel[signalValue="true"][tone="success"],
    QLabel[statusValue="true"][tone="success"],
    QLabel[stateCardValue="true"][tone="success"],
    QLabel[statCellValue="true"][tone="success"],
    QLabel[signalLampValue="true"][tone="success"] {{
      color: {c["accent_green"]};
    }}
    QLabel[signalLampDot="true"] {{
      color: {c["lamp_off"]};
      font-size: 14px;
      min-width: 12px;
      max-width: 12px;
    }}
    QLabel[signalLampDot="true"][tone="active"] {{
      color: {c["accent_cyan"]};
    }}
    QLabel[signalLampDot="true"][tone="warning"] {{
      color: {c["accent_yellow"]};
    }}
    QLabel[signalLampDot="true"][tone="locked"] {{
      color: {c["accent_red"]};
    }}
    QLabel[signalLampDot="true"][tone="success"] {{
      color: {c["accent_green"]};
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
      border: 3px solid {c["stroke_soft"]};
      background: rgba(9, 16, 42, 0.97);
    }}
    QProgressBar {{
      border: 3px solid {c["stroke_soft"]};
      background: {c["bg_inset"]};
      min-height: 12px;
    }}
    QProgressBar::chunk {{
      background: {c["accent_cyan"]};
      margin: 1px;
    }}
    QStatusBar {{
      background: {c["bg_inset"]};
      color: {c["text_secondary"]};
      border-top: 3px solid {c["stroke_subtle"]};
      font-family: "Cascadia Mono", "IBM Plex Mono", monospace;
    }}
    QCheckBox {{
      spacing: 8px;
      color: {c["text_primary"]};
    }}
    QCheckBox::indicator {{
      width: 15px;
      height: 15px;
      border: 3px solid {c["stroke_soft"]};
      background: {c["bg_inset"]};
    }}
    QCheckBox::indicator:checked {{
      background: {c["accent_cyan"]};
      border-color: {c["accent_cyan"]};
    }}
    QWizard {{
      border: 3px solid {c["accent_cyan"]};
      background: {c["bg_main"]};
    }}
    QWizardPage {{
      background: {c["bg_main"]};
    }}
    QWizard QLabel {{
      color: {c["text_primary"]};
    }}
    """
