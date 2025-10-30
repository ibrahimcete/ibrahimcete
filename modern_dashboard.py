# -*- coding: utf-8 -*-
"""
Modern Dashboard Components
Gelişmiş dashboard, charts ve data visualization
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, QSize, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QFont, QPainterPath, QPolygonF, QPointF
)
import random
from datetime import datetime, timedelta


# ============================================================================
# METRIC CARDS
# ============================================================================

class MetricCard(QFrame):
    """Modern metrik kartı"""

    def __init__(self, title="", value="0", change="+12%", icon="📊",
                 color="#5858D6", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.change = change
        self.icon = icon
        self.color = QColor(color)

        self.setMinimumHeight(140)
        self.setObjectName("metricCard")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header (icon + title)
        header = QHBoxLayout()

        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 28px;")
        icon_label.setFixedSize(40, 40)

        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 180);
            font-weight: 500;
        """)

        header.addWidget(icon_label)
        header.addWidget(title_label, 1)
        header.addStretch()

        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
        """)

        # Change indicator
        self.change_label = QLabel(self.change)
        is_positive = self.change.startswith("+")
        change_color = "#4CAF50" if is_positive else "#F44336"
        arrow = "↗" if is_positive else "↘"

        self.change_label.setText(f"{arrow} {self.change}")
        self.change_label.setStyleSheet(f"""
            font-size: 12px;
            color: {change_color};
            font-weight: 600;
        """)

        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addWidget(self.change_label)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(self.color.red(), self.color.green(),
                                       self.color.blue(), 200))
        gradient.setColorAt(1.0, QColor(self.color.red() - 30,
                                       self.color.green() - 30,
                                       self.color.blue() - 30, 200))

        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)
        painter.fillPath(path, gradient)

        # Glass overlay
        overlay = QLinearGradient(0, 0, 0, self.height() // 2)
        overlay.setColorAt(0.0, QColor(255, 255, 255, 30))
        overlay.setColorAt(1.0, QColor(255, 255, 255, 0))

        overlay_path = QPainterPath()
        overlay_rect = QRect(0, 0, self.width(), self.height() // 2)
        overlay_path.addRoundedRect(overlay_rect, 15, 15)
        painter.fillPath(overlay_path, overlay)

        # Border
        pen = QPen(QColor(255, 255, 255, 60), 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

        # Decorative circle
        painter.setOpacity(0.08)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.width() - 50, -30, 100, 100)

    def update_value(self, value, change=None):
        """Değeri güncelle"""
        self.value = str(value)
        self.value_label.setText(self.value)

        if change:
            self.change = change
            is_positive = change.startswith("+")
            arrow = "↗" if is_positive else "↘"
            self.change_label.setText(f"{arrow} {change}")


# ============================================================================
# MINI CHARTS
# ============================================================================

class SparklineChart(QWidget):
    """Küçük çizgi grafik (sparkline)"""

    def __init__(self, data=None, color="#5858D6", parent=None):
        super().__init__(parent)
        self.data = data or [random.randint(10, 90) for _ in range(20)]
        self.color = QColor(color)
        self.setMinimumHeight(60)

    def set_data(self, data):
        """Veriyi güncelle"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        if not self.data or len(self.data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        padding = 5

        # Veri aralığını hesapla
        min_val = min(self.data)
        max_val = max(self.data)
        value_range = max_val - min_val if max_val != min_val else 1

        # Noktaları hesapla
        points = []
        step = (width - 2 * padding) / (len(self.data) - 1)

        for i, value in enumerate(self.data):
            x = padding + i * step
            y = height - padding - ((value - min_val) / value_range) * (height - 2 * padding)
            points.append(QPointF(x, y))

        # Gradient fill altı
        path = QPainterPath()
        path.moveTo(points[0].x(), height)
        for point in points:
            path.lineTo(point)
        path.lineTo(points[-1].x(), height)
        path.closeSubpath()

        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0.0, QColor(self.color.red(), self.color.green(),
                                       self.color.blue(), 100))
        gradient.setColorAt(1.0, QColor(self.color.red(), self.color.green(),
                                       self.color.blue(), 0))
        painter.fillPath(path, gradient)

        # Çizgi
        pen = QPen(self.color, 2)
        painter.setPen(pen)
        polygon = QPolygonF(points)
        painter.drawPolyline(polygon)

        # Son nokta vurgu
        painter.setBrush(self.color)
        painter.drawEllipse(points[-1], 4, 4)


class MiniBarChart(QWidget):
    """Mini bar grafik"""

    def __init__(self, data=None, colors=None, parent=None):
        super().__init__(parent)
        self.data = data or [random.randint(20, 100) for _ in range(7)]
        self.colors = colors or ["#5858D6", "#30A24C", "#CA7137"]
        self.setMinimumHeight(80)

    def set_data(self, data):
        """Veriyi güncelle"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        padding = 10

        max_val = max(self.data)
        bar_width = (width - 2 * padding) / len(self.data) - 4

        for i, value in enumerate(self.data):
            bar_height = (value / max_val) * (height - 2 * padding)
            x = padding + i * (bar_width + 4)
            y = height - padding - bar_height

            # Gradient bar
            gradient = QLinearGradient(0, y, 0, y + bar_height)
            color = QColor(self.colors[i % len(self.colors)])
            gradient.setColorAt(0.0, color)
            gradient.setColorAt(1.0, QColor(color.red() - 40,
                                           color.green() - 40,
                                           color.blue() - 40))

            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 4, 4)


class DonutChart(QWidget):
    """Donut (halka) grafik"""

    def __init__(self, percentage=75, color="#5858D6", label="", parent=None):
        super().__init__(parent)
        self.percentage = percentage
        self.color = QColor(color)
        self.label = label
        self.setFixedSize(120, 120)

        # Animation
        self.current_percentage = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_progress)

    def set_percentage(self, percentage):
        """Yüzdeyi ayarla ve animasyon başlat"""
        self.percentage = percentage
        self.current_percentage = 0
        self.timer.start(16)

    def animate_progress(self):
        """Progress animasyonu"""
        if self.current_percentage < self.percentage:
            self.current_percentage += 2
            self.update()
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 10

        # Background circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 50, 100))
        painter.drawEllipse(center_x - radius, center_y - radius,
                           radius * 2, radius * 2)

        # Progress arc
        pen = QPen(self.color, 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Arc hesaplama (başlangıç -90 derece = üst)
        start_angle = -90 * 16
        span_angle = int(-(self.current_percentage / 100) * 360 * 16)
        painter.drawArc(center_x - radius + 6, center_y - radius + 6,
                       (radius - 6) * 2, (radius - 6) * 2,
                       start_angle, span_angle)

        # Center text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
        text = f"{int(self.current_percentage)}%"
        painter.drawText(self.rect(), Qt.AlignCenter, text)

        # Label
        if self.label:
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor(180, 180, 180))
            label_rect = QRect(0, center_y + 15, self.width(), 20)
            painter.drawText(label_rect, Qt.AlignCenter, self.label)


# ============================================================================
# ACTIVITY TIMELINE
# ============================================================================

class ActivityTimeline(QWidget):
    """Aktivite zaman çizelgesi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self.setMinimumHeight(200)

    def add_activity(self, title, time, icon="•", color="#5858D6"):
        """Aktivite ekle"""
        self.activities.append({
            "title": title,
            "time": time,
            "icon": icon,
            "color": QColor(color)
        })
        self.update()

    def clear(self):
        """Tüm aktiviteleri temizle"""
        self.activities.clear()
        self.update()

    def paintEvent(self, event):
        if not self.activities:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        y_offset = 20
        line_x = 30

        for i, activity in enumerate(self.activities):
            # Timeline line
            if i < len(self.activities) - 1:
                painter.setPen(QPen(QColor(80, 80, 100), 2))
                painter.drawLine(line_x, y_offset + 15, line_x, y_offset + 60)

            # Circle
            painter.setBrush(activity["color"])
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(line_x - 6, y_offset + 9, 12, 12)

            # Title
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            painter.drawText(50, y_offset + 20, activity["title"])

            # Time
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(50, y_offset + 38, activity["time"])

            y_offset += 60


# ============================================================================
# STAT PROGRESS BAR
# ============================================================================

class StatProgressBar(QFrame):
    """İstatistikli progress bar"""

    def __init__(self, label="", current=0, target=100, color="#5858D6", parent=None):
        super().__init__(parent)
        self.label = label
        self.current = current
        self.target = target
        self.color = QColor(color)
        self.setMinimumHeight(60)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        # Header (label + value)
        header = QHBoxLayout()

        label_widget = QLabel(self.label)
        label_widget.setStyleSheet("""
            font-size: 13px;
            color: white;
            font-weight: 500;
        """)

        self.value_label = QLabel(f"{self.current}/{self.target}")
        self.value_label.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 180);
            font-weight: 600;
        """)

        header.addWidget(label_widget)
        header.addStretch()
        header.addWidget(self.value_label)

        layout.addLayout(header)

        # Progress bar (custom paint)
        self.progress_widget = QWidget()
        self.progress_widget.setFixedHeight(8)
        layout.addWidget(self.progress_widget)

    def set_progress(self, current, target=None):
        """Progress'i güncelle"""
        self.current = current
        if target:
            self.target = target
        self.value_label.setText(f"{self.current}/{self.target}")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.setBrush(QColor(30, 30, 50))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        # Progress bar area
        bar_y = self.height() - 18
        bar_height = 8
        bar_width = self.width() - 30

        # Background bar
        painter.setBrush(QColor(50, 50, 70))
        painter.drawRoundedRect(15, bar_y, bar_width, bar_height, 4, 4)

        # Progress
        if self.target > 0:
            progress_width = int((self.current / self.target) * bar_width)

            # Gradient
            gradient = QLinearGradient(15, bar_y, 15 + progress_width, bar_y)
            gradient.setColorAt(0.0, self.color)
            gradient.setColorAt(1.0, QColor(self.color.red() + 30,
                                           self.color.green() + 30,
                                           self.color.blue() + 30))

            painter.setBrush(gradient)
            painter.drawRoundedRect(15, bar_y, progress_width, bar_height, 4, 4)


# ============================================================================
# LIVE STATS WIDGET
# ============================================================================

class LiveStatsWidget(QFrame):
    """Canlı istatistikler widget'ı"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("liveStats")
        self.setMinimumHeight(300)

        self.data_points = []
        self.max_points = 50

        self.setup_ui()
        self.start_simulation()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("📈 Canlı Performans")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(title)

        # Chart area
        self.chart_widget = QWidget()
        self.chart_widget.setMinimumHeight(200)
        layout.addWidget(self.chart_widget)

    def start_simulation(self):
        """Simulasyon başlat (gerçek veri yerine)"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.add_random_data)
        self.timer.start(1000)  # Her saniye

    def add_random_data(self):
        """Rastgele veri ekle"""
        value = random.randint(30, 100)
        self.data_points.append(value)

        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)

        self.update()

    def add_data(self, value):
        """Gerçek veri ekle"""
        self.data_points.append(value)
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.data_points or len(self.data_points) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Chart area
        chart_rect = self.chart_widget.geometry()
        padding = 10

        # Scale
        min_val = min(self.data_points)
        max_val = max(self.data_points)
        value_range = max_val - min_val if max_val != min_val else 1

        # Points
        points = []
        step = (chart_rect.width() - 2 * padding) / (len(self.data_points) - 1)

        for i, value in enumerate(self.data_points):
            x = chart_rect.x() + padding + i * step
            y = (chart_rect.y() + chart_rect.height() - padding -
                 ((value - min_val) / value_range) * (chart_rect.height() - 2 * padding))
            points.append(QPointF(x, y))

        # Gradient fill
        path = QPainterPath()
        path.moveTo(points[0].x(), chart_rect.bottom())
        for point in points:
            path.lineTo(point)
        path.lineTo(points[-1].x(), chart_rect.bottom())
        path.closeSubpath()

        gradient = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        gradient.setColorAt(0.0, QColor(88, 88, 214, 150))
        gradient.setColorAt(1.0, QColor(88, 88, 214, 0))
        painter.fillPath(path, gradient)

        # Line
        pen = QPen(QColor(88, 88, 214), 3)
        painter.setPen(pen)
        polygon = QPolygonF(points)
        painter.drawPolyline(polygon)


# Export functions
def create_metric_card(title, value, change, icon, color):
    """Metric card oluştur"""
    return MetricCard(title, value, change, icon, color)


def create_sparkline(data, color):
    """Sparkline oluştur"""
    return SparklineChart(data, color)


def create_donut_chart(percentage, color, label):
    """Donut chart oluştur"""
    chart = DonutChart(percentage, color, label)
    chart.set_percentage(percentage)  # Animasyonu başlat
    return chart
