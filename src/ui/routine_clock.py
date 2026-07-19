import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


class RoutineClock(QWidget):
    HOURS = range(24)

    def __init__(self):
        super().__init__()
        self.blocks = []
        self.setMinimumSize(420, 420)

    def set_blocks(self, blocks):
        self.blocks = sorted(blocks, key=lambda block: block["layer_order"])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPointF(self.width() / 2, self.height() / 2)
        radius = max(40, min(self.width(), self.height()) / 2 - 42)
        clock_rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
        )

        painter.setPen(Qt.NoPen)

        for block in self.blocks:
            start_minute = block["start_minute"]
            duration = (block["end_minute"] - start_minute) % (24 * 60)
            start_angle = 90 - (start_minute / (24 * 60)) * 360
            span_angle = -(duration / (24 * 60)) * 360

            painter.setBrush(QColor(block["color"]))
            painter.drawPie(
                clock_rect,
                round(start_angle * 16),
                round(span_angle * 16),
            )

        painter.setPen(QPen(QColor("#7D7D7D"), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(clock_rect)

        label_font = QFont(painter.font())
        label_font.setPointSize(11)
        label_font.setWeight(QFont.Weight.Black)
        painter.setFont(label_font)

        for hour in self.HOURS:
            angle = (hour / 24) * math.tau - math.pi / 2
            edge = QPointF(
                center.x() + math.cos(angle) * radius,
                center.y() + math.sin(angle) * radius,
            )

            painter.setPen(QPen(QColor("#000000"), 2))
            painter.drawLine(center, edge)

            label_radius = radius + 20
            label_center = QPointF(
                center.x() + math.cos(angle) * label_radius,
                center.y() + math.sin(angle) * label_radius,
            )
            label_rect = QRectF(
                label_center.x() - 18,
                label_center.y() - 10,
                36,
                20,
            )

            painter.setPen(QColor("#000000"))
            painter.drawText(label_rect, Qt.AlignCenter, f"{hour}h")
