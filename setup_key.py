import os
from pathlib import Path
from cryptography.fernet import Fernet

def setup_encryption_key() -> None:
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    
    # 1. Check if EDITH_ENCRYPTION_KEY already exists and has a value in .env
    key_exists = False
    lines = []
    
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            if line.strip().startswith("EDITH_ENCRYPTION_KEY="):
                parts = line.split("=", 1)
                if len(parts) > 1 and parts[1].strip():
                    key_exists = True
                    break
                    
    if key_exists:
        print("Encryption key already set, Boss!")
        return

    # 2. Generate new Fernet key
    new_key = Fernet.generate_key().decode()
    
    # 3. Write directly into the .env file under EDITH_ENCRYPTION_KEY=
    key_written = False
    new_lines = []
    
    if not env_path.exists():
        new_lines = [
            "# EDITH - Environment Configuration\n",
            f"EDITH_ENCRYPTION_KEY={new_key}\n"
        ]
        key_written = True
    else:
        for line in lines:
            if line.strip().startswith("EDITH_ENCRYPTION_KEY="):
                new_lines.append(f"EDITH_ENCRYPTION_KEY={new_key}\n")
                key_written = True
            else:
                new_lines.append(line)
                
        if not key_written:
            new_lines.append(f"\nEDITH_ENCRYPTION_KEY={new_key}\n")
            
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print("Encryption key generated and saved securely, Boss!")

if __name__ == "__main__":
    setup_encryption_key()
