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

    # Function to replace content between markers
    def replace_between_markers(content, start_marker, end_marker, replacement):
        start_index = content.find(start_marker) + len(start_marker)
        end_index = content.find(end_marker)
        if start_index == -1 or end_index == -1:
            return content
        return content[:start_index] + '\n' + replacement + '\n' + content[end_index:]

    # Update plot section
    readme_content = replace_between_markers(
        readme_content,
        '<!-- PLOT_PLACEHOLDER_START -->',
        '<!-- PLOT_PLACEHOLDER_END -->',
        plot_url
    )

    # Update downloads table section
    readme_content = replace_between_markers(
        readme_content,
        '<!-- TABLE_DOWNLOADS_PLACEHOLDER_START -->',
        '<!-- TABLE_DOWNLOADS_PLACEHOLDER_END -->',
        downloads_md
    )

    # Update paths table section
    readme_content = replace_between_markers(
        readme_content,
        '<!-- TABLE_PATHS_PLACEHOLDER_START -->',
        '<!-- TABLE_PATHS_PLACEHOLDER_END -->',
        paths_md
    )

    # Update referrers table section
    readme_content = replace_between_markers(
        readme_content,
        '<!-- TABLE_REFERRERS_PLACEHOLDER_START -->',
        '<!-- TABLE_REFERRERS_PLACEHOLDER_END -->',
        referrers_md
    )

    # Write the updated content back to the README.md file
    write_file(readme_path, readme_content)

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to the files
    readme_path = os.path.join(current_dir, 'README.md')
    plot_path = os.path.join(current_dir, 'plots/clones_plot.png')
    downloads_md_path = os.path.join(current_dir, 'plots/downloads_table.md')
    paths_md_path = os.path.join(current_dir, 'plots/paths_table.md')
    referrers_md_path = os.path.join(current_dir, 'plots/referrers_table.md')

    # Update the README.md file
    update_readme(readme_path, plot_path, downloads_md_path, paths_md_path, referrers_md_path)

if __name__ == "__main__":
    main()

