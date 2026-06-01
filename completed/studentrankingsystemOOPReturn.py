students_db = []

class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def displayStudent(self):
        print(f"Student name: {self.name}")
        print(f"Average is: {self.average()}")
        
    
    def average(self):
        total = 0
        for mark in self.marks:
            print(f"Marks are: {mark}")
            total += mark
        print(f"Total is: {total}")
        average = total / len(self.marks)
        return average
        

def add_student():
    name = input("Enter the student name: ")
    no_of_subject = int(input("Enter the number of subjects: "))
    marks = []
    i = 1
    while i <= no_of_subject:
        mark = int(input("Enter the mark: "))
        marks.append(mark)
        i += 1
    student = Student(name, marks)
    students_db.append(student)

def view_student():
    if not students_db:
        print("Students are found!")
    
    for student in students_db:
        student.displayStudent()


def search_student():
    searchStudent = input("Enter the student name to search: ")
    foundStatus = False
    for student in students_db:
        if searchStudent.lower() == student.name.lower():
            foundStatus = True
            student.displayStudent()
            break
    if not foundStatus:
        print("Searched student is not in the database!")

def find_topper():
    max_average = 0
    top_student = None
    for student in students_db:
        avg = student.average()
        
        if avg > max_average:
            max_average = avg
            top_student = student.name
    print(f"Top Scorer: {top_student} with average {max_average}")
        


while True:
    print("Student Tracker Management!")
    print("1. Add Student")
    print("2. View Student")
    print("3. Search Student")
    print("4. Find Topper")
    print("5. Exit")

    menu = input("Enter the option: ")
    if menu == "1":
        print("Add Student")
        add_student()
        continue
    elif menu == "2":
        print("View Student")
        view_student()
        continue
    elif menu == "3":
        print("Search Student")
        search_student()
        continue
    elif menu == "4":
        print("Find Topper")
        find_topper()
        continue
    elif menu == "5":
        print("Good bye!")
        break