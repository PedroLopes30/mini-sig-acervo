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

class Acervo():
    def __init__(self):
        pass

    def __iadd__(self, obra:Obra):
        pass

    def __isub__(self, obra:Obra):
        pass
    
    def adicionar(self, obra):
        pass

    def remover(self, obra):
        pass

    def emprestar(self, obra, usuario, dias=7):
        pass

    def devolver(self, emprestimo, data_dev):
        pass

    def renovar(self, emprestimo, dias_extra):
        pass
    def relatorio_inventario(self, emprestimo, data_ref):
        pass

    def relatorio_debitos(self):
        pass

    def relatorio_usuario(self, usuario):
        pass

    def _valida_obra(self, obra):
        pass

    def _relatorio_builder(self, titulo):
        pass