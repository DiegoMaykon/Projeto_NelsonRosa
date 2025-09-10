import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QTabWidget
)

ARQUIVO_ACESSORIOS = "acessorios.json"


def carregar_acessorios():
    if os.path.exists(ARQUIVO_ACESSORIOS):
        with open(ARQUIVO_ACESSORIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_acessorios(acessorios):
    with open(ARQUIVO_ACESSORIOS, "w", encoding="utf-8") as f:
        json.dump(acessorios, f, indent=4, ensure_ascii=False)


class TelaAcessorios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Acessórios")
        self.setGeometry(250, 250, 700, 500)

        self.acessorios = carregar_acessorios()

        self.abas = QTabWidget()
        self.aba_listagem = QWidget()
        self.aba_cadastro = QWidget()
        self.aba_edicao = QWidget()

        self.abas.addTab(self.aba_listagem, "Acessórios Cadastrados")
        self.abas.addTab(self.aba_cadastro, "Novo Acessório")

        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.abas)
        self.setLayout(layout_principal)

        self.inicializar_aba_listagem()
        self.inicializar_aba_cadastro()
        self.inicializar_aba_edicao()

    # -----------------------------
    # Aba de listagem
    # -----------------------------
    def inicializar_aba_listagem(self):
        layout = QVBoxLayout()

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Código do Item", "Nome", "Descrição", "Valor (R$)"])
        self.tabela.setColumnWidth(0, 120)
        self.tabela.setColumnWidth(1, 180)
        self.tabela.setColumnWidth(2, 220)
        self.tabela.setColumnWidth(3, 100)

        layout.addWidget(self.tabela)

        btn_editar = QPushButton("Editar Selecionado")
        btn_editar.clicked.connect(self.editar_acessorio)
        layout.addWidget(btn_editar)

        btn_excluir = QPushButton("Excluir Selecionado")
        btn_excluir.clicked.connect(self.excluir_acessorio)
        layout.addWidget(btn_excluir)

        self.aba_listagem.setLayout(layout)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.tabela.setRowCount(len(self.acessorios))
        for row, acessorio in enumerate(self.acessorios):
            self.tabela.setItem(row, 0, QTableWidgetItem(acessorio["codigo"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(acessorio["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(acessorio["descricao"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(acessorio["valor"])))

    # -----------------------------
    # Aba de cadastro
    # -----------------------------
    def inicializar_aba_cadastro(self):
        layout = QVBoxLayout()

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código do Item")
        layout.addWidget(QLabel("Código do Item:"))
        layout.addWidget(self.input_codigo)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do acessório")
        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.input_nome)

        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Descrição")
        layout.addWidget(QLabel("Descrição:"))
        layout.addWidget(self.input_descricao)

        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Valor em R$")
        layout.addWidget(QLabel("Valor (R$):"))
        layout.addWidget(self.input_valor)

        btn_salvar = QPushButton("Salvar Acessório")
        btn_salvar.clicked.connect(self.salvar_novo_acessorio)
        layout.addWidget(btn_salvar)

        self.aba_cadastro.setLayout(layout)

    def salvar_novo_acessorio(self):
        codigo = self.input_codigo.text().strip()
        nome = self.input_nome.text().strip()
        descricao = self.input_descricao.text().strip()
        valor = self.input_valor.text().strip()

        if not codigo or not nome or not valor:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return

        try:
            valor = float(valor)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return

        novo_acessorio = {"codigo": codigo, "nome": nome, "descricao": descricao, "valor": valor}
        self.acessorios.append(novo_acessorio)
        salvar_acessorios(self.acessorios)
        QMessageBox.information(self, "Sucesso", "Acessório cadastrado com sucesso!")

        self.input_codigo.clear()
        self.input_nome.clear()
        self.input_descricao.clear()
        self.input_valor.clear()

        self.atualizar_tabela()
        self.abas.setCurrentWidget(self.aba_listagem)

    # -----------------------------
    # Aba de edição
    # -----------------------------
    def inicializar_aba_edicao(self):
        layout = QVBoxLayout()

        self.edit_codigo = QLineEdit()
        layout.addWidget(QLabel("Código do Item:"))
        layout.addWidget(self.edit_codigo)

        self.edit_nome = QLineEdit()
        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.edit_nome)

        self.edit_descricao = QLineEdit()
        layout.addWidget(QLabel("Descrição:"))
        layout.addWidget(self.edit_descricao)

        self.edit_valor = QLineEdit()
        layout.addWidget(QLabel("Valor (R$):"))
        layout.addWidget(self.edit_valor)

        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(self.salvar_edicao)
        layout.addWidget(btn_salvar)

        self.aba_edicao.setLayout(layout)

    def editar_acessorio(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um acessório para editar!")
            return

        acessorio = self.acessorios[row]
        self.edit_codigo.setText(acessorio["codigo"])
        self.edit_nome.setText(acessorio["nome"])
        self.edit_descricao.setText(acessorio["descricao"])
        self.edit_valor.setText(str(acessorio["valor"]))

        self.acessorio_em_edicao = row
        self.abas.addTab(self.aba_edicao, "Editar Acessório")
        self.abas.setCurrentWidget(self.aba_edicao)

    def salvar_edicao(self):
        codigo = self.edit_codigo.text().strip()
        nome = self.edit_nome.text().strip()
        descricao = self.edit_descricao.text().strip()
        valor = self.edit_valor.text().strip()

        if not codigo or not nome or not valor:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return

        try:
            valor = float(valor)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return

        self.acessorios[self.acessorio_em_edicao] = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "valor": valor
        }

        salvar_acessorios(self.acessorios)
        QMessageBox.information(self, "Sucesso", "Acessório atualizado com sucesso!")

        self.atualizar_tabela()
        self.abas.removeTab(self.abas.indexOf(self.aba_edicao))
        self.abas.setCurrentWidget(self.aba_listagem)

    def excluir_acessorio(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um acessório para excluir!")
            return

        confirm = QMessageBox.question(
            self, "Confirmar Exclusão",
            "Tem certeza que deseja excluir este acessório?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.acessorios.pop(row)
            salvar_acessorios(self.acessorios)
            self.atualizar_tabela()
            QMessageBox.information(self, "Sucesso", "Acessório excluído com sucesso!")
