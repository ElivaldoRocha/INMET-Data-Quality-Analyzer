# Arquitetura do Aplicativo Streamlit - Análise de Qualidade de Dados INMET

## Visão Geral

Aplicativo Streamlit para análise de qualidade de dados de estações meteorológicas automáticas do INMET, com suporte a arquivos de até 200 MB, processamento assíncrono, visualizações interativas e geração de relatórios em PDF.

## Estrutura do Projeto

```
inmet-data-quality-analyzer/
├── app.py                          # Aplicativo principal Streamlit
├── modules/
│   ├── __init__.py
│   ├── data_loader.py             # Carregamento e parsing de arquivos CSV
│   ├── data_validator.py          # Validação e detecção de anomalias
│   ├── quality_metrics.py         # Cálculo de métricas de qualidade
│   ├── visualizations.py          # Gráficos e visualizações
│   ├── report_generator.py        # Geração de relatórios em PDF
│   └── utils.py                   # Funções utilitárias
├── config.py                       # Configurações e constantes
├── requirements.txt                # Dependências Python
├── pyproject.toml                  # Configuração do projeto uv
└── README.md                       # Documentação
```

## Dependências Principais

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
scipy>=1.11.0
scikit-learn>=1.3.0
reportlab>=4.0.0
weasyprint>=60.0
python-dateutil>=2.8.2
```

## Fluxo de Funcionamento

### 1. Carregamento de Dados (data_loader.py)

**Funcionalidades:**
- Upload de arquivo CSV via interface Streamlit
- Detecção automática de metadados (linhas 1-9)
- Identificação automática da linha de cabeçalho
- Parsing com tratamento de separadores (`;`) e decimais (`,`)
- Conversão de valores `null` para NaN
- Correção de valores malformados (começando com vírgula)
- Processamento em chunks para arquivos grandes (até 200 MB)
- Cache de dados para performance

**Saídas:**
- DataFrame com dados limpos
- Dicionário de metadados
- Informações de estrutura (número de linhas, colunas, período)

### 2. Validação de Dados (data_validator.py)

**Funcionalidades:**
- Validação de limites físicos por variável
- Detecção de outliers (IQR, Z-score)
- Identificação de valores anômalos
- Detecção de mudanças abruptas (change point detection)
- Validação de sequência de datas
- Detecção de duplicatas

**Saídas:**
- Flags de validação por registro
- Relatório de anomalias encontradas
- Índices de registros problemáticos

### 3. Métricas de Qualidade (quality_metrics.py)

**Indicadores Calculados:**

**Por Variável:**
- Completude (% de dados não-nulos)
- Validade (% de dados dentro de limites)
- Média, mediana, desvio padrão
- Mínimo e máximo observados
- Número de outliers detectados
- Períodos de dados faltantes

**Geral:**
- Índice de qualidade geral (0-100)
- Proporção de dados válidos
- Proporção de dados inválidos
- Proporção de dados faltantes
- Recomendação de usabilidade científica

**Índice de Qualidade Geral (fórmula):**
```
QI = (Completude × 0.4 + Validade × 0.4 + Consistência × 0.2) × 100
```

### 4. Visualizações (visualizations.py)

**Gráficos Interativos (Plotly):**
1. **Série Temporal** - Linha com dados válidos/inválidos destacados
2. **Calendar Plot** - Heatmap de completude/qualidade por dia
3. **Distribuição** - Histograma e box plot
4. **Outliers** - Scatter plot destacando anomalias
5. **Dados Faltantes** - Heatmap de padrões de falta
6. **Estatísticas Descritivas** - Tabelas interativas
7. **Comparação de Variáveis** - Correlação e scatter plots

**Funcionalidades:**
- Zoom e pan interativos
- Hover com informações detalhadas
- Download de imagens PNG
- Responsividade

### 5. Interface Streamlit (app.py)

**Layout Principal:**

**Seção 1: Upload e Metadados**
- Campo de upload de arquivo CSV
- Exibição automática de metadados
- Seletor de variável para análise
- Indicador de progresso para processamento

**Seção 2: Visão Geral de Qualidade**
- Cartão com índice de qualidade geral (0-100)
- Indicadores de completude, validade, consistência
- Recomendação científica (Adequado/Parcialmente Adequado/Inadequado)
- Resumo de dados faltantes e inválidos

**Seção 3: Análise Detalhada**
- Abas para diferentes visualizações
- Gráficos interativos por variável
- Tabelas de estatísticas descritivas
- Detalhes de anomalias encontradas

**Seção 4: Relatório e Downloads**
- Botão para gerar relatório em PDF
- Botões para download de gráficos individuais
- Opções de formato de exportação

### 6. Geração de Relatório PDF (report_generator.py)

**Conteúdo do Relatório:**

1. **Capa**
   - Título: "Relatório de Qualidade de Dados Meteorológicos"
   - Nome da estação
   - Período analisado
   - Data e hora de geração
   - Desenvolvedor

2. **Resumo Executivo**
   - Índice de qualidade geral
   - Recomendação de uso
   - Principais achados

3. **Metadados da Estação**
   - Código, latitude, longitude, altitude
   - Situação, período, periodicidade

4. **Análise por Variável**
   - Tabela com métricas (completude, validade, etc.)
   - Gráficos de série temporal
   - Gráficos de distribuição

5. **Análise de Qualidade**
   - Dados faltantes (quantidade, períodos)
   - Dados inválidos (quantidade, tipos)
   - Outliers detectados
   - Anomalias temporais

6. **Recomendações**
   - Adequabilidade para uso científico
   - Sugestões de tratamento
   - Métodos de preenchimento (se aplicável)

7. **Rodapé**
   - Data e hora de geração
   - Nome do sistema: "INMET Data Quality Analyzer"
   - Desenvolvedor: [Nome do Usuário]
   - Página número

## Funcionalidades Avançadas

### 1. Processamento Assíncrono
- Uso de `@st.cache_data` para cache de dados
- Processamento em chunks para arquivos grandes
- Indicador de progresso com `st.progress()`

### 2. Inteligência de Metadados
- Detecção automática de linha de cabeçalho
- Extração de metadados estruturados
- Validação de formato esperado

### 3. Seletor de Variáveis
- Dropdown com todas as variáveis disponíveis
- Pré-seleção da primeira variável
- Atualização dinâmica de visualizações

### 4. Download de Gráficos
- Exportação de cada gráfico como PNG
- Resolução alta (300 DPI para relatórios)
- Nomes descritivos com timestamp

### 5. Validação Científica
- Limites físicos por tipo de variável
- Comparação com dados históricos
- Recomendação baseada em critérios estabelecidos

### 6. Análise Temporal
- Detecção de períodos de dados faltantes
- Análise de mudanças abruptas
- Tendências temporais

## Constantes de Validação (config.py)

```python
# Limites físicos por variável
PHYSICAL_LIMITS = {
    'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)': (0, 500),
    'PRESSAO ATMOSFERICA MEDIA DIARIA (AUT)(mB)': (900, 1050),
    'TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)': (-50, 50),
    'TEMPERATURA MAXIMA, DIARIA (AUT)(°C)': (-50, 60),
    'TEMPERATURA MEDIA, DIARIA (AUT)(°C)': (-50, 60),
    'TEMPERATURA MINIMA, DIARIA (AUT)(°C)': (-50, 60),
    'UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)': (0, 100),
    'UMIDADE RELATIVA DO AR, MINIMA DIARIA (AUT)(%)': (0, 100),
    'VENTO, RAJADA MAXIMA DIARIA (AUT)(m/s)': (0, 100),
    'VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)': (0, 50),
}

# Critérios de qualidade
QUALITY_THRESHOLDS = {
    'completude_minima': 0.70,  # 70% de dados não-nulos
    'validade_minima': 0.90,    # 90% de dados válidos
    'consistencia_minima': 0.85, # 85% de consistência
}
```

## Tratamento de Performance

1. **Cache de Dados**: `@st.cache_data` para evitar reprocessamento
2. **Processamento em Chunks**: Leitura de arquivos grandes em partes
3. **Lazy Loading**: Visualizações carregadas sob demanda
4. **Otimização de Memória**: Uso eficiente de tipos de dados (int32, float32)
5. **Paralelização**: Cálculos independentes em paralelo (se necessário)

## Tratamento de Erros

- Validação de formato de arquivo
- Tratamento de exceções em parsing
- Mensagens de erro claras ao usuário
- Logging de operações
- Recuperação graceful de falhas

## Segurança

- Validação de entrada de arquivo
- Limite de tamanho de arquivo (200 MB)
- Sanitização de nomes de arquivo
- Sem armazenamento permanente de dados
- Dados processados apenas em memória

## Extensibilidade

- Módulos independentes para fácil manutenção
- Fácil adição de novas variáveis
- Suporte a diferentes formatos de arquivo (futuro)
- API para integração com outros sistemas
