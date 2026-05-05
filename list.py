import os
import json

def get_game_data(directory_path, base_url):
    temp_list = []
    
    if not os.path.exists(directory_path):
        print(f"Warning: The directory {directory_path} does not exist. Skipping.")
        return temp_list

    for folder_name in os.listdir(directory_path):
        full_path = os.path.join(directory_path, folder_name)
        
        if os.path.isdir(full_path):
            # Clean up the name for display
            display_name = folder_name.replace('-', ' ').replace('_', ' ').title()
            
            # Construct the URL based on the specific base_url provided
            url = f"{base_url.rstrip('/')}/{folder_name}"
            
            temp_list.append({
                "name": display_name,
                "url": url
            })
            
    return temp_list

# Configuration for both sources
sources = [
    {'path': './files', 'url': 'https://phexusmath.github.io/files'},
    {'path': './complete', 'url': 'https://phexusmath.github.io/complete'}
]

all_games = []

# Collect games from all source directories
for source in sources:
    all_games.extend(get_game_data(source['path'], source['url']))

# Sort the final list alphanumerically by the "name" key
# lambda x: x['name'].lower() ensures 'Apple' comes before 'banana'
all_games.sort(key=lambda x: x['name'].lower())

# Output and Save
if all_games:
    json_output = json.dumps(all_games, indent=2)
    print(json_output)
    
    with open('list.json', 'w') as f:
        f.write(json_output)
    print(f"\nSuccess: {len(all_games)} games saved to list.json")