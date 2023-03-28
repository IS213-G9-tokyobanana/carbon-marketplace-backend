class CustomException(Exception):
    def __init__(self,message):
        super().__init__(message)
        self.message = message

    @property
    def message(self):
        return self.message

    @message.setter
    def message(self,message):
        self.message = message
    
    def json(self): 
        return {
            "message":self.message
        }