# Análise da Estrutura do Arquivo INMET

## Informações Gerais do Arquivo

**Arquivo**: dados_A201_D_2003-01-19_2024-12-31.csv
**Tamanho**: 448 KB
**Número de linhas**: 8030
**Período**: 2003-01-19 a 2024-12-31 (21 anos)
**Periodicidade**: Diária

## Metadados do Arquivo (Linhas 1-9)

O arquivo começa com informações de metadados em linhas separadas:

```
Codigo Estacao: A201
Latitude: -1.41111111
Longitude: -48.43944444
Altitude: 21.17
Situacao: Pane
Data Inicial: 2003-01-19
Data Final: 2024-12-31
Periodicidade da Medicao: Diaria
```

**Linha 10**: Vazia
**Linha 11**: Cabeçalho com nomes das variáveis (separadas por `;`)

## Variáveis Disponíveis (11 colunas)

1. **Data Medicao** - Data da medição (formato YYYY-MM-DD)
2. **PRECIPITACAO TOTAL, DIARIO (AUT)(mm)** - Precipitação total diária em mm
3. **PRESSAO ATMOSFERICA MEDIA DIARIA (AUT)(mB)** - Pressão atmosférica média em mB
4. **TEMPERATURA DO PONTO DE ORVALHO MEDIA DIARIA (AUT)(°C)** - Temperatura do ponto de orvalho em °C
5. **TEMPERATURA MAXIMA, DIARIA (AUT)(°C)** - Temperatura máxima em °C
6. **TEMPERATURA MEDIA, DIARIA (AUT)(°C)** - Temperatura média em °C
7. **TEMPERATURA MINIMA, DIARIA (AUT)(°C)** - Temperatura mínima em °C
8. **UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)** - Umidade relativa média em %
9. **UMIDADE RELATIVA DO AR, MINIMA DIARIA (AUT)(%)** - Umidade relativa mínima em %
10. **VENTO, RAJADA MAXIMA DIARIA (AUT)(m/s)** - Rajada máxima de vento em m/s
11. **VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)** - Velocidade média do vento em m/s

## Características dos Dados

- **Separador**: Ponto-e-vírgula (`;`)
- **Decimal**: Vírgula (`,`)
- **Valores Nulos**: Representados como `null`
- **Dados Faltantes**: Comuns nos primeiros registros (2003-01-19, 2003-01-20)
- **Anomalias Observadas**: Alguns valores começam com vírgula (ex: `,9`, `,2`, `,6`, `,8`)

## Padrões de Qualidade Observados

1. **Dados Faltantes Iniciais**: As primeiras datas têm muitos valores `null`
2. **Valores Incompletos**: Alguns valores numéricos começam com vírgula (formato de número incompleto)
3. **Consistência Temporal**: Sequência de datas contínua (sem saltos)
4. **Completude Variável**: Diferentes variáveis têm diferentes proporções de dados faltantes

## Recomendações para o App

1. Identificar automaticamente a linha de cabeçalho (linha 11)
2. Extrair metadados das linhas 1-9
3. Detectar e corrigir valores numéricos malformados (começando com vírgula)
4. Calcular estatísticas de completude por variável
5. Identificar períodos contínuos de dados faltantes
6. Validar ranges esperados para cada variável meteorológica
