# Guia Rápido - INMET Data Quality Analyzer

## Instalação Rápida

### 1. Clonar ou Preparar o Projeto

```bash
cd inmet-analyzer
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

## Executar o Aplicativo

```bash
streamlit run app.py
```

O aplicativo abrirá em `http://localhost:8501`

## Como Usar

### Passo 1: Upload do Arquivo
- Clique em "Faça upload de um arquivo CSV" na barra lateral
- Selecione um arquivo CSV de estação meteorológica do INMET
- O aplicativo processará automaticamente

### Passo 2: Visualizar Metadados
- Os metadados da estação aparecem automaticamente
- Código, latitude, longitude, altitude, etc.

### Passo 3: Análise de Qualidade
- **Visão Geral**: Índice de qualidade geral (0-100)
- **Completude**: % de dados não-nulos
- **Validade**: % de dados dentro de limites físicos
- **Consistência**: % de dados sem anomalias

### Passo 4: Análise Detalhada
- Selecione uma variável no dropdown
- Explore gráficos interativos:
  - Série temporal
  - Distribuição
  - Estatísticas descritivas
  - Outliers detectados
  - Índices de qualidade

### Passo 5: Gerar Relatório
- Clique em "📥 Gerar Relatório em PDF"
- Baixe o relatório completo
- Inclui análise detalhada e recomendações

## Interpretação dos Resultados

### Índice de Qualidade Geral

| Faixa | Interpretação | Recomendação |
|-------|---------------|--------------|
| 80-100 | Adequado | Dados de qualidade adequada para uso científico |
| 60-79 | Parcialmente Adequado | Dados com qualidade moderada, revise antes de usar |
| 0-59 | Inadequado | Dados com qualidade insuficiente para uso científico |

### Métricas Principais

**Completude**: Proporção de dados não-nulos
- 100%: Sem dados faltantes
- 70-99%: Alguns dados faltantes
- <70%: Muitos dados faltantes

**Validade**: Proporção de dados dentro de limites físicos
- 100%: Todos os dados válidos
- 90-99%: Alguns valores fora de limites
- <90%: Muitos valores inválidos

**Consistência**: Ausência de anomalias
- 100%: Sem anomalias detectadas
- 85-99%: Poucas anomalias
- <85%: Muitas anomalias detectadas

## Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate
```

### Erro: "Arquivo excede o limite"
- O aplicativo suporta até 200 MB
- Divida arquivos maiores em períodos menores

### Erro: "Sem dados disponíveis"
- Verifique se o arquivo está no formato correto
- Certifique-se de que tem dados meteorológicos válidos

## Formato de Arquivo Esperado

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

## Dicas e Truques

### 1. Otimizar Performance
- Para arquivos grandes, use dados de períodos menores
- O cache automático acelera análises repetidas

### 2. Exportar Gráficos
- Passe o mouse sobre os gráficos
- Clique no ícone de câmera para salvar como PNG
- Use em apresentações e artigos

### 3. Análise Comparativa
- Compare múltiplas variáveis usando a aba "Comparação de Qualidade"
- Identifique variáveis com problemas

### 4. Relatórios Customizados
- Gere relatórios em PDF com um clique
- Inclui todas as análises e recomendações
- Ideal para documentação científica

## Variáveis Suportadas

1. Precipitação Total Diária (mm)
2. Pressão Atmosférica Média Diária (mB)
3. Temperatura do Ponto de Orvalho Média Diária (°C)
4. Temperatura Máxima Diária (°C)
5. Temperatura Média Diária (°C)
6. Temperatura Mínima Diária (°C)
7. Umidade Relativa do Ar Média Diária (%)
8. Umidade Relativa do Ar Mínima Diária (%)
9. Vento - Rajada Máxima Diária (m/s)
10. Vento - Velocidade Média Diária (m/s)

## Contato e Suporte

Para dúvidas ou sugestões, consulte a documentação completa em `README.md`.

## Referências

- [INMET - Instituto Nacional de Meteorologia](https://www.inmet.gov.br/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
