import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)

ARQUIVO_CLIENTES = "clientes.json"

class TelaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Clientes")
        self.setGeometry(250, 250, 850, 500)

        self.clientes = self.carregar_clientes()
        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()

        # Botões principais
        btn_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Adicionar Cliente")
        btn_adicionar.clicked.connect(self.abrir_adicionar)
        btn_layout.addWidget(btn_adicionar)

        btn_editar = QPushButton("Editar Cliente")
        btn_editar.clicked.connect(self.abrir_editar)
        btn_layout.addWidget(btn_editar)

        btn_excluir = QPushButton("Excluir Cliente")
        btn_excluir.clicked.connect(self.excluir_cliente)
        btn_layout.addWidget(btn_excluir)

        layout.addLayout(btn_layout)

        # Tabela de clientes
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["Nome", "CPF/CNPJ", "Email", "Telefone", "Endereço", "Número"]
        )

        # Faz com que a tabela se ajuste ao conteúdo
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.atualizar_tabela()

    # --------------------------
    # Funções de arquivo
    # --------------------------
    def carregar_clientes(self):
        if os.path.exists(ARQUIVO_CLIENTES):
            with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def salvar_clientes(self):
        with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
            json.dump(self.clientes, f, indent=4, ensure_ascii=False)

    # --------------------------
    # Atualizar tabela
    # --------------------------
    def atualizar_tabela(self):
        self.tabela.setRowCount(len(self.clientes))
        for row, cliente in enumerate(self.clientes):
            self.tabela.setItem(row, 0, QTableWidgetItem(cliente["nome"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente["cpf_cnpj"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(cliente.get("email", "")))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente.get("telefone", "")))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente.get("endereco", "")))
            self.tabela.setItem(row, 5, QTableWidgetItem(cliente.get("numero", "")))

    # --------------------------
    # Abrir adicionar cliente
    # --------------------------
    def abrir_adicionar(self):
        self.tela_edicao = JanelaEdicaoCliente(parent=self)
        self.tela_edicao.show()

    # --------------------------
    # Abrir edição cliente
    # --------------------------
    def abrir_editar(self):
        linha = self.tabela.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Erro", "Selecione um cliente para editar!")
            return

        cliente = self.clientes[linha]
        self.tela_edicao = JanelaEdicaoCliente(parent=self, linha=linha, cliente=cliente)
        self.tela_edicao.show()

    # --------------------------
    # Excluir cliente
    # --------------------------
    def excluir_cliente(self):
        linha = self.tabela.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Erro", "Selecione um cliente para excluir!")
            return

        confirm = QMessageBox.question(
            self, "Confirmar exclusão",
            "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.clientes.pop(linha)
            self.salvar_clientes()
            self.atualizar_tabela()


# --------------------------
# Janela de edição/adicionar cliente
# --------------------------
class JanelaEdicaoCliente(QWidget):
    def __init__(self, parent=None, linha=None, cliente=None):
        super().__init__()
        self.parent = parent
        self.linha = linha
        self.setWindowTitle("Editar Cliente" if cliente else "Adicionar Cliente")
        self.setGeometry(300, 300, 650, 300)

        self.inicializar_ui(cliente)

    def inicializar_ui(self, cliente=None):
        layout = QVBoxLayout()

        # Linha 1: Nome, CPF/CNPJ, Email
        form_layout1 = QHBoxLayout()
        self.input_nome = QLineEdit(cliente["nome"] if cliente else "")
        form_layout1.addWidget(QLabel("Nome:"))
        form_layout1.addWidget(self.input_nome)

        self.input_cpf_cnpj = QLineEdit(cliente["cpf_cnpj"] if cliente else "")
        form_layout1.addWidget(QLabel("CPF/CNPJ:"))
        form_layout1.addWidget(self.input_cpf_cnpj)

        self.input_email = QLineEdit(cliente.get("email", "") if cliente else "")
        form_layout1.addWidget(QLabel("Email:"))
        form_layout1.addWidget(self.input_email)
        layout.addLayout(form_layout1)

        # Linha 2: Telefone, Endereço, Número
        form_layout2 = QHBoxLayout()
        self.input_telefone = QLineEdit(cliente.get("telefone", "") if cliente else "")
        form_layout2.addWidget(QLabel("Telefone:"))
        form_layout2.addWidget(self.input_telefone)

        self.input_endereco = QLineEdit(cliente.get("endereco", "") if cliente else "")
        form_layout2.addWidget(QLabel("Endereço:"))
        form_layout2.addWidget(self.input_endereco)

        self.input_numero = QLineEdit(cliente.get("numero", "") if cliente else "")
        form_layout2.addWidget(QLabel("Número:"))
        form_layout2.addWidget(self.input_numero)

        layout.addLayout(form_layout2)

        # Botão salvar
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

    def salvar(self):
        nome = self.input_nome.text()
        cpf = self.input_cpf_cnpj.text()
        email = self.input_email.text()
        telefone = self.input_telefone.text()
        endereco = self.input_endereco.text()
        numero = self.input_numero.text()

        if not nome or not cpf:
            QMessageBox.warning(self, "Erro", "Nome e CPF/CNPJ são obrigatórios!")
            return

        novo_cliente = {
            "nome": nome,
            "cpf_cnpj": cpf,
            "email": email,
            "telefone": telefone,
            "endereco": endereco,
            "numero": numero
        }

        if self.linha is not None:
            # Editar cliente existente
            self.parent.clientes[self.linha] = novo_cliente
        else:
            # Adicionar novo cliente
            self.parent.clientes.append(novo_cliente)

        self.parent.salvar_clientes()
        self.parent.atualizar_tabela()
        self.close()
