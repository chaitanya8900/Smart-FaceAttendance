import pickle
import os

file_path = "encodings.pickle"

if not os.path.exists(file_path):
    print("❌ No registered users found.")
    exit()

name_to_delete = input("Enter the name to delete: ").strip()

new_data = []

with open(file_path, "rb") as f:
    while True:
        try:
            name, encoding = pickle.load(f)
            if name != name_to_delete:
                new_data.append((name, encoding))
        except EOFError:
            break

if len(new_data) == 0:
    os.remove(file_path)
    print(f"🗑️ All users deleted. File removed.")
else:
    with open(file_path, "wb") as f:
        for item in new_data:
            pickle.dump(item, f)
    print(f"✅ {name_to_delete} has been removed.")
