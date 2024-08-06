import json
import os
import requests

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the JSON files relative to the script's directory
data_folder = os.path.join(script_dir, 'data')
shield_folder = os.path.join(script_dir, 'shields')
clones_file_path = os.path.join(data_folder, 'clones.json')
downloads_file_path = os.path.join(data_folder, 'downloads.json')
output_file_path = os.path.join(shield_folder, 'badge_data.json')
release_output_file_path = os.path.join(shield_folder, 'release_badge_data.json')

# Ensure the data folder exists
os.makedirs(data_folder, exist_ok=True)

# Initialize counters
total_clones = 0
total_downloads = 0

# Read and sum the 'count' values from clones.json
if os.path.exists(clones_file_path):
    try:
        with open(clones_file_path, 'r') as clones_file:
            clones_data = json.load(clones_file)
            total_clones = sum(item.get('count', 0) for item in clones_data)
    except Exception as e:
        print(f"Error reading {clones_file_path}: {e}")

# Ensure downloads.json exists and has initial data if it doesn't exist
if not os.path.exists(downloads_file_path):
    initial_downloads_data = []
    try:
        with open(downloads_file_path, 'w') as downloads_file:
            json.dump(initial_downloads_data, downloads_file)
            print(f"Created initial {downloads_file_path}")
    except Exception as e:
        print(f"Error creating {downloads_file_path}: {e}")
else:
    # Read and sum the 'download_count' values from downloads.json, ensuring no duplicates
    try:
        with open(downloads_file_path, 'r') as downloads_file:
            downloads_data = json.load(downloads_file)

            # Use a set to keep track of unique asset IDs
            seen_asset_ids = set()
            for item in downloads_data:
                asset_id = item.get('asset_id')
                if asset_id not in seen_asset_ids:
                    seen_asset_ids.add(asset_id)
                    download_count = item.get('download_count', 0)
                    total_downloads += download_count
    except Exception as e:
        print(f"Error reading {downloads_file_path}: {e}")

# Fetch the latest release from the foreign repository
#/sandialabs/snl-quest

OWNER = "sandialabs"
REPO = "snl-quest"
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
headers = {
    "Authorization": f"token {os.getenv('QUEST_TOKEN')}"
}

try:
    response = requests.get(GITHUB_API_URL, headers=headers)
    response.raise_for_status()
    latest_release = response.json()
    latest_release_tag = latest_release["tag_name"]
except requests.exceptions.RequestException as e:
    latest_release_tag = "unknown"
    print(f"Error fetching latest release: {e}")
except KeyError as e:
    latest_release_tag = "unknown"
    print(f"Key error in the response data: {e}")

print(f'Total Clones: {total_clones}')
print(f'Total Downloads: {total_downloads}')
print(f'Latest Release: {latest_release_tag}')

# Calculate the combined total
combined_total = total_clones + total_downloads

# Prepare the output data for the summed downloads and clones
output_data = {
    "schemaVersion": 1,
    "label": "Downloads",
    "message": str(combined_total),
    "color": "blue"
}

# Prepare the output data for the latest release clones
release_output_data = {
    "schemaVersion": 1,
    "label": f"v2.0 clones",
    "message": str(total_clones),
    "color": "purple"
}

# Write the output data to badge_data.json
try:
    with open(output_file_path, 'w') as output_file:
        json.dump(output_data, output_file)
        print(f"Successfully wrote to {output_file_path}")
except Exception as e:
    print(f"Error writing to {output_file_path}: {e}")

# Write the release clones data to release_badge_data.json
try:
    with open(release_output_file_path, 'w') as output_file:
        json.dump(release_output_data, output_file)
        print(f"Successfully wrote to {release_output_file_path}")
except Exception as e:
    print(f"Error writing to {release_output_file_path}: {e}")
