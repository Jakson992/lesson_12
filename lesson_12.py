from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle


class AddressBook(UserDict):
    file_name = 'data.bin'
    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self, N):
        records = list(self.data.values())
        for i in range(0, len(records), N):
            yield [str(record) for record in records[i:i + N]]

    def save_to_file(self, address_book):
        with open(self.file_name, 'wb') as file:
            pickle.dump(address_book, file)

    def load_from_file(self):
        with open(self.file_name, 'rb') as file:
            data = pickle.load(file)
        self.update(data)

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}: {self.value}"


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name can not be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    def validate(self):
        if not re.match(r"^\+?\d{9,15}$", self.value):
            raise ValueError("Invalid phone number")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.validate()

    def __str__(self):
        return f"{self.__class__.__name__}: {self.value}"


class Birthday(Field):
    DATE_FORMAT = '%d.%m.%Y'

    def __init__(self, value=None):
        self._value = None
        if value:
            self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not re.match(r"\d{2}\.\d{2}\.\d{4}", new_value):
            raise ValueError("Invalid date format. Please use dd.mm.yyyy format.")
        date = datetime.strptime(new_value, self.DATE_FORMAT)
        if date > datetime.now():
            raise ValueError("Invalid date. Birthday date can not be in the future.")
        self._value = date.date()

    def days_to_birthday(self):
        if not self._value:
            return None
        today = datetime.now().date()
        next_birthday = datetime(today.year, self._value.month, self._value.day).date()
        if next_birthday < today:
            next_birthday = datetime(today.year + 1, self._value.month, self._value.day).date()
        return (next_birthday - today).days

    def __str__(self):
        return f"{self.__class__.__name__}: {self.value.strftime(self.DATE_FORMAT)}"


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        if phone:
            self.add_phone(phone)
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        phone_obj.validate()
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return True
        return False

    def __str__(self):
        phones = ", ".join(str(p) for p in self.phones)
        birthday_str = f", {self.birthday}" if self.birthday.value else ""
        return f"{self.name}, {phones}{birthday_str}"


my_contacts = AddressBook()


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact with that name not found."
        except ValueError:
            return "Please enter a valid command."
        except IndexError:
            return "Please enter both name and phone number, separated by a space."

    return wrapper


@input_error
def hello(*args):
    return "How can I help you?"


@input_error
def add(*args):
    _, name, phone = args[0].split()
    record = Record(name)
    record.add_phone(phone)
    my_contacts[name] = record
    return f"Contact {name} with phone {phone} has been added."


@input_error
def change(*args):
    _, name, phone = args[0].split()
    if name in my_contacts:
        record = my_contacts[name]
        record.edit_phone(record.phones[0].value, phone)
        return f"Phone number for contact {name} changed."
    else:
        return f"Contact with name {name} not found."


@input_error
def phone(*args):
    _, name = args[0].split()
    if name in my_contacts:
        return f"Phone number for contact {name} is {my_contacts[name]}."
    else:
        return f"Contact with name {name} is not defined."


@input_error
def show_all(*args):
    if my_contacts:
        contacts_str = ""
        for name, record in my_contacts.items():
            contacts_str += f"{record}\n"
        return contacts_str
    else:
        return "You have no contacts."


@input_error
def exit(*args):
    return "Goodbye!"


COMMANDS = {
    hello: "hello",
    add: "add",
    change: "change",
    phone: "phone",
    show_all: "show all",
    exit: "exit"
}


def command_handler(text):
    for command, keywords in COMMANDS.items():
        if text.lower().startswith(keywords):
            return command, text
    return None, ''


def main():
    while True:
        user_input = input('>>> ')
        command, data = command_handler(user_input)
        if not command:
            print("Unknown command, try again.")
            continue
        print(command(data))
        if command == exit:
            break


if __name__ == '__main__':
    main()
