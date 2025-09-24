import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QCompleter, QComboBox, QSpinBox, QAbstractItemView,
    QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from reportlab.pdfgen import canvas

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
        self.setGeometry(250, 250, 900, 500)

        self.pedidos = carregar_json(ARQUIVO_PEDIDOS)
        self.clientes = carregar_json(ARQUIVO_CLIENTES)
        self.acessorios = carregar_json(ARQUIVO_ACESSORIOS)
        self.itens_pedido = []

        self.ultima_pasta = ""  # Guarda a última pasta usada para salvar PDFs

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
        self.input_acessorio = QComboBox()
        for a in self.acessorios:
            self.input_acessorio.addItem(a["nome"])
        hbox_acessorio.addWidget(self.input_acessorio)

        hbox_acessorio.addWidget(QLabel("Quantidade:"))
        self.input_qtd = QSpinBox()
        self.input_qtd.setRange(1, 999)
        self.input_qtd.setValue(1)
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

    def adicionar_item(self):
        nome = self.input_acessorio.currentText()
        qtd = self.input_qtd.value()
        acessorio = next((a for a in self.acessorios if a["nome"] == nome), None)
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

    def atualizar_pedidos_finalizados(self):
        self.tabela_pedidos.setRowCount(len(self.pedidos))
        for row, pedido in enumerate(self.pedidos):
            self.tabela_pedidos.setItem(row, 0, QTableWidgetItem(str(pedido["numero"])))
            cliente_nome = pedido["cliente"].get("nome_razao") or pedido["cliente"].get("nome", "Sem Nome")
            self.tabela_pedidos.setItem(row, 1, QTableWidgetItem(cliente_nome))
            self.tabela_pedidos.setItem(row, 2, QTableWidgetItem(pedido.get("data", "")))
            self.tabela_pedidos.setItem(row, 3, QTableWidgetItem(f"R$ {pedido.get('total', 0):.2f}"))

            # Ações: Editar / Excluir
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

            # Botão PDF
            btn_pdf = QPushButton("Baixar PDF")
            btn_pdf.clicked.connect(lambda checked, r=row: self.gerar_pdf(r))
            self.tabela_pedidos.setCellWidget(row, 5, btn_pdf)

    # --------------------------
    # Edição com ComboBox + SpinBox
    # --------------------------
    def abrir_edicao(self, row):
        pedido = self.pedidos[row]

        self.janela_edicao = QWidget()
        self.janela_edicao.setWindowTitle(f"Editar Pedido nº {pedido['numero']}")
        self.janela_edicao.setGeometry(300, 300, 700, 500)

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

        # Tabela editável
        self.tabela_edicao = QTableWidget()
        self.tabela_edicao.setColumnCount(3)
        self.tabela_edicao.setHorizontalHeaderLabels(["Acessório", "Qtd", "Subtotal"])
        self.tabela_edicao.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.tabela_edicao)

        for item in pedido["itens"]:
            self.adicionar_linha_edicao(item["nome"], item["quantidade"])

        # Botões adicionar/remover
        hbox_botoes = QHBoxLayout()
        btn_add_item = QPushButton("Adicionar Item")
        btn_add_item.clicked.connect(lambda: self.adicionar_linha_edicao())
        hbox_botoes.addWidget(btn_add_item)
        btn_remover_item = QPushButton("Remover Item")
        btn_remover_item.clicked.connect(self.remover_linha_edicao)
        hbox_botoes.addWidget(btn_remover_item)
        layout.addLayout(hbox_botoes)

        # Botão salvar
        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(lambda: self.salvar_edicao(row))
        layout.addWidget(btn_salvar)

        self.janela_edicao.setLayout(layout)
        self.janela_edicao.show()

    def adicionar_linha_edicao(self, nome=None, qtd=1):
        row_item = self.tabela_edicao.rowCount()
        self.tabela_edicao.insertRow(row_item)

        combo = QComboBox()
        for a in self.acessorios:
            combo.addItem(a["nome"])
        if nome:
            combo.setCurrentText(nome)
        combo.currentIndexChanged.connect(lambda _, r=row_item: self.recalcular_subtotal(r))
        self.tabela_edicao.setCellWidget(row_item, 0, combo)

        spin = QSpinBox()
        spin.setRange(1, 999)
        spin.setValue(qtd)
        spin.valueChanged.connect(lambda _, r=row_item: self.recalcular_subtotal(r))
        self.tabela_edicao.setCellWidget(row_item, 1, spin)

        self.recalcular_subtotal(row_item)

    def remover_linha_edicao(self):
        linha = self.tabela_edicao.currentRow()
        if linha >= 0:
            self.tabela_edicao.removeRow(linha)

    def recalcular_subtotal(self, row):
        combo: QComboBox = self.tabela_edicao.cellWidget(row, 0)
        spin: QSpinBox = self.tabela_edicao.cellWidget(row, 1)
        if not combo or not spin:
            return
        nome = combo.currentText()
        qtd = spin.value()
        acessorio = next((a for a in self.acessorios if a["nome"] == nome), None)
        if acessorio:
            subtotal = qtd * float(acessorio["valor"])
            self.tabela_edicao.setItem(row, 2, QTableWidgetItem(f"R$ {subtotal:.2f}"))

    def salvar_edicao(self, row):
        cliente_nome = self.edit_cliente.text().strip()
        cliente = next(
            (c for c in self.clientes if c.get("nome_razao", c.get("nome", "")).lower() == cliente_nome.lower()), None
        )
        if not cliente:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
            return

        itens_editados = []
        for r in range(self.tabela_edicao.rowCount()):
            combo: QComboBox = self.tabela_edicao.cellWidget(r, 0)
            spin: QSpinBox = self.tabela_edicao.cellWidget(r, 1)
            if not combo or not spin:
                continue
            nome = combo.currentText()
            qtd = spin.value()
            acessorio = next((a for a in self.acessorios if a["nome"] == nome), None)
            if acessorio:
                subtotal = qtd * float(acessorio["valor"])
                itens_editados.append({"nome": nome, "quantidade": qtd, "subtotal": subtotal})

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
        confirm = QMessageBox.question(self, "Confirmar Exclusão", f"Deseja excluir o pedido nº {self.pedidos[row]['numero']}?")
        if confirm == QMessageBox.Yes:
            self.pedidos.pop(row)
            salvar_json(self.pedidos, ARQUIVO_PEDIDOS)
            self.atualizar_pedidos_finalizados()


    def gerar_pdf(self, row):
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
        )
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        import os

        pedido = self.pedidos[row]
        cliente = pedido["cliente"]
        nome_cliente = cliente.get("nome_razao") or cliente.get("nome", "")

        # Seleciona pasta e nome do arquivo
        pasta_inicial = self.ultima_pasta if self.ultima_pasta else ""
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF",
            os.path.join(pasta_inicial, f"pedido_{pedido['numero']}.pdf"),
            "PDF Files (*.pdf)"
        )
        if not caminho:
            return

        self.ultima_pasta = os.path.dirname(caminho)

        # Configuração do PDF
        doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elementos = []

        # --- Logo ---
        logo_path = """D:\Projeto_NelsonRosa\LogoALMETAIS.PNG"""  # caminho da sua logo
        if os.path.exists(logo_path):
            img_logo = Image(logo_path, width=100, height=100,hAlign="LEFT")
            elementos.append(img_logo)
        elementos.append(Spacer(1, 20))

        # --- Estilos para tabelas ---
        estilo_cabecalho = ParagraphStyle(name="Cabecalho", fontSize=10, fontName='Helvetica-Bold')
        estilo_normal = ParagraphStyle(name="Normal", fontSize=9, fontName='Helvetica')

        # --- Dados Empresa (direita) ---
        dados_empresa = [
            ["Iorli de Fatima Marcondes Rosa Representações"],
            ["CNPJ: 34.308.499/0001-10"],
            ["IE: 1706084.2144-6"],
            ["R. Arcendino Rosa Neves 278 - Xaxim, Curitiba - PR"],
            ["Telefone: (41) 99914-7644"],
            ["Email: Nelsonrosaperfis@yahoo.com.br"]
        ]
        tabela_empresa = Table(dados_empresa, colWidths=[250], hAlign='RIGHT')
        tabela_empresa.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
        ]))

        # --- Dados Cliente (esquerda) ---
        dados_cliente = [
            ["Dados do Cliente:"],
            [f"Nome: {cliente.get('nome', '')}"],
            [f"CPF/CNPJ: {cliente.get('cpf_cnpj', '')}"],
            [f"Email: {cliente.get('email', '')}"],
            [f"Telefone: {cliente.get('telefone', '')}"],
            [f"Rua: {cliente.get('rua', '')}"],
            [f"Número: {cliente.get('numero', '')}"],
            [f"Cidade: {cliente.get('cidade', '')}"],
            [f"Estado: {cliente.get('estado', '')}"],
            [f"IE: {cliente.get('ie', '')}"]
        ]
        tabela_cliente = Table(dados_cliente, colWidths=[250], hAlign='LEFT')
        tabela_cliente.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
        ]))

        # --- Coloca Empresa e Cliente na mesma linha ---
        from reportlab.platypus import KeepTogether
        tabela_horizontal = Table([[tabela_cliente, tabela_empresa]], colWidths=[270, 270])
        tabela_horizontal.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elementos.append(tabela_horizontal)
        elementos.append(Spacer(1, 20))

        # --- Título e número do pedido ---
        elementos.append(Paragraph(f"<b>Proposta Comercial nº {pedido['numero']}</b>", styles['Title']))
        elementos.append(Spacer(1, 10))

        # --- Tabela de Itens ---
        dados_itens = [["Acessório", "Qtd", "Subtotal (R$)"]]
        for item in pedido["itens"]:
            dados_itens.append([item['nome'], str(item['quantidade']), f"{item['subtotal']:.2f}"])

        tabela_itens = Table(dados_itens, colWidths=[250, 80, 100])
        tabela_itens.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elementos.append(tabela_itens)
        elementos.append(Spacer(1, 15))

        # --- Total ---
        elementos.append(Paragraph(f"<b>Total: R$ {pedido.get('total', 0):.2f}</b>", styles['Heading2']))

        # --- Gera PDF ---
        doc.build(elementos)
        QMessageBox.information(self, "PDF Gerado", f"PDF do pedido nº {pedido['numero']} salvo com sucesso!")




