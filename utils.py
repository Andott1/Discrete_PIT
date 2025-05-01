import os
import random
import csv
import sys
import itertools
from collections import Counter
from config import LOTTERY_CONFIG

def generate_lucky_numbers(lottery_type):
    """Generate lucky numbers based on lottery type"""
    min_num, max_num = LOTTERY_CONFIG[lottery_type]
    
    all_combinations = list(itertools.combinations(range(min_num, max_num + 1), 6))
    sampled_combinations = random.sample(all_combinations, 1000)
    
    number_counter = Counter(num for comb in sampled_combinations for num in comb)
    
    top_6 = [str(num).zfill(2) for num, _ in number_counter.most_common(6)]
    
    return top_6, sampled_combinations, number_counter

def export_data_to_csv(file_path, lucky_numbers, frequency_table, combinations_table, recent_results_table, history_table):
    """Export all data to a CSV file"""
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        
        writer.writerow(["Lucky Numbers:", lucky_numbers])
        writer.writerow([])
        
        writer.writerow(["Frequency Table:"])
        writer.writerow(["Number", "Frequency"])
        for row in range(frequency_table.rowCount()):
            writer.writerow([
                frequency_table.item(row, 0).text(),
                frequency_table.item(row, 1).text()
            ])
        writer.writerow([])

        if combinations_table:
            writer.writerow(["Random 1000 Combinations:"])
            writer.writerow(["Combination #", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6"])
            for row in range(combinations_table.rowCount()):
                writer.writerow([
                    combinations_table.item(row, col).text()
                    for col in range(combinations_table.columnCount())
                ])
            writer.writerow([])
        
        writer.writerow(["Recent Results:"])
        writer.writerow(["Draw", "1", "2", "3", "4", "5", "6"])
        for row in range(recent_results_table.rowCount()):
            writer.writerow([
                recent_results_table.item(row, col).text()
                for col in range(recent_results_table.columnCount())
            ])
        writer.writerow([])

        writer.writerow(["Lucky Numbers History:"])
        writer.writerow(["Lotto Type", "1", "2", "3", "4", "5", "6"])
        for row in range(history_table.rowCount()):
            writer.writerow([
                history_table.item(row, col).text()
                for col in range(history_table.columnCount())
            ])
            
    return True

def check_assets():
    """Check if the assets directory and required files exist"""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory not found at {assets_dir}")
        print("Please create the assets directory and add the required files.")
        return False
    
    # Check splash screen
    splash_image_path = os.path.join(assets_dir, "splash_screen.png")
    if not os.path.exists(splash_image_path):
        print(f"Error: Splash screen image not found at {splash_image_path}")
        return False
    
    # Check main background
    background_image_path = os.path.join(assets_dir, "layout_main_screen.png")
    if not os.path.exists(background_image_path):
        print(f"Error: Main app background image not found at {background_image_path}")
        return False
    
    # Check balls directory and ball images
    balls_dir = os.path.join(assets_dir, "Balls")
    if not os.path.exists(balls_dir):
        print(f"Error: Balls directory not found at {balls_dir}")
        return False
    
    for i in range(1, 7):
        ball_image_path = os.path.join(balls_dir, f"ball_{i}.png")
        if not os.path.exists(ball_image_path):
            print(f"Error: Ball image ball_{i}.png not found at {balls_dir}")
            return False
    
    print("Assets check passed. All required files found.")
    return True
