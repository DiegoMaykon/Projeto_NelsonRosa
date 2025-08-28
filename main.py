# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from clientes import TelaClientes
from acessorios import TelaAcessorios
from pedidos import TelaPedidos

class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos - Projeto Nelson Rosa")
        self.setGeometry(200, 200, 400, 300)
        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()

        # Botão Clientes
        btn_clientes = QPushButton("Clientes")
        btn_clientes.clicked.connect(self.abrir_clientes)
        layout.addWidget(btn_clientes)

        # Botão Acessórios
        btn_acessorios = QPushButton("Acessórios")
        btn_acessorios.clicked.connect(self.abrir_acessorios)
        layout.addWidget(btn_acessorios)

        # Botão Pedidos
        btn_pedidos = QPushButton("Pedidos")
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        layout.addWidget(btn_pedidos)

        # Botão Sair
        btn_sair = QPushButton("Sair")
        btn_sair.clicked.connect(self.close)
        layout.addWidget(btn_sair)

        # Configura container central
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # --------------------------
    # Ações dos botões
    # --------------------------
    def abrir_clientes(self):
        # Cria e mostra a janela de clientes
        self.tela_clientes = TelaClientes()
        self.tela_clientes.show()

    def abrir_acessorios(self):
        # Cria e mostra a janela de acessórios
        self.tela_acessorios = TelaAcessorios()
        self.tela_acessorios.show()

    def abrir_pedidos(self):
        # Cria e mostra a janela de pedidos
        self.tela_pedidos = TelaPedidos()
        self.tela_pedidos.show()

# --------------------------
# Execução da aplicação
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
