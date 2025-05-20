import streamlit as st
import hashlib
import json
import os
import time
from cryptography.fernet import fernet
from base64 import urlsafe_b64decode
from hashlib import pbkdf2_hmac

## data info by user
DATA_FILE = "secure_data.json"
SALT = b"secure_salt_value"
LOCKOUT_DURATION = 60

#login detail
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "lockout_time" not in st.session_state:
    st.session_state.lockout_time = 0

# data loaded
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE , "w") as f:
        json.dump(data, f)

def generate_key(passkey):
    key = pbkdf2_hmac('sha256' , passkey.encode(), SALT, 100000)
    return urlsafe_b64decode(key)

def hash_password(password):
    return hashlib.pbkdf2_hmac('sha256' , password.encode(), SALT, 100000).hax()

# cryptography.fernet used
def encrypt_text(text, key):
    cipher = fernet(generate_key(key))
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypt_text, key):
    try:
        cipher = fernet(generate_key(key))
        return cipher.decrypt(encrypt_text.encode()).decode()
    except:
        return None

stored_data = load_data()

#navigattion
st.title("🔐 SECURE DATA ENCRYPTION")
menu = ["Home", "Register", "Login", "Store Data", "Retrieve Data"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("WELCOME TO MY DATA ENCRYPTION !")
    st.markdown("Use this app to **securely store and retrieve data")

# user register
elif choice == "Register":
    st.subheader("🗉 REGISTER USER")
    username = st.text_input("choose Username")
    password = st.text_input("choose Password", type= "password")

    if st.button("Register"):
        if username and password:
            if username in stored_data:
                st.warning("⚠️ User already exist.")
            else:
                stored_data[username] = {
                    "password": hash_password(password),
                    "data": []
                }
                save_data(stored_data)
                st.success("🎉 User register successfully!")
        else:
            st.error("Both fields are required.")
    elif choice == "Login":
        st.subheader("🗝️ User Login")

        if time.time() < st.session_state.lockout_time:
            remaining = int(st.session_state.lockout_time - time.time())
            st.error(f"⌛ Too many failed attempts. please wait {remaining} seconds.")
            st.stop()
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in stored_data and stored_data[username]["password"] == hash_password(password):
                st.session_state.authenticated_user = username
                st.session_state.failed_attempts = 0
                st.success(f"✔️Welcome{username}!")
            else:
                st.session_state.failed_attempts += 1
                remaining = 3 - st.session_state.failed_attempts
                st.error(f"❌Invalid Credentials! Attempts left: {remaining}")

                if st.session_state.failed_attempts >= 3:
                    st.session_state.lockout_time = time.time() + LOCKOUT_DURATION
                    st.error("⏹️ To many failed attempts. Locked for 60 seconds")
                    st.stop()

# data stored
elif choice == "Stored Data":
    if not st.session_state.authenticated_user:
        st.warning("⚠️please login first.")
    else:
        st.subheader("📦Store Encrypted Data!")
        data = st.text_area("Enter data to encrypty")
        passkey = st.text_input("Encryption key (passphrase)", type="password")

        if st.button("Encrypt And Save"):
            if data and passkey:
                encrypted = encrypt_text(data,passkey)
                stored_data[st.session_state.authenticated_user]["data"].append(encrypted)
                save_data(stored_data)
                st.success("✔️Data encrypted and save successfully!")

            else:
                st.error("All fields are required to fill.")

#data sectioon
elif choice == "Retieve Data":
    if not st.session_state.authenticated_user:
        st.warning("🔓 Please login first")
    else:
        st.subheader("🔍 Retieve data")
        user_data = stored_data.get(st.session_state.authenticated_user, {}).get("data", [])

        if not user_data:
            st.info("No data Found!")
        else:
            st.write("Encrypted Data Enteries:")
            for i, item in enumerate(user_data):
                st.code(item,language="text")

            encrypted_input = st.text_area("Enter Encrypted Text")
            passkey = st.text_input("Enter Passkey T decrypt", type="password")

            if st.button("Decrypt"):
                result = decrypt_text(encrypted_input, passkey)
                if result:
                    st.success(f"✔️ Decrypted : {result}")
                else:
                    st.error("❌ Incorrect passkey or corrupted data.")
