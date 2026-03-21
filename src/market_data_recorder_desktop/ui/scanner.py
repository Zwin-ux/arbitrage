from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget


class ArcadeScannerWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._phase = 0
        self._scan_state = "standby"
        self._signals_found = 0
        self._routes_ready = 0
        self._top_edge_bps = 0
        self._top_quality = 0
        self._top_label = "Waiting for first route"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_phase)
        self._timer.start(80)
        self.setMinimumHeight(320)

    def sizeHint(self) -> QSize:
        return QSize(720, 340)

    def set_snapshot(
        self,
        *,
        scan_state: str,
        signals_found: int,
        routes_ready: int,
        top_edge_bps: int,
        top_quality: int,
        top_label: str,
    ) -> None:
        self._scan_state = scan_state
        self._signals_found = signals_found
        self._routes_ready = routes_ready
        self._top_edge_bps = top_edge_bps
        self._top_quality = top_quality
        self._top_label = top_label
        self.update()

    def _advance_phase(self) -> None:
        self._phase = (self._phase + 1) % 180
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rect = QRectF(self.rect()).adjusted(10, 10, -10, -10)
        palette = self._palette_for_state()

        painter.fillRect(self.rect(), QColor("#061127"))
        painter.fillRect(rect, QColor("#081630"))
        painter.setPen(QPen(palette["border"], 2))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor(255, 255, 255, 24), 1))
        painter.drawRect(rect.adjusted(6, 6, -6, -6))

        inner_rect = rect.adjusted(18, 18, -18, -18)
        center = QPointF(round(inner_rect.center().x()), round(inner_rect.top() + inner_rect.height() * 0.47))
        radius = min(inner_rect.width(), inner_rect.height()) * 0.34

        for angle in range(0, 360, 6):
            radians = math.radians(angle)
            inner_radius = radius * 0.28
            outer_radius = radius * 1.12
            start = QPointF(
                center.x() + math.cos(radians) * inner_radius,
                center.y() + math.sin(radians) * inner_radius,
            )
            end = QPointF(
                center.x() + math.cos(radians) * outer_radius,
                center.y() + math.sin(radians) * outer_radius,
            )
            color = QColor(palette["vector"])
            color.setAlpha(66 if angle % 24 == 0 else 30)
            painter.setPen(QPen(color, 1))
            painter.drawLine(start, end)

        sweep_angle = (self._phase * 2.0) % 360.0
        sweep_radians = math.radians(sweep_angle)
        sweep_end = QPointF(
            center.x() + math.cos(sweep_radians) * radius * 1.1,
            center.y() + math.sin(sweep_radians) * radius * 1.1,
        )
        painter.setPen(QPen(palette["accent"], 2))
        painter.drawLine(center, sweep_end)

        for ring_index, ring_factor in enumerate((0.42, 0.68, 0.94), start=1):
            ring_color = QColor(palette["vector"])
            ring_color.setAlpha(70 if ring_index == 2 else 38)
            painter.setPen(QPen(ring_color, 1))
            painter.drawEllipse(center, radius * ring_factor, radius * ring_factor)

        pulse = 1.0 + 0.06 * math.sin(self._phase / 8.0)

        dot_angles = (22, 88, 148, 214, 276, 332)
        for index, angle in enumerate(dot_angles):
            radians = math.radians(angle + self._phase * 0.6)
            orbit_radius = radius * (0.64 if index % 2 == 0 else 0.82)
            dot_center = QPointF(
                center.x() + math.cos(radians) * orbit_radius,
                center.y() + math.sin(radians) * orbit_radius,
            )
            dot_color = palette["signal"] if index < max(1, min(self._signals_found, len(dot_angles))) else palette["vector"]
            dot_alpha = 230 if index < self._signals_found else 110
            color = QColor(dot_color)
            color.setAlpha(dot_alpha)
            painter.fillRect(
                int(dot_center.x()) - 3,
                int(dot_center.y()) - 3,
                6,
                6,
                color,
            )

        core_size = max(16, int(radius * 0.24 * pulse))
        painter.fillRect(
            int(center.x()) - core_size // 2,
            int(center.y()) - core_size // 2,
            core_size,
            core_size,
            palette["accent"],
        )
        painter.fillRect(
            int(center.x()) - max(6, core_size // 4),
            int(center.y()) - max(6, core_size // 4),
            max(12, core_size // 2),
            max(12, core_size // 2),
            QColor("#ffffff"),
        )

        control_bar = QRectF(inner_rect.left() + 28, inner_rect.bottom() - 36, inner_rect.width() - 56, 14)
        stripe_colors = (QColor("#00f0ff"), QColor("#7cffb2"), QColor("#ff3ed2"), QColor("#ffd700"))
        stripe_width = max(6.0, control_bar.width() / 36.0)
        stripe_x = control_bar.left()
        stripe_index = 0
        while stripe_x < control_bar.right():
            painter.fillRect(
                QRectF(stripe_x, control_bar.top(), min(stripe_width, control_bar.right() - stripe_x), control_bar.height()),
                stripe_colors[stripe_index % len(stripe_colors)],
            )
            stripe_x += stripe_width
            stripe_index += 1
        painter.setPen(QPen(palette["border"], 1))
        painter.drawRect(control_bar)

        self._draw_text_block(painter, rect, palette)
        self._draw_scanlines(painter, rect)

    def _draw_text_block(self, painter: QPainter, rect: QRectF, palette: dict[str, QColor]) -> None:
        painter.setPen(palette["label"])
        title_font = QFont("Cascadia Mono", 10)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(rect.adjusted(18, 14, -18, -18), Qt.AlignmentFlag.AlignLeft, "ROUTE SCAN")
        painter.drawText(rect.adjusted(18, 14, -18, -18), Qt.AlignmentFlag.AlignRight, self._scan_state.upper())

        body_font = QFont("Cascadia Mono", 9)
        painter.setFont(body_font)
        metrics = [
            f"SIGNALS  {self._signals_found:02d}",
            f"ROUTES   {self._routes_ready:02d}",
            f"TOP RETURN {self._top_edge_bps:+d} BPS",
            f"QUALITY  {self._top_quality:03d}",
            f"FOCUS    {self._top_label[:22].upper()}",
        ]
        baseline_y = int(rect.top()) + 42
        for index, line in enumerate(metrics):
            painter.setPen(palette["label"])
            painter.drawText(int(rect.left()) + 20, baseline_y + index * 18, line)

        painter.setPen(palette["accent"])
        painter.drawText(
            int(rect.left()) + 20,
            int(rect.bottom()) - 52,
            "RADAR LOCKED TO LOCAL BOOKS ONLY",
        )
        painter.setPen(palette["vector"])
        painter.drawText(
            int(rect.left()) + 20,
            int(rect.bottom()) - 18,
            "PRACTICE FIRST  |  CLEAR RETURNS  |  EXPLAINABLE ROUTES",
        )

    @staticmethod
    def _draw_scanlines(painter: QPainter, rect: QRectF) -> None:
        scanline_color = QColor(255, 255, 255, 12)
        painter.setPen(QPen(scanline_color, 1))
        y = int(rect.top()) + 1
        while y < int(rect.bottom()):
            painter.drawLine(int(rect.left()) + 1, y, int(rect.right()) - 1, y)
            y += 4

    def _palette_for_state(self) -> dict[str, QColor]:
        if self._scan_state == "active":
            accent = QColor("#7cffb2")
            signal = QColor("#7cffb2")
        elif self._scan_state == "locked":
            accent = QColor("#ffd700")
            signal = QColor("#ffd700")
        else:
            accent = QColor("#00f0ff")
            signal = QColor("#ff3ed2")
        return {
            "border": QColor("#1fd6ff"),
            "vector": QColor("#00f0ff"),
            "signal": signal,
            "accent": accent,
            "label": QColor("#d9f7ff"),
        }
