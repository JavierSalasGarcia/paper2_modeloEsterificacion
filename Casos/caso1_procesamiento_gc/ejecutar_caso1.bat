@echo off
REM ##############################################################################
REM CASO 1: Procesamiento Automatizado de Datos GC-FID
REM ##############################################################################
REM Descripción: Procesa datos de cromatografía de gases (GC-FID) para calcular
REM              concentraciones, conversión y estadísticas.
REM
REM Objetivo: Demostrar la facilidad de uso del sistema vs métodos manuales
REM
REM Entrada: CSV con áreas de picos del cromatógrafo
REM Salida: Concentraciones, conversión, gráficas y estadísticas
REM
REM Autores: J. Salas-García et al.
REM Fecha: 2025-11-22
REM ##############################################################################

echo ==========================================================================
echo CASO 1: Procesamiento Automatizado de Datos GC-FID
echo ==========================================================================
echo.

REM Variables de configuración
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..\
set INPUT_FILE=%SCRIPT_DIR%datos\experimento_60C.csv
set OUTPUT_DIR=%SCRIPT_DIR%resultados

REM Verificar que existe el archivo de entrada
if not exist "%INPUT_FILE%" (
    echo ❌ ERROR: No se encuentra el archivo de entrada: %INPUT_FILE%
    exit /b 1
)

REM Crear directorio de salida si no existe
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 📂 Configuración:
echo    - Entrada:  %INPUT_FILE%
echo    - Salida:   %OUTPUT_DIR%
echo.

echo 🔬 Ejecutando procesamiento GC-FID...
echo.

REM Registrar tiempo de inicio
set START_TIME=%TIME%

REM Ejecutar main.py con modo process_gc
cd /d "%ROOT_DIR%"
python main.py --mode process_gc --input "%INPUT_FILE%" --output "%OUTPUT_DIR%" --c-tg0 0.5

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Registrar tiempo de finalización
set END_TIME=%TIME%

echo.
echo ==========================================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ CASO 1 COMPLETADO EXITOSAMENTE
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Fin:    %END_TIME%
    echo.
    echo 📊 Resultados generados en: %OUTPUT_DIR%
    echo.
    echo Archivos esperados:
    echo    - processed_gc_data.csv       (Datos procesados^)
    echo    - concentrations.png          (Gráfica de concentraciones^)
    echo    - conversion_curve.png        (Curva de conversión^)
    echo    - statistics_summary.json     (Estadísticas^)
) else (
    echo ❌ ERROR: El procesamiento falló con código %EXIT_CODE%
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Error:  %END_TIME%
)
echo ==========================================================================
echo.

REM Retornar al directorio del caso
cd /d "%SCRIPT_DIR%"

exit /b %EXIT_CODE%
