import os
import toml
import git
import sys

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

def find_toml_file(base_dir, filename):
    """Recursively search for a TOML file with the given filename."""
    for root, dirs, files in os.walk(base_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def extract_sub_ecosystems(toml_file):
    """Extract the 'sub_ecosystems' array from the given TOML file."""
    try:
        data = toml.load(toml_file)
        sub_ecosystems = data.get('sub_ecosystems', [])
        if not sub_ecosystems:
            return []

        # finding all the sub-ecosystems
        transformed_ecosystems = [s.lower().replace(' (', '-').replace(')', '').replace(' ', '-') for s in sub_ecosystems]
        print(f"Found {len(transformed_ecosystems)} sub-ecosystems overall")

        transformed_ecosystems_brackets = [s.lower().split(' (')[0].replace(' ', '-') for s in sub_ecosystems if '(' in s]
        if len(transformed_ecosystems_brackets) > 0:
            print(f"Found {len(transformed_ecosystems_brackets)} sub-ecosystems which include brackets")

        transformed_ecosystems.extend(transformed_ecosystems_brackets)
        
        transformed_ecosystems = list(set(transformed_ecosystems))
        print(f"Found {len(transformed_ecosystems)} potential sub-ecosystem files")
        return transformed_ecosystems
    except Exception as e:
        print(f"Error reading {toml_file}: {e}")
        return []

def find_all_toml_files(base_dir):
    """Find all TOML files in the directory."""
    toml_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.toml'):
                toml_files.append(os.path.join(root, file))
    return toml_files

def extract_repo_urls(toml_files):
    """Extract [[repo]] URL links from a list of TOML files."""
    repo_urls = []
    for file in toml_files:
        repo_urls.extend(extract_repo_urls_recursive(file))
    return repo_urls

def extract_repo_urls_recursive(toml_file):
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
            sub_ecosystem_file = find_toml_file(os.path.dirname(toml_file), sub_ecosystem + '.toml')
            
            if sub_ecosystem_file:
                urls.extend(extract_repo_urls_recursive(sub_ecosystem_file))
    except Exception as e:
        print(f"Error reading {toml_file}: {e}")
    return urls

def write_combined_toml(output_file, repo_urls):
    """Write the combined TOML file with all [[repo]] links."""
    with open(output_file, 'w') as f:
        f.write('[repo]\n')
        for url in repo_urls:
            f.write(f'url = "{url}"\n')
    print(f"Combined TOML file written to {output_file}")

def main(repo_url, original_toml_filename):
    clone_dir = repo_url.split('/')[-1].replace('.git', '')
    clone_repo(repo_url, clone_dir)
    
    original_toml_file = find_toml_file(clone_dir, original_toml_filename)
    if not original_toml_file:
        print(f"File {original_toml_filename} not found in the repository.")
        return
    
    sub_ecosystems = extract_sub_ecosystems(original_toml_file)
    if not sub_ecosystems:
        print(f"No 'sub_ecosystems' found in {original_toml_filename}.")
        return
    
    all_toml_files = find_all_toml_files(clone_dir)
    print(f"Looking through {len(all_toml_files)} TOML files in the repository...")
    
    toml_files_to_check_set = set([original_toml_file])
    for ecosystem_file in sub_ecosystems:
        found_toml_file = find_toml_file(clone_dir, ecosystem_file + '.toml')
        if found_toml_file:
            # print(f"Adding ub-ecosystem file: {found_toml_file}")
            toml_files_to_check_set.add(found_toml_file)

    toml_files_to_check = list(toml_files_to_check_set)
    toml_files_to_check.sort(key=str.lower)
    print(f"Combining {len(toml_files_to_check)} sub-ecosystem TOML files")

    repo_urls = list(set(extract_repo_urls(toml_files_to_check)))
    print(f"Extracted a total of {len(repo_urls)} unique repo URLs")
    output_toml_filename = original_toml_filename.replace('.toml', '_combined.toml')
    write_combined_toml(output_toml_filename, repo_urls)

if __name__ == '__main__':
    ELECTRIC_CAPITAL_REPO_URL = "https://github.com/electric-capital/crypto-ecosystems"

    if len(sys.argv) != 2:
        print("Usage: python3 extract.py <ecosystem_file_name>")
        sys.exit(1)

    ecosystem_file = sys.argv[1]

    main(ELECTRIC_CAPITAL_REPO_URL, ecosystem_file)
