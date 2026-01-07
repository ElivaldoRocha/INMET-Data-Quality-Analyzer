"""
Módulo para carregamento e parsing de arquivos CSV do INMET
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, Dict, Any
import streamlit as st
from config import (
    CSV_SEPARATOR, DECIMAL_SEPARATOR, NULL_VALUES,
    METADATA_END_LINE, HEADER_LINE, MAX_FILE_SIZE_BYTES
)


class INMETDataLoader:
    """Carregador de dados INMET com suporte a arquivos grandes"""

    def __init__(self, file_path: str):
        """
        Inicializa o carregador de dados

        Args:
            file_path: Caminho para o arquivo CSV
        """
        self.file_path = file_path
        self.metadata = {}
        self.df = None
        self.header_line = None

    def validate_file(self) -> bool:
        """Valida o arquivo antes do processamento"""
        try:
            file_size = pd.io.common.get_filepath_or_buffer(self.file_path)[1]
            if file_size > MAX_FILE_SIZE_BYTES:
                raise ValueError(f"Arquivo excede o limite de tamanho permitido")
            return True
        except Exception as e:
            st.error(f"Erro ao validar arquivo: {str(e)}")
            return False

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extrai metadados do arquivo (linhas 1-9)

        Returns:
            Dicionário com metadados da estação
        """
        metadata = {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for i in range(METADATA_END_LINE):
                    line = f.readline().strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        except Exception as e:
            st.warning(f"Não foi possível extrair metadados: {str(e)}")

        self.metadata = metadata
        return metadata

    def find_header_line(self) -> int:
        """
        Identifica automaticamente a linha de cabeçalho

        Returns:
            Número da linha de cabeçalho (0-indexed)
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if 'Data Medicao' in line or 'Data Medicao' in line:
                        self.header_line = i
                        return i
        except Exception as e:
            st.warning(f"Erro ao procurar cabeçalho: {str(e)}")

        # Se não encontrar, usa o padrão
        self.header_line = HEADER_LINE
        return HEADER_LINE

    def fix_malformed_numbers(self, value: str) -> str:
        """
        Corrige números malformados (começando com vírgula)

        Args:
            value: Valor a ser corrigido

        Returns:
            Valor corrigido
        """
        if isinstance(value, str):
            # Se começa com vírgula, adiciona 0 antes
            if value.startswith(','):
                value = '0' + value
        return value

    def load_data(self, progress_callback=None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Carrega e processa o arquivo CSV

        Args:
            progress_callback: Função para atualizar progresso

        Returns:
            Tupla (DataFrame processado, dicionário de metadados)
        """
        try:
            # Extrai metadados
            self.extract_metadata()

            # Encontra linha de cabeçalho
            header_line = self.find_header_line()

            # Lê o arquivo CSV
            if progress_callback:
                progress_callback(0.3)

            df = pd.read_csv(
                self.file_path,
                sep=CSV_SEPARATOR,
                decimal=DECIMAL_SEPARATOR,
                skiprows=header_line,
                na_values=NULL_VALUES,
                dtype_backend='numpy_nullable'
            ).dropna(axis=1, how='all')

            if progress_callback:
                progress_callback(0.6)

            # Renomeia coluna de data se necessário
            if 'Data Medicao' in df.columns:
                df.rename(columns={'Data Medicao': 'Data'}, inplace=True)
            elif df.columns[0].startswith('Data'):
                df.rename(columns={df.columns[0]: 'Data'}, inplace=True)

            # Converte coluna de data para datetime
            df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')

            # Corrige números malformados em todas as colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in df.columns:
                if col != 'Data' and col not in numeric_cols:
                    # Tenta converter para numérico
                    df[col] = df[col].apply(self.fix_malformed_numbers)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            if progress_callback:
                progress_callback(0.9)

            # Ordena por data
            df = df.sort_values('Data').reset_index(drop=True)

            self.df = df

            if progress_callback:
                progress_callback(1.0)

            return df, self.metadata

        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            raise

    def get_data_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre os dados carregados

        Returns:
            Dicionário com informações do dataset
        """
        if self.df is None:
            return {}

        info = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "date_range_start": self.df['Data'].min(),
            "date_range_end": self.df['Data'].max(),
            "expected_days": (self.df['Data'].max() - self.df['Data'].min()).days + 1,
            "actual_days": len(self.df),
            "variables": [col for col in self.df.columns if col != 'Data'],
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        return info

    def get_variables(self) -> list:
        """Retorna lista de variáveis disponíveis"""
        if self.df is None:
            return []
        return [col for col in self.df.columns if col != 'Data']

    def get_dataframe(self) -> pd.DataFrame:
        """Retorna o DataFrame carregado"""
        return self.df

    def get_metadata(self) -> Dict[str, Any]:
        """Retorna os metadados extraídos"""
        return self.metadata
