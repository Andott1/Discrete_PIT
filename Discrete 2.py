import itertools
import random
from collections import Counter
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import qt_material

# Generate all possible 6/49 combinations
numbers = range(1, 50)
LUCKY_NUMBERS = list(itertools.combinations(numbers, 6))

# Function to fetch the last 5 Superlotto 6/49 winning numbers
def fetch_latest_winning_numbers():
    url = 'https://www.pcso.gov.ph/SearchLottoResult.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    winning_numbers_list = []
    draw_dates = []
    
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 1:
            game_type = cols[0].text.strip()
            if 'Superlotto 6/49' in game_type:
                draw_date = cols[2].text.strip()
                winning_numbers = cols[1].text.strip().split('-')
                try:
                    winning_numbers_list.append([int(num) for num in winning_numbers])
                    draw_dates.append(draw_date)
                except ValueError:
                    continue
        
        if len(winning_numbers_list) >= 5:
            break
    
    return list(zip(draw_dates, winning_numbers_list))

# PyQt GUI class
class LotteryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = True
        self.latest_winning_numbers = fetch_latest_winning_numbers()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Lucky Numbers Generator")
        self.setGeometry(100, 100, 1100, 650)
        self.apply_theme()
        
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # Left Column - Buttons & Lucky Numbers
        self.label = QLabel("Click the button to get Lucky Numbers!")
        self.label.setFont(QFont("Arial", 16, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label)
        
        self.button = QPushButton("Generate Lucky Numbers")
        self.button.setFont(QFont("Arial", 14, QFont.Bold))
        self.button.clicked.connect(self.generate_lucky_numbers)
        left_layout.addWidget(self.button)
        
        self.toggle_button = QPushButton("Switch to Light Mode")
        self.toggle_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.toggle_button.clicked.connect(self.toggle_theme)
        left_layout.addWidget(self.toggle_button)
        
        self.analysis_label = QLabel("Analysis: ")
        self.analysis_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.analysis_label.setAlignment(Qt.AlignCenter)
        self.analysis_label.setStyleSheet("color: #FF5733; background-color: #F5F5F5; padding: 10px; border-radius: 10px;")
        left_layout.addWidget(self.analysis_label)
        
        self.latest_results_label = QLabel("Recent 5 Superlotto 6/49 Results:")
        self.latest_results_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(self.latest_results_label)
        
        self.latest_results_text = QTextEdit()
        self.latest_results_text.setReadOnly(True)
        self.latest_results_text.setFont(QFont("Courier", 11))
        left_layout.addWidget(self.latest_results_text)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separator)
        
        # Right Column - Random Combinations & Frequency
        self.text_combinations = QTextEdit()
        self.text_combinations.setReadOnly(True)
        self.text_combinations.setFont(QFont("Courier", 11))
        right_layout.addWidget(self.text_combinations)
        
        self.text_frequency = QTextEdit()
        self.text_frequency.setReadOnly(True)
        self.text_frequency.setFont(QFont("Courier", 11))
        right_layout.addWidget(self.text_frequency)
        
        left_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)
        
        self.setLayout(main_layout)
        self.display_latest_results()
    
    def generate_lucky_numbers(self):
        self.random_picks = random.sample(LUCKY_NUMBERS, 1000)
        all_numbers = [num for combo in self.random_picks for num in combo]
        self.frequency = Counter(all_numbers)
        lucky_draw = [num for num, count in self.frequency.most_common(6)]
        
        self.label.setText(f"<span style='color: #FFD700; font-size: 18px; font-weight: bold;'>Lucky Numbers: {', '.join(map(str, lucky_draw))}</span>")
        
        combinations_text = "\n".join(map(str, self.random_picks))
        self.text_combinations.setText(f"Random 1000 Combinations:\n{combinations_text}")
        
        frequency_text = "\n".join(f"{num}: {count}" for num, count in sorted(self.frequency.items()))
        self.text_frequency.setText(f"Number Frequencies:\n{frequency_text}")
        
        if self.latest_winning_numbers:
            self.analyze_against_winning_numbers(lucky_draw)
    
    def analyze_against_winning_numbers(self, lucky_draw):
        analysis_text = ""
        for draw_date, draw in self.latest_winning_numbers:
            match_count = len(set(lucky_draw) & set(draw))
            match_percentage = (match_count / 6) * 100
            analysis_text += f"{draw_date}: {match_count} matches ({match_percentage:.2f}%)\n"
        self.analysis_label.setText(f"Analysis:\n{analysis_text}")
    
    def display_latest_results(self):
        results_text = "\n".join(
            f"{draw[0]}: {', '.join(map(str, draw[1]))}" for draw in self.latest_winning_numbers
        )
        self.latest_results_text.setText(results_text)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.toggle_button.setText("Switch to Dark Mode" if not self.dark_mode else "Switch to Light Mode")
    
    def apply_theme(self):
        theme = "dark_teal.xml" if self.dark_mode else "light_blue.xml"
        qt_material.apply_stylesheet(app, theme=theme)

# Run the application
if __name__ == '__main__':
    app = QApplication([])
    window = LotteryApp()
    window.show()
    app.exec_()
