import sqlite3

# Create & connect to the database
conn = sqlite3.connect("flights.db")
cursor = conn.cursor()

# Create Flights table
cursor.execute('''
CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_name TEXT NOT NULL,
    departure_city TEXT NOT NULL,
    destination_city TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    economy_seats INTEGER NOT NULL,
    business_seats INTEGER NOT NULL,
    first_class_seats INTEGER NOT NULL,
    economy_available INTEGER NOT NULL,
    business_available INTEGER NOT NULL,
    first_class_available INTEGER NOT NULL
)
''')

# Create Bookings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER NOT NULL,
    passenger_name TEXT NOT NULL,
    seat_class TEXT CHECK (seat_class IN ('economy', 'business', 'first_class')),
    num_seats INTEGER NOT NULL,
    booking_status TEXT DEFAULT 'confirmed',
    FOREIGN KEY(flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE
)
''')

# Flight data (converted to lowercase)
flights_data = [
    ("flight a", "new york", "los angeles", "2025-02-25 08:00", "2025-02-25 11:00", 100, 50, 20, 100, 50, 20),
    ("flight b", "chicago", "miami", "2025-02-26 10:00", "2025-02-26 13:00", 120, 40, 30, 120, 40, 30)
]

# Insert into flights table with lowercase values
cursor.executemany('''
INSERT OR IGNORE INTO flights 
(flight_name, departure_city, destination_city, departure_time, arrival_time, economy_seats, business_seats, first_class_seats, economy_available, business_available, first_class_available) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [(f.lower(), d.lower(), dest.lower(), dep_time, arr_time, eco, bus, first, eco_avail, bus_avail, first_avail) for f, d, dest, dep_time, arr_time, eco, bus, first, eco_avail, bus_avail, first_avail in flights_data])

conn.commit()
conn.close()
