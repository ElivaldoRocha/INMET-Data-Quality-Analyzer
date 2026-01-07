# Resumo Técnico - INMET Data Quality Analyzer

## Visão Geral do Projeto

O **INMET Data Quality Analyzer** é um aplicativo Streamlit desenvolvido para análise automatizada de qualidade de dados de estações meteorológicas automáticas do Instituto Nacional de Meteorologia (INMET). O sistema implementa métodos estatísticos avançados para detecção de anomalias, validação de dados e geração de relatórios científicos.

## Arquitetura do Sistema

### Camadas de Processamento

```
┌─────────────────────────────────────┐
│   Interface Streamlit (app.py)      │
│   - Upload de arquivos              │
│   - Visualizações interativas       │
│   - Seletor de variáveis            │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Módulos de Processamento          │
│   - data_loader.py                  │
│   - data_validator.py               │
│   - quality_metrics.py              │
│   - visualizations.py               │
│   - report_generator.py             │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Bibliotecas Científicas           │
│   - Pandas (manipulação de dados)   │
│   - NumPy (computação numérica)     │
│   - SciPy (estatística)             │
│   - Plotly (visualizações)          │
│   - ReportLab (geração de PDF)      │
└─────────────────────────────────────┘
```

## Módulos Principais

### 1. data_loader.py (INMETDataLoader)

**Responsabilidades:**
- Carregamento de arquivos CSV com suporte a até 200 MB
- Extração automática de metadados (linhas 1-9)
- Identificação automática de linha de cabeçalho
- Parsing com tratamento de separadores (`;`) e decimais (`,`)
- Correção de valores malformados
- Cache de dados para performance

**Métodos Principais:**
- `load_data()`: Carrega e processa arquivo
- `extract_metadata()`: Extrai informações da estação
- `find_header_line()`: Identifica cabeçalho automaticamente
- `fix_malformed_numbers()`: Corrige valores incompletos

### 2. data_validator.py (DataValidator)

**Responsabilidades:**
- Validação de limites físicos por variável
- Detecção de outliers (IQR, Z-score)
- Detecção de mudanças abruptas (change points)
- Análise de padrões de dados faltantes
- Validação de sequência de datas

**Métodos Principais:**
- `validate_physical_limits()`: Verifica limites físicos
- `detect_outliers_iqr()`: Detecta outliers por IQR
- `detect_outliers_zscore()`: Detecta outliers por Z-score
- `detect_change_points()`: Identifica mudanças abruptas
- `detect_missing_data_patterns()`: Analisa dados faltantes
- `validate_date_sequence()`: Valida sequência temporal

### 3. quality_metrics.py (QualityMetricsCalculator)

**Responsabilidades:**
- Cálculo de completude (% dados não-nulos)
- Cálculo de validade (% dados dentro de limites)
- Cálculo de consistência (ausência de anomalias)
- Cálculo de índice de qualidade geral (0-100)
- Estatísticas descritivas por variável
- Recomendações de usabilidade científica

**Fórmula do Índice de Qualidade:**
```
QI = (Completude × 0.4 + Validade × 0.4 + Consistência × 0.2) × 100
```

**Métodos Principais:**
- `calculate_completeness()`: Calcula completude
- `calculate_validity()`: Calcula validade
- `calculate_consistency()`: Calcula consistência
- `calculate_quality_index()`: Calcula índice geral
- `get_recommendation()`: Retorna recomendação de uso
- `get_variable_quality_report()`: Relatório detalhado por variável

### 4. visualizations.py (Visualizer)

**Responsabilidades:**
- Criação de gráficos interativos com Plotly
- Série temporal com dados válidos/faltantes
- Calendar plot (heatmap de dias)
- Distribuição (histograma e box plot)
- Detecção de outliers
- Comparação de qualidade entre variáveis
- Heatmap de dados faltantes

**Gráficos Implementados:**
- `plot_time_series()`: Série temporal
- `plot_distribution()`: Histograma com média
- `plot_box_plot()`: Box plot com desvio padrão
- `plot_missing_data_heatmap()`: Heatmap de completude
- `plot_calendar_heatmap()`: Calendar plot
- `plot_quality_gauge()`: Medidor de qualidade
- `plot_quality_comparison()`: Comparação de variáveis
- `plot_outliers()`: Visualização de outliers

### 5. report_generator.py (ReportGenerator)

**Responsabilidades:**
- Geração de relatórios em PDF
- Estruturação de conteúdo (capa, resumo, análises)
- Inclusão de tabelas com métricas
- Rodapé com data, hora e desenvolvedor
- Suporte a figuras Plotly (futuro)

**Seções do Relatório:**
1. Capa com informações da estação
2. Resumo executivo com recomendação
3. Metadados da estação
4. Análise de completude
5. Análise de validade
6. Índices de qualidade por variável
7. Rodapé com data e desenvolvedor

## Métodos Estatísticos Implementados

### Detecção de Outliers

**Método IQR (Interquartile Range):**
```
Q1 = 25º percentil
Q3 = 75º percentil
IQR = Q3 - Q1
Outlier se: x < Q1 - 1.5×IQR ou x > Q3 + 1.5×IQR
```

**Método Z-score:**
```
Z = (x - μ) / σ
Outlier se: |Z| > 3.0
```

### Detecção de Mudanças Abruptas

```
Média móvel: rolling_mean(window=30)
Desvio padrão móvel: rolling_std(window=30)
Change point se: |valor - rolling_mean| > 2 × rolling_std
```

### Validação de Limites Físicos

Cada variável tem limites definidos em `config.py`:
```python
PHYSICAL_LIMITS = {
    'TEMPERATURA MAXIMA': (-50, 60),
    'UMIDADE RELATIVA': (0, 100),
    'PRESSAO ATMOSFERICA': (900, 1050),
    # ...
}
```

## Fluxo de Processamento

```
1. Upload de arquivo CSV
   ↓
2. Extração de metadados (linhas 1-9)
   ↓
3. Identificação de cabeçalho (linha 11)
   ↓
4. Parsing do CSV com tratamento de decimais
   ↓
5. Conversão de datas e correção de valores
   ↓
6. Validação de limites físicos
   ↓
7. Detecção de outliers (IQR e Z-score)
   ↓
8. Cálculo de métricas de qualidade
   ↓
9. Geração de visualizações interativas
   ↓
10. Geração de relatório em PDF
```

## Otimizações de Performance

### Cache de Dados
```python
@st.cache_data
def load_and_process_file(uploaded_file):
    # Processamento em cache
```

### Processamento Eficiente
- Uso de `dtype_backend='numpy_nullable'` para economia de memória
- Operações vetorizadas com NumPy/Pandas
- Lazy loading de visualizações

### Tratamento de Arquivos Grandes
- Suporte a arquivos de até 200 MB
- Processamento sem carregamento completo em memória
- Indicador de progresso durante processamento

## Limites Físicos Configurados

| Variável | Mínimo | Máximo | Unidade |
|----------|--------|--------|---------|
| Precipitação | 0 | 500 | mm |
| Pressão Atmosférica | 900 | 1050 | mB |
| Temperatura Orvalho | -50 | 50 | °C |
| Temperatura Máxima | -50 | 60 | °C |
| Temperatura Média | -50 | 60 | °C |
| Temperatura Mínima | -50 | 60 | °C |
| Umidade Relativa Média | 0 | 100 | % |
| Umidade Relativa Mínima | 0 | 100 | % |
| Rajada Máxima Vento | 0 | 100 | m/s |
| Velocidade Média Vento | 0 | 50 | m/s |

## Critérios de Qualidade

### Completude Mínima
- Padrão: 70% de dados não-nulos
- Configurável em `config.py`

### Validade Mínima
- Padrão: 90% de dados dentro de limites
- Configurável em `config.py`

### Consistência Mínima
- Padrão: 85% sem anomalias
- Configurável em `config.py`

### Recomendações
- **Adequado**: QI ≥ 80 → Uso científico recomendado
- **Parcialmente Adequado**: 60 ≤ QI < 80 → Revisar antes de usar
- **Inadequado**: QI < 60 → Não recomendado para uso científico

## Dependências

| Biblioteca | Versão | Propósito |
|-----------|--------|----------|
| streamlit | ≥1.28.0 | Framework web |
| pandas | ≥2.0.0 | Manipulação de dados |
| numpy | ≥1.24.0 | Computação numérica |
| plotly | ≥5.17.0 | Visualizações interativas |
| scipy | ≥1.11.0 | Análise estatística |
| scikit-learn | ≥1.3.0 | Machine learning |
| reportlab | ≥4.0.0 | Geração de PDF |
| python-dateutil | ≥2.8.2 | Manipulação de datas |

## Segurança

- Validação de entrada de arquivo
- Limite de tamanho (200 MB)
- Sanitização de nomes de arquivo
- Sem armazenamento permanente
- Processamento apenas em memória

## Extensibilidade

O projeto foi estruturado para facilitar:
- Adição de novas variáveis meteorológicas
- Implementação de novos métodos de validação
- Suporte a diferentes formatos de arquivo
- Integração com APIs externas
- Customização de limites físicos

## Testes Realizados

### Teste com Arquivo Fornecido
```
Arquivo: dados_A201_D_2003-01-19_2024-12-31.csv
Tamanho: 448 KB
Linhas: 8.018
Período: 2003-01-19 a 2024-12-31 (21 anos)
Variáveis: 11

Resultados:
✓ Carregamento: Sucesso
✓ Validação: 10 variáveis validadas
✓ Métricas: Índice de Qualidade = 86.77/100
✓ Recomendação: Adequado
```

## Próximas Melhorias

1. **Suporte a Múltiplas Estações**: Análise comparativa
2. **Machine Learning**: Previsão de anomalias
3. **API REST**: Integração com sistemas externos
4. **Banco de Dados**: Armazenamento de histórico
5. **Gráficos 3D**: Visualizações avançadas
6. **Exportação**: Suporte a Excel e outros formatos

## Referências Científicas

- Durre et al. (2010): "Comprehensive Automated Quality Assurance of Daily Surface Observations"
- NOAA GHCN-Daily: Procedimentos de controle de qualidade
- Métodos de preenchimento de falhas em dados meteorológicos
- Técnicas de interpolação espacial para dados climáticos

## Conclusão

O INMET Data Quality Analyzer fornece uma solução completa e automatizada para avaliação de qualidade de dados meteorológicos. Através de métodos estatísticos robustos e visualizações interativas, permite que pesquisadores e meteorologistas identifiquem rapidamente problemas nos dados e tomem decisões informadas sobre sua usabilidade científica.
