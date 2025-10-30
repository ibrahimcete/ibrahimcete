# -*- coding: utf-8 -*-
"""
Modern UI Components Library
Gelişmiş widget'lar ve animasyonlar için bileşen kütüphanesi
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QGraphicsBlurEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QTimer, QPoint, QRect, QSize, Signal, QObject
)
from PySide6.QtGui import (
    QPainter, QColor, QLinearGradient, QRadialGradient, QPen, QBrush,
    QFont, QPainterPath, QPixmap, QConicalGradient
)
import math
import random


# ============================================================================
# MODERN CARD COMPONENTS
# ============================================================================

class GlassCard(QFrame):
    """Glassmorphism efektli modern kart"""

    def __init__(self, title="", subtitle="", color=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.base_color = color or QColor(255, 255, 255, 30)
        self.hover_scale = 1.0

        self.setMinimumHeight(140)
        self.setup_ui()
        self.setup_effects()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)

        # Subtitle
        self.subtitle_label = QLabel(self.subtitle)
        self.subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: rgba(255, 255, 255, 180);
        """)

        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()

    def setup_effects(self):
        # Glow effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(25)
        self.glow.setColor(QColor(255, 255, 255, 100))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Glass background
        path = QPainterPath()
        rect = self.rect().adjusted(2, 2, -2, -2)
        path.addRoundedRect(rect, 16, 16)

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 40))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 10))

        painter.fillPath(path, gradient)

        # Border
        pen = QPen(QColor(255, 255, 255, 80), 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

        # Shine effect (top left)
        shine = QLinearGradient(0, 0, self.width(), 0)
        shine.setColorAt(0.0, QColor(255, 255, 255, 60))
        shine.setColorAt(0.3, QColor(255, 255, 255, 0))
        shine_rect = QRect(0, 0, self.width() // 2, 3)
        painter.fillRect(shine_rect, shine)

    def enterEvent(self, event):
        """Hover animasyonu"""
        self.animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover çıkış animasyonu"""
        self.animate_hover(False)
        super().leaveEvent(event)

    def animate_hover(self, entering):
        # Scale animation
        self.scale_anim = QPropertyAnimation(self, b"geometry")
        self.scale_anim.setDuration(200)
        self.scale_anim.setEasingCurve(QEasingCurve.OutCubic)

        current = self.geometry()
        if entering:
            # Büyüt
            scaled = current.adjusted(-5, -5, 5, 5)
            self.glow.setBlurRadius(35)
        else:
            # Küçült
            scaled = current.adjusted(5, 5, -5, -5)
            self.glow.setBlurRadius(25)

        self.scale_anim.setStartValue(current)
        self.scale_anim.setEndValue(scaled)
        self.scale_anim.start()


class NeumorphicCard(QFrame):
    """Neumorphism (Soft UI) efektli kart"""

    def __init__(self, content="", color=None, parent=None):
        super().__init__(parent)
        self.content = content
        self.bg_color = color or QColor(45, 45, 60)
        self.pressed = False

        self.setMinimumSize(160, 160)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        self.content_label = QLabel(self.content)
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("""
            font-size: 14px;
            color: white;
            font-weight: 500;
        """)

        layout.addWidget(self.content_label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)

        if not self.pressed:
            # Çıkık görünüm (normal)
            # Açık gölge (sol-üst)
            painter.setPen(Qt.NoPen)
            light = QColor(self.bg_color.red() + 30, self.bg_color.green() + 30,
                          self.bg_color.blue() + 30, 120)
            painter.setBrush(light)
            painter.drawRoundedRect(rect.adjusted(-6, -6, 0, 0), 20, 20)

            # Koyu gölge (sağ-alt)
            dark = QColor(self.bg_color.red() - 30, self.bg_color.green() - 30,
                         self.bg_color.blue() - 30, 120)
            painter.setBrush(dark)
            painter.drawRoundedRect(rect.adjusted(0, 0, 6, 6), 20, 20)
        else:
            # Basık görünüm (pressed)
            # İç gölge efekti
            dark = QColor(self.bg_color.red() - 40, self.bg_color.green() - 40,
                         self.bg_color.blue() - 40, 150)
            painter.setBrush(dark)
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 18, 18)

        # Ana arka plan
        painter.setBrush(self.bg_color)
        painter.drawRoundedRect(rect, 20, 20)

    def mousePressEvent(self, event):
        self.pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.update()
        super().mouseReleaseEvent(event)


class AnimatedStatCard(QFrame):
    """Animasyonlu istatistik kartı"""

    def __init__(self, icon="📊", title="", value=0, color="#5858D6", parent=None):
        super().__init__(parent)
        self.icon = icon
        self.title = title
        self.current_value = 0
        self.target_value = value
        self.color = QColor(color)

        self.setFixedHeight(130)
        self.setup_ui()
        self.animate_value()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # Icon + Title
        header = QHBoxLayout()
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 32px;")

        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 200);
            font-weight: 500;
        """)

        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()

        # Value
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
        """)

        # Trend indicator
        self.trend_label = QLabel("↗ +12%")
        self.trend_label.setStyleSheet("""
            font-size: 11px;
            color: #4CAF50;
            font-weight: 500;
        """)

        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addWidget(self.trend_label)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(self.color)
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, self.color)
        gradient.setColorAt(1.0, QColor(self.color.red() - 40,
                                       self.color.green() - 40,
                                       self.color.blue() - 40))

        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)
        painter.fillPath(path, gradient)

        # Decorative circle
        painter.setOpacity(0.1)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.width() - 60, -20, 120, 120)

    def animate_value(self):
        """Değeri animasyonlu şekilde güncelle"""
        self.value_timer = QTimer(self)
        self.value_timer.timeout.connect(self._update_value)
        self.value_timer.start(30)  # 30ms

    def _update_value(self):
        if self.current_value < self.target_value:
            increment = max(1, (self.target_value - self.current_value) // 20)
            self.current_value = min(self.current_value + increment, self.target_value)
            self.value_label.setText(str(self.current_value))
        else:
            self.value_timer.stop()

    def update_value(self, new_value):
        """Yeni değer set et ve animasyon başlat"""
        self.target_value = new_value
        self.animate_value()


# ============================================================================
# MODERN BUTTONS
# ============================================================================

class GradientButton(QPushButton):
    """Gradient arka planlı modern buton"""

    def __init__(self, text="", icon="", colors=None, parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.colors = colors or ["#667eea", "#764ba2"]
        self.hover_offset = 0

        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_effects()

    def setup_effects(self):
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        # Gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(self.colors[0]))
        gradient.setColorAt(1.0, QColor(self.colors[1]))

        # Hover efekti
        if self.underMouse():
            # Daha parlak
            gradient.setColorAt(0.0, QColor(self.colors[0]).lighter(115))
            gradient.setColorAt(1.0, QColor(self.colors[1]).lighter(115))

        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, gradient)

        # Text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))

        text = f"{self.icon_text} {self.text()}" if self.icon_text else self.text()
        painter.drawText(rect, Qt.AlignCenter, text)


class FloatingActionButton(QPushButton):
    """Material Design FAB"""

    clicked_signal = Signal()

    def __init__(self, icon="➕", color="#FF4081", parent=None):
        super().__init__(icon, parent)
        self.base_color = QColor(color)
        self.setFixedSize(56, 56)
        self.setCursor(Qt.PointingHandCursor)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Circle
        color = self.base_color.lighter(110) if self.underMouse() else self.base_color
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect().adjusted(4, 4, -4, -4))

        # Icon
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 20))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


# ============================================================================
# LOADING & PROGRESS
# ============================================================================

class CircularProgress(QWidget):
    """Dairesel loading animasyonu"""

    def __init__(self, size=64, color="#5858D6", parent=None):
        super().__init__(parent)
        self.angle = 0
        self.color = QColor(color)
        self.setFixedSize(size, size)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)

    def start(self):
        self.timer.start(16)  # 60 FPS

    def stop(self):
        self.timer.stop()

    def rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Çember
        size = min(self.width(), self.height())
        rect = QRect(4, 4, size - 8, size - 8)

        # Gradient
        gradient = QConicalGradient(self.width() // 2, self.height() // 2, self.angle)
        gradient.setColorAt(0.0, self.color)
        gradient.setColorAt(0.5, QColor(self.color.red(), self.color.green(),
                                       self.color.blue(), 50))
        gradient.setColorAt(1.0, self.color)

        pen = QPen(gradient, 4, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, self.angle * 16, 280 * 16)


class PulseLoader(QWidget):
    """Pulse animasyonlu loader"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scale = 1.0
        self.growing = True
        self.setFixedSize(40, 40)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pulse)

    def start(self):
        self.timer.start(30)

    def stop(self):
        self.timer.stop()

    def pulse(self):
        if self.growing:
            self.scale += 0.05
            if self.scale >= 1.3:
                self.growing = False
        else:
            self.scale -= 0.05
            if self.scale <= 0.8:
                self.growing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()
        radius = int(15 * self.scale)

        # Gradient
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(88, 88, 214, 200))
        gradient.setColorAt(1.0, QColor(88, 88, 214, 50))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)


# ============================================================================
# NOTIFICATIONS
# ============================================================================

class ToastNotification(QFrame):
    """Modern toast bildirim"""

    def __init__(self, message="", type="info", parent=None):
        super().__init__(parent)
        self.message = message
        self.type = type  # info, success, warning, error

        self.setup_ui()
        self.setup_animation()

        # Auto-hide
        QTimer.singleShot(3000, self.hide_toast)

    def setup_ui(self):
        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        # Icon
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        icon_label = QLabel(icons.get(self.type, "ℹ️"))
        icon_label.setStyleSheet("font-size: 24px;")

        # Message
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 500;
        """)
        msg_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(msg_label, 1)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Color based on type
        colors = {
            "info": QColor(33, 150, 243),
            "success": QColor(76, 175, 80),
            "warning": QColor(255, 152, 0),
            "error": QColor(244, 67, 54)
        }
        color = colors.get(self.type, QColor(33, 150, 243))

        # Glass effect
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 12, 12)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), 230))
        gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 180))

        painter.fillPath(path, gradient)

        # Border
        pen = QPen(QColor(255, 255, 255, 100), 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

    def setup_animation(self):
        # Slide in from top
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()

    def hide_toast(self):
        # Fade out
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.deleteLater)
        self.fade_out.start()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def show_toast(parent, message, type="info"):
    """Toast göster"""
    toast = ToastNotification(message, type, parent)

    # Üst merkeze yerleştir
    parent_rect = parent.rect()
    toast_x = (parent_rect.width() - toast.width()) // 2
    toast.move(toast_x, 20)
    toast.show()

    return toast


def create_glow_effect(color, blur_radius=30):
    """Glow efekti oluştur"""
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur_radius)
    effect.setColor(color)
    effect.setOffset(0, 0)
    return effect
