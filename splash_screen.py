import os
import sys
import time
from PyQt6.QtWidgets import QApplication, QSplashScreen, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QSize, QEventLoop
from PyQt6.QtGui import QPixmap, QIcon, QFont

def get_main_window_size():
    """Get the size that will be used for the main window"""
    screen = QApplication.primaryScreen()
    screen_size = screen.size()
    
    width = int(screen_size.width() * 0.6)
    height = int(screen_size.height() * 0.75)
    
    return QSize(width, height)

class LotterySplashScreen(QWidget):
    """Custom splash screen with background image and styled button"""
    
    def __init__(self, main_app_callback):
        super().__init__()
        print("Initializing splash screen...")
        self.main_app_callback = main_app_callback
        self.setWindowTitle("Lottery Number Generator")
        self.setWindowFlags(Qt.WindowType.Window) # Remove window frame
        
        # Try to set up the UI, with error handling
        try:
            self.setup_ui()
            print("Splash screen UI setup complete")
        except Exception as e:
            print(f"Error setting up splash screen: {e}")
            # If there's an error, just start the main application
            self.main_app_callback()
            self.close()
        
    def setup_ui(self):
        # Set up the main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Find the splash screen image
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        possible_names = ["splash_screen.png", "splash screen.png", "splash-screen.png", "splash.png"]
        splash_image_path = None
        
        for name in possible_names:
            path = os.path.join(assets_dir, name)
            if os.path.exists(path):
                splash_image_path = path
                print(f"Found splash screen image: {path}")
                break
        
        if not splash_image_path:
            raise FileNotFoundError(f"Splash screen image not found in {assets_dir}")
        
        # Load the splash screen image
        original_pixmap = QPixmap(splash_image_path)
        if original_pixmap.isNull():
            raise ValueError(f"Failed to load splash screen image from {splash_image_path}")
        
        # Get the size for the main window
        main_window_size = get_main_window_size()
        
        # Scale the image to match the main window size
        scaled_pixmap = original_pixmap.scaled(
            main_window_size.width(), 
            main_window_size.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        print(f"Scaled splash image from {original_pixmap.width()}x{original_pixmap.height()} to {scaled_pixmap.width()}x{scaled_pixmap.height()}")
        
        # Create a label for the background image
        self.background_label = QLabel(self)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setScaledContents(False)
        self.background_label.resize(scaled_pixmap.width(), scaled_pixmap.height())
        
        # Set the window size to match the scaled image
        self.setFixedSize(scaled_pixmap.width(), scaled_pixmap.height())
        
        # Create a button with an icon
        self.start_button = QPushButton("GENERATE NUMBERS", self)
        
        # Try to load an icon for the button
        try:
            button_icon_path = os.path.join(assets_dir, "lottery_ball.png")
            if os.path.exists(button_icon_path):
                button_icon = QIcon(button_icon_path)
                self.start_button.setIcon(button_icon)
                self.start_button.setIconSize(QSize(32, 32))
        except Exception as e:
            print(f"Error loading button icon: {e}")

        # Set button size based on percentage of splash screen size
        button_width = int(self.width() * 0.45)   # 40% of splash screen width
        button_height = int(self.height() * 0.12)  # 8% of splash screen height
        
        # Style the button
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFA500, stop:1 #FF6347);
                color: white;
                border-radius: {button_height // 2}px; /* pill-like shape */
                font-size: {int(button_height * 0.4)}px; /* scale font to button height */
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF8C00, stop:1 #FF4500);
            }}
            QPushButton:pressed {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF7F00, stop:1 #FF3300);
            }}
        """)
        
        # Position the button at the bottom center of the splash screen

        self.start_button.setFixedSize(button_width, button_height)
        # Position the button centered at bottom
        self.start_button.move(
            (self.width() - button_width) // 2,
            self.height() - button_height - int(self.height() * 0.12)  # 5% margin from bottom
        )
        
        # Connect the button click to start the main application
        self.start_button.clicked.connect(self.start_main_application)
        
        # Set the layout
        self.setLayout(layout)
        
        # Center the splash screen on the screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - scaled_pixmap.width()) // 2
        y = (screen_geometry.height() - scaled_pixmap.height()) // 2
        self.move(x, y)
        
        # Print success message
        print(f"Splash screen set up successfully with scaled image: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
        
    def showEvent(self, event):
        """Called when the splash screen is shown"""
        super().showEvent(event)
        print("Splash screen shown")
        
        # Process events to ensure the splash screen is displayed
        QApplication.processEvents()
        
    def start_main_application(self):
        """Close the splash screen and start the main application"""
        print("Starting main application...")
        self.hide()
        self.main_app_callback()
        
    def mousePressEvent(self, event):
        """Allow dragging the window when clicking anywhere on it"""
        self.oldPos = event.globalPosition().toPoint()
        
    def mouseMoveEvent(self, event):
        """Move the window when dragging"""
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()