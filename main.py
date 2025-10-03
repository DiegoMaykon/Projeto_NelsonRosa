import sys
import os
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from clientes import TelaClientes
from acessorios import TelaAcessorios
from pedidos import TelaPedidos

# Arquivos principais do sistema
ARQUIVOS_SISTEMA = ["clientes.json", "acessorios.json", "pedidos.json"]

class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos - Projeto Nelson Rosa")
        self.setGeometry(200, 200, 1024, 768)
        self.inicializar_ui()

    def inicializar_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_principal = QHBoxLayout()
        central_widget.setLayout(layout_principal)

        # Fundo
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
        btn_backup = QPushButton("Backup")
        btn_restaurar = QPushButton("Restaurar Backup")
        btn_sair = QPushButton("Sair")

        for btn in [btn_clientes, btn_acessorios, btn_pedidos, btn_backup, btn_restaurar, btn_sair]:
            btn.setStyleSheet(estilo_botoes)

        # Layout de botões
        layout_botoes = QVBoxLayout()
        layout_botoes.addStretch()
        layout_botoes.addWidget(btn_clientes)
        layout_botoes.addSpacing(10)
        layout_botoes.addWidget(btn_acessorios)
        layout_botoes.addSpacing(10)
        layout_botoes.addWidget(btn_pedidos)
        layout_botoes.addSpacing(10)
        layout_botoes.addWidget(btn_backup)
        layout_botoes.addSpacing(10)
        layout_botoes.addWidget(btn_restaurar)
        layout_botoes.addSpacing(10)
        layout_botoes.addWidget(btn_sair)
        layout_botoes.addStretch()
        layout_principal.addStretch()
        layout_principal.addLayout(layout_botoes)

        # Conectar botões
        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_acessorios.clicked.connect(self.abrir_acessorios)
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        btn_backup.clicked.connect(self.fazer_backup)
        btn_restaurar.clicked.connect(self.restaurar_backup)
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

    # ----------------------------
    # Função de Backup
    # ----------------------------
    def fazer_backup(self):
        pasta_backup = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Backup")
        if not pasta_backup:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pasta_destino = os.path.join(pasta_backup, f"backup_{timestamp}")
        os.makedirs(pasta_destino, exist_ok=True)

        for arquivo in ARQUIVOS_SISTEMA:
            if os.path.exists(arquivo):
                shutil.copy2(arquivo, pasta_destino)

        QMessageBox.information(self, "Backup Concluído", f"Backup realizado com sucesso em:\n{pasta_destino}")

    # ----------------------------
    # Função de Restauração
    # ----------------------------
    def restaurar_backup(self):
        pasta_backup = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Backup")
        if not pasta_backup:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Restauração",
            "Deseja realmente restaurar este backup? Isso irá substituir os arquivos atuais.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        for arquivo in ARQUIVOS_SISTEMA:
            arquivo_backup = os.path.join(pasta_backup, arquivo)
            if os.path.exists(arquivo_backup):
                shutil.copy2(arquivo_backup, arquivo)

        QMessageBox.information(self, "Restauração Concluída", "Backup restaurado com sucesso!\nReinicie o sistema para atualizar as telas.")

# ----------------------------
# Execução do sistema
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
