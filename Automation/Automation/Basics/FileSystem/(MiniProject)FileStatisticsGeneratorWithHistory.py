from pathlib import Path
import json

folder = Path(input("Enter the path: "))

if not folder.exists() or not folder.is_dir():
    print("Folder not found!")
    exit()

# Fresh statistics for this scan
files_stat = {}

for file in folder.rglob("*.*"):
    extension = file.suffix

    if extension in files_stat:
        files_stat[extension] += 1
    else:
        files_stat[extension] = 1

print("\nCurrent Scan Results:")
for extension, count in files_stat.items():
    print(f"{extension}: {count}")

# History file
history_file = folder / "file_stats_history.json"

# Load existing history
try:
    with open(history_file, "r") as f:
        history = json.load(f)

except FileNotFoundError:
    history = []

# Add current scan to history
history.append(files_stat)

# Save updated history
with open(history_file, "w") as f:
    json.dump(history, f, indent=4)

print("\nHistory updated successfully!")

# Verify what was saved
with open(history_file, "r") as f:
    loaded_history = json.load(f)

print(f"\nTotal scans stored: {len(loaded_history)}")

print("\nHistory Contents:")
for scan_number, scan in enumerate(loaded_history, start=1):
    print(f"\nScan {scan_number}")

    for extension, count in scan.items():
        print(f"{extension}: {count}")