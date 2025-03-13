from os import name, system
system_name = name
# Imports based on the system
if system_name == 'nt':
    import msvcrt
else:
    import sys
    import termios
    import readline  # Moves the cursor based on arrow press


alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def alphabet_to_num(char: str):
    # Converts the characters to uppercase and verifies where the letter is
    char = char.upper()
    return alphabet.find(char)


def purge():  # Clears every single line
    if system_name == 'nt':
        system("cls")
    else:
        system("clear")


# Universal line clear (using the OS function is overkill!!!)
def clear_lines(amount=1):
    for _ in range(amount):  # For each line...
        print("\033[A", end="\033[K")  # Move the cursor up and erase everything in this line


# Replaces a specific character by a new string
def replace_index(old: str, index: int, new: str):
    return old[:index] + new + old[index+1:]


# Prompts the user to answer yes or no
def ask_boolean(prompt=""):
    while True:  # Loops until interrupted or answered correctly
        try:                           # Prompts with the desired message
            print(prompt)
            selection = wait_key()
        except KeyboardInterrupt:      # If there is an interrupt, returns None
            return
        finally:                       # Clears a single line, so it won't be wasting space
            clear_lines()

        # Matches the user choice to either y or n, and returns the according boolean value
        match selection.lower():
            case "y":
                return True
            case "n":
                return False
            case _:
                print("(Select only y or n!)", end=" ")


# Prompts the user to choose one from the given list
def ask_from_list(prompt, lst):
    while True:  # Loops until interrupted or answered correctly
        try:                           # Prompts with the desired message
            user_input = input(prompt)
        except KeyboardInterrupt:       # If there is an interrupt, pass it forward, but first break the line
            print()
            raise KeyboardInterrupt
        finally:                       # Clears a single line, so it won't be wasting space
            clear_lines()

        # Gets the selected index from the provided list and returns it
        try:
            selection = lst.index(user_input)
            return selection
        except ValueError:
            print("(Please select a valid option)", end=" ")  # This happens the selected option is not valid


# Used for an easier number conversion
def ask_number(prompt:str="", desired_type=int, minimum=None, maximum=None):
    while True:
        try:                            # Sends the desired request, and then grabs user input
            user_input = input(prompt)
        except KeyboardInterrupt:       # If there is an interrupt, pass it forward, but first break the line
            print()
            raise KeyboardInterrupt
        finally:
            clear_lines()               # Clears a single line, so it won't be wasting space

        # Tries to convert the input to the selected type, and prints an error in case it fails
        try:
            user_input = desired_type(user_input)
        except ValueError:
            if desired_type is int:
                print("(Input a valid integer!)", end=" ")
            else:
                print("(Input a valid number!)", end=" ")
            continue

        # Prevents the user from flooding the terminal (in C this would overflow the buffer)
        if desired_type is not int:
            user_input = round(user_input, 3)

        # In case there is a minimum and the specified number is under the minimum allowed, loop again
        if minimum is not None and user_input < minimum:
            print(f"(Your input needs to be equal or higher than {minimum}!)", end=" ")
            continue

        # In case there is a maximum and the specified number is over the maximum allowed, loop again
        if maximum is not None and user_input > maximum:
            print(f"(Your input needs to be equal or lower than {maximum}!)", end=" ")
            continue

        return user_input  # If no error was caught, returns the input with the specified type


# This was a stack overflow question, and I found this snippet quite useful
def wait_key(prompt=None):
    if prompt:
        print(prompt)
    result = None
    if system_name == 'nt':  # If the system is windows...
        result = msvcrt.getwch()
    else:  # If the system is Unix...
        fd = sys.stdin.fileno()  # Gets the stdin file descriptor

        old_term = termios.tcgetattr(fd)
        new_attr = termios.tcgetattr(fd)

        # Creates a new terminal setting to get only one character
        # Disabling canonical mode makes the terminal get the keys as soon as they are pressed
        # Disabling echo makes your character disappear
        new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO

        # Then the new terminal setting is set
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)

        try:  # Tries to read a single character
            result = sys.stdin.read(1)
        except IOError:  # Except there is an error
            pass
        finally:  # Resets the terminal setting to what it was before
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)
    if result == chr(3):  # In case the char was actually ctrl + c
        raise KeyboardInterrupt
    return result


# Colorizes text output
class Colorize:
    GRAY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PINK = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'
    FAINT = '\033[2m'
    UNDERLINE = '\033[4m'


colors = Colorize()