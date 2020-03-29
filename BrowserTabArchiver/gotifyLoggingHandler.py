import logging
import requests

class GotifyHandler(logging.Handler):
    def __init__(self, address, apiKey, priority):
        logging.Handler.__init__(self)
        self.address = address
        self.apiKey = apiKey
        self.priority = priority if priority else 8

    def emit(self, record):
        # Make a short title (handy for calls to logging.exception())
        msg = self.format(record)
        title = msg.splitlines()[0]
        try:
            response = requests.post(self.address+'/message', params={"token":self.apiKey}, json={'message':msg, 'title':title, 'priority':self.priority})
            if response.status_code != 200:
                print ("GotifyHandler.emit(): server error {}".format(response.status_code))
        except requests.exceptions.ConnectionError:
            print ("GotifyHandler.emit(): connection error. not retrying.")