import sqlite3


class Database:
    def __init__(self, database_name):
        # Prevents exploits
        database_name = database_name.replace("/", "")
        # Prevents bugs
        database_name = database_name.strip()
        database_name = database_name.replace(" ", "_")

        # If no extension was specified
        if '.' not in database_name:
            self.name = database_name
            self.ext = "sqlite"
        else:
            self.name, self.ext = database_name.split('.', 1)
            # In case the ext is not in the whitelist...
            if self.ext not in {'sqlite', 'db'}:
                self.ext = "sqlite"
        
        if self.name == '':
            self.name = 'cine_room'
        
        self.conn = None
        self.cursor = None
        self._initialize()


    def _initialize(self):
        # Makes the connection
        self.conn = sqlite3.connect(f'databases/{self.name}.{self.ext}')
        self.cursor = self.conn.cursor()

        # Creates the options table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS options 
                            (ticket_price REAL, rows INTEGER, columns INTEGER)''')

        # Creates the seat table if it doesn't exist
        # Genders are:
        # 0 - male
        # 1 - female
        # 2 - other
        # 3 - unspecified
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS seats 
                            (seat_id INTEGER PRIMARY KEY, age INTEGER, gender INTEGER)''')
        self.conn.commit()


    # Saves a new seat occupant with the specified ID, age, and gender.
    def save_seat(self, seat_id: int, age: int, gender: int):        
        # Saves the new seat specification
        self.cursor.execute('''INSERT INTO seats (seat_id, age, gender)
                            VALUES (?,?,?)''', (seat_id, age, gender))
        self.conn.commit()
    

    # Removes the occupant with the specified ID
    def remove_seat(self, seat_id: int):        
        # Removes the seat based on its ID
        self.cursor.execute('DELETE FROM seats WHERE seat_id = ?', (seat_id,))
        self.conn.commit()
    

    # Deletes every saved seat
    def drop_seats(self):        
        # Clears the seat table
        self.cursor.execute('DELETE FROM seats')
        self.conn.commit()
    
    
    # Retrieves a list of every occupied seat
    def get_occupied(self):
        self.cursor.execute("SELECT seat_id, age, gender FROM seats")
        result = self.cursor.fetchall()
        return result


    # Fetches the seat situation
    def get_seat(self, seat_id: int):
        # Returns a tuple containing the seat occupant's age and gender,
        # Or None if the seat is empty.
        self.cursor.execute("SELECT age, gender FROM seats WHERE seat_id = ?", (seat_id,))
        result = self.cursor.fetchone()
        return result


    #Saves the provided options to the database.
    def save_options(self, ticket_price: float, rows: int, columns: int):
        # Overrides the options if they already exist
        self.cursor.execute('''REPLACE INTO options (ticket_price, rows, columns)
                            VALUES (?,?,?)''', (ticket_price, rows, columns))
        self.conn.commit()

    
    # Fetches the current options from the database
    def get_options(self):
        # Returns a tuple containing ticket price, number of lines, and number of columns,
        # Or None if no options are set.
        self.cursor.execute("SELECT * FROM options")
        result = self.cursor.fetchone()
        return result
