import os
import json

# যেসব JSON ফাইল চেক করতে হবে
json_files = [
    "used_tx.json",
    "users_db.json",
    "subscriptions.json",
    "data.json"
]

# প্রতিটি ফাইলের জন্য ডিফল্ট কনটেন্ট
default_data = {
    "used_tx.json": [],
    "users_db.json": {},
    "subscriptions.json": [],
    "data.json": {}
}

def ensure_valid_json(file_name, default_content):
    if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        print(f"[FIX] {file_name} was empty or missing. Creating with default content.")
        with open(file_name, "w") as f:
            json.dump(default_content, f, indent=4)
        return

    # JSON লোড করে চেক করো
    try:
        with open(file_name, "r") as f:
            json.load(f)
        print(f"[OK] {file_name} is valid.")
    except json.JSONDecodeError:
        print(f"[ERROR] {file_name} is invalid. Resetting with default content.")
        with open(file_name, "w") as f:
            json.dump(default_content, f, indent=4)

if __name__ == "__main__":
    for file in json_files:
        ensure_valid_json(file, default_data[file])
