"""
Configurações e constantes do aplicativo INMET Data Quality Analyzer
"""

import os
from datetime import datetime

# Configurações Gerais
APP_NAME = "INMET Data Quality Analyzer"
APP_VERSION = "1.0.0"
DEVELOPER_NAME = "Dev.: Elivaldo Rocha"

# Limites de Arquivo
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Configurações de Parsing
CSV_SEPARATOR = ";"
DECIMAL_SEPARATOR = ","
NULL_VALUES = ["null", "NULL", "None", "nan", "NaN", ""]
METADATA_END_LINE = 9
HEADER_LINE = 10  # Linha com nomes das variáveis (0-indexed)

# Limites Físicos por Variável (min, max)
PHYSICAL_LIMITS = {
    "PRECIPITACAO TOTAL, DIARIO (AUT)(mm)": (0, 500),
    "PRESSAO ATMOSFERICA MEDIA DIARIA (AUT)(mB)": (900, 1050),
    "TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)": (-50, 50),
    "TEMPERATURA MAXIMA, DIARIA (AUT)(°C)": (-50, 60),
    "TEMPERATURA MEDIA, DIARIA (AUT)(°C)": (-50, 60),
    "TEMPERATURA MINIMA, DIARIA (AUT)(°C)": (-50, 60),
    "UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)": (0, 100),
    "UMIDADE RELATIVA DO AR, MINIMA DIARIA (AUT)(%)": (0, 100),
    "VENTO, RAJADA MAXIMA DIARIA (AUT)(m/s)": (0, 100),
    "VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)": (0, 50),
}

# Critérios de Qualidade
QUALITY_THRESHOLDS = {
    "completude_minima": 0.70,      # 70% de dados não-nulos
    "validade_minima": 0.90,        # 90% de dados válidos
    "consistencia_minima": 0.85,    # 85% de consistência
}

# Pesos para Índice de Qualidade Geral
QUALITY_INDEX_WEIGHTS = {
    "completude": 0.4,
    "validade": 0.4,
    "consistencia": 0.2,
}

# Critérios de Recomendação
RECOMMENDATION_CRITERIA = {
    "adequado": 80,                 # QI >= 80
    "parcialmente_adequado": 60,    # 60 <= QI < 80
    "inadequado": 0,                # QI < 60
}

# Configurações do Plotly para st.plotly_chart (config parameter)
# NOTA: Estas são opções de configuração do JavaScript, NÃO propriedades de layout
PLOTLY_CHART_CONFIG = {
    "responsive": True,
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

# Cores para Visualizações
COLORS = {
    "valid": "#1f77b4",      # Azul
    "invalid": "#ff7f0e",    # Laranja
    "missing": "#d62728",    # Vermelho
    "anomaly": "#9467bd",    # Roxo
    "good": "#2ca02c",       # Verde
    "warning": "#ff7f0e",    # Laranja
    "error": "#d62728",      # Vermelho
}

# Configurações de PDF
PDF_SETTINGS = {
    "page_size": "A4",
    "margin_top": 20,
    "margin_bottom": 20,
    "margin_left": 20,
    "margin_right": 20,
    "font_name": "Helvetica",
    "font_size": 11,
    "title_font_size": 16,
    "heading_font_size": 14,
}

# Nomes Simplificados das Variáveis (para exibição)
VARIABLE_NAMES_SHORT = {
    "PRECIPITACAO TOTAL, DIARIO (AUT)(mm)": "Precipitação (mm)",
    "PRESSAO ATMOSFERICA MEDIA DIARIA (AUT)(mB)": "Pressão (mB)",
    "TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)": "Temp. Orvalho (°C)",
    "TEMPERATURA MAXIMA, DIARIA (AUT)(°C)": "Temp. Máxima (°C)",
    "TEMPERATURA MEDIA, DIARIA (AUT)(°C)": "Temp. Média (°C)",
    "TEMPERATURA MINIMA, DIARIA (AUT)(°C)": "Temp. Mínima (°C)",
    "UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)": "Umidade Média (%)",
    "UMIDADE RELATIVA DO AR, MINIMA DIARIA (AUT)(%)": "Umidade Mínima (%)",
    "VENTO, RAJADA MAXIMA DIARIA (AUT)(m/s)": "Rajada Máxima (m/s)",
    "VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)": "Velocidade Média (m/s)",
}

# Unidades das Variáveis
VARIABLE_UNITS = {
    "PRECIPITACAO TOTAL, DIARIO (AUT)(mm)": "mm",
    "PRESSAO ATMOSFERICA MEDIA DIARIA (AUT)(mB)": "mB",
    "TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)": "°C",
    "TEMPERATURA MAXIMA, DIARIA (AUT)(°C)": "°C",
    "TEMPERATURA MEDIA, DIARIA (AUT)(°C)": "°C",
    "TEMPERATURA MINIMA, DIARIA (AUT)(°C)": "°C",
    "UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)": "%",
    "UMIDADE RELATIVA DO AR, MINIMA DIARIA (AUT)(%)": "%",
    "VENTO, RAJADA MAXIMA DIARIA (AUT)(m/s)": "m/s",
    "VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)": "m/s",
}

# Configurações de Streamlit
STREAMLIT_CONFIG = {
    "page_title": "INMET Data Quality Analyzer",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Mensagens
MESSAGES = {
    "welcome": "Bem-vindo ao INMET Data Quality Analyzer",
    "upload_prompt": "Faça upload de um arquivo CSV de estação meteorológica",
    "processing": "Processando arquivo...",
    "success": "Arquivo processado com sucesso!",
    "error": "Erro ao processar arquivo",
    "no_file": "Nenhum arquivo foi carregado",
    "file_too_large": f"Arquivo excede o limite de {MAX_FILE_SIZE_MB} MB",
}