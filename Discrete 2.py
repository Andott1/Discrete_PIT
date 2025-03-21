import itertools
import random
from collections import Counter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit

# Generate all possible 6/49 combinations
numbers = range(1, 50)
LUCKY_NUMBERS = list(itertools.combinations(numbers, 6))

# PyQt GUI class
class LotteryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("Click the button to get Lucky Numbers!")
        layout.addWidget(self.label)
        
        self.button = QPushButton("Generate Lucky Numbers")
        self.button.clicked.connect(self.generate_lucky_numbers)
        layout.addWidget(self.button)
        
        self.text_combinations = QTextEdit()
        self.text_combinations.setReadOnly(True)
        layout.addWidget(self.text_combinations)
        
        self.text_frequency = QTextEdit()
        self.text_frequency.setReadOnly(True)
        layout.addWidget(self.text_frequency)
        
        self.setLayout(layout)
        self.setWindowTitle("Lucky Numbers Generator")
        
    def generate_lucky_numbers(self):
        # Randomly pick 1000 combinations
        random_picks = random.sample(LUCKY_NUMBERS, 1000)
        
        # Count the frequency of each number
        all_numbers = [num for combo in random_picks for num in combo]
        frequency = Counter(all_numbers)
        
        # Get top 6 most common numbers
        lucky_draw = [num for num, count in frequency.most_common(6)]
        
        self.label.setText(f"Lucky Numbers: {', '.join(map(str, lucky_draw))}")
        
        combinations_text = "\n".join(map(str, random_picks))
        self.text_combinations.setText(f"Random 1000 Combinations:\n{combinations_text}")
        
        frequency_text = "\n".join(f"{num}: {count}" for num, count in sorted(frequency.items()))
        self.text_frequency.setText(f"Number Frequencies:\n{frequency_text}")

# Run the application
if __name__ == '__main__':
    app = QApplication([])
    window = LotteryApp()
    window.show()
    app.exec_()