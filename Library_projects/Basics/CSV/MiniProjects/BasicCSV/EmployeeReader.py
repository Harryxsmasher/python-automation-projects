from pathlib import Path
import csv

csv_file = Path(
    r"C:\Users\Prave\Desktop\Projects\python-automation-projects\Library_projects\Basics\CSV\MiniProjects\BasicCSV"
) / "employee.csv"


with open(csv_file, "r") as f:
    # reader = csv.reader(f)

    # next(reader)
    # for row in reader:
    #     print(f"{row[0]} - {row[1]} - {row[2]}")

    reader = csv.DictReader(f)

    
    for row in reader:
        print(f'{row["Name"]} - {row["Department"]} - {row["Experience"]} years')