#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para calibrar pesos de optimización multi-objetivo usando ML.

Objetivo: Encontrar función de pesos que produzca transición gradual
         en condiciones operacionales (T, RPM, Cat) vs tiempo de reacción.

Autor: J. Salas-García et al.
Fecha: 2025-11-22
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.kinetic_model import KineticModel
from src.optimization.optimizer import OperationalOptimizer


class WeightCalibrator:
    """
    Calibra pesos de optimización multi-objetivo para transición gradual.
    """

    def __init__(self,
                 kinetic_params: Dict,
                 time_range: Tuple[float, float] = (60, 120),
                 n_points: int = 5):
        """
        Inicializa calibrador.

        Args:
            kinetic_params: Parámetros cinéticos {A, Ea}
            time_range: Rango de tiempos (min, max) en minutos
            n_points: Número de puntos a evaluar
        """
        self.kinetic_params = kinetic_params
        self.time_range = time_range
        self.n_points = n_points

        # Generar tiempos equiespaciados
        self.times = np.linspace(time_range[0], time_range[1], n_points)

        # Condiciones iniciales estándar
        self.C0 = {
            'TG': 0.5,
            'MeOH': 0.5 * 6.0,  # Relación molar 6:1
            'FAME': 0.0,
            'GL': 0.0,
        }

        # Bounds de optimización
        self.bounds = {
            'temperature': (50, 65),
            'rpm': (200, 800),
            'catalyst_%': (0.5, 2.5),
        }

    def run_optimization(self,
                        t_reaction: float,
                        energy_weight: float,
                        catalyst_weight: float) -> Dict:
        """
        Ejecuta optimización para un tiempo y pesos dados.

        Returns:
            Dict con {T, rpm, cat, conversion}
        """
        # Crear modelo cinético
        model = KineticModel(
            model_type='1-step',
            reversible=False,
            temperature=60.0,
            kinetic_params={
                'A_forward': self.kinetic_params['A'],
                'Ea_forward': self.kinetic_params['Ea'] / 1000.0,  # J/mol → kJ/mol
                'A_reverse': 0,
                'Ea_reverse': 0
            }
        )

        # Crear optimizador
        optimizer = OperationalOptimizer(model, objective_type='multiobjective')

        # Ejecutar optimización
        result = optimizer.optimize(
            C0=self.C0,
            t_reaction=t_reaction,
            method='differential_evolution',
            bounds=self.bounds,
            maxiter=20,  # Muy reducido para calibración rápida
            energy_weight=energy_weight,
            catalyst_weight=catalyst_weight,
            verbose=False
        )

        return {
            'temperature': result['temperature_C'],
            'rpm': result['rpm'],
            'catalyst_%': result['catalyst_%'],
            'conversion': result['conversion_%']
        }

    def evaluate_weight_function(self,
                                 weight_params: np.ndarray) -> float:
        """
        Evalúa función de pesos y calcula penalización por discontinuidad.

        Args:
            weight_params: [a0, a1, a2, b0, b1, b2]
                          energy_weight = a0 + a1*t_norm + a2*t_norm^2
                          catalyst_weight = b0 + b1*t_norm + b2*t_norm^2

        Returns:
            Score (menor es mejor): suma de discontinuidades + penalizaciones
        """
        a0, a1, a2, b0, b1, b2 = weight_params

        # Normalizar tiempos
        t_norm = (self.times - self.time_range[0]) / (self.time_range[1] - self.time_range[0])

        # Calcular pesos para cada tiempo
        energy_weights = a0 + a1 * t_norm + a2 * (t_norm ** 2)
        catalyst_weights = b0 + b1 * t_norm + b2 * (t_norm ** 2)

        # Forzar pesos no negativos
        energy_weights = np.maximum(0, energy_weights)
        catalyst_weights = np.maximum(0, catalyst_weights)

        # Ejecutar optimizaciones
        results = []
        for i, t in enumerate(self.times):
            try:
                res = self.run_optimization(
                    t_reaction=t,
                    energy_weight=energy_weights[i],
                    catalyst_weight=catalyst_weights[i]
                )
                results.append(res)
            except Exception as e:
                print(f"Error en t={t}: {e}")
                return 1e6

        # Extraer variables
        temps = np.array([r['temperature'] for r in results])
        rpms = np.array([r['rpm'] for r in results])
        cats = np.array([r['catalyst_%'] for r in results])
        convs = np.array([r['conversion'] for r in results])

        # Calcular discontinuidades (variaciones abruptas)
        # Usar diferencias normalizadas
        dt = np.diff(self.times)

        # Normalizar cambios por el rango de cada variable
        dT_norm = np.abs(np.diff(temps)) / (self.bounds['temperature'][1] - self.bounds['temperature'][0])
        dRPM_norm = np.abs(np.diff(rpms)) / (self.bounds['rpm'][1] - self.bounds['rpm'][0])
        dCat_norm = np.abs(np.diff(cats)) / (self.bounds['catalyst_%'][1] - self.bounds['catalyst_%'][0])

        # Penalización por discontinuidad (queremos cambios suaves)
        discontinuity_penalty = (
            100.0 * np.sum(dT_norm / dt) +      # Penalizar cambios bruscos en T
            100.0 * np.sum(dRPM_norm / dt) +    # Penalizar cambios bruscos en RPM
            100.0 * np.sum(dCat_norm / dt)      # Penalizar cambios bruscos en Cat
        )

        # Penalización por valores constantes (queremos transición gradual)
        # Si RPM y Cat no cambian entre puntos consecutivos, penalizar
        rpm_constant_penalty = 50.0 * np.sum(dRPM_norm < 0.01)  # < 1% de cambio
        cat_constant_penalty = 50.0 * np.sum(dCat_norm < 0.01)

        # Penalización si conversión final < 96.5% (norma EN 14214)
        conversion_penalty = 0
        if convs[-1] < 96.5:
            conversion_penalty = 1000.0 * (96.5 - convs[-1])

        # Penalización si pesos son demasiado grandes (queremos pesos razonables)
        weight_magnitude_penalty = 0.1 * (np.sum(energy_weights**2) + np.sum(catalyst_weights**2))

        # Score total
        score = (discontinuity_penalty +
                rpm_constant_penalty +
                cat_constant_penalty +
                conversion_penalty +
                weight_magnitude_penalty)

        return score

    def calibrate(self, method='differential_evolution') -> Dict:
        """
        Calibra parámetros de función de pesos.

        Returns:
            Dict con parámetros óptimos y resultados
        """
        print("="*70)
        print("CALIBRACIÓN DE PESOS DE OPTIMIZACIÓN MULTI-OBJETIVO")
        print("="*70)
        print(f"\nTiempos de reacción: {self.times}")
        print(f"Objetivo: Transición gradual en T, RPM, Cat%")
        print(f"\nMétodo de calibración: {method}")
        print()

        # Límites para parámetros de función cuadrática
        # energy_weight = a0 + a1*t + a2*t^2
        # catalyst_weight = b0 + b1*t + b2*t^2
        param_bounds = [
            (0, 0.5),   # a0: intercepto energy
            (0, 5.0),   # a1: coef lineal energy
            (0, 5.0),   # a2: coef cuadrático energy
            (0, 0.2),   # b0: intercepto catalyst
            (0, 2.0),   # b1: coef lineal catalyst
            (0, 2.0),   # b2: coef cuadrático catalyst
        ]

        if method == 'differential_evolution':
            print("Ejecutando Differential Evolution...")
            result = differential_evolution(
                func=self.evaluate_weight_function,
                bounds=param_bounds,
                maxiter=30,  # Reducido para prueba rápida
                seed=42,
                disp=True,
                workers=1,
                atol=0.01,
                tol=0.01
            )
        else:
            # Método de minimización local
            x0 = np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2])
            result = minimize(
                fun=self.evaluate_weight_function,
                x0=x0,
                method='L-BFGS-B',
                bounds=param_bounds
            )

        # Extraer parámetros óptimos
        a0, a1, a2, b0, b1, b2 = result.x

        print("\n" + "="*70)
        print("PARÁMETROS CALIBRADOS")
        print("="*70)
        print(f"\nFunción de pesos de energía:")
        print(f"  energy_weight(t) = {a0:.4f} + {a1:.4f}*t_norm + {a2:.4f}*t_norm²")
        print(f"\nFunción de pesos de catalizador:")
        print(f"  catalyst_weight(t) = {b0:.4f} + {b1:.4f}*t_norm + {b2:.4f}*t_norm²")
        print(f"\nScore final: {result.fun:.2f}")
        print()

        # Validar con optimizaciones finales
        print("Validando con optimizaciones finales...")
        t_norm = (self.times - self.time_range[0]) / (self.time_range[1] - self.time_range[0])
        energy_weights = a0 + a1 * t_norm + a2 * (t_norm ** 2)
        catalyst_weights = b0 + b1 * t_norm + b2 * (t_norm ** 2)

        final_results = []
        for i, t in enumerate(self.times):
            res = self.run_optimization(
                t_reaction=t,
                energy_weight=max(0, energy_weights[i]),
                catalyst_weight=max(0, catalyst_weights[i])
            )
            final_results.append({
                't_min': t,
                'energy_weight': max(0, energy_weights[i]),
                'catalyst_weight': max(0, catalyst_weights[i]),
                **res
            })

        # Imprimir tabla de resultados
        df = pd.DataFrame(final_results)
        print("\nRESULTADOS DE VALIDACIÓN:")
        print("="*70)
        print(df.to_string(index=False))
        print()

        # Crear gráficas
        self._plot_results(df, a0, a1, a2, b0, b1, b2)

        return {
            'params': {
                'a0': float(a0), 'a1': float(a1), 'a2': float(a2),
                'b0': float(b0), 'b1': float(b1), 'b2': float(b2)
            },
            'results': final_results,
            'score': float(result.fun)
        }

    def _plot_results(self, df: pd.DataFrame,
                     a0, a1, a2, b0, b1, b2):
        """Genera gráficas de resultados de calibración."""
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))

        # Plot 1: Temperatura vs Tiempo
        ax = axes[0, 0]
        ax.plot(df['t_min'], df['temperature'], 'o-', linewidth=2, markersize=8)
        ax.set_xlabel('Tiempo (min)', fontweight='bold')
        ax.set_ylabel('Temperatura (°C)', fontweight='bold')
        ax.set_title('Temperatura Óptima vs Tiempo', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Plot 2: RPM vs Tiempo
        ax = axes[0, 1]
        ax.plot(df['t_min'], df['rpm'], 'o-', linewidth=2, markersize=8, color='orange')
        ax.set_xlabel('Tiempo (min)', fontweight='bold')
        ax.set_ylabel('RPM', fontweight='bold')
        ax.set_title('Agitación Óptima vs Tiempo', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Plot 3: Catalizador vs Tiempo
        ax = axes[0, 2]
        ax.plot(df['t_min'], df['catalyst_%'], 'o-', linewidth=2, markersize=8, color='green')
        ax.set_xlabel('Tiempo (min)', fontweight='bold')
        ax.set_ylabel('Catalizador (%)', fontweight='bold')
        ax.set_title('% CaO Óptimo vs Tiempo', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Plot 4: Conversión vs Tiempo
        ax = axes[1, 0]
        ax.plot(df['t_min'], df['conversion'], 'o-', linewidth=2, markersize=8, color='red')
        ax.axhline(y=96.5, color='r', linestyle='--', linewidth=2, label='EN 14214')
        ax.set_xlabel('Tiempo (min)', fontweight='bold')
        ax.set_ylabel('Conversión (%)', fontweight='bold')
        ax.set_title('Conversión vs Tiempo', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 5: Función de pesos
        ax = axes[1, 1]
        t_norm = (df['t_min'] - self.time_range[0]) / (self.time_range[1] - self.time_range[0])
        ax.plot(df['t_min'], df['energy_weight'], 'o-', linewidth=2, markersize=8, label='Energy')
        ax.plot(df['t_min'], df['catalyst_weight'], 's-', linewidth=2, markersize=8, label='Catalyst')
        ax.set_xlabel('Tiempo (min)', fontweight='bold')
        ax.set_ylabel('Peso de penalización', fontweight='bold')
        ax.set_title('Funciones de Peso Calibradas', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 6: Ecuaciones de peso
        ax = axes[1, 2]
        ax.axis('off')
        equations = f"""
FUNCIONES CALIBRADAS:

Energy weight:
  w_e(t) = {a0:.3f} + {a1:.3f}·t_n + {a2:.3f}·t_n²

Catalyst weight:
  w_c(t) = {b0:.3f} + {b1:.3f}·t_n + {b2:.3f}·t_n²

donde:
  t_n = (t - {self.time_range[0]}) / {self.time_range[1] - self.time_range[0]}

Rango de tiempos: {self.time_range[0]}-{self.time_range[1]} min
        """
        ax.text(0.1, 0.5, equations, fontsize=11, family='monospace',
               verticalalignment='center')

        plt.tight_layout()
        plt.savefig('weight_calibration_results.png', dpi=300, bbox_inches='tight')
        print("✓ Gráficas guardadas en: weight_calibration_results.png")


def main():
    """Función principal."""
    # Cargar parámetros cinéticos calibrados
    with open('variables_esterificacion_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    kinetic_params = {
        'A': dataset['parametros_cineticos_calibrados']['factor_preexponencial']['valor'],
        'Ea': dataset['parametros_cineticos_calibrados']['energia_activacion']['valor']
    }

    print("\nParámetros cinéticos:")
    print(f"  A = {kinetic_params['A']:.2e} L/(mol·min)")
    print(f"  Ea = {kinetic_params['Ea']:.0f} J/mol")
    print()

    # Crear calibrador (versión rápida para prueba)
    calibrator = WeightCalibrator(
        kinetic_params=kinetic_params,
        time_range=(60, 120),
        n_points=5  # 60, 75, 90, 105, 120 (menos puntos = más rápido)
    )

    # Calibrar (versión rápida)
    results = calibrator.calibrate(method='differential_evolution')

    # Guardar resultados
    output_file = 'calibrated_weights.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✓ Resultados guardados en: {output_file}")
    print()

    # Imprimir código para main.py
    params = results['params']
    print("="*70)
    print("CÓDIGO PARA USAR EN main.py:")
    print("="*70)
    print(f"""
# Normalizar tiempo
t_norm = (t_reaction - 60.0) / (120.0 - 60.0)

# Aplicar función calibrada
energy_weight = {params['a0']:.4f} + {params['a1']:.4f}*t_norm + {params['a2']:.4f}*(t_norm**2)
catalyst_weight = {params['b0']:.4f} + {params['b1']:.4f}*t_norm + {params['b2']:.4f}*(t_norm**2)

# Asegurar no-negatividad
energy_weight = max(0, energy_weight)
catalyst_weight = max(0, catalyst_weight)
    """)


if __name__ == '__main__':
    main()
