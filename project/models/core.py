# Imports
from models.models import Obra, Usuario, Emprestimo, format_data
import datetime
from rich.table import Table

# Classes

class Acervo:
    """
    Gerencia o acervo de obras disponíveis para empréstimo.
    """

    def __init__(self):
        """
        Inicializa o dicionário de obras disponíveis.
        """
        self.obras_disponiveis = dict()

    def __iadd__(self, obra:Obra):
        """
        Adiciona uma unidade de uma obra ao acervo.

        Args:
            obra (Obra): Obra a ser adicionada.

        Returns:
            Acervo: Instância atualizada do acervo.
        """
        self.__validar_obra(obra)

        if obra.quantidade > 0:
            self.obras_disponiveis[obra.id] = self.obras_disponiveis.get(obra.id, 0) + 1
            obra.quantidade -= 1

            return self

        print("Não foi possível realizar essa função. Sem estoque dessa obra.")
        return self

    def __isub__(self, obra):
        """
        Remove uma unidade da obra do acervo.

        Args:
            obra (Obra): Obra a ser removida.

        Returns:
            Acervo: Instância atualizada do acervo.
        """
        self.__validar_obra(obra)
        
        if obra.disponivel(self):
            self.obras_disponiveis[obra.id] -= 1
            obra.quantidade += 1
            if self.obras_disponiveis[obra.id] == 0: self.obras_disponiveis.pop(obra.id)

        return self

    def adicionar(self, obra):
        """
        Interface pública para adicionar obra ao acervo.

        Args:
            obra (Obra): Obra a ser adicionada.
        """
        self += obra

    def remover(self, obra):
        """
        Interface pública para remover obra do acervo.

        Args:
            obra (Obra): Obra a ser removida.
        """
        self -= obra

    def emprestar(self, obra:Obra, usuario:Usuario, dias=7):
        """
        Realiza o empréstimo de uma obra para um usuário.

        Args:
            obra (Obra): Obra a ser emprestada.
            usuario (Usuario): Usuário que recebe o empréstimo.
            dias (int, opcional): Prazo para devolução. Default é 7 dias.

        Returns:
            Emprestimo: Instância do empréstimo criado.

        Raises:
            ValueError: Caso não haja estoque disponível.
        """
        self.__validar_obra(obra)
        if not obra.disponivel(self):
            raise ValueError("Sem estoque da obra.")
        
        self.remover(obra)
        obra.quantidade -= 1

        emprestimo = Emprestimo(obra, usuario)
        emprestimo.marcar_devolucao(dias)

        return emprestimo

    def devolver(self, emprestimo:Emprestimo, data_dev=None):
        """
        Realiza a devolução de uma obra emprestada.

        Args:
            emprestimo (Emprestimo): Empréstimo a ser finalizado.
            data_dev (str, opcional): Data de devolução. Se None, usa a data atual.
        """
        if data_dev:
            data_dev = datetime.datetime.strptime(data_dev, format_data).date()
        else:
            data_dev = datetime.datetime.today() 
        
        valor_multa = self.valor_multa(emprestimo, data_dev)
        if valor_multa:
            print(f"Sua multa é de R${valor_multa} pelo atraso.")
        print("Obrigado pela devolução!")
        
        self.adicionar(emprestimo.obra)
        Emprestimo.emprestimos.remove(emprestimo)

        return

    def renovar(self, emprestimo, dias_extras):
        """
        Renova o empréstimo por mais alguns dias.

        Args:
            emprestimo (Emprestimo): Empréstimo a ser renovado.
            dias_extras (int): Dias adicionais.
        """
        dias = ((emprestimo.data_prev_devol - emprestimo.data_retirada).days + dias_extras)
        emprestimo.marcar_devolucao(dias)

    def valor_multa(self, emprestimo, data_ref):
        """
        Calcula o valor da multa por atraso.

        Args:
            emprestimo (Emprestimo): Empréstimo analisado.
            data_ref (date): Data de referência para cálculo.

        Returns:
            float | None: Valor da multa ou None se não houver atraso.
        """
        atraso = emprestimo.dias_atraso(data_ref)     
        if atraso > 0: 
            return float(atraso * 1)
        return 

    def relatorio_inventario(self):
        """
        Gera uma tabela com o inventário das obras disponíveis no acervo.

        Returns:
            Table: Tabela formatada com dados das obras.
        """
        table = Table(title="Obras", show_lines=True)

        table.add_column("Obra", justify="left", style="white", no_wrap=True)
        table.add_column("Autor", justify="left", style="yellow", no_wrap=True)
        table.add_column("Ano", justify="left", style="green", no_wrap=True)
        table.add_column("Categoria", justify="left", style="cyan", no_wrap=True)
        table.add_column("Estoque do Acervo", justify="left", style="red", no_wrap=True)

        for obra in Obra.obras:
            for obra_acervo, estoque  in self.obras_disponiveis.items():
                if obra.id == obra_acervo:
                    table.add_row(obra.titulo, obra.autor, str(obra.ano), obra.categoria, str(estoque))

        return table

    def relatorio_debito(self):
        """
        Gera uma tabela com os usuários que possuem débitos por atraso.

        Returns:
            Table: Tabela de débitos e multas.
        """
        table = Table(title="Débitos", show_lines=True)

        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Multa", justify="left", style="red", no_wrap=True)

        for emprestimo in Emprestimo.emprestimos:
            if self.valor_multa(emprestimo, datetime.date.today()):
                table.add_row(emprestimo.usuario.nome, emprestimo.obra.titulo, f"R$ {str(self.valor_multa(emprestimo, datetime.date.today()))}")

        return table

    def historico_usuario(self, usuario:Usuario):
        """
        Gera uma tabela com o histórico de empréstimos de um usuário.

        Args:
            usuario (Usuario): Usuário para o qual gerar o histórico.

        Returns:
            Table: Tabela com os empréstimos do usuário.
        """
        table = Table(title=f"Histórico de {usuario.nome}", show_lines=True)

        table.add_column("Usuário", justify="left", style="white", no_wrap=True)
        table.add_column("Obra", justify="left", style="cyan", no_wrap=True)
        table.add_column("Data de Retirada", justify="left", style="green", no_wrap=True)
        table.add_column("Data de Devolução", justify="left", style="purple", no_wrap=True)

        for emprestimo in Emprestimo.emprestimos:
            if usuario == emprestimo.usuario:
                table.add_row(usuario.nome, emprestimo.obra.titulo, str(emprestimo.data_retirada), str(emprestimo.data_prev_devol))
        return table

    def __validar_obra(self, obra:Obra):
        """
        Verifica se o objeto é uma instância da classe Obra.

        Args:
            obra (Obra): Objeto a ser validado.

        Raises:
            TypeError: Se o objeto não for do tipo Obra.
        """
        if not isinstance(obra, Obra):
            raise TypeError("Esse objeto não pertence a classe Obra.")
        return
