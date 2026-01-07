"""
Módulo para criação de visualizações interativas com Plotly
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List
from config import COLORS, VARIABLE_NAMES_SHORT


class Visualizer:
    """Criador de visualizações interativas"""

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o visualizador

        Args:
            df: DataFrame com dados
        """
        self.df = df

    def plot_time_series(self, column: str, title: str = None) -> go.Figure:
        """
        Cria gráfico de série temporal

        Args:
            column: Nome da coluna
            title: Título do gráfico

        Returns:
            Figura Plotly
        """
        if title is None:
            title = VARIABLE_NAMES_SHORT.get(column, column)

        # Separa dados válidos e nulos
        valid_data = self.df[self.df[column].notna()]
        null_indices = self.df[self.df[column].isna()].index

        fig = go.Figure()

        # Linha de dados válidos
        fig.add_trace(go.Scatter(
            x=valid_data['Data'],
            y=valid_data[column],
            mode='lines',
            name='Dados Válidos',
            line=dict(color=COLORS['valid'], width=2),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Valor: %{y:.2f}<extra></extra>',
        ))

        # Marca dados nulos
        if len(null_indices) > 0:
            null_data = self.df.loc[null_indices]
            fig.add_trace(go.Scatter(
                x=null_data['Data'],
                y=[None] * len(null_data),
                mode='markers',
                name='Dados Faltantes',
                marker=dict(size=5, color=COLORS['missing']),
                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Dado Faltante<extra></extra>',
            ))

        fig.update_layout(
            title=f'Série Temporal - {title}',
            xaxis_title='Data',
            yaxis_title='Valor',
            hovermode='x unified',
            template='plotly_white',
            height=400,
        )

        return fig

    def plot_distribution(self, column: str, title: str = None) -> go.Figure:
        """
        Cria gráfico de distribuição

        Args:
            column: Nome da coluna
            title: Título do gráfico

        Returns:
            Figura Plotly
        """
        if title is None:
            title = VARIABLE_NAMES_SHORT.get(column, column)

        data = self.df[column].dropna()

        fig = go.Figure()

        # Histograma
        fig.add_trace(go.Histogram(
            x=data,
            name='Frequência',
            marker=dict(color=COLORS['valid']),
            nbinsx=30,
            hovertemplate='Intervalo: %{x}<br>Frequência: %{y}<extra></extra>',
        ))

        # Adiciona linha de média
        mean_val = data.mean()
        fig.add_vline(
            x=mean_val,
            line_dash='dash',
            line_color=COLORS['warning'],
            annotation_text=f'Média: {mean_val:.2f}',
            annotation_position='top right',
        )

        fig.update_layout(
            title=f'Distribuição - {title}',
            xaxis_title='Valor',
            yaxis_title='Frequência',
            template='plotly_white',
            height=400,
        )

        return fig

    def plot_box_plot(self, column: str, title: str = None) -> go.Figure:
        """
        Cria box plot

        Args:
            column: Nome da coluna
            title: Título do gráfico

        Returns:
            Figura Plotly
        """
        if title is None:
            title = VARIABLE_NAMES_SHORT.get(column, column)

        data = self.df[column].dropna()

        fig = go.Figure()

        fig.add_trace(go.Box(
            y=data,
            name=title,
            marker=dict(color=COLORS['valid']),
            boxmean='sd',
            hovertemplate='Valor: %{y:.2f}<extra></extra>',
        ))

        fig.update_layout(
            title=f'Box Plot - {title}',
            yaxis_title='Valor',
            template='plotly_white',
            height=400,
        )

        return fig

    def plot_missing_data_heatmap(self) -> go.Figure:
        """
        Cria heatmap de dados faltantes

        Returns:
            Figura Plotly
        """
        # Cria cópia para não modificar o original
        df_temp = self.df.copy()
        
        # Agrupa dados por mês
        df_temp['YearMonth'] = df_temp['Data'].dt.to_period('M')
        
        # Cria matriz de completude
        completeness_matrix = []
        months = []
        variables = [col for col in df_temp.columns if col not in ['Data', 'YearMonth']]

        for period in df_temp['YearMonth'].unique():
            month_data = df_temp[df_temp['YearMonth'] == period]
            month_completeness = []
            
            for var in variables:
                completeness = (month_data[var].notna().sum() / len(month_data)) * 100
                month_completeness.append(completeness)
            
            completeness_matrix.append(month_completeness)
            months.append(str(period))

        completeness_matrix = np.array(completeness_matrix).T

        fig = go.Figure(data=go.Heatmap(
            z=completeness_matrix,
            x=months,
            y=[VARIABLE_NAMES_SHORT.get(v, v) for v in variables],
            colorscale='RdYlGn',
            zmin=0,
            zmax=100,
            hovertemplate='Variável: %{y}<br>Período: %{x}<br>Completude: %{z:.1f}%<extra></extra>',
        ))

        fig.update_layout(
            title='Heatmap de Completude de Dados (por mês)',
            xaxis_title='Período',
            yaxis_title='Variável',
            height=400 + len(variables) * 20,
        )

        return fig

    def plot_calendar_heatmap(self, column: str, title: str = None) -> go.Figure:
        """
        Cria calendar plot (heatmap de dias)

        Args:
            column: Nome da coluna
            title: Título do gráfico

        Returns:
            Figura Plotly
        """
        if title is None:
            title = VARIABLE_NAMES_SHORT.get(column, column)

        # Cria coluna de status (válido/faltante/inválido)
        df_temp = self.df.copy()
        df_temp['Status'] = 'Válido'
        df_temp.loc[df_temp[column].isna(), 'Status'] = 'Faltante'

        # Agrupa por data
        daily_status = df_temp.groupby('Data')['Status'].first().reset_index()
        daily_status['DayOfWeek'] = daily_status['Data'].dt.dayofweek
        daily_status['Week'] = daily_status['Data'].dt.isocalendar().week
        daily_status['Year'] = daily_status['Data'].dt.year

        # Cria cores
        color_map = {'Válido': 0, 'Faltante': 1, 'Inválido': 2}
        daily_status['StatusCode'] = daily_status['Status'].map(color_map)

        fig = px.scatter(
            daily_status,
            x='Week',
            y='DayOfWeek',
            color='Status',
            hover_data={'Data': '|%d/%m/%Y', 'Week': False, 'DayOfWeek': False},
            color_discrete_map={'Válido': COLORS['valid'], 'Faltante': COLORS['missing'], 'Inválido': COLORS['invalid']},
            title=f'Calendar Plot - {title}',
            height=300,
        )

        fig.update_layout(
            yaxis=dict(
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                ticktext=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
            ),
            xaxis_title='Semana do Ano',
            yaxis_title='Dia da Semana',
            template='plotly_white',
        )

        return fig

    def plot_quality_gauge(self, quality_index: float) -> go.Figure:
        """
        Cria gráfico de medidor para índice de qualidade

        Args:
            quality_index: Valor do índice (0-100)

        Returns:
            Figura Plotly
        """
        fig = go.Figure(go.Indicator(
            mode='gauge+number+delta',
            value=quality_index,
            title={'text': 'Índice de Qualidade Geral'},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['valid']},
                'steps': [
                    {'range': [0, 60], 'color': COLORS['error']},
                    {'range': [60, 80], 'color': COLORS['warning']},
                    {'range': [80, 100], 'color': COLORS['good']},
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 90,
                },
            },
        ))

        fig.update_layout(
            height=400,
        )

        return fig

    def plot_quality_comparison(self, quality_metrics: Dict) -> go.Figure:
        """
        Cria gráfico comparativo de qualidade por variável

        Args:
            quality_metrics: Dicionário com métricas de qualidade

        Returns:
            Figura Plotly
        """
        variables = []
        quality_indices = []

        for var, metrics in quality_metrics.items():
            short_name = VARIABLE_NAMES_SHORT.get(var, var)
            variables.append(short_name)
            quality_indices.append(metrics.get('quality_index', 0))

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=variables,
            y=quality_indices,
            marker=dict(
                color=quality_indices,
                colorscale='RdYlGn',
                cmin=0,
                cmax=100,
                colorbar=dict(title='Índice'),
            ),
            text=[f'{qi:.1f}' for qi in quality_indices],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Índice: %{y:.2f}<extra></extra>',
        ))

        fig.update_layout(
            title='Índice de Qualidade por Variável',
            xaxis_title='Variável',
            yaxis_title='Índice de Qualidade',
            height=400,
            template='plotly_white',
        )

        return fig

    def plot_outliers(self, column: str, outlier_indices: List[int], title: str = None) -> go.Figure:
        """
        Cria gráfico destacando outliers

        Args:
            column: Nome da coluna
            outlier_indices: Índices dos outliers
            title: Título do gráfico

        Returns:
            Figura Plotly
        """
        if title is None:
            title = VARIABLE_NAMES_SHORT.get(column, column)

        df_temp = self.df.copy()
        df_temp['IsOutlier'] = df_temp.index.isin(outlier_indices)

        fig = go.Figure()

        # Dados normais
        normal_data = df_temp[~df_temp['IsOutlier']]
        fig.add_trace(go.Scatter(
            x=normal_data['Data'],
            y=normal_data[column],
            mode='markers',
            name='Dados Normais',
            marker=dict(color=COLORS['valid'], size=4),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Valor: %{y:.2f}<extra></extra>',
        ))

        # Outliers
        outlier_data = df_temp[df_temp['IsOutlier']]
        fig.add_trace(go.Scatter(
            x=outlier_data['Data'],
            y=outlier_data[column],
            mode='markers',
            name='Outliers',
            marker=dict(color=COLORS['anomaly'], size=8, symbol='diamond'),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Outlier: %{y:.2f}<extra></extra>',
        ))

        fig.update_layout(
            title=f'Detecção de Outliers - {title}',
            xaxis_title='Data',
            yaxis_title='Valor',
            hovermode='x unified',
            template='plotly_white',
            height=400,
        )

        return fig