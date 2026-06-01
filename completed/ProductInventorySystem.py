inventorydb = []

class Product:
    def __init__(self, name, price, quantity, category):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.category = category
    
    def displayProducts(self):
        print(f"Product Name: {self.name}")
        print(f"Product Price: {self.price}")
        print(f"Product Quantity: {self.quantity}")
        print(f"Product Category: {self.category}")


def add_product():
    product_name = input("Enter the product: ")
    product_price = int(input("Enter the product price: "))
    product_quantity = int(input("Enter the product quantity: "))
    product_category = input("Enter the product category: ")

    product = Product(product_name, product_price, product_quantity, product_category)
    inventorydb.append(product)
    print("Product is successfully added!")


def view_product():
    if not inventorydb:
        print("No product has been found!")
    
    for product in inventorydb:
        product.displayProducts()

def totalInventoryValue():
    total = 0
    for product in inventorydb:
        value = product.price * product.quantity
        total += value
    print(f"Total value of the Inventory is: {total}")

def search_product():
    searchName = input("Enter the product name: ")
    foundStatus = False
    for product in inventorydb:
        if searchName.lower() == product.name.lower():
            foundStatus = True
            product.displayProducts()
            break
    if not foundStatus:
        print("Not found")

def totalvaluebycategory():
    categoryName = input("Enter the category name: ")
    foundStatus = False
    categoryValue = 0
    for product in inventorydb:
        if categoryName.lower() == product.category.lower():
            foundStatus = True
            value = product.price * product.quantity
            categoryValue += value
    print(f"Total by category is: {categoryValue}")

    if not foundStatus:
        print("Category is not found")


while True:
    print("Inventory Management System!")
    print("1. Add View")    
    print("2. View Products")    
    print("3. Total Inventory Value")    
    print("4. Search Product")    
    print("5. Total by Category")    
    print("6. Exit")
    menu = input("Enter your option: ")
    if menu == "1":
        print("Add products")
        add_product()
        continue
    elif menu == "2":
        print("View products")
        view_product()
        continue
    elif menu == "3":
        print("Total inventory Value")
        totalInventoryValue()
        continue
    elif menu == "4":
        print("Search Product")
        search_product()
        continue
    elif menu == "5":
        print("Total by Category")
        totalvaluebycategory()
        continue
    elif menu == "6":
        print("Good bye!")
        break    