"""Gera report/CredPay_Neo4j.docx e .pdf a partir de report/resultados.json e cypher/*.cypher.
Nao acessa o banco. Uso: python src/relatorio.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
REL = RAIZ / "report"
CLARO, ROXO, CINZA, ESCURO, TEXTO = "D8D8F6", "B18FCF", "978897", "494850", "2C2C34"


def rgb(h):
    return RGBColor.from_string(h)


def sombra(elem_pr, cor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    elem_pr.append(shd)


def fonte(run, tam=None, cor=TEXTO, negrito=None, nome=None, italico=None):
    if tam:
        run.font.size = Pt(tam)
    run.font.color.rgb = rgb(cor)
    if negrito is not None:
        run.bold = negrito
    if italico is not None:
        run.italic = italico
    if nome:
        run.font.name = nome
        run._element.rPr.rFonts.set(qn("w:eastAsia"), nome)


def borda_inferior(p, cor, sz):
    bd = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", str(sz)), ("space", "1"), ("color", cor)):
        b.set(qn(f"w:{k}"), v)
    bd.append(b)
    p._p.get_or_add_pPr().append(bd)


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.0)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.font.color.rgb = rgb(TEXTO)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.1
for nome, tam, cor in (("Heading 1", 18, ROXO), ("Heading 2", 13, ESCURO)):
    st = doc.styles[nome]
    st.font.name = "Calibri"
    st.font.size = Pt(tam)
    st.font.bold = True
    st.font.color.rgb = rgb(cor)
    st.paragraph_format.space_before = Pt(16 if nome == "Heading 1" else 10)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.keep_with_next = True


def titulo(txt, nivel=1):
    return doc.add_heading(txt, level=nivel)


def par(txt="", negrito_ini=None, **kw):
    p = doc.add_paragraph()
    if negrito_ini:
        fonte(p.add_run(negrito_ini), negrito=True, cor=ESCURO)
    if txt:
        fonte(p.add_run(txt), **kw)
    return p


def lista(itens):
    for it in itens:
        p = doc.add_paragraph(style="List Bullet")
        fonte(p.add_run(it[0]), negrito=True, cor=ESCURO)
        fonte(p.add_run(it[1]))
        p.paragraph_format.space_after = Pt(3)


def codigo(txt):
    linhas = txt.strip("\n").split("\n")
    for i, ln in enumerate(linhas):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = pf.space_before = Pt(0)
        pf.line_spacing = 1.0
        pf.left_indent = Cm(0.2)
        pf.keep_together = True
        if i < len(linhas) - 1:
            pf.keep_with_next = True
        sombra(p._p.get_or_add_pPr(), CLARO)
        fonte(p.add_run(ln if ln else " "), tam=8, nome="Consolas")
    esp = doc.add_paragraph()
    esp.paragraph_format.space_after = Pt(2)
    esp.paragraph_format.keep_with_next = True


def tabela(cab, linhas, larguras=None):
    t = doc.add_table(rows=1, cols=len(cab))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    bordas = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{lado}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:color"), CINZA)
        bordas.append(b)
    t._tbl.tblPr.append(bordas)

    def celula(c, txt, cor, fundo, neg=False):
        c.text = ""
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.keep_with_next = True
        fonte(p.add_run(str(txt)), tam=10, cor=cor, negrito=neg)
        if fundo:
            sombra(c._tc.get_or_add_tcPr(), fundo)

    for c, txt in zip(t.rows[0].cells, cab):
        celula(c, txt, CLARO, ESCURO, True)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for i, ln in enumerate(linhas):
        r = t.add_row()
        r._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for c, txt in zip(r.cells, ln):
            celula(c, txt, TEXTO, CLARO if i % 2 == 1 else None)
    if larguras:
        t.autofit = False
        for r in t.rows:
            for c, w in zip(r.cells, larguras):
                c.width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def quebra():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def diagrama(caminho):
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=200)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    pos = {"Cliente": (1.3, 3), "Conta": (5, 3), "Cartao": (8.7, 4.9), "Dispositivo": (8.7, 3),
           "IP": (8.7, 1.1), "Endereco": (1.3, 5.1)}
    nomes = {"Cartao": "Cartão", "Endereco": "Endereço"}
    for n, (x, y) in pos.items():
        ax.add_patch(plt.Circle((x, y), 0.8, color="#" + (ROXO if n == "Conta" else CLARO),
                                ec="#" + ESCURO, lw=1.5, zorder=3))
        ax.text(x, y, nomes.get(n, n), ha="center", va="center", fontsize=8.5,
                color="#" + TEXTO, fontweight="bold", zorder=4)

    def seta(a, b, rot, dx=0.0, dy=0.0):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color="#" + ESCURO, lw=1.4, shrinkA=33, shrinkB=33))
        ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, rot, ha="center", va="center", fontsize=8,
                color="#" + ESCURO, bbox=dict(fc="white", ec="none", pad=1.5), zorder=5)

    seta("Cliente", "Conta", "TITULAR_DE", 0, 0.25)
    seta("Cliente", "Endereco", "MORA_EM", 0.75, 0)
    seta("Conta", "Cartao", "USA_CARTAO", -0.3, 0.2)
    seta("Conta", "Dispositivo", "ACESSOU_DE", 0, 0.25)
    seta("Conta", "IP", "USOU_IP", -0.3, -0.2)
    # laco TRANSFERIU: Conta -> Conta
    ax.annotate("", xy=(5.45, 3.78), xytext=(4.55, 3.78), zorder=2,
                arrowprops=dict(arrowstyle="-|>", color="#" + ROXO, lw=2.2, connectionstyle="arc3,rad=-2.4"))
    ax.text(5, 5.3, "TRANSFERIU\n{valor, data}", ha="center", fontsize=8.5,
            color="#" + ESCURO, fontweight="bold")
    fig.savefig(caminho, bbox_inches="tight", facecolor="white")
    plt.close(fig)


dados = json.loads((REL / "resultados.json").read_text(encoding="utf-8"))
cont, cons = dados["contagem"], dados["consultas"]


def cypher(nome):
    txt = (RAIZ / "cypher" / f"{nome}.cypher").read_text(encoding="utf-8")
    return "\n".join(ln for ln in txt.splitlines() if not ln.strip().startswith("//"))


# ---------------------------------------------------------------- capa
for _ in range(5):
    doc.add_paragraph()
p = doc.add_paragraph()
fonte(p.add_run("Detectando fraudes na CredPay Digital com Neo4j"), tam=30, cor=ROXO, negrito=True)
p.paragraph_format.space_after = Pt(10)
p = doc.add_paragraph()
fonte(p.add_run("Protótipo de banco de dados em grafos para identificar padrões de fraude em transferências"),
      tam=14, cor=ESCURO)
borda_inferior(doc.add_paragraph(), ROXO, 18)
for _ in range(5):
    doc.add_paragraph()
for rot, val in (("Disciplina: ", "Banco de Dados"), ("Data: ", "19/11/2026")):
    p = doc.add_paragraph()
    fonte(p.add_run(rot), cor=ESCURO, negrito=True, tam=13)
    fonte(p.add_run(val), tam=13)
p = doc.add_paragraph()
fonte(p.add_run("Integrantes: "), cor=ESCURO, negrito=True, tam=13)
fonte(p.add_run("Heitor Shiniti Miasato"), tam=13)
quebra()

# ---------------------------------------------------------------- 1
titulo("1 Contexto e problema")
par("A CredPay Digital é uma fintech fictícia que oferece contas, cartões e transferências entre clientes. "
    "Como em qualquer instituição financeira, parte dos usuários tenta cometer fraudes: abrir várias contas "
    "com os mesmos dados de acesso, usar uma conta nova como \"laranja\" para receber dinheiro de muitas "
    "origens ou girar valores em círculo para esconder a origem.")
par("O ponto em comum desses golpes é que a suspeita não está em uma linha isolada, e sim na relação entre "
    "várias entidades: clientes, contas, cartões, dispositivos e endereços de IP. Este trabalho constrói um "
    "protótipo em Neo4j (banco de dados orientado a grafos) que representa essas relações e usa consultas "
    "Cypher para encontrar sete padrões de fraude pedidos no enunciado:")
lista([("Padrão 1: ", "vários clientes acessando a partir do mesmo dispositivo."),
       ("Padrão 2: ", "clientes diferentes usando o mesmo IP."),
       ("Padrão 3: ", "conta recém-criada recebendo de muitas origens."),
       ("Padrão 4: ", "anel (ciclo) de transferências."),
       ("Padrão 5: ", "o mesmo cartão em contas de clientes diferentes."),
       ("Padrão 6: ", "cadeia de transferências entre pares sem histórico anterior."),
       ("Padrão 7: ", "passagem rápida, quando a conta recebe e repassa quase de imediato.")])
par("Os dados são fictícios e o escopo é um protótipo didático: não há API, interface nem volume real de "
    "clientes. Os resultados mostrados são saídas reais das consultas, executadas em uma instância Neo4j Aura.")

# ---------------------------------------------------------------- 2
titulo("2 Por que grafos")
par("No modelo relacional do enunciado, cada transferência é uma linha da tabela de transações, com conta de "
    "origem e conta de destino. Perguntar \"quem recebeu de quem\" é simples, mas perguntar \"essa conta "
    "voltou a receber o dinheiro que ela mesma enviou, passando por três intermediários?\" exige ligar a "
    "tabela com ela mesma. Com auto-joins fixos, é preciso saber de antemão o número de saltos.")
par("Exemplo: ciclo de 4 saltos (A, B, C, D e de volta a A) com auto-joins em SQL.")
codigo("""SELECT t1.origem
FROM transacao t1
JOIN transacao t2 ON t2.origem = t1.destino
JOIN transacao t3 ON t3.origem = t2.destino
JOIN transacao t4 ON t4.origem = t3.destino
WHERE t4.destino = t1.origem;""")
par("O SQL:1999 resolve a profundidade variável com WITH RECURSIVE. Em PostgreSQL, ciclos de 3 a 5 saltos "
    "sem repetir conta (a ordem temporal não está incluída, para manter o exemplo curto):")
codigo("""WITH RECURSIVE c(ini, atual, caminho, n) AS (
  SELECT origem, destino, ARRAY[origem, destino], 1 FROM transacao
  UNION ALL
  SELECT c.ini, t.destino, c.caminho || t.destino, c.n + 1
  FROM c JOIN transacao t ON t.origem = c.atual
  WHERE c.n < 5 AND (t.destino = c.ini OR NOT t.destino = ANY(c.caminho))
)
SELECT * FROM c WHERE atual = ini AND n >= 3;""")
par("O mesmo padrão em Cypher é escrito como um caminho que começa e termina no mesmo nó, com limite de "
    "3 a 5 saltos (no Cypher esse limite do caminho variável é um literal):")
codigo("MATCH p = (a:Conta)-[:TRANSFERIU*3..5]->(a)\nRETURN a.id, [n IN nodes(p) | n.id]")
par("Portanto o grafo não traz uma capacidade que o SQL não tenha. A vantagem está na legibilidade (a consulta "
    "se parece com a pergunta do analista), na travessia por adjacência, que segue ponteiros entre nós sem "
    "buscar em índice a cada salto, e na possibilidade de misturar tipos de vínculo (dispositivo, IP, "
    "cartão) no mesmo padrão.")
par("Isso não significa que o banco relacional seja ruim: para cadastro, saldo e lançamentos contábeis ele "
    "continua sendo a escolha certa. O grafo entra como camada de análise de relações.")

# ---------------------------------------------------------------- 3
titulo("3 Modelo de grafo")
par("O modelo tem seis tipos de nós (tabela 1) e seis tipos de relacionamentos (tabela 2). "
    "A figura 1 resume como eles se ligam.")
img = REL / "_modelo.png"
diagrama(img)
doc.add_picture(str(img), width=Cm(13.5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = par("Figura 1: modelo de grafo da CredPay.", italico=True, cor=CINZA, tam=9)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
par("Tabela 1: nós e propriedades.", italico=True, cor=CINZA, tam=9).paragraph_format.keep_with_next = True
tabela(["Nó", "Propriedades", "Descrição"], [
    ["Cliente", "id, nome, cpf (mascarado)", "Pessoa titular de uma ou mais contas."],
    ["Conta", "id, tipo, criada_em", "Conta corrente; criada_em permite achar contas novas."],
    ["Cartao", "id", "Cartão usado por contas."],
    ["Dispositivo", "id", "Aparelho de onde a conta foi acessada."],
    ["IP", "id", "Endereço IP de acesso."],
    ["Endereco", "id", "Endereço residencial dos clientes."]], [3, 5, 8])
par("Tabela 2: relacionamentos.", italico=True, cor=CINZA, tam=9).paragraph_format.keep_with_next = True
tabela(["Relacionamento", "Direção", "Propriedades"], [
    ["TITULAR_DE", "(Cliente) → (Conta)", "-"],
    ["TRANSFERIU", "(Conta) → (Conta)", "id, valor, data"],
    ["USA_CARTAO", "(Conta) → (Cartao)", "-"],
    ["ACESSOU_DE", "(Conta) → (Dispositivo)", "-"],
    ["USOU_IP", "(Conta) → (IP)", "-"],
    ["MORA_EM", "(Cliente) → (Endereco)", "-"]], [4, 6.5, 5.5])
titulo("Por que TRANSFERIU é uma aresta e não um nó", 2)
par("Uma transferência tem origem, destino, valor e data. Como ela sempre liga exatamente duas contas e não "
    "precisa ser ligada a outras coisas, cabe numa aresta com propriedades. Assim, uma cadeia de transferências "
    "é um caminho direto Conta, Conta, Conta, sem um nó \"Transação\" no meio de cada salto. Com a transação "
    "como nó, o mesmo caminho teria o dobro de saltos e as consultas de ciclo e cadeia ficariam mais pesadas e "
    "menos legíveis. Se um dia a transação precisasse se relacionar com outros nós (por exemplo, uma "
    "investigação ou um lote de pagamentos), vale reavaliar e promovê-la a nó.")

# ---------------------------------------------------------------- 4
titulo("4 Dataset")
par("A base mistura três origens:")
lista([("Dados do enunciado: ", "clientes C001 a C004, contas A001 a A004 e transações T001 a T004, que formam o "
        "ciclo A001, A002, A003, A004 e de volta a A001. Entram intactos."),
       ("Dados sintéticos de fraude: ", "um cenário para cada um dos demais padrões (por exemplo, três clientes no "
        "dispositivo D1 e uma conta nova A013 recebendo de A005, A006 e A007)."),
       ("Controles negativos: ", "casos parecidos com fraude que não devem ser marcados, como duas contas do mesmo "
        "cliente no mesmo dispositivo, três contas do mesmo cliente no mesmo dispositivo, uma conta antiga recebendo de várias origens, um repasse que demora duas horas ou uma cadeia rápida cujo par de contas já havia transacionado.")])
par("O CPF é um valor mascarado (não há dado pessoal real). A carga é idempotente: o script apaga o grafo inteiro da instância e "
    "recarrega tudo, então pode ser repetido sem duplicar dados. Contagens após a carga (tabela 3):")
par("Tabela 3: contagem de nós e relacionamentos.", italico=True, cor=CINZA, tam=9).paragraph_format.keep_with_next = True
n, a = cont["nos"], cont["arestas"]
tabela(["Nós", "Qtd.", "Relacionamentos", "Qtd."],
       [[k1, n[k1], k2, a[k2]] for k1, k2 in zip(sorted(n), sorted(a))], [4, 2.5, 5, 2.5])
par(f"No total são {sum(n.values())} nós e {sum(a.values())} relacionamentos. "
    "Os dados sintéticos têm datas fixas e a referência de \"hoje\" na consulta 3 é 19/11/2026, para que o "
    "resultado seja reproduzível.")

# ---------------------------------------------------------------- 5
titulo("5 As sete consultas")
par("Para cada consulta mostramos o padrão de fraude, o código Cypher, o resultado real (lido de "
    "resultados.json), a interpretação e o controle negativo, isto é, um caso parecido que a consulta "
    "corretamente não retorna.")

Q = [
    ("q1_dispositivo_compartilhado", "03_q1_dispositivo_compartilhado", "Consulta 1: dispositivo compartilhado",
     "Várias contas (três ou mais), de pelo menos dois clientes diferentes, acessadas pelo mesmo aparelho.",
     "O dispositivo D1 é usado por três clientes (C005, C006 e C007), cada um com sua conta. Pode ser fraude (uma pessoa operando várias identidades), mas também família ou aparelho compartilhado, então o resultado é um alerta para revisão.",
     "O dispositivo D4 tem duas contas (A011 e A012) do mesmo cliente C011, e não atinge três contas. O dispositivo D5 tem três contas (A040, A041 e A042), mas todas do mesmo cliente C040: isola o critério de dois ou mais clientes. Nenhum dos dois aparece."),
    ("q2_ip_compartilhado", "03_q2_ip_compartilhado", "Consulta 2: IP compartilhado",
     "Clientes diferentes usando o mesmo endereço IP.",
     "O IP 203.0.113.10 foi usado pelos clientes C009 e C010. Dois clientes no mesmo IP merecem revisão, ainda que possa haver explicação legítima (casa ou escritório).",
     "O IP 198.51.100.7 é usado por duas contas (A011 e A012), mas do mesmo cliente C011, então não é retornado."),
    ("q3_conta_nova_recebendo", "03_q3_conta_nova_recebendo", "Consulta 3: conta nova recebendo de várias origens",
     "Conta aberta há pouco tempo que recebe transferências de três ou mais origens diferentes, comportamento típico de conta de passagem.",
     "A conta A013, criada em 15/11/2026, recebeu de A005, A006 e A007 em poucos dias. Note que essas três origens são justamente as contas que compartilham o dispositivo D1 (consulta 1): o cruzamento reforça a suspeita.",
     "A conta A014 também recebe de três origens (A008, A009 e A010), mas foi criada em 2024. O filtro por criada_em (últimos 30 dias, com referência fixa em 19/11/2026) a exclui."),
    ("q4_ciclo", "03_q4_ciclo", "Consulta 4: anel de transferências (ciclo)",
     "Dinheiro que sai de uma conta, passa por outras e volta à origem, o que pode simular movimentação sem motivo econômico. Procuramos também grupos aparentemente sem relação entre si, por isso a consulta lista os vínculos compartilhados entre os titulares.",
     "A consulta retorna dois anéis, os que vinculos vazio aparecem primeiro. O anel A037, A038, A039 não tem nenhum vínculo compartilhado entre os titulares (nem endereço, dispositivo, IP ou cartão): é o caso mais próximo de grupos aparentemente sem relação que movimentam dinheiro em círculo. O anel do enunciado (A001 a A004 e de volta a A001) tem vinculos Endereco: C001 e C002 moram no mesmo endereço E1. Isso pode indicar grupo coordenado ou apenas família; ambos os anéis merecem revisão humana. A exigência de datas crescentes ao longo do caminho é uma regra de negócio (segue o fluxo do dinheiro: cada repasse só ocorre depois de a conta receber) e, além disso, faz cada anel ser reportado uma única vez, e não uma por conta de partida (deduplica rotações). Nenhuma conta se repete no anel.",
     "As cadeias abertas (como A019, A020, A021, A022) não retornam: não voltam à conta de partida. Não há ciclo falso, porque as demais transferências do dataset nunca fecham em um nó de origem."),
    ("q5_cartao_compartilhado", "03_q5_cartao_compartilhado", "Consulta 5: cartão compartilhado",
     "O mesmo cartão associado a contas de clientes diferentes, sinal de uso de cartão de terceiros.",
     "O cartão K1 aparece nas contas A015 e A016, de C015 e C016. A consulta agrupa por cliente (e não por conta) porque o que indica uso de cartão de terceiros são titulares diferentes: um cliente com duas contas no mesmo cartão é comum.",
     "K2 está em duas contas, mas do mesmo cliente (C017), e K3 tem apenas uma conta. Nenhum dos dois atinge dois clientes distintos."),
    ("q6_cadeia_sem_historico", "03_q6_cadeia_sem_historico", "Consulta 6: cadeia entre pares sem histórico",
     "Sequência de três transferências em até 24 horas em que cada par consecutivo de contas não tem nenhuma transferência anterior ao início da cadeia (em qualquer direção), típico de dinheiro sendo empurrado rapidamente por contas descartáveis.",
     "A cadeia A019, A020, A021, A022 ocorreu em 17/11/2026 entre 09h e 20h, com valores quase iguais (900, 880 e 860), ou seja, só uma pequena fatia ficou no caminho.",
     "A cadeia do enunciado (A001 a A004) não retorna: as transferências são espaçadas por dois dias, fora da janela de 24 horas. A cadeia A033, A034, A035, A036 ocorre em menos de 24 horas, mas A035 já havia transferido para A034 antes (em 01/11/2026): falha só pelo histórico do par, pois a verificação é feita por par consecutivo."),
    ("q7_passagem_rapida", "03_q7_passagem_rapida", "Consulta 7: passagem rápida",
     "A conta recebe e repassa quase todo o valor (80% a 100%) em poucos minutos, sem reter o dinheiro, comportamento de conta de passagem.",
     "A conta A027 recebeu 1000 de A028 às 10h00 e repassou 980 a A029 às 10h04: quatro minutos depois, com 98% do valor (a consulta exige entre 80% e 100%).",
     "A conta A030 também recebe (de A031) e repassa (a A032), mas só duas horas depois, fora da janela de 10 minutos."),
]


def fmt(v):
    return ", ".join(str(x) for x in v) if isinstance(v, list) else str(v)


for chave, arq, tit, padrao, interp, ctrl in Q:
    titulo(tit, 2)
    par(padrao, negrito_ini="Padrão de fraude. ").paragraph_format.keep_with_next = True
    par("Código Cypher:", cor=ESCURO, negrito=True).paragraph_format.keep_with_next = True
    codigo(cypher(arq))
    linhas = cons[chave]
    cols = list(linhas[0])
    par(f"Resultado real ({len(linhas)} linha{'s' if len(linhas) != 1 else ''}):",
        cor=ESCURO, negrito=True).paragraph_format.keep_with_next = True
    tabela(cols, [[fmt(ln[c]) for c in cols] for ln in linhas])
    par(interp, negrito_ini="Interpretação. ")
    par(ctrl, negrito_ini="Controle negativo. ")

# ---------------------------------------------------------------- 6
titulo("6 Limitações e próximos passos")
lista([("Algoritmos de grafos (GDS): ", "o Neo4j Graph Data Science oferece detecção de comunidades, centralidade e "
        "componentes conexos que encontrariam grupos suspeitos sem definir o padrão antes. O plano gratuito do Aura "
        "não inclui a biblioteca, por isso ficou fora do protótipo."),
       ("Escala: ", "o dataset tem poucas dezenas de nós. Com milhões de clientes, consultas de caminho de tamanho "
        "variável precisariam de limites de profundidade, índices nas propriedades usadas nos filtros e testes de desempenho. "
        "Mesmo com adjacência direta, a busca ainda usa índice ou varredura de rótulo para achar o nó âncora, e o "
        "custo dominante em ciclos é a explosão de caminhos (grau elevado à potência k), que afeta qualquer modelo. "
        "Para mitigar: ancorar a consulta em contas específicas, usar janela de tempo e criar índice em TRANSFERIU(data)."),
       ("Janela de tempo: ", "os limites (30 dias, 24 horas, 10 minutos) foram escolhidos por nós e usam uma data de "
        "referência fixa. Em produção seriam parâmetros calibrados com dados reais e a data atual."),
       ("Falsos positivos: ", "uma família que divide o mesmo roteador ou um escritório com um único IP também seria "
        "marcada. Os resultados devem ser tratados como alertas para análise humana, não como prova de fraude, "
        "e podem ser combinados em uma pontuação de risco."),
       ("Dados sintéticos: ", "como os cenários foram desenhados para ativar as consultas, os resultados mostram que "
        "elas funcionam, não qual é a taxa real de acerto em dados de verdade."),
       ("Carga destrutiva: ", "o script de carga apaga o banco inteiro da instância; deve ser usado apenas em uma instância de demonstração.")])

# ---------------------------------------------------------------- 7
titulo("7 Conclusão")
par("O protótipo mostrou que um modelo de grafo expressa de forma natural as relações que importam para a "
    "detecção de fraude. Os sete padrões do enunciado viraram consultas Cypher curtas, e cada uma retornou o "
    "caso fraudulento esperado e deixou de fora o controle negativo correspondente, o que dá mais confiança de "
    "que o filtro faz o que promete. A comparação com SQL mostra que o ganho do grafo é de legibilidade e de "
    "travessia por adjacência, não de capacidade: ciclos e cadeias também são possíveis com WITH RECURSIVE.")
par("Como próximos passos, o mais valioso seria testar com dados reais anonimizados, calibrar os limites e "
    "combinar as consultas em uma pontuação de risco por conta.")

# rodape com numero de pagina
rod = sec.footer.paragraphs[0]
rod.alignment = WD_ALIGN_PARAGRAPH.CENTER
fonte(rod.add_run("CredPay Digital | Neo4j | página "), tam=9, cor=CINZA)
r = rod.add_run()
fonte(r, tam=9, cor=CINZA)
for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if tipo:
        e = OxmlElement("w:fldChar")
        e.set(qn("w:fldCharType"), tipo)
    else:
        e = OxmlElement("w:instrText")
        e.set(qn("xml:space"), "preserve")
        e.text = txt
    r._r.append(e)

saida = REL / "CredPay_Neo4j.docx"
doc.save(saida)
img.unlink()
from docx2pdf import convert  # noqa: E402

convert(str(saida), str(REL / "CredPay_Neo4j.pdf"))
print("gerado:", saida, "e PDF")
