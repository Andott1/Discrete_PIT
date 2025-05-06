import os
import glob
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QDesktopWidget, QSpacerItem)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QCursor

from LotteryBall import LotteryBall


class SplashScreen(QWidget):
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.load_custom_font()
        
        icon_path = self.asset_manager.load_asset("Assets/Icons/app_icon.ico")
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Welcome to Let's Play Lotto")
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Center and scale window to percent of screen
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = int(screen_width * 0.65)
        window_height = int(screen_height * 0.65)

        self.setFixedSize(window_width, window_height)

        # Load and scale splash image
        splash_path = self.asset_manager.load_asset("Assets/Screens/splash_screen.png")
        splash_image = QPixmap(splash_path)

        if splash_image.isNull():
            print(f"Failed to load image: {splash_path}")
        else:
            print("Splash screen image loaded successfully.")

        scaled_image = splash_image.scaled(window_width, window_height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Image label (background)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(scaled_image)
        self.image_label.setGeometry(0, 0, window_width, window_height)
        self.image_label.setScaledContents(True)

        # Overlay layout on top of image
        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(20, 20, 20, 50)
        overlay_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Start button
        self.start_button = QPushButton("Start Generating", self)
        button_width = int(screen_width * 0.125)
        button_height = int(screen_height * 0.075)
        self.start_button.setFixedSize(button_width, button_height)
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.setVisible(False)
        self.start_button.clicked.connect(self.launch_main)

        # Button styling
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 1),
                                stop: 1 rgba(245, 115, 35, 1));
                color: #FFFFFF;
                border-radius: 25;
                padding: 10px;
                font-family: 'Roboto ExtraBold';
                font-size: 24px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 0.75),
                                stop: 1 rgba(245, 115, 35, 0.75));
                color: rgba(255, 255, 255, 0.75);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 rgba(255, 210, 80, 0.25),
                                stop: 1 rgba(245, 115, 35, 0.25));
                color: rgba(255, 255, 255, 0.25);
            }
        """)

        overlay_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.setLayout(overlay_layout)

        QTimer.singleShot(1000, self.animate_button)


    # Loads custom font in Assets/Fonts folder
    def load_custom_font(self):
        font_dir = self.asset_manager.get_font_dir()
        if not font_dir or not os.path.exists(font_dir):
            print(f"Font directory not found: {font_dir}")
            return

        print(f"Loading fonts from: {font_dir}")
        loaded_families = []

        # Use glob to find all .ttf files recursively
        font_paths = glob.glob(os.path.join(font_dir, '**', '*.ttf'), recursive=True)

        for font_path in font_paths:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font: {font_path} → {families}")
                loaded_families.extend(families)
            else:
                print(f"Failed to load font: {font_path}")

        if loaded_families:
            font = QFont(loaded_families[0] if loaded_families else "Arial")
            QApplication.setFont(font)
            print(f"Application font set to: {loaded_families[0] if loaded_families else 'Arial'}")
        else:
            print("No fonts were loaded.")

    # Simple button animation
    def animate_button(self):
        self.start_button.setVisible(True)
        self.start_button.update()

        self.anim = QPropertyAnimation(self.start_button, b"geometry")
        self.anim.setDuration(500)
        self.anim.setStartValue(QRect(
            self.start_button.x(),
            self.start_button.y() + 50,
            self.start_button.width(),
            self.start_button.height()
        ))
        self.anim.setEndValue(self.start_button.geometry())
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()

    # Splash screen show logic
    def launch_main(self):
        self.close()
        self.main = LotteryBall(asset_manager=self.asset_manager)
        self.main.show()

