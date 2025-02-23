import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

system_message = SystemMessage(
    content="You are an AI assistant that helps users with flight-related queries. "
            "You can check flight status and provide conversational responses."
)

def flight_status(prompt):
    return f"Flight Status: {prompt}"

def conversation(prompt):
    return f"AI Chat Response: {prompt}"

tools = [
    Tool(name="Flight Status", description="Check the status of a flight", func=flight_status),
    Tool(name="Conversational Chat", description="Communicate with users", func=conversation)
]

llm = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

memory = ConversationBufferMemory(memory_key="chat_history")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    memory=memory,
    verbose=True
)

user_prompt = PromptTemplate.from_template("User Query: {query}")

st.set_page_config(page_title="Flight Booking Chatbot")
st.title("✈️ Flight Booking Chatbot")
st.caption("Ask me your query about flight booking details")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask me about flights..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    response = agent.run(user_prompt.format(query=user_input))

    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with st.chat_message("assistant"):
        st.markdown(response)
