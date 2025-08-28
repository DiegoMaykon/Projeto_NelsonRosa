import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QCompleter
)
from PyQt5.QtCore import Qt, QDate

ARQUIVO_PEDIDOS = "pedidos.json"
ARQUIVO_CLIENTES = "clientes.json"
ARQUIVO_ACESSORIOS = "acessorios.json"


# --------------------------
# Funções utilitárias
# --------------------------
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_json(dados, arquivo):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# --------------------------
# Tela de Pedidos
# --------------------------
class TelaPedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciamento de Pedidos")
        self.setGeometry(250, 250, 800, 500)

        self.pedidos = carregar_json(ARQUIVO_PEDIDOS)
        self.clientes = carregar_json(ARQUIVO_CLIENTES)
        self.acessorios = carregar_json(ARQUIVO_ACESSORIOS)
        self.itens_pedido = []

        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()
        abas = QTabWidget()
        abas.addTab(self.aba_novo_pedido(), "Novo Pedido")
        abas.addTab(self.aba_pedidos_finalizados(), "Pedidos Finalizados")
        layout.addWidget(abas)
        self.setLayout(layout)

    # --------------------------
    # Aba Novo Pedido
    # --------------------------
    def aba_novo_pedido(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Cliente
        hbox_cliente = QHBoxLayout()
        hbox_cliente.addWidget(QLabel("Cliente (nome/razão):"))
        self.input_cliente = QLineEdit()

        # compatibilidade com nome antigo e novo
        nomes_clientes = [c.get("nome_razao", c.get("nome", "")) for c in self.clientes]
        completer_clientes = QCompleter(nomes_clientes)
        completer_clientes.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_cliente.setCompleter(completer_clientes)

        hbox_cliente.addWidget(self.input_cliente)
        layout.addLayout(hbox_cliente)

        # Acessório
        hbox_acessorio = QHBoxLayout()
        hbox_acessorio.addWidget(QLabel("Acessório:"))
        self.input_acessorio = QLineEdit()

        nomes_acessorios = [a["nome"] for a in self.acessorios]
        completer_acessorios = QCompleter(nomes_acessorios)
        completer_acessorios.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_acessorio.setCompleter(completer_acessorios)

        hbox_acessorio.addWidget(self.input_acessorio)

        hbox_acessorio.addWidget(QLabel("Quantidade:"))
        self.input_qtd = QLineEdit()
        hbox_acessorio.addWidget(self.input_qtd)

        btn_add_item = QPushButton("Adicionar Item")
        btn_add_item.clicked.connect(self.adicionar_item)
        hbox_acessorio.addWidget(btn_add_item)
        layout.addLayout(hbox_acessorio)

        # Tabela de Itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(3)
        self.tabela_itens.setHorizontalHeaderLabels(["Acessório", "Qtd", "Subtotal"])
        layout.addWidget(self.tabela_itens)

        # Finalizar pedido
        btn_finalizar = QPushButton("Finalizar Pedido")
        btn_finalizar.clicked.connect(self.finalizar_pedido)
        layout.addWidget(btn_finalizar)

        widget.setLayout(layout)
        return widget

    # --------------------------
    # Aba Pedidos Finalizados
    # --------------------------
    def aba_pedidos_finalizados(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.tabela_pedidos = QTableWidget()
        self.tabela_pedidos.setColumnCount(5)
        self.tabela_pedidos.setHorizontalHeaderLabels(["Número", "Cliente", "Data", "Total", "Ações"])
        layout.addWidget(self.tabela_pedidos)

        widget.setLayout(layout)
        self.atualizar_pedidos_finalizados()
        return widget

    # --------------------------
    # Funções de Pedido
    # --------------------------
    def adicionar_item(self):
        nome = self.input_acessorio.text().strip()
        qtd_texto = self.input_qtd.text().strip()

        if not nome or not qtd_texto.isdigit():
            QMessageBox.warning(self, "Erro", "Preencha o acessório e a quantidade corretamente!")
            return

        qtd = int(qtd_texto)
        acessorio = next((a for a in self.acessorios if a["nome"].lower() == nome.lower()), None)

        if not acessorio:
            QMessageBox.warning(self, "Erro", "Acessório não encontrado!")
            return

        subtotal = qtd * float(acessorio["valor"])
        item = {"nome": acessorio["nome"], "quantidade": qtd, "subtotal": subtotal}
        self.itens_pedido.append(item)

        row = self.tabela_itens.rowCount()
        self.tabela_itens.insertRow(row)
        self.tabela_itens.setItem(row, 0, QTableWidgetItem(acessorio["nome"]))
        self.tabela_itens.setItem(row, 1, QTableWidgetItem(str(qtd)))
        self.tabela_itens.setItem(row, 2, QTableWidgetItem(f"R$ {subtotal:.2f}"))

        self.input_acessorio.clear()
        self.input_qtd.clear()

    def finalizar_pedido(self):
        cliente_nome = self.input_cliente.text().strip()
        cliente = next(
            (c for c in self.clientes if c.get("nome_razao", c.get("nome", "")).lower() == cliente_nome.lower()), None
        )

        if not cliente:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
            return

        numero = len(self.pedidos) + 1
        data = QDate.currentDate().toString("dd/MM/yyyy")

        pedido = {
            "numero": numero,
            "cliente": cliente,  # salva dict completo
            "itens": self.itens_pedido,
            "data": data,
            "total": sum(item["subtotal"] for item in self.itens_pedido),
        }

        self.pedidos.append(pedido)
        salvar_json(self.pedidos, ARQUIVO_PEDIDOS)

        QMessageBox.information(self, "Sucesso", f"Pedido nº {numero} salvo com sucesso!")
        self.atualizar_pedidos_finalizados()
        self.itens_pedido = []
        self.tabela_itens.setRowCount(0)
        self.input_cliente.clear()

    def atualizar_pedidos_finalizados(self):
        self.tabela_pedidos.setRowCount(len(self.pedidos))
        for row, pedido in enumerate(self.pedidos):
            self.tabela_pedidos.setItem(row, 0, QTableWidgetItem(str(pedido["numero"])))

            if isinstance(pedido["cliente"], dict):
                cliente_nome = pedido["cliente"].get("nome_razao") or pedido["cliente"].get("nome") or "Sem Nome"
            else:
                cliente_nome = str(pedido["cliente"])

            self.tabela_pedidos.setItem(row, 1, QTableWidgetItem(cliente_nome))
            self.tabela_pedidos.setItem(row, 2, QTableWidgetItem(pedido.get("data", "")))
            self.tabela_pedidos.setItem(row, 3, QTableWidgetItem(f"R$ {pedido.get('total', 0):.2f}"))

            # ações (editar/excluir)
            acoes = QWidget()
            hbox = QHBoxLayout()
            hbox.setContentsMargins(0, 0, 0, 0)

            btn_editar = QPushButton("Editar")
            btn_editar.clicked.connect(lambda checked, r=row: self.abrir_edicao(r))
            hbox.addWidget(btn_editar)

            btn_excluir = QPushButton("Excluir")
            btn_excluir.clicked.connect(lambda checked, r=row: self.excluir_pedido(r))
            hbox.addWidget(btn_excluir)

            acoes.setLayout(hbox)
            self.tabela_pedidos.setCellWidget(row, 4, acoes)

    # --------------------------
    # Edição de Pedido
    # --------------------------
    def abrir_edicao(self, row):
        pedido = self.pedidos[row]

        # Nova janela de edição
        self.janela_edicao = QWidget()
        self.janela_edicao.setWindowTitle(f"Editar Pedido nº {pedido['numero']}")
        self.janela_edicao.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        # Cliente
        hbox_cliente = QHBoxLayout()
        hbox_cliente.addWidget(QLabel("Cliente:"))
        self.edit_cliente = QLineEdit(pedido["cliente"].get("nome_razao") or pedido["cliente"].get("nome", ""))
        nomes_clientes = [c.get("nome_razao", c.get("nome", "")) for c in self.clientes]
        completer_clientes = QCompleter(nomes_clientes)
        completer_clientes.setCaseSensitivity(Qt.CaseInsensitive)
        self.edit_cliente.setCompleter(completer_clientes)
        hbox_cliente.addWidget(self.edit_cliente)
        layout.addLayout(hbox_cliente)

        # Tabela de itens
        self.tabela_edicao = QTableWidget()
        self.tabela_edicao.setColumnCount(3)
        self.tabela_edicao.setHorizontalHeaderLabels(["Acessório", "Qtd", "Subtotal"])
        layout.addWidget(self.tabela_edicao)

        # Preenche com os itens existentes
        for item in pedido["itens"]:
            row_item = self.tabela_edicao.rowCount()
            self.tabela_edicao.insertRow(row_item)
            self.tabela_edicao.setItem(row_item, 0, QTableWidgetItem(item["nome"]))
            self.tabela_edicao.setItem(row_item, 1, QTableWidgetItem(str(item["quantidade"])))
            self.tabela_edicao.setItem(row_item, 2, QTableWidgetItem(f"R$ {item['subtotal']:.2f}"))

        # Botão salvar alterações
        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(lambda: self.salvar_edicao(row))
        layout.addWidget(btn_salvar)

        self.janela_edicao.setLayout(layout)
        self.janela_edicao.show()

    def salvar_edicao(self, row):
        cliente_nome = self.edit_cliente.text().strip()
        cliente = next(
            (c for c in self.clientes if c.get("nome_razao", c.get("nome", "")).lower() == cliente_nome.lower()), None
        )

        if not cliente:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
            return

        # Reconstrói os itens da tabela editada
        itens_editados = []
        for r in range(self.tabela_edicao.rowCount()):
            nome = self.tabela_edicao.item(r, 0).text()
            qtd = int(self.tabela_edicao.item(r, 1).text())
            acessorio = next((a for a in self.acessorios if a["nome"].lower() == nome.lower()), None)
            if not acessorio:
                continue
            subtotal = qtd * float(acessorio["valor"])
            itens_editados.append({"nome": nome, "quantidade": qtd, "subtotal": subtotal})

        # Atualiza o pedido
        self.pedidos[row]["cliente"] = cliente
        self.pedidos[row]["itens"] = itens_editados
        self.pedidos[row]["total"] = sum(item["subtotal"] for item in itens_editados)

        salvar_json(self.pedidos, ARQUIVO_PEDIDOS)
        QMessageBox.information(self, "Sucesso", "Pedido atualizado com sucesso!")

        self.janela_edicao.close()
        self.atualizar_pedidos_finalizados()

    # --------------------------
    # Excluir Pedido
    # --------------------------
    def excluir_pedido(self, row):
        numero = self.pedidos[row]["numero"]
        confirmacao = QMessageBox.question(
            self, "Confirmar", f"Excluir o pedido nº {numero}?", QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            del self.pedidos[row]
            salvar_json(self.pedidos, ARQUIVO_PEDIDOS)
            self.atualizar_pedidos_finalizados()
