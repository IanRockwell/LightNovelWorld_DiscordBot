import os
import json

def get_auth_json_path():
    folder_name = 'auth'  # Specify the folder name here
    file_name = 'auth.json'
    return os.path.abspath(os.path.join(folder_name, file_name))

def read_auth_json():
    file_path = get_auth_json_path()
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"[auth.read_auth_json] File '{file_path}' not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[auth.read_auth_json] Error decoding JSON in '{file_path}': {str(e)}")
        return {}

def write_auth_json(data):
    file_path = get_auth_json_path()
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"[auth.write_auth_json] Data written to '{file_path}' successfully.")
    except Exception as e:
        print(f"[auth.write_auth_json] Error writing to '{file_path}': {str(e)}")

def set_value_from_auth_json(key, new_value):
    data = read_auth_json()
    data[key] = new_value
    write_auth_json(data)

def get_value_from_auth_json(key):
    data = read_auth_json()
    if key in data:
        return data[key]
    else:
        print(f"[auth.get_value_from_auth_json] Key '{key}' not found in auth.json.")
        return None