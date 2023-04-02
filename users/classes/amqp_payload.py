class Payload():
    def __init__(self, resource_id, type, data) -> None:
        self._resource_id = resource_id
        self._type = type
        self._data = data

    @property
    def resource_id(self):
        return self._resource_id
    
    @property
    def type(self):
        return self._type

    @property
    def data(self):
        return self._data
    
    @resource_id.setter
    def resource_id(self, resource_id):
        self._resource_id = resource_id
    
    @type.setter
    def type(self, type):
        self._type = type
    
    @data.setter
    def data(self, data):
        self._data = data

    def json(self):
        return {
            'resource_id': self.resource_id,
            'type': self.type,
            'data': self.data
        }

    def __repr__(self) -> str:
        return f'{self.json()}'
