from PyQt5.QtCore import pyqtSignal, QThread

from FetchLatest import fetch_latest_winning_numbers


class FetchResultsThread(QThread):
    results_fetched = pyqtSignal(list)
    
    def __init__(self, lottery_type, lucky_numbers, from_date, to_date):
        super().__init__()
        self.lottery_type = lottery_type
        self.lucky_numbers = lucky_numbers
        self.from_date = from_date
        self.to_date = to_date
    
    def run(self):
        try:
            recent_results = fetch_latest_winning_numbers(self.lottery_type, self.from_date, self.to_date)
            table_data = []
            for draw_date, res in recent_results:
                # Make sure we have exactly 6 numbers (pad if necessary)
                numbers = res[:6]
                while len(numbers) < 6:
                    numbers.append("")
                
                row = [draw_date] + numbers
                table_data.append(row)
        except Exception as e:
            print(f"Error fetching results: {e}")
            table_data = []
        
        self.results_fetched.emit(table_data)