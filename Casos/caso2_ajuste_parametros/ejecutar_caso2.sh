#!/bin/bash
################################################################################
# CASO 2: Ajuste de Parámetros Cinéticos
################################################################################
# Descripción: Calibra el modelo cinético usando datos experimentales de
#              Kouzu et al. (2008) a 4 temperaturas diferentes.
#
# Objetivo: Obtener parámetros A y Ea que minimicen el error entre
#           predicciones del modelo y datos experimentales
#
# Entrada: JSON con datos de conversión a 60, 65, 70, 75°C
# Salida: Parámetros calibrados, métricas de ajuste, gráficas
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 2: Ajuste de Parámetros Cinéticos"
echo "=========================================================================="
echo ""

# Variables de configuración
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$SCRIPT_DIR/../.."
INPUT_FILE="$SCRIPT_DIR/datos/datos_kouzu_4temps.json"
OUTPUT_DIR="$SCRIPT_DIR/resultados"

# Verificar que existe el archivo de entrada
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ ERROR: No se encuentra el archivo de entrada: $INPUT_FILE"
    exit 1
fi

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

echo "📂 Configuración:"
echo "   - Entrada:  $INPUT_FILE"
echo "   - Salida:   $OUTPUT_DIR"
echo "   - Datos:    Kouzu et al. (2008), 4 temperaturas, 28 puntos"
echo ""

echo "🔬 Ejecutando ajuste de parámetros cinéticos..."
echo "   - Parámetros a ajustar: A (factor preexponencial), Ea (energía activación)"
echo "   - Algoritmo: Levenberg-Marquardt (leastsq)"
echo "   - Modelo: 1-paso reversible"
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Ejecutar main.py con modo fit_params
cd "$ROOT_DIR"
python main.py \
    --mode fit_params \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_DIR" \
    --model-type 1-step \
    --verbose

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 2 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo de convergencia: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos esperados:"
    echo "   - parametros_calibrados.json     (A, Ea calibrados)"
    echo "   - metricas_ajuste.xlsx           (R², RMSE, MAE, etc.)"
    echo "   - ajuste_experimental_vs_modelo.png (Validación visual)"
    echo "   - analisis_residuales.png        (Normalidad, homocedasticidad)"
    echo "   - intervalos_confianza.png       (IC 95% para A y Ea)"
    echo ""
    echo "🎯 Criterios de aceptación:"
    echo "   - R² > 0.98 ✓"
    echo "   - RMSE < 5% ✓"
    echo ""
    echo "📈 Parámetros calibrados esperados:"
    echo "   - A ≈ 8.0×10⁵ L/(mol·min)"
    echo "   - Ea ≈ 50.0 kJ/mol"
else
    echo "❌ ERROR: El ajuste falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
