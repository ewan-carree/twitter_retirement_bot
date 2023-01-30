
import json
import os

# Using OS library to call CLI commands in Python
os.system("snscrape --jsonl --max-results 5 twitter-search Retraite> user-tweets.json")

# load JSON data from file
with open("user-tweets.json", "r") as file:
    data = file.readlines()

# parse JSON data into a list of dictionaries
records = [json.loads(record) for record in data]

# wrap records in a single dictionary
wrapped_data = {"records": records}

# save wrapped data to a new file
with open("wrapped_data.json", "w") as file:
    json.dump(wrapped_data, file, indent=4)

for record in records:
    print(record["renderedContent"])
    print()
