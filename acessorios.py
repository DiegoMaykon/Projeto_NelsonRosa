import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)

ARQUIVO_ACESSORIOS = "acessorios.json"

def carregar_json():
    if not os.path.exists(ARQUIVO_ACESSORIOS):
        return []
    with open(ARQUIVO_ACESSORIOS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(dados):
    with open(ARQUIVO_ACESSORIOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# --------------------------
# Tela principal de acessórios
# --------------------------
class TelaAcessorios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Acessórios")
        self.setGeometry(250, 250, 700, 400)
        self.acessorios = carregar_json()
        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()

        # Inputs para novo acessório
        form_layout = QHBoxLayout()
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do acessório")
        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.input_nome)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Valor (R$)")
        form_layout.addWidget(QLabel("Valor:"))
        form_layout.addWidget(self.input_valor)

        btn_adicionar = QPushButton("Adicionar")
        btn_adicionar.clicked.connect(self.adicionar_acessorio)
        form_layout.addWidget(btn_adicionar)

        layout.addLayout(form_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Valor (R$)", "Editar", "Excluir"])
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.tabela.setRowCount(len(self.acessorios))
        for row, acessorio in enumerate(self.acessorios):
            self.tabela.setItem(row, 0, QTableWidgetItem(acessorio["nome"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(acessorio["valor"])))

            # Botão editar
            btn_editar = QPushButton("Editar")
            btn_editar.clicked.connect(lambda checked, r=row: self.abrir_edicao(r))
            self.tabela.setCellWidget(row, 2, btn_editar)

            # Botão excluir
            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, r=row: self.excluir_acessorio(r))
            self.tabela.setCellWidget(row, 3, btn_excluir)

    def adicionar_acessorio(self):
        nome = self.input_nome.text().strip()
        valor = self.input_valor.text().strip()

        if not nome or not valor:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return

        try:
            valor = float(valor.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor válido!")
            return

        self.acessorios.append({"nome": nome, "valor": valor})
        salvar_json(self.acessorios)
        self.atualizar_tabela()
        self.input_nome.clear()
        self.input_valor.clear()

    def abrir_edicao(self, index):
        acessorio = self.acessorios[index]
        self.janela_edicao = TelaEdicaoAcessorio(acessorio, index, self)
        self.janela_edicao.show()

    def excluir_acessorio(self, index):
        confirm = QMessageBox.question(
            self, "Excluir Acessório",
            f"Tem certeza que deseja excluir o acessório '{self.acessorios[index]['nome']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.acessorios.pop(index)
            salvar_json(self.acessorios)
            self.atualizar_tabela()


# --------------------------
# Tela de edição de acessório
# --------------------------
class TelaEdicaoAcessorio(QWidget):
    def __init__(self, acessorio, index, parent):
        super().__init__()
        self.setWindowTitle("Editar Acessório")
        self.setGeometry(300, 300, 400, 200)
        self.acessorio = acessorio
        self.index = index
        self.parent = parent
        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()

        # Campo nome
        nome_layout = QHBoxLayout()
        nome_layout.addWidget(QLabel("Nome:"))
        self.input_nome = QLineEdit(self.acessorio["nome"])
        nome_layout.addWidget(self.input_nome)
        layout.addLayout(nome_layout)

        # Campo valor
        valor_layout = QHBoxLayout()
        valor_layout.addWidget(QLabel("Valor (R$):"))
        self.input_valor = QLineEdit(str(self.acessorio["valor"]))
        valor_layout.addWidget(self.input_valor)
        layout.addLayout(valor_layout)

        # Botão salvar
        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(self.salvar_edicao)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

    def salvar_edicao(self):
        nome = self.input_nome.text().strip()
        valor = self.input_valor.text().strip()

        if not nome or not valor:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return

        try:
            valor = float(valor.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor válido!")
            return

        # Atualizar acessório
        self.parent.acessorios[self.index] = {"nome": nome, "valor": valor}
        salvar_json(self.parent.acessorios)
        self.parent.atualizar_tabela()
        self.close()
