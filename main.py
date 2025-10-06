import sys
import os
import shutil
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QDesktopWidget, QWidget,
    QHBoxLayout, QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from clientes import TelaClientes
from acessorios import TelaAcessorios
from pedidos import TelaPedidos


# ==============================
# 🔹 Diretório fixo de dados do sistema
# ==============================
PASTA_DADOS = os.path.join(os.getenv("APPDATA"), "SistemaGestao")
os.makedirs(PASTA_DADOS, exist_ok=True)

# Caminhos completos dos arquivos JSON
ARQUIVO_CLIENTES = os.path.join(PASTA_DADOS, "clientes.json")
ARQUIVO_ACESSORIOS = os.path.join(PASTA_DADOS, "acessorios.json")
ARQUIVO_PEDIDOS = os.path.join(PASTA_DADOS, "pedidos.json")

# Lista principal usada para backup
ARQUIVOS_SISTEMA = [ARQUIVO_CLIENTES, ARQUIVO_ACESSORIOS, ARQUIVO_PEDIDOS]

# Número máximo de backups a manter
MAX_BACKUPS = 1


# ==============================
# 🔹 Classe Principal
# ==============================
class TelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos AL Metais - Nelson Rosa - V1.0")

        # Caminho da imagem no mesmo diretório do script/executável
        diretorio_atual = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.caminho_fundo = os.path.join(diretorio_atual, "logopreta2.png")

        self.inicializar_ui()
        self.inicializar_backup_automatico()  # Ativa backup automático diário
        self.ajustar_resolucao()

    # ==============================
    # Ajuste de resolução
    # ==============================
    def ajustar_resolucao(self):
        """Ajusta a janela conforme a resolução da tela e inicia em modo tela cheia"""
        tela = QDesktopWidget().screenGeometry()
        largura = tela.width()
        altura = tela.height()
        self.setGeometry(0, 0, largura, altura)

    # ==============================
    # Interface
    # ==============================
    def inicializar_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout_principal = QHBoxLayout()
        central_widget.setLayout(self.layout_principal)

        # ===== Fundo da tela =====
        self.label_fundo = QLabel(central_widget)
        self.label_fundo.setScaledContents(True)
        self.label_fundo.lower()  # Mantém o fundo atrás dos botões

        if os.path.exists(self.caminho_fundo):
            self.pixmap_original = QPixmap(self.caminho_fundo)
            self.atualizar_fundo()
        else:
            print(f"⚠️ Imagem de fundo não encontrada: {self.caminho_fundo}")

        # ===== Estilo dos botões =====
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

        # ===== Botões principais =====
        btn_clientes = QPushButton("Clientes")
        btn_acessorios = QPushButton("Itens")
        btn_pedidos = QPushButton("Pedidos")
        btn_backup = QPushButton("Backup")
        btn_restaurar = QPushButton("Restaurar Backup")
        btn_sair = QPushButton("Sair")

        for btn in [btn_clientes, btn_acessorios, btn_pedidos, btn_backup, btn_restaurar, btn_sair]:
            btn.setStyleSheet(estilo_botoes)

        # ===== Layout de botões =====
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

        self.layout_principal.addStretch()
        self.layout_principal.addLayout(layout_botoes)

        # ===== Conectar botões =====
        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_acessorios.clicked.connect(self.abrir_acessorios)
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        btn_backup.clicked.connect(self.fazer_backup)
        btn_restaurar.clicked.connect(self.restaurar_backup)
        btn_sair.clicked.connect(self.close)

    # ==============================
    # Fundo dinâmico
    # ==============================
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.atualizar_fundo()

    def atualizar_fundo(self):
        """Faz o fundo preencher toda a tela (sem bordas)"""
        if hasattr(self, "pixmap_original"):
            scaled_pixmap = self.pixmap_original.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            self.label_fundo.setPixmap(scaled_pixmap)
            self.label_fundo.resize(self.size())

    # ==============================
    # Telas
    # ==============================
    def abrir_clientes(self):
        self.tela_clientes = TelaClientes()
        self.tela_clientes.show()

    def abrir_acessorios(self):
        self.tela_acessorios = TelaAcessorios()
        self.tela_acessorios.show()

    def abrir_pedidos(self):
        self.tela_pedidos = TelaPedidos()
        self.tela_pedidos.show()

    # ==============================
    # Backup manual
    # ==============================
    def fazer_backup(self):
        pasta_backup = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Backup")
        if not pasta_backup:
            return
        self.realizar_backup(pasta_backup)
        QMessageBox.information(self, "Backup Concluído", f"Backup realizado com sucesso em:\n{pasta_backup}")

    # ==============================
    # Restauração manual
    # ==============================
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
            nome = os.path.basename(arquivo)
            arquivo_backup = os.path.join(pasta_backup, nome)
            if os.path.exists(arquivo_backup):
                shutil.copy2(arquivo_backup, arquivo)
        QMessageBox.information(self, "Restauração Concluída", "Backup restaurado com sucesso!\nReinicie o sistema para atualizar as telas.")

    # ==============================
    # Backup automático diário
    # ==============================
    def inicializar_backup_automatico(self):
        self.pasta_backup_automatica = os.path.join(PASTA_DADOS, "backups")
        os.makedirs(self.pasta_backup_automatica, exist_ok=True)
        self.backup_automatico()
        self.timer_backup = QTimer()
        self.timer_backup.timeout.connect(self.backup_automatico)
        self.timer_backup.start(24 * 60 * 60 * 1000)  # 1 dia

    def backup_automatico(self):
        self.realizar_backup(self.pasta_backup_automatica, mostrar_msg=False)
        self.limpar_backups_antigos(self.pasta_backup_automatica)
        print(f"Backup automático realizado em: {self.pasta_backup_automatica}")

    # ==============================
    # Funções de backup
    # ==============================
    def realizar_backup(self, pasta_backup, mostrar_msg=True):
        os.makedirs(pasta_backup, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pasta_destino = os.path.join(pasta_backup, f"backup_{timestamp}")
        os.makedirs(pasta_destino, exist_ok=True)
        for arquivo in ARQUIVOS_SISTEMA:
            if os.path.exists(arquivo):
                shutil.copy2(arquivo, pasta_destino)
        if mostrar_msg:
            print(f"Backup realizado em: {pasta_destino}")

    def limpar_backups_antigos(self, pasta_backup):
        if not os.path.exists(pasta_backup):
            return
        backups = [d for d in os.listdir(pasta_backup) if os.path.isdir(os.path.join(pasta_backup, d))]
        backups.sort()
        while len(backups) > MAX_BACKUPS:
            antigo = backups.pop(0)
            caminho_antigo = os.path.join(pasta_backup, antigo)
            shutil.rmtree(caminho_antigo)
            print(f"Backup antigo removido: {caminho_antigo}")


# ==============================
# Execução
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
