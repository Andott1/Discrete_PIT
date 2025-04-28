import random
import csv
from collections import Counter
from config import LOTTERY_CONFIG

def generate_lucky_numbers(lottery_type):
    """Generate lucky numbers based on lottery type"""
    min_num, max_num = LOTTERY_CONFIG[lottery_type]
    
    # Generate 2000 random combinations and take 1000 unique ones
    sampled_combinations = {tuple(sorted(random.sample(range(min_num, max_num + 1), 6))) for _ in range(2000)}
    sampled_combinations = list(sampled_combinations)[:1000]
    
    # Count frequency of each number
    number_counter = Counter(num for comb in sampled_combinations for num in comb)
    
    # Get top 6 most frequent numbers
    top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]
    
    return top_6, sampled_combinations, number_counter

def export_data_to_csv(file_path, lucky_numbers, frequency_table, combinations_table, recent_results_table, history_table):
    """Export all data to a CSV file"""
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        
        # Export Lucky Numbers
        writer.writerow(["Lucky Numbers:", lucky_numbers])
        writer.writerow([])  # Blank row

        # Export Frequency Table
        writer.writerow(["Frequency Table:"])
        writer.writerow(["Number", "Frequency"])
        for row in range(frequency_table.rowCount()):
            writer.writerow([
                frequency_table.item(row, 0).text(),
                frequency_table.item(row, 1).text()
            ])
        writer.writerow([])  # Blank row

        # Export Random 1000 Combinations
        writer.writerow(["Random 1000 Combinations:"])
        writer.writerow(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
        for row in range(combinations_table.rowCount()):
            writer.writerow([
                combinations_table.item(row, col).text()
                for col in range(combinations_table.columnCount())
            ])
        writer.writerow([])  # Blank row

        # Export Recent Results
        writer.writerow(["Recent Results:"])
        writer.writerow(["Draw", "1", "2", "3", "4", "5", "6"])
        for row in range(recent_results_table.rowCount()):
            writer.writerow([
                recent_results_table.item(row, col).text()
                for col in range(recent_results_table.columnCount())
            ])
        writer.writerow([])  # Blank row

        # Export Generation History
        writer.writerow(["Lucky Numbers History:"])
        writer.writerow(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        for row in range(history_table.rowCount()):
            writer.writerow([
                history_table.item(row, col).text()
                for col in range(history_table.columnCount())
            ])
            
    return True