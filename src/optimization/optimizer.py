"""
Módulo de Optimización de Variables Operacionales

Optimiza temperatura, agitación (RPM) y concentración de catalizador
para maximizar rendimiento de biodiésel.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from scipy.optimize import minimize, differential_evolution, dual_annealing
from scipy.optimize import OptimizeResult
import warnings

from ..models.kinetic_model import KineticModel


class OperationalOptimizer:
    """
    Optimizador de variables operacionales para transesterificación.

    Attributes:
        model (KineticModel): Modelo cinético
        bounds (Dict): Límites de variables
        objective_type (str): Tipo de objetivo ('maximize_conversion', 'minimize_time')
        optimization_result (OptimizeResult): Resultado de la optimización
    """

    def __init__(self,
                 model: KineticModel,
                 objective_type: str = 'maximize_conversion'):
        """
        Inicializa el optimizador.

        Args:
            model: Instancia de KineticModel
            objective_type: 'maximize_conversion', 'maximize_yield', 'minimize_time'
        """
        self.model = model
        self.objective_type = objective_type
        self.bounds = self._default_bounds()
        self.optimization_result = None
        self.history = []

    def _default_bounds(self) -> Dict:
        """Define límites por defecto para variables (ajustados a condiciones industriales realistas)."""
        return {
            'temperature': (50.0, 65.0),      # °C - Evita saponificación y evaporación de MeOH
            'rpm': (200.0, 800.0),             # rpm
            'catalyst_%': (1.0, 5.0),          # % masa
        }

    def set_bounds(self, bounds: Dict):
        """
        Establece límites personalizados para variables.

        Args:
            bounds: Diccionario con límites {variable: (min, max)}
        """
        self.bounds.update(bounds)

    def _objective_function(self,
                           x: np.ndarray,
                           C0: Dict[str, float],
                           t_reaction: float,
                           target_conversion: float = 95.0,
                           energy_weight: float = 0.0,
                           catalyst_weight: float = 0.0) -> float:
        """
        Función objetivo para optimización.

        Args:
            x: Vector de variables [temperature, rpm, catalyst_%]
            C0: Condiciones iniciales
            t_reaction: Tiempo de reacción (min)
            target_conversion: Conversión objetivo (%)
            energy_weight: Peso para penalización energética (T y RPM)
            catalyst_weight: Peso para penalización de catalizador

        Returns:
            Valor de la función objetivo (a minimizar)
        """
        T, rpm, cat_pct = x

        # Actualizar temperatura del modelo
        self.model.set_temperature(T)

        # Simular reacción
        try:
            results = self.model.simulate(
                t_span=(0, t_reaction),
                C0=C0,
                method='Radau'
            )

            if not results['success']:
                return 1e6  # Penalización por fallo

            # Extraer métricas
            conversion_final = results['conversion_%'][-1]
            yield_final = results['FAME_yield_%'][-1]

            # Guardar historial
            self.history.append({
                'temperature': T,
                'rpm': rpm,
                'catalyst_%': cat_pct,
                'conversion_%': conversion_final,
                'FAME_yield_%': yield_final,
            })

            # Calcular función objetivo según tipo
            if self.objective_type == 'maximize_conversion':
                objective = -conversion_final  # Negativo para minimización

            elif self.objective_type == 'maximize_yield':
                objective = -yield_final

            elif self.objective_type == 'minimize_time':
                # Encontrar tiempo para alcanzar conversión objetivo
                idx_target = np.where(results['conversion_%'] >= target_conversion)[0]
                if len(idx_target) > 0:
                    t_target = results['t'][idx_target[0]]
                    objective = t_target
                else:
                    objective = t_reaction * 2  # Penalización si no alcanza

            elif self.objective_type == 'multiobjective':
                # Optimización multi-objetivo: balancear conversión vs costos operacionales
                # Normalizar variables a [0, 1]
                T_norm = (T - self.bounds['temperature'][0]) / (self.bounds['temperature'][1] - self.bounds['temperature'][0])
                rpm_norm = (rpm - self.bounds['rpm'][0]) / (self.bounds['rpm'][1] - self.bounds['rpm'][0])
                cat_norm = (cat_pct - self.bounds['catalyst_%'][0]) / (self.bounds['catalyst_%'][1] - self.bounds['catalyst_%'][0])

                # Penalizaciones por costos
                energy_penalty = energy_weight * (0.6 * T_norm + 0.4 * rpm_norm)  # 60% temperatura, 40% agitación
                catalyst_penalty = catalyst_weight * cat_norm

                # Función objetivo: maximizar conversión, minimizar costos
                objective = -conversion_final + energy_penalty + catalyst_penalty

            else:
                raise ValueError(f"Tipo de objetivo '{self.objective_type}' no reconocido")

            return objective

        except Exception as e:
            warnings.warn(f"Error en simulación: {str(e)}")
            return 1e6  # Penalización por error

    def optimize(self,
                C0: Dict[str, float],
                t_reaction: float = 120.0,
                method: str = 'differential_evolution',
                maxiter: int = 100,
                verbose: bool = True,
                **kwargs) -> Dict:
        """
        Ejecuta optimización de variables operacionales.

        Args:
            C0: Condiciones iniciales
            t_reaction: Tiempo de reacción (min)
            method: Método de optimización
                   ('differential_evolution', 'nelder-mead', 'slsqp', 'dual_annealing')
            maxiter: Número máximo de iteraciones
            verbose: Si mostrar progreso
            **kwargs: Argumentos adicionales para el optimizador
                     bounds: Diccionario con límites personalizados (opcional)

        Returns:
            Diccionario con resultados de optimización
        """
        self.history = []

        # Actualizar bounds si se proporcionan en kwargs
        if 'bounds' in kwargs:
            self.set_bounds(kwargs['bounds'])
            # Eliminar bounds de kwargs para no pasarlo a _objective_function
            kwargs.pop('bounds')

        # Preparar límites para scipy
        bounds_list = [
            self.bounds['temperature'],
            self.bounds['rpm'],
            self.bounds['catalyst_%'],
        ]

        # Punto inicial (centro del rango)
        x0 = np.array([
            np.mean(self.bounds['temperature']),
            np.mean(self.bounds['rpm']),
            np.mean(self.bounds['catalyst_%']),
        ])

        if verbose:
            print(f"=== Optimización: {self.objective_type} ===")
            print(f"Método: {method}")
            print(f"Límites:")
            print(f"  Temperatura: {self.bounds['temperature']} °C")
            print(f"  RPM: {self.bounds['rpm']}")
            print(f"  Catalizador: {self.bounds['catalyst_%']} %")
            print("\nOptimizando...\n")

        # Filtrar kwargs para _objective_function
        obj_kwargs = {}
        if 'target_conversion' in kwargs:
            obj_kwargs['target_conversion'] = kwargs['target_conversion']
        if 'energy_weight' in kwargs:
            obj_kwargs['energy_weight'] = kwargs['energy_weight']
        if 'catalyst_weight' in kwargs:
            obj_kwargs['catalyst_weight'] = kwargs['catalyst_weight']

        # Ejecutar optimización según método
        if method.lower() == 'differential_evolution':
            result = differential_evolution(
                func=lambda x: self._objective_function(x, C0, t_reaction, **obj_kwargs),
                bounds=bounds_list,
                maxiter=maxiter,
                seed=42,
                disp=verbose,
                workers=1
            )

        elif method.lower() == 'dual_annealing':
            result = dual_annealing(
                func=lambda x: self._objective_function(x, C0, t_reaction, **obj_kwargs),
                bounds=bounds_list,
                maxiter=maxiter,
                seed=42
            )

        elif method.lower() in ['nelder-mead', 'slsqp', 'l-bfgs-b']:
            result = minimize(
                fun=lambda x: self._objective_function(x, C0, t_reaction, **obj_kwargs),
                x0=x0,
                method=method.upper(),
                bounds=bounds_list if method.lower() != 'nelder-mead' else None,
                options={'maxiter': maxiter, 'disp': verbose}
            )

        else:
            raise ValueError(f"Método '{method}' no reconocido")

        self.optimization_result = result

        # Organizar resultados
        T_opt, rpm_opt, cat_opt = result.x

        # Simular con condiciones óptimas para obtener métricas completas
        self.model.set_temperature(T_opt)
        final_results = self.model.simulate(
            t_span=(0, t_reaction),
            C0=C0
        )

        optimal_conditions = {
            'temperature_C': T_opt,
            'rpm': rpm_opt,
            'catalyst_%': cat_opt,
            'objective_value': -result.fun if 'maximize' in self.objective_type else result.fun,
            'conversion_%': final_results['conversion_%'][-1],
            'FAME_yield_%': final_results['FAME_yield_%'][-1],
            'success': result.success,
            'message': result.message,
            'n_iterations': result.nit if hasattr(result, 'nit') else result.nfev,
            'n_evaluations': result.nfev,
        }

        if verbose:
            print("\n=== Condiciones Óptimas ===")
            print(f"  Temperatura: {T_opt:.2f} °C")
            print(f"  RPM: {rpm_opt:.0f}")
            print(f"  Catalizador: {cat_opt:.2f} %")
            print(f"\n=== Resultados ===")
            print(f"  Conversión: {optimal_conditions['conversion_%']:.2f} %")
            print(f"  Rendimiento FAME: {optimal_conditions['FAME_yield_%']:.2f} %")
            print(f"  Evaluaciones: {result.nfev}")
            print(f"  Éxito: {result.success}")

        return optimal_conditions

    def response_surface(self,
                        C0: Dict[str, float],
                        t_reaction: float,
                        var1: str = 'temperature',
                        var2: str = 'catalyst_%',
                        fixed_vars: Optional[Dict] = None,
                        n_points: int = 20) -> Dict:
        """
        Genera superficie de respuesta para dos variables.

        Args:
            C0: Condiciones iniciales
            t_reaction: Tiempo de reacción
            var1: Primera variable ('temperature', 'rpm', 'catalyst_%')
            var2: Segunda variable
            fixed_vars: Valores fijos para otras variables
            n_points: Número de puntos por dimensión

        Returns:
            Diccionario con mallas de variables y respuesta
        """
        if fixed_vars is None:
            fixed_vars = {}

        # Crear mallas
        range1 = np.linspace(self.bounds[var1][0], self.bounds[var1][1], n_points)
        range2 = np.linspace(self.bounds[var2][0], self.bounds[var2][1], n_points)
        X1, X2 = np.meshgrid(range1, range2)

        # Inicializar matriz de respuesta
        Z_conversion = np.zeros_like(X1)
        Z_yield = np.zeros_like(X1)

        # Determinar valor fijo para tercera variable
        all_vars = {'temperature', 'rpm', 'catalyst_%'}
        third_var = list(all_vars - {var1, var2})[0]

        if third_var not in fixed_vars:
            fixed_vars[third_var] = np.mean(self.bounds[third_var])

        # Evaluar superficie
        for i in range(n_points):
            for j in range(n_points):
                # Construir vector de variables
                x = {var1: X1[i, j], var2: X2[i, j]}
                x.update(fixed_vars)

                # Ordenar según [temperature, rpm, catalyst_%]
                x_vec = np.array([
                    x['temperature'],
                    x['rpm'],
                    x['catalyst_%']
                ])

                # Simular
                self.model.set_temperature(x['temperature'])
                try:
                    results = self.model.simulate(
                        t_span=(0, t_reaction),
                        C0=C0,
                        method='Radau'
                    )

                    Z_conversion[i, j] = results['conversion_%'][-1]
                    Z_yield[i, j] = results['FAME_yield_%'][-1]

                except:
                    Z_conversion[i, j] = np.nan
                    Z_yield[i, j] = np.nan

        return {
            var1: X1,
            var2: X2,
            'conversion_%': Z_conversion,
            'FAME_yield_%': Z_yield,
            'fixed_vars': fixed_vars,
        }

    def multi_objective_optimize(self,
                                 C0: Dict[str, float],
                                 t_reaction: float,
                                 weights: Dict[str, float] = None) -> Dict:
        """
        Optimización multiobjetivo (conversión + tiempo + costo).

        Args:
            C0: Condiciones iniciales
            t_reaction: Tiempo máximo de reacción
            weights: Pesos para cada objetivo {'conversion': w1, 'time': w2, 'cost': w3}

        Returns:
            Condiciones óptimas
        """
        if weights is None:
            weights = {'conversion': 1.0, 'time': 0.3, 'cost': 0.5}

        def multi_objective(x):
            T, rpm, cat_pct = x

            self.model.set_temperature(T)
            results = self.model.simulate((0, t_reaction), C0)

            # Objetivo 1: Maximizar conversión
            conversion = results['conversion_%'][-1]
            obj1 = -conversion / 100  # Normalizado

            # Objetivo 2: Minimizar tiempo
            idx_95 = np.where(results['conversion_%'] >= 95)[0]
            if len(idx_95) > 0:
                time_to_95 = results['t'][idx_95[0]]
            else:
                time_to_95 = t_reaction
            obj2 = time_to_95 / t_reaction  # Normalizado

            # Objetivo 3: Minimizar costo (proporcional a catalizador)
            obj3 = cat_pct / 5.0  # Normalizado

            # Función objetivo ponderada
            total_obj = (weights['conversion'] * obj1 +
                        weights['time'] * obj2 +
                        weights['cost'] * obj3)

            return total_obj

        # Optimizar
        bounds_list = [
            self.bounds['temperature'],
            self.bounds['rpm'],
            self.bounds['catalyst_%'],
        ]

        result = differential_evolution(
            func=multi_objective,
            bounds=bounds_list,
            seed=42,
            maxiter=100
        )

        T_opt, rpm_opt, cat_opt = result.x

        # Simular con condiciones óptimas
        self.model.set_temperature(T_opt)
        final_results = self.model.simulate((0, t_reaction), C0)

        return {
            'temperature_C': T_opt,
            'rpm': rpm_opt,
            'catalyst_%': cat_opt,
            'conversion_%': final_results['conversion_%'][-1],
            'FAME_yield_%': final_results['FAME_yield_%'][-1],
            'objective_value': result.fun,
        }

    def get_optimization_history(self) -> pd.DataFrame:
        """
        Retorna historial de evaluaciones de optimización.

        Returns:
            DataFrame con historial
        """
        return pd.DataFrame(self.history)

    def export_results(self, filepath: str, format: str = 'excel'):
        """
        Exporta resultados de optimización.

        Args:
            filepath: Ruta del archivo
            format: Formato ('excel', 'json', 'csv')
        """
        if self.optimization_result is None:
            raise ValueError("Debe ejecutar optimize() primero")

        history_df = self.get_optimization_history()

        if format == 'excel':
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja con condiciones óptimas
                optimal_df = pd.DataFrame([{
                    'temperature_C': self.optimization_result.x[0],
                    'rpm': self.optimization_result.x[1],
                    'catalyst_%': self.optimization_result.x[2],
                    'objective_value': self.optimization_result.fun,
                }])
                optimal_df.to_excel(writer, sheet_name='Optimal', index=False)

                # Hoja con historial
                history_df.to_excel(writer, sheet_name='History', index=False)

            print(f"Resultados guardados en: {filepath}")

        elif format == 'json':
            import json
            with open(filepath, 'w') as f:
                json.dump(self.history, f, indent=2)

        else:
            raise ValueError(f"Formato '{format}' no soportado")


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Optimizer - Ejemplo de Uso ===\n")

    # Crear modelo
    model = KineticModel(model_type='1-step', reversible=True, temperature=65)

    # Condiciones iniciales
    C0 = {
        'TG': 0.5,
        'MeOH': 4.5,
        'FAME': 0.0,
        'GL': 0.0,
    }

    # Crear optimizador
    optimizer = OperationalOptimizer(model, objective_type='maximize_conversion')

    # Ejecutar optimización
    optimal = optimizer.optimize(
        C0=C0,
        t_reaction=120,
        method='differential_evolution',
        maxiter=50,
        verbose=True
    )

    print(f"\n=== Historial ({len(optimizer.history)} evaluaciones) ===")
    history = optimizer.get_optimization_history()
    print(history.describe())
