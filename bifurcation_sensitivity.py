#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análisis de Sensibilidad del Punto de Bifurcación

Investiga cómo diferentes parámetros afectan la ubicación del punto
de transición (70-72 min) entre regímenes RÁPIDO y ECONÓMICO.

Autor: J. Salas-García et al.
Fecha: 2025-11-22
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from fuzzy_weight_optimizer import FuzzyWeightOptimizer
from src.optimization.optimizer import Optimizer
from src.model.esterification import EsterificationModel


class BifurcationSensitivityAnalyzer:
    """
    Analiza sensibilidad del punto de bifurcación a diferentes parámetros.
    """

    def __init__(self, base_dir='Casos/caso3_optimizacion/sensitivity'):
        """
        Inicializa analizador.

        Args:
            base_dir: Directorio para guardar resultados
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Cargar parámetros base del caso 3
        with open('Casos/caso3_optimizacion/parametros_caso3.json', 'r') as f:
            self.base_params = json.load(f)

        # Tiempos de evaluación centrados en la zona de bifurcación
        self.eval_times = [60, 65, 68, 69, 70, 71, 72, 73, 74, 75, 78, 80, 85, 90]

    def find_bifurcation_point(self, results):
        """
        Identifica el punto de bifurcación en resultados de optimización.

        Args:
            results: Lista de diccionarios con resultados de optimización

        Returns:
            Tupla (t_before, t_after, delta_rpm) donde ocurre el salto
        """
        for i in range(len(results) - 1):
            rpm_current = results[i]['rpm']
            rpm_next = results[i + 1]['rpm']

            # Detectar salto significativo en RPM (>100)
            delta_rpm = abs(rpm_next - rpm_current)
            if delta_rpm > 100:
                return (results[i]['t_reaction_min'],
                       results[i + 1]['t_reaction_min'],
                       delta_rpm)

        return (None, None, 0)

    def run_optimization_sweep(self, fuzzy_system, t_molar_ratio=6.0):
        """
        Ejecuta optimización para todos los tiempos de evaluación.

        Args:
            fuzzy_system: Sistema de lógica difusa configurado
            t_molar_ratio: Relación molar metanol:aceite

        Returns:
            Lista de resultados de optimización
        """
        results = []

        for t_reaction in self.eval_times:
            # Calcular pesos usando lógica difusa
            fuzzy_result = fuzzy_system.get_weights(t_reaction)
            energy_weight = fuzzy_result['energy_weight']
            catalyst_weight = fuzzy_result['catalyst_weight']

            # Crear modelo y optimizador
            model = EsterificationModel()
            model.load_parameters(self.base_params['parametros_cineticos'])

            optimizer = Optimizer(
                model=model,
                objective_type='multiobjective',
                method='differential_evolution'
            )

            # Ejecutar optimización
            result = optimizer.optimize(
                t_reaction=t_reaction,
                molar_ratio=t_molar_ratio,
                energy_weight=energy_weight,
                catalyst_weight=catalyst_weight,
                maxiter=100,
                seed=42
            )

            result['t_reaction_min'] = t_reaction
            result['energy_weight'] = energy_weight
            result['catalyst_weight'] = catalyst_weight
            result['memberships'] = fuzzy_result['memberships']

            results.append(result)

        return results

    # ========================================================================
    # EXPERIMENTO 1: Sensibilidad a 'peak2' de SHORT
    # ========================================================================

    def experiment_fuzzy_peak2(self, peak2_values=[65, 67.5, 70, 72.5, 75]):
        """
        Analiza efecto de variar 'peak2' del régimen SHORT.

        Args:
            peak2_values: Lista de valores de peak2 a evaluar

        Returns:
            Dict con resultados del experimento
        """
        print("\n" + "="*80)
        print("EXPERIMENTO 1: Sensibilidad a 'peak2' del régimen SHORT")
        print("="*80)
        print(f"\nEvaluando peak2 = {peak2_values}")
        print(f"Hipótesis: Mayor peak2 -> bifurcación más tardía\n")

        experiment_results = {
            'parameter': 'fuzzy_short_peak2',
            'values': peak2_values,
            'bifurcation_points': [],
            'all_results': {}
        }

        for peak2 in peak2_values:
            print(f"\n--- Ejecutando con peak2={peak2} min ---")

            # Crear sistema difuso modificado
            fuzzy = FuzzyWeightOptimizer(time_range=(60, 120))
            fuzzy.short_params['peak2'] = peak2
            fuzzy.short_params['end'] = peak2 + 15  # Mantener ancho consistente
            fuzzy.medium_params['start'] = peak2  # Ajustar inicio de MEDIUM

            # Ejecutar optimización
            results = self.run_optimization_sweep(fuzzy)

            # Encontrar punto de bifurcación
            t_before, t_after, delta_rpm = self.find_bifurcation_point(results)

            if t_before is not None:
                bifurcation_point = (t_before + t_after) / 2
                print(f"[OK] Bifurcación encontrada: {t_before} -> {t_after} min "
                      f"(punto medio = {bifurcation_point:.1f} min)")
            else:
                bifurcation_point = None
                print("[WARNING] No se detectó bifurcación clara")

            experiment_results['bifurcation_points'].append(bifurcation_point)
            experiment_results['all_results'][peak2] = results

        # Guardar resultados
        output_file = self.base_dir / 'exp1_fuzzy_peak2.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convertir resultados a formato serializable
            serializable = {
                'parameter': experiment_results['parameter'],
                'values': experiment_results['values'],
                'bifurcation_points': experiment_results['bifurcation_points']
            }
            json.dump(serializable, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Resultados guardados en: {output_file}")

        return experiment_results

    # ========================================================================
    # EXPERIMENTO 2: Sensibilidad a pesos de penalización
    # ========================================================================

    def experiment_penalty_weights(self, energy_medium_values=[0.4, 0.6, 0.8, 1.0, 1.2]):
        """
        Analiza efecto de variar 'energy_medium' en lógica difusa.

        Args:
            energy_medium_values: Lista de valores de energy_medium a evaluar

        Returns:
            Dict con resultados del experimento
        """
        print("\n" + "="*80)
        print("EXPERIMENTO 2: Sensibilidad a energy_medium")
        print("="*80)
        print(f"\nEvaluando energy_medium = {energy_medium_values}")
        print(f"Hipótesis: Mayor energy_medium -> bifurcación más temprana\n")

        experiment_results = {
            'parameter': 'energy_medium',
            'values': energy_medium_values,
            'bifurcation_points': [],
            'all_results': {}
        }

        for energy_med in energy_medium_values:
            print(f"\n--- Ejecutando con energy_medium={energy_med} ---")

            # Crear sistema difuso modificado
            fuzzy = FuzzyWeightOptimizer(time_range=(60, 120))

            # Modificar pesos (esto requiere modificar get_weights temporalmente)
            # Guardamos el método original
            original_get_weights = fuzzy.get_weights

            def modified_get_weights(t):
                result = original_get_weights(t)
                memberships = result['memberships']

                # Recalcular energy_weight con nuevo energy_medium
                energy_weight = (memberships['short'] * 0.0 +
                               memberships['medium'] * energy_med +
                               memberships['long'] * 1.5)

                result['energy_weight'] = energy_weight
                return result

            # Reemplazar temporalmente
            fuzzy.get_weights = modified_get_weights

            # Ejecutar optimización
            results = self.run_optimization_sweep(fuzzy)

            # Encontrar punto de bifurcación
            t_before, t_after, delta_rpm = self.find_bifurcation_point(results)

            if t_before is not None:
                bifurcation_point = (t_before + t_after) / 2
                print(f"[OK] Bifurcación encontrada: {t_before} -> {t_after} min "
                      f"(punto medio = {bifurcation_point:.1f} min)")
            else:
                bifurcation_point = None
                print("[WARNING] No se detectó bifurcación clara")

            experiment_results['bifurcation_points'].append(bifurcation_point)
            experiment_results['all_results'][energy_med] = results

        # Guardar resultados
        output_file = self.base_dir / 'exp2_penalty_weights.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            serializable = {
                'parameter': experiment_results['parameter'],
                'values': experiment_results['values'],
                'bifurcation_points': experiment_results['bifurcation_points']
            }
            json.dump(serializable, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Resultados guardados en: {output_file}")

        return experiment_results

    # ========================================================================
    # EXPERIMENTO 3: Sensibilidad a límites de RPM
    # ========================================================================

    def experiment_rpm_bounds(self, rpm_min_values=[100, 150, 200, 250, 300]):
        """
        Analiza efecto de variar límite inferior de RPM.

        Args:
            rpm_min_values: Lista de límites inferiores de RPM a evaluar

        Returns:
            Dict con resultados del experimento
        """
        print("\n" + "="*80)
        print("EXPERIMENTO 3: Sensibilidad a límite inferior de RPM")
        print("="*80)
        print(f"\nEvaluando RPM_min = {rpm_min_values}")
        print(f"Hipótesis: Mayor RPM_min -> bifurcación más tardía\n")

        experiment_results = {
            'parameter': 'rpm_min_bound',
            'values': rpm_min_values,
            'bifurcation_points': [],
            'all_results': {}
        }

        fuzzy = FuzzyWeightOptimizer(time_range=(60, 120))

        for rpm_min in rpm_min_values:
            print(f"\n--- Ejecutando con RPM_min={rpm_min} ---")

            results = []

            for t_reaction in self.eval_times:
                # Calcular pesos
                fuzzy_result = fuzzy.get_weights(t_reaction)
                energy_weight = fuzzy_result['energy_weight']
                catalyst_weight = fuzzy_result['catalyst_weight']

                # Crear modelo y optimizador
                model = EsterificationModel()
                model.load_parameters(self.base_params['parametros_cineticos'])

                optimizer = Optimizer(
                    model=model,
                    objective_type='multiobjective',
                    method='differential_evolution'
                )

                # Modificar bounds
                custom_bounds = {
                    'temperature': (50.0, 65.0),
                    'rpm': (rpm_min, 731.0),
                    'catalyst_%': (0.5, 2.0)
                }

                # Ejecutar optimización con bounds modificados
                result = optimizer.optimize(
                    t_reaction=t_reaction,
                    molar_ratio=6.0,
                    energy_weight=energy_weight,
                    catalyst_weight=catalyst_weight,
                    bounds=custom_bounds,
                    maxiter=100,
                    seed=42
                )

                result['t_reaction_min'] = t_reaction
                result['energy_weight'] = energy_weight
                result['catalyst_weight'] = catalyst_weight

                results.append(result)

            # Encontrar punto de bifurcación
            t_before, t_after, delta_rpm = self.find_bifurcation_point(results)

            if t_before is not None:
                bifurcation_point = (t_before + t_after) / 2
                print(f"[OK] Bifurcación encontrada: {t_before} -> {t_after} min "
                      f"(punto medio = {bifurcation_point:.1f} min)")
            else:
                bifurcation_point = None
                print("[WARNING] No se detectó bifurcación clara")

            experiment_results['bifurcation_points'].append(bifurcation_point)
            experiment_results['all_results'][rpm_min] = results

        # Guardar resultados
        output_file = self.base_dir / 'exp3_rpm_bounds.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            serializable = {
                'parameter': experiment_results['parameter'],
                'values': experiment_results['values'],
                'bifurcation_points': experiment_results['bifurcation_points']
            }
            json.dump(serializable, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Resultados guardados en: {output_file}")

        return experiment_results

    # ========================================================================
    # Visualización
    # ========================================================================

    def plot_sensitivity_summary(self, experiments):
        """
        Crea gráfica resumen de todos los experimentos.

        Args:
            experiments: Lista de diccionarios con resultados de experimentos
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        for idx, exp in enumerate(experiments):
            ax = axes[idx]

            param_values = exp['values']
            bifurcation_points = exp['bifurcation_points']

            # Filtrar valores None
            valid_data = [(p, b) for p, b in zip(param_values, bifurcation_points) if b is not None]
            if valid_data:
                params, points = zip(*valid_data)

                ax.plot(params, points, 'o-', linewidth=2.5, markersize=10,
                       color='#E63946', markerfacecolor='white', markeredgewidth=2)
                ax.axhline(y=71, color='gray', linestyle='--', linewidth=1.5,
                          alpha=0.7, label='Bifurcación base (71 min)')

                ax.set_xlabel(exp['parameter'], fontsize=12, fontweight='bold')
                ax.set_ylabel('Punto de bifurcación (min)', fontsize=12, fontweight='bold')
                ax.set_title(f"Sensibilidad a {exp['parameter']}", fontsize=13, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=10)

        plt.tight_layout()
        output_file = self.base_dir / 'sensitivity_summary.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n[OK] Gráfica resumen guardada en: {output_file}")
        plt.close()

    def generate_report(self, experiments):
        """
        Genera reporte markdown con resultados de sensibilidad.

        Args:
            experiments: Lista de diccionarios con resultados de experimentos
        """
        report = []
        report.append("# Análisis de Sensibilidad del Punto de Bifurcación")
        report.append("\n**Fecha**: 2025-11-22\n")
        report.append("---\n")

        report.append("## Resumen de Experimentos\n")

        for idx, exp in enumerate(experiments, 1):
            report.append(f"\n### Experimento {idx}: {exp['parameter']}\n")
            report.append(f"\n**Valores evaluados**: {exp['values']}\n")
            report.append(f"\n**Puntos de bifurcación encontrados**:\n")

            report.append("\n| Parámetro | Bifurcación (min) | Desplazamiento (min) |")
            report.append("\n|-----------|-------------------|----------------------|")

            base_bifurcation = 71.0  # Punto de referencia

            for param_val, bif_point in zip(exp['values'], exp['bifurcation_points']):
                if bif_point is not None:
                    displacement = bif_point - base_bifurcation
                    sign = '+' if displacement > 0 else ''
                    report.append(f"\n| {param_val} | {bif_point:.1f} | {sign}{displacement:.1f} |")
                else:
                    report.append(f"\n| {param_val} | N/A | N/A |")

            report.append("\n")

        report.append("\n---\n")
        report.append("\n## Conclusiones\n")
        report.append("\nVer gráficas en `sensitivity_summary.png` para interpretación visual.\n")

        output_file = self.base_dir / 'SENSITIVITY_REPORT.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(report))

        print(f"[OK] Reporte generado en: {output_file}")


def main():
    """Función principal."""
    print("\n" + "="*80)
    print("ANÁLISIS DE SENSIBILIDAD DEL PUNTO DE BIFURCACIÓN")
    print("="*80)
    print("\nObjetivo: Investigar cómo manipular la frontera entre regímenes RÁPIDO y ECONÓMICO")
    print("Método: Variar parámetros y medir desplazamiento del punto 70-72 min\n")

    analyzer = BifurcationSensitivityAnalyzer()

    # Ejecutar experimentos
    print("\n[INFO] Iniciando experimentos de sensibilidad...")
    print("[INFO] Esto puede tomar varios minutos (3-5 min por experimento)\n")

    experiments = []

    # Experimento 1: peak2 del régimen SHORT
    exp1 = analyzer.experiment_fuzzy_peak2(peak2_values=[65, 67.5, 70, 72.5, 75])
    experiments.append(exp1)

    # Experimento 2: energy_medium
    exp2 = analyzer.experiment_penalty_weights(energy_medium_values=[0.4, 0.6, 0.8, 1.0, 1.2])
    experiments.append(exp2)

    # Experimento 3: RPM_min
    exp3 = analyzer.experiment_rpm_bounds(rpm_min_values=[100, 150, 200, 250, 300])
    experiments.append(exp3)

    # Generar visualización y reporte
    print("\n" + "="*80)
    print("GENERANDO REPORTE FINAL")
    print("="*80)

    analyzer.plot_sensitivity_summary(experiments)
    analyzer.generate_report(experiments)

    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)
    print("\nResultados disponibles en: Casos/caso3_optimizacion/sensitivity/")
    print("  - exp1_fuzzy_peak2.json")
    print("  - exp2_penalty_weights.json")
    print("  - exp3_rpm_bounds.json")
    print("  - sensitivity_summary.png")
    print("  - SENSITIVITY_REPORT.md")
    print()


if __name__ == '__main__':
    main()
