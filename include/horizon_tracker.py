class HorizonTrackerController:
    def __init__(self):
        print("[HORZ]: Initialized")
        self.conn = sqlite3.connect("/home/mendel/tes-camera/image_info.db")
        self.cursor = self.conn.cursor()
    
    def detect(self, image_id):
        # Function that analyzes the image, and adds the findings to the DB row
        ...