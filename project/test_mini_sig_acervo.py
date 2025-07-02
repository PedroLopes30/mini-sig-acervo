from models.models import Obra, Usuario
from models.core import Acervo
from datetime import date, timedelta
from rich.console import Console

console = Console()

acervo = Acervo()
livro = Obra("POO Essencial", "Ana Silva", 2025, "Livro", 2)
joao  = Usuario("João", "joao@example.com")

acervo += livro                # adiciona exemplar
acervo += livro                # adiciona exemplar
emp = acervo.emprestar(livro, joao)  # empresta

# simula atraso de 3 dias
after3 = date.today() + timedelta(days=3)
print("Multa:", acervo.valor_multa(emp, after3))

console.print(acervo.relatorio_inventario())