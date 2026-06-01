my_directory = []
user_input = ""
while True:
    print("Dictonary tasks 2")
    print("1. Add User data")
    print("2. View User data")
    print("3. Classify Users")
    print("4. Search Users")
    print("5. Exit program")
    user_input = input("Enter options to begin!!")
    
    if user_input == "1":
        name = input("Enter your name: ")
        age = int(input("Enter your age: "))
        user = {"name" : name, "age": age}
        my_directory.append(user)
        continue
    elif user_input == "2":
        for user in my_directory:
            print(user)
        continue
    elif user_input == "3":
        for user in my_directory:
            name = user["name"]
            age = user["age"]

            if age < 18:
                status = "Minor"
                print(f"name: {name}, Age: {age}, status: {status}")
            elif age <= 60:
                status = "Adult"
                print(f"name: {name}, Age: {age}, status: {status}")
            else:
                status = "Senior"
                print(f"name: {name}, Age: {age}, status: {status}")
        continue
    elif user_input == "4":
        search_name = input("Enter a name to find: ")
        found_status = False
        for user in my_directory:
            if search_name == user["name"]:
                found_status = True
                if found_status == True:
                    print("User found!")
                    break
                else:
                    print("Not Found")
                    continue
                 
        continue
    elif user_input == "5":
        print("Good bye!")
        exit()
    break


    







