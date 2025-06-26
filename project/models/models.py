# Imports
import uuid
import datetime

# Classes
class BaseEntity():
    def __init__(self):
        self.id = self._gerar_id()
        self.creation_date = datetime.date.today()

    def __eq__(self, other):
        return id(self) == id(other) and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()   
    
class Obra(BaseEntity):
    def __init__(self, titulo, autor, ano, categoria):
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = 1

    def disponivel(self, estoque):
        for obra_acervo in estoque:
            if obra_acervo["obra"].__eq__(self): return True
        return False
        
    def __str__(self):
        return f"{self.titulo} ({self.ano})."  

class Usuario(BaseEntity):
    
    def __init__(self, nome, email):
        super().__init__()
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        return self.nome.lower() < other.nome.lower()

    def __str__(self):
        return f"{self.nome}"  

class Emprestimo(BaseEntity):

    def __init__(self, obra, usuario):
        super().__init__()
        self.obra = obra
        self.usuario = usuario
        self.data_retirada = datetime.date.today()
        self.data_prev_devol = None 

    def marcar_devolucao(self, data_dev_real): 
        self.data_prev_devol = self.data_retirada + datetime.timedelta(days=data_dev_real)
        return self.data_prev_devol

    def dias_atraso(self, data_ref):
        if self.data_prev_devol:
            atraso = (data_ref - self.data_prev_devol).days
            if atraso > 0:
                return atraso
            else:
                return 0
        return None
    
    def __str__(self):
        return f"-> {self.obra.titulo} - Data de retirada: {self.data_retirada}\n - Data prevista de devolução: {self.data_prev_devol}\n - Usuário: {self.usuario.nome}"
    
class Acervo:
    def __init__(self):
        self.acervo = [] # Estrutura: {"obra": obra, "estoque": estoque}

    def __verificar_obra(self, obra):
        if obra.disponivel(self.acervo):
            for obra_acervo in self.acervo:
                if obra_acervo["obra"].__eq__(obra):
                    return obra_acervo
        return False

    def __iadd__(self, obra:Obra):
        obra_acervo = self.__verificar_obra(obra)
        if obra_acervo:
            if obra.quantidade >= 1:
                obra.quantidade -= 1
                obra_acervo["estoque"] +=1
                return self.acervo
            return "Sem obra disponível."
        
        self.adicionar(obra)
        return self.acervo

    def __isub__(self, obra:Obra):
        obra_acervo = self.__verificar_obra(obra)
        if obra_acervo["estoque"] >= 1:
            if obra_acervo["estoque"] == 1:
                self.remover(obra_acervo)
            else:
                obra_acervo["estoque"] -=1
            obra.quantidade += 1
        return self.acervo
    
    def adicionar(self, obra):
        if obra.quantidade >= 1:
            self.acervo.append({"obra": obra, "estoque": 1})
            obra.quantidade -= 1

    def remover(self, obra_acervo):
        self.acervo.remove(obra_acervo)