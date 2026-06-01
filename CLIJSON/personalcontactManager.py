import json, re

contact_list = []

class Contact:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

    def print_contact_info(self):
        print(f"Contact Name: {self.name} | Phone: {self.phone} | Email: {self.email}")

def dump_data():
    data = []
    for contact in contact_list:
        p_obj = {"name": contact.name, "phone": contact.phone, "email": contact.email}
        data.append(p_obj)
    
    with open("contact.json", "w") as f:
        json.dump(data, f, indent=2)
    print("data saved!")

def load_data():
    with open("contact.json", "r") as f:
        contact_dict = json.load(f)
        contact_list.clear()

        for contact in contact_dict:
            name = contact['name']
            phone = contact['phone']
            email = contact['email']

            contact = Contact(name, phone, email)
            contact_list.append(contact)
        print("data loaded!")

def add_contact():
    name = input("Enter the contact name: ")
    phone = input("Enter the contact number: ")
    email = input("Enter the email address: ")
    found_status = False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    for contact in contact_list:
        if name.lower() == contact.name.lower():
            found_status = True
            print("Contact Already Exists!")
        if not phone.isnumeric():
            print("Phone number is not valid")
        if re.match(pattern, email):
            email_status = True
        else: 
            email_status = False
            print("Invalid Email format")
        
            
    if not found_status and phone.isnumeric() and email_status == True:
        contact = Contact(name, phone, email)
        contact_list.append(contact)
        print("Contact Successfully Added")
    
        
def view_contact():
    if not contact_list:
        print("No data is available in the database!")
        return
    for contact in contact_list:
        contact.print_contact_info()

def search_contact():
    search_name = input("Enter the contact name: ")
    found_status = False

    for contact in contact_list:
        if search_name.lower() == contact.name.lower():
            found_status = True
            contact.print_contact_info()
            break
    if not found_status:
        print("No data is found!")

def delete_contact():
    search_name = input("Enter the contact name: ")
    found_status = False

    for contact in contact_list:
        if search_name.lower() == contact.name.lower():
            found_status = True
            contact_list.remove(contact)
            print("Contact is deleted!")
            break
    if not found_status:
        print("No data is found!")

def update_contact():
    search_name = input("Enter the name to update: ")
    found_status = False
    for contact in contact_list:
        if search_name.lower() == contact.name.lower():
            found_status = True
            while True:
                options = input("Enter the option to select which of the following to be updated: \nEnter the number to follow\n1. name\n2. Phone\n3. Email\n4. Go to main menu!\n")
                if options == "1":
                    name = input("Enter the name to update: ")
                    contact.name = name                   
                    print("Name has been updated!")
                    contact.print_contact_info()
                elif options == "2":
                    phone = int(input("Enter the phone to be updated: "))
                    contact.phone = phone
                    print("Phone has been updated!")
                    contact.print_contact_info()
                elif options == "3": 
                    email = input("Enter the email to be updated: ")
                    contact.email = email                    
                    print("Email has been updated!")
                    contact.print_contact_info()
                elif options == "4":
                    break
            
    if not found_status:
        print("No such name exists in the list!")
    
while True:
    print("Personal Contact Manager")
    print("1. Load Data")
    print("2. Add Data")
    print("3. View Data")
    print("4. Delete Data")
    print("5. Dump Data")
    print("6. Search Contact")
    print("7. Update Contact")
    print("8. Exit")

    menu = input("Enter the menu option: ")
    if menu == "1":
        load_data()
    elif menu == "2":
        add_contact()
    elif menu == "3":
        view_contact()
    elif menu == "4":
        delete_contact()
    elif menu == "5":
        dump_data()
    elif menu == "6":
        search_contact()
    elif menu == "7":
        update_contact()
    elif menu == "8":
        print("good bye!")
        break

