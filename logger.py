
# This class handles application logging
import machine

class Logger:

    def __init__(self, file_name):
        self.file_name = file_name

    # Input: String to be logged
    # Output: None
    # Writes given string to log file
    def log(self, log_str):
        curr_time = str(machine.RTC().datetime())
        f = open(self.file_name, "a")
        f.write(curr_time + " " + log_str)
        f.close()

    # Input: None
    # Output: None
    # Uploads current log file to class' upload_endpoint
    def upload():
        pass



