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