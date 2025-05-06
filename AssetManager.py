import sys
import os
import glob
from PyQt5.QtGui import QFontDatabase, QPixmap


class AssetManager:
    def __init__(self):
        """
        Initialize the AssetManager with proper path resolution for both development
        and PyInstaller bundled environments.
        """
        # Base directories to check for assets
        self.asset_dirs = [
            "Assets/App Screenshots",
            "Assets/Fonts",
            "Assets/Icons",
            "Assets/Screens",
        ]
        
        # Map to cache resolved asset paths
        self.asset_cache = {}
        
        # Print the base directory for debugging
        print(f"Base directory: {self.get_base_dir()}")
        
        # Pre-scan assets to populate cache
        self.scan_assets()
    
    def get_base_dir(self):
        """
            the base directory for assets, handling both development and PyInstaller environments.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            return sys._MEIPASS
        else:
        # When running normally (like python main.py)
            return os.path.dirname(os.path.abspath(__file__))
    
    def scan_assets(self):
        """
        Scan all asset directories and populate the asset cache.
        """
        base_dir = self.get_base_dir()
        print(f"Scanning assets in: {base_dir}")
        
        # Scan each asset directory
        for asset_dir in self.asset_dirs:
            full_dir_path = os.path.join(base_dir, asset_dir)
            
            if os.path.exists(full_dir_path):
                print(f"Found asset directory: {full_dir_path}")
                
                # Scan all files in this directory and subdirectories
                for root, _, files in os.walk(full_dir_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Get the relative path from the base directory
                        rel_path = os.path.relpath(full_path, base_dir)
                        # Store in cache with normalized path
                        normalized_path = rel_path.replace('\\', '/')
                        self.asset_cache[normalized_path] = full_path
                        
                        # Also store with simplified path (for robustness)
                        simple_path = os.path.join(asset_dir, file).replace('\\', '/')
                        self.asset_cache[simple_path] = full_path
                        
                        print(f"Cached asset: {normalized_path} -> {full_path}")
            else:
                print(f"Asset directory not found: {full_dir_path}")
        
        print(f"Total assets cached: {len(self.asset_cache)}")
        
        # Try to find assets with recursive glob pattern (fallback method)
        self.find_assets_with_glob()
    
    def find_assets_with_glob(self):
        """
        Use glob to find assets recursively as a fallback method.
        """
        base_dir = self.get_base_dir()
        
        # Search for all files in the Assets directory
        for pattern in ["Assets/**/*.*", "Assets/*.*"]:
            for file_path in glob.glob(os.path.join(base_dir, pattern), recursive=True):
                if os.path.isfile(file_path):
                    # Get filename
                    filename = os.path.basename(file_path)
                    # Add to cache with just the filename as key (most permissive)
                    self.asset_cache[filename] = file_path
                    
                    # Also add with partial path
                    rel_path = os.path.relpath(file_path, base_dir)
                    self.asset_cache[rel_path.replace('\\', '/')] = file_path
    
    def resolve_asset(self, asset_path):
        """
        Resolve an asset path to its full path, handling both development and PyInstaller environments.
        
        Args:
            asset_path (str): The relative path to the asset (e.g., "Assets/Fonts/Roboto.ttf")
            
        Returns:
            str: The full path to the asset, or None if not found
        """
        # Normalize the path
        normalized_path = asset_path.replace('\\', '/')
        
        # Check if the asset is in the cache
        if normalized_path in self.asset_cache:
            return self.asset_cache[normalized_path]
        
        # Try with just the filename
        filename = os.path.basename(normalized_path)
        if filename in self.asset_cache:
            return self.asset_cache[filename]
        
        # If not in cache, try direct resolution
        base_dir = self.get_base_dir()
        full_path = os.path.join(base_dir, normalized_path)
        
        if os.path.exists(full_path):
            # Add to cache for future lookups
            self.asset_cache[normalized_path] = full_path
            return full_path
        
        # Try to find the file by searching all subdirectories
        for root, _, files in os.walk(base_dir):
            if filename in files:
                full_path = os.path.join(root, filename)
                self.asset_cache[normalized_path] = full_path
                return full_path
        
        # Asset not found
        print(f"Asset not found: {asset_path}")
        return None
    
    def load_asset(self, asset_path):
        """
        Resolve and return the full path to an asset.
        
        Args:
            asset_path (str): The relative path to the asset
            
        Returns:
            str: The full path to the asset, or None if not found
        """
        return self.resolve_asset(asset_path)
    
    def load_pixmap(self, image_path):
        """
        Load an image as a QPixmap, with robust error handling.
        
        Args:
            image_path (str): The relative path to the image
            
        Returns:
            QPixmap: The loaded pixmap, or an empty pixmap if loading failed
        """
        resolved_path = self.resolve_asset(image_path)
        if not resolved_path:
            print(f"Image not found: {image_path}")
            return QPixmap()
        
        pixmap = QPixmap(resolved_path)
        if pixmap.isNull():
            print(f"Failed to load image as pixmap: {resolved_path}")
            
            # Try alternative paths
            filename = os.path.basename(image_path)
            for key, path in self.asset_cache.items():
                if filename in key and key != image_path:
                    print(f"Trying alternative path: {path}")
                    alt_pixmap = QPixmap(path)
                    if not alt_pixmap.isNull():
                        return alt_pixmap
            
            return QPixmap()
        
        return pixmap
    
    def load_fonts(self):
        """
        Load all fonts in the Fonts directory.
        
        Returns:
            list: A list of loaded font family names
        """
        loaded_families = []
        font_dir = os.path.join(self.get_base_dir(), "Assets", "Fonts")
        
        if not os.path.exists(font_dir):
            print(f"Font directory not found: {font_dir}")
            # Try to find fonts using the asset cache
            for key, path in self.asset_cache.items():
                if "Fonts" in key and path.lower().endswith(('.ttf', '.otf')):
                    font_id = QFontDatabase.addApplicationFont(path)
                    if font_id != -1:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        print(f"Loaded font: {path} → {families}")
                        loaded_families.extend(families)
                    else:
                        print(f"Failed to load font: {path}")
            
            return loaded_families
        
        print(f"Loading fonts from: {font_dir}")
        
        # Find all font files
        font_files = []
        for ext in ['.ttf', '.otf']:
            font_files.extend(glob.glob(os.path.join(font_dir, f"**/*{ext}"), recursive=True))
        
        # Load each font
        for font_path in font_files:
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font: {font_path} → {families}")
                loaded_families.extend(families)
            else:
                print(f"Failed to load font: {font_path}")
        
        return loaded_families
    
    def get_font_dir(self):
        """
        Get the directory containing fonts.
        
        Returns:
            str: The full path to the fonts directory, or None if not found
        """
        font_dir = "Assets/Fonts"
        resolved = self.resolve_asset(font_dir)
        if resolved:
            return os.path.dirname(resolved)
        
        # Fallback: try to find any font file and return its directory
        for key, path in self.asset_cache.items():
            if "Fonts" in key and os.path.exists(path):
                return os.path.dirname(path)
        
        # Last resort: return the base Assets directory
        return os.path.join(self.get_base_dir(), "Assets")