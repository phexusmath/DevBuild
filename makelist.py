import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Read zones.json
with open('zones.json', 'r', encoding='utf-8') as f:
    zones_data = json.load(f)

base_urls_list = []

# Process each game
for game in zones_data:
    game_name = game['name']
    
    # Sanitize game name for folder creation (remove invalid characters)
    sanitized_name = "".join(c for c in game_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    index_path = Path(sanitized_name) / 'index.html'
    
    # Check if index.html exists
    if index_path.exists():
        try:
            # Read and parse the HTML file
            with open(index_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            # Find the base tag
            base_tag = soup.find('base')
            
            if base_tag and base_tag.get('href'):
                base_url = base_tag.get('href')
                base_urls_list.append({
                    "name": game_name,
                    "url": base_url
                })
                print(f"✓ Found base URL for {game_name}: {base_url}")
            else:
                print(f"✗ No base tag found in {sanitized_name}/index.html")
        except Exception as e:
            print(f"✗ Error reading {sanitized_name}/index.html: {e}")
    else:
        print(f"✗ File not found: {sanitized_name}/index.html")

# Write to new JSON file
output_file = 'base_urls.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(base_urls_list, f, indent=2, ensure_ascii=False)

print(f"\n✓ Extraction complete! Saved to {output_file}")
