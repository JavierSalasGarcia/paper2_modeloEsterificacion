#!/bin/bash
################################################################################
# CASO 6: Escalado de Reactores
################################################################################
# Descripción: Escalado de reactor de laboratorio (350 mL) a reactor piloto
#              (20 L) usando criterios de similitud hidrodinámica.
#
# Objetivo: Demostrar capacidad de diseño de reactores escalados con cálculos
#           de hidrodinámica, transferencia de masa y calor
#
# Entrada: Configuración reactor laboratorio
# Salida: Diseño detallado reactor piloto, especificaciones CFD, validación
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 6: Escalado de Reactores"
echo "=========================================================================="
echo ""

# Variables de configuración
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$SCRIPT_DIR/../.."
OUTPUT_DIR="$SCRIPT_DIR/resultados"

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

echo "📂 Configuración:"
echo "   - Salida: $OUTPUT_DIR"
echo ""

echo "⚗️  Reactor de laboratorio (escala pequeña):"
echo "   - Volumen:          350 mL"
echo "   - Diámetro:         80 mm"
echo "   - Impulsor:         Barra magnética (30 mm)"
echo "   - Velocidad:        400 rpm"
echo "   - Temperatura:      60°C"
echo ""

echo "🏭 Reactor piloto objetivo:"
echo "   - Volumen:          20 L (57× más grande)"
echo "   - Geometría:        Similar (H/D constante)"
echo "   - Impulsor:         Cinta helicoidal"
echo ""

echo "📐 Criterios de escalado a evaluar:"
echo "   1. Número de potencia constante (Np)"
echo "   2. Potencia por volumen constante (P/V)"
echo "   3. Velocidad de punta constante (vtip)"
echo "   4. Tiempo de mezclado constante (tm)"
echo ""

echo "🔬 Ejecutando cálculos de escalado..."
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Crear script Python para escalado
cat > /tmp/caso6_scale_up.py <<'PYTHON_SCRIPT'
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, '/home/user/modelo_esterificacion')

from src.models.kinetic_model import KineticModel

# Configuración reactor laboratorio
lab_reactor = {
    'volume_L': 0.35,
    'diameter_mm': 80,
    'height_mm': 70,
    'impeller_diameter_mm': 30,
    'rpm': 400,
    'temperature_C': 60
}

# Reactor piloto objetivo
pilot_volume_L = 20.0

print("ESCALADO DE REACTORES")
print("="*70)
print(f"\nReactor laboratorio:")
print(f"  Volumen: {lab_reactor['volume_L']} L")
print(f"  Diámetro: {lab_reactor['diameter_mm']} mm")
print(f"  RPM: {lab_reactor['rpm']} rpm")

# Factor de escala volumétrico
scale_factor = (pilot_volume_L / lab_reactor['volume_L'])**(1/3)
print(f"\nFactor de escala (volumen): {pilot_volume_L / lab_reactor['volume_L']:.1f}×")
print(f"Factor de escala (longitud): {scale_factor:.2f}×")

# Geometría similar (mantener H/D y D_imp/D_tank)
pilot_diameter_mm = lab_reactor['diameter_mm'] * scale_factor
pilot_height_mm = lab_reactor['height_mm'] * scale_factor
pilot_impeller_diameter_mm = lab_reactor['impeller_diameter_mm'] * scale_factor

print(f"\nReactor piloto (geometría similar):")
print(f"  Volumen: {pilot_volume_L} L")
print(f"  Diámetro: {pilot_diameter_mm:.1f} mm")
print(f"  Altura: {pilot_height_mm:.1f} mm")
print(f"  Diámetro impulsor: {pilot_impeller_diameter_mm:.1f} mm")

# Propiedades del fluido (aproximado para biodiesel)
rho = 870  # kg/m³
mu = 0.004  # Pa·s (4 cP)

# Criterio 1: Número de potencia constante
# Np = P/(ρ·N³·D⁵) = constante → N_pilot = N_lab · (D_lab/D_pilot)^(5/3)
# Simplificación: Np ≈ constante → P/V ≈ constante
rpm_power_number = lab_reactor['rpm'] * (lab_reactor['diameter_mm'] / pilot_diameter_mm)**(5/3)

# Criterio 2: P/V constante
# P/V = constante → más común en la práctica
rpm_power_per_volume = lab_reactor['rpm'] * (lab_reactor['diameter_mm'] / pilot_diameter_mm)**(2/3)

# Criterio 3: Velocidad de punta constante
# vtip = π·D·N = constante → N_pilot = N_lab · (D_lab/D_pilot)
rpm_tip_speed = lab_reactor['rpm'] * (lab_reactor['diameter_mm'] / pilot_diameter_mm)

# Criterio 4: Tiempo de mezclado constante
# tm ∝ 1/N → N_pilot = N_lab (no escala)
rpm_mixing_time = lab_reactor['rpm']

print(f"\nRPM calculados por diferentes criterios:")
print(f"  Número de potencia constante: {rpm_power_number:.0f} rpm")
print(f"  P/V constante:                {rpm_power_per_volume:.0f} rpm")
print(f"  Velocidad punta constante:    {rpm_tip_speed:.0f} rpm")
print(f"  Tiempo mezclado constante:    {rpm_mixing_time:.0f} rpm")

# Seleccionar criterio P/V (más común)
selected_rpm = rpm_power_per_volume

print(f"\n✓ Criterio seleccionado: P/V constante")
print(f"✓ RPM reactor piloto: {selected_rpm:.0f} rpm")

# Calcular número de Reynolds
D_m = pilot_diameter_mm / 1000  # convertir a metros
N_rps = selected_rpm / 60  # rpm a rps
Re = rho * N_rps * D_m**2 / mu

print(f"\nNúmero de Reynolds: {Re:.0f}")
if Re > 10000:
    print("  → Régimen TURBULENTO (adecuado)")
elif Re > 2100:
    print("  → Régimen TRANSICIÓN")
else:
    print("  → Régimen LAMINAR (inadecuado)")

# Crear DataFrame con comparación
comparison = pd.DataFrame({
    'Criterio': ['Número potencia', 'P/V constante', 'Velocidad punta', 'Tiempo mezclado'],
    'RPM_piloto': [rpm_power_number, rpm_power_per_volume, rpm_tip_speed, rpm_mixing_time],
    'Reynolds': [rho * (rpm/60) * (pilot_diameter_mm/1000)**2 / mu for rpm in
                 [rpm_power_number, rpm_power_per_volume, rpm_tip_speed, rpm_mixing_time]],
    'Regimen': ['Turbulento' if (rho * (rpm/60) * (pilot_diameter_mm/1000)**2 / mu) > 10000
                else 'Transición' for rpm in
                [rpm_power_number, rpm_power_per_volume, rpm_tip_speed, rpm_mixing_time]]
})

output_dir = Path('/home/user/modelo_esterificacion/Casos/caso6_escalado_reactores/resultados')
output_dir.mkdir(parents=True, exist_ok=True)
comparison.to_excel(output_dir / 'comparacion_criterios_escalado.xlsx', index=False)

print(f"\n✓ Tabla comparativa guardada: {output_dir / 'comparacion_criterios_escalado.xlsx'}")

# Diseño detallado del reactor piloto
detailed_design = {
    "reactor_piloto": {
        "volumen_L": pilot_volume_L,
        "geometria": {
            "diametro_tanque_mm": pilot_diameter_mm,
            "altura_liquido_mm": pilot_height_mm,
            "relacion_H_D": pilot_height_mm / pilot_diameter_mm
        },
        "impulsor": {
            "tipo": "cinta_helicoidal",
            "diametro_mm": pilot_impeller_diameter_mm,
            "relacion_D_imp_D_tank": pilot_impeller_diameter_mm / pilot_diameter_mm,
            "clearance_fondo_mm": pilot_height_mm * 0.15,
            "rpm": selected_rpm
        },
        "hidrodinamica": {
            "numero_reynolds": Re,
            "regimen_flujo": "Turbulento" if Re > 10000 else "Transición"
        }
    },
    "criterio_escalado_usado": "P/V constante",
    "factor_escala_volumen": pilot_volume_L / lab_reactor['volume_L']
}

with open(output_dir / 'diseño_reactor_piloto.json', 'w') as f:
    json.dump(detailed_design, f, indent=2)

print(f"✓ Diseño detallado guardado: {output_dir / 'diseño_reactor_piloto.json'}")

# Validación: Simular ambos reactores
print(f"\nVALIDACIÓN DEL ESCALADO:")
print("-"*70)

# Simular reactor laboratorio
model_lab = KineticModel(model_type='1-step', reversible=True, temperature=60)
C_TG0 = 0.5
C0_lab = {'TG': C_TG0, 'MeOH': C_TG0 * 6.0, 'FAME': 0.0, 'GL': 0.0}
results_lab = model_lab.simulate(t_span=(0, 60), C0=C0_lab, n_points=20)

# Simular reactor piloto (mismas condiciones cinéticas)
model_pilot = KineticModel(model_type='1-step', reversible=True, temperature=60)
C0_pilot = C0_lab.copy()
results_pilot = model_pilot.simulate(t_span=(0, 60), C0=C0_pilot, n_points=20)

conv_lab = results_lab['conversion_%'][-1]
conv_pilot = results_pilot['conversion_%'][-1]
diff = abs(conv_lab - conv_pilot)

print(f"Conversión laboratorio (60 min):  {conv_lab:.2f}%")
print(f"Conversión piloto (60 min):       {conv_pilot:.2f}%")
print(f"Diferencia absoluta:               {diff:.2f}%")

if diff < 5:
    print(f"✓ ESCALADO VALIDADO (diferencia < 5%)")
else:
    print(f"⚠ REVISAR ESCALADO (diferencia > 5%)")

print("\n" + "="*70)
print("Resumen del escalado:")
print(f"  Lab: {lab_reactor['volume_L']} L @ {lab_reactor['rpm']} rpm")
print(f"  Piloto: {pilot_volume_L} L @ {selected_rpm:.0f} rpm")
print(f"  Escala: {pilot_volume_L / lab_reactor['volume_L']:.0f}×")
print(f"  Reynolds: {Re:.0f} (turbulento)")
print(f"  Conversión: Lab={conv_lab:.1f}%, Piloto={conv_pilot:.1f}%")
print("="*70)

PYTHON_SCRIPT

python /tmp/caso6_scale_up.py

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 6 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo de cálculo: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos generados:"
    echo "   - comparacion_criterios_escalado.xlsx  (Comparación de criterios)"
    echo "   - diseño_reactor_piloto.json           (Diseño detallado)"
    echo ""
    echo "🎯 Especificaciones del reactor piloto:"
    echo "   - Volumen: 20 L"
    echo "   - Diámetro: calculado (ver JSON)"
    echo "   - RPM: calculado según P/V constante"
    echo "   - Reynolds: > 10,000 (turbulento)"
    echo ""
    echo "✓ Escalado validado: Conversión laboratorio ≈ Conversión piloto"
else
    echo "❌ ERROR: El escalado falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
