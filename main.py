import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from clientes import TelaClientes
from acessorios import TelaAcessorios
from pedidos import TelaPedidos
from PyQt5.QtGui import QPalette, QBrush, QPixmap

class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos - Projeto Nelson Rosa")
        self.setGeometry(200, 200, 1024, 768)

        # Monta a interface
        self.inicializar_ui()

    def inicializar_ui(self):
        # Cria o widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal (centralizado verticalmente)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Caminho da imagem de fundo
        caminho_fundo = r"D:\Projeto_NelsonRosa\logopreta.png"
        if os.path.exists(caminho_fundo):
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(QPixmap(caminho_fundo)))
            self.setPalette(palette)
        else:
            print("⚠️ Imagem de fundo não encontrada:", caminho_fundo)

        # Estilo dos botões
        estilo_botoes = """
            QPushButton {
                background-color: rgba(0, 0, 0, 100); 
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 180);
            }
        """

        # Botões principais
        btn_clientes = QPushButton("Clientes")
        btn_acessorios = QPushButton("Acessórios")
        btn_pedidos = QPushButton("Pedidos")
        btn_sair = QPushButton("Sair")

        # Aplica o estilo nos botões
        for btn in [btn_clientes, btn_acessorios, btn_pedidos, btn_sair]:
            btn.setStyleSheet(estilo_botoes)
            layout.addWidget(btn)

        # Conectar botões às telas
        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_acessorios.clicked.connect(self.abrir_acessorios)
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        btn_sair.clicked.connect(self.close)

    # Métodos para abrir telas
    def abrir_clientes(self):
        self.tela_clientes = TelaClientes()
        self.tela_clientes.show()

    def abrir_acessorios(self):
        self.tela_acessorios = TelaAcessorios()
        self.tela_acessorios.show()

    def abrir_pedidos(self):
        self.tela_pedidos = TelaPedidos()
        self.tela_pedidos.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
