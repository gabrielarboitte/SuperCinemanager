#!/bin/python3
from db import *  # Interaction with the CRUD
from os import getcwd, listdir, makedirs  # Interaction with the file system
from art import *  # Menus and other visible content
from utils import *  # Useful functions for a variety of circumstances

# Saves the current dir_path globally
dir_path = getcwd()
databases_path = dir_path + "/databases"

# Sets the global gender variable
genders = ["male", "female", "other", "unspecified"]


# Defines the manager class
class Manager:
    # Initializes variables with empty values
    def __init__(self):
        self.db = None
        self.ticket_price = None
        self.rows = None
        self.columns = None
    
    # Takes the row and column index, and converts it to the seat id
    # Returns KeyError if the seat id is out of the room limits
    def calculate_id(self, row: int, column: int):
        # The provided row and column must be within the limits
        if not 0 <= row < self.rows:
            raise KeyError(f"The row must be within A-{alphabet[self.rows - 1]}")
        if not 0 <= column < self.columns:
            raise KeyError(f"The column must be within 1-{self.columns}")

        # Gets the id based on the row + column calculations
        return row * self.columns + column
    
    # Prints the current seat map based on the available information
    def print_map(self):
        occupied_seats = [seat[0] for seat in self.db.get_occupied()]
        for row in range(self.rows):
            print("  ", end="")
            print("╔════╗ " * self.columns)  # customization done
            print(alphabet[row], end=" ")
            for i in range(self.columns):
                print(f"║ {'웃' if row * self.columns + i in occupied_seats else '  '} ║", end=" ")  # customization done
            print()
            print("  ", end="")
            print("╚════╝ " * self.columns)  # customization done
        # Prints the column numbers
        print("  ", end="")
        for column in range(self.columns):
            print(f"  {column + 1:0>2}  ", end=" ")
        print()
    
    # Clears the amount of lines printed by the map
    def clear_map(self):
        # Clears the column numbers
        clear_lines()
        # Clears the map
        clear_lines(self.rows * 3)
    
    # Validates if a range of columns is free in given row
    # Returns True if every seat is free, False if at least one is occupied
    # Raises KeyError if the starting or final seat doesn't exist
    def validate_row_range(self, row: int, column: int, column_range: int = 1):
        # The provided row and column must be within the limits
        if 0 > column or column + column_range > self.columns:
            raise KeyError('The row must not exceed the border')
        
        # The id of the first and last seats
        starting_id = self.calculate_id(row, column)
        ending_id = starting_id + column_range
        
        # Validates if any of the selected seats is occupied
        for seat_id in range(starting_id, ending_id):
            # If the value is not None, returns False
            # Meaning that at least one seat is not free 
            if self.db.get_seat(seat_id):
                return False
        return True
    
    # This function should add a new seat to the database
    def book_seat(self, row: int, column: int, age: int, gender: int):
        seat_id = self.calculate_id(row, column)

        # If the seat is free, saves the new occupant
        if self.db.get_seat(seat_id) is None:
            self.db.save_seat(seat_id, age, gender)
    
    # This function should remove a seat from the database
    def unbook_seat(self, row: int, column: int):
        seat_id = self.calculate_id(row, column)

        # If the seat is occupied, clears it
        if self.db.get_seat(seat_id):
            self.db.remove_seat(seat_id)
            
    
    # Retrieves the specified seat
    def get_seat(self, row: int, column: int):
        seat_id = self.calculate_id(row, column)
        return self.db.get_seat(seat_id)

    # Retrieves every seat from the database, and returns related information
    # Tuple with (row_key, column_n, age, gender, ticket_price)
    def seat_list(self):
        seats = []
        for seat_id, age, gender in self.db.get_occupied():
            row = seat_id // self.columns
            column = seat_id % self.columns

            row_key = alphabet[row]
            column_n = column + 1
            if 17 < age < 60:
                ticket_price = self.ticket_price
            else:
                ticket_price = self.ticket_price / 2

            seats.append((row_key, column_n, age, gender, ticket_price))
        return seats

    
    # Simple database update, discards the previous if it exists
    def set_database(self, db: Database):
        # Saves the database
        self.db = db
        # Verifies if the database is already initialized
        db_options = self.db.get_options()
        if db_options is not None:
            # Sets the database variables in the object
            self.ticket_price, self.rows, self.columns = db_options
            return True
    
    # Updates the object variables and saves them to the database options
    def set_options(self, ticket_price: float, rows: int, columns: int):
        self.ticket_price = ticket_price
        self.rows = rows
        self.columns = columns
        self.db.save_options(ticket_price, rows, columns)


# Converts a key/number (e.g. A1) into the row and column indexes
def seat_parser(position):
    try:
        row = alphabet_to_num(position[0])
        column = int(position[1:]) - 1
    except IndexError:
        raise ValueError
    return row, column

### FUNCTIONS FROM THE MAIN MENU ###

# Function 1, used to initialize the provided manager
def initialize_manager(manager):
    # Tracks how many lines to clear
    printed = 4
    # In case the database name is not specified in the arguments 
    if len(argv) == 1:
        try:
            # Retrieves the files inside the databse folder
            db_list = listdir(databases_path)
        except FileNotFoundError:
            # Create the directory if it does not exist
            makedirs(databases_path)
            db_list = []
        # In case the file list is not empty...
        if db_list:
            printed += 2
            print('Available databases found:')
            for database in db_list:
                printed += 1
                print("-", database.replace('.sqlite', ""))  # Hides ext when it is default
            print()
        db_name = input('Specify the name of the database to use (default: cine_room): ')
        clear_lines()
    else:
        db_name = argv[1] # Argv 0 is the name of the file starting the function
   
    # Prints the database name
    print("Selected database:", db_name if db_name.strip() else "cine_room")

    # Sets the new database of the manager
    is_initialized = manager.set_database(Database(db_name))
    
    # If the database is not yet initialized, sets its options based on input
    if not is_initialized:
        ticket_price = ask_number("Please, specify the ticket price: ", float, 0.01)
        rows = ask_number("Please, specify the amount of rows in the movie theater: ", int, 1, 26)
        columns = ask_number("Please, specify the amount of columns in the movie theater: ", int, 1, 18)

        manager.set_options(ticket_price, rows, columns)
    
    # Prints the current database options
    print(f"This {manager.rows}x{manager.columns} room has a ticket price of {manager.ticket_price:.2f}$")
    print()
    print("Press any key to continue...")
    wait_key()

    clear_lines(printed)


# Function 2.1, used to verify the seat status
def verify_seat(manager):
    manager.print_map()
    print()

    while True:
        # First, input the seat
        position = input(f"Please, select your seat (A1-{alphabet[manager.rows - 1]}{manager.columns}): ")
        clear_lines()
        try:
            # Tries to parse its index
            row, column = seat_parser(position)
            # Validates availability
            result = manager.get_seat(row, column)
            print(f"Validating seat {position.upper()}...")
            # The loop only stops when a result is found or keyboard interrupt
            break
        # In case the position is malformed...
        except ValueError:
            print("(Please, choose a valid position e.g., A1)", end=" ")
        # In case the row is not valid...
        except KeyError as e:
            # Prints the error message
            print("(" + e.args[0] + ")", end=" ")
    

    try:
        # Retrieves age and gender variables from the result
        age, gender = result
        # Prints the values to the user
        print("Its occupant's age is", age, "and their gender is", genders[gender])  # I DEMAND CUSTOMIZATION
    # If the result is None, TypeError is raised when trying to split it into two variables
    except TypeError:
        print("This seat is empty")
    
    print()
    wait_key("Press any key to continue...")
    clear_lines(5)
    manager.clear_map()



# Function 2.2, used to make new reservations
def book_seats(manager):
    manager.print_map()
    print()

    while True:
        # First, input the seat
        position = input(f"Please, select the starting seat (A1-{alphabet[manager.rows - 1]}{manager.columns}): ")
        clear_lines()
        try:
            # Tries to parse its index
            row, column = seat_parser(position)
            # Validates availability
            print(f"validating seat {position.upper()}...")
            if manager.get_seat(row, column):
                wait_key("The selected seat is already occupied! (press to continue)")
                clear_lines(2)
                continue
            print("Seat is available!")
            # Asks for how many seats to add
            column_range = ask_number("Specify how many seats you want to book: ", int, 1)
            # Clears seat validation log
            clear_lines(2)
            is_free = manager.validate_row_range(row, column, column_range)
            # The loop only stops when no error occurs or it is interrupted
            break
        # In case the position is malformed...
        except ValueError:
            print("(Please, choose a valid position e.g., A1)", end=" ")
        # In case the row is not valid...
        except KeyError as e:
            # Prints the error message
            print(e.args[0], end=" ")
    
    # If manager.validate_row_range didn't find any occupied seat
    if is_free:
        print("Booking new seats...")
        # Initializing variables
        i = 0
        gender_initials = [gender[0] for gender in genders]
        # For every free seat in the row...
        while i < column_range:
            print()
            # Keep track of the current seat
            print(f"Seat {alphabet[row]}{column + i + 1}")
            age = ask_number("Please, enter the age: ", int, 1)  # No age maximum (imortal beings are welcomed)
            # This zip function just iterates tuples until one of them ends, it is not like zipping folders
            print("Choose one of the genders from:",
                   ', '.join([f"{g} ({gender})" for g, gender in zip(gender_initials, genders)]))
            gender = ask_from_list("Your choice: ", gender_initials)
            clear_lines(3)
            # The row remains the same, the range starts at 0
            print(f"{alphabet[row]}{column + i + 1} - {age} years old, {genders[gender]}")
            manager.book_seat(row, column + i, age, gender)
            i += 1
    else:
        print("There is at least one booked seat in the list")
    
    print()
    wait_key("Press any key to continue...")
    clear_lines(4)
    if is_free:
        clear_lines(column_range)
    manager.clear_map()


# Function 2.3, used to remove reservations
def unbook_seats(manager):
    manager.print_map()
    print()

    while True:
        # First, input the seat
        position = input(f"Please, select the starting seat (A1-{alphabet[manager.rows - 1]}{manager.columns}): ")
        clear_lines()
        try:
            # Tries to parse its index
            row, column = seat_parser(position)
            # Validates starting seat
            manager.get_seat(row, column)
            # Asks for how many seats to remove and validates the row
            column_range = ask_number("Specify how many seats you want to unbook: ", int, 1)
            is_free = manager.validate_row_range(row, column, column_range)
            # The loop stops only when no error occurs or it is interrupted
            break
        # In case the position is malformed...
        except ValueError:
            print("(Please, choose a valid position e.g., A1)", end=" ")
        # In case the row is not valid...
        except KeyError as e:
            # Prints the error message
            print(e.args[0], end=" ")
    
    occupied_seats = []
    # If every seat is free...
    if is_free:
        print("There are no seats to unbook!")
    # Else, there are seats to unbook
    else:
        print("Occupied seats:")
        for i in range(column_range):
            try:
                # Saves only if the seat exist, and prints its information
                age, gender = manager.get_seat(row, column + i)
                occupied_seats.append(column + i)
            except TypeError:
                continue
            # The row remains the same, the range starts at 0
            print(f"{alphabet[row]}{column + i + 1} - {age} years old, {genders[gender]}")
        # Gives a last chance ot give up
        print()
        if ask_boolean("Are you sure that you want to clear these seats? [y/n]"):
            # Using the previously saved list
            for seat_column in occupied_seats:
                manager.unbook_seat(row, seat_column)
            print("The seats where succesfully unbooked")
        else:
            print("No seat was unbooked")

    print()
    wait_key("Press any key to continue...")
    clear_lines(4 + len(occupied_seats) + (not is_free) * 2)
    manager.clear_map()


# Function 3, used to delete every seat in the room
def room_clear(manager):
    # Verifies the amount of booked seats
    occupied_seats = len(manager.seat_list())
    # In case it is 0...
    if not occupied_seats:
        print("This database is already empty!")
        print()
        wait_key("Press any key to continue...")
        clear_lines(3)
        return
    if occupied_seats > 10:
        print("Warning: there are many seats saved, be sure you want to delete everything")
        print()
    print("Are you sure you want do delete every data in this room? [y/n]")
    print("(This action is unreversible, you will remove", occupied_seats, "seats)")
    answer = ask_boolean()
    print()
    if answer:
        manager.db.drop_seats()
        print("This room was completely reset!")
    else:
        print("You canceled the room reset")
    print()
    wait_key("Press any key to continue...")
    clear_lines(6 + (occupied_seats > 10) * 2)


# Function 4, the report generator
def generate_reports(manager):
    # Returned when no seat is occupied
    reservations = manager.seat_list()
    boys = 0
    girls = 0
    other = 0
    unspecified = 0
    minors = []
    adults = []
    elders = []
    if not reservations:
        print("This room is still empty!")
        print()
        wait_key("Press any key to continue...")
        clear_lines(3)
        return
    print("╔══════════════════╗")
    print("║ Reservation list ║")
    print("╚══════════════════╝")
    for row, column, age, gender, ticket_price in reservations:
        # First prints the row
        print(row + str(column), '-', age, 'years old,', genders[gender] + ',', f"${ticket_price:.2f}")
        # Then does other statistical validation
        match gender:
            case 0:
                boys += 1
            case 1:
                girls += 1
            case 2:
                other += 1
            case 3:
                unspecified += 1
        if age < 18:
            minors.append(ticket_price)
        elif age < 60:
            adults.append(ticket_price)
        else:
            elders.append(ticket_price)
    print()
    wait_key("Press any key to continue...")
    # Clears the first report
    clear_lines(5 + len(reservations))
    # The total amount of seats
    room_size = manager.rows * manager.columns
    reserved_seats = len(reservations)
    # Prints the room size and occupation
    print("""╔════════════════════╗ 
║  this room has...  ║
╠════════════════════╣""")
    print(f"║ {manager.rows} rows".ljust(21) + "║")
    print(f"║ {manager.columns} columns".ljust(21) + "║")
    print(f"║ {room_size} seats".ljust(21) + "║")
    print(f"║ {reserved_seats} reserved seats".ljust(21) + "║")
    print(f"║ {room_size - reserved_seats} free seats".ljust(21) + "║")
    print("╚════════════════════╝")
    print("")
    wait_key("Press any key to continue...")
    # Clears the second report
    clear_lines(11)

    # Prints information about the seat occupants
    print("╔══════════════╗ ")
    print("║ Demographics ║")
    print("╚══════════════╝")
    print()

    # Boys and girls amount
    bng = boys + girls
    if bng:
        print("Boys x girls percentage")
        girls_percent = girls / bng * 100
        boys_percent = boys / bng * 100
        print(colors.PINK, f"{girls} girls ({girls_percent:.2f}%) [", "═" * round(girls_percent / 10), 
              colors.BLUE, "═" * round(boys_percent / 10), f"] {boys} boys ({boys_percent:.2f}%)", colors.END , sep="")

    # Others and unspecified amount
    onu = other + unspecified
    if onu:
        print("Others x unspecified percentage")
        others_percent = other / onu * 100
        unspecified_percent = unspecified / onu * 100
        print(colors.YELLOW, f"{other} other ({others_percent:.2f}%) [", "═" * round(others_percent / 10),
              colors.GREEN, "═" * round(unspecified_percent / 10), f"] {unspecified} unspecified ({unspecified_percent:.2f}%)", colors.END , sep="")
    
    print()

    print("╔═════════════╗")
    display_loading_bar(reserved_seats, minors, "Minors ")
    display_loading_bar(reserved_seats, adults, "Adults ")
    display_loading_bar(reserved_seats, elders, "Elders ")
    print("╠═════════════╣")
    display_loading_bar(reserved_seats, [seat[4] for seat in reservations], "Total  ")
    print("╚═════════════╝")
    print()

    wait_key("Press any key to continue...")
    # Clears the third report
    clear_lines(14 + (bng > 0) * 2 + (onu > 0) * 2)


# Helper function to display the age bars in generate reports
def display_loading_bar(total, age, name):
    age_revenue = sum(age)
    try:
        age_percent = len(age) / total * 100
        age_bar = round(age_percent / 10) * '═'
    except ZeroDivisionError:
        age_percent = 0.
        age_bar = ''
    
    formatted_percent = f"{age_percent:.2f}%".rjust(7)
    print(f"║ {name}: {len(age):0>2} ║ {formatted_percent} |", 
          age_bar + (10 - len(age_bar)) * ' ', "|", f"${age_revenue:.2f}")


### FUNCTIONS FROM THE MAIN MENU ###


# Creates a loop inside the submenu
def submenu(manager):
    while True:
        print(submenu_art)
        try:
            # No need for enters
            func = int(wait_key("Choose function to start: "))
        # In case the user interrupts, exits the submenu
        except KeyboardInterrupt:
            func = 4
        # If the selection is not a valid number, ignore
        except ValueError:
            continue
        finally:
            # Clears the submenu
            clear_lines(12)
        match func:
            case 1:
                # Prints the age and gender of the occupant of given seat
                verify_seat(manager)
            case 2:
                # Saves new data to the room
                book_seats(manager)
            case 3:
                # Removes a seat's data from the room
                unbook_seats(manager)
            case 4:
                # Breaks the submenu loop and return to the main menu
                break


def menu(manager):
    # Prints the menu
    print(menu_art)
    try:
        # No need for enters
        func = int(wait_key("Choose function to start: "))
    # In case the user interrupts, exits the program
    except KeyboardInterrupt:
        func = 5
    # If the selection is not a valid number, ignore
    except ValueError:
        return
    finally:
        # Clears the menu
        clear_lines(11)
    match func:
        case 1:
            initialize_manager(manager)
        case 2:
            while True:
                try:
                    submenu(manager)
                    break
                except KeyboardInterrupt:
                    print()
                    print("Function aborted!")
                    continue
        case 3:
            room_clear(manager)
        case 4:
            generate_reports(manager)
        case 5:
            clear_lines()
            exit()


if __name__ == '__main__':
    # Used to parse the command line arguments
    from sys import argv

    # Initializes a new object for the manager variable
    first_manager = Manager()

    # Sets the default variables based on user input
    try:
        initialize_manager(first_manager)
    # Basic detection of keyboard interruption
    except KeyboardInterrupt:
        print()
        print('Aborted, finishing early')
        exit()
    
    while True:
        try:
            menu(first_manager)
        except KeyboardInterrupt:
            print()
            print("Function aborted")
