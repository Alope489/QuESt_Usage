import requests
import logging
import json
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_github_downloads(repo_owner, repo_name, access_token):
    logging.info("Starting to fetch download statistics from GitHub.")
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Failed to fetch data: {response.status_code} - {response.text}")
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

    releases = response.json()
    download_stats = []

    for release in releases:
        for asset in release['assets']:
            download_stats.append({
                "release_id": release['id'],
                "release_name": release['name'],
                "asset_id": asset['id'],
                "asset_name": asset['name'],
                "download_count": asset['download_count'],
                "created_at": asset['created_at'],
                "updated_at": asset['updated_at']
            })

    logging.info(f"Fetched download statistics for {len(releases)} releases.")
    return download_stats

def get_repo_traffic(repo_owner, repo_name, access_token):
    logging.info("Starting to fetch repository traffic data from GitHub.")
    url_clones = f"https://api.github.com/repos/{repo_owner}/{repo_name}/traffic/clones"
    headers = {"Authorization": f"token {access_token}"}

    response_clones = requests.get(url_clones, headers=headers)

    if response_clones.status_code != 200:
        logging.error(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")
        raise Exception(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")

    clones_data = response_clones.json().get('clones', [])
    return clones_data

def save_to_json(data, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
        existing_data.extend(data)
    else:
        existing_data = data

    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=4)

def main():
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = "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"
    try:
        download_stats = get_github_downloads(repo_owner, repo_name, access_token)
        save_to_json(download_stats, "downloads.json")

        clones_data = get_repo_traffic(repo_owner, repo_name, access_token)
        save_to_json(clones_data, "clones.json")

        logging.info("Script ran successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

if __name__ == "__main__":
    main()

