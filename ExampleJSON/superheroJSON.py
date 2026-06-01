import json

superhero_db = []
class Superhero:
    def __init__ (self, name, age, secretIdentity, powers):
        self.name = name
        self.age = age
        self.secretIdentity = secretIdentity
        self.powers = powers

    def display_information(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Secret Identity: {self.secretIdentity}")

        for power in self.powers:
            print(f"Powers: {power}")


def add_super_hero():
    powers = []
    print("Adding a new hero information!")

    name = input("Enter the super hero name: ")
    age = int(input("Enter the age of the hero: "))
    secretIdentity = input("Enter the secret identity of the hero: ")
    power_count = int(input("Enter the count of powers the superhero has: "))
    i = 1
    while i <= power_count:
        power = input("Enter the powers of the super hero: ")
        powers.append(power)
        i += 1
        print(f"{power} has been added to the list")
    superhero = Superhero(name, age, secretIdentity, powers)
    superhero_db.append(superhero)
    print("Superhero information has been added")

def view_super_hero():
    if not superhero_db:
        print("No data is available!")
        return
    for hero in superhero_db:
        hero.display_information()


def load_super_hero_data():
    with open("ExampleJSON/superhero.json", "r") as f:
        json.load(f)

def save_super_hero_information():
    members = []
    for hero in superhero_db:
        python_obj = {"Name" : hero.name, "Age" : hero.age, "secret_identity" : hero.secretIdentity, "Powers" : hero.powers}
        members.append(python_obj)
    with open("ExampleJSON/superhero.json", "w") as f:
        json.dump(python_obj, f)
    print("JSON saved successfully!")


while True:
    print("Super hero database!")
    print("1. ADD Hero")
    print("2. View Hero")
    print("3. exit")
    menu = input("Enter the menu: ")
    if menu == "1":
        add_super_hero()
    elif menu == "2":
        view_super_hero()
    elif menu == "3":
        save_super_hero_information()
    elif menu == "4":
        print("Good bye!")
        break


