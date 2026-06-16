import streamlit as st
import json
import os
import hashlib
import secrets
import getpass
import subprocess
import sys

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256$100000${salt}${key.hex()}"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"paths": [], "users": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

st.set_page_config(page_title="Macro Setup Wizard", page_icon="🛠️")

st.sidebar.title("Macro Setup")
page = st.sidebar.radio("Navigate", ["Home", "Locations", "Setup Accounts", "Finish Setup"])

if page == "Home":
    st.title("Welcome to Macro")
    st.write("Macro is a lightweight media streaming server.")
    st.write("Follow the steps in the sidebar to configure your instance.")

elif page == "Locations":
    st.title("Manage File Paths")
    config = load_config()
    
    st.subheader("Current Paths")
    if not config["paths"]:
        st.info("No paths added yet.")
    else:
        for i, path in enumerate(config["paths"]):
            col1, col2 = st.columns([4, 1])
            col1.write(path)
            if col2.button("Remove", key=f"rem_{i}"):
                config["paths"].pop(i)
                save_config(config)
                st.rerun()

    st.divider()
    new_path = st.text_input("Add new folder path")
    if st.button("Add Path"):
        if new_path and new_path not in config["paths"]:
            config["paths"].append(new_path)
            save_config(config)
            st.success(f"Added: {new_path}")
            st.rerun()

    if st.button("Clear All Paths"):
        config["paths"] = []
        save_config(config)
        st.rerun()

elif page == "Setup Accounts":
    st.title("Create User Accounts")
    config = load_config()

    st.subheader("Existing Users")
    if not config.get("users"):
        st.info("No users created yet.")
    else:
        for user in config["users"]:
            st.write(f"- {user}")

    st.divider()
    st.subheader("Create New User")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not new_user or not new_pass:
            st.error("Username and password are required.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            config["users"][new_user] = hash_password(new_pass)
            save_config(config)
            st.success(f"User '{new_user}' created!")
            st.rerun()

elif page == "Finish Setup":
    st.title("Finalize Setup")
    st.write("This will create and start a systemd service for Macro.")
    
    sudo_pass = st.text_input("Enter sudo password", type="password")
    
    if st.button("Start Service"):
        if not sudo_pass:
            st.error("Sudo password is required.")
        else:
            st.info("Setting up systemd service...")
            
            server_dir = os.path.dirname(os.path.abspath(__file__))
            service_name = "macro.service"
            temp_service_path = "/tmp/macro.service"
            user = getpass.getuser()

            service_content = f"""[Unit]
Description=Macro API Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={server_dir}
ExecStart={sys.executable} {os.path.join(server_dir, "main.py")}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
            try:
                with open(temp_service_path, "w") as f:
                    f.write(service_content)
                
                commands = [
                    f"sudo -S cp {temp_service_path} /etc/systemd/system/{service_name}",
                    "sudo -S systemctl daemon-reload",
                    f"sudo -S systemctl enable {service_name}",
                    f"sudo -S systemctl start {service_name}"
                ]

                success = True
                for cmd in commands:
                    proc = subprocess.Popen(
                        cmd, shell=True, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    stdout, stderr = proc.communicate(input=sudo_pass + "\n")
                    if proc.returncode != 0:
                        success = False
                        st.error(f"Error: {stderr.strip() or stdout.strip()}")
                        break
                
                if success:
                    st.success("Service successfully created and started!")
                    
            except Exception as e:
                st.error(f"Failed: {str(e)}")
            finally:
                if os.path.exists(temp_service_path):
                    os.remove(temp_service_path)
