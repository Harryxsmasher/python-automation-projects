import json

with open('completed/data.json', 'r') as file:
    python_obj = json.load(file)
print(python_obj)