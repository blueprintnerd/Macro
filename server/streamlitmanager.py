import streamlit as st
import requests
import sqlite3

def draw_manager(ip_address):
    st.write("Macro Manager")

    sidebar = st.sidebar.selectbox(
      ('Network', 'Filepaths', 'Users')
    )