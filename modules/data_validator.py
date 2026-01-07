"""
Módulo para validação de dados meteorológicos
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from scipy import stats
from config import PHYSICAL_LIMITS


class DataValidator:
    """Validador de dados meteorológicos com detecção de anomalias"""

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o validador

        Args:
            df: DataFrame com dados meteorológicos
        """
        self.df = df.copy()
        self.validation_results = {}
        self.anomalies = {}

    def validate_physical_limits(self) -> Dict[str, Dict]:
        """
        Valida se os valores estão dentro de limites físicos

        Returns:
            Dicionário com resultados de validação por variável
        """
        results = {}

        for col in self.df.columns:
            if col == 'Data':
                continue

            if col not in PHYSICAL_LIMITS:
                continue

            min_limit, max_limit = PHYSICAL_LIMITS[col]
            valid_mask = (self.df[col] >= min_limit) & (self.df[col] <= max_limit)
            null_mask = self.df[col].isna()

            results[col] = {
                'valid_count': valid_mask.sum(),
                'invalid_count': (~valid_mask & ~null_mask).sum(),
                'null_count': null_mask.sum(),
                'total_count': len(self.df),
                'valid_percentage': (valid_mask.sum() / len(self.df)) * 100,
                'invalid_indices': self.df[~valid_mask & ~null_mask].index.tolist(),
                'min_limit': min_limit,
                'max_limit': max_limit,
            }

        self.validation_results = results
        return results

    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5) -> Tuple[List[int], Dict]:
        """
        Detecta outliers usando método IQR (Interquartile Range)

        Args:
            column: Nome da coluna
            multiplier: Multiplicador para IQR (padrão 1.5)

        Returns:
            Tupla (índices de outliers, estatísticas)
        """
        data = self.df[column].dropna()

        if len(data) < 4:
            return [], {}

        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outlier_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
        outlier_indices = self.df[outlier_mask & self.df[column].notna()].index.tolist()

        stats_dict = {
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': len(outlier_indices),
            'outlier_percentage': (len(outlier_indices) / len(self.df)) * 100,
        }

        return outlier_indices, stats_dict

    def detect_outliers_zscore(self, column: str, threshold: float = 3.0) -> Tuple[List[int], Dict]:
        """
        Detecta outliers usando Z-score

        Args:
            column: Nome da coluna
            threshold: Limiar de Z-score (padrão 3.0)

        Returns:
            Tupla (índices de outliers, estatísticas)
        """
        data = self.df[column].dropna()

        if len(data) < 2:
            return [], {}

        z_scores = np.abs(stats.zscore(data))
        outlier_mask = z_scores > threshold

        outlier_indices = data[outlier_mask].index.tolist()

        stats_dict = {
            'threshold': threshold,
            'mean': data.mean(),
            'std': data.std(),
            'outlier_count': len(outlier_indices),
            'outlier_percentage': (len(outlier_indices) / len(self.df)) * 100,
        }

        return outlier_indices, stats_dict

    def detect_change_points(self, column: str, window_size: int = 30) -> Dict:
        """
        Detecta mudanças abruptas nos dados (change points)

        Args:
            column: Nome da coluna
            window_size: Tamanho da janela para análise

        Returns:
            Dicionário com pontos de mudança detectados
        """
        data = self.df[column].dropna()

        if len(data) < window_size * 2:
            return {'change_points': [], 'message': 'Dados insuficientes'}

        # Calcula a média móvel
        rolling_mean = data.rolling(window=window_size, center=True).mean()
        rolling_std = data.rolling(window=window_size, center=True).std()

        # Detecta pontos onde o valor está fora de 2 desvios padrão da média móvel
        change_mask = np.abs(data - rolling_mean) > 2 * rolling_std

        change_points = data[change_mask].index.tolist()

        return {
            'change_points': change_points,
            'change_count': len(change_points),
            'change_percentage': (len(change_points) / len(self.df)) * 100,
        }

    def detect_missing_data_patterns(self) -> Dict:
        """
        Analisa padrões de dados faltantes

        Returns:
            Dicionário com análise de dados faltantes
        """
        patterns = {}

        for col in self.df.columns:
            if col == 'Data':
                continue

            null_mask = self.df[col].isna()
            null_count = null_mask.sum()

            if null_count == 0:
                patterns[col] = {
                    'null_count': 0,
                    'null_percentage': 0,
                    'consecutive_nulls': [],
                }
                continue

            # Encontra períodos contínuos de dados faltantes
            consecutive_nulls = []
            start_idx = None
            for idx, is_null in enumerate(null_mask):
                if is_null and start_idx is None:
                    start_idx = idx
                elif not is_null and start_idx is not None:
                    consecutive_nulls.append({
                        'start': start_idx,
                        'end': idx - 1,
                        'length': idx - start_idx,
                        'start_date': self.df.loc[start_idx, 'Data'],
                        'end_date': self.df.loc[idx - 1, 'Data'],
                    })
                    start_idx = None

            # Se termina com null
            if start_idx is not None:
                consecutive_nulls.append({
                    'start': start_idx,
                    'end': len(self.df) - 1,
                    'length': len(self.df) - start_idx,
                    'start_date': self.df.loc[start_idx, 'Data'],
                    'end_date': self.df.loc[len(self.df) - 1, 'Data'],
                })

            patterns[col] = {
                'null_count': null_count,
                'null_percentage': (null_count / len(self.df)) * 100,
                'consecutive_nulls': consecutive_nulls,
            }

        return patterns

    def validate_date_sequence(self) -> Dict:
        """
        Valida a sequência de datas

        Returns:
            Dicionário com informações sobre a sequência de datas
        """
        dates = self.df['Data'].dropna()

        if len(dates) < 2:
            return {'valid': False, 'message': 'Dados insuficientes'}

        # Verifica se as datas estão em ordem crescente
        is_sorted = (dates.diff().dt.days >= 0).all() or (dates.diff().dt.days <= 0).all()

        # Encontra gaps nas datas
        date_diffs = dates.diff().dt.days
        expected_diff = 1  # Esperado para dados diários

        gaps = []
        for idx, diff in enumerate(date_diffs):
            if pd.notna(diff) and diff != expected_diff and diff != 0:
                gaps.append({
                    'date': dates.iloc[idx],
                    'gap_days': int(diff),
                })

        return {
            'is_sorted': is_sorted,
            'total_dates': len(dates),
            'date_range': (dates.min(), dates.max()),
            'expected_days': (dates.max() - dates.min()).days + 1,
            'actual_days': len(dates),
            'gaps': gaps,
            'gap_count': len(gaps),
        }

    def get_validation_summary(self) -> Dict:
        """
        Retorna um resumo completo da validação

        Returns:
            Dicionário com resumo de validação
        """
        # Executa todas as validações
        physical_limits = self.validate_physical_limits()
        missing_patterns = self.detect_missing_data_patterns()
        date_validation = self.validate_date_sequence()

        summary = {
            'physical_limits': physical_limits,
            'missing_patterns': missing_patterns,
            'date_validation': date_validation,
        }

        return summary

    def get_anomalies_for_variable(self, column: str) -> Dict:
        """
        Retorna todas as anomalias detectadas para uma variável

        Args:
            column: Nome da coluna

        Returns:
            Dicionário com anomalias detectadas
        """
        anomalies = {
            'column': column,
            'physical_limits': {},
            'outliers_iqr': {},
            'outliers_zscore': {},
            'change_points': {},
        }

        # Validação de limites físicos
        if column in self.validation_results:
            anomalies['physical_limits'] = self.validation_results[column]
        else:
            if column != 'Data':
                self.validate_physical_limits()
                if column in self.validation_results:
                    anomalies['physical_limits'] = self.validation_results[column]

        # Outliers IQR
        outlier_indices_iqr, stats_iqr = self.detect_outliers_iqr(column)
        anomalies['outliers_iqr'] = {
            'indices': outlier_indices_iqr,
            'stats': stats_iqr,
        }

        # Outliers Z-score
        outlier_indices_zscore, stats_zscore = self.detect_outliers_zscore(column)
        anomalies['outliers_zscore'] = {
            'indices': outlier_indices_zscore,
            'stats': stats_zscore,
        }

        # Change points
        anomalies['change_points'] = self.detect_change_points(column)

        return anomalies
