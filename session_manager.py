import streamlit as st
from streamlit_cookies_manager import CookieManager

# Initialize cookie manager
cookies_manager = CookieManager()

def set_session(user_id, email):
    st.session_state['user_id'] = user_id
    st.session_state['logged_in'] = True
    st.session_state['email'] = email
    # Save session to cookies
    cookies_manager["user_id"] = str(user_id)
    cookies_manager["email"] = email
    cookies_manager.save()

def clear_session():
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['email'] = ""
    # Clear cookies
    cookies_manager["user_id"] = ""
    cookies_manager["email"] = ""
    cookies_manager.save()

def load_session():
    # Load cookies if available
    if not cookies_manager.ready():
        cookies_manager.load()

    user_cookie = cookies_manager.get("user_id", None)
    if user_cookie:
        st.session_state['user_id'] = int(user_cookie)
        st.session_state['logged_in'] = True
        st.session_state['email'] = cookies_manager.get("email", "")
    else:
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['email'] = ""

load_session()
