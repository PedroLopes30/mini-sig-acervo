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
    
class Obra(BaseEntity):

    def __init__(self, titulo, autor, ano, categoria):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = 1

    def disponivel(self, estoque):
        if estoque >= 1:
            return True
        
    def __str__(self):
        return f"{self.titulo} ({self.ano})."  

class Usuario(BaseEntity):
    
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        return self.nome.lower() < other.nome.lower()

    def __str__(self):
        return f"{self.nome}"  

class Emprestimo(BaseEntity):

    def __init__(self, obra, usuario):
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