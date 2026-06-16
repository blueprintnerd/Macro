import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import os

st.set_page_config(page_title="Macro Web Client", page_icon="🎵")

if "auth" not in st.session_state:
    st.session_state.auth = None
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:1470"
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""

def login():
    st.title("Macro Login")
    api_url = st.text_input("Server URL", value=st.session_state.api_url)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            response = requests.post(
                f"{api_url}/login", 
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )
            if response.status_code == 200:
                st.session_state.auth = (username, password)
                st.session_state.api_url = api_url
                st.session_state.username = username
                st.session_state.password = password
                st.rerun()
            else:
                st.error("Invalid credentials.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def dashboard():
    st.title("Macro Dashboard")
    st.sidebar.title(f"User: {st.session_state.username}")
    
    view = st.sidebar.radio("View", ["Files", "Music"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = None
        st.rerun()

    url = st.session_state.api_url
    auth = HTTPBasicAuth(*st.session_state.auth)

    endpoint = "/files" if view == "Files" else "/music"
    st.subheader(f"Macro {view}")

    try:
        response = requests.get(f"{url}{endpoint}", auth=auth, timeout=5)
        if response.status_code == 200:
            files = response.json()
            present_files = [f for f in files if f.get("status", "present") == "present"]
            
            if not present_files:
                st.info(f"No {view.lower()} found.")
            else:
                for f in present_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f.get("name", "Unknown File"))
                    with col2:
                        if st.button("Play", key=f"{view}_{f.get('id')}"):
                            st.session_state.playing = f
                
                if "playing" in st.session_state:
                    f = st.session_state.playing
                    st.divider()
                    st.subheader(f"Now Playing: {f.get('name')}")
                    
    
                    stream_url = f"{url}/stream/{f.get('id')}"
                    auth_stream_url = stream_url.replace("http://", f"http://{st.session_state.username}:{st.session_state.password}@")
                    st.audio(auth_stream_url)

        else:
            st.error(f"Failed to retrieve {view.lower()}.")
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")

if st.session_state.auth is None:
    login()
else:
    dashboard()
