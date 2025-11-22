#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Lógica Difusa para Optimización Multi-Objetivo

Usa lógica difusa para determinar pesos de penalización que produzcan
transiciones suaves entre regímenes operacionales.

Autor: J. Salas-García et al.
Fecha: 2025-11-22
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple


class FuzzyWeightOptimizer:
    """
    Optimizador de pesos usando lógica difusa.

    Define tres regímenes operacionales:
    - CORTO: Tiempo corto (60-70 min) → Priorizar conversión
    - MEDIO: Tiempo medio (70-100 min) → Balance conversión-costo
    - LARGO: Tiempo largo (100-120 min) → Priorizar ahorro energético
    """

    def __init__(self, time_range: Tuple[float, float] = (60, 120)):
        """
        Inicializa sistema difuso.

        Args:
            time_range: Rango (min, max) de tiempos en minutos
        """
        self.t_min, self.t_max = time_range

        # Parámetros de funciones de membresía (triangulares/trapezoidales)
        # CORTO: tiempo 60-80 min
        self.short_params = {
            'start': 60,
            'peak1': 60,
            'peak2': 70,
            'end': 85
        }

        # MEDIO: tiempo 70-110 min
        self.medium_params = {
            'start': 70,
            'peak1': 85,
            'peak2': 100,
            'end': 110
        }

        # LARGO: tiempo 100-120 min
        self.long_params = {
            'start': 95,
            'peak1': 105,
            'peak2': 120,
            'end': 120
        }

    def membership_short(self, t: float) -> float:
        """
        Función de membresía para régimen CORTO.
        Trapezoidal: alta membresía para t < 70, decae hasta 85.
        """
        p = self.short_params
        if t <= p['peak1']:
            return 1.0
        elif t <= p['peak2']:
            return 1.0
        elif t <= p['end']:
            return (p['end'] - t) / (p['end'] - p['peak2'])
        else:
            return 0.0

    def membership_medium(self, t: float) -> float:
        """
        Función de membresía para régimen MEDIO.
        Trapezoidal: crece desde 70, máximo 85-100, decae hasta 110.
        """
        p = self.medium_params
        if t <= p['start']:
            return 0.0
        elif t <= p['peak1']:
            return (t - p['start']) / (p['peak1'] - p['start'])
        elif t <= p['peak2']:
            return 1.0
        elif t <= p['end']:
            return (p['end'] - t) / (p['end'] - p['peak2'])
        else:
            return 0.0

    def membership_long(self, t: float) -> float:
        """
        Función de membresía para régimen LARGO.
        Trapezoidal: crece desde 95, máximo desde 105.
        """
        p = self.long_params
        if t <= p['start']:
            return 0.0
        elif t <= p['peak1']:
            return (t - p['start']) / (p['peak1'] - p['start'])
        elif t <= p['peak2']:
            return 1.0
        else:
            return 1.0

    def get_weights(self, t: float) -> Dict[str, float]:
        """
        Calcula pesos de penalización usando lógica difusa.

        Args:
            t: Tiempo de reacción (min)

        Returns:
            Dict con energy_weight y catalyst_weight
        """
        # Calcular grados de membresía
        mu_short = self.membership_short(t)
        mu_medium = self.membership_medium(t)
        mu_long = self.membership_long(t)

        # Normalizar (suma = 1)
        total = mu_short + mu_medium + mu_long
        if total > 0:
            mu_short /= total
            mu_medium /= total
            mu_long /= total

        # Reglas difusas para energy_weight:
        # SI tiempo es CORTO ENTONCES energy_weight = BAJO (0.0)
        # SI tiempo es MEDIO ENTONCES energy_weight = MODERADO (0.8)
        # SI tiempo es LARGO ENTONCES energy_weight = ALTO (1.5)

        energy_low = 0.0
        energy_medium = 0.8
        energy_high = 1.5

        energy_weight = (mu_short * energy_low +
                        mu_medium * energy_medium +
                        mu_long * energy_high)

        # Reglas difusas para catalyst_weight:
        # SI tiempo es CORTO ENTONCES catalyst_weight = BAJO (0.0)
        # SI tiempo es MEDIO ENTONCES catalyst_weight = MODERADO (0.3)
        # SI tiempo es LARGO ENTONCES catalyst_weight = ALTO (0.6)

        catalyst_low = 0.0
        catalyst_medium = 0.3
        catalyst_high = 0.6

        catalyst_weight = (mu_short * catalyst_low +
                          mu_medium * catalyst_medium +
                          mu_long * catalyst_high)

        return {
            'energy_weight': energy_weight,
            'catalyst_weight': catalyst_weight,
            'memberships': {
                'short': mu_short,
                'medium': mu_medium,
                'long': mu_long
            }
        }

    def plot_membership_functions(self, filename='fuzzy_memberships.png'):
        """Grafica funciones de membresía."""
        t_values = np.linspace(60, 120, 300)

        mu_short = [self.membership_short(t) for t in t_values]
        mu_medium = [self.membership_medium(t) for t in t_values]
        mu_long = [self.membership_long(t) for t in t_values]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Funciones de membresía
        ax1.plot(t_values, mu_short, 'b-', linewidth=2, label='CORTO')
        ax1.plot(t_values, mu_medium, 'g-', linewidth=2, label='MEDIO')
        ax1.plot(t_values, mu_long, 'r-', linewidth=2, label='LARGO')
        ax1.fill_between(t_values, 0, mu_short, alpha=0.3, color='blue')
        ax1.fill_between(t_values, 0, mu_medium, alpha=0.3, color='green')
        ax1.fill_between(t_values, 0, mu_long, alpha=0.3, color='red')
        ax1.set_xlabel('Tiempo de reacción (min)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Grado de membresía μ(t)', fontsize=12, fontweight='bold')
        ax1.set_title('Funciones de Membresía - Regímenes Operacionales', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.05, 1.1])

        # Plot 2: Pesos resultantes
        weights_energy = []
        weights_catalyst = []
        for t in t_values:
            w = self.get_weights(t)
            weights_energy.append(w['energy_weight'])
            weights_catalyst.append(w['catalyst_weight'])

        ax2.plot(t_values, weights_energy, 'o-', linewidth=2.5, markersize=4,
                label='energy_weight', color='#E63946')
        ax2.plot(t_values, weights_catalyst, 's-', linewidth=2.5, markersize=4,
                label='catalyst_weight', color='#F18F01')
        ax2.set_xlabel('Tiempo de reacción (min)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Peso de penalización', fontsize=12, fontweight='bold')
        ax2.set_title('Pesos de Penalización (Salida del Sistema Difuso)', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"[OK] Grafica de logica difusa guardada en: {filename}")
        plt.close()

    def print_weight_table(self, times: list):
        """Imprime tabla de pesos para tiempos dados."""
        print("\n" + "="*80)
        print("TABLA DE PESOS CALCULADOS POR LOGICA DIFUSA")
        print("="*80)
        print(f"\n{'Tiempo':>8} | {'u_CORTO':>9} | {'u_MEDIO':>9} | {'u_LARGO':>9} | "
              f"{'E_weight':>9} | {'C_weight':>9}")
        print(f"{'(min)':>8} | {'':>9} | {'':>9} | {'':>9} | {'':>9} | {'':>9}")
        print("-"*80)

        for t in times:
            result = self.get_weights(t)
            mem = result['memberships']
            print(f"{t:>8.0f} | {mem['short']:>9.3f} | {mem['medium']:>9.3f} | "
                  f"{mem['long']:>9.3f} | {result['energy_weight']:>9.4f} | "
                  f"{result['catalyst_weight']:>9.4f}")
        print()


def main():
    """Función principal."""
    print("\n" + "="*80)
    print("SISTEMA DE LÓGICA DIFUSA PARA OPTIMIZACIÓN MULTI-OBJETIVO")
    print("="*80)
    print("\nObjetivo: Calcular pesos de penalización con transiciones suaves")
    print("Método: Lógica difusa con 3 regímenes (CORTO, MEDIO, LARGO)")
    print()

    # Crear sistema difuso
    fuzzy = FuzzyWeightOptimizer(time_range=(60, 120))

    # Evaluar para diferentes tiempos
    times = [60, 70, 75, 80, 90, 100, 105, 110, 120]

    # Imprimir tabla
    fuzzy.print_weight_table(times)

    # Generar gráficas
    fuzzy.plot_membership_functions('fuzzy_memberships.png')

    # Generar código para main.py
    print("="*80)
    print("CÓDIGO PARA USAR EN main.py:")
    print("="*80)
    print("""
# Importar sistema difuso
from fuzzy_weight_optimizer import FuzzyWeightOptimizer

# Crear sistema difuso (una vez, fuera del loop)
fuzzy_optimizer = FuzzyWeightOptimizer(time_range=(60, 120))

# Dentro del loop de optimización:
# Calcular pesos usando lógica difusa
fuzzy_result = fuzzy_optimizer.get_weights(t_reaction)
energy_weight = fuzzy_result['energy_weight']
catalyst_weight = fuzzy_result['catalyst_weight']

print(f"Pesos de optimización (lógica difusa):")
print(f"  Membresías: CORTO={fuzzy_result['memberships']['short']:.3f}, "
      f"MEDIO={fuzzy_result['memberships']['medium']:.3f}, "
      f"LARGO={fuzzy_result['memberships']['long']:.3f}")
print(f"  energy_weight = {energy_weight:.4f}")
print(f"  catalyst_weight = {catalyst_weight:.4f}")
    """)

    print("\n[OK] Sistema difuso configurado y listo para usar")
    print()


if __name__ == '__main__':
    main()
