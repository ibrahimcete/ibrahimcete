# -*- coding: utf-8 -*-
"""
Design System - Modern UI için tema ve stil yönetimi
Renk paletleri, tipografi, spacing, animasyon ayarları
"""

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtCore import QEasingCurve
from dataclasses import dataclass
from typing import Dict, List
import json


# ============================================================================
# COLOR PALETTES
# ============================================================================

class ColorPalette:
    """Modern renk paleti"""

    # Primary Colors
    PRIMARY = "#5858D6"  # Mor
    PRIMARY_LIGHT = "#7B7BE8"
    PRIMARY_DARK = "#3D3DA8"

    # Secondary Colors
    SECONDARY = "#30A24C"  # Yeşil
    SECONDARY_LIGHT = "#4CBF6D"
    SECONDARY_DARK = "#257A3A"

    # Accent Colors
    ACCENT = "#CA7137"  # Turuncu
    ACCENT_LIGHT = "#E08F5E"
    ACCENT_DARK = "#A85828"

    ERROR = "#F44336"
    WARNING = "#FF9800"
    SUCCESS = "#4CAF50"
    INFO = "#2196F3"

    # Neutral Colors (Dark Theme)
    BACKGROUND_DARK = "#0F0F1E"
    BACKGROUND_CARD_DARK = "#1A1A2E"
    BACKGROUND_ELEVATED_DARK = "#25253E"

    SURFACE_DARK = "#16162A"
    SURFACE_VARIANT_DARK = "#2A2A3E"

    TEXT_PRIMARY_DARK = "#FFFFFF"
    TEXT_SECONDARY_DARK = "#B0B0C0"
    TEXT_DISABLED_DARK = "#707080"

    BORDER_DARK = "#2A2A3E"
    DIVIDER_DARK = "#202030"

    # Neutral Colors (Light Theme)
    BACKGROUND_LIGHT = "#F5F5F7"
    BACKGROUND_CARD_LIGHT = "#FFFFFF"
    BACKGROUND_ELEVATED_LIGHT = "#FAFAFA"

    SURFACE_LIGHT = "#FFFFFF"
    SURFACE_VARIANT_LIGHT = "#F0F0F2"

    TEXT_PRIMARY_LIGHT = "#1A1A1A"
    TEXT_SECONDARY_LIGHT = "#666666"
    TEXT_DISABLED_LIGHT = "#AAAAAA"

    BORDER_LIGHT = "#E0E0E0"
    DIVIDER_LIGHT = "#F0F0F0"

    # Gradient Collections
    GRADIENTS = {
        "purple_blue": ["#667eea", "#764ba2"],
        "pink_orange": ["#f093fb", "#f5576c"],
        "green_blue": ["#4facfe", "#00f2fe"],
        "orange_red": ["#fa709a", "#fee140"],
        "purple_pink": ["#a8edea", "#fed6e3"],
        "sunset": ["#ff6b6b", "#feca57", "#48dbfb"],
        "ocean": ["#2E3192", "#1BFFFF"],
        "fire": ["#f12711", "#f5af19"],
        "forest": ["#134e5e", "#71b280"],
        "royal": ["#141e30", "#243b55"],
    }

    # Glassmorphism colors
    GLASS_LIGHT = "rgba(255, 255, 255, 0.1)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.2)"
    GLASS_BLUR = 15

    @staticmethod
    def qcolor(hex_color: str, alpha: int = 255) -> QColor:
        """Hex string'i QColor'a çevir"""
        color = QColor(hex_color)
        color.setAlpha(alpha)
        return color

    @staticmethod
    def rgba(hex_color: str, alpha: float = 1.0) -> str:
        """Hex'i RGBA string'e çevir"""
        color = QColor(hex_color)
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"


# ============================================================================
# TYPOGRAPHY
# ============================================================================

@dataclass
class FontStyle:
    """Font stilleri"""
    family: str
    size: int
    weight: int
    letter_spacing: float = 0.0

    def to_qfont(self) -> QFont:
        """QFont'a çevir"""
        font = QFont(self.family, self.size, self.weight)
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.letter_spacing)
        return font


class Typography:
    """Tipografi sistemi"""

    # Font Families
    PRIMARY_FONT = "Segoe UI"
    SECONDARY_FONT = "Roboto"
    MONOSPACE_FONT = "Consolas"

    # Display Styles
    DISPLAY_LARGE = FontStyle(PRIMARY_FONT, 57, QFont.Bold)
    DISPLAY_MEDIUM = FontStyle(PRIMARY_FONT, 45, QFont.Bold)
    DISPLAY_SMALL = FontStyle(PRIMARY_FONT, 36, QFont.Bold)

    # Headline Styles
    HEADLINE_LARGE = FontStyle(PRIMARY_FONT, 32, QFont.Bold)
    HEADLINE_MEDIUM = FontStyle(PRIMARY_FONT, 28, QFont.Bold)
    HEADLINE_SMALL = FontStyle(PRIMARY_FONT, 24, QFont.Bold)

    # Title Styles
    TITLE_LARGE = FontStyle(PRIMARY_FONT, 22, QFont.DemiBold)
    TITLE_MEDIUM = FontStyle(PRIMARY_FONT, 16, QFont.DemiBold, 0.15)
    TITLE_SMALL = FontStyle(PRIMARY_FONT, 14, QFont.DemiBold, 0.1)

    # Body Styles
    BODY_LARGE = FontStyle(PRIMARY_FONT, 16, QFont.Normal)
    BODY_MEDIUM = FontStyle(PRIMARY_FONT, 14, QFont.Normal, 0.25)
    BODY_SMALL = FontStyle(PRIMARY_FONT, 12, QFont.Normal, 0.4)

    # Label Styles
    LABEL_LARGE = FontStyle(PRIMARY_FONT, 14, QFont.Medium, 0.1)
    LABEL_MEDIUM = FontStyle(PRIMARY_FONT, 12, QFont.Medium, 0.5)
    LABEL_SMALL = FontStyle(PRIMARY_FONT, 11, QFont.Medium, 0.5)

    # Code Style
    CODE = FontStyle(MONOSPACE_FONT, 13, QFont.Normal)


# ============================================================================
# SPACING & LAYOUT
# ============================================================================

class Spacing:
    """Spacing sistemi (8pt grid)"""

    UNIT = 8  # Base unit

    XS = UNIT * 0.5  # 4px
    SM = UNIT * 1    # 8px
    MD = UNIT * 2    # 16px
    LG = UNIT * 3    # 24px
    XL = UNIT * 4    # 32px
    XXL = UNIT * 6   # 48px

    # Container paddings
    CONTAINER_PADDING = MD
    CARD_PADDING = LG
    SECTION_MARGIN = XL

    # Element spacing
    ELEMENT_GAP = SM
    LIST_ITEM_SPACING = SM
    BUTTON_PADDING_H = LG
    BUTTON_PADDING_V = SM


class BorderRadius:
    """Border radius değerleri"""

    NONE = 0
    SM = 4
    MD = 8
    LG = 12
    XL = 16
    XXL = 24
    FULL = 9999  # Pill shape


# ============================================================================
# SHADOWS & EFFECTS
# ============================================================================

class Shadows:
    """Gölge efektleri"""

    @staticmethod
    def elevation_1():
        """Çok hafif gölge"""
        return {
            "blur": 4,
            "offset": (0, 1),
            "color": QColor(0, 0, 0, 50)
        }

    @staticmethod
    def elevation_2():
        """Hafif gölge"""
        return {
            "blur": 8,
            "offset": (0, 2),
            "color": QColor(0, 0, 0, 80)
        }

    @staticmethod
    def elevation_3():
        """Orta gölge"""
        return {
            "blur": 12,
            "offset": (0, 4),
            "color": QColor(0, 0, 0, 100)
        }

    @staticmethod
    def elevation_4():
        """Güçlü gölge"""
        return {
            "blur": 16,
            "offset": (0, 6),
            "color": QColor(0, 0, 0, 120)
        }

    @staticmethod
    def elevation_5():
        """Çok güçlü gölge"""
        return {
            "blur": 24,
            "offset": (0, 8),
            "color": QColor(0, 0, 0, 140)
        }

    @staticmethod
    def glow(color: QColor):
        """Glow efekti"""
        return {
            "blur": 20,
            "offset": (0, 0),
            "color": color
        }


# ============================================================================
# ANIMATIONS
# ============================================================================

class AnimationConfig:
    """Animasyon ayarları"""

    # Durations (ms)
    DURATION_INSTANT = 50
    DURATION_FAST = 150
    DURATION_NORMAL = 250
    DURATION_SLOW = 400
    DURATION_SLOWER = 600

    # Easing curves
    EASE_IN = QEasingCurve.InCubic
    EASE_OUT = QEasingCurve.OutCubic
    EASE_IN_OUT = QEasingCurve.InOutCubic
    EASE_BOUNCE = QEasingCurve.OutBounce
    EASE_ELASTIC = QEasingCurve.OutElastic
    EASE_BACK = QEasingCurve.OutBack

    # Standard animations
    FADE_DURATION = DURATION_NORMAL
    SLIDE_DURATION = DURATION_NORMAL
    SCALE_DURATION = DURATION_FAST
    ROTATE_DURATION = DURATION_SLOW


# ============================================================================
# THEME MANAGER
# ============================================================================

class Theme:
    """Tema yöneticisi"""

    def __init__(self, mode="dark"):
        self.mode = mode  # "dark" veya "light"
        self.colors = ColorPalette()
        self.typography = Typography()
        self.spacing = Spacing()
        self.shadows = Shadows()
        self.animation = AnimationConfig()

    def get_background(self) -> str:
        """Ana arka plan rengi"""
        return self.colors.BACKGROUND_DARK if self.mode == "dark" else self.colors.BACKGROUND_LIGHT

    def get_surface(self) -> str:
        """Yüzey rengi"""
        return self.colors.SURFACE_DARK if self.mode == "dark" else self.colors.SURFACE_LIGHT

    def get_text_primary(self) -> str:
        """Ana metin rengi"""
        return self.colors.TEXT_PRIMARY_DARK if self.mode == "dark" else self.colors.TEXT_PRIMARY_LIGHT

    def get_text_secondary(self) -> str:
        """İkincil metin rengi"""
        return self.colors.TEXT_SECONDARY_DARK if self.mode == "dark" else self.colors.TEXT_SECONDARY_LIGHT

    def get_border(self) -> str:
        """Border rengi"""
        return self.colors.BORDER_DARK if self.mode == "dark" else self.colors.BORDER_LIGHT

    def to_stylesheet(self) -> str:
        """Tema için stylesheet oluştur"""
        return f"""
        QMainWindow, QWidget {{
            background-color: {self.get_background()};
            color: {self.get_text_primary()};
            font-family: {self.typography.PRIMARY_FONT};
            font-size: {self.typography.BODY_MEDIUM.size}px;
        }}

        QFrame[objectName="card"] {{
            background-color: {self.get_surface()};
            border-radius: {BorderRadius.LG}px;
            border: 1px solid {self.get_border()};
        }}

        QPushButton {{
            background-color: {self.colors.PRIMARY};
            color: white;
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {self.spacing.SM}px {self.spacing.LG}px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {self.colors.PRIMARY_LIGHT};
        }}

        QPushButton:pressed {{
            background-color: {self.colors.PRIMARY_DARK};
        }}

        QLineEdit, QTextEdit, QComboBox {{
            background-color: {self.get_surface()};
            color: {self.get_text_primary()};
            border: 1px solid {self.get_border()};
            border-radius: {BorderRadius.SM}px;
            padding: {self.spacing.SM}px;
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {self.colors.PRIMARY};
        }}

        QScrollBar:vertical {{
            background-color: {self.get_surface()};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.colors.PRIMARY};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors.PRIMARY_LIGHT};
        }}

        QTableWidget {{
            background-color: {self.get_surface()};
            border: 1px solid {self.get_border()};
            border-radius: {BorderRadius.MD}px;
            gridline-color: {self.get_border()};
        }}

        QHeaderView::section {{
            background-color: {self.colors.PRIMARY};
            color: white;
            padding: {self.spacing.SM}px;
            border: none;
            font-weight: bold;
        }}

        QTabWidget::pane {{
            border: none;
            background-color: transparent;
        }}

        QTabBar::tab {{
            background-color: {self.get_surface()};
            color: {self.get_text_secondary()};
            border: none;
            border-radius: {BorderRadius.SM}px {BorderRadius.SM}px 0 0;
            padding: {self.spacing.SM}px {self.spacing.LG}px;
            margin-right: {self.spacing.XS}px;
        }}

        QTabBar::tab:selected {{
            background-color: {self.colors.PRIMARY};
            color: white;
        }}

        QTabBar::tab:hover {{
            background-color: {self.colors.PRIMARY_LIGHT};
            color: white;
        }}

        QProgressBar {{
            background-color: {self.get_surface()};
            border: none;
            border-radius: {BorderRadius.SM}px;
            text-align: center;
            color: white;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.colors.PRIMARY},
                stop:1 {self.colors.SECONDARY}
            );
            border-radius: {BorderRadius.SM}px;
        }}

        QToolTip {{
            background-color: {self.colors.SURFACE_DARK};
            color: white;
            border: 1px solid {self.colors.PRIMARY};
            border-radius: {BorderRadius.SM}px;
            padding: {self.spacing.SM}px;
        }}
        """

    def toggle_mode(self):
        """Dark/Light mode'u değiştir"""
        self.mode = "light" if self.mode == "dark" else "dark"

    def export_config(self) -> dict:
        """Tema konfigürasyonunu dışa aktar"""
        return {
            "mode": self.mode,
            "primary_color": self.colors.PRIMARY,
            "secondary_color": self.colors.SECONDARY,
            "accent_color": self.colors.ACCENT,
        }

    def import_config(self, config: dict):
        """Tema konfigürasyonunu içe aktar"""
        if "mode" in config:
            self.mode = config["mode"]
        if "primary_color" in config:
            self.colors.PRIMARY = config["primary_color"]
        if "secondary_color" in config:
            self.colors.SECONDARY = config["secondary_color"]
        if "accent_color" in config:
            self.colors.ACCENT = config["accent_color"]


# ============================================================================
# PRESET THEMES
# ============================================================================

class PresetThemes:
    """Hazır temalar"""

    @staticmethod
    def dark_blue():
        theme = Theme("dark")
        theme.colors.PRIMARY = "#2196F3"
        theme.colors.SECONDARY = "#00BCD4"
        theme.colors.ACCENT = "#FF5722"
        return theme

    @staticmethod
    def dark_purple():
        theme = Theme("dark")
        theme.colors.PRIMARY = "#9C27B0"
        theme.colors.SECONDARY = "#E91E63"
        theme.colors.ACCENT = "#FFC107"
        return theme

    @staticmethod
    def dark_green():
        theme = Theme("dark")
        theme.colors.PRIMARY = "#4CAF50"
        theme.colors.SECONDARY = "#8BC34A"
        theme.colors.ACCENT = "#FF9800"
        return theme

    @staticmethod
    def light_modern():
        theme = Theme("light")
        theme.colors.PRIMARY = "#6366F1"
        theme.colors.SECONDARY = "#10B981"
        theme.colors.ACCENT = "#F59E0B"
        return theme

    @staticmethod
    def cyberpunk():
        theme = Theme("dark")
        theme.colors.PRIMARY = "#FF00FF"
        theme.colors.SECONDARY = "#00FFFF"
        theme.colors.ACCENT = "#FFFF00"
        theme.colors.BACKGROUND_DARK = "#0A0A0A"
        return theme


# Global theme instance
current_theme = Theme("dark")


def get_current_theme() -> Theme:
    """Aktif temayı al"""
    return current_theme


def set_theme(theme: Theme):
    """Aktif temayı değiştir"""
    global current_theme
    current_theme = theme
