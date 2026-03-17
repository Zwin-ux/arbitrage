from __future__ import annotations

from dataclasses import dataclass, field

from market_data_recorder_desktop.app_types import SemanticStateColor, SurfaceTier, TypeRamp


@dataclass(frozen=True)
class ColorTokens:
    bg_base: str = "#08132A"
    bg_panel: str = "#0E2248"
    bg_panel_alt: str = "#102958"
    bg_console: str = "#050B18"
    border_active: str = "#00EAFF"
    border_idle: str = "#294D85"
    border_warn: str = "#FFD84A"
    border_locked: str = "#FF5C7A"
    border_success: str = "#5CFFB2"
    text_primary: str = "#E6F1FF"
    text_dim: str = "#9FB3D1"
    text_muted: str = "#6F86A8"
    text_accent: str = "#00EAFF"
    state_active: str = "#00EAFF"
    state_locked: str = "#FF5C7A"
    state_warn: str = "#FFD84A"
    state_offline: str = "#6F86A8"
    state_success: str = "#5CFFB2"
    state_route: str = "#FF3ED2"


@dataclass(frozen=True)
class BorderTokens:
    pixel_line: int = 2
    double_frame: int = 4
    inset_frame: int = 3
    warning_frame: int = 3
    active_frame: int = 4


@dataclass(frozen=True)
class TypographyTokens:
    display_font: str = '"Cascadia Mono", "IBM Plex Mono", monospace'
    ui_font: str = '"Segoe UI Variable Text", "Segoe UI", "IBM Plex Sans"'
    mono_font: str = '"Cascadia Mono", "IBM Plex Mono", monospace'


@dataclass(frozen=True)
class EffectTokens:
    scanline_intensity: float = 0.08
    crt_noise: float = 0.04
    blink_timing_ms: int = 240
    pulse_timing_ms: int = 420
    caret_blink_timing_ms: int = 560


@dataclass(frozen=True)
class ThemeTokens:
    colors: ColorTokens = field(default_factory=ColorTokens)
    borders: BorderTokens = field(default_factory=BorderTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    effects: EffectTokens = field(default_factory=EffectTokens)
    spacing: tuple[int, ...] = (8, 16, 24, 32, 40, 48)
    type_ramp: dict[TypeRamp, int] = field(
        default_factory=lambda: {
            "label": 10,
            "body": 12,
            "title": 16,
            "display": 24,
            "console": 11,
        }
    )
    surface_tones: dict[SurfaceTier, str] = field(
        default_factory=lambda: {
            "shell": "#08132A",
            "primary": "#102958",
            "secondary": "#0E2248",
            "inset": "#050B18",
        }
    )
    semantic_colors: dict[SemanticStateColor, str] = field(
        default_factory=lambda: {
            "active": "#00EAFF",
            "warning": "#FFD84A",
            "locked": "#FF5C7A",
            "idle": "#6F86A8",
            "error": "#FF5C7A",
            "success": "#5CFFB2",
        }
    )


SUPERIOR_THEME = ThemeTokens()


def build_desktop_stylesheet(tokens: ThemeTokens = SUPERIOR_THEME) -> str:
    c = tokens.colors
    b = tokens.borders
    t = tokens.typography
    r = tokens.type_ramp
    return f"""
    QWidget {{
      background: {c.bg_base};
      color: {c.text_primary};
      font-family: {t.ui_font};
      font-size: {r["body"]}px;
      outline: none;
    }}
    QMainWindow,
    QWidget#DesktopShell,
    QWidget#ContentFrame,
    QWidget#PageFrame,
    QWizard,
    QWizardPage {{
      background: {c.bg_base};
    }}
    QFrame#ShellHeader,
    QFrame#ContentFrame,
    QFrame#NavFrame,
    QFrame#ProfileBar,
    QFrame#RuntimeDeck,
    QFrame#ShellMarquee {{
      background: {c.bg_panel};
      border: {b.double_frame}px solid {c.border_active};
    }}
    QFrame#ContentFrame {{
      background: {c.bg_panel_alt};
      border-color: {c.border_idle};
    }}
    QFrame#NavFrame {{
      background: {c.bg_panel};
      border-color: {c.border_idle};
    }}
    QTabWidget#PrimaryNav::pane {{
      border: 0;
      background: transparent;
    }}
    QTabBar::tab {{
      background: {c.bg_panel};
      color: {c.text_dim};
      min-height: 18px;
      padding: 8px 16px;
      margin-right: 8px;
      border-top: {b.active_frame}px solid {c.border_idle};
      border-left: {b.active_frame}px solid {c.border_idle};
      border-right: {b.active_frame}px solid {c.border_idle};
      border-bottom: {b.active_frame}px solid {c.bg_console};
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    QTabBar::tab:selected {{
      background: {c.bg_panel_alt};
      color: {c.text_primary};
      border-top-color: {c.border_active};
      border-left-color: {c.border_active};
      border-right-color: {c.border_active};
      border-bottom-color: {c.bg_panel_alt};
      margin-bottom: -2px;
    }}
    QTabBar::tab:hover:!selected {{
      color: {c.text_primary};
      border-top-color: {c.border_warn};
      border-left-color: {c.border_warn};
      border-right-color: {c.border_warn};
    }}
    QLabel#MarqueeEyebrow,
    QLabel#MachineHint,
    QLabel[sectionLabel="true"],
    QLabel[panelSector="true"],
    QLabel[commandKey="true"],
    QLabel[telemetryLampTitle="true"],
    QLabel[signalLampTitle="true"],
    QLabel[statusModuleTitle="true"],
    QLabel[statCellTitle="true"] {{
      background: transparent;
      color: {c.text_dim};
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    QLabel#MarqueeTitle,
    QLabel#heroTitle,
    QLabel[panelTitle="true"],
    QLabel[statusModuleValue="true"],
    QLabel[statCellValue="true"],
    QLabel[telemetryLampValue="true"],
    QLabel[signalLampValue="true"] {{
      background: transparent;
      color: {c.text_primary};
      font-family: {t.display_font};
      font-size: {r["title"]}px;
      font-weight: 900;
      letter-spacing: 1px;
    }}
    QLabel#heroTitle {{
      font-size: {r["display"]}px;
    }}
    QLabel#MarqueeTitle {{
      color: {c.text_accent};
      font-size: {r["display"]}px;
      letter-spacing: 2px;
    }}
    QLabel#MarqueeTitle[flickerPhase="dim"] {{
      color: {c.text_dim};
    }}
    QLabel#MarqueeSubtitle {{
      background: transparent;
      color: {c.border_warn};
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    QLabel#heroText,
    QLabel[panelToneText="true"],
    QLabel[statusModuleDetail="true"],
    QLabel[statCellDetail="true"],
    QLabel[muted="true"] {{
      background: transparent;
      color: {c.text_dim};
      font-size: {r["body"]}px;
    }}
    QPushButton {{
      background: {c.state_active};
      color: {c.bg_console};
      border-top: {b.active_frame}px solid {c.text_primary};
      border-left: {b.active_frame}px solid {c.text_primary};
      border-right: {b.active_frame}px solid {c.border_active};
      border-bottom: {b.active_frame}px solid {c.border_active};
      padding: 8px 16px;
      min-height: 20px;
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    QPushButton:hover {{
      border-right-color: {c.border_warn};
      border-bottom-color: {c.border_warn};
    }}
    QPushButton:pressed {{
      border-top-color: {c.border_active};
      border-left-color: {c.border_active};
      border-right-color: {c.text_primary};
      border-bottom-color: {c.text_primary};
      padding-top: 9px;
      padding-left: 17px;
      padding-bottom: 7px;
      padding-right: 15px;
    }}
    QPushButton[buttonRole="secondary"] {{
      background: {c.bg_panel};
      color: {c.text_primary};
      border-top-color: {c.text_dim};
      border-left-color: {c.text_dim};
      border-right-color: {c.state_route};
      border-bottom-color: {c.state_route};
    }}
    QPushButton[buttonRole="ghost"] {{
      background: {c.bg_console};
      color: {c.text_dim};
      border-top-color: {c.border_idle};
      border-left-color: {c.border_idle};
      border-right-color: {c.border_idle};
      border-bottom-color: {c.border_idle};
    }}
    QPushButton:disabled {{
      background: {c.bg_console};
      color: {c.text_muted};
      border-top-color: {c.border_idle};
      border-left-color: {c.border_idle};
      border-right-color: {c.border_idle};
      border-bottom-color: {c.border_idle};
    }}
    QPushButton:focus {{
      border-right-color: {c.border_warn};
      border-bottom-color: {c.border_warn};
    }}
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QComboBox,
    QListWidget {{
      background: {c.bg_console};
      color: {c.text_primary};
      border: {b.inset_frame}px solid {c.border_idle};
      padding: 8px;
      selection-background-color: {c.state_route};
      font-size: {r["body"]}px;
    }}
    QComboBox::drop-down {{
      width: 24px;
      border: 0;
    }}
    QPlainTextEdit[consoleRole="system"],
    QListWidget[consoleRole="system"] {{
      background: {c.bg_console};
      border-color: {c.border_active};
      font-family: {t.mono_font};
      font-size: {r["console"]}px;
      line-height: 1.45;
    }}
    QListWidget::item {{
      padding: 8px 4px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}
    QListWidget::item:selected {{
      background: {c.bg_panel_alt};
      color: {c.text_primary};
    }}
    QFrame[pixelPanel="true"],
    QFrame[telemetryLamp="true"],
    QFrame[signalLamp="true"],
    QFrame[statusModule="true"],
    QFrame[statCell="true"],
    QFrame[commandFooter="true"] {{
      background: {c.bg_panel};
      border: {b.inset_frame}px solid {c.border_idle};
    }}
    QFrame[pixelPanel="true"][tone="active"],
    QFrame[telemetryLamp="true"][tone="active"],
    QFrame[signalLamp="true"][tone="active"],
    QFrame[statusModule="true"][tone="active"],
    QFrame[statCell="true"][tone="active"] {{
      border-color: {c.state_active};
    }}
    QFrame[pixelPanel="true"][tone="warning"],
    QFrame[telemetryLamp="true"][tone="warning"],
    QFrame[signalLamp="true"][tone="warning"],
    QFrame[statusModule="true"][tone="warning"],
    QFrame[statCell="true"][tone="warning"] {{
      border-color: {c.state_warn};
    }}
    QFrame[pixelPanel="true"][tone="locked"],
    QFrame[telemetryLamp="true"][tone="locked"],
    QFrame[signalLamp="true"][tone="locked"],
    QFrame[statusModule="true"][tone="locked"],
    QFrame[statCell="true"][tone="locked"] {{
      border-color: {c.state_locked};
    }}
    QFrame[pixelPanel="true"][tone="success"],
    QFrame[telemetryLamp="true"][tone="success"],
    QFrame[signalLamp="true"][tone="success"],
    QFrame[statusModule="true"][tone="success"],
    QFrame[statCell="true"][tone="success"] {{
      border-color: {c.state_success};
    }}
    QFrame[pixelPanel="true"][compact="true"] {{
      background: {c.bg_panel_alt};
    }}
    QLabel[telemetryLampDot="true"],
    QLabel[signalLampDot="true"] {{
      background: transparent;
      color: {c.state_offline};
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 900;
      min-width: 16px;
      max-width: 16px;
    }}
    QLabel[telemetryLampDot="true"][tone="active"],
    QLabel[signalLampDot="true"][tone="active"],
    QLabel[telemetryLampValue="true"][tone="active"],
    QLabel[signalLampValue="true"][tone="active"],
    QLabel[statusModuleValue="true"][tone="active"],
    QLabel[statCellValue="true"][tone="active"],
    QLabel[stateChip="true"][tone="active"],
    QLabel[riskBadge="true"][tone="active"] {{
      color: {c.state_active};
    }}
    QLabel[telemetryLampDot="true"][tone="warning"],
    QLabel[signalLampDot="true"][tone="warning"],
    QLabel[telemetryLampValue="true"][tone="warning"],
    QLabel[signalLampValue="true"][tone="warning"],
    QLabel[statusModuleValue="true"][tone="warning"],
    QLabel[statCellValue="true"][tone="warning"],
    QLabel[stateChip="true"][tone="warning"],
    QLabel[riskBadge="true"][tone="warning"] {{
      color: {c.state_warn};
    }}
    QLabel[telemetryLampDot="true"][tone="locked"],
    QLabel[signalLampDot="true"][tone="locked"],
    QLabel[telemetryLampValue="true"][tone="locked"],
    QLabel[signalLampValue="true"][tone="locked"],
    QLabel[statusModuleValue="true"][tone="locked"],
    QLabel[statCellValue="true"][tone="locked"],
    QLabel[stateChip="true"][tone="locked"],
    QLabel[riskBadge="true"][tone="locked"] {{
      color: {c.state_locked};
    }}
    QLabel[telemetryLampDot="true"][tone="success"],
    QLabel[signalLampDot="true"][tone="success"],
    QLabel[telemetryLampValue="true"][tone="success"],
    QLabel[signalLampValue="true"][tone="success"],
    QLabel[statusModuleValue="true"][tone="success"],
    QLabel[statCellValue="true"][tone="success"],
    QLabel[stateChip="true"][tone="success"],
    QLabel[riskBadge="true"][tone="success"] {{
      color: {c.state_success};
    }}
    QLabel[stateChip="true"],
    QLabel[riskBadge="true"] {{
      background: {c.bg_console};
      border: {b.pixel_line}px solid {c.border_idle};
      padding: 4px 8px;
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    QProgressBar[meterBar="true"] {{
      background: {c.bg_console};
      border: {b.inset_frame}px solid {c.border_idle};
      min-height: 16px;
    }}
    QProgressBar[meterBar="true"]::chunk {{
      background: {c.state_active};
      margin: 1px;
    }}
    QStatusBar {{
      background: {c.bg_console};
      color: {c.text_dim};
      border-top: {b.inset_frame}px solid {c.border_idle};
      font-family: {t.mono_font};
    }}
    QCheckBox {{
      background: transparent;
      color: {c.text_primary};
      spacing: 8px;
    }}
    QCheckBox::indicator {{
      width: 16px;
      height: 16px;
      border: {b.inset_frame}px solid {c.border_idle};
      background: {c.bg_console};
    }}
    QCheckBox::indicator:checked {{
      background: {c.state_active};
      border-color: {c.state_active};
    }}
    QGroupBox {{
      background: {c.bg_panel};
      border: {b.inset_frame}px solid {c.border_idle};
      margin-top: 16px;
      padding: 12px;
      font-weight: 700;
    }}
    QGroupBox::title {{
      subcontrol-origin: margin;
      left: 12px;
      padding: 0 6px;
      color: {c.border_warn};
      font-family: {t.display_font};
      font-size: {r["label"]}px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    QWidget#OverlayHost {{
      background: transparent;
    }}
    QFrame[stateOverlay="true"] {{
      background: rgba(5, 11, 24, 0.97);
      border: {b.double_frame}px solid {c.border_active};
    }}
    QWizard {{
      border: {b.double_frame}px solid {c.border_active};
      background: {c.bg_base};
    }}
    QWizardPage {{
      background: {c.bg_base};
    }}
    """
