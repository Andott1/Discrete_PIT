from PyQt5.QtCore import pyqtSignal, QThread
import traceback
from FetchLatest import fetch_latest_winning_numbers


class FetchResultsThread(QThread):
    results_fetched = pyqtSignal(list, list)  # full_results, display_table_data
    
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
            
            # If no results were found, emit an empty list
            if not recent_results:
                print("[DEBUG] No results found for the selected criteria")
                self.results_fetched.emit([], [])
                return
                
            table_data = []
          
            for draw_date, res in recent_results:
                numbers = res[:6]
                while len(numbers) < 6:
                    numbers.append("")
                        
                row = [draw_date] + numbers
                table_data.append(row)

                # Limit the number of results to display_limit
                if len(table_data) >= self.display_limit:
                    break
                    
            print(f"[DEBUG] Displaying {len(table_data)} results (limited by display_limit={self.display_limit})")
            print(f"[DEBUG] Total results fetched: {len(recent_results)}")
            
            self.results_fetched.emit(recent_results, table_data)
            
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching results: {e}")
            self.results_fetched.emit([], [])
