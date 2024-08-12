# FileEncryptor

FileEncryptor is a Python-based script designed to encrypt and decrypt files and directories. The script automatically sets up the necessary environment, installs required libraries, and provides an intuitive command-line interface for encryption and decryption.

## Features

- **Automatic Environment Setup**: Automatically checks and updates Python to the latest version, installs or upgrades `pip`, and installs required libraries.
- **File and Directory Encryption**: Encrypts all files in a specified directory using the Fernet symmetric encryption.
- **File and Directory Decryption**: Decrypts all encrypted files in a specified directory using the correct encryption key.
- **Encrypted Key Storage**: Stores the encryption key securely using a custom password-protected AES encryption.
- **Key Recovery Script**: Generates a script (`show_key.py`) that allows users to reveal the Fernet key with the correct password.

## Prerequisites

- Python 3.x
- Internet connection (for downloading Python updates and required libraries)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/ItamaRoginsky/FileEncryptor.git
    cd FileEncryptor
    ```

2. Run the script:

    ```bash
    python FileEncryptor.py
    ```

## Usage

1. **Encryption**:

    - Run the script and choose to encrypt files:
    
      ```bash
      python FileEncryptor.py
      ```
    
    - Select the encryption option by typing `e` when prompted.
    - The script will encrypt all files in the current directory.

2. **Decryption**:

    - Run the script and choose to decrypt files:
    
      ```bash
      python FileEncryptor.py
      ```
    
    - Select the decryption option by typing `d` when prompted.
    - Enter the correct encryption key to decrypt all files in the current directory.

## Key Management

- **Key Storage**: The encryption key is stored in a `key.txt` file, encrypted with a custom password (`itamar` by default).
- **Key Recovery**: The `show_key.py` script allows you to reveal the encryption key by entering the correct password.

## Security Considerations

- The password used to encrypt the key is hardcoded in the script. Ensure to change the default password (`itamar`) to something more secure and memorable.
- Store the `key.txt` file and `show_key.py` script securely, as they are essential for decrypting your files.

## Disclaimer

This tool is provided for educational purposes only. Use it responsibly and ensure you have proper authorization when encrypting files.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
