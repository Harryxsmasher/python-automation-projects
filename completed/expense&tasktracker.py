import json

expense_db = []
task_db = []


class Expense:
    def __init__(self, title, amount, category):
        self.title = title
        self.amount = amount
        self.category = category

    def display_expense(self):
        print(f"Title: {self.title} | Amount: {self.amount} | Category: {self.category}")


class Task:
    def __init__(self, title):
        self.title = title
        self.status = "Pending"

    def display_task(self):
        print(f"Task: {self.title} | Status: {self.status}")
 
    def mark_completed(self):
        self.status = "Completed"


def add_expense():
    title = input("Enter the expense name: ")
    amount = float(input("Enter the expense amount: "))
    category = input("Enter the expense category: ")

    expense = Expense(title, amount, category)
    expense_db.append(expense)
    print("Expense has been added!")
    save_data()


def add_task():
    title = input("Enter the task name: ")

    task = Task(title)
    task_db.append(task)
    print("Task has been added!")
    save_data()


def view_expenses():
    if not expense_db:
        print("No data available!")
        return

    for expense in expense_db:
        expense.display_expense()

def delete_expense():
    search_expense = input("Enter the expense name: ")
    found_status = False

    for expense in expense_db:
        if search_expense.lower() == expense.title.lower():
            expense_db.remove(expense)
            found_status = True
            save_data()
            break
    if not found_status:
        print("Expense is not found!")


def view_tasks():
    if not task_db:
        print("No data available!")
        return

    for task in task_db:
        task.display_task()


def total_expense():
    if not expense_db:
        print("No data available!")
        return

    total = 0
    for expense in expense_db:
        total += expense.amount

    print(f"Total expense is: {total}")
    save_data()


def mark_task_completed():
    searchTask = input("Enter the task name to be marked as completed: ")
    found_status = False

    for task in task_db:
        if searchTask.lower() == task.title.lower():
            task.mark_completed()
            found_status = True
            print("Task has been marked as completed!")
            save_data()
            break

    if not found_status:
        print("No Task has been found!")


def delete_task():
    searchTask = input("Enter the task name to be marked as completed: ")
    found_status = False

    for task in task_db:
        if searchTask.lower() == task.title.lower():
            task_db.remove(task)
            found_status = True
            print("Task has been Deleted")
            break

    if not found_status:
        print("No Task has been found!")

def total_expense_by_category():
    category = input("Enter the category name: ")
    found_status = False
    category_total = 0

    for expense in expense_db:
        if category.lower() == expense.category.lower():
            category_total += expense.amount
            found_status = True

    if found_status:
        print(f"Total expense by category is: {category_total}")
    else:
        print(f"{category} has not been found in the database!")

def save_expense():
    with open("completed/data.txt", "a") as f:
        for expense in expense_db:
            line = f"{expense.title},{expense.amount},{expense.category}\n"
            f.write(line)
    print("Data saved sucessfully.")

def save_expense_json():
    data = []
    for expense in expense_db:
        python_obj = {"Title" : expense.title, "Amount": expense.amount, "Category" : expense.category}
        data.append(python_obj)
        
    with open("completed/data.json", "w") as f:
        json.dump(data, f)
    print("JSON saved successfully")
            
def save_data():
    data = {
        "tasks": [],
        "expenses": []
    }

    # convert tasks → dict
    for task in task_db:
        data["tasks"].append({
            "title": task.title,
            "status": task.status
        })

    # convert expenses → dict
    for expense in expense_db:
        data["expenses"].append({
            "title": expense.title,
            "amount": expense.amount,
            "category": expense.category
        })

    with open("completed/data.json", "w") as f:
        json.dump(data, f)

    print("All data saved!")


def load_data():
    try:
        with open("completed/data.json", "r") as f:
            data = json.load(f)

        task_db.clear()
        expense_db.clear()

        # rebuild tasks
        for t in data["tasks"]:
            task = Task(t["title"])
            task.status = t["status"]
            task_db.append(task)

        # rebuild expenses
        for e in data["expenses"]:
            expense = Expense(
                e["title"],
                float(e["amount"]),
                e["category"]
            )
            expense_db.append(expense)

        print("All data loaded!")

    except FileNotFoundError:
        print("No saved data found")

def load_expense():
    try:    
        with open("completed/data.txt", "r") as f:
            expense_db.clear()

            for line in f:
                title, amount, category = line.strip().split(",")

                amount = float(amount)

                expense = Expense(title, amount, category)
                expense_db.append(expense)
        
        print("Data Loaded Successfully")
    except FileNotFoundError:
        print("No saved data found")

def load_expense_json():
    try:
        with open("completed/data.json", "r") as f:
            data = json.load(f)
        
        expense_db.clear()
        
        for item in data:
            expense = Expense(item["Title"], float(item["Amount"]), item["Category"])
            expense_db.append(expense)

        print("JSON Loaded Successfully")
    
    except FileNotFoundError:
        print("No saved data found")
        

while True:
    print("\nExpense and Task Management System!")
    print("1. Task Menu")
    print("2. Expense Menu")
    print("3. Exit")
    load_data()
    main_menu = input("Enter the option for the main menu: ")

    if main_menu == "1":
        while True:
            print("\nTask Management!")
            print("1. Add Task")
            print("2. View Task")
            print("3. Mark as Completed")
            print("4. Delete Task")
            print("5. Go Back to Main Menu")

            menu = input("Enter the option: ")

            if menu == "1":
                add_task()
            elif menu == "2":
                view_tasks() # FIXED ()
            elif menu == "3":
                mark_task_completed()
            elif menu == "4":
                delete_task()
            elif menu == "5":
                print("Going back to main menu!")
                break

    elif main_menu == "2":
        while True:
            print("\nExpense Management System!")
            print("1. Add Expense")
            print("2. View Expense")
            print("3. Total Expense")
            print("4. Delete Expense")
            print("5. Total Expense by Category")
            print("6. Save to a file")
            print("7. Load from a file")
            print("8. Go back to Main Menu")
            print("9. Exit")
            print("10. Save to a json file")
            print("11. Load from a json file")

            menu = input("Enter the option: ")

            if menu == "1":
                add_expense()
            elif menu == "2":
                view_expenses()
            elif menu == "3":
                total_expense()
            elif menu == "4":
                delete_expense()
            elif menu == "5":
                total_expense_by_category()
            elif menu == "6":
                save_expense()
            elif menu == "7":
                load_expense()
            elif menu == "8":
                print("Going back to main menu!")
                break
            elif menu == "9":
                print("Good bye!")
                exit()
            elif menu == "10":
                save_expense_json()
            elif menu == "11":
                load_expense_json()

    elif main_menu == "3":
        print("Good bye!")
        break 