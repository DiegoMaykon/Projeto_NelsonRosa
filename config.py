import os
from pathlib import Path

def criar_pasta_dados():
    """Cria a pasta de dados dentro do diretório do projeto."""
    pasta_base = Path(__file__).parent  # mesmo diretório do projeto
    pasta_dados = pasta_base / "dados"
    pasta_dados.mkdir(parents=True, exist_ok=True)
    return str(pasta_dados)

# Caminho base de dados
PASTA_DADOS = criar_pasta_dados()

# Caminhos completos dos arquivos JSON
ARQUIVO_CLIENTES = os.path.join(PASTA_DADOS, "clientes.json")
ARQUIVO_ACESSORIOS = os.path.join(PASTA_DADOS, "acessorios.json")
ARQUIVO_PEDIDOS = os.path.join(PASTA_DADOS, "pedidos.json")

# Lista principal usada para backup
ARQUIVOS_SISTEMA = [ARQUIVO_CLIENTES, ARQUIVO_ACESSORIOS, ARQUIVO_PEDIDOS]

