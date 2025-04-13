import streamlit as st
import json
from utils import covert_currency,url_param,get_news
import streamlit as st
import time

# ✅ This must come before any other Streamlit command
st.set_page_config(page_title="News Carousel", layout="centered")

if 'carousel_started' not in st.session_state:
    st.session_state.carousel_started = False

# Navigation tabs
nav = st.sidebar.selectbox("Navigate", ["USD to INR", "INR to USD"])

# Initialize default values
from_currency = ""
to_currency = ""

# Set currency based on navigation
if nav == "USD to INR":
    from_currency = "usd"
    to_currency = "inr"
        # Optional: reset so it can run again
    st.session_state.carousel_started = False
elif nav == "INR to USD":
    from_currency = "inr"
    to_currency = "usd"
        # Optional: reset so it can run again
    st.session_state.carousel_started = False

# Display the form
with st.form(key="currency_form"):
    amount = st.number_input(f"Enter amount in {from_currency.upper()}:", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Convert")

    if submit:
        result = {
            "From": from_currency,
            "To": to_currency,
            "Amount": amount
        }
        print(result)
        user_input = url_param(From=from_currency.upper(), To=to_currency.upper(), amount=amount)
    
        with st.spinner("Calling Vasa agent... wait for 2 mins...fetching data from xe.com"):
            response_dict = covert_currency(user_input)

        # Step 3: Show agent response
        st.subheader("Converted Amount (via Gemini Agent):")
        from_currency = list(response_dict.keys())[0].upper()
        to_currency = list(response_dict.keys())[1].upper()
        from_amount = list(response_dict.values())[0]
        to_amount = list(response_dict.values())[1]

        # Fancy display
        st.markdown(f"""
            <div style="padding: 1rem; border-radius: 12px; background-color: #e6f7ff; border: 1px solid #91d5ff; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">
                <h2 style="color: #1890ff; margin-bottom: 0.5rem;">💱 Currency Converted!</h2>
                <p style="font-size: 20px; margin: 0;"><strong>{from_amount:.2f} {from_currency}</strong> = 
                <strong style="color: green;">{to_amount:.2f} {to_currency}</strong></p>
            </div>
        """, unsafe_allow_html=True)


if not st.session_state.carousel_started:
    st.session_state.carousel_started = True

    st.title("📰 USD/INR News")
    news_data = get_news()
    placeholder = st.empty()

    for i in range(1000):  # Auto-scroll
        index = i % len(news_data)
        news_item = news_data[index]

        with placeholder.container():
            st.markdown(
                f"""
                <div style="padding: 1.5rem; border-radius: 12px; background-color: #f0f4ff; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); text-align: center;">
                    <b style="font-size: 1.2rem; font-weight: 600;">{news_item['headline']}</b>
                    <p style="margin-top: 0.5rem; font-size: 0.95rem; color: #666;">SOURCE: {news_item['source']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        time.sleep(3)

    # Optional: reset so it can run again
    # st.session_state.carousel_started = False
