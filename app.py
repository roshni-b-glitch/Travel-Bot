import streamlit as st
import requests
import json

# --------------------------------------------------
# Config
# --------------------------------------------------
API_URL = "http://127.0.0.1:8000/travel-plan"

st.set_page_config(page_title="Travel Chatbot", page_icon="✈️", layout="wide")

# --------------------------------------------------
# Session State for Chat
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("Travel Assistant 🤖")
    st.markdown(
        """
    Enter your travel details and our Bot will suggest flights, hotels, and itinerary!
    """
    )

# --------------------------------------------------
# Chat Input
# --------------------------------------------------
st.title("Travel Chatbot ✈️🏨")

with st.form("travel_form", clear_on_submit=True):
    st.subheader("Flight Details")
    origin = st.text_input("Origin (Airport Code)", "DEL")
    destination = st.text_input("Destination (Airport Code)", "BLR")
    outbound_date = st.date_input("Outbound Date")
    return_date = st.date_input("Return Date")

    st.subheader("Hotel Details")
    location = st.text_input("City", "Bangalore")
    check_in_date = st.date_input("Check-in Date")
    check_out_date = st.date_input("Check-out Date")

    submitted = st.form_submit_button("Ask Myra")

if submitted:
    # Convert dates to string
    outbound_date = outbound_date.strftime("%Y-%m-%d")
    return_date = return_date.strftime("%Y-%m-%d")
    check_in_date = check_in_date.strftime("%Y-%m-%d")
    check_out_date = check_out_date.strftime("%Y-%m-%d")

    # Prepare request payload
    payload = {
        "flight_req": {
            "origin": origin,
            "destination": destination,
            "outbound_date": outbound_date,
            "return_date": return_date
        },
        "hotel_req": {
            "location": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }
    }

    # Show user message
    user_msg = f"Origin: {origin}, Destination: {destination}, Dates: {outbound_date} to {return_date}, Hotel in {location} ({check_in_date} to {check_out_date})"
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # Call Travel Planner API
    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        if response.status_code == 200:
            # Build chatbot reply
            flights_info = "\n".join([f"{f['airline']} | {f['price']} | {f['duration']}" for f in data["flights"]])
            hotels_info = "\n".join([f"{h['name']} | {h['price']} | Rating {h['rating']}" for h in data["hotels"]])
            reply = f"**Flights:**\n{flights_info}\n\n**Hotels:**\n{hotels_info}\n\n**Flight Recommendation:** {data['ai_flight_recommendation']}\n\n**Hotel Recommendation:** {data['ai_hotel_recommendation']}\n\n**Itinerary:**\n{data['itinerary']}"
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {data}"})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"API request failed: {e}"})

# --------------------------------------------------
# Display chat messages
# --------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Myra:** {msg['content']}")
