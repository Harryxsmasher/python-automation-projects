# Polymorphism example

class FileReader:
    def __init__(self, filename):
        self.filename = filename
    
    def read(self):
        print(f"Reading generic file: {self.filename}")


class CSVReader(FileReader):
    def __init__(self, filename):
        super().__init__ (filename)

    def read(self):
        print(f"Reading CSV file: {self.filename}")


class JSONReader(FileReader):
    def __init__(self, filename):
        super().__init__(filename)

    def read(self):
        print(f"Reading JSON file: {self.filename}")


class ExcelReader(FileReader):
    def __init__ (self, filename):
        super(). __init__(filename)
    
    def read(self):
        print(f"Reading Excel file: {self.filename}")



csv = CSVReader("Employee.csv")
json = JSONReader("Employee.json")
excel = ExcelReader("Employee.xlsx")



csv.read()
json.read()
excel.read()
# reader.read()

print(isinstance(csv, CSVReader))
print(isinstance(json, JSONReader))
print(isinstance(excel, ExcelReader))




