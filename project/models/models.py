# Imports
import uuid
import datetime

# Variaveis
format_data = '%d-%m-%Y'

# Classes
class BaseEntity():
    """
    Classe base para outras entidades, fornecendo um ID único e data de criação.
    """

    def __init__(self):
        """
        Inicializa a entidade com um ID único e registra a data de criação atual.
        """
        self.id = self._gerar_id()
        self.creation_date = datetime.datetime.now().strftime(format_data)

    def __eq__(self, other):
        """
        Compara duas instâncias pelo ID e tipo de classe.

        Args:
            other: Outro objeto para comparar.

        Returns:
            bool: True se forem da mesma classe e tiverem o mesmo ID, False caso contrário.
        """
        if not hasattr(other, 'id'):
            return False
        return self.__class__ == other.__class__ and self.id == other.id

    def _gerar_id(self):
        """
        Gera um UUID para a instância.

        Returns:
            UUID: Identificador único.
        """
        return uuid.uuid4()


class Obra(BaseEntity):
    """
    Representa uma obra literária no sistema.
    """

    obras = []

    def __init__(self, titulo:str, autor:str, ano, categoria:str, quantidade=1):
        """
        Inicializa uma nova obra com seus atributos e a adiciona à lista global de obras.

        Args:
            titulo (str): Título da obra.
            autor (str): Autor da obra.
            ano: Ano de publicação.
            categoria (str): Categoria da obra.
            quantidade (int, opcional): Quantidade de exemplares. Default é 1.
        """
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

        Obra.obras.append(self)

    def disponivel(self, estoque):
        """
        Verifica se a obra está disponível no estoque.

        Args:
            estoque (Acervo): Instância de Acervo.

        Returns:
            bool: True se houver exemplares disponíveis, False caso contrário.
        """
        if not hasattr(estoque, 'obras_disponiveis'):
            return False
        
        return estoque.obras_disponiveis.get(self.id) > 0

    def __str__(self):
        """
        Retorna uma representação textual da obra.

        Returns:
            str: Título e ano da obra.
        """
        return f"{self.titulo} - ({self.ano})."  


class Usuario(BaseEntity):
    """
    Representa um usuário do sistema.
    """

    def __init__(self, nome:str, email:str):
        """
        Inicializa um novo usuário.

        Args:
            nome (str): Nome do usuário.
            email (str): E-mail do usuário.
        """
        super().__init__()
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        """
        Compara usuários alfabeticamente pelo nome (case-insensitive).

        Args:
            other (Usuario): Outro usuário para comparação.

        Returns:
            bool: True se o nome for lexicograficamente menor.
        """
        return self.nome.lower() < other.nome.lower()

    def __str__(self):
        """
        Representação textual do usuário.

        Returns:
            str: Nome do usuário.
        """
        return self.nome
    

class Emprestimo(BaseEntity):
    """
    Representa um empréstimo de uma obra a um usuário.
    """

    emprestimos = []

    def __init__(self, obra:Obra, usuario:Usuario):
        """
        Inicializa um novo empréstimo com a obra, o usuário e a data de retirada.

        Args:
            obra (Obra): Obra emprestada.
            usuario (Usuario): Usuário que realizou o empréstimo.
        """
        super().__init__()
        self.obra = obra
        self.usuario = usuario
        self.data_retirada = datetime.datetime.now().strftime(format_data)
        self.data_prev_devol = None

        Emprestimo.emprestimos.append(self)

    def marcar_devolucao(self, data_dev_real:int):
        """
        Define a data prevista de devolução com base em um número de dias.

        Args:
            data_dev_real (int): Quantidade de dias para devolução.
        """
        self.data_prev_devol = datetime.datetime.strptime(self.data_retirada, format_data).date() + datetime.timedelta(days=data_dev_real)

    def dias_atraso(self, data_ref):
        """
        Calcula o número de dias de atraso com base em uma data de referência.

        Args:
            data_ref (date): Data atual ou de referência.

        Returns:
            int | None: Dias de atraso ou None se não houver previsão de devolução.
        """
        if self.data_prev_devol:
            atraso = (data_ref - self.data_prev_devol).days
            if atraso > 0:
                return atraso
            else:
                return 0
        return None

    def __str__(self):
        """
        Retorna uma descrição do empréstimo.

        Returns:
            str: Detalhes da obra emprestada e do usuário.
        """
        return f"-> {self.obra.titulo} - Data de retirada: {self.data_retirada}\n - Data prevista de devolução: {self.data_prev_devol}\n - Usuário: {self.usuario.nome}"
