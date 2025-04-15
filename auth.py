import json
import os

# Path to the users.json file
USERS_FILE = "users.json"

# Load existing users from the JSON file
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or malformed, return an empty dictionary
            return {}
    return {}  # Return an empty dictionary if the file doesn't exist

# Save new user to the JSON file
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

# Sign up a new user
def signup(email, password):
    users = load_users()
    if email in users:
        return False, "Email already exists. Please log in."
    users[email] = {"password": password}
    save_users(users)
    return True, "Signup successful! Please log in."

# Log in an existing user
def login(email, password):
    users = load_users()
    if email in users and users[email]["password"] == password:
        return True, "Login successful!"
    return False, "Invalid email or password."