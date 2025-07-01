import uuid
import datetime
from rich.table import Table
from rich.console import Console

class BaseEntity:
    """Classe base para entidades com ID único e data de criação."""

    def __init__(self):
        """Inicializa a entidade com um ID UUID e a data atual."""
        self.id = self._gerar_id()
        self.creation_date = datetime.date.today()

    def __eq__(self, other):
        """Verifica se duas entidades são iguais.

        Args:
            other (BaseEntity): Outra entidade para comparar.

        Returns:
            bool: True se forem da mesma classe e IDs iguais.
        """
        return self.__class__ == other.__class__ and self.id == other.id

    def _gerar_id(self):
        """Gera um ID único.

        Returns:
            uuid.UUID: Identificador único.
        """
        return uuid.uuid4()

class Obra(BaseEntity):
    """Representa uma obra no sistema."""

    def __init__(self, titulo, autor, ano, categoria, quantidade=1):
        """Inicializa uma nova obra.

        Args:
            titulo (str): Título da obra.
            autor (str): Nome do autor.
            ano (int): Ano de publicação.
            categoria (str): Gênero ou categoria da obra.
            quantidade (int): Quantidade disponível. Defaults to 1.
        """
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

    def disponivel(self, estoque):
        """Verifica se a obra está presente no estoque do acervo.

        Args:
            estoque (list): Lista de obras no acervo.

        Returns:
            bool: True se a obra estiver disponível.
        """
        for obra_acervo in estoque:
            if obra_acervo["obra"] == self:
                return True
        return False

    def __str__(self):
        """Retorna a representação em string da obra."""
        return f"{self.titulo} ({self.ano})."

class Usuario(BaseEntity):
    """Representa um usuário do sistema."""

    def __init__(self, nome, email):
        """Inicializa um novo usuário.

        Args:
            nome (str): Nome do usuário.
            email (str): Endereço de e-mail.
        """
        super().__init__()
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        """Compara usuários por ordem alfabética do nome."""
        return self.nome.lower() < other.nome.lower()

    def __str__(self):
        """Retorna a representação em string do usuário."""
        return f"{self.nome}"

class Emprestimo(BaseEntity):
    """Representa um empréstimo de uma obra para um usuário."""

    def __init__(self, obra, usuario):
        """Inicializa um novo empréstimo.

        Args:
            obra (Obra): Obra emprestada.
            usuario (Usuario): Usuário que realizou o empréstimo.
        """
        super().__init__()
        self.obra = obra
        self.usuario = usuario
        self.data_retirada = datetime.date.today()
        self.data_prev_devol = None

    def marcar_devolucao(self, data_dev_real):
        """Define a data prevista de devolução.

        Args:
            data_dev_real (int): Número de dias para devolução.

        Returns:
            datetime.date: Data prevista de devolução.
        """
        self.data_prev_devol = self.data_retirada + datetime.timedelta(days=data_dev_real)
        return self.data_prev_devol

    def dias_atraso(self, data_ref):
        """Calcula os dias de atraso na devolução.

        Args:
            data_ref (datetime.date): Data de referência para cálculo.

        Returns:
            int or None: Número de dias de atraso, ou None se não há previsão.
        """
        if self.data_prev_devol:
            atraso = (data_ref - self.data_prev_devol).days
            return atraso if atraso > 0 else 0
        return None

    def __str__(self):
        """Retorna uma string com os detalhes do empréstimo."""
        return (f"-> {self.obra.titulo} - Data de retirada: {self.data_retirada}\n"
                f" - Data prevista de devolução: {self.data_prev_devol}\n"
                f" - Usuário: {self.usuario.nome}")

class Acervo:
    """Gerencia o acervo de obras e os empréstimos."""

    def __init__(self):
        """Inicializa o acervo e a lista de empréstimos."""
        self.acervo = []
        self.__emprestimos = []

    def __verificar_obra(self, obra):
        """Verifica se a obra está no acervo.

        Args:
            obra (Obra): Obra a ser verificada.

        Returns:
            dict or bool: Registro da obra ou False se não existir.
        """
        self.__valida_obra(obra)
        if obra.disponivel(self.acervo):
            for obra_acervo in self.acervo:
                if obra_acervo["obra"] == obra:
                    return obra_acervo
        return False

    def __iadd__(self, obra):
        """Adiciona ou incrementa estoque da obra no acervo.

        Args:
            obra (Obra): Obra a ser adicionada.

        Returns:
            Acervo or str: O acervo atualizado ou mensagem de erro.
        """
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
        """Remove uma unidade da obra do acervo.

        Args:
            obra (Obra): Obra a ser removida.

        Returns:
            Acervo: O acervo atualizado.
        """
        obra_acervo = self.__verificar_obra(obra)
        if obra_acervo and obra_acervo["estoque"] >= 1:
            if obra_acervo["estoque"] == 1:
                self.remover(obra_acervo)
            else:
                obra_acervo["estoque"] -= 1
            obra.quantidade += 1
        return self

    def adicionar(self, obra):
        """Adiciona uma nova obra ao acervo.

        Args:
            obra (Obra): Obra a ser adicionada.
        """
        if obra.quantidade >= 1:
            self.acervo.append({"obra": obra, "estoque": 1})
            obra.quantidade -= 1

    def remover(self, obra_acervo):
        """Remove uma obra do acervo.

        Args:
            obra_acervo (dict): Registro da obra a ser removida.
        """
        self.acervo.remove(obra_acervo)

    def emprestar(self, obra, usuario, dias=7):
        """Registra um novo empréstimo.

        Args:
            obra (Obra): Obra a ser emprestada.
            usuario (Usuario): Usuário que irá pegar a obra.
            dias (int): Dias para devolução. Defaults to 7.

        Returns:
            Emprestimo: Objeto representando o empréstimo.

        Raises:
            ValueError: Se a obra não estiver disponível.
        """
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
        """Registra a devolução de uma obra.

        Args:
            emprestimo (Emprestimo): Empréstimo a ser encerrado.
            data_dev (str): Data de devolução em formato "YYYY-MM-DD".
        """
        data_dev = datetime.datetime.strptime(data_dev, "%Y-%m-%d").date()
        valor_multa = self.valor_multa(emprestimo, data_dev)
        if valor_multa:
            print(f"Sua multa é de R${valor_multa} pelo atraso.")
        print("Obrigado pela devolução!")

        self.__iadd__(emprestimo.obra)
        self.__emprestimos.remove(emprestimo)

    def renovar(self, emprestimo, dias_extras):
        """Renova a data de devolução de um empréstimo.

        Args:
            emprestimo (Emprestimo): Empréstimo a ser renovado.
            dias_extras (int): Dias extras para renovar.
        """
        dias = (emprestimo.data_prev_devol - emprestimo.data_retirada).days + dias_extras
        emprestimo.marcar_devolucao(dias)

    def valor_multa(self, emprestimo, data_ref):
        """Calcula o valor da multa por atraso.

        Args:
            emprestimo (Emprestimo): Empréstimo em questão.
            data_ref (datetime.date): Data usada como referência.

        Returns:
            float or None: Valor da multa ou None se não houver atraso.
        """
        atraso = emprestimo.dias_atraso(data_ref)
        if atraso > 0:
            return float(atraso * 1)
        return

    def relatorio_inventario(self):
        """Gera um relatório com o inventário atual.

        Returns:
            Table: Tabela com as obras disponíveis.
        """
        table = Table(title="Obras", show_lines=True)
        table.add_column("Obra", justify="left", style="white", no_wrap=True)
        table.add_column("Autor", justify="left", style="yellow", no_wrap=True)
        table.add_column("Ano", justify="left", style="green", no_wrap=True)
        table.add_column("Categoria", justify="left", style="cyan", no_wrap=True)
        table.add_column("Estoque do Acervo", justify="left", style="red", no_wrap=True)

        for obra_acervo in self.acervo:
            obra = obra_acervo["obra"]
            table.add_row(obra.titulo, obra.autor, str(obra.ano), obra.categoria, str(obra_acervo["estoque"]))
        return table

    def relatorio_debito(self):
        """Gera um relatório com os usuários que possuem débitos.

        Returns:
            Table: Tabela com usuários e multas.
        """
        table = Table(title="Débitos", show_lines=True)
        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Multa", justify="left", style="red", no_wrap=True)

        for emprestimo in self.__emprestimos:
            multa = self.valor_multa(emprestimo, datetime.date.today())
            if multa:
                table.add_row(emprestimo.usuario.nome, emprestimo.obra.titulo, f"R$ {multa}")
        return table

    def historico_usuario(self, usuario):
        """Exibe o histórico de empréstimos de um usuário.

        Args:
            usuario (Usuario): Usuário a ser consultado.

        Returns:
            Table: Tabela com obras emprestadas.
        """
        table = Table(title=f"Histórico de {usuario.nome}", show_lines=True)
        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Data de Retirada", justify="left", style="green", no_wrap=True)

        for emprestimo in self.__emprestimos:
            if usuario == emprestimo.usuario:
                table.add_row(usuario.nome, emprestimo.obra.titulo, str(emprestimo.data_retirada))
        return table

    def __valida_obra(self, obra):
        """Valida se um objeto é instância da classe Obra.

        Args:
            obra (object): Objeto a ser validado.

        Raises:
            TypeError: Se não for instância de Obra.
        """
        if not isinstance(obra, Obra):
            raise TypeError("Esse objeto não pertence à classe Obra.")
        return