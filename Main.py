import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtGui import QIcon

from ui_builder import setup_main_layout
from event_handlers import (handle_update_time, handle_toggle_details, handle_resize_event,
                           handle_generate_lucky_numbers, handle_export_data, handle_display_results)
from ui_utils import resize_and_center
from splash_screen import LotterySplashScreen  # Use the custom splash screen
# from simple_splash import show_splash_screen  # Alternative: use the simple splash screen

class LotteryAnalyzer(QWidget):
    """Main application window for the Lottery Number Analyzer"""
    
    def __init__(self):
        super().__init__()
        setup_main_layout(self)
        resize_and_center(self)
        
        # Set application icon if available
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            icon_path = os.path.join(assets_dir, "lottery_ball.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Error setting application icon: {e}")
    
    # Event handlers - these methods delegate to the handler functions
    def update_time_display(self):
        handle_update_time(self)
        
    def toggle_details(self, checked):
        handle_toggle_details(self, checked)

    def resizeEvent(self, event):
        handle_resize_event(self, event)
    
    def generate_lucky_numbers(self):
        handle_generate_lucky_numbers(self)
    
    def display_results(self, recent_results):
        handle_display_results(self, recent_results)
    
    def export_data(self):
        handle_export_data(self)

def check_assets():
    """Check if the assets directory exists and create it if needed"""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created assets directory: {assets_dir}")
        return False
    return True

def main():
    print("Starting Lottery Number Generator application...")
    app = QApplication(sys.argv)
    
    # Check if assets directory exists
    check_assets()
    
    # Create the main window but don't show it yet
    main_window = LotteryAnalyzer()
    
    # Function to show the main window
    def show_main_window():
        print("Showing main window...")
        main_window.show()
    
    # Show the splash screen using the custom implementation
    splash = LotterySplashScreen(show_main_window)
    splash.show()
    
    # Alternative: Show the splash screen using the simple implementation
    # splash = show_splash_screen(app, show_main_window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()