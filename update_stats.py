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
    else:
        existing_data = []

    updated_data = []
    if filename == "clones.json":
        updated_data = update_clones(existing_data, data)
    elif filename == "downloads.json":
        updated_data = update_downloads(existing_data, data)
    elif filename in ["referrers.json", "paths.json"]:
        updated_data = append_unique(existing_data, data)

    with open(filename, 'w') as f:
        json.dump(updated_data, f, indent=4)

def update_clones(existing_data, new_data):
    existing_dict = {entry["timestamp"]: entry for entry in existing_data}
    for new_entry in new_data:
        if new_entry["timestamp"] in existing_dict:
            existing_dict[new_entry["timestamp"]].update(new_entry)
        else:
            existing_dict[new_entry["timestamp"]] = new_entry
    return list(existing_dict.values())

def update_downloads(existing_data, new_data):
    existing_dict = {(entry["release_id"], entry["asset_id"]): entry for entry in existing_data}
    for new_entry in new_data:
        key = (new_entry["release_id"], new_entry["asset_id"])
        if key in existing_dict:
            existing_dict[key].update(new_entry)
        else:
            existing_dict[key] = new_entry
    return list(existing_dict.values())

def append_unique(existing_data, new_data):
    existing_dict = {tuple(entry.items()): entry for entry in existing_data}
    for new_entry in new_data:
        key = tuple(new_entry.items())
        if key not in existing_dict:
            existing_dict[key] = new_entry
    return list(existing_dict.values())

def aggregate_referrals():
    if os.path.exists("referrers.json"):
        with open("referrers.json", 'r') as f:
            referrers_data = json.load(f)
    else:
        referrers_data = []

    aggregate_data = {}
    for entry in referrers_data:
        referrer = entry["referrer"]
        if referrer not in aggregate_data:
            aggregate_data[referrer] = {"referrer": referrer, "count": 0, "uniques": 0}
        aggregate_data[referrer]["count"] += entry["count"]
        aggregate_data[referrer]["uniques"] += entry["uniques"]

    with open("aggregated_referrers.json", 'w') as f:
        json.dump(list(aggregate_data.values()), f, indent=4)

def main():
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv("QUEST_TOKEN")
    try:
        download_stats = get_github_downloads(repo_owner, repo_name, access_token)
        save_to_json(download_stats, "downloads.json")

        traffic_stats = get_repo_traffic(repo_owner, repo_name, access_token)
        save_to_json(traffic_stats["clones"], "clones.json")
        save_to_json(traffic_stats["referrers"], "referrers.json")
        save_to_json(traffic_stats["paths"], "paths.json")

        aggregate_referrals()

        logging.info("Script ran successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
