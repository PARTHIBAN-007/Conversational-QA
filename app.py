import streamlit as st
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.tools import Tool
from langchain.agents import initialize_agent
import os
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser

# Load API Key
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

def get_db_connection():
    conn = sqlite3.connect("flights.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  
    return conn

def get_flights():
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM Flights").fetchall()

def book_flight(flight_id, passenger_name, seat_class, num_seats):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {seat_class}_available FROM Flights WHERE flight_id = ?", (flight_id,))
    available_seats = cursor.fetchone()[0]

    if available_seats < num_seats:
        conn.close()
        return False, "Not enough seats available!", None  

    cursor.execute(
        "INSERT INTO bookings (flight_id, passenger_name, seat_class, num_seats) VALUES (?, ?, ?, ?)", 
        (flight_id, passenger_name, seat_class, num_seats)
    )

    booking_id = cursor.lastrowid

    cursor.execute(f"UPDATE Flights SET {seat_class}_available = {seat_class}_available - ? WHERE flight_id = ?", 
                   (num_seats, flight_id))

    conn.commit()
    conn.close()
    
    return True, "Booking successful!", booking_id  

class SQLQuery(BaseModel):
    query: str

class FlightBooking:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)
       
        self.sql_query_template = """
        
        Convert the following English question into an SQL query for a SQLite database.

        The database schema:
        **Flights Table**
        - flight_id
        - flight_name
        - departure_city
        - destination_city
        - departure_time
        - arrival_time
        - economy_seats
        - business_seats
        - first_class_seats
        - economy_available
        - business_available
        - first_class_available

        **Bookings Table**
        - booking_id
        - flight_id
        - passenger_name
        - seat_class
        - num_seats
        - booking_status

        Example:
        - *How many flights are available?*
          SELECT COUNT(*) FROM Flights;

        - *Show all bookings for Flight A*
          SELECT * FROM Bookings WHERE flight_id = (SELECT flight_id FROM Flights WHERE flight_name = 'Flight A');

        Convert the user query below into SQL:
        **User Query:** {query}
        Only return the SQL query in JSON format: {{"query": "SQL_QUERY_HERE"}}
        """

        self.parser = PydanticOutputParser(pydantic_object=SQLQuery)
    

    def llm_generate_sql(self, query):
        prompt = self.sql_query_template.format(query=query)
        response = self.llm.invoke(prompt) 
        return response.content 

    def execute_sql(self, query):
        sql_query = self.llm_generate_sql(query)
        parsed_output = self.parser.parse(sql_query)
        sql_query = parsed_output.query
        sql_query = sql_query.lower()

        with get_db_connection() as conn:
            cur = conn.cursor()
            db_response = cur.execute(sql_query).fetchall()
        res = [dict(row) for row in db_response] 
        return self.llm_response(query,res)
        
    def llm_response(self,question,response):
        prompt = f"""You are an AI-powered travel assistant designed to help users find and book flights effortlessly.
        Your role is to engage in a natural conversation, gather necessary details, and retrieve relevant flight options based on user inputs
        user Query : {question}, data from database : {response}
        if the data from database iss null  asks the user to provide more information about the flight and booking details
        don't reveal any information about database or any secrets"""
        llm_response = self.llm.invoke(prompt) 
        print(prompt)
        return llm_response.content

    

st.set_page_config(page_title="Flight Booking Chatbot")
st.title("✈️ Flight Booking Chatbot")
st.caption("Ask me anything about flights and bookings!")

flights = get_flights()
with st.sidebar:
    st.title("Flight Schedule")
    if not flights:
        st.write("No flights available.")
    else:
        for flight in flights:
            st.write(f"**{flight['flight_name']}** - {flight['departure_city']} → {flight['destination_city']}")
            st.write(f"Departure: {flight['departure_time']} | Arrival: {flight['arrival_time']}")
            st.write(f"Seats Available: Economy: {flight['economy_available']}, Business: {flight['business_available']}, First Class: {flight['first_class_available']}")
            st.write("---")

    st.header("Book a Flight")
    flight_dict = {data["flight_name"]: data["flight_id"] for data in flights}
    flight_name = st.selectbox("Flight Name", list(flight_dict.keys()))
    flight_id = flight_dict[flight_name]
    passenger_name = st.text_input("Passenger Name")
    seat_class = st.selectbox("Seat Class", ["economy", "business", "first_class"])
    num_seats = st.number_input("Number of Seats", min_value=1)

    if st.button("Book Now"):
        success, message, booking_id = book_flight(flight_id, passenger_name.lower(), seat_class, num_seats)
        print(booking_id)
        st.success(f"{message}  Your Booking ID is: **{booking_id}**")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask about flights...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    chatbot = FlightBooking()
    response = chatbot.execute_sql(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
