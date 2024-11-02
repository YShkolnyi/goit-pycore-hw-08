from collections import UserDict
from datetime import datetime, date, timedelta
from colorama import Fore
import pickle

def log_info(message):
    return f"{Fore.GREEN}{message}{Fore.RESET}"

def log_warning(message):
    return f"{Fore.YELLOW}{message}{Fore.RESET}"

def log_error(message):
    return f"{Fore.RED}{message}{Fore.RESET}"

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError
        super().__init__(value) 

class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError
        super().__init__(value) 

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            self.value = value
        except ValueError:
            raise ValueError(log_error("Invalid date format. Use DD.MM.YYYY"))
    
    def get_date(self):
        return datetime.strptime(self.value, '%d.%m.%Y').date()

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self,phone):
        self.phones.append(Phone(phone))

    def add_birthday(self,birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self,phone):
        for i in self.phones: 
            if i.value == phone:
                self.phones.remove(i)
    
    def edit_phone(self,old_phone,new_phone): 
        for i in self.phones: 
            if i.value == old_phone: 
                index = self.phones.index(i)
                self.phones[index] = Phone (new_phone)
                break 
        else: 
            raise ValueError (log_warning(f"This phone {old_phone} doesn't exist in address book."))

    def find_phone(self,phone):
        for i in self.phones:
            if i.value == phone: 
                return i 
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday if self.birthday else ''}"

class AddressBook(UserDict):
    def add_record(self,record):
        self.data[record.name.value]=record

    def find(self,name):
        return self.data.get(name)
    
    def delete(self,name):
        del self.data[name]

    def __str__(self):
        records = "\n".join(str(record) for record in self.data.values())
        return f"{records}"
    
    def get_upcoming_birthdays(self, days=7):

        birthdays_list = []
        today = date.today()

        for name in self.data:
            if self.data[name].birthday != None:
                birthday = self.data[name].birthday.get_date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year+1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() == 5:
                        wishing_day = birthday_this_year + timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        wishing_day = birthday_this_year + timedelta(days=1)
                    else:
                        wishing_day = birthday_this_year

                    birthdays_list.append({'name':name,'wishing day':wishing_day})
        return birthdays_list
 
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return f"{message}\n{log_warning('Please give me the correct data input.')}"
        except IndexError:
            return log_error("Give me name and right phone please.")
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    global message
    message = log_error("Contact hasn't been added.")
    name, *phones = args
    record = book.find(name)
    if record is None:
        if len(phones) != 0:
            for phone in phones:
                test = Phone(phone)
        record = Record(name)
        book.add_record(record)
        message = log_info("Contact added.")
    for phone in phones:
        if not record.find_phone(phone):
            record.add_phone(phone)
            message = log_info("Contact updated.")
        else:
            message = f"{message}\n{log_warning('This contact already exist.')}"
    return message

@input_error
def change_contact(args, book: AddressBook):
    global message
    message = log_error("Contact hasn't been updated.")
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if old_phone and new_phone and not record.find_phone(new_phone):
        record.edit_phone(old_phone, new_phone)
        message = log_info('Contact updated.')
    else:
        message = message + f"\n{log_warning('New phone already exist in contact.')}"
    return message

@input_error
def show_phone(args, book: AddressBook):
    message = log_error("Contact hasn't been found.")
    name, *_ = args
    record = book.find(name)
    if record:
        message = f'Search result for "{name}": {"; ".join(p.value for p in record.phones)}'
    return message

@input_error
def add_birthday(args, book: AddressBook):
    global message
    message = log_error("Contact hasn't been updated.")
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        message = log_info("Contact updated")
    return message

@input_error
def show_birthday(args, book: AddressBook):
    global message
    message = log_error('No input data')
    name, *_ = args
    record = book.find(name)
    if record:
        birthday = record.birthday
        if birthday:
            birthday = birthday.get_date().strftime('%d.%m.%Y')
            return f"{name}'s birthday is on {birthday}."
        else:
            message = log_error("Contact no birthdays entered.")
            return message
    else:
        message = log_error("Contact hasn't been found.")
        return message

def show_all(book: AddressBook):
    message = log_warning('AddressBook is epty yet.')
    if book:
        return book
    else:
        return message
    
def birthdays(args, book: AddressBook):
    message = log_warning('The address book does not contain birthdays.')
    days = 7
    if args:
        days, *_ = args
    if book:
        birthdays = book.get_upcoming_birthdays(int(days))
        message = f'You shoud wish this person in next {days} days:\n'
        if birthdays:
            for contact in birthdays:
                submessage = f'You should wish {contact.get("name")}  on {contact.get("wishing day").strftime("%d.%m.%Y")}.\n'
                message = message + submessage
        else:
            message = log_warning(f'Nobody has a birthday in the next {days} days.')
        message = message.rstrip('\n')
    return message

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")
            
if __name__ == "__main__":
    main()
