## Extract all repositories from one ecosystem (electric capital data)

Data from: [Electric Capital](https://github.com/electric-capital/crypto-ecosystems)

# Pre-requisites

1. use Python 3.8.10 or higher
2. install dependencies: `pip install -r requirements.txt`

# Extract all repo urls related to an ecosystem (including sub-ecosystem repo urls)

1. in the CLI:

`python3 extract.py <ecosystem_file_name>`

For example, to get all repo urls for the Polygon ecosystem & sub ecosystems:

`python3 extract.py polygon.toml`

2. get your toml and csv file from the /results folder



## Compare two csv files for their links

This script will automatically look for any columns called "repo_link" or "githubLink" in two csv
files and output a summary of the repos that are new to one or the other file.

Same pre-requisites as mentioned above

1. in the CLI:

`python3 compareCSV.py <csv_file_name1> <csv_file_name2>`

For example:

`python3 compareCSV.py polygon.csv polygon_new.csv`

1. get your toml and csv file from the /comparison-results folder
