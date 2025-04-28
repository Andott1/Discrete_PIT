import sys
from PyQt6.QtWidgets import QApplication, QWidget

from ui_builder import setup_main_layout
from event_handlers import (handle_update_time, handle_toggle_details, handle_resize_event,
                           handle_generate_lucky_numbers, handle_export_data, handle_display_results)
from ui_utils import resize_and_center

class LotteryAnalyzer(QWidget):
    """Main application window for the Lottery Number Analyzer"""
    
    def __init__(self):
        super().__init__()
        setup_main_layout(self)
        resize_and_center(self)
    
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryAnalyzer()
    window.show()
    sys.exit(app.exec())