import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QIcon

from modern_ui_builder import build_modern_ui, update_lottery_balls
from utils import generate_lucky_numbers, export_data_to_csv
from ui_utils import populate_table, display_recent_results, add_history
from splash_screen import LotterySplashScreen
from check_assets import check_assets

class LotteryAnalyzer(QWidget):
    """Main application window for the Lottery Number Analyzer"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Number Generator")
        
        # Build the modern UI
        build_modern_ui(self)
        
        # Set application icon if available
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            icon_path = os.path.join(assets_dir, "lottery_ball.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Error setting application icon: {e}")
    
    def generate_lucky_numbers(self):
        """Generate lucky numbers and update the UI"""
        lottery_type = self.lottery_selector.currentText()
        from_date = self.from_date_edit.date().toString("MM/dd/yyyy")
        to_date = self.to_date_edit.date().toString("MM/dd/yyyy")
        
        # Use the existing function from utils.py
        top_6, sampled_combinations, number_counter = generate_lucky_numbers(lottery_type)
        
        # Update the lottery balls with randomized ball images
        update_lottery_balls(self, top_6)
        
        # Populate the frequency table
        populate_table(self.result_table, number_counter)
        
        # Add to history
        add_history(self.history_table, lottery_type, top_6)
        
        # Show a success message
        QMessageBox.information(self, "Success", f"Lucky numbers generated successfully for {lottery_type}!")
    
    def export_data(self):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            # Get the numbers from the lottery balls
            numbers = []
            for ball in self.lottery_balls:
                numbers.append(str(ball.number))
            
            # Use the existing function from utils.py
            export_data_to_csv(
                file_path, 
                f"Lucky Numbers: {'-'.join(numbers)}", 
                self.result_table, 
                None,  # No combinations table in the new UI
                self.recent_results_table, 
                self.history_table
            )
            
            QMessageBox.information(self, "Success", "Data exported successfully!")
            return True
        return False

def main():
    print("Starting Lottery Number Generator application...")
    app = QApplication(sys.argv)
    
    # Check if assets directory exists
    if not check_assets():
        sys.exit(1)
    
    # Create the main window but don't show it yet
    main_window = LotteryAnalyzer()
    
    # Function to show the main window
    def show_main_window():
        print("Showing main window...")
        main_window.show()
    
    # Show the splash screen
    splash = LotterySplashScreen(show_main_window)
    splash.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()