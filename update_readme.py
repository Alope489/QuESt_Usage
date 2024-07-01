import os

def read_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def write_file(filepath, content):
    with open(filepath, 'w') as file:
        file.write(content)

def update_readme(readme_path, plot_path, downloads_md_path, paths_md_path, referrers_md_path):
    # Read the README.md file
    readme_content = read_file(readme_path)

    # Read the plot and markdown table files
    plot_url = f'![Clones Plot](plots/clones_plot.png)'
    downloads_md = read_file(downloads_md_path)
    paths_md = read_file(paths_md_path)
    referrers_md = read_file(referrers_md_path)

    # Check if placeholders or existing content
    if 'PLOT_PLACEHOLDER' in readme_content:
        readme_content = readme_content.replace('PLOT_PLACEHOLDER', plot_url)
    else:
        readme_content = readme_content.replace(f'![Clones Plot](plots/clones_plot.png)', plot_url)

    if 'TABLE_DOWNLOADS_PLACEHOLDER' in readme_content:
        readme_content = readme_content.replace('TABLE_DOWNLOADS_PLACEHOLDER', downloads_md)
    else:
        start = readme_content.find('## Release Downloads') + len('## Release Downloads')
        end = readme_content.find('## Most Visited Paths')
        readme_content = readme_content[:start] + '\n' + downloads_md + '\n' + readme_content[end:]

    if 'TABLE_PATHS_PLACEHOLDER' in readme_content:
        readme_content = readme_content.replace('TABLE_PATHS_PLACEHOLDER', paths_md)
    else:
        start = readme_content.find('## Most Visited Paths') + len('## Most Visited Paths')
        end = readme_content.find('## Referrers')
        readme_content = readme_content[:start] + '\n' + paths_md + '\n' + readme_content[end:]

    if 'TABLE_REFERRERS_PLACEHOLDER' in readme_content:
        readme_content = readme_content.replace('TABLE_REFERRERS_PLACEHOLDER', referrers_md)
    else:
        start = readme_content.find('## Referrers') + len('## Referrers')
        end = len(readme_content)
        readme_content = readme_content[:start] + '\n' + referrers_md + '\n' + readme_content[end:]

    # Write the updated content back to the README.md file
    write_file(readme_path, readme_content)

def main():
    # Paths to the files
    readme_path = 'README.md'
    plot_path = 'plots/clones_plot.png'
    downloads_md_path = 'plots/downloads_table.md'
    paths_md_path = 'plots/paths_table.md'
    referrers_md_path = 'plots/referrers_table.md'

    # Update the README.md file
    update_readme(readme_path, plot_path, downloads_md_path, paths_md_path, referrers_md_path)

if __name__ == "__main__":
    main()
