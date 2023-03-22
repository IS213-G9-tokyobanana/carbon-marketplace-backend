class ResponseBodyJSON():
    def __init__(self, success: bool, data) -> None:
        self._success = success
        self._data = data
    
    @property
    def success(self):
        return self._success
    
    @property
    def data(self):
        return self._data
    
    @success.setter
    def success(self, success: bool):
        self._success = success
    
    @data.setter
    def data(self, data):
        self._data = data

    def json(self) -> dict:
        return {
            "success": self.success,
            "data": self.data
        }

    def __repr__(self) -> str:
        return f'{self.json()}'
    

class CustomException(Exception):
    def __init__(self, message, resource=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._message = message
        self._resource = resource

    @property
    def message(self):
        return self._message
        
    @property
    def resource(self):
        return self._resource
    
    @message.setter
    def message(self, message):
        self._message = message
    
    @resource.setter
    def resource(self, resource):
        self._resource = resource

    def json(self) -> dict:
        return {
            "message": self.message,
            "resource": self.resource
        }
    def __repr__(self) -> str:
        return f'{self.json()}'

