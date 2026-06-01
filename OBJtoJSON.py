import json

students_obj = []

class Student:
    def __init__(self, name, mark):
        self.name = name
        self.mark = mark

    def print_info(self):
        print(f"Name: {self.name} | Mark: {self.mark}")

def get_student_info():
    timesofinput = int(input("Enter the times of user you want to input: "))
    i = 1
    while i <= timesofinput:
        name = input("Enter the name: ")
        mark = float(input("Enter the mark: "))
        student = Student(name, mark)
        students_obj.append(student)
        i += 1
    
def dump_data():
    data = []
    for student in students_obj:
        python_obj = {"name" : student.name, "mark" : student.mark}

        data.append(python_obj)
    with open ("student.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Data saved")

def load_data():
    with open("student.json", "r") as f:
        student_dict = json.load(f)
        students_obj.clear()

        for student in student_dict:
            student = Student(student['name'], student['mark'])
            students_obj.append(student)

        print("data loaded")

def view_data():
    for student in students_obj:
        student.print_info()

def search_data():
    search_name = input("Enter the name to search: ")
    found_status = False

    for student in students_obj:
        if search_name == student.name:
            found_status = True
            student.print_info()
            break
    if not found_status:
        print("No data is found!")

while True:
    print("1. Add")
    print("2. Dump")
    print("3. Load")
    print("4. view")
    print("5. search")
    print("6. exit")

    menu = input("Enter the option: ")

    if menu == "1":
        get_student_info()
    elif menu == "2":
        dump_data()
    elif menu == "3":
        load_data()
    elif menu == "4":
        view_data()
    elif menu == "5":
        search_data()
    elif menu == "6":
        print("Good bye!")
        break