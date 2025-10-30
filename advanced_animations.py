# -*- coding: utf-8 -*-
"""
Advanced Animations System
İleri seviye animasyon ve efekt kütüphanesi
"""

from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import (
    QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup,
    QEasingCurve, Qt, QTimer, QPoint, QRect, QSize, QObject, Signal
)
from PySide6.QtGui import QPainter, QColor, QPen
import math
import random


# ============================================================================
# ANIMATION PRESETS
# ============================================================================

class AnimationPresets:
    """Hazır animasyon paketleri"""

    @staticmethod
    def fade_in(widget, duration=300):
        """Fade in animasyonu"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        return anim

    @staticmethod
    def fade_out(widget, duration=300):
        """Fade out animasyonu"""
        effect = widget.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        return anim

    @staticmethod
    def slide_in_from_left(widget, duration=400):
        """Soldan slide in"""
        start_pos = widget.pos()
        widget.move(start_pos.x() - widget.width(), start_pos.y())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.OutBack)
        return anim

    @staticmethod
    def slide_in_from_right(widget, duration=400):
        """Sağdan slide in"""
        start_pos = widget.pos()
        widget.move(start_pos.x() + widget.width(), start_pos.y())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.OutBack)
        return anim

    @staticmethod
    def slide_in_from_top(widget, duration=400):
        """Üstten slide in"""
        start_pos = widget.pos()
        widget.move(start_pos.x(), start_pos.y() - widget.height())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        return anim

    @staticmethod
    def slide_in_from_bottom(widget, duration=400):
        """Alttan slide in"""
        start_pos = widget.pos()
        widget.move(start_pos.x(), start_pos.y() + widget.height())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        return anim

    @staticmethod
    def scale_in(widget, duration=300):
        """Scale (büyüme) animasyonu"""
        anim = QPropertyAnimation(widget, b"size")
        anim.setDuration(duration)
        anim.setStartValue(QSize(0, 0))
        anim.setEndValue(widget.size())
        anim.setEasingCurve(QEasingCurve.OutElastic)
        return anim

    @staticmethod
    def bounce(widget, duration=600):
        """Bounce (zıplama) animasyonu"""
        start_pos = widget.pos()
        bounce_height = 30

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(start_pos)
        anim.setKeyValueAt(0.5, QPoint(start_pos.x(), start_pos.y() - bounce_height))
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        return anim

    @staticmethod
    def shake(widget, duration=500):
        """Shake (sallanma) animasyonu"""
        start_pos = widget.pos()
        shake_distance = 10

        anim = QSequentialAnimationGroup()

        for i in range(4):
            move_right = QPropertyAnimation(widget, b"pos")
            move_right.setDuration(duration // 8)
            move_right.setEndValue(QPoint(start_pos.x() + shake_distance, start_pos.y()))

            move_left = QPropertyAnimation(widget, b"pos")
            move_left.setDuration(duration // 8)
            move_left.setEndValue(QPoint(start_pos.x() - shake_distance, start_pos.y()))

            anim.addAnimation(move_right)
            anim.addAnimation(move_left)

        # Son pozisyon
        move_center = QPropertyAnimation(widget, b"pos")
        move_center.setDuration(duration // 8)
        move_center.setEndValue(start_pos)
        anim.addAnimation(move_center)

        return anim

    @staticmethod
    def pulse(widget, duration=800):
        """Pulse (nabız) animasyonu - boyut değişimi"""
        original_size = widget.size()
        scale_factor = 1.1

        grow = QPropertyAnimation(widget, b"size")
        grow.setDuration(duration // 2)
        grow.setStartValue(original_size)
        grow.setEndValue(QSize(int(original_size.width() * scale_factor),
                              int(original_size.height() * scale_factor)))
        grow.setEasingCurve(QEasingCurve.OutCubic)

        shrink = QPropertyAnimation(widget, b"size")
        shrink.setDuration(duration // 2)
        shrink.setStartValue(QSize(int(original_size.width() * scale_factor),
                                   int(original_size.height() * scale_factor)))
        shrink.setEndValue(original_size)
        shrink.setEasingCurve(QEasingCurve.InCubic)

        anim = QSequentialAnimationGroup()
        anim.addAnimation(grow)
        anim.addAnimation(shrink)
        return anim

    @staticmethod
    def rotate_flip(widget, duration=600):
        """Rotate flip animasyonu (simüle)"""
        # QWidget rotate desteği sınırlı, resize trick kullanıyoruz
        original_size = widget.size()

        shrink = QPropertyAnimation(widget, b"size")
        shrink.setDuration(duration // 2)
        shrink.setStartValue(original_size)
        shrink.setEndValue(QSize(0, original_size.height()))
        shrink.setEasingCurve(QEasingCurve.InCubic)

        grow = QPropertyAnimation(widget, b"size")
        grow.setDuration(duration // 2)
        grow.setStartValue(QSize(0, original_size.height()))
        grow.setEndValue(original_size)
        grow.setEasingCurve(QEasingCurve.OutCubic)

        anim = QSequentialAnimationGroup()
        anim.addAnimation(shrink)
        anim.addAnimation(grow)
        return anim


# ============================================================================
# PARTICLE EFFECTS
# ============================================================================

class Particle:
    """Tek bir particle"""

    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx  # Velocity X
        self.vy = vy  # Velocity Y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.alpha = 255

    def update(self, dt=1):
        """Particle'ı güncelle"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.2  # Gravity
        self.age += dt
        self.alpha = max(0, 255 * (1 - self.age / self.lifetime))

    def is_dead(self):
        """Particle öldü mü?"""
        return self.age >= self.lifetime


class ParticleEmitter(QWidget):
    """Particle emitter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)

    def emit_particles(self, x, y, count=20, color=None):
        """Particle'ları yay"""
        color = color or QColor(88, 88, 214)

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 5  # Yukarı doğru bias

            size = random.randint(3, 8)
            lifetime = random.randint(30, 60)

            particle = Particle(x, y, vx, vy, color, size, lifetime)
            self.particles.append(particle)

    def start(self):
        """Particle animasyonunu başlat"""
        self.timer.start(16)  # 60 FPS

    def stop(self):
        """Particle animasyonunu durdur"""
        self.timer.stop()
        self.particles.clear()

    def update_particles(self):
        """Tüm particle'ları güncelle"""
        # Update
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

        # Redraw
        self.update()

        # Stop timer if no particles
        if not self.particles:
            self.timer.stop()

    def paintEvent(self, event):
        """Particle'ları çiz"""
        if not self.particles:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for particle in self.particles:
            color = QColor(particle.color)
            color.setAlpha(int(particle.alpha))
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)

            painter.drawEllipse(
                int(particle.x - particle.size / 2),
                int(particle.y - particle.size / 2),
                int(particle.size),
                int(particle.size)
            )


# ============================================================================
# LOADING ANIMATIONS
# ============================================================================

class WaveLoader(QWidget):
    """Dalga animasyonlu loader"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = 0
        self.setFixedSize(200, 60)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)

    def start(self):
        self.timer.start(30)

    def stop(self):
        self.timer.stop()

    def advance(self):
        self.offset = (self.offset + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 5 dalga çubuğu
        bar_width = 10
        bar_spacing = 15
        max_height = 50

        for i in range(5):
            x = 50 + i * (bar_width + bar_spacing)

            # Sinüs dalgası
            phase = (self.offset + i * 45) % 360
            height = max_height * (0.3 + 0.7 * abs(math.sin(math.radians(phase))))

            y = (self.height() - height) / 2

            # Gradient
            from PySide6.QtGui import QLinearGradient
            gradient = QLinearGradient(0, y, 0, y + height)
            gradient.setColorAt(0.0, QColor(88, 88, 214))
            gradient.setColorAt(1.0, QColor(48, 162, 76))

            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), bar_width, int(height), 5, 5)


class RippleEffect(QWidget):
    """Ripple (dalga) efekti"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ripples = []  # (x, y, radius, alpha)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ripples)

    def create_ripple(self, x, y):
        """Yeni ripple oluştur"""
        self.ripples.append([x, y, 0, 255])
        if not self.timer.isActive():
            self.timer.start(16)

    def update_ripples(self):
        """Ripple'ları güncelle"""
        for ripple in self.ripples[:]:
            ripple[2] += 5  # Radius artır
            ripple[3] -= 8  # Alpha azalt

            if ripple[3] <= 0:
                self.ripples.remove(ripple)

        self.update()

        if not self.ripples:
            self.timer.stop()

    def paintEvent(self, event):
        if not self.ripples:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for x, y, radius, alpha in self.ripples:
            color = QColor(88, 88, 214, max(0, int(alpha)))
            pen = QPen(color, 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(int(x - radius), int(y - radius),
                               int(radius * 2), int(radius * 2))


# ============================================================================
# TRANSITION EFFECTS
# ============================================================================

class PageTransition:
    """Sayfa geçiş efektleri"""

    @staticmethod
    def fade_transition(old_widget, new_widget, duration=300):
        """Fade geçiş"""
        # Fade out old
        fade_out = AnimationPresets.fade_out(old_widget, duration)

        # Fade in new
        new_widget.setVisible(True)
        fade_in = AnimationPresets.fade_in(new_widget, duration)

        # Parallel
        group = QParallelAnimationGroup()
        group.addAnimation(fade_out)
        group.addAnimation(fade_in)

        fade_out.finished.connect(lambda: old_widget.setVisible(False))

        return group

    @staticmethod
    def slide_transition(old_widget, new_widget, direction="left", duration=400):
        """Slide geçiş"""
        # Old widget slide out
        old_end_x = -old_widget.width() if direction == "left" else old_widget.width()
        old_slide = QPropertyAnimation(old_widget, b"pos")
        old_slide.setDuration(duration)
        old_slide.setEndValue(QPoint(old_end_x, old_widget.pos().y()))
        old_slide.setEasingCurve(QEasingCurve.InOutCubic)

        # New widget slide in
        new_start_x = new_widget.width() if direction == "left" else -new_widget.width()
        new_widget.move(new_start_x, new_widget.pos().y())
        new_widget.setVisible(True)

        new_slide = QPropertyAnimation(new_widget, b"pos")
        new_slide.setDuration(duration)
        new_slide.setEndValue(QPoint(0, new_widget.pos().y()))
        new_slide.setEasingCurve(QEasingCurve.InOutCubic)

        # Parallel
        group = QParallelAnimationGroup()
        group.addAnimation(old_slide)
        group.addAnimation(new_slide)

        old_slide.finished.connect(lambda: old_widget.setVisible(False))

        return group


# ============================================================================
# ANIMATION MANAGER
# ============================================================================

class AnimationManager(QObject):
    """Animasyon yöneticisi"""

    animation_started = Signal(str)
    animation_finished = Signal(str)

    def __init__(self):
        super().__init__()
        self.animations = {}  # name -> animation
        self.active_count = 0

    def add_animation(self, name, animation):
        """Animasyon ekle"""
        self.animations[name] = animation
        animation.finished.connect(lambda: self.on_animation_finished(name))

    def start(self, name):
        """Animasyonu başlat"""
        if name in self.animations:
            self.animations[name].start()
            self.active_count += 1
            self.animation_started.emit(name)

    def stop(self, name):
        """Animasyonu durdur"""
        if name in self.animations:
            self.animations[name].stop()

    def on_animation_finished(self, name):
        """Animasyon bittiğinde"""
        self.active_count = max(0, self.active_count - 1)
        self.animation_finished.emit(name)

    def is_animating(self):
        """Herhangi bir animasyon aktif mi?"""
        return self.active_count > 0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def animate_widget_entrance(widget, style="fade"):
    """Widget'ın giriş animasyonunu yap"""
    animations = {
        "fade": AnimationPresets.fade_in,
        "slide_left": AnimationPresets.slide_in_from_left,
        "slide_right": AnimationPresets.slide_in_from_right,
        "slide_top": AnimationPresets.slide_in_from_top,
        "slide_bottom": AnimationPresets.slide_in_from_bottom,
        "scale": AnimationPresets.scale_in,
        "bounce": AnimationPresets.bounce,
    }

    anim_func = animations.get(style, AnimationPresets.fade_in)
    anim = anim_func(widget)
    anim.start()
    return anim


def animate_widget_exit(widget, style="fade", callback=None):
    """Widget'ın çıkış animasyonunu yap"""
    anim = AnimationPresets.fade_out(widget)

    if callback:
        anim.finished.connect(callback)

    anim.start()
    return anim


def create_staggered_animation(widgets, anim_func, delay=50):
    """Ardışık (staggered) animasyon oluştur"""
    group = QSequentialAnimationGroup()

    for i, widget in enumerate(widgets):
        anim = anim_func(widget)

        # Delay ekle
        if i > 0:
            pause = QPropertyAnimation(widget, b"pos")
            pause.setDuration(delay)
            group.addAnimation(pause)

        group.addAnimation(anim)

    return group
