import sqlite3
import os
import time
from datetime import datetime, timezone

class DatabaseHandler:
    def __init__(self, db_path):
        try:
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    main_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_id TEXT,
                    image_group INTEGER,
                    image_path TEXT,
                    saved_epoch INTEGER,
                    camera_source INTEGER,
                    location_prediction TEXT, -- This should change based on what location prediction features we do
                    has_earth INTEGER, -- SQLite doesnt have integers, so store this as 1=True 0=False
                    has_space INTEGER -- SQLite doesnt have integers, so store this as 1=True 0=False
                )
            ''')
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Database connection failed: {e}")
    
    def _generate_image_group(self):
        previous_image_group = self.cursor.execute("SELECT MAX(image_group) FROM metadata").fetchone()
        image_group = previous_image_group[0]+1 if previous_image_group is not None and previous_image_group[0] is not None else 1
        return image_group

    def _generate_image_folder(self):
        image_folder = f"{os.path.expanduser('~/captures')}/{self._generate_image_group()}"
        os.makedirs(image_folder, exist_ok=True)
        return image_folder

    def save_images(self, connection_manager, enable_mask, timeout_seconds=10):
        # Generate save path
        image_folder = self._generate_image_folder()
        image_group = self._generate_image_group()

        # Save each image over UART
        mask_indices = [i for i, bit in enumerate(enable_mask) if bit == '1']
        for i in mask_indices:
            # Save image
            image_id = f"{image_group}_{i}"
            image_path = f"{image_folder}/{image_id}.jpg"
            with open(image_path, 'wb') as f:
                start_time = time.time()
                while True:
                    chunk = connection_manager.read_bytes(512, timeout_seconds)
                    if chunk:
                        if b'EOF' in chunk:
                            eof_index = chunk.find(b'EOF')
                            f.write(chunk[:eof_index])
                            break
                        f.write(chunk)
                        start_time = time.time()
                    else:
                        if time.time() - start_time > timeout_seconds:
                            print(f"[HOST] Timeout while receiving image {image_id}")
                            break
                        time.sleep(0.01)
                print(f"[HOST] Received image {image_id}")

            # Enter image metadata into the metadata table.
            self.cursor.execute(
                (
                    "INSERT INTO metadata(image_id, image_group, saved_epoch, camera_source, image_path) "
                    "VALUES(?, ?, ?, ?, ?)"
                ),
                ( image_id, image_group, int(datetime.now(tz=timezone.utc).timestamp()), i, image_path)
            )
            self.db.commit()
        return True

    def retrieve(self, args):
        self.accepted_arguments = {
            "image_id": None, 
            "request_epoch": None, 
            "capture_epoch": None, 
            "look_before_epoch": 0
        }

        for i in range(0, len(args), 2):
            key = args[i]
            if key in self.accepted_arguments:
                self.accepted_arguments[key] = int(self.arguments[i+1])
        
        self.query(
            self.accepted_arguments["image_id"],
            self.accepted_arguments["request_epoch"],
            self.accepted_arguments["capture_epoch"],
            self.accepted_arguments["look_before_epoch"]
        )
    
    def query(
        self,
        image_id,
        request_epoch,
        capture_epoch,
        look_before_epoch
    ):
        try:
            base = "SELECT * FROM metadata WHERE 1=1"
            params = []

            # Handle different query cases based on input arguments
            if image_id is not None:
                base += "AND image_id = ?"
                params.append(image_id)
            if request_epoch is not None:
                if look_before_epoch == 1:
                    query += " AND ABS(request_epoch - ?) IS NOT NULL"
                else:
                    query += " AND request_epoch >= ?"
                params.append(request_epoch)
            if capture_epoch is not None:
                if look_before_epoch == 1:
                    query += " AND ABS(capture_epoch - ?) IS NOT NULL"
                else:
                    query += " AND capture_epoch >= ?"
                params.append(capture_epoch)
            if look_before_epoch == 1:
                query += " ORDER BY ABS(request_epoch - ?) ASC"
                params.append(request_epoch)
            query += " LIMIT 1"

            # Execute query
            cursor = self.db.cursor()
            cursor.execute(query, params)

            # Process results
            rows = cursor.fetchall()
            for row in rows:
                image_id = row[0]
                image_path = row[1] if row[1] else "NULL"
                request_epoch = row[2]
                capture_epoch = row[3]
                camera_source = row[4]
                print(
                    f"image_id: {image_id}, "
                    f"image_path: {image_path}, "
                    f"request_epoch: {request_epoch}, "
                    f"capture_epoch: {capture_epoch}, "
                    f"camera_source: {camera_source}"
                )
        except Exception as e:
            print(f"Query failed: {e}")
            