"""
Módulo para cálculo de métricas de qualidade de dados
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from config import (
    QUALITY_THRESHOLDS, QUALITY_INDEX_WEIGHTS,
    RECOMMENDATION_CRITERIA, VARIABLE_NAMES_SHORT
)


class QualityMetricsCalculator:
    """Calculador de métricas de qualidade de dados meteorológicos"""

    def __init__(self, df: pd.DataFrame, validation_results: Dict):
        """
        Inicializa o calculador

        Args:
            df: DataFrame com dados
            validation_results: Resultados de validação do DataValidator
        """
        self.df = df
        self.validation_results = validation_results
        self.metrics = {}

    def calculate_completeness(self, column: str = None) -> Dict:
        """
        Calcula métrica de completude (% de dados não-nulos)

        Args:
            column: Coluna específica (None para todas)

        Returns:
            Dicionário com métricas de completude
        """
        completeness = {}

        if column:
            columns = [column]
        else:
            columns = [col for col in self.df.columns if col != 'Data']

        for col in columns:
            non_null_count = self.df[col].notna().sum()
            total_count = len(self.df)
            completeness_pct = (non_null_count / total_count) * 100

            completeness[col] = {
                'non_null_count': non_null_count,
                'null_count': total_count - non_null_count,
                'total_count': total_count,
                'completeness_percentage': completeness_pct,
            }

        return completeness

    def calculate_validity(self, column: str = None) -> Dict:
        """
        Calcula métrica de validade (% de dados dentro de limites físicos)

        Args:
            column: Coluna específica (None para todas)

        Returns:
            Dicionário com métricas de validade
        """
        validity = {}

        if column:
            columns = [column]
        else:
            columns = [col for col in self.df.columns if col != 'Data']

        for col in columns:
            if col in self.validation_results:
                result = self.validation_results[col]
                total_non_null = result['valid_count'] + result['invalid_count']

                if total_non_null > 0:
                    validity_pct = (result['valid_count'] / total_non_null) * 100
                else:
                    validity_pct = 0

                validity[col] = {
                    'valid_count': result['valid_count'],
                    'invalid_count': result['invalid_count'],
                    'null_count': result['null_count'],
                    'total_count': result['total_count'],
                    'validity_percentage': validity_pct,
                    'min_limit': result['min_limit'],
                    'max_limit': result['max_limit'],
                }

        return validity

    def calculate_consistency(self, column: str = None) -> Dict:
        """
        Calcula métrica de consistência (ausência de anomalias)

        Args:
            column: Coluna específica (None para todas)

        Returns:
            Dicionário com métricas de consistência
        """
        consistency = {}

        if column:
            columns = [column]
        else:
            columns = [col for col in self.df.columns if col != 'Data']

        for col in columns:
            data = self.df[col].dropna()

            if len(data) < 2:
                consistency[col] = {
                    'consistency_percentage': 0,
                    'anomaly_count': 0,
                    'message': 'Dados insuficientes',
                }
                continue

            # Detecta outliers simples (valores fora de 3 desvios padrão)
            mean = data.mean()
            std = data.std()

            if std == 0:
                anomaly_count = 0
            else:
                anomaly_mask = np.abs((data - mean) / std) > 3
                anomaly_count = anomaly_mask.sum()

            consistency_pct = ((len(data) - anomaly_count) / len(data)) * 100

            consistency[col] = {
                'consistency_percentage': consistency_pct,
                'anomaly_count': anomaly_count,
                'anomaly_percentage': (anomaly_count / len(data)) * 100 if len(data) > 0 else 0,
                'mean': mean,
                'std': std,
            }

        return consistency

    def calculate_descriptive_statistics(self, column: str) -> Dict:
        """
        Calcula estatísticas descritivas para uma coluna

        Args:
            column: Nome da coluna

        Returns:
            Dicionário com estatísticas descritivas
        """
        data = self.df[column].dropna()

        if len(data) == 0:
            return {'message': 'Sem dados disponíveis'}

        stats = {
            'count': len(data),
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'q1': data.quantile(0.25),
            'q3': data.quantile(0.75),
            'iqr': data.quantile(0.75) - data.quantile(0.25),
            'skewness': data.skew(),
            'kurtosis': data.kurtosis(),
        }

        return stats

    def calculate_quality_index(self, column: str = None) -> Dict:
        """
        Calcula índice de qualidade geral (0-100)

        Args:
            column: Coluna específica (None para todas)

        Returns:
            Dicionário com índices de qualidade
        """
        completeness = self.calculate_completeness(column)
        validity = self.calculate_validity(column)
        consistency = self.calculate_consistency(column)

        quality_indices = {}

        for col in completeness.keys():
            comp_pct = completeness[col]['completeness_percentage']
            valid_pct = validity.get(col, {}).get('validity_percentage', 0)
            cons_pct = consistency.get(col, {}).get('consistency_percentage', 0)

            # Normaliza percentuais para 0-100
            comp_score = min(comp_pct, 100)
            valid_score = min(valid_pct, 100)
            cons_score = min(cons_pct, 100)

            # Calcula índice ponderado
            quality_index = (
                comp_score * QUALITY_INDEX_WEIGHTS['completude'] +
                valid_score * QUALITY_INDEX_WEIGHTS['validade'] +
                cons_score * QUALITY_INDEX_WEIGHTS['consistencia']
            )

            quality_indices[col] = {
                'quality_index': quality_index,
                'completeness_score': comp_score,
                'validity_score': valid_score,
                'consistency_score': cons_score,
            }

        self.metrics = quality_indices
        return quality_indices

    def get_recommendation(self, quality_index: float) -> Tuple[str, str]:
        """
        Retorna recomendação de uso baseada no índice de qualidade

        Args:
            quality_index: Índice de qualidade (0-100)

        Returns:
            Tupla (recomendação, descrição)
        """
        if quality_index >= RECOMMENDATION_CRITERIA['adequado']:
            return ('Adequado', 'Dados de qualidade adequada para uso científico')
        elif quality_index >= RECOMMENDATION_CRITERIA['parcialmente_adequado']:
            return ('Parcialmente Adequado', 'Dados com qualidade moderada, recomenda-se revisão antes do uso')
        else:
            return ('Inadequado', 'Dados com qualidade insuficiente para uso científico')

    def get_overall_quality_index(self) -> Dict:
        """
        Calcula índice de qualidade geral para todo o dataset

        Returns:
            Dicionário com índice de qualidade geral
        """
        if not self.metrics:
            self.calculate_quality_index()

        # Média dos índices de qualidade de todas as variáveis
        quality_indices = [m['quality_index'] for m in self.metrics.values()]

        if not quality_indices:
            overall_index = 0
        else:
            overall_index = np.mean(quality_indices)

        recommendation, description = self.get_recommendation(overall_index)

        return {
            'overall_quality_index': overall_index,
            'recommendation': recommendation,
            'description': description,
            'variable_count': len(self.metrics),
            'average_completeness': np.mean([m['completeness_score'] for m in self.metrics.values()]),
            'average_validity': np.mean([m['validity_score'] for m in self.metrics.values()]),
            'average_consistency': np.mean([m['consistency_score'] for m in self.metrics.values()]),
        }

    def get_quality_summary(self) -> Dict:
        """
        Retorna resumo completo de qualidade

        Returns:
            Dicionário com resumo de qualidade
        """
        completeness = self.calculate_completeness()
        validity = self.calculate_validity()
        consistency = self.calculate_consistency()
        overall = self.get_overall_quality_index()

        summary = {
            'overall': overall,
            'completeness': completeness,
            'validity': validity,
            'consistency': consistency,
        }

        return summary

    def get_variable_quality_report(self, column: str) -> Dict:
        """
        Retorna relatório detalhado de qualidade para uma variável

        Args:
            column: Nome da coluna

        Returns:
            Dicionário com relatório detalhado
        """
        completeness = self.calculate_completeness(column)
        validity = self.calculate_validity(column)
        consistency = self.calculate_consistency(column)
        stats = self.calculate_descriptive_statistics(column)
        quality = self.calculate_quality_index(column)

        short_name = VARIABLE_NAMES_SHORT.get(column, column)

        report = {
            'variable': column,
            'variable_short_name': short_name,
            'completeness': completeness.get(column, {}),
            'validity': validity.get(column, {}),
            'consistency': consistency.get(column, {}),
            'statistics': stats,
            'quality_index': quality.get(column, {}),
        }

        return report
