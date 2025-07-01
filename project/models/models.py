# Imports
import uuid
import datetime
from rich.table import Table
from rich.console import Console

# Classes
class BaseEntity():
    def __init__(self):
        self.id = self._gerar_id()
        self.creation_date = datetime.date.today()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()   
    
class Obra(BaseEntity):
    def __init__(self, titulo, autor, ano, categoria, quantidade=1):
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

    def disponivel(self, estoque):
        for obra_acervo in estoque:
            if obra_acervo["obra"] == self: return True
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
        self.__emprestimos = []

    def __verificar_obra(self, obra):
        self.__valida_obra(obra)

        if obra.disponivel(self.acervo):
            for obra_acervo in self.acervo:
                if obra_acervo["obra"] == obra:
                    return obra_acervo
        return False

    def __iadd__(self, obra):
        obra_acervo = self.__verificar_obra(obra)
        if obra_acervo:
            if obra.quantidade >= 1:
                obra.quantidade -= 1
                obra_acervo["estoque"] += 1
                return self
            return "Sem obra disponível."
        
        self.adicionar(obra)
        return self

    def __isub__(self, obra):
        obra_acervo = self.__verificar_obra(obra)
        if obra_acervo:
            if obra_acervo["estoque"] >= 1:
                if obra_acervo["estoque"] == 1:
                    self.remover(obra_acervo)
                else:
                    obra_acervo["estoque"] -=1
                obra.quantidade += 1
        return self
    
    def adicionar(self, obra):
        if obra.quantidade >= 1:
            self.acervo.append({"obra": obra, "estoque": 1})
            obra.quantidade -= 1

    def remover(self, obra_acervo):
        self.acervo.remove(obra_acervo)

    def emprestar(self, obra, usuario, dias=7):
        self.__valida_obra(obra)
        if obra.disponivel(self.acervo):
            self -= obra
            obra.quantidade -= 1
            emprestimo = Emprestimo(obra, usuario)
            emprestimo.marcar_devolucao(dias)
            self.__emprestimos.append(emprestimo)
            return emprestimo
        raise ValueError("Sem estoque da obra.")
    
    def devolver(self, emprestimo, data_dev):
        data_dev = datetime.datetime.strptime(data_dev, "%Y-%m-%d").date()
        valor_multa = self.valor_multa(emprestimo, data_dev)
        if valor_multa:
            print(f"Sua multa é de R${valor_multa} pelo atraso.")
        print("Obrigado pela devolução!")
        
        self.__iadd__(emprestimo.obra)
        self.__emprestimos.remove(emprestimo)

        return

    def renovar(self, emprestimo, dias_extras):
        dias = ((emprestimo.data_prev_devol - emprestimo.data_retirada).days + dias_extras)
        emprestimo.marcar_devolucao(dias)
        
    def valor_multa(self, emprestimo, data_ref):
        atraso = emprestimo.dias_atraso(data_ref)     
        if atraso > 0: 
            return float(atraso * 1)
        return 

    def relatorio_inventario(self):
        # Criação tabela
        table = Table(title="Obras", show_lines=True)

        # Criação colunas
        table.add_column("Obra", justify="left", style="white", no_wrap=True)
        table.add_column("Autor", justify="left", style="yellow", no_wrap=True)
        table.add_column("Ano", justify="left", style="green", no_wrap=True)
        table.add_column("Categoria", justify="left", style="cyan", no_wrap=True)
        table.add_column("Estoque do Acervo", justify="left", style="red", no_wrap=True)

        # Criação linhas
        for obra_acervo in self.acervo:
            obra = obra_acervo["obra"]
            table.add_row(obra.titulo, obra.autor, str(obra.ano), obra.categoria, str(obra_acervo["estoque"]))

        return table

    def relatorio_debito(self):
        # Criação tabela
        table = Table(title="Débitos", show_lines=True)

        # Criação colunas
        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Multa", justify="left", style="red", no_wrap=True)

        # Criação linhas
        for emprestimo in self.__emprestimos:
            if self.valor_multa(emprestimo, datetime.date.today()):
                table.add_row(emprestimo.usuario.nome, emprestimo.obra.titulo, f"R$ {str(self.valor_multa(emprestimo, datetime.date.today()))}")

        return table

    def historico_usuario(self, usuario):
        # Criação tabela
        table = Table(title=f"Histórico de {usuario.nome}", show_lines=True)

        # Criação colunas
        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Data de Retirada", justify="left", style="green", no_wrap=True)

        # Criação linhas
        for emprestimo in self.__emprestimos:
            if usuario == emprestimo.usuario:
                table.add_row(usuario.nome, emprestimo.obra.titulo, str(emprestimo.data_retirada))
        
        return table

    def __valida_obra(self, obra):
        if not isinstance(obra, Obra):
            raise TypeError("Esse objeto não pertence a classe Obra.")
        return
