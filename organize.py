import json
import os
import shutil
from pathlib import Path

# Read zones.json
with open('zones.json', 'r', encoding='utf-8') as f:
    zones_data = json.load(f)

# Get the current directory
current_dir = Path('.')

# Create organized structure
for game in zones_data:
    game_name = game['name']
    html_file = game['url']
    
    # Extract just the filename (e.g., "0.html" or "1-fde.html")
    filename = Path(html_file).name
    
    # Sanitize game name for folder creation (remove invalid characters)
    sanitized_name = "".join(c for c in game_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    game_folder = current_dir / sanitized_name
    
    # Create game folder if it doesn't exist
    game_folder.mkdir(exist_ok=True)
    
    # Create the destination path
    index_path = game_folder / 'index.html'
    
    # Check if the HTML file exists
    html_source = current_dir / filename
    
    if html_source.exists():
        # Move the HTML file to game-name/index.html
        shutil.move(str(html_source), str(index_path))
        print(f"✓ Organized: {game_name} -> {sanitized_name}/index.html")
    else:
        print(f"✗ Not found: {filename} for {game_name}")

print("\nOrganization complete!")
