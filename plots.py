import os
import json
import logging
import matplotlib.pyplot as plt
import pandas as pd

# Explicitly import tabulate
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger()

# Directory paths
root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(root_dir, 'data')
output_dir = os.path.join(root_dir, 'plots')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Helper function to load JSON data
def load_json_data(filename):
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            logger.info(f"Loaded data from {filename}: {data[:2]}...")  # Log the first two records for debugging
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {filename}")
        return []

# Function to generate and save the clones plot
def save_clones_plot(clones, output_dir):
    if not clones:
        logger.warning("No clones data available to plot")
        return

    # Convert list of dictionaries to DataFrame
    clones_df = pd.DataFrame(clones)

    # Convert timestamp to datetime and set it as the index
    clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp'])
    clones_df.set_index('timestamp', inplace=True)

    # Remove duplicate entries by summing counts and uniques for each day
    clones_df = clones_df.resample('D').sum()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(clones_df.index, clones_df['count'], marker='o', label='Total Clones')
    ax.plot(clones_df.index, clones_df['uniques'], marker='o', label='Unique Clones')
    ax.set_title('Clones Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Clones')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    
    fig.subplots_adjust(bottom=0.2, top=0.9)  # Adjust margins to reduce white space
    plt.savefig(os.path.join(output_dir, 'clones_plot.png'), bbox_inches='tight', pad_inches=0.01)  # Reduce padding
    plt.close()

# Function to add totals row to a DataFrame
def add_totals_row(df, count_col, uniques_col):
    if df.empty:
        logger.warning(f"DataFrame is empty, cannot add totals row for columns: {count_col}, {uniques_col}")
        return df

    total_count = df[count_col].astype(int).sum()
    total_uniques = df[uniques_col].astype(int).sum() if uniques_col else None

    if uniques_col:
        totals_row = pd.DataFrame({count_col: [total_count], uniques_col: [total_uniques]}, index=["Total"])
    else:
        totals_row = pd.DataFrame({count_col: [total_count]}, index=["Total"])

    return pd.concat([df, totals_row])

# Main function to generate markdown tables and plots
def main():
    # Load data from JSON files
    clones = load_json_data("clones.json")
    referrers = load_json_data("aggregated_referrers.json")
    paths = load_json_data("aggregated_paths.json")
    downloads = load_json_data("downloads.json")

    # Debug: Print the keys of the loaded data
    logger.info(f"Clones keys: {clones[0].keys() if clones else 'No data'}")
    logger.info(f"Referrers keys: {referrers[0].keys() if referrers else 'No data'}")
    logger.info(f"Paths keys: {paths[0].keys() if paths else 'No data'}")
    logger.info(f"Downloads keys: {downloads[0].keys() if downloads else 'No data'}")

    # Create DataFrames
    referrers_df = pd.DataFrame(referrers)
    if not referrers_df.empty and 'referrer' in referrers_df.columns and 'count' in referrers_df.columns and 'uniques' in referrers_df.columns:
        referrers_df = referrers_df[['referrer', 'count', 'uniques']]
        referrers_df.columns = ["Referrer", "Number of Referrals", "Unique Referrals"]
        referrers_df = add_totals_row(referrers_df, "Number of Referrals", "Unique Referrals")
    else:
        logger.warning("Referrers data is missing expected columns or is empty")

    paths_df = pd.DataFrame(paths)
    if not paths_df.empty and 'path' in paths_df.columns and 'count' in paths_df.columns and 'uniques' in paths_df.columns:
        paths_df = paths_df[['path', 'count', 'uniques']]
        paths_df.columns = ["Most Visited Path", "Times Visited", "Unique Visits"]
        paths_df = add_totals_row(paths_df, "Times Visited", "Unique Visits")
    else:
        logger.warning("Paths data is missing expected columns or is empty")

    downloads_df = pd.DataFrame(downloads)
    if not downloads_df.empty and 'asset_name' in downloads_df.columns and 'download_count' in downloads_df.columns:
        downloads_df = downloads_df[['asset_name', 'download_count']]
        downloads_df.columns = ["Asset Name", "Download Count"]
        downloads_df = add_totals_row(downloads_df, "Download Count", None)
    else:
        logger.warning("Downloads data is missing expected columns or is empty")

    # Generate and save the clones plot
    save_clones_plot(clones, output_dir)

    # Convert DataFrames to markdown
    referrers_md = dataframe_to_markdown(referrers_df)
    paths_md = dataframe_to_markdown(paths_df)
    downloads_md = dataframe_to_markdown(downloads_df)

    # Save markdown tables to files
    with open(os.path.join(output_dir, 'referrers_table.md'), 'w') as f:
        f.write(referrers_md)
    with open(os.path.join(output_dir, 'paths_table.md'), 'w') as f:
        f.write(paths_md)
    with open(os.path.join(output_dir, 'downloads_table.md'), 'w') as f:
        f.write(downloads_md)

    logger.info("Tables and plot have been saved in the 'plots' directory.")

# Entry point
if __name__ == "__main__":
    main()

