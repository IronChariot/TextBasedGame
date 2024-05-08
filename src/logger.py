import os

class Logger:
    def __init__(self, log_file_name):
        self.log_file_name = log_file_name
        self.log_file_path = os.path.join(os.getcwd(), "logs", log_file_name)
        self.log_file = open(self.log_file_path, "w")
        self.log_file.write("--------------------------------------------------------------\n")
        self.last_updated_time = self.get_last_updated_time()

    def write_to_log(self, text):
        self.log_file.write(text + "\n")

    def close_log(self):
        self.log_file.close()

    def get_last_updated_time(self):
        return os.path.getmtime(self.log_file_path)
    
    def read_log(self):
        with open(self.log_file_path, "r") as log_file:
            return log_file.read()