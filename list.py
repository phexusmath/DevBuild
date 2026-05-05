import os
import json

def generate_game_json(directory_path, base_url):
    game_list = []
    
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"Error: The directory {directory_path} does not exist.")
        return

    # List all items in the directory
    for folder_name in os.listdir(directory_path):
        # Create the full path to check if it's a directory
        full_path = os.path.join(directory_path, folder_name)
        
        if os.path.isdir(full_path):
            # Format the name (optional: you could replace dashes/underscores with spaces)
            # Example: "temple-run-2" -> "Temple Run 2"
            display_name = folder_name.replace('-', ' ').replace('_', ' ').title()
            
            # Construct the URL
            url = f"{base_url.rstrip('/')}/{folder_name}"
            
            # Append the object to our list
            game_list.append({
                "name": display_name,
                "url": url
            })
            
    return game_list

# Configuration
target_directory = './files'  # Relative path to your /files folder
url_prefix = 'https://phexusmath.github.io/files'

# Execute
games = generate_game_json(target_directory, url_prefix)

# Output as JSON
if games:
    json_output = json.dumps(games, indent=2)
    print(json_output)
    
    # Optional: Save to a file
    with open('games.json', 'w') as f:
        f.write(json_output)