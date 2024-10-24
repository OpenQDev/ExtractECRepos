import pandas as pd
import argparse
import os

def find_file_in_directory(filename):
    # Walk through the directory tree
    for root, dirs, files in os.walk('.'):
        # Check for the file in the current directory
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(f"File '{filename}' not found in the current directory or any subdirectories.")

def get_links_from_file(file_path, column_names):
    df = pd.read_csv(file_path)
    for column in column_names:
        if column in df.columns:
            # Convert all links to lowercase for case-insensitive comparison
            return set(df[column].str.lower())
    raise ValueError(f"None of the specified columns {column_names} found in {file_path}")

def compare_csv(file1_name, file2_name, additional_columns):
    # Find the full paths of the files
    file1_path = find_file_in_directory(file1_name)
    file2_path = find_file_in_directory(file2_name)

    # Default column names plus any additional ones provided
    default_columns = ['repo_link', 'githubLink']
    column_names = default_columns + additional_columns

    # Extract the relevant columns
    file1_links = get_links_from_file(file1_path, column_names)
    file2_links = get_links_from_file(file2_path, column_names)

    # Find new repos in each file
    new_in_file1 = file1_links - file2_links
    new_in_file2 = file2_links - file1_links

    # Prepare summary
    summary = (
        f"Summary:\n"
        f"{file1_name} has {len(new_in_file1)} new repos\n"
        f"{file2_name} has {len(new_in_file2)} new repos\n"
    )

    # Print summary to the command line
    print(summary)

    # Ensure the output directory exists
    output_dir = './comparison-results'
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_filename = os.path.join(output_dir, f"{file1_name}-{file2_name}.txt")
    
    with open(output_filename, 'w') as f:
        # Write summary to file
        f.write(summary + "\n")

        # Write detailed output for file1
        f.write(f"{file1_path} has {len(new_in_file1)} new repos:\n")
        for repo in new_in_file1:
            f.write(f"{repo}\n")
        f.write("\n")

        # Write detailed output for file2
        f.write(f"{file2_path} has {len(new_in_file2)} new repos:\n")
        for repo in new_in_file2:
            f.write(f"{repo}\n")

    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two CSV files for new repository links.')
    parser.add_argument('file1', help='Name of the first CSV file')
    parser.add_argument('file2', help='Name of the second CSV file')
    parser.add_argument('--columns', nargs='*', default=[], help='Additional column names to look for links')

    args = parser.parse_args()
    compare_csv(args.file1, args.file2, args.columns)
