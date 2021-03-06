

# This class handles all the data uploads to the Azure server
import ujson
import urequests
from logger import Logger

class DataUploader:

    URL = "https://team1-fydp.azurewebsites.net/result"
    ESP_LOG_FILE = "esp_log.txt"

    def __init__(self):
        self.logger = Logger(self.ESP_LOG_FILE)

    def upload_data(self, data):

        headers = {"content-type" : "application/json"}
        self.logger.log("Data uploaded: " + str(data))
        response = urequests.put(self.URL, data = ujson.dumps(data), headers=headers)
        self.logger.log("Server response" + str(response.json()))



