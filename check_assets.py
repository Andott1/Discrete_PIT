import os
import sys

def check_assets():
    """Check if the assets directory and required files exist"""
    
    # Get the path to the assets directory
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    # Check if the assets directory exists
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory not found at {assets_dir}")
        print("Please create the assets directory and add the required files.")
        return False
    
    # Check if the splash screen image exists
    splash_image_path = os.path.join(assets_dir, "splash_screen.png")
    if not os.path.exists(splash_image_path):
        print(f"Error: Splash screen image not found at {splash_image_path}")
        print("Please add the splash screen image to the assets directory.")
        return False
    
    # Check if the lottery ball images exist
    balls_dir = os.path.join(assets_dir, "Balls")
    if not os.path.exists(balls_dir):
        print(f"Error: Balls directory not found at {balls_dir}")
        print("Please create the Balls directory and add the ball images.")
        return False
    
    for i in range(1, 7):
        ball_image_path = os.path.join(balls_dir, f"ball_{i}.png")
        if not os.path.exists(ball_image_path):
            print(f"Error: {ball_image_path} not found.")
            print(f"Please add the ball_{i}.png images to the Balls directory.")
            return False
    
    # Check if the main app background exists
    background_image_path = os.path.join(assets_dir, "layout_main_screen.png")
    if not os.path.exists(background_image_path):
        print(f"Error: Main app background image not found at {background_image_path}")
        print("Please add the layout_main_screen.png image to the assets directory.")
        return False
    
    print("Assets check passed. All required files found.")
    return True

if __name__ == "__main__":
    if not check_assets():
        sys.exit(1)
