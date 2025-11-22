"""
Módulo de Exportación de Resultados

Exporta resultados a múltiples formatos (Excel, JSON, CSV).

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path


class ResultsExporter:
    """Exportador de resultados a múltiples formatos."""

    def __init__(self, output_dir: str = "results/exports"):
        """
        Inicializa el exportador.

        Args:
            output_dir: Directorio de salida
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_excel(self,
                       data_dict: Dict[str, pd.DataFrame],
                       filename: str = "results.xlsx"):
        """
        Exporta múltiples DataFrames a Excel (hojas separadas).

        Args:
            data_dict: {sheet_name: DataFrame}
            filename: Nombre del archivo
        """
        filepath = self.output_dir / filename

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Exportado a: {filepath}")
        return filepath

    def export_to_json(self, data: Dict, filename: str = "results.json"):
        """Exporta diccionario a JSON."""
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Exportado a: {filepath}")
        return filepath

    def export_to_csv(self, df: pd.DataFrame, filename: str = "results.csv"):
        """Exporta DataFrame a CSV."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)

        print(f"Exportado a: {filepath}")
        return filepath

    def create_summary_report(self,
                             simulation_results: Dict,
                             optimization_results: Dict,
                             comparison_metrics: pd.DataFrame,
                             filename: str = "summary_report.xlsx"):
        """
        Crea reporte resumen completo en Excel.

        Args:
            simulation_results: Resultados de simulación
            optimization_results: Resultados de optimización
            comparison_metrics: Métricas de comparación
            filename: Nombre del archivo
        """
        # Crear hojas del reporte
        sheets = {}

        # Hoja 1: Condiciones óptimas
        if optimization_results:
            sheets['Optimal_Conditions'] = pd.DataFrame([optimization_results])

        # Hoja 2: Métricas de comparación
        if comparison_metrics is not None:
            sheets['Comparison_Metrics'] = comparison_metrics

        # Hoja 3: Resultados de simulación
        if 't' in simulation_results:
            sim_df = pd.DataFrame({
                'time_min': simulation_results['t'],
                **{k: v for k, v in simulation_results.items()
                   if k.startswith('C_') or k.endswith('_%')}
            })
            sheets['Simulation_Results'] = sim_df

        return self.export_to_excel(sheets, filename)
