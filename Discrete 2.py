import sys
import itertools
import random
import requests
import csv
from collections import Counter
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QCheckBox, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Lottery configurations
LOTTERY_CONFIG = {"6/58": (1, 58), "6/55": (1, 55), "6/49": (1, 49), "6/45": (1, 45), "6/42": (1, 42)}

def fetch_latest_winning_numbers(lottery_type):
    url = 'https://www.pcso.gov.ph/SearchLottoResult.aspx'
    results = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return []
        
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            game_type = cols[0].get_text(strip=True)
            if lottery_type.replace("6/", "") in game_type:
                winning_numbers = [num.zfill(2) for num in cols[1].get_text(strip=True).split('-') if num.isdigit()]
                if winning_numbers:
                    results.append('-'.join(winning_numbers))
                if len(results) >= 3:
                    break
    except requests.RequestException as e:
        print(f"Error fetching results: {e}")
    return results

class FetchResultsThread(QThread):
    results_fetched = pyqtSignal(str)
    
    def __init__(self, lottery_type, lucky_numbers):
        super().__init__()
        self.lottery_type = lottery_type
        self.lucky_numbers = lucky_numbers
    
    def run(self):
        try:
            recent_results = fetch_latest_winning_numbers(self.lottery_type)
            results_text = "\n".join([f"Draw {i+1}: {res}" for i, res in enumerate(recent_results)])
            matches = [set(self.lucky_numbers) & set(map(int, res.split('-'))) for res in recent_results]
            match_text = "\n".join([f"Matches in Draw {i+1}: {'-'.join(map(lambda x: str(x).zfill(2), match))}" for i, match in enumerate(matches) if match])
            result_text = f"<b>Recent Results:</b><br>{results_text}<br><br><b>{match_text}</b>" if recent_results else "<b>Recent Results:</b> No results found."
        except Exception as e:
            result_text = f"Error fetching results: {e}"
        
        self.results_fetched.emit(result_text)

class LotteryAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.lottery_selector = QComboBox()
        self.lottery_selector.addItems(LOTTERY_CONFIG.keys())
        layout.addWidget(QLabel("Select Lottery Type:"))
        layout.addWidget(self.lottery_selector)
        
        self.generate_button = QPushButton("Generate Lucky Numbers")
        self.generate_button.clicked.connect(self.generate_lucky_numbers)
        layout.addWidget(self.generate_button)
        
        self.lucky_numbers_label = QLabel("<b>Lucky Numbers:</b> ")
        layout.addWidget(self.lucky_numbers_label)
        
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Number", "Frequency"])
        layout.addWidget(self.result_table)
        
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        layout.addWidget(self.export_button)
        
        self.combinations_display = QTextEdit()
        self.combinations_display.setReadOnly(True)
        layout.addWidget(QLabel("Randomly Picked 1000 Combinations:"))
        layout.addWidget(self.combinations_display)
        
        self.recent_results_label = QLabel("<b>Recent Results:</b> ")
        layout.addWidget(self.recent_results_label)
        
        self.dark_mode_toggle = QCheckBox("Dark Mode")
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_toggle)
        
        self.setLayout(layout)
        self.setWindowTitle("Lottery Number Frequency Analyzer")
        self.setGeometry(100, 100, 550, 600)
    
    def generate_lucky_numbers(self):
        lottery_type = self.lottery_selector.currentText()
        min_num, max_num = LOTTERY_CONFIG[lottery_type]
        
        sampled_combinations = {tuple(sorted(random.sample(range(min_num, max_num + 1), 6))) for _ in range(2000)}
        sampled_combinations = list(sampled_combinations)[:1000]
        self.combinations_display.setText('\n'.join(map(str, sampled_combinations)))
        
        number_counter = Counter(num for comb in sampled_combinations for num in comb)
        top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]
        
        self.lucky_numbers_label.setText(f"Lucky Numbers: {'-'.join(top_6)}")
        self.populate_table(number_counter)
        self.fetch_recent_results(lottery_type, top_6)
    
    def populate_table(self, number_counter):
        self.result_table.setRowCount(len(number_counter))
        for i, (num, freq) in enumerate(number_counter.most_common()):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(num)))
            self.result_table.setItem(i, 1, QTableWidgetItem(str(freq)))
    
    def fetch_recent_results(self, lottery_type, lucky_numbers):
        self.thread = FetchResultsThread(lottery_type, lucky_numbers)
        self.thread.results_fetched.connect(self.recent_results_label.setText)
        self.thread.start()
    
    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Number", "Frequency"])
                for row in range(self.result_table.rowCount()):
                    writer.writerow([self.result_table.item(row, 0).text(), self.result_table.item(row, 1).text()])
    
    def toggle_dark_mode(self, state):
        dark_stylesheet = """
            QWidget { background-color: #353535; color: white; }
            QPushButton { background-color: #555; color: white; border-radius: 5px; }
            QTableWidget { background-color: #252525; color: white; }
            QHeaderView::section { background-color: #454545; color: white; }
            QTableWidget QTableCornerButton::section { background-color: #454545; }
        """
        light_stylesheet = """
            QWidget { background-color: white; color: black; }
            QPushButton { background-color: #ddd; color: black; border-radius: 5px; }
            QTableWidget { background-color: white; color: black; }
            QHeaderView::section { background-color: transparent; color: black; }
        """
        self.setStyleSheet(dark_stylesheet if state == Qt.CheckState.Checked.value else light_stylesheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryAnalyzer()
    window.show()
    sys.exit(app.exec())

#QTableWidget QTableCornerButton::section { background-color: #454545; }
