import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from clientes import TelaClientes
from acessorios import TelaAcessorios
from pedidos import TelaPedidos


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

        # Layout principal horizontal (2 colunas: esquerda vazia, direita botões)
        layout_principal = QHBoxLayout()
        central_widget.setLayout(layout_principal)

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

        # Aplica estilo
        for btn in [btn_clientes, btn_acessorios, btn_pedidos, btn_sair]:
            btn.setStyleSheet(estilo_botoes)

        # Layout de botões (coluna da direita)
        layout_botoes = QVBoxLayout()
        layout_botoes.addStretch()
        layout_botoes.addWidget(btn_clientes)
        layout_botoes.addSpacing(15)
        layout_botoes.addWidget(btn_acessorios)
        layout_botoes.addSpacing(15)
        layout_botoes.addWidget(btn_pedidos)
        layout_botoes.addSpacing(15)
        layout_botoes.addWidget(btn_sair)
        layout_botoes.addStretch()

        # Coloca no layout principal (esquerda vazia, direita botões)
        layout_principal.addStretch()  # parte vazia à esquerda
        layout_principal.addLayout(layout_botoes)  # botões na direita

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
