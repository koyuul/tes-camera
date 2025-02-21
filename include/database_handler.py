import sqlite3

class DatabaseHandler:
    def __init__(self):
        try:
            self.db = sqlite3.connect("/home/mendel/tes-camera/image_info.db")
        except sqlite.Error as e:
            print(f"Databse connectio failed: {e}")
        
    def retrieve(self, args):
        self.accepted_arguments = {
            "image_id": None, 
            "request_epoch": None, 
            "capture_epoch": None, 
            "look_before_epoch": 0
        }

        for i in range(0, len(args), 2):
            key = args[i]
            if key in accepted_arguments:
                accepted_arguments[key] = int(arguments[i+1])
        
        self.query(
            accepted_arguments["image_id"],
            accepted_arguments["request_epoch"],
            accepted_arguments["capture_epoch"],
            accepted_arguments["look_before_epoch"]
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
            