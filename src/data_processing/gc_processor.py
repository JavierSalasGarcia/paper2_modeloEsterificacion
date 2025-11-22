"""
Módulo para Procesamiento de Datos de Cromatografía de Gases (GC-FID)

Este módulo procesa datos crudos de cromatografía de gases con detector de ionización
de llama (GC-FID) para cuantificar FAMEs y calcular conversión de triglicéridos.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings


class GCProcessor:
    """
    Procesador de datos de cromatografía de gases (GC-FID) para análisis de biodiésel.

    Attributes:
        response_factors (Dict[str, float]): Factores de respuesta para cada FAME
        internal_standard (str): Nombre del estándar interno utilizado
        is_concentration (float): Concentración del estándar interno (mol/L)
    """

    def __init__(self,
                 response_factors: Optional[Dict[str, float]] = None,
                 internal_standard: str = "methyl_heptadecanoate",
                 is_concentration: float = 0.1):
        """
        Inicializa el procesador GC-FID.

        Args:
            response_factors: Diccionario con factores de respuesta {compuesto: factor}
            internal_standard: Nombre del estándar interno
            is_concentration: Concentración del estándar interno (mol/L)
        """
        self.internal_standard = internal_standard
        self.is_concentration = is_concentration

        # Factores de respuesta por defecto para FAMEs comunes
        self.response_factors = response_factors or self._default_response_factors()

    def _default_response_factors(self) -> Dict[str, float]:
        """
        Factores de respuesta por defecto para FAMEs comunes.

        Basados en literatura para GC-FID.
        """
        return {
            # FAMEs (ésteres metílicos de ácidos grasos)
            'methyl_palmitate': 1.05,      # C16:0
            'methyl_stearate': 1.08,        # C18:0
            'methyl_oleate': 1.06,          # C18:1
            'methyl_linoleate': 1.04,       # C18:2
            'methyl_linolenate': 1.02,      # C18:3

            # Estándar interno
            'methyl_heptadecanoate': 1.00,  # C17:0 (IS)

            # Intermediarios
            'monoglyceride': 0.95,
            'diglyceride': 0.93,
            'triglyceride': 0.90,

            # Otros
            'methanol': 0.80,
            'glycerol': 0.85,
        }

    def calculate_concentration(self,
                               area: float,
                               area_is: float,
                               compound: str) -> float:
        """
        Calcula la concentración de un compuesto usando el método del estándar interno.

        C_i = (A_i / A_IS) * (C_IS / f_i)

        Args:
            area: Área del pico del compuesto
            area_is: Área del pico del estándar interno
            compound: Nombre del compuesto

        Returns:
            Concentración del compuesto (mol/L)
        """
        if area_is == 0:
            warnings.warn("Área del estándar interno es cero. Retornando 0.")
            return 0.0

        rf = self.response_factors.get(compound, 1.0)
        concentration = (area / area_is) * (self.is_concentration / rf)

        return concentration

    def calculate_conversion(self,
                           C_TG: float,
                           C_TG0: float) -> float:
        """
        Calcula la conversión de triglicéridos.

        X_TG = (C_TG0 - C_TG) / C_TG0 * 100%

        Args:
            C_TG: Concentración actual de triglicéridos (mol/L)
            C_TG0: Concentración inicial de triglicéridos (mol/L)

        Returns:
            Conversión en porcentaje (%)
        """
        if C_TG0 == 0:
            warnings.warn("Concentración inicial de TG es cero. Retornando 0.")
            return 0.0

        conversion = ((C_TG0 - C_TG) / C_TG0) * 100.0
        return max(0.0, min(100.0, conversion))  # Limitar entre 0-100%

    def calculate_fame_yield(self,
                            C_FAME_total: float,
                            C_TG0: float) -> float:
        """
        Calcula el rendimiento de FAMEs.

        Y_FAME = (Σ C_FAME) / (3 * C_TG0) * 100%

        Args:
            C_FAME_total: Concentración total de FAMEs (mol/L)
            C_TG0: Concentración inicial de triglicéridos (mol/L)

        Returns:
            Rendimiento de FAME en porcentaje (%)
        """
        if C_TG0 == 0:
            warnings.warn("Concentración inicial de TG es cero. Retornando 0.")
            return 0.0

        # Cada triglicérido genera 3 FAMEs
        yield_fame = (C_FAME_total / (3.0 * C_TG0)) * 100.0
        return max(0.0, min(100.0, yield_fame))

    def process_chromatogram(self,
                            chromatogram_data: pd.DataFrame,
                            time_column: str = 'time',
                            area_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Procesa un cromatograma completo con múltiples compuestos.

        Args:
            chromatogram_data: DataFrame con columnas de tiempo y áreas de picos
            time_column: Nombre de la columna de tiempos de retención
            area_columns: Lista de nombres de columnas con áreas (si None, usar todas excepto time)

        Returns:
            DataFrame con concentraciones calculadas
        """
        if area_columns is None:
            area_columns = [col for col in chromatogram_data.columns if col != time_column]

        # Verificar que existe columna de estándar interno
        if self.internal_standard not in area_columns:
            raise ValueError(f"Estándar interno '{self.internal_standard}' no encontrado en datos")

        results = pd.DataFrame()
        results[time_column] = chromatogram_data[time_column]

        area_is = chromatogram_data[self.internal_standard]

        # Calcular concentraciones para cada compuesto
        for compound in area_columns:
            if compound == self.internal_standard:
                continue

            areas = chromatogram_data[compound]
            concentrations = [
                self.calculate_concentration(area, area_is.iloc[i], compound)
                for i, area in enumerate(areas)
            ]
            results[f'C_{compound}'] = concentrations

        return results

    def process_time_series(self,
                          data: Dict[float, Dict[str, float]],
                          C_TG0: float) -> pd.DataFrame:
        """
        Procesa una serie temporal de muestras de reacción.

        Args:
            data: Diccionario {tiempo: {compuesto: área}}
            C_TG0: Concentración inicial de triglicéridos (mol/L)

        Returns:
            DataFrame con tiempo, concentraciones, conversión y rendimiento
        """
        results = []

        for time, areas in sorted(data.items()):
            row = {'time': time}

            # Obtener área del estándar interno
            area_is = areas.get(self.internal_standard, 0)

            if area_is == 0:
                warnings.warn(f"Área IS = 0 en t={time}. Saltando este punto.")
                continue

            # Calcular concentraciones
            C_TG = 0
            C_DG = 0
            C_MG = 0
            C_GL = 0
            C_FAME_total = 0

            for compound, area in areas.items():
                if compound == self.internal_standard:
                    continue

                conc = self.calculate_concentration(area, area_is, compound)
                row[f'C_{compound}'] = conc

                # Sumar categorías
                if 'triglyceride' in compound.lower() or compound.lower() == 'tg':
                    C_TG += conc
                elif 'diglyceride' in compound.lower() or compound.lower() == 'dg':
                    C_DG += conc
                elif 'monoglyceride' in compound.lower() or compound.lower() == 'mg':
                    C_MG += conc
                elif 'glycerol' in compound.lower() or compound.lower() == 'gl':
                    C_GL += conc
                elif 'methyl' in compound.lower() or 'fame' in compound.lower():
                    C_FAME_total += conc

            # Agregar totales por categoría
            row['C_TG_total'] = C_TG
            row['C_DG_total'] = C_DG
            row['C_MG_total'] = C_MG
            row['C_GL_total'] = C_GL
            row['C_FAME_total'] = C_FAME_total

            # Calcular conversión y rendimiento
            row['conversion_%'] = self.calculate_conversion(C_TG, C_TG0)
            row['FAME_yield_%'] = self.calculate_fame_yield(C_FAME_total, C_TG0)

            results.append(row)

        return pd.DataFrame(results)

    def load_from_csv(self,
                     filepath: str,
                     time_col: str = 'time_min',
                     **kwargs) -> pd.DataFrame:
        """
        Carga datos de cromatografía desde archivo CSV.

        Args:
            filepath: Ruta al archivo CSV
            time_col: Nombre de la columna de tiempo
            **kwargs: Argumentos adicionales para pd.read_csv

        Returns:
            DataFrame con datos crudos
        """
        data = pd.read_csv(filepath, **kwargs)

        if time_col not in data.columns:
            raise ValueError(f"Columna de tiempo '{time_col}' no encontrada en CSV")

        return data

    def csv_to_dict(self,
                    df: pd.DataFrame,
                    time_col: str = 'tiempo_min',
                    compound_col: str = 'compuesto',
                    area_col: str = 'area_pico') -> Dict[float, Dict[str, float]]:
        """
        Convierte DataFrame en formato largo a diccionario anidado.

        Args:
            df: DataFrame con columnas tiempo, compuesto, área
            time_col: Nombre de columna de tiempo
            compound_col: Nombre de columna de compuesto
            area_col: Nombre de columna de área

        Returns:
            Diccionario {tiempo: {compuesto: área}}
        """
        result = {}

        for _, row in df.iterrows():
            time = float(row[time_col])
            compound = str(row[compound_col])
            area = float(row[area_col])

            if time not in result:
                result[time] = {}

            result[time][compound] = area

        return result

    def export_processed_data(self,
                            processed_data: pd.DataFrame,
                            output_path: str,
                            format: str = 'csv'):
        """
        Exporta datos procesados a archivo.

        Args:
            processed_data: DataFrame con datos procesados
            output_path: Ruta del archivo de salida
            format: Formato ('csv', 'excel', 'json')
        """
        if format == 'csv':
            processed_data.to_csv(output_path, index=False)
        elif format == 'excel':
            processed_data.to_excel(output_path, index=False)
        elif format == 'json':
            processed_data.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Formato '{format}' no soportado. Use 'csv', 'excel' o 'json'.")

    def summary_statistics(self, processed_data: pd.DataFrame) -> Dict:
        """
        Calcula estadísticas resumen de los datos procesados.

        Args:
            processed_data: DataFrame con datos procesados

        Returns:
            Diccionario con estadísticas
        """
        stats = {}

        if 'conversion_%' in processed_data.columns:
            stats['conversion'] = {
                'initial': processed_data['conversion_%'].iloc[0],
                'final': processed_data['conversion_%'].iloc[-1],
                'max': processed_data['conversion_%'].max(),
                'mean': processed_data['conversion_%'].mean(),
                'std': processed_data['conversion_%'].std()
            }

        if 'FAME_yield_%' in processed_data.columns:
            stats['FAME_yield'] = {
                'final': processed_data['FAME_yield_%'].iloc[-1],
                'max': processed_data['FAME_yield_%'].max(),
                'mean': processed_data['FAME_yield_%'].mean()
            }

        return stats


# Funciones de utilidad

def validate_chromatogram_data(data: pd.DataFrame,
                              required_columns: List[str]) -> Tuple[bool, str]:
    """
    Valida que el DataFrame de cromatograma tenga las columnas requeridas.

    Args:
        data: DataFrame a validar
        required_columns: Lista de columnas requeridas

    Returns:
        (valid, message): Tupla con booleano de validez y mensaje
    """
    missing = [col for col in required_columns if col not in data.columns]

    if missing:
        return False, f"Columnas faltantes: {', '.join(missing)}"

    return True, "Datos válidos"


def calculate_response_factor_experimental(area_compound: float,
                                          conc_compound: float,
                                          area_is: float,
                                          conc_is: float) -> float:
    """
    Calcula el factor de respuesta experimental para un compuesto.

    RF = (A_compound / C_compound) / (A_IS / C_IS)

    Args:
        area_compound: Área del pico del compuesto
        conc_compound: Concentración conocida del compuesto
        area_is: Área del estándar interno
        conc_is: Concentración del estándar interno

    Returns:
        Factor de respuesta
    """
    if conc_compound == 0 or conc_is == 0:
        raise ValueError("Concentraciones no pueden ser cero")

    rf = (area_compound / conc_compound) / (area_is / conc_is)
    return rf


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== GC Processor - Ejemplo de Uso ===\n")

    # Crear procesador
    processor = GCProcessor()

    # Datos de ejemplo (áreas de picos)
    example_data = {
        0: {'methyl_heptadecanoate': 1000, 'triglyceride': 900, 'methyl_oleate': 100},
        30: {'methyl_heptadecanoate': 1000, 'triglyceride': 600, 'methyl_oleate': 400},
        60: {'methyl_heptadecanoate': 1000, 'triglyceride': 300, 'methyl_oleate': 700},
        90: {'methyl_heptadecanoate': 1000, 'triglyceride': 100, 'methyl_oleate': 900},
    }

    # Concentración inicial de TG
    C_TG0 = 0.5  # mol/L

    # Procesar serie temporal
    results = processor.process_time_series(example_data, C_TG0)

    print("Resultados procesados:")
    print(results[['time', 'C_TG_total', 'C_FAME_total', 'conversion_%', 'FAME_yield_%']])

    print("\n=== Estadísticas Resumen ===")
    stats = processor.summary_statistics(results)
    print(f"Conversión final: {stats['conversion']['final']:.2f}%")
    print(f"Rendimiento FAME final: {stats['FAME_yield']['final']:.2f}%")
