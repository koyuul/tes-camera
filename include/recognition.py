class RecognitionController:
    def __init__(self):
        print("[RECOG]: Initialized")
        self.conn = sqlite3.connect("/home/mendel/tes-camera/image_info.db")
        self.cursor = self.conn.cursor()
    
    def recognize(self):
        # Function that analyzes the image, and adds the findings to the DB row
        ...