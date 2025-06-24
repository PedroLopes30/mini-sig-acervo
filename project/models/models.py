# Imports
import uuid
import datetime

# Classes
class BaseEntity():
    def __init__(self):
        self.id = self._gerar_id()
        self.creation_date = datetime.date.today()

    def __eq__(self, other):
        return self == other and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()