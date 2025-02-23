# Flight Booking Assistant

##  Overview
The **Flight Booking Assistant** is a chatbot-based application that allows users to search for flights, check availability, and book tickets. It integrates with a database to store flight details and booking information while leveraging AI to handle user queries.

##  Features
- **Flight Search**: Find available flights based on user inputs (departure city, destination, date, airline, and seat class).
- **Flight Booking**: Reserve seats and get a unique `booking_id` upon successful booking.
- **Chatbot Integration**: Uses `LangChain` and `Google Gemini API` to handle user inquiries.
- **Database Management**: Stores flights and bookings using `SQLite`.

<a href = "https://drive.google.com/file/d/1Ym8MXaKGZomNVUBV6_8ihg9YG3i82hBv/view?usp=drive_link">watch demo video</a>

##  Tech Stack
- **Frontend**: `Streamlit`
- **Backend**: `Python`, `LangChain`, `SQLite`
- **AI Model**: `Google Gemini API`


##  Setup & Installation
### 1️ Clone the Repository
```bash
git clone https://github.com/PARTHIBAN-007/Conversational-QA.git
cd Conversational-QA
```
### 2️ Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️ Set Up Google Gemini API
- Obtain an GEMINI API key 
- Add it to your environment variables:
```bash
GEMINI_API_KEY = 'your-api-key'
```
### Run the sql.py for Database Creation - Optional
### 4️ Run the Application
```bash
streamlit run app.py
```

##  Usage
- Search for flights in the sidebar.
- Select a flight and enter booking details.
- Click "Book Now" to reserve a seat.
- Use the chat interface to ask about flight and booking details.

