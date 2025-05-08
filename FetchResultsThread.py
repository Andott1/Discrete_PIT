from PyQt5.QtCore import pyqtSignal, QThread
import traceback
from collections import Counter
from FetchLatest import fetch_latest_winning_numbers


class FetchResultsThread(QThread):
    results_fetched = pyqtSignal(list)
    
    def __init__(self, lottery_type, lucky_numbers, from_date, to_date, fetch_limit, display_limit=None):
        super().__init__()
        self.lottery_type = lottery_type
        self.lucky_numbers = lucky_numbers
        self.from_date = from_date
        self.to_date = to_date
        self.fetch_limit = fetch_limit

        # If display_limit is not provided, use fetch_limit as default
        self.display_limit = display_limit if display_limit is not None else fetch_limit
    
    def run(self):
        try:
            recent_results = fetch_latest_winning_numbers(self.lottery_type, self.from_date, self.to_date, self.fetch_limit)
            table_data = []
            number_counter = Counter()
            
            for draw_date, res in recent_results:
                numbers = res[:6]
                while len(numbers) < 6:
                    numbers.append("")
                
                # Update the counter with each number from the results
                for num in numbers:
                    if num:  # Only count non-empty numbers
                        number_counter[int(num)] += 1
                        
                row = [draw_date] + numbers
                table_data.append(row)

                # Limit the number of results to display_limit
                if len(table_data) >= self.display_limit:
                    break
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching results: {e}")
            table_data = []
            number_counter = Counter()

        self.results_fetched.emit(table_data, number_counter)