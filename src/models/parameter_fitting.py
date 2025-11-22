"""
Módulo de Ajuste de Parámetros Cinéticos

Utiliza lmfit para ajustar parámetros cinéticos (Ea, A) a datos experimentales
de transesterificación.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from lmfit import Parameters, Minimizer, report_fit
import warnings

from .kinetic_model import KineticModel


class ParameterFitter:
    """
    Ajustador de parámetros cinéticos usando optimización no lineal.

    Attributes:
        model (KineticModel): Modelo cinético a ajustar
        experimental_data (List[Dict]): Lista de datasets experimentales
        weights (Dict): Pesos para diferentes componentes en la función objetivo
    """

    def __init__(self,
                 model_type: str = '1-step',
                 reversible: bool = True):
        """
        Inicializa el ajustador de parámetros.

        Args:
            model_type: Tipo de modelo ('1-step' o '3-step')
            reversible: Si considerar reversibilidad
        """
        self.model_type = model_type
        self.reversible = reversible
        self.model = None
        self.experimental_data = []
        self.weights = {'TG': 1.0, 'FAME': 1.0, 'DG': 0.5, 'MG': 0.5, 'GL': 0.5}
        self.fit_result = None

    def add_experiment(self,
                      data: pd.DataFrame,
                      T_celsius: float,
                      C0: Dict[str, float],
                      experiment_id: str = ""):
        """
        Agrega un dataset experimental para el ajuste.

        Args:
            data: DataFrame con columnas 'time' y concentraciones ('C_TG', 'C_FAME', etc.)
            T_celsius: Temperatura del experimento (°C)
            C0: Condiciones iniciales del experimento
            experiment_id: Identificador del experimento
        """
        experiment = {
            'data': data,
            'temperature': T_celsius,
            'C0': C0,
            'id': experiment_id or f'exp_{len(self.experimental_data) + 1}'
        }
        self.experimental_data.append(experiment)

    def set_weights(self, weights: Dict[str, float]):
        """
        Establece pesos para diferentes componentes en la función objetivo.

        Args:
            weights: Diccionario {componente: peso}
        """
        self.weights.update(weights)

    def _residuals(self, params_lmfit: Parameters) -> np.ndarray:
        """
        Calcula residuales entre modelo y datos experimentales.

        Args:
            params_lmfit: Objeto Parameters de lmfit

        Returns:
            Array de residuales ponderados
        """
        # Extraer parámetros de lmfit
        kinetic_params = self._lmfit_to_kinetic_params(params_lmfit)

        # Crear modelo con parámetros actuales
        self.model = KineticModel(
            model_type=self.model_type,
            reversible=self.reversible,
            kinetic_params=kinetic_params,
            temperature=65  # Se actualizará para cada experimento
        )

        residuals = []

        # Iterar sobre cada experimento
        for exp in self.experimental_data:
            # Actualizar temperatura
            self.model.set_temperature(exp['temperature'])

            # Simular
            t_exp = exp['data']['time'].values
            results = self.model.simulate(
                t_span=(t_exp[0], t_exp[-1]),
                C0=exp['C0'],
                t_eval=t_exp
            )

            # Calcular residuales para cada componente medido
            for component in self.weights.keys():
                col_name = f'C_{component}'
                if col_name in exp['data'].columns:
                    C_exp = exp['data'][col_name].values
                    C_model = results[col_name]

                    # Residual ponderado
                    weight = self.weights[component]
                    res = weight * (C_exp - C_model)
                    residuals.extend(res)

        return np.array(residuals)

    def _lmfit_to_kinetic_params(self, params_lmfit: Parameters) -> Dict:
        """
        Convierte Parameters de lmfit a diccionario de parámetros cinéticos.

        Args:
            params_lmfit: Objeto Parameters de lmfit

        Returns:
            Diccionario con estructura de parámetros cinéticos
        """
        if self.model_type == '1-step':
            return {
                'Ea_forward': params_lmfit['Ea_forward'].value,
                'Ea_reverse': params_lmfit['Ea_reverse'].value if self.reversible else 0,
                'A_forward': params_lmfit['A_forward'].value,
                'A_reverse': params_lmfit['A_reverse'].value if self.reversible else 0,
            }
        else:  # 3-step
            kinetic_params = {}
            for step in ['step1', 'step2', 'step3']:
                kinetic_params[step] = {
                    'Ea_forward': params_lmfit[f'{step}_Ea_forward'].value,
                    'Ea_reverse': params_lmfit[f'{step}_Ea_reverse'].value if self.reversible else 0,
                    'A_forward': params_lmfit[f'{step}_A_forward'].value,
                    'A_reverse': params_lmfit[f'{step}_A_reverse'].value if self.reversible else 0,
                }
            return kinetic_params

    def setup_parameters(self,
                        initial_guess: Optional[Dict] = None,
                        bounds: Optional[Dict] = None) -> Parameters:
        """
        Configura parámetros iniciales y límites para el ajuste.

        Args:
            initial_guess: Valores iniciales de parámetros
            bounds: Límites (min, max) para cada parámetro

        Returns:
            Objeto Parameters de lmfit configurado
        """
        params = Parameters()

        # Límites por defecto (basados en literatura)
        default_bounds = {
            'Ea': (20, 200),      # kJ/mol
            'A': (1e5, 1e15),     # min^-1 o L/(mol·min)
        }

        if bounds is None:
            bounds = {}

        if self.model_type == '1-step':
            # Valores iniciales por defecto (de literatura)
            defaults = {
                'Ea_forward': 60.0,
                'Ea_reverse': 50.0,
                'A_forward': 1e11,
                'A_reverse': 1e10,
            }

            if initial_guess:
                defaults.update(initial_guess)

            # Ea_forward
            params.add('Ea_forward',
                      value=defaults['Ea_forward'],
                      min=bounds.get('Ea_forward', default_bounds['Ea'])[0],
                      max=bounds.get('Ea_forward', default_bounds['Ea'])[1])

            # A_forward (en escala logarítmica para mejor convergencia)
            params.add('A_forward',
                      value=defaults['A_forward'],
                      min=bounds.get('A_forward', default_bounds['A'])[0],
                      max=bounds.get('A_forward', default_bounds['A'])[1])

            if self.reversible:
                params.add('Ea_reverse',
                          value=defaults['Ea_reverse'],
                          min=bounds.get('Ea_reverse', default_bounds['Ea'])[0],
                          max=bounds.get('Ea_reverse', default_bounds['Ea'])[1])

                params.add('A_reverse',
                          value=defaults['A_reverse'],
                          min=bounds.get('A_reverse', default_bounds['A'])[0],
                          max=bounds.get('A_reverse', default_bounds['A'])[1])

        else:  # 3-step
            # Valores iniciales para cada paso
            for i, step in enumerate(['step1', 'step2', 'step3'], 1):
                defaults = {
                    'Ea_forward': 65.0 - i * 3,  # Decreciente
                    'Ea_reverse': 55.0 - i * 2,
                    'A_forward': 1e11 / (i * 0.5),
                    'A_reverse': 1e10 / (i * 0.5),
                }

                if initial_guess and step in initial_guess:
                    defaults.update(initial_guess[step])

                params.add(f'{step}_Ea_forward',
                          value=defaults['Ea_forward'],
                          min=bounds.get(f'{step}_Ea_forward', default_bounds['Ea'])[0],
                          max=bounds.get(f'{step}_Ea_forward', default_bounds['Ea'])[1])

                params.add(f'{step}_A_forward',
                          value=defaults['A_forward'],
                          min=bounds.get(f'{step}_A_forward', default_bounds['A'])[0],
                          max=bounds.get(f'{step}_A_forward', default_bounds['A'])[1])

                if self.reversible:
                    params.add(f'{step}_Ea_reverse',
                              value=defaults['Ea_reverse'],
                              min=default_bounds['Ea'][0],
                              max=default_bounds['Ea'][1])

                    params.add(f'{step}_A_reverse',
                              value=defaults['A_reverse'],
                              min=default_bounds['A'][0],
                              max=default_bounds['A'][1])

        return params

    def fit(self,
            method: str = 'leastsq',
            max_nfev: int = 1000,
            verbose: bool = True,
            **kwargs) -> Dict:
        """
        Ejecuta el ajuste de parámetros.

        Args:
            method: Método de optimización ('leastsq', 'least_squares', 'differential_evolution')
            max_nfev: Número máximo de evaluaciones de función
            verbose: Si imprimir progreso
            **kwargs: Argumentos adicionales para setup_parameters

        Returns:
            Diccionario con resultados del ajuste
        """
        if len(self.experimental_data) == 0:
            raise ValueError("No hay datos experimentales. Use add_experiment() primero.")

        # Configurar parámetros
        params = self.setup_parameters(**kwargs)

        # Crear minimizador
        minimizer = Minimizer(self._residuals, params)

        # Ajustar
        if verbose:
            print(f"Iniciando ajuste de parámetros ({self.model_type}, reversible={self.reversible})...")
            print(f"Número de experimentos: {len(self.experimental_data)}")
            print(f"Método: {method}")

        self.fit_result = minimizer.minimize(method=method, max_nfev=max_nfev)

        if verbose:
            print("\n=== Resultados del Ajuste ===")
            report_fit(self.fit_result)

        # Organizar resultados
        results = {
            'success': self.fit_result.success,
            'message': self.fit_result.message,
            'nfev': self.fit_result.nfev,
            'chisqr': self.fit_result.chisqr,
            'redchi': self.fit_result.redchi,
            'aic': self.fit_result.aic,
            'bic': self.fit_result.bic,
            'params': self._lmfit_to_kinetic_params(self.fit_result.params),
            'params_lmfit': self.fit_result.params,
            'covariance': self.fit_result.covar,
            'fitted_model': self.model,
        }

        # Calcular R²
        results['R_squared'] = self._calculate_r_squared()

        return results

    def _calculate_r_squared(self) -> float:
        """Calcula coeficiente de determinación R²."""
        if self.fit_result is None:
            return 0.0

        # Calcular residuales finales
        residuals = self.fit_result.residual

        # SS_res (suma de cuadrados de residuales)
        SS_res = np.sum(residuals ** 2)

        # SS_tot (suma de cuadrados totales)
        # Calcular media de todos los datos experimentales
        all_data = []
        for exp in self.experimental_data:
            for component in self.weights.keys():
                col_name = f'C_{component}'
                if col_name in exp['data'].columns:
                    all_data.extend(exp['data'][col_name].values)

        y_mean = np.mean(all_data)
        SS_tot = np.sum((np.array(all_data) - y_mean) ** 2)

        # R² = 1 - SS_res / SS_tot
        if SS_tot == 0:
            return 0.0

        R2 = 1 - (SS_res / SS_tot)
        return R2

    def get_confidence_intervals(self, confidence: float = 0.95) -> Dict:
        """
        Calcula intervalos de confianza para parámetros ajustados.

        Args:
            confidence: Nivel de confianza (default 95%)

        Returns:
            Diccionario con intervalos de confianza
        """
        if self.fit_result is None:
            raise ValueError("Debe ejecutar fit() primero")

        from scipy import stats

        # Grados de libertad
        ndata = len(self.fit_result.residual)
        nparams = len(self.fit_result.var_names)
        dof = ndata - nparams

        # t-value para el nivel de confianza
        t_value = stats.t.ppf((1 + confidence) / 2, dof)

        intervals = {}
        for name, param in self.fit_result.params.items():
            if param.stderr is not None:
                ci = t_value * param.stderr
                intervals[name] = {
                    'value': param.value,
                    'stderr': param.stderr,
                    'ci_lower': param.value - ci,
                    'ci_upper': param.value + ci,
                    'relative_error_%': (param.stderr / param.value * 100) if param.value != 0 else np.inf
                }

        return intervals

    def plot_parity(self, ax=None, components: Optional[List[str]] = None):
        """
        Genera parity plot (modelo vs experimental).

        Args:
            ax: Matplotlib axis (si None, crea nuevo)
            components: Lista de componentes a plotear (si None, todos)

        Returns:
            Matplotlib axis
        """
        import matplotlib.pyplot as plt

        if self.fit_result is None:
            raise ValueError("Debe ejecutar fit() primero")

        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        if components is None:
            components = list(self.weights.keys())

        # Recolectar datos experimentales y del modelo
        C_exp_all = []
        C_model_all = []
        colors = []
        color_map = {'TG': 'blue', 'FAME': 'green', 'DG': 'orange', 'MG': 'red', 'GL': 'purple'}

        for exp in self.experimental_data:
            self.model.set_temperature(exp['temperature'])
            t_exp = exp['data']['time'].values
            results = self.model.simulate(
                t_span=(t_exp[0], t_exp[-1]),
                C0=exp['C0'],
                t_eval=t_exp
            )

            for component in components:
                col_name = f'C_{component}'
                if col_name in exp['data'].columns:
                    C_exp = exp['data'][col_name].values
                    C_model = results[col_name]

                    C_exp_all.extend(C_exp)
                    C_model_all.extend(C_model)
                    colors.extend([color_map.get(component, 'gray')] * len(C_exp))

        # Plot
        ax.scatter(C_exp_all, C_model_all, c=colors, alpha=0.6, edgecolors='k')

        # Línea de paridad
        max_val = max(max(C_exp_all), max(C_model_all))
        ax.plot([0, max_val], [0, max_val], 'k--', label='Paridad perfecta')

        # Bandas de ±10%
        ax.fill_between([0, max_val], [0, max_val * 0.9], [0, max_val * 1.1],
                        alpha=0.2, color='gray', label='±10%')

        ax.set_xlabel('Concentración Experimental (mol/L)', fontsize=12)
        ax.set_ylabel('Concentración Modelo (mol/L)', fontsize=12)
        ax.set_title(f'Parity Plot - Modelo {self.model_type}', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

        return ax

    def export_results(self, filepath: str, format: str = 'json'):
        """
        Exporta resultados del ajuste a archivo.

        Args:
            filepath: Ruta del archivo
            format: Formato ('json', 'yaml', 'csv')
        """
        if self.fit_result is None:
            raise ValueError("Debe ejecutar fit() primero")

        import json

        results_dict = {
            'model_type': self.model_type,
            'reversible': self.reversible,
            'fitted_parameters': self._lmfit_to_kinetic_params(self.fit_result.params),
            'statistics': {
                'R_squared': self._calculate_r_squared(),
                'chisqr': self.fit_result.chisqr,
                'redchi': self.fit_result.redchi,
                'aic': self.fit_result.aic,
                'bic': self.fit_result.bic,
                'nfev': self.fit_result.nfev,
            },
            'confidence_intervals': self.get_confidence_intervals(),
            'experiments': [
                {
                    'id': exp['id'],
                    'temperature': exp['temperature'],
                    'n_points': len(exp['data'])
                }
                for exp in self.experimental_data
            ]
        }

        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(results_dict, f, indent=2, default=str)
        else:
            raise NotImplementedError(f"Formato '{format}' no implementado aún")


if __name__ == "__main__":
    # Ejemplo de uso con datos sintéticos
    print("=== Parameter Fitting - Ejemplo de Uso ===\n")

    # Generar datos sintéticos (simulando experimentos)
    true_model = KineticModel(model_type='1-step', reversible=True, temperature=65)

    # Experimento 1: 65°C
    C0_exp1 = {'TG': 0.5, 'MeOH': 4.5, 'FAME': 0.0, 'GL': 0.0}
    t_exp1 = np.array([0, 15, 30, 45, 60, 90, 120])
    results_exp1 = true_model.simulate((0, 120), C0_exp1, t_eval=t_exp1)

    # Agregar ruido
    noise_level = 0.02
    data_exp1 = pd.DataFrame({
        'time': t_exp1,
        'C_TG': results_exp1['C_TG'] + np.random.normal(0, noise_level, len(t_exp1)),
        'C_FAME': results_exp1['C_FAME'] + np.random.normal(0, noise_level, len(t_exp1)),
    })

    # Crear fitter
    fitter = ParameterFitter(model_type='1-step', reversible=True)
    fitter.add_experiment(data_exp1, T_celsius=65, C0=C0_exp1, experiment_id="Exp_65C")

    # Ajustar parámetros
    results = fitter.fit(method='leastsq', verbose=True)

    print(f"\nR² = {results['R_squared']:.4f}")
    print(f"Chi-square reducido = {results['redchi']:.4e}")

    print("\nParámetros ajustados:")
    for param_name, value in results['params'].items():
        print(f"  {param_name}: {value:.4e}")

    print("\nIntervalos de confianza (95%):")
    ci = fitter.get_confidence_intervals()
    for name, vals in ci.items():
        print(f"  {name}: {vals['value']:.4e} ± {vals['stderr']:.4e} "
              f"({vals['relative_error_%']:.2f}%)")
