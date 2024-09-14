import requests
import os
import json

SERVER_URL = "http://100.124.166.5:5000"  
TIMEOUT = 3000

session = requests.Session()

def login(password):
    try:
        response = session.post(f"{SERVER_URL}/login", json={"password": password}, timeout=TIMEOUT)
        if response.status_code == 200:
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return False

def logout():
    try:
        response = session.get(f"{SERVER_URL}/logout", timeout=TIMEOUT)
        if response.status_code == 200:
            print("Logged out successfully")
        else:
            print("Logout failed")
    except requests.exceptions.RequestException as e:
        print(f"Error during logout: {e}")

def get_directory_structure():
    try:
        response = session.get(f"{SERVER_URL}/list_files", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Authentication required. Please log in.")
            return None
        else:
            print(f"Failed to get directory structure. Status code: {response.status_code}")
            print("Response content:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        return None

def download_file(file_path, save_path):
    try:
        url = f"{SERVER_URL}/download"
        params = {'path': file_path}
        response = session.get(url, params=params, timeout=TIMEOUT)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File {file_path} downloaded successfully.")
        elif response.status_code == 401:
            print("Authentication required. Please log in.")
        else:
            print(f"Failed to download {file_path}. Status code: {response.status_code}")
            print("Response content:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {file_path}. Error: {e}")
    except IOError as e:
        print(f"Failed to save file {file_path}. Error: {e}")



def print_directory_structure(structure, indent=""):
    for item, value in structure.items():
        if value == "file":
            print(f"{indent}{item}")
        else:
            print(f"{indent}{item}/")
            print_directory_structure(value, indent + "  ")

if __name__ == "__main__":
    directory_structure = get_directory_structure()
    print("Directory structure:")
    print_directory_structure(directory_structure)
    
    def find_first_file(structure, path=""):
        for item, value in structure.items():
            if value == "file":
                return os.path.join(path, item)
            else:
                result = find_first_file(value, os.path.join(path, item))
                if result:
                    return result
        return None

    first_file = find_first_file(directory_structure)
    if first_file:
        download_file(first_file, f'./downloaded_{os.path.basename(first_file)}')
    else:
        print("No files found in the directory structure.")