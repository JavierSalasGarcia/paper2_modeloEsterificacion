#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo 3: Optimización de Condiciones Operacionales
=====================================================

Este script muestra cómo optimizar temperatura, agitación (RPM) y
concentración de catalizador para maximizar la conversión.

Autor: Sistema de Modelado de Esterificación
Fecha: 2025-01-15
"""

import sys
from pathlib import Path
import json

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.kinetic_model import KineticModel
from optimization.optimizer import OperationalOptimizer
import matplotlib.pyplot as plt

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Parámetros cinéticos ajustados (modificar con tus valores)
PARAMETROS_CINETICOS = {
    'A_forward': 2.98e10,  # min⁻¹
    'Ea_forward': 51.9,    # kJ/mol
    'A_reverse': 1.5e8,    # min⁻¹
    'Ea_reverse': 45.0     # kJ/mol
}

# Condiciones iniciales
C0 = {
    'TG': 0.5,      # mol/L
    'MeOH': 4.5,    # mol/L (relación molar 9:1)
    'FAME': 0.0,
    'GL': 0.0
}

# Tiempo de reacción
TIEMPO_REACCION = 120  # minutos

# Límites de optimización
BOUNDS = {
    'temperature': (50.0, 80.0),      # °C
    'rpm': (200.0, 800.0),            # rpm
    'catalyst_%': (1.0, 5.0)          # % masa
}

# Directorio de salida
OUTPUT_DIR = 'results/optimization/'

# =============================================================================
# OPTIMIZACIÓN
# =============================================================================

def main():
    """Función principal"""

    print("="*80)
    print("OPTIMIZACIÓN DE CONDICIONES OPERACIONALES")
    print("="*80)

    # 1. Crear modelo cinético
    print(f"\n[1/4] Creando modelo cinético...")
    model = KineticModel(
        model_type='1-step',
        reversible=True
    )

    # Establecer parámetros ajustados
    model.set_parameters(PARAMETROS_CINETICOS)
    print(f"   ✓ Modelo configurado con parámetros ajustados")

    # 2. Crear optimizador
    print(f"\n[2/4] Configurando optimizador...")
    optimizer = OperationalOptimizer(
        model=model,
        objective_type='maximize_conversion'
    )

    # Establecer límites
    optimizer.set_bounds(BOUNDS)

    print(f"   ✓ Límites de optimización:")
    print(f"      Temperatura:  {BOUNDS['temperature'][0]:.1f} - {BOUNDS['temperature'][1]:.1f} °C")
    print(f"      Agitación:    {BOUNDS['rpm'][0]:.0f} - {BOUNDS['rpm'][1]:.0f} rpm")
    print(f"      Catalizador:  {BOUNDS['catalyst_%'][0]:.1f} - {BOUNDS['catalyst_%'][1]:.1f} %")

    # 3. Ejecutar optimización
    print(f"\n[3/4] Ejecutando optimización...")
    print(f"   Algoritmo: Differential Evolution")
    print(f"   Objetivo: Maximizar conversión de TG")
    print(f"   Esto puede tomar 1-5 minutos...")
    print(f"   {'─'*60}")

    resultado_optimo = optimizer.optimize(
        C0=C0,
        t_reaction=TIEMPO_REACCION,
        method='differential_evolution',
        maxiter=100,
        verbose=True
    )

    # 4. Mostrar resultados
    print(f"\n{'='*80}")
    print("RESULTADOS DE LA OPTIMIZACIÓN")
    print('='*80)

    print(f"\n🎯 CONDICIONES ÓPTIMAS:")
    print(f"   {'─'*60}")
    print(f"   Temperatura:     {resultado_optimo['temperature']:.2f} °C")
    print(f"   Agitación:       {resultado_optimo['rpm']:.0f} rpm")
    print(f"   Catalizador:     {resultado_optimo['catalyst_%']:.2f} %")
    print(f"   {'─'*60}")

    print(f"\n📈 CONVERSIÓN PREDICHA:")
    print(f"   {'─'*60}")
    print(f"   Conversión:      {resultado_optimo['conversion_%']:.2f} %")
    print(f"   Tiempo:          {TIEMPO_REACCION} min")
    print(f"   {'─'*60}")

    # 5. Análisis de sensibilidad
    print(f"\n[4/4] Generando análisis de sensibilidad...")

    sensitivity = optimizer.sensitivity_analysis(
        C0=C0,
        t_reaction=TIEMPO_REACCION,
        base_conditions=resultado_optimo
    )

    print(f"\n🔍 ANÁLISIS DE SENSIBILIDAD:")
    print(f"   {'─'*60}")
    for variable, sensibilidad in sensitivity.items():
        print(f"   {variable:15s}: {sensibilidad:+.4f}")
    print(f"   {'─'*60}")
    print(f"   (Valores positivos = aumento favorece la conversión)")

    # 6. Superficie de respuesta
    print(f"\n[5/5] Generando superficie de respuesta...")

    surface_data = optimizer.response_surface(
        C0=C0,
        t_reaction=TIEMPO_REACCION,
        var1='temperature',
        var2='catalyst_%',
        fixed_rpm=resultado_optimo['rpm'],
        resolution=20
    )

    # 7. Exportar resultados
    print(f"\n[6/6] Exportando resultados...")

    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Guardar resultados en JSON
    results_file = output_path / 'condiciones_optimas.json'
    with open(results_file, 'w') as f:
        json.dump({
            'condiciones_optimas': resultado_optimo,
            'analisis_sensibilidad': sensitivity,
            'parametros_cineticos_usados': PARAMETROS_CINETICOS,
            'tiempo_reaccion_min': TIEMPO_REACCION
        }, f, indent=2)

    print(f"   ✓ Resultados guardados en: {results_file}")

    # 8. Generar gráficas
    print(f"\n[7/7] Generando gráficas...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Gráfica 1: Superficie de respuesta
    from mpl_toolkits.mplot3d import Axes3D
    fig2 = plt.figure(figsize=(10, 8))
    ax = fig2.add_subplot(111, projection='3d')

    X = surface_data['var1_values']
    Y = surface_data['var2_values']
    Z = surface_data['conversion_surface']

    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    ax.set_xlabel('Temperatura (°C)')
    ax.set_ylabel('Catalizador (%)')
    ax.set_zlabel('Conversión (%)')
    ax.set_title('Superficie de Respuesta')
    fig2.colorbar(surf, shrink=0.5, aspect=5)

    # Marcar óptimo
    ax.scatter(
        [resultado_optimo['temperature']],
        [resultado_optimo['catalyst_%']],
        [resultado_optimo['conversion_%']],
        color='red', s=100, marker='*',
        label='Óptimo'
    )
    ax.legend()

    surface_file = output_path / 'superficie_respuesta.png'
    fig2.savefig(surface_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Superficie guardada en: {surface_file}")

    # Gráfica 2: Tornado plot (sensibilidad)
    variables = list(sensitivity.keys())
    valores = list(sensitivity.values())

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    colors = ['green' if v > 0 else 'red' for v in valores]
    ax3.barh(variables, valores, color=colors)
    ax3.axvline(x=0, color='black', linewidth=0.8)
    ax3.set_xlabel('Sensibilidad')
    ax3.set_title('Análisis de Sensibilidad (Tornado Plot)')
    ax3.grid(True, alpha=0.3)

    tornado_file = output_path / 'analisis_sensibilidad.png'
    fig3.savefig(tornado_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ Tornado plot guardado en: {tornado_file}")

    plt.show()

    print("\n" + "="*80)
    print("OPTIMIZACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print(f"\nArchivos generados:")
    print(f"  - Resultados: {results_file}")
    print(f"  - Superficie de respuesta: {surface_file}")
    print(f"  - Análisis de sensibilidad: {tornado_file}")
    print(f"\nCondiciones óptimas encontradas:")
    print(f"  T = {resultado_optimo['temperature']:.1f}°C, ")
    print(f"  RPM = {resultado_optimo['rpm']:.0f}, ")
    print(f"  Cat = {resultado_optimo['catalyst_%']:.2f}%")
    print(f"  → Conversión = {resultado_optimo['conversion_%']:.2f}%")
    print("="*80)

if __name__ == '__main__':
    main()
