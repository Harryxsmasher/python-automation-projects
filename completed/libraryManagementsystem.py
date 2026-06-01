booksdb = []

class Book:
    def __init__(self, title, author, copies):
        self.title = title
        self.author = author
        self.copies = copies   

    def display_book(self):
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Copies: {self.copies}")

def add_books():
    print("Add books")
    title = input("Enter the title of the book: ")
    author = input("Enter the author of the book: ")
    copies = int(input("Enter the copies of the book: "))

    book = Book(title, author, copies)
    booksdb.append(book)

def view_books():
    if not booksdb:
        print("Books are not found")
        return
    for book in booksdb:
        book.display_book()     

def search_books():
    booktosearch = input("Enter the name of the book: ")
    found_status = False
    for book in booksdb:
        if booktosearch.lower() == book.title.lower():
            found_status = True
            book.display_book()
    if not found_status:
        print("Books are not found")
                
def borrow_books():
    booktosearch = input("Enter the name of the book: ")
    found_status = False
    for book in booksdb:
        if booktosearch.lower() == book.title.lower() and book.copies > 0:
            found_status = True
            book.copies -= 1
            book.display_book()
            print("Book is borrowed")
        elif booktosearch.lower() == book.title.lower() and book.copies <= 0:
            found_status = True
            print("Book is found but no copies are available")
            break
    if not found_status:
        print("Book is not found")

while True:
    print("Library Managament System")
    print("1. Add Book")
    print("2. View Book")
    print("3. Search Book")
    print("4. Borrow Book")
    print("5. Exit")

    menu = input("Enter your option: ")
    if menu == "1":
        add_books()
        continue
    elif menu == "2":
        view_books()
        continue
    elif menu == "3":
        search_books()
        continue
    elif menu == "4":
        borrow_books()
        continue
    elif menu == "5":
        print("Good bye!")
        break
        