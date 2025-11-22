#!/bin/bash
################################################################################
# CASO 1: Procesamiento Automatizado de Datos GC-FID
################################################################################
# Descripción: Procesa datos de cromatografía de gases (GC-FID) para calcular
#              concentraciones, conversión y estadísticas.
#
# Objetivo: Demostrar la facilidad de uso del sistema vs métodos manuales
#
# Entrada: CSV con áreas de picos del cromatógrafo
# Salida: Concentraciones, conversión, gráficas y estadísticas
#
# Autores: J. Salas-García et al.
# Fecha: 2025-11-22
################################################################################

echo "=========================================================================="
echo "CASO 1: Procesamiento Automatizado de Datos GC-FID"
echo "=========================================================================="
echo ""

# Variables de configuración
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$SCRIPT_DIR/../.."
INPUT_FILE="$SCRIPT_DIR/datos/experimento_60C.csv"
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
echo ""

echo "🔬 Ejecutando procesamiento GC-FID..."
echo ""

# Registrar tiempo de inicio
START_TIME=$(date +%s)

# Ejecutar main.py con modo process_gc
cd "$ROOT_DIR"
python main.py \
    --mode process_gc \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_DIR" \
    --c-tg0 0.5

# Capturar código de salida
EXIT_CODE=$?

# Registrar tiempo de finalización
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CASO 1 COMPLETADO EXITOSAMENTE"
    echo "⏱️  Tiempo de ejecución: ${ELAPSED_TIME} segundos"
    echo ""
    echo "📊 Resultados generados en: $OUTPUT_DIR"
    echo ""
    echo "Archivos esperados:"
    echo "   - processed_gc_data.csv       (Datos procesados)"
    echo "   - concentrations.png          (Gráfica de concentraciones)"
    echo "   - conversion_curve.png        (Curva de conversión)"
    echo "   - statistics_summary.json     (Estadísticas)"
else
    echo "❌ ERROR: El procesamiento falló con código $EXIT_CODE"
    echo "⏱️  Tiempo antes del error: ${ELAPSED_TIME} segundos"
fi
echo "=========================================================================="
echo ""

# Retornar al directorio del caso
cd "$SCRIPT_DIR"

exit $EXIT_CODE
