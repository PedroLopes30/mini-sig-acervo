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
    
class Obra():
    pass

class Usuario():
    pass

class Emprestimo():
    pass

class Acervo():
    def __init__(self):
        self.acervo = {}

    def __iadd__(self, obra:Obra):
        if obra in self.acervo:
            self.acervo[obra] += 1
            return self.acervo

        self.adicionar(obra)
        return self.acervo

    def __isub__(self, obra:Obra):
        if obra in self.acervo:
            if self.acervo.obra > 1:
                self.acervo[obra] -= 1
                return self.acervo
            self.remover(obra)
    
        return "Não contém essa obra no acervo"
    
    def adicionar(self, obra):
        self.acervo[obra] = 1

    def remover(self, obra):
        del self.acervo[obra]

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