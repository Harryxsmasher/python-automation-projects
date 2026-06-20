import csv
from pathlib import Path

csv_file = Path(
    r"C:\Users\Prave\Desktop\Projects\python-automation-projects\Library_projects\Basics\CSV\MiniProjects\BasicCSV"
) / "employee.csv"

headers = ["Name", "Phone_Number"]

def add_contacts(Name, Phno):
    with open(csv_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        contact_details = {"Name" : Name, "Phone_Number" : Phno}
        writer.writeheader()
        writer.writerow(contact_details)
    print("Contact Added Successfully")

def view_contacts():
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f'{row["Name"]} - {row["Phone_Number"]}')


def search_contacts(name_search):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        found_status = False
        for row in reader:
            if name_search == row["Name"]:
                found_status = True
                print(f'{row["Name"]} - {row["Phone_Number"]}')
                print("Contact found!")

    if not found_status:
        print("Contact not found!")

menu_option = " "

while True:
    print("1.Add Contacts")
    print("2.View Contacts")
    print("3.Search Contacts")
    print("4.Exit")
    menu_option = input("Enter your option: ")
    if menu_option == "1":
        try:
            Name = input("Enter the name: ")
            Phno = int(input("Enter the phone number: "))
        except ValueError:
            print("Enter the values correctly")
        else:
            add_contacts(Name, Phno)
            
    elif menu_option == "2":
        print("==============View PhoneBook==============")
        view_contacts()
    
    elif menu_option == "3":
        name_search = input("Enter the name to search: ")
        search_contacts(name_search)
    
    elif menu_option == "4":
        print("Goodbye!")
        break
    
        


