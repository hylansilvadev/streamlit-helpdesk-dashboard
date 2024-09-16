import streamlit as st
import pandas as pd
from streamlit_apexjs import st_apexcharts

# Configura o layout da página
st.set_page_config(page_title="Helpdesk Analysis Dashboard", layout="wide")

# Carrega os dados (substitua pelo caminho correto do seu arquivo CSV)
data = pd.read_csv("app/data/data_helpdesk.csv")

# Exibe uma amostra da tabela
st.table(data.head(20))

# Função para criar gráfico de donut
def create_donut_chart(options, series, title, col):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
        st_apexcharts(options, series, 'donut', '400', '')

# Gráfico de Senioridade
seniority_counts = data['RequestorSeniority'].value_counts()
options_seniority = {
    "chart": {"type": 'donut', "toolbar": {"show": False}},
    "labels": seniority_counts.index.tolist(),
    "legend": {"show": True, "position": "bottom"}
}
series_seniority = seniority_counts.values.tolist()

# Gráfico de Satisfação
satisfaction_counts = data['Satisfaction'].value_counts()
options_satisfaction = {
    "chart": {"type": 'donut', "toolbar": {"show": False}},
    "labels": satisfaction_counts.index.tolist(),
    "legend": {"show": True, "position": "bottom"}
}
series_satisfaction = satisfaction_counts.values.tolist()

# Gráfico de FiledAgainst
filled_against_counts = data["FiledAgainst"].value_counts()
options_filled_against = {
    "chart": {"type": 'donut', "toolbar": {"show": False}},
    "labels": filled_against_counts.index.tolist(),
    "legend": {"show": True, "position": "bottom"}
}
series_filled_against = filled_against_counts.values.tolist()

# Divisão em colunas para exibir os gráficos
col1, col2, col3 = st.columns(3)
create_donut_chart(options_seniority, series_seniority, 'Distribuição de Senioridade', col1)
create_donut_chart(options_satisfaction, series_satisfaction, 'Distribuição de Satisfação do Cliente', col2)
create_donut_chart(options_filled_against, series_filled_against, 'Distribuição de FiledAgainst', col3)

# Mapeamento de satisfação para o gráfico de barras
satisfaction_map = {
    "0 - Unknown": 0,
    "1 - Unsatisfied": 1,
    "2 - Satisfied": 2,
    "3 - Highly satisfied": 3
}
data['SatisfactionValue'] = data['Satisfaction'].map(satisfaction_map)
filtered_data = data.dropna(subset=['SatisfactionValue', 'daysOpen'])

# Agrupa por Satisfação e calcula a média de dias
grouped_data = filtered_data.groupby('Satisfaction')['daysOpen'].mean().reset_index()

# Configurações do gráfico de barras (Média de Dias x Satisfação)
options_bars = {
    "chart": {"type": 'bar', "height": 350, "toolbar": {"show": False}},
    "xaxis": {"categories": grouped_data['Satisfaction'].tolist(), "title": {"text": "Níveis de Satisfação"}},
    "yaxis": {"title": {"text": "Média de dias"}},
    "legend": {"show": True, "position": "top"}
}
series_bars = [{
    "name": "Média de dias",
    "data": [round(value) for value in grouped_data['daysOpen'].tolist()]
}]
st.markdown("<h3 style='text-align: center;'>Média de dias x Satisfação</h3>", unsafe_allow_html=True)
st_apexcharts(options_bars, series_bars, 'bar', '500', '')

# Criando a crosstab para Severidade vs Prioridade
severity_priority_ct = pd.crosstab(data['Severity'], data['Priority'])

# Preparação dos dados de Severidade vs Prioridade para o slope chart
series_severity_priority_slope = []

for severity, row in severity_priority_ct.iterrows():
    for i, priority in enumerate(severity_priority_ct.columns):
        if i < len(severity_priority_ct.columns) - 1:
            series_severity_priority_slope.append({
                "name": severity,
                "data": [
                    {"x": priority, "y": int(row[priority])},  # Conversão para int
                    {"x": severity_priority_ct.columns[i + 1], "y": int(row[severity_priority_ct.columns[i + 1]])}  # Conversão para int
                ]
            })

# Configurações para o gráfico de slope chart (Severidade vs Prioridade)
options_severity_priority_slope = {
    "chart": {"type": 'line', "height": 350, "toolbar": {"show": False}},
    "xaxis": {"categories": severity_priority_ct.columns.tolist(), "title": {"text": "Prioridade"}},
    "yaxis": {"title": {"text": "Número de Tickets"}},
    "stroke": {"curve": 'smooth'},
    "markers": {"size": 5},
    "legend": {"show": True, "position": "top"},
    "tooltip": {"shared": True},
}

# Exibe o gráfico de slope chart de Severidade vs Prioridade dos Tickets
st.markdown("<h3 style='text-align: center;'>Severidade vs Prioridade dos Tickets - Slope Chart</h3>", unsafe_allow_html=True)
st_apexcharts(options_severity_priority_slope, series_severity_priority_slope, 'line', '900', '')
