# -*- coding: utf-8 -*-
"""
Modern UI Launcher - Ultra-Modern Dashboard Showcase
Yeni tasarım sisteminin tam demo'su
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea, QPushButton, QFrame, QTabWidget,
    QLineEdit, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon

# Modern UI bileşenleri
from modern_ui_components import (
    GlassCard, NeumorphicCard, AnimatedStatCard, GradientButton,
    FloatingActionButton, CircularProgress, PulseLoader,
    ToastNotification, show_toast, create_glow_effect
)

from design_system import (
    Theme, ColorPalette, Typography, Spacing, BorderRadius,
    PresetThemes, get_current_theme, set_theme
)

from advanced_animations import (
    AnimationPresets, ParticleEmitter, WaveLoader, RippleEffect,
    animate_widget_entrance
)

from modern_dashboard import (
    MetricCard, SparklineChart, MiniBarChart, DonutChart,
    ActivityTimeline, StatProgressBar, LiveStatsWidget
)

import random


class ModernUIShowcase(QMainWindow):
    """
    🚀 Ultra-Modern Dashboard Showcase

    Tüm modern UI bileşenlerinin canlı demo'su
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Ultra-Modern Dashboard v4.0")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 900)

        # Tema
        self.theme = PresetThemes.dark_purple()
        set_theme(self.theme)

        # Apply theme
        self.setStyleSheet(self.theme.to_stylesheet())

        # UI oluştur
        self.init_ui()

        # Animasyonlu giriş
        self.setWindowOpacity(0.0)
        fade_in = AnimationPresets.fade_in(self, 800)
        fade_in.start()

        # Particle emitter
        self.particle_emitter = ParticleEmitter(self)
        self.particle_emitter.setGeometry(0, 0, self.width(), self.height())
        self.particle_emitter.raise_()

        # Ripple effect
        self.ripple_effect = RippleEffect(self)
        self.ripple_effect.setGeometry(0, 0, self.width(), self.height())
        self.ripple_effect.raise_()

        # Welcome toast
        QTimer.singleShot(1000, lambda: show_toast(
            self, "🎉 Hoş Geldiniz! Ultra-Modern Dashboard yüklendi.", "success"
        ))

    def init_ui(self):
        """UI'ı oluştur"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Main content
        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")
        tabs.setDocumentMode(True)

        # Tab 1: Modern Dashboard
        dashboard_tab = self.create_dashboard_tab()
        tabs.addTab(dashboard_tab, "📊 Dashboard")

        # Tab 2: Components Showcase
        components_tab = self.create_components_tab()
        tabs.addTab(components_tab, "🎨 Components")

        # Tab 3: Animations Demo
        animations_tab = self.create_animations_tab()
        tabs.addTab(animations_tab, "✨ Animations")

        # Tab 4: Charts & Data
        charts_tab = self.create_charts_tab()
        tabs.addTab(charts_tab, "📈 Charts")

        main_layout.addWidget(tabs)

    def create_top_bar(self):
        """Üst bar oluştur"""
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(70)

        # Glass efekti
        bar.setStyleSheet(f"""
            QFrame#topBar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ColorPalette.rgba(ColorPalette.PRIMARY, 0.3)},
                    stop:0.5 {ColorPalette.rgba(ColorPalette.SECONDARY, 0.3)},
                    stop:1 {ColorPalette.rgba(ColorPalette.ACCENT, 0.3)}
                );
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 10, 30, 10)

        # Logo + Title
        title_label = QLabel("🚀 B2B Otomasyon Motoru")
        title_label.setFont(Typography.HEADLINE_SMALL.to_qfont())
        title_label.setStyleSheet("color: white; font-weight: bold;")

        subtitle = QLabel("v4.0 Ultra-Modern Edition")
        subtitle.setFont(Typography.BODY_SMALL.to_qfont())
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.7);")

        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle)

        # Search bar
        search = QLineEdit()
        search.setPlaceholderText("🔍 Ara...")
        search.setFixedWidth(300)
        search.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: {BorderRadius.MD}px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ColorPalette.PRIMARY};
                background-color: rgba(255, 255, 255, 0.15);
            }}
        """)

        # Action buttons
        notif_btn = FloatingActionButton("🔔", ColorPalette.ACCENT)
        notif_btn.setFixedSize(45, 45)
        notif_btn.clicked.connect(lambda: show_toast(
            self, "📬 3 yeni bildiriminiz var", "info"
        ))

        settings_btn = FloatingActionButton("⚙️", ColorPalette.SECONDARY)
        settings_btn.setFixedSize(45, 45)
        settings_btn.clicked.connect(self.toggle_theme)

        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(search)
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)

        return bar

    def create_dashboard_tab(self):
        """Ana dashboard sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)

        # Animated stat cards
        card1 = AnimatedStatCard("📈", "Toplam Firma", 1247, ColorPalette.PRIMARY)
        card2 = AnimatedStatCard("✅", "Başarılı Email", 856, ColorPalette.SUCCESS)
        card3 = AnimatedStatCard("📊", "Analiz Edilen", 423, ColorPalette.ACCENT)
        card4 = AnimatedStatCard("🎯", "Hedef Oran", 92, ColorPalette.SECONDARY)

        metrics_layout.addWidget(card1)
        metrics_layout.addWidget(card2)
        metrics_layout.addWidget(card3)
        metrics_layout.addWidget(card4)

        layout.addLayout(metrics_layout)

        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Live stats
        live_stats = LiveStatsWidget()
        charts_layout.addWidget(live_stats, 2)

        # Activity timeline
        timeline_frame = QFrame()
        timeline_frame.setObjectName("card")
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.setContentsMargins(20, 20, 20, 20)

        timeline_title = QLabel("📋 Son Aktiviteler")
        timeline_title.setFont(Typography.TITLE_MEDIUM.to_qfont())
        timeline_title.setStyleSheet("color: white; font-weight: bold;")

        timeline = ActivityTimeline()
        timeline.add_activity("Yeni firma eklendi", "5 dk önce", "✅", ColorPalette.SUCCESS)
        timeline.add_activity("Email kampanyası gönderildi", "12 dk önce", "📧", ColorPalette.PRIMARY)
        timeline.add_activity("Analiz tamamlandı", "25 dk önce", "📊", ColorPalette.ACCENT)
        timeline.add_activity("Rapor oluşturuldu", "1 saat önce", "📄", ColorPalette.SECONDARY)

        timeline_layout.addWidget(timeline_title)
        timeline_layout.addWidget(timeline)

        charts_layout.addWidget(timeline_frame, 1)

        layout.addLayout(charts_layout)

        # Progress bars
        progress_title = QLabel("🎯 Hedef İlerleme")
        progress_title.setFont(Typography.TITLE_MEDIUM.to_qfont())
        progress_title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(progress_title)

        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(15)

        pb1 = StatProgressBar("Aylık Firma Hedefi", 847, 1000, ColorPalette.PRIMARY)
        pb2 = StatProgressBar("Email Gönderim Hedefi", 1203, 1500, ColorPalette.SECONDARY)
        pb3 = StatProgressBar("Analiz Hedefi", 678, 800, ColorPalette.ACCENT)

        progress_layout.addWidget(pb1)
        progress_layout.addWidget(pb2)
        progress_layout.addWidget(pb3)

        layout.addLayout(progress_layout)
        layout.addStretch()

        return widget

    def create_components_tab(self):
        """Bileşenler showcase sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Section: Cards
        cards_title = QLabel("💎 Modern Cards")
        cards_title.setFont(Typography.HEADLINE_SMALL.to_qfont())
        cards_title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(cards_title)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        glass_card = GlassCard(
            "Glassmorphism Card",
            "Modern cam efektli kart tasarımı",
            ColorPalette.qcolor(ColorPalette.PRIMARY)
        )
        neuro_card = NeumorphicCard("Neumorphic Design\n\nSoft UI elementi")
        metric_card = MetricCard(
            "Metrik Kartı",
            "2,547",
            "+18%",
            "📊",
            ColorPalette.ACCENT
        )

        cards_layout.addWidget(glass_card)
        cards_layout.addWidget(neuro_card)
        cards_layout.addWidget(metric_card)

        layout.addLayout(cards_layout)

        # Section: Buttons
        buttons_title = QLabel("🎯 Modern Buttons")
        buttons_title.setFont(Typography.HEADLINE_SMALL.to_qfont())
        buttons_title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(buttons_title)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        btn1 = GradientButton("Primary Action", "🚀", ColorPalette.GRADIENTS["purple_blue"])
        btn1.clicked.connect(lambda: show_toast(self, "Primary buton tıklandı!", "info"))

        btn2 = GradientButton("Success Action", "✅", ColorPalette.GRADIENTS["green_blue"])
        btn2.clicked.connect(lambda: show_toast(self, "Başarılı!", "success"))

        btn3 = GradientButton("Warning Action", "⚠️", ColorPalette.GRADIENTS["orange_red"])
        btn3.clicked.connect(lambda: show_toast(self, "Dikkat!", "warning"))

        buttons_layout.addWidget(btn1)
        buttons_layout.addWidget(btn2)
        buttons_layout.addWidget(btn3)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Section: Loaders
        loaders_title = QLabel("⏳ Loading Animations")
        loaders_title.setFont(Typography.HEADLINE_SMALL.to_qfont())
        loaders_title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(loaders_title)

        loaders_layout = QHBoxLayout()
        loaders_layout.setSpacing(30)

        circular = CircularProgress(80, ColorPalette.PRIMARY)
        circular.start()

        pulse = PulseLoader()
        pulse.start()

        wave = WaveLoader()
        wave.start()

        loaders_layout.addWidget(circular)
        loaders_layout.addWidget(pulse)
        loaders_layout.addWidget(wave)
        loaders_layout.addStretch()

        layout.addLayout(loaders_layout)
        layout.addStretch()

        return widget

    def create_animations_tab(self):
        """Animasyonlar demo sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        title = QLabel("✨ Animasyon Galerisi")
        title.setFont(Typography.HEADLINE_MEDIUM.to_qfont())
        title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title)

        # Animasyon butonları
        grid = QGridLayout()
        grid.setSpacing(15)

        animations = [
            ("Fade In", "fade"),
            ("Slide Left", "slide_left"),
            ("Slide Right", "slide_right"),
            ("Slide Top", "slide_top"),
            ("Slide Bottom", "slide_bottom"),
            ("Scale", "scale"),
            ("Bounce", "bounce"),
            ("Shake", "shake"),
            ("Pulse", "pulse"),
        ]

        self.demo_widget = QFrame()
        self.demo_widget.setFixedSize(200, 200)
        self.demo_widget.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {ColorPalette.PRIMARY},
                stop:1 {ColorPalette.SECONDARY}
            );
            border-radius: {BorderRadius.XL}px;
        """)

        demo_label = QLabel("🎭\nDemo\nWidget", self.demo_widget)
        demo_label.setAlignment(Qt.AlignCenter)
        demo_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        demo_label.setGeometry(0, 0, 200, 200)

        row, col = 0, 0
        for name, anim_type in animations:
            btn = GradientButton(name, "", ColorPalette.GRADIENTS["purple_pink"])
            btn.clicked.connect(lambda checked, at=anim_type: self.play_animation(at))
            grid.addWidget(btn, row, col)

            col += 1
            if col > 2:
                col = 0
                row += 1

        # Particle button
        particle_btn = GradientButton("🎆 Particle Explosion", "", ColorPalette.GRADIENTS["fire"])
        particle_btn.clicked.connect(self.trigger_particles)
        grid.addWidget(particle_btn, row, col)

        layout.addLayout(grid)

        # Demo widget area
        demo_area = QHBoxLayout()
        demo_area.addStretch()
        demo_area.addWidget(self.demo_widget)
        demo_area.addStretch()
        layout.addLayout(demo_area)

        layout.addStretch()

        return widget

    def create_charts_tab(self):
        """Charts showcase sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        title = QLabel("📈 Chart Gallery")
        title.setFont(Typography.HEADLINE_MEDIUM.to_qfont())
        title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title)

        # Row 1: Sparklines
        sparklines_layout = QHBoxLayout()
        sparklines_layout.setSpacing(20)

        for i, color in enumerate([ColorPalette.PRIMARY, ColorPalette.SECONDARY, ColorPalette.ACCENT]):
            frame = QFrame()
            frame.setObjectName("card")
            frame_layout = QVBoxLayout(frame)

            label = QLabel(f"Metrik {i+1}")
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

            data = [random.randint(20, 100) for _ in range(30)]
            sparkline = SparklineChart(data, color)

            frame_layout.addWidget(label)
            frame_layout.addWidget(sparkline)

            sparklines_layout.addWidget(frame)

        layout.addLayout(sparklines_layout)

        # Row 2: Donut charts
        donuts_layout = QHBoxLayout()
        donuts_layout.setSpacing(30)

        donut1 = DonutChart(75, ColorPalette.PRIMARY, "Tamamlanan")
        donut1.set_percentage(75)

        donut2 = DonutChart(62, ColorPalette.SECONDARY, "Devam Eden")
        donut2.set_percentage(62)

        donut3 = DonutChart(88, ColorPalette.ACCENT, "Başarı Oranı")
        donut3.set_percentage(88)

        donuts_layout.addWidget(donut1)
        donuts_layout.addWidget(donut2)
        donuts_layout.addWidget(donut3)
        donuts_layout.addStretch()

        layout.addLayout(donuts_layout)

        # Row 3: Bar chart
        bar_frame = QFrame()
        bar_frame.setObjectName("card")
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.setContentsMargins(20, 20, 20, 20)

        bar_title = QLabel("📊 Haftalık Performans")
        bar_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        bar_chart = MiniBarChart(
            [45, 67, 82, 91, 78, 95, 103],
            [ColorPalette.PRIMARY, ColorPalette.SECONDARY, ColorPalette.ACCENT]
        )

        bar_layout.addWidget(bar_title)
        bar_layout.addWidget(bar_chart)

        layout.addWidget(bar_frame)
        layout.addStretch()

        return widget

    def play_animation(self, anim_type):
        """Animasyon oynat"""
        from advanced_animations import AnimationPresets

        if anim_type == "fade":
            anim = AnimationPresets.fade_in(self.demo_widget, 500)
        elif anim_type == "slide_left":
            anim = AnimationPresets.slide_in_from_left(self.demo_widget)
        elif anim_type == "slide_right":
            anim = AnimationPresets.slide_in_from_right(self.demo_widget)
        elif anim_type == "slide_top":
            anim = AnimationPresets.slide_in_from_top(self.demo_widget)
        elif anim_type == "slide_bottom":
            anim = AnimationPresets.slide_in_from_bottom(self.demo_widget)
        elif anim_type == "scale":
            anim = AnimationPresets.scale_in(self.demo_widget, 600)
        elif anim_type == "bounce":
            anim = AnimationPresets.bounce(self.demo_widget)
        elif anim_type == "shake":
            anim = AnimationPresets.shake(self.demo_widget)
        elif anim_type == "pulse":
            anim = AnimationPresets.pulse(self.demo_widget)
        else:
            return

        anim.start()
        show_toast(self, f"✨ {anim_type.title()} animasyonu oynatılıyor!", "info")

    def trigger_particles(self):
        """Particle patlaması"""
        center_x = self.demo_widget.x() + self.demo_widget.width() // 2
        center_y = self.demo_widget.y() + self.demo_widget.height() // 2

        colors = [
            ColorPalette.qcolor(ColorPalette.PRIMARY),
            ColorPalette.qcolor(ColorPalette.SECONDARY),
            ColorPalette.qcolor(ColorPalette.ACCENT),
        ]

        for color in colors:
            self.particle_emitter.emit_particles(center_x, center_y, 15, color)

        if not self.particle_emitter.timer.isActive():
            self.particle_emitter.start()

        show_toast(self, "🎆 Particle patlaması!", "success")

    def toggle_theme(self):
        """Temayı değiştir"""
        themes = [
            PresetThemes.dark_purple(),
            PresetThemes.dark_blue(),
            PresetThemes.dark_green(),
            PresetThemes.cyberpunk(),
        ]

        current = themes.index(self.theme) if self.theme in themes else 0
        next_index = (current + 1) % len(themes)
        self.theme = themes[next_index]

        set_theme(self.theme)
        self.setStyleSheet(self.theme.to_stylesheet())

        show_toast(self, "🎨 Tema değiştirildi!", "success")

    def mousePressEvent(self, event):
        """Mouse click -> ripple effect"""
        self.ripple_effect.create_ripple(event.pos().x(), event.pos().y())
        super().mousePressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Font
    app.setFont(QFont("Segoe UI", 10))

    # Ana pencere
    window = ModernUIShowcase()
    window.show()

    sys.exit(app.exec())
