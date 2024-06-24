import requests
import logging
import json
from datetime import datetime, timedelta
import os

def get_github_downloads(repo_owner, repo_name, access_token):
    logging.info("Starting to fetch download statistics from GitHub.")
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    headers = {
        "Authorization": f"token {access_token}"
    }
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
    url_referrers = f"https://api.github.com/repos/{repo_owner}/{repo_name}/traffic/popular/referrers"
    url_paths = f"https://api.github.com/repos/{repo_owner}/{repo_name}/traffic/popular/paths"
    headers = {
        "Authorization": f"token {access_token}"
    }

    response_clones = requests.get(url_clones, headers=headers)
    response_referrers = requests.get(url_referrers, headers=headers)
    response_paths = requests.get(url_paths, headers=headers)

    if response_clones.status_code != 200:
        logging.error(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")
        raise Exception(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")

    if response_referrers.status_code != 200:
        logging.error(f"Failed to fetch referrers data: {response_referrers.status_code} - {response_referrers.text}")
        raise Exception(f"Failed to fetch referrers data: {response_referrers.status_code} - {response_referrers.text}")

    if response_paths.status_code != 200:
        logging.error(f"Failed to fetch paths data: {response_paths.status_code} - {response_paths.text}")
        raise Exception(f"Failed to fetch paths data: {response_paths.status_code} - {response_paths.text}")

    current_time = datetime.utcnow().date()
    start_time = current_time - timedelta(days=14)

    traffic_data = {
        "clones": [{"timestamp": clone["timestamp"], **clone} for clone in response_clones.json().get('clones', [])],
        "referrers": [{"timestamp_start": start_time.isoformat(), "timestamp_end": current_time.isoformat(), **referrer} for referrer in response_referrers.json()],
        "paths": [{"timestamp_start": start_time.isoformat(), "timestamp_end": current_time.isoformat(), **path} for path in response_paths.json()]
    }

    return traffic_data

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
    access_token = os.getenv("GITHUB_TOKEN")
    try:
        download_stats = get_github_downloads(repo_owner, repo_name, access_token)
        save_to_json(download_stats, "downloads.json")
        
        traffic_stats = get_repo_traffic(repo_owner, repo_name, access_token)
        save_to_json(traffic_stats["clones"], "clones.json")
        save_to_json(traffic_stats["referrers"], "referrers.json")
        save_to_json(traffic_stats["paths"], "paths.json")
        
        logging.info("Script ran successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

if __name__ == "__main__":
    main()

