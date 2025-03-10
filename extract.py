import os
import toml
import git
import sys
import re

TOML_EXTENSION = '.toml'

def clone_repo(repo_url, clone_dir):
    """Clone a Git repository to a specified directory if it doesn't exist, otherwise pull."""
    if os.path.exists(clone_dir):
        repo = git.Repo(clone_dir)
        origin = repo.remote(name='origin')
        origin.pull()
        print(f"Pulled changes for repository at {clone_dir}")
    else:
        print(f"Cloning repository from {repo_url} into {clone_dir}...")
        git.Repo.clone_from(repo_url, clone_dir)

def purify_string(input_string):
    # Remove non-alphanumeric characters and convert to lowercase
    return ''.join(re.findall(r'\w+', input_string)).lower()

def find_toml_file(base_dir, filename):
    """Find a file."""
    purified_filename = purify_string(filename)
    for root, dirs, files in os.walk(base_dir):
        for file_to_check in files:
            if purify_string(file_to_check) == purified_filename:
                return os.path.join(root, file_to_check)
    return None

def match_toml_file(all_toml_files, filename):
    """Match a file with the exhaustive liste of toml filenames."""
    purified_filename = purify_string(filename)
    for file_to_check in all_toml_files:
        if purified_filename in purify_string(file_to_check):
            return file_to_check
    return None

def extract_sub_ecosystems(toml_file):
    """Extract the 'sub_ecosystems' array from the given TOML file."""
    try:
        data = toml.load(toml_file)
        sub_ecosystems = data.get('sub_ecosystems', [])
        if not sub_ecosystems:
            return []
        return sub_ecosystems
    
    except Exception as e:
        print(f"Error reading {toml_file}: {e}")
        return []

def find_all_toml_files(base_dir):
    """Find all TOML files in the directory."""
    toml_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(TOML_EXTENSION):
                toml_files.append(os.path.join(root, file))
    return toml_files

def extract_repo_urls(all_toml_files, toml_files):
    """Extract [[repo]] URL links from a list of TOML files."""
    repo_urls = []
    for file in toml_files:
        repo_urls.extend(extract_repo_urls_recursive(all_toml_files, file))
    return repo_urls

def extract_repo_urls_recursive(all_toml_files, toml_file):
    """Recursively extract [[repo]] URL links from a TOML file and its sub-ecosystems."""
    urls = []
    try:
        data = toml.load(toml_file)
        for repo in data.get('repo', []):
            if 'url' in repo:
                urls.append(repo['url'])
        
        sub_ecosystems = extract_sub_ecosystems(toml_file)
        if not sub_ecosystems:
            return urls
        if len(sub_ecosystems) > 0: 
            print(f"Found {len(sub_ecosystems)} sub-ecosystems in {toml_file}: {sub_ecosystems}")
        for sub_ecosystem in sub_ecosystems:
            sub_ecosystem_file = match_toml_file(all_toml_files, sub_ecosystem + TOML_EXTENSION)
            
            if sub_ecosystem_file:
                urls.extend(extract_repo_urls_recursive(all_toml_files, sub_ecosystem_file))
    except Exception as e:
        print(f"Error reading {toml_file}: {e}")
    return urls

def write_combined_toml(output_file, repo_urls):
    """Write the combined TOML file with all [[repo]] links."""
    with open(output_file, 'w') as f:
        for url in repo_urls:
            f.write(f'[[repo]]\nurl = "{url}"\n\n')
    print(f"Combined TOML file written to {output_file}")

def write_combined_csv(output_file, repo_urls):
    """Write the combined CSV file with repo owner, repo name, and links."""
    with open(output_file, 'w') as f:
        f.write("repo_name,repo_link\n")
        for url in repo_urls:
            parts = url.split('/')
            repo_owner = parts[-2]
            repo_name = parts[-1].replace('.git', '')
            f.write(f'{repo_owner}/{repo_name},{url}\n')
    print(f"Combined CSV file written to {output_file}")


def main(repo_url, original_toml_filename):
    clone_dir = repo_url.split('/')[-1].replace('.git', '')
    clone_repo(repo_url, clone_dir)
    
    original_toml_file = find_toml_file(clone_dir, original_toml_filename)
    if not original_toml_file:
        print(f"File {original_toml_filename} not found in the repository.")
        return
    
    all_toml_files = find_all_toml_files(clone_dir)
    print(f"Looking through {len(all_toml_files)} TOML files in the repository...")

    sub_ecosystems = extract_sub_ecosystems(original_toml_file)
    if not sub_ecosystems:
        print(f"No 'sub_ecosystems' found in {original_toml_filename}.")
    
    toml_files_to_check_set = set([original_toml_file])
    for ecosystem_file in sub_ecosystems:
        if ecosystem_file == "The LAOs Chain (KLAOS)":
            print(f"Skipping {ecosystem_file}")
        found_toml_file = match_toml_file(all_toml_files, ecosystem_file + TOML_EXTENSION)
        if found_toml_file:
            # print(f"Adding ub-ecosystem file: {found_toml_file}")
            toml_files_to_check_set.add(found_toml_file)

    toml_files_to_check = list(toml_files_to_check_set)
    toml_files_to_check.sort(key=str.lower)
    # print(f"Combining {toml_files_to_check} sub-ecosystem TOML files")

    repo_urls = list(set(extract_repo_urls(all_toml_files, toml_files_to_check)))
    print(f"Extracted a total of {len(repo_urls)} unique repo URLs")

    if not os.path.exists("results"):
        os.makedirs("results")

    output_toml_filename = os.path.join("results", original_toml_filename.replace(TOML_EXTENSION, '_combined.toml'))
    write_combined_toml(output_toml_filename, repo_urls)

    output_csv_filename = os.path.join("results", original_toml_filename.replace(TOML_EXTENSION, '_combined.csv'))
    write_combined_csv(output_csv_filename, repo_urls)

if __name__ == '__main__':
    ELECTRIC_CAPITAL_REPO_URL = "https://github.com/electric-capital/crypto-ecosystems"

    if len(sys.argv) != 2:
        print("Usage: python3 extract.py <ecosystem_file_name>")
        sys.exit(1)

    ecosystem_file = sys.argv[1]

    main(ELECTRIC_CAPITAL_REPO_URL, ecosystem_file)
