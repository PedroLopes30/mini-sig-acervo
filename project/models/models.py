# Imports
import uuid
import datetime

# Variaveis
format_data = '%d-%m-%Y'

# Classes
class BaseEntity():
    def __init__(self):
        self.id = self._gerar_id()
        self.creation_date = datetime.datetime.now().strftime(format_data)

    def __eq__(self, other):
        if not hasattr(other, 'id'):
            return False
        return self.__class__ == other.__class__ and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()   
    
class Obra(BaseEntity):

    obras = []

    def __init__(self, titulo:str, autor:str, ano, categoria:str, quantidade=1):
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

        Obra.obras.append(self)

    def disponivel(self, estoque):
        if not hasattr(estoque, 'obras_disponiveis'):
            return False
        
        return estoque.obras_disponiveis.get(self.id) > 0
        
    def __str__(self):
        return f"{self.titulo} - ({self.ano})."  

class Usuario(BaseEntity):
    
    def __init__(self, nome:str, email:str):
        super().__init__()
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        return self.nome.lower() < other.nome.lower()

    def __str__(self):
        return self.nome

class Emprestimo(BaseEntity):

    emprestimos = []

    def __init__(self, obra:Obra, usuario:Usuario):
        super().__init__()
        self.obra = obra
        self.usuario = usuario
        self.data_retirada = datetime.datetime.now().strftime(format_data)
        self.data_prev_devol = None

        Emprestimo.emprestimos.append(self)

    def marcar_devolucao(self, data_dev_real):
        self.data_prev_devol = datetime.datetime.strptime(self.data_retirada, format_data).date() + datetime.timedelta(days=data_dev_real)

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
    