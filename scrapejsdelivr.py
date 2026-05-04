import json
import os
import requests
from pathlib import Path
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load URLs from base_urls.json
def load_urls(filename='base_urls.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []

# Create output directory
def create_output_dir(dirname='downloaded_games'):
    Path(dirname).mkdir(exist_ok=True)
    return dirname

# Convert jsdelivr URL to GitHub API URL
def get_github_api_url(jsdelivr_url):
    """
    Convert https://cdn.jsdelivr.net/gh/user/repo@ref/path/
    to https://api.github.com/repos/user/repo/contents/path?ref=ref
    """
    # Extract parts from jsdelivr URL
    # Format: https://cdn.jsdelivr.net/gh/USER/REPO@REF/PATH/ or
    #         https://cdn.jsdelivr.net/gh/USER/REPO/PATH/
    
    parts = jsdelivr_url.replace('https://cdn.jsdelivr.net/gh/', '')
    
    # Split by @ to get ref if it exists
    if '@' in parts:
        repo_part, ref_and_path = parts.split('@', 1)
        if '/' in ref_and_path:
            ref, path = ref_and_path.split('/', 1)
        else:
            ref = ref_and_path
            path = ''
    else:
        # No ref specified, use main/master
        parts_list = parts.split('/')
        repo_part = '/'.join(parts_list[:2])
        path = '/'.join(parts_list[2:]) if len(parts_list) > 2 else ''
        ref = 'main'
    
    # Remove trailing slash from path
    path = path.rstrip('/')
    
    user, repo = repo_part.split('/')
    
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    if ref:
        api_url += f"?ref={ref}"
    
    return api_url, user, repo, ref, path

# Download repository contents recursively
def download_repo_contents(api_url, output_dir, game_name):
    """Download all files from GitHub API recursively"""
    try:
        response = requests.get(api_url, timeout=30, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # If it's a file, download it
        if isinstance(data, dict) and 'download_url' in data:
            file_response = requests.get(data['download_url'], timeout=30, verify=False)
            file_response.raise_for_status()
            
            filepath = os.path.join(output_dir, game_name, data['name'])
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(file_response.content)
            print(f"  ✓ {data['name']}")
            return True
        
        # If it's a directory, recursively download contents
        elif isinstance(data, list):
            for item in data:
                if item['type'] == 'file':
                    file_response = requests.get(item['download_url'], timeout=30, verify=False)
                    file_response.raise_for_status()
                    
                    filepath = os.path.join(output_dir, game_name, item['path'])
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_response.content)
                    print(f"  ✓ {item['path']}")
                
                elif item['type'] == 'dir':
                    # Recursively download subdirectory
                    download_repo_contents(item['url'], output_dir, game_name)
            
            return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download {game_name}: {e}")
        return False

# Main scraper function
def scrape_all(json_file='base_urls.json', output_dir='downloaded_games'):
    games = load_urls(json_file)
    
    if not games:
        print("No games to download.")
        return
    
    output_dir = create_output_dir(output_dir)
    print(f"Starting download to '{output_dir}'...\n")
    
    for game in games:
        name = game.get('name', 'unknown')
        url = game.get('url', '')
        
        if not url:
            print(f"✗ Skipped {name}: No URL provided")
            continue
        
        print(f"Downloading {name}...")
        
        try:
            api_url, user, repo, ref, path = get_github_api_url(url)
            download_repo_contents(api_url, output_dir, name)
            print(f"✓ Completed: {name}\n")
        except Exception as e:
            print(f"✗ Error processing {name}: {e}\n")
    
    print("Done!")

if __name__ == '__main__':
    scrape_all()