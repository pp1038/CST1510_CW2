import bcrypt
from pathlib import Path

USERS_FILES = Path(__file__).parent / "DATA" / "users.txt"


def hash_password(password):
    binary_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(binary_password, salt)
    return hashed_password.decode("utf-8")        # bytes -> normal string


def is_valid_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def register(username, password):
    USERS_FILES.parent.mkdir(exist_ok=True)       # make DATA folder if missing
    hashed_password = hash_password(password)
    with open(USERS_FILES, "a") as f:
        f.write(f"{username},{hashed_password}\n")   # no spaces around the comma
    print(f"User {username} registered")


def login(username, password):
    if not USERS_FILES.exists():
        print("No users registered yet")
        return

    with open(USERS_FILES, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            stored_username, stored_password = line.split(",")

            if username == stored_username:
                if is_valid_password(password, stored_password):
                    print("Login successful")
                    print(f"Welcome {username}")
                else:
                    print("Incorrect password")
                return

    print("Username not found")


if __name__ == "__main__":
    while True:
        choice = input("Do you want to (1) register (2) login or (3) exit? ")
        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            register(username, password)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            login(username, password)

        elif choice == "3":
            print("Exiting")
            break