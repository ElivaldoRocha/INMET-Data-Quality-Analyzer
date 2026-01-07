"""
Aplicativo Streamlit - INMET Data Quality Analyzer
Análise de qualidade de dados de estações meteorológicas automáticas
"""

import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Importa módulos
from modules import (
    INMETDataLoader,
    DataValidator,
    QualityMetricsCalculator,
    Visualizer,
    ReportGenerator,
)
from config import (
    STREAMLIT_CONFIG, MESSAGES, VARIABLE_NAMES_SHORT,
    MAX_FILE_SIZE_MB, RECOMMENDATION_CRITERIA
)

# Configuração da página
st.set_page_config(**STREAMLIT_CONFIG)

# CSS customizado
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .quality-good {
        color: #2ca02c;
        font-weight: bold;
    }
    .quality-warning {
        color: #ff7f0e;
        font-weight: bold;
    }
    .quality-error {
        color: #d62728;
        font-weight: bold;
    }
    .developer-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .developer-card h4 {
        color: white;
        margin-bottom: 15px;
        font-size: 1.3em;
    }
    .developer-card p {
        color: rgba(255,255,255,0.95);
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .developer-card a {
        color: #ffd700;
        text-decoration: none;
    }
    .developer-card a:hover {
        text-decoration: underline;
    }
    .badge {
        display: inline-block;
        background-color: rgba(255,255,255,0.2);
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.85em;
        margin: 3px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_file(uploaded_file):
    """Carrega e processa arquivo com cache"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_path = tmp_file.name

    try:
        # Carrega dados
        loader = INMETDataLoader(tmp_path)
        
        progress_bar = st.progress(0)
        def update_progress(value):
            progress_bar.progress(value)
        
        df, metadata = loader.load_data(update_progress)
        info = loader.get_data_info()

        # Valida dados
        validator = DataValidator(df)
        validation_results = validator.validate_physical_limits()
        missing_patterns = validator.detect_missing_data_patterns()
        date_validation = validator.validate_date_sequence()

        # Calcula métricas
        metrics_calc = QualityMetricsCalculator(df, validation_results)
        quality_summary = metrics_calc.get_quality_summary()

        return {
            'df': df,
            'metadata': metadata,
            'info': info,
            'validator': validator,
            'metrics_calc': metrics_calc,
            'quality_summary': quality_summary,
            'validation_results': validation_results,
            'missing_patterns': missing_patterns,
            'date_validation': date_validation,
        }
    finally:
        # Remove arquivo temporário
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def display_metadata(metadata, info):
    """Exibe metadados da estação"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Código da Estação', metadata.get('Codigo Estacao', 'N/A'))

    with col2:
        latitude = metadata.get('Latitude', 'N/A')
        st.metric('Latitude', latitude)

    with col3:
        longitude = metadata.get('Longitude', 'N/A')
        st.metric('Longitude', longitude)

    with col4:
        altitude = metadata.get('Altitude', 'N/A')
        st.metric('Altitude (m)', altitude)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Período Inicial', metadata.get('Data Inicial', 'N/A'))

    with col2:
        st.metric('Período Final', metadata.get('Data Final', 'N/A'))

    with col3:
        st.metric('Total de Registros', f"{info['total_rows']:,}")

    with col4:
        st.metric('Variáveis', info['total_columns'] - 1)


def display_quality_overview(quality_summary):
    """Exibe visão geral de qualidade"""
    overall = quality_summary.get('overall', {})
    quality_index = overall.get('overall_quality_index', 0)
    recommendation = overall.get('recommendation', 'N/A')

    # Determina cor baseado no índice
    if quality_index >= RECOMMENDATION_CRITERIA['adequado']:
        color = 'green'
        css_class = 'quality-good'
    elif quality_index >= RECOMMENDATION_CRITERIA['parcialmente_adequado']:
        color = 'orange'
        css_class = 'quality-warning'
    else:
        color = 'red'
        css_class = 'quality-error'

    # Exibe índice principal
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.metric('Índice de Qualidade Geral', f"{quality_index:.2f}/100")

    with col2:
        st.metric('Recomendação', recommendation)

    with col3:
        avg_completeness = overall.get('average_completeness', 0)
        st.metric('Completude Média', f"{avg_completeness:.1f}%")

    # Visualizador
    visualizer = Visualizer(pd.DataFrame())  # Dummy para usar método
    col1, col2 = st.columns([2, 1])

    with col1:
        # Gráfico de qualidade geral
        fig_gauge = Visualizer(pd.DataFrame()).plot_quality_gauge(quality_index)
        st.plotly_chart(fig_gauge, width='stretch')

    with col2:
        description = overall.get('description', 'N/A')
        st.markdown(f"""
        <div class='metric-card'>
            <h4>Interpretação</h4>
            <p><strong>Índice:</strong> {quality_index:.2f}/100</p>
            <p><strong>Status:</strong> <span class='{css_class}'>{recommendation}</span></p>
            <p><strong>Descrição:</strong> {description}</p>
        </div>
        """, unsafe_allow_html=True)


def display_variable_analysis(df, metrics_calc, validator, selected_variable):
    """Exibe análise detalhada de variável"""
    st.subheader(f'Análise Detalhada: {VARIABLE_NAMES_SHORT.get(selected_variable, selected_variable)}')

    # Cria abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        'Série Temporal',
        'Distribuição',
        'Estatísticas',
        'Outliers',
        'Qualidade'
    ])

    visualizer = Visualizer(df)

    with tab1:
        st.plotly_chart(
            visualizer.plot_time_series(selected_variable),
            width='stretch'
        )

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                visualizer.plot_distribution(selected_variable),
                width='stretch'
            )
        with col2:
            st.plotly_chart(
                visualizer.plot_box_plot(selected_variable),
                width='stretch'
            )

    with tab3:
        report = metrics_calc.get_variable_quality_report(selected_variable)
        stats = report.get('statistics', {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('Média', f"{stats.get('mean', 0):.2f}")
        with col2:
            st.metric('Mediana', f"{stats.get('median', 0):.2f}")
        with col3:
            st.metric('Desvio Padrão', f"{stats.get('std', 0):.2f}")
        with col4:
            st.metric('Contagem', f"{stats.get('count', 0)}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('Mínimo', f"{stats.get('min', 0):.2f}")
        with col2:
            st.metric('Q1', f"{stats.get('q1', 0):.2f}")
        with col3:
            st.metric('Q3', f"{stats.get('q3', 0):.2f}")
        with col4:
            st.metric('Máximo', f"{stats.get('max', 0):.2f}")

    with tab4:
        outlier_indices, stats_iqr = validator.detect_outliers_iqr(selected_variable)
        if outlier_indices:
            st.plotly_chart(
                visualizer.plot_outliers(selected_variable, outlier_indices),
                width='stretch'
            )
            st.write(f'**Outliers Detectados (IQR):** {len(outlier_indices)}')
            outlier_pct = stats_iqr.get("outlier_percentage", 0)
            st.write(f'**Percentual:** {outlier_pct:.2f}%')
        else:
            st.info('Nenhum outlier detectado')

    with tab5:
        report = metrics_calc.get_variable_quality_report(selected_variable)
        quality = report.get('quality_index', {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('Completude', f"{quality.get('completeness_score', 0):.1f}%")
        with col2:
            st.metric('Validade', f"{quality.get('validity_score', 0):.1f}%")
        with col3:
            st.metric('Consistência', f"{quality.get('consistency_score', 0):.1f}%")
        with col4:
            st.metric('Índice Geral', f"{quality.get('quality_index', 0):.1f}")


def display_developer_info():
    """Exibe informações sobre o desenvolvedor"""
    st.markdown("""
    <div class='developer-card'>
        <h4>👨‍💻 Sobre o Desenvolvedor</h4>
        <p><strong>Elivaldo Carvalho Rocha</strong></p>
        <p>
            Meteorologista e desenvolvedor Full Stack com sólida formação acadêmica e experiência em análise de dados 
            meteorológicos e climáticos. Mestre em Gestão de Risco e Desastres Naturais na Amazônia (UFPA), 
            Bacharel em Meteorologia (UFPA), com especializações em Agrometeorologia e Climatologia, 
            Ciência de Dados Geográficos, Análise de Dados Espaciais, Geotecnologias, Georreferenciamento, Geoprocessamento 
            e Sensoriamento Remoto.
        </p>
        <p>
            Possui experiência em climatologia, meteorologia sinótica, previsão de tempo e processamento de imagens de satélites.
        </p>
        <p>
            <span class='badge'>Python</span>
            <span class='badge'>JavaScript</span>
            <span class='badge'>R</span>
            <span class='badge'>SQL</span>
            <span class='badge'>PyQGIS</span>
            <span class='badge'>Streamlit</span>
            <span class='badge'>Machine Learning</span>
        </p>
        <p style='margin-top: 15px; font-size: 0.9em;'>
            📧 <a href='mailto:carvalhovaldo09@gmail.com'>carvalhovaldo09@gmail.com</a> | 
            🔗 <a href='https://linkedin.com/in/elivaldo-rocha-10509b116' target='_blank'>LinkedIn</a> | 
            💻 <a href='https://github.com/ElivaldoRocha' target='_blank'>GitHub</a> |
            📚 <a href='https://lattes.cnpq.br/2673936555772229' target='_blank'>Lattes</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Função principal"""
    st.title('📊 INMET Data Quality Analyzer')
    st.markdown('Análise de qualidade de dados de estações meteorológicas automáticas')

    # Sidebar
    st.sidebar.title('Configurações')

    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader(
        MESSAGES['upload_prompt'],
        type=['csv'],
        help=f'Máximo {MAX_FILE_SIZE_MB} MB'
    )

    if uploaded_file is None:
        st.info(MESSAGES['no_file'])
        st.markdown("""
        ### Como usar:
        1. Faça upload de um arquivo CSV na escala diária (separador decimal "," e separador de colunas ";") de estação automática meteorológica do INMET
        2. O aplicativo analisará automaticamente a qualidade dos dados
        3. Visualize gráficos interativos e estatísticas detalhadas
        4. Gere um relatório em PDF com os resultados
        """)
        
        # Exibe informações do desenvolvedor
        st.divider()
        display_developer_info()
        
        return

    # Processa arquivo
    st.sidebar.info('Processando arquivo...')
    data = load_and_process_file(uploaded_file)

    st.sidebar.success('Arquivo processado com sucesso!')

    # Extrai dados
    df = data['df']
    metadata = data['metadata']
    info = data['info']
    metrics_calc = data['metrics_calc']
    quality_summary = data['quality_summary']

    # Seção 1: Metadados
    st.header('📍 Informações da Estação')
    display_metadata(metadata, info)

    st.divider()

    # Seção 2: Visão Geral de Qualidade
    st.header('📈 Visão Geral de Qualidade')
    display_quality_overview(quality_summary)

    st.divider()

    # Seção 3: Análise Geral
    st.header('🔍 Análise Geral')

    tab1, tab2, tab3, tab4 = st.tabs([
        'Completude',
        'Validade',
        'Consistência',
        'Dados Faltantes'
    ])

    visualizer = Visualizer(df)

    with tab1:
        completeness = quality_summary.get('completeness', {})
        comp_data = []
        for var, metrics in completeness.items():
            comp_pct = metrics.get('completeness_percentage', 0)
            comp_data.append({
                'Variável': VARIABLE_NAMES_SHORT.get(var, var),
                'Completude (%)': f"{comp_pct:.2f}%",
                'Não-nulos': metrics.get('non_null_count', 0),
                'Nulos': metrics.get('null_count', 0),
            })
        st.dataframe(pd.DataFrame(comp_data), width='stretch')

    with tab2:
        validity = quality_summary.get('validity', {})
        val_data = []
        for var, metrics in validity.items():
            val_pct = metrics.get('validity_percentage', 0)
            val_data.append({
                'Variável': VARIABLE_NAMES_SHORT.get(var, var),
                'Validade (%)': f"{val_pct:.2f}%",
                'Válidos': metrics.get('valid_count', 0),
                'Inválidos': metrics.get('invalid_count', 0),
            })
        st.dataframe(pd.DataFrame(val_data), width='stretch')

    with tab3:
        consistency = quality_summary.get('consistency', {})
        cons_data = []
        for var, metrics in consistency.items():
            cons_pct = metrics.get('consistency_percentage', 0)
            cons_data.append({
                'Variável': VARIABLE_NAMES_SHORT.get(var, var),
                'Consistência (%)': f"{cons_pct:.2f}%",
                'Anomalias': metrics.get('anomaly_count', 0),
            })
        st.dataframe(pd.DataFrame(cons_data), width='stretch')

    with tab4:
        st.plotly_chart(
            visualizer.plot_missing_data_heatmap(),
            width='stretch'
        )

    st.divider()

    # Seção 4: Análise por Variável
    st.header('🔬 Análise Detalhada por Variável')

    variables = info['variables']
    selected_variable = st.selectbox(
        'Selecione uma variável para análise detalhada:',
        variables,
        format_func=lambda x: VARIABLE_NAMES_SHORT.get(x, x)
    )

    if selected_variable:
        display_variable_analysis(df, metrics_calc, data['validator'], selected_variable)

    st.divider()

    # Seção 5: Gráfico de Qualidade Comparativa
    st.header('📊 Comparação de Qualidade')

    quality_metrics = metrics_calc.calculate_quality_index()
    st.plotly_chart(
        visualizer.plot_quality_comparison(quality_metrics),
        width='stretch'
    )

    st.divider()

    # Seção 6: Relatório e Downloads
    st.header('📄 Relatório e Downloads')

    col1, col2 = st.columns(2)

    with col1:
        if st.button('📥 Gerar Relatório em PDF'):
            with st.spinner('Gerando relatório...'):
                report_gen = ReportGenerator(metadata, quality_summary, df)
                pdf_bytes = report_gen.create_pdf()

                station_code = metadata.get("Codigo Estacao", "estacao")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label='⬇️ Baixar Relatório PDF',
                    data=pdf_bytes,
                    file_name=f'relatorio_qualidade_{station_code}_{timestamp}.pdf',
                    mime='application/pdf'
                )

    with col2:
        st.info('💡 Dica: Clique no botão acima para gerar um relatório completo em PDF')

    # Rodapé com informações do desenvolvedor (versão compacta)
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85em; padding: 10px;'>
        Desenvolvido por <strong>Elivaldo Carvalho Rocha</strong> | 
        Meteorologista | Mestre em Gestão de Risco e Desastres Naturais na Amazônia (UFPA)<br>
        📧 carvalhovaldo09@gmail.com | 
        <a href='https://github.com/ElivaldoRocha' target='_blank'>GitHub</a> | 
        <a href='https://linkedin.com/in/elivaldo-rocha-10509b116' target='_blank'>LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()