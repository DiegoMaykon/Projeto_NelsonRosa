import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QCompleter, QComboBox, QSpinBox, QAbstractItemView, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from fpdf import FPDF

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
        self.abas = QTabWidget()
        self.abas.addTab(self.aba_novo_pedido(), "Novo Pedido")
        self.abas.addTab(self.aba_pedidos_finalizados(), "Pedidos Finalizados")
        layout.addWidget(self.abas)
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
        self.tabela_pedidos.setColumnCount(6)
        self.tabela_pedidos.setHorizontalHeaderLabels(["Número", "Cliente", "Data", "Total", "Ações", "PDF"])
        self.tabela_pedidos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_pedidos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_pedidos.setSelectionMode(QTableWidget.SingleSelection)
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
            "cliente": cliente,
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
            cliente_nome = pedido["cliente"].get("nome_razao") or pedido["cliente"].get("nome", "Sem Nome")
            self.tabela_pedidos.setItem(row, 1, QTableWidgetItem(cliente_nome))
            self.tabela_pedidos.setItem(row, 2, QTableWidgetItem(pedido.get("data", "")))
            self.tabela_pedidos.setItem(row, 3, QTableWidgetItem(f"R$ {pedido.get('total', 0):.2f}"))

            # ações
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

            # botão gerar PDF
            btn_pdf = QPushButton("Gerar PDF")
            btn_pdf.clicked.connect(lambda checked, r=row: self.gerar_pdf_pedido(r))
            self.tabela_pedidos.setCellWidget(row, 5, btn_pdf)

    # --------------------------
    # Função de gerar PDF
    # --------------------------
    def gerar_pdf_pedido(self, row):
        pedido = self.pedidos[row]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Pedido Nº {pedido['numero']}", ln=True)
        pdf.set_font("Arial", '', 12)
        cliente_nome = pedido["cliente"].get("nome_razao") or pedido["cliente"].get("nome", "Sem Nome")
        pdf.cell(0, 10, f"Cliente: {cliente_nome}", ln=True)
        pdf.cell(0, 10, f"Data: {pedido.get('data','')}", ln=True)
        pdf.cell(0, 10, f"Total: R$ {pedido.get('total',0):.2f}", ln=True)
        pdf.ln(10)
        pdf.cell(0, 10, "Itens do Pedido:", ln=True)
        for item in pedido['itens']:
            pdf.cell(0, 10, f"{item['nome']} - Qtd: {item['quantidade']} - Subtotal: R$ {item['subtotal']:.2f}", ln=True)

        arquivo_pdf, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF do Pedido",
            f"Pedido_{pedido['numero']}.pdf",
            "Arquivos PDF (*.pdf)"
        )

        if arquivo_pdf:
            pdf.output(arquivo_pdf)
            QMessageBox.information(self, "PDF Gerado", f"PDF do pedido {pedido['numero']} salvo como:\n{arquivo_pdf}")

    # --------------------------
    # Edição de Pedido (ComboBox/SpinBox)
    # --------------------------
    # (Mantém o código que você já tem para abrir_edicao, adicionar_linha_edicao,
    # recalcular_subtotal, salvar_edicao e remover_linha_edicao)

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
