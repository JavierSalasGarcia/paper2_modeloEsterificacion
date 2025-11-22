"""
Módulo de Comparación y Métricas Estadísticas

Calcula métricas de error y genera análisis comparativo entre modelos.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats


class ModelComparison:
    """
    Comparador de modelos con métricas estadísticas.

    Attributes:
        model1_name (str): Nombre del primer modelo
        model2_name (str): Nombre del segundo modelo
        metrics (Dict): Métricas calculadas
    """

    def __init__(self,
                 model1_name: str = "Model1",
                 model2_name: str = "Model2"):
        """
        Inicializa comparador de modelos.

        Args:
            model1_name: Nombre del primer modelo
            model2_name: Nombre del segundo modelo
        """
        self.model1_name = model1_name
        self.model2_name = model2_name
        self.metrics = {}

    def calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula Root Mean Square Error (RMSE).

        RMSE = sqrt(mean((y_true - y_pred)²))

        Args:
            y_true: Valores verdaderos/referencia
            y_pred: Valores predichos

        Returns:
            RMSE
        """
        return np.sqrt(np.mean((y_true - y_pred) ** 2))

    def calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula Mean Absolute Error (MAE).

        MAE = mean(|y_true - y_pred|)

        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos

        Returns:
            MAE
        """
        return np.mean(np.abs(y_true - y_pred))

    def calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula coeficiente de determinación R².

        R² = 1 - (SS_res / SS_tot)

        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos

        Returns:
            R²
        """
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula Mean Absolute Percentage Error (MAPE).

        MAPE = mean(|y_true - y_pred| / |y_true|) × 100%

        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos

        Returns:
            MAPE (%)
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            mape = np.nan_to_num(mape, nan=0.0, posinf=0.0)

        return mape

    def calculate_nrmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula Normalized Root Mean Square Error (NRMSE).

        NRMSE = RMSE / (max(y_true) - min(y_true))

        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos

        Returns:
            NRMSE
        """
        rmse = self.calculate_rmse(y_true, y_pred)
        range_y = np.max(y_true) - np.min(y_true)

        if range_y == 0:
            return 0.0

        return rmse / range_y

    def calculate_pearson_r(self, y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
        """
        Calcula coeficiente de correlación de Pearson y p-value.

        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos

        Returns:
            (r, p_value)
        """
        r, p_value = stats.pearsonr(y_true, y_pred)
        return r, p_value

    def calculate_all_metrics(self,
                             y_true: np.ndarray,
                             y_pred: np.ndarray,
                             variable_name: str = "") -> Dict:
        """
        Calcula todas las métricas disponibles.

        Args:
            y_true: Valores del modelo de referencia
            y_pred: Valores del modelo a comparar
            variable_name: Nombre de la variable (opcional)

        Returns:
            Diccionario con todas las métricas
        """
        metrics = {
            'variable': variable_name,
            'n_points': len(y_true),
            'RMSE': self.calculate_rmse(y_true, y_pred),
            'MAE': self.calculate_mae(y_true, y_pred),
            'R2': self.calculate_r2(y_true, y_pred),
            'MAPE_%': self.calculate_mape(y_true, y_pred),
            'NRMSE': self.calculate_nrmse(y_true, y_pred),
            'max_error': np.max(np.abs(y_true - y_pred)),
            'mean_error': np.mean(y_true - y_pred),
            'std_error': np.std(y_true - y_pred),
        }

        # Correlación de Pearson
        r, p_value = self.calculate_pearson_r(y_true, y_pred)
        metrics['pearson_r'] = r
        metrics['pearson_p_value'] = p_value

        # Rango de valores
        metrics['y_true_min'] = np.min(y_true)
        metrics['y_true_max'] = np.max(y_true)
        metrics['y_pred_min'] = np.min(y_pred)
        metrics['y_pred_max'] = np.max(y_pred)

        return metrics

    def compare_models(self,
                      model1_results: Dict,
                      model2_results: Dict,
                      variables: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Compara resultados de dos modelos para múltiples variables.

        Args:
            model1_results: Resultados del modelo 1
            model2_results: Resultados del modelo 2
            variables: Lista de variables a comparar (si None, todas las comunes)

        Returns:
            DataFrame con métricas para cada variable
        """
        if variables is None:
            # Encontrar variables comunes
            vars1 = set(k for k in model1_results.keys() if k.startswith('C_') or k.endswith('_%'))
            vars2 = set(k for k in model2_results.keys() if k.startswith('C_') or k.endswith('_%'))
            variables = list(vars1 & vars2)

        all_metrics = []

        for var in variables:
            if var not in model1_results or var not in model2_results:
                continue

            y1 = np.array(model1_results[var])
            y2 = np.array(model2_results[var])

            # Interpolar si tienen diferente longitud
            if len(y1) != len(y2):
                min_len = min(len(y1), len(y2))
                y1 = y1[:min_len]
                y2 = y2[:min_len]

            metrics = self.calculate_all_metrics(y1, y2, var)
            all_metrics.append(metrics)

        df_metrics = pd.DataFrame(all_metrics)
        self.metrics = df_metrics

        return df_metrics

    def generate_summary(self) -> str:
        """
        Genera resumen textual de la comparación.

        Returns:
            String con resumen
        """
        if len(self.metrics) == 0:
            return "No hay métricas calculadas. Ejecute compare_models() primero."

        summary = f"=== Comparación: {self.model1_name} vs {self.model2_name} ===\n\n"

        for _, row in self.metrics.iterrows():
            summary += f"Variable: {row['variable']}\n"
            summary += f"  RMSE: {row['RMSE']:.4e}\n"
            summary += f"  MAE: {row['MAE']:.4e}\n"
            summary += f"  R²: {row['R2']:.4f}\n"
            summary += f"  MAPE: {row['MAPE_%']:.2f}%\n"
            summary += f"  Pearson r: {row['pearson_r']:.4f} (p={row['pearson_p_value']:.4e})\n"
            summary += f"  Error máximo: {row['max_error']:.4e}\n\n"

        # Promedio general
        summary += "=== Promedios Generales ===\n"
        summary += f"  R² promedio: {self.metrics['R2'].mean():.4f}\n"
        summary += f"  RMSE promedio: {self.metrics['RMSE'].mean():.4e}\n"
        summary += f"  MAPE promedio: {self.metrics['MAPE_%'].mean():.2f}%\n"

        return summary

    def classify_agreement(self, R2: float, MAPE: float) -> str:
        """
        Clasifica el nivel de acuerdo entre modelos.

        Args:
            R2: Coeficiente de determinación
            MAPE: Error porcentual absoluto medio

        Returns:
            Clasificación del acuerdo
        """
        if R2 > 0.95 and MAPE < 5:
            return "Excelente"
        elif R2 > 0.90 and MAPE < 10:
            return "Muy bueno"
        elif R2 > 0.80 and MAPE < 15:
            return "Bueno"
        elif R2 > 0.70 and MAPE < 20:
            return "Aceptable"
        else:
            return "Pobre"

    def export_metrics(self, filepath: str, format: str = 'excel'):
        """
        Exporta métricas a archivo.

        Args:
            filepath: Ruta del archivo de salida
            format: Formato ('excel', 'csv', 'json')
        """
        if len(self.metrics) == 0:
            raise ValueError("No hay métricas para exportar")

        if format == 'excel':
            self.metrics.to_excel(filepath, index=False)
        elif format == 'csv':
            self.metrics.to_csv(filepath, index=False)
        elif format == 'json':
            self.metrics.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Formato '{format}' no soportado")

        print(f"Métricas exportadas a: {filepath}")


# Funciones auxiliares

def bland_altman_analysis(y1: np.ndarray, y2: np.ndarray) -> Dict:
    """
    Análisis de Bland-Altman para acuerdo entre métodos.

    Args:
        y1: Valores del método 1
        y2: Valores del método 2

    Returns:
        Diccionario con estadísticas de Bland-Altman
    """
    mean_vals = (y1 + y2) / 2
    diff_vals = y1 - y2

    mean_diff = np.mean(diff_vals)
    std_diff = np.std(diff_vals)

    # Límites de acuerdo (mean ± 1.96*std)
    upper_loa = mean_diff + 1.96 * std_diff
    lower_loa = mean_diff - 1.96 * std_diff

    return {
        'mean_difference': mean_diff,
        'std_difference': std_diff,
        'upper_LOA': upper_loa,
        'lower_LOA': lower_loa,
        'mean_values': mean_vals,
        'differences': diff_vals,
    }


def bootstrap_confidence_intervals(y_true: np.ndarray,
                                   y_pred: np.ndarray,
                                   metric_func: callable,
                                   n_bootstrap: int = 1000,
                                   confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Calcula intervalos de confianza de una métrica usando bootstrap.

    Args:
        y_true: Valores verdaderos
        y_pred: Valores predichos
        metric_func: Función que calcula la métrica
        n_bootstrap: Número de muestras bootstrap
        confidence: Nivel de confianza

    Returns:
        (metric_value, ci_lower, ci_upper)
    """
    n = len(y_true)
    bootstrap_values = []

    for _ in range(n_bootstrap):
        # Muestreo con reemplazo
        indices = np.random.choice(n, n, replace=True)
        y_true_boot = y_true[indices]
        y_pred_boot = y_pred[indices]

        metric = metric_func(y_true_boot, y_pred_boot)
        bootstrap_values.append(metric)

    bootstrap_values = np.array(bootstrap_values)

    # Calcular métrica original
    metric_value = metric_func(y_true, y_pred)

    # Calcular percentiles
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_values, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_values, (1 - alpha / 2) * 100)

    return metric_value, ci_lower, ci_upper


def residual_analysis(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """
    Análisis de residuales.

    Args:
        y_true: Valores verdaderos
        y_pred: Valores predichos

    Returns:
        Diccionario con estadísticas de residuales
    """
    residuals = y_true - y_pred

    # Test de normalidad (Shapiro-Wilk)
    if len(residuals) >= 3:
        statistic, p_value = stats.shapiro(residuals)
    else:
        statistic, p_value = np.nan, np.nan

    return {
        'residuals': residuals,
        'mean': np.mean(residuals),
        'std': np.std(residuals),
        'min': np.min(residuals),
        'max': np.max(residuals),
        'median': np.median(residuals),
        'skewness': stats.skew(residuals),
        'kurtosis': stats.kurtosis(residuals),
        'shapiro_statistic': statistic,
        'shapiro_p_value': p_value,
        'normality': 'Normal' if p_value > 0.05 else 'No normal',
    }


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Model Comparison - Ejemplo de Uso ===\n")

    # Datos sintéticos
    t = np.linspace(0, 120, 13)
    y_model1 = 0.5 * np.exp(-0.015 * t)  # Modelo 1
    y_model2 = 0.5 * np.exp(-0.015 * t) + np.random.normal(0, 0.01, len(t))  # Modelo 2 con ruido

    # Crear comparador
    comparator = ModelComparison(model1_name="Model1", model2_name="Model2")

    # Calcular métricas
    metrics = comparator.calculate_all_metrics(y_model1, y_model2, "C_TG")

    print("Métricas de Comparación:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Clasificar acuerdo
    agreement = comparator.classify_agreement(metrics['R2'], metrics['MAPE_%'])
    print(f"\nNivel de acuerdo: {agreement}")

    # Análisis de Bland-Altman
    print("\n=== Bland-Altman Analysis ===")
    ba = bland_altman_analysis(y_model1, y_model2)
    print(f"  Diferencia media: {ba['mean_difference']:.4f}")
    print(f"  Límite superior: {ba['upper_LOA']:.4f}")
    print(f"  Límite inferior: {ba['lower_LOA']:.4f}")

    # Análisis de residuales
    print("\n=== Residual Analysis ===")
    res_analysis = residual_analysis(y_model1, y_model2)
    print(f"  Media residuales: {res_analysis['mean']:.4e}")
    print(f"  Desviación estándar: {res_analysis['std']:.4e}")
    print(f"  Normalidad: {res_analysis['normality']}")
