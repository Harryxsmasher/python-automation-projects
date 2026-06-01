import json

with open("ExampleJSON/DUMPDATA/example.json", "r") as f:
    data = json.load(f)

for member in data['members']:
    print(member['name'], member['age'], member['secretIdentity'], member['powers'])
