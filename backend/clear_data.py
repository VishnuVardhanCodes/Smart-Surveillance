import sqlite3
import os

def clear_all_data():
    print("Starting data cleanup...")
    
    # 1. Clear SQLite Database
    db_path = 'database/surveillance.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM detections")
            conn.commit()
            conn.close()
            print("Database records cleared.")
        except Exception as e:
            print(f"Error clearing database: {e}")
    else:
        print("Database not found, skipping.")

    # 2. Clear Detection Images
    images_dir = 'images'
    if os.path.exists(images_dir):
        try:
            for subdir in ['persons', 'vehicles', 'plates']:
                dir_path = os.path.join(images_dir, subdir)
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
            print("Detection images cleared.")
        except Exception as e:
            print(f"Error clearing images: {e}")

    # 3. Clear Logs
    log_file = 'logs/detections.log'
    if os.path.exists(log_file):
        try:
            with open(log_file, 'w') as f:
                f.truncate(0)
            print("Logs cleared.")
        except Exception as e:
            print(f"Error clearing logs: {e}")

    print("Reset complete. System is ready for a fresh start.")

if __name__ == "__main__":
    clear_all_data()
