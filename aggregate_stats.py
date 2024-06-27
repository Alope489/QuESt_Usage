import requests
import logging
import json
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_github_data(repo_owner, repo_name, access_token, data_type):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/traffic/{data_type}"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {data_type} data: {response.status_code}")
    return response.json()

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def aggregate_data(new_data, existing_data, key_field, count_field, unique_field):
    existing_dict = {entry[key_field]: entry for entry in existing_data}

    for entry in new_data:
        key = entry[key_field]
        if key in existing_dict:
            existing_dict[key][count_field] += entry[count_field]
            existing_dict[key][unique_field] += entry[unique_field]
        else:
            existing_dict[key] = {
                key_field: key,
                count_field: entry[count_field],
                unique_field: entry[unique_field]
            }
    return list(existing_dict.values())

def save_aggregated_data(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv('GITHUB_TOKEN')

    try:
        # Pull data from GitHub API
        referrers_response = get_github_data(repo_owner, repo_name, access_token, "popular/referrers")
        referrers_data = referrers_response if isinstance(referrers_response, list) else referrers_response.get('referrers', [])

        paths_response = get_github_data(repo_owner, repo_name, access_token, "popular/paths")
        paths_data = paths_response if isinstance(paths_response, list) else paths_response.get('paths', [])

        # Load existing aggregated data
        aggregated_referrers = load_json("data/aggregated_referrers.json")
        aggregated_paths = load_json("data/aggregated_paths.json")

        # Aggregate new data with existing data
        aggregated_referrers = aggregate_data(referrers_data, aggregated_referrers, "referrer", "count", "uniques")
        aggregated_paths = aggregate_data(paths_data, aggregated_paths, "path", "count", "uniques")

        # Save updated aggregated data
        save_aggregated_data(aggregated_referrers, "data/aggregated_referrers.json")
        save_aggregated_data(aggregated_paths, "data/aggregated_paths.json")

        logging.info("Aggregation script ran successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
