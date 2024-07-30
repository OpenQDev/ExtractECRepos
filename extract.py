import os
import toml
import git
import requests

def clone_repo(repo_url, clone_dir):
    """Clone a Git repository to a specified directory."""
    print(f"Cloning repository from {repo_url} into {clone_dir}...")
#    git.Repo.clone_from(repo_url, clone_dir)

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
        # finding all the sub-ecosystems
        transformed_ecosystems = [s.lower().replace(' (', '-').replace(')', '').replace(' ', '-') for s in sub_ecosystems]
        print(f"Found {len(transformed_ecosystems)} sub-ecosystems overall")

        transformed_ecosystems_brackets = [s.lower().split(' (')[0].replace(' ', '-') for s in sub_ecosystems if '(' in s]
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
                # print(f"appending {file}...")
                toml_files.append(os.path.join(root, file))
    return toml_files

def extract_repo_urls(toml_files):
    """Extract [[repo]] URL links from a list of TOML files."""
    repo_urls = []
    for file in toml_files:
        try:
            data = toml.load(file)
            for repo in data.get('repo', []):
                if 'url' in repo:
                    repo_urls.append(repo['url'])
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return repo_urls

def write_combined_toml(output_file, repo_urls):
    """Write the combined TOML file with all [[repo]] links."""
    with open(output_file, 'w') as f:
        f.write('[repo]\n')
        for url in repo_urls:
            f.write(f'url = "{url}"\n')
    print(f"Combined TOML file written to {output_file}")

def main(repo_url, original_toml_filename, output_toml_filename):
    clone_dir = 'repo_clone'
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

    repo_urls = extract_repo_urls(toml_files_to_check)
    print(f"Extracted a total of {len(repo_urls)} repo URLs")
    write_combined_toml(output_toml_filename, repo_urls)

if __name__ == '__main__':
    # Fill in data you want to use
    REPO_URL = 'https://github.com/electric-capital/crypto-ecosystems.git'
    ORIGINAL_TOML_FILENAME = 'polygon.toml'
    OUTPUT_TOML_FILENAME = 'combined_repos.toml'
    
    main(REPO_URL, ORIGINAL_TOML_FILENAME, OUTPUT_TOML_FILENAME)
