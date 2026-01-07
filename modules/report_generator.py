"""
Módulo para geração de relatórios em PDF
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import io
from config import PDF_SETTINGS, VARIABLE_NAMES_SHORT, APP_NAME, DEVELOPER_NAME


class ReportGenerator:
    """Gerador de relatórios em PDF"""

    def __init__(self, metadata: Dict, quality_summary: Dict, df: pd.DataFrame, figures: Dict = None):
        """
        Inicializa o gerador de relatórios

        Args:
            metadata: Metadados da estação
            quality_summary: Resumo de qualidade
            df: DataFrame com dados
            figures: Dicionário com figuras Plotly (opcional)
        """
        self.metadata = metadata
        self.quality_summary = quality_summary
        self.df = df
        self.figures = figures or {}
        self.generation_time = datetime.now()

    def create_pdf(self, output_path: str = None) -> bytes:
        """
        Cria relatório em PDF

        Args:
            output_path: Caminho para salvar o PDF (None para retornar bytes)

        Returns:
            Bytes do PDF ou None se salvo em arquivo
        """
        # Cria buffer ou arquivo
        if output_path:
            pdf_buffer = output_path
        else:
            pdf_buffer = io.BytesIO()

        # Cria documento com margens em mm (valores do PDF_SETTINGS são em mm)
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=PDF_SETTINGS['margin_right'] * mm,
            leftMargin=PDF_SETTINGS['margin_left'] * mm,
            topMargin=PDF_SETTINGS['margin_top'] * mm,
            bottomMargin=PDF_SETTINGS['margin_bottom'] * mm,
        )

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=PDF_SETTINGS['title_font_size'],
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=PDF_SETTINGS['heading_font_size'],
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=10,
            spaceBefore=10,
        )
        normal_style = styles['Normal']

        # Constrói conteúdo
        story = []

        # Capa
        story.extend(self._create_cover(title_style, heading_style, normal_style))
        story.append(PageBreak())

        # Resumo Executivo
        story.extend(self._create_executive_summary(heading_style, normal_style))
        story.append(PageBreak())

        # Metadados
        story.extend(self._create_metadata_section(heading_style, normal_style))
        story.append(Spacer(1, 10 * mm))

        # Análise de Qualidade
        story.extend(self._create_quality_analysis(heading_style, normal_style))
        story.append(PageBreak())

        # Análise por Variável
        story.extend(self._create_variable_analysis(heading_style, normal_style))

        # Rodapé
        doc.build(
            story,
            onFirstPage=self._add_footer,
            onLaterPages=self._add_footer,
        )

        if output_path is None:
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()

    def _create_cover(self, title_style, heading_style, normal_style) -> List:
        """Cria página de capa"""
        story = []

        story.append(Spacer(1, 50 * mm))
        story.append(Paragraph(APP_NAME, title_style))
        story.append(Spacer(1, 10 * mm))

        story.append(Paragraph('Relatório de Qualidade de Dados Meteorológicos', heading_style))
        story.append(Spacer(1, 20 * mm))

        # Informações da estação
        station_code = self.metadata.get('Codigo Estacao', 'N/A')
        story.append(Paragraph(f'<b>Estação:</b> {station_code}', normal_style))
        story.append(Spacer(1, 3 * mm))

        # Verifica se há datas válidas
        if not self.df['Data'].isna().all():
            date_min = self.df['Data'].min()
            date_max = self.df['Data'].max()
            if pd.notna(date_min) and pd.notna(date_max):
                date_range = f'{date_min.strftime("%d/%m/%Y")} a {date_max.strftime("%d/%m/%Y")}'
            else:
                date_range = 'N/A'
        else:
            date_range = 'N/A'
        
        story.append(Paragraph(f'<b>Período Analisado:</b> {date_range}', normal_style))
        story.append(Spacer(1, 3 * mm))

        total_days = len(self.df)
        story.append(Paragraph(f'<b>Total de Registros:</b> {total_days}', normal_style))
        story.append(Spacer(1, 40 * mm))

        # Data de geração
        gen_date = self.generation_time.strftime('%d/%m/%Y às %H:%M:%S')
        story.append(Paragraph(f'<b>Data de Geração:</b> {gen_date}', normal_style))
        story.append(Spacer(1, 3 * mm))

        story.append(Paragraph(f'<b>Desenvolvedor:</b> {DEVELOPER_NAME}', normal_style))

        return story

    def _create_executive_summary(self, heading_style, normal_style) -> List:
        """Cria resumo executivo"""
        story = []

        story.append(Paragraph('Resumo Executivo', heading_style))

        overall = self.quality_summary.get('overall', {})
        quality_index = overall.get('overall_quality_index', 0)
        recommendation = overall.get('recommendation', 'N/A')
        description = overall.get('description', 'N/A')

        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(f'<b>Índice de Qualidade Geral:</b> {quality_index:.2f}/100', normal_style))
        story.append(Spacer(1, 3 * mm))

        story.append(Paragraph(f'<b>Recomendação:</b> {recommendation}', normal_style))
        story.append(Spacer(1, 3 * mm))

        story.append(Paragraph(f'<b>Descrição:</b> {description}', normal_style))
        story.append(Spacer(1, 8 * mm))

        # Estatísticas gerais
        avg_completeness = overall.get('average_completeness', 0)
        avg_validity = overall.get('average_validity', 0)
        avg_consistency = overall.get('average_consistency', 0)

        story.append(Paragraph('<b>Estatísticas Gerais:</b>', normal_style))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(f'• Completude Média: {avg_completeness:.2f}%', normal_style))
        story.append(Paragraph(f'• Validade Média: {avg_validity:.2f}%', normal_style))
        story.append(Paragraph(f'• Consistência Média: {avg_consistency:.2f}%', normal_style))

        return story

    def _create_metadata_section(self, heading_style, normal_style) -> List:
        """Cria seção de metadados"""
        story = []

        story.append(Paragraph('Metadados da Estação', heading_style))
        story.append(Spacer(1, 5 * mm))

        # Cria tabela com metadados
        metadata_data = [['Informação', 'Valor']]
        for key, value in self.metadata.items():
            metadata_data.append([key, str(value)])

        metadata_table = Table(metadata_data, colWidths=[50 * mm, 100 * mm])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(metadata_table)

        return story

    def _create_quality_analysis(self, heading_style, normal_style) -> List:
        """Cria seção de análise de qualidade"""
        story = []

        story.append(Paragraph('Análise de Qualidade', heading_style))
        story.append(Spacer(1, 5 * mm))

        # Completude
        story.append(Paragraph('<b>Completude (% de dados não-nulos)</b>', normal_style))
        story.append(Spacer(1, 3 * mm))
        
        completeness = self.quality_summary.get('completeness', {})
        completeness_data = [['Variável', 'Não-nulos', 'Nulos', 'Completude (%)']]
        for var, metrics in completeness.items():
            short_name = VARIABLE_NAMES_SHORT.get(var, var)
            # Trunca nome se muito longo
            if len(short_name) > 25:
                short_name = short_name[:22] + '...'
            completeness_data.append([
                short_name,
                str(metrics.get('non_null_count', 0)),
                str(metrics.get('null_count', 0)),
                f"{metrics.get('completeness_percentage', 0):.2f}%",
            ])

        completeness_table = Table(completeness_data, colWidths=[50 * mm, 30 * mm, 30 * mm, 35 * mm])
        completeness_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        story.append(completeness_table)
        story.append(Spacer(1, 8 * mm))

        # Validade
        story.append(Paragraph('<b>Validade (% de dados dentro de limites físicos)</b>', normal_style))
        story.append(Spacer(1, 3 * mm))
        
        validity = self.quality_summary.get('validity', {})
        validity_data = [['Variável', 'Válidos', 'Inválidos', 'Validade (%)']]
        for var, metrics in validity.items():
            short_name = VARIABLE_NAMES_SHORT.get(var, var)
            if len(short_name) > 25:
                short_name = short_name[:22] + '...'
            validity_data.append([
                short_name,
                str(metrics.get('valid_count', 0)),
                str(metrics.get('invalid_count', 0)),
                f"{metrics.get('validity_percentage', 0):.2f}%",
            ])

        validity_table = Table(validity_data, colWidths=[50 * mm, 30 * mm, 30 * mm, 35 * mm])
        validity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        story.append(validity_table)

        return story

    def _create_variable_analysis(self, heading_style, normal_style) -> List:
        """Cria seção de análise por variável"""
        story = []

        story.append(Paragraph('Índice de Qualidade por Variável', heading_style))
        story.append(Spacer(1, 5 * mm))

        quality_data = [['Variável', 'Complet.', 'Validade', 'Consist.', 'Índice']]

        completeness = self.quality_summary.get('completeness', {})
        validity = self.quality_summary.get('validity', {})
        consistency = self.quality_summary.get('consistency', {})

        for var in completeness.keys():
            short_name = VARIABLE_NAMES_SHORT.get(var, var)
            if len(short_name) > 20:
                short_name = short_name[:17] + '...'
            comp_score = completeness.get(var, {}).get('completeness_percentage', 0)
            valid_score = validity.get(var, {}).get('validity_percentage', 0)
            cons_score = consistency.get(var, {}).get('consistency_percentage', 0)
            overall_score = (comp_score * 0.4 + valid_score * 0.4 + cons_score * 0.2)

            quality_data.append([
                short_name,
                f'{comp_score:.1f}%',
                f'{valid_score:.1f}%',
                f'{cons_score:.1f}%',
                f'{overall_score:.1f}%',
            ])

        quality_table = Table(quality_data, colWidths=[45 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        story.append(quality_table)

        return story

    def _add_footer(self, canvas, doc):
        """Adiciona rodapé com data, hora e desenvolvedor"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)

        # Rodapé esquerdo
        footer_text = f'{APP_NAME} - {DEVELOPER_NAME}'
        canvas.drawString(PDF_SETTINGS['margin_left'] * mm, 10 * mm, footer_text)

        # Rodapé direito
        gen_date = self.generation_time.strftime('%d/%m/%Y %H:%M:%S')
        canvas.drawRightString(
            A4[0] - PDF_SETTINGS['margin_right'] * mm,
            10 * mm,
            f'Gerado em: {gen_date}'
        )

        # Número de página
        page_num = doc.page
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f'Página {page_num}')

        canvas.restoreState()