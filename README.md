# INMET Data Quality Analyzer

Aplicativo Streamlit para análise de qualidade de dados de estações meteorológicas automáticas do Instituto Nacional de Meteorologia (INMET).

## Características Principais

### 📊 Análise Completa de Qualidade
- **Índice de Qualidade Geral** (0-100) baseado em completude, validade e consistência
- **Métricas por Variável**: Completude, validade, consistência, estatísticas descritivas
- **Detecção de Anomalias**: Outliers (IQR, Z-score), mudanças abruptas, dados faltantes
- **Validação de Limites Físicos**: Verificação automática de valores dentro de limites esperados

### 📈 Visualizações Interativas
- **Série Temporal**: Gráficos de linha com dados válidos e faltantes destacados
- **Calendar Plot**: Heatmap de completude por dia
- **Distribuição**: Histogramas e box plots
- **Heatmap de Dados Faltantes**: Análise temporal de padrões de falta
- **Detecção de Outliers**: Visualização de anomalias detectadas
- **Comparação de Qualidade**: Índices de qualidade por variável

### 📄 Relatórios
- **Relatório em PDF**: Documento completo com análise de qualidade
- **Download de Gráficos**: Exportação de visualizações individuais
- **Metadados**: Informações automáticas da estação
- **Rodapé Personalizado**: Data, hora e desenvolvedor

### 🔧 Funcionalidades Avançadas
- **Upload de Arquivos**: Suporte a arquivos de até 200 MB
- **Processamento Assíncrono**: Indicador de progresso durante processamento
- **Cache Inteligente**: Otimização de performance para análises repetidas
- **Seletor de Variáveis**: Análise detalhada por variável meteorológica
- **Metadados Automáticos**: Extração automática de informações da estação

## Estrutura do Projeto

```
inmet-analyzer/
├── app.py                          # Aplicativo principal Streamlit
├── config.py                       # Configurações e constantes
├── modules/
│   ├── __init__.py
│   ├── data_loader.py             # Carregamento e parsing de arquivos
│   ├── data_validator.py          # Validação e detecção de anomalias
│   ├── quality_metrics.py         # Cálculo de métricas de qualidade
│   ├── visualizations.py          # Gráficos interativos
│   └── report_generator.py        # Geração de relatórios em PDF
├── requirements.txt                # Dependências Python
├── pyproject.toml                  # Configuração do projeto uv
└── README.md                       # Este arquivo
```

## Instalação

### Usando pip

```bash
# Clone ou navegue até o diretório do projeto
cd inmet-analyzer

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### Usando uv (recomendado)

```bash
# Instale uv se ainda não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navegue até o diretório do projeto
cd inmet-analyzer

# Crie um ambiente virtual e instale dependências
uv venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Uso

### Executar o Aplicativo

```bash
# Com pip
streamlit run app.py

# Com uv
uv run streamlit run app.py
```

O aplicativo abrirá em `http://localhost:8501`

### Fluxo de Uso

1. **Upload do Arquivo**: Faça upload de um arquivo CSV de estação meteorológica
2. **Análise Automática**: O aplicativo processa e analisa os dados automaticamente
3. **Visualização**: Explore gráficos interativos e estatísticas
4. **Análise Detalhada**: Selecione uma variável para análise profunda
5. **Geração de Relatório**: Gere um relatório completo em PDF
6. **Download**: Baixe o relatório ou gráficos individuais

## Formato de Arquivo Esperado

O aplicativo espera arquivos CSV do INMET com a seguinte estrutura:

```
Codigo Estacao: A201
Latitude: -1.41111111
Longitude: -48.43944444
Altitude: 21.17
Situacao: Pane
Data Inicial: 2003-01-19
Data Final: 2024-12-31
Periodicidade da Medicao: Diaria

Data Medicao;PRECIPITACAO TOTAL, DIARIO (AUT)(mm);...
2003-01-19;null;...
2003-01-20;5.2;...
```

### Características do Formato
- **Metadados**: Linhas 1-9 com informações da estação
- **Cabeçalho**: Linha 11 com nomes das variáveis
- **Separador**: Ponto-e-vírgula (`;`)
- **Decimais**: Vírgula (`,`)
- **Valores Nulos**: Representados como `null`

## Variáveis Suportadas

O aplicativo suporta as seguintes variáveis meteorológicas:

1. **Precipitação Total Diária** (mm)
2. **Pressão Atmosférica Média Diária** (mB)
3. **Temperatura do Ponto de Orvalho Média Diária** (°C)
4. **Temperatura Máxima Diária** (°C)
5. **Temperatura Média Diária** (°C)
6. **Temperatura Mínima Diária** (°C)
7. **Umidade Relativa do Ar Média Diária** (%)
8. **Umidade Relativa do Ar Mínima Diária** (%)
9. **Vento - Rajada Máxima Diária** (m/s)
10. **Vento - Velocidade Média Diária** (m/s)

## Métricas de Qualidade

### Completude
Percentual de dados não-nulos em relação ao total de registros.

### Validade
Percentual de dados dentro de limites físicos aceitáveis para cada variável.

### Consistência
Percentual de dados sem anomalias detectadas (outliers, mudanças abruptas).

### Índice de Qualidade Geral
Cálculo ponderado:
```
QI = (Completude × 0.4 + Validade × 0.4 + Consistência × 0.2) × 100
```

### Recomendação de Uso
- **Adequado** (QI ≥ 80): Dados de qualidade adequada para uso científico
- **Parcialmente Adequado** (60 ≤ QI < 80): Dados com qualidade moderada, recomenda-se revisão
- **Inadequado** (QI < 60): Dados com qualidade insuficiente para uso científico

## Métodos Estatísticos Utilizados

### Detecção de Outliers
- **IQR (Interquartile Range)**: Método robusto para identificar valores extremos
- **Z-score**: Detecção de valores fora de 3 desvios padrão da média

### Validação de Dados
- **Limites Físicos**: Verificação de valores dentro de intervalos esperados
- **Validação de Sequência de Datas**: Detecção de gaps e inconsistências temporais
- **Detecção de Mudanças Abruptas**: Identificação de change points

### Análise de Dados Faltantes
- **Padrões Temporais**: Identificação de períodos contínuos de falta
- **Distribuição**: Análise da proporção e localização de dados faltantes

## Dependências

- **streamlit**: Framework web para aplicações Python
- **pandas**: Manipulação e análise de dados
- **numpy**: Computação numérica
- **plotly**: Visualizações interativas
- **scipy**: Algoritmos científicos
- **scikit-learn**: Machine learning e análise estatística
- **reportlab**: Geração de PDFs
- **weasyprint**: Renderização de HTML para PDF
- **python-dateutil**: Manipulação de datas

## Configuração

As configurações principais estão em `config.py`:

```python
# Limites de arquivo
MAX_FILE_SIZE_MB = 200

# Critérios de qualidade
QUALITY_THRESHOLDS = {
    'completude_minima': 0.70,
    'validade_minima': 0.90,
    'consistencia_minima': 0.85,
}

# Pesos para índice de qualidade
QUALITY_INDEX_WEIGHTS = {
    'completude': 0.4,
    'validade': 0.4,
    'consistencia': 0.2,
}
```

## Performance

O aplicativo foi otimizado para lidar com arquivos de até 200 MB:

- **Cache de Dados**: Uso de `@st.cache_data` para evitar reprocessamento
- **Processamento em Chunks**: Leitura eficiente de arquivos grandes
- **Lazy Loading**: Visualizações carregadas sob demanda
- **Otimização de Memória**: Uso eficiente de tipos de dados

## Tratamento de Erros

O aplicativo inclui tratamento robusto de erros:

- Validação de formato de arquivo
- Tratamento de exceções em parsing
- Mensagens de erro claras ao usuário
- Recuperação graceful de falhas

## Segurança

- Validação de entrada de arquivo
- Limite de tamanho de arquivo
- Sanitização de nomes de arquivo
- Sem armazenamento permanente de dados
- Dados processados apenas em memória

## Extensibilidade

O projeto foi estruturado para facilitar extensões:

- Módulos independentes para fácil manutenção
- Fácil adição de novas variáveis
- Suporte a diferentes formatos de arquivo (futuro)
- API para integração com outros sistemas

## Contribuindo

Para contribuir com melhorias:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## Suporte

Para suporte, abra uma issue no repositório do projeto.

## Referências

- [INMET - Instituto Nacional de Meteorologia](https://www.inmet.gov.br/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [NOAA Quality Assurance Procedures](https://www.ncei.noaa.gov/pub/data/ghcn/daily/papers/durre-menne-etal2010.pdf)

## Changelog

### v1.0.0 (2024)
- Versão inicial do aplicativo
- Análise completa de qualidade de dados
- Visualizações interativas com Plotly
- Geração de relatórios em PDF
- Suporte a arquivos de até 200 MB
