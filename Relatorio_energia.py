##Para este projeto a base de dados utilizadas foi a do "Kaggle", https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def read_data(file_path):
    return pd.read_csv("C://Users//guilh//anaconda3//Projetos Meus//Energia//oficial//Energia_planilha - Copia.csv")

def calculate_within_limits(turbina):
    dentro_limite = []

    for _, row in turbina.iterrows():
        potencia = row['Active Power (KW)']
        pot_min = row['Curva teórica (KW)'] * 0.95
        pot_max = row['Curva teórica (KW)'] * 1.05

        if pot_min <= potencia <= pot_max:
            dentro_limite.append('Dentro')
        elif potencia == 0:
            dentro_limite.append('Zero')
        else:
            dentro_limite.append('Fora')

    turbina['Dentro Limite'] = dentro_limite
    return turbina

def create_scatter_plot(data):
    fig, ax = plt.subplots(figsize=(7, 5))  # Reduzindo a largura do gráfico

    colors_map = {'Dentro': 'blue', 'Fora': 'red', 'Zero': 'green'}

    for grupo, color in colors_map.items():
        dados_grupo = data[data['Dentro Limite'] == grupo]
        ax.scatter(dados_grupo['Velocidade do Vento'], dados_grupo['Active Power (KW)'],
                   color=color, label=grupo, s=10, alpha=0.5)

    ax.set_xlabel('Velocidade do Vento')
    ax.set_ylabel('Active Power (KW)')
    ax.legend()

    return fig

def generate_report(turbina, title, author, city):
    doc = SimpleDocTemplate("Relatorio.pdf", pagesize=letter)
    story = []

    # Cabeçalho
    header_style = getSampleStyleSheet()["Normal"]
    header_style.alignment = 1  # Centraliza o texto
    story.append(Spacer(1, -3))  # Espaço entre o início da página e o cabeçalho
    story.append(Paragraph("<b>Relatório Turbina Eólica</b>", getSampleStyleSheet()["Title"]))
    story.append(Paragraph(title, header_style))
    story.append(Paragraph("Responsável: {}".format(author), header_style))
    story.append(Paragraph("Cidade: {}".format(city), header_style))
    story.append(Paragraph("Data: {}".format(datetime.datetime.now().strftime("%Y-%m-%d")), header_style))
    story.append(Spacer(1, 170))  # Espaço entre o cabeçalho e o conteúdo do relatório

    # Gráfico com a divisão dos grupos
    fig = create_scatter_plot(turbina)
    fig.savefig("grafico.png")

    # Adicionando o gráfico ao PDF
    img = "grafico.png"
    im = plt.imread(img)
    width, height = letter
    aspect = width / height
    story.append(Paragraph("<b>Gráfico com a divisão dos grupos:</b>", getSampleStyleSheet()["Heading2"]))
    story.append(Paragraph('<img src="{}" width="350" height="230"/>'.format(img), getSampleStyleSheet()["BodyText"]))

    # Relação estatística
    dentro_limite = turbina["Dentro Limite"]
    den = round((dentro_limite.eq('Dentro').sum() / len(dentro_limite)) * 100, 2)
    fora = round((dentro_limite.eq('Fora').sum() / len(dentro_limite)) * 100, 2)
    zer = round((dentro_limite.eq('Zero').sum() / len(dentro_limite)) * 100, 2)

    story.append(Paragraph("<b>Relação estatística:</b>", getSampleStyleSheet()["Heading2"]))
    relacao = [
        "{}% estão dentro da margem do sensor".format(den),
        "{}% estão fora da margem do sensor".format(fora),
        "{}% não foram capturados pelo sensor".format(zer)
    ]
    for r in relacao:
        story.append(Paragraph(r, getSampleStyleSheet()["BodyText"]))

    story.append(Spacer(1, 10))  # Espaço entre a relação estatística e a tabela
    # Tabela
    table_data = [list(turbina.columns)] + turbina.head(10).values.tolist()
    table = Table(table_data, colWidths=[70, 90, 100, 130, 90, 80])  # Reduzindo a largura das colunas
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
                               ('TEXTCOLOR', (0, 0), (0, -1), colors.black),  # Fonte preta na primeira coluna
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Mantendo a primeira coluna em negrito
                               ('FONTSIZE', (1, 0), (-1, -1), 8),  # Reduzindo o tamanho da fonte para 8
                               ('FONTSIZE', (0, 0), (0, -1), 8),  # Reduzindo o tamanho da fonte para 8 na primeira coluna
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    story.append(Spacer(1, -10))  # Espaço entre a tabela e o final da página
    story.append(Paragraph("<b>Tabela:</b>", getSampleStyleSheet()["Heading2"]))
    story.append(table)

    # Adicionar o conteúdo ao documento
    doc.build(story)

if __name__ == "__main__":
    title = input("Qual a turbina: ")
    author = input("Digite o nome do autor: ")
    city = input("Digite o nome da cidade: ")

    file_path = "Energia_planilha.Copia.csv"
    turbina = read_data(file_path)
    turbina.columns = ['Data/hora', 'Active Power (KW)', 'Velocidade do Vento', 'Curva teórica (KW)', 'Direção do Vento']
    turbina = calculate_within_limits(turbina)
    generate_report(turbina, title, author, city)

