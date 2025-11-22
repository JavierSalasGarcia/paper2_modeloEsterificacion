@echo off
REM ##############################################################################
REM CASO 2: Ajuste de Parámetros Cinéticos
REM ##############################################################################
REM Descripción: Calibra el modelo cinético usando datos experimentales de
REM              Kouzu et al. (2008) a 4 temperaturas diferentes.
REM
REM Objetivo: Obtener parámetros A y Ea que minimicen el error entre
REM           predicciones del modelo y datos experimentales
REM
REM Entrada: JSON con datos de conversión a 60, 65, 70, 75°C
REM Salida: Parámetros calibrados, métricas de ajuste, gráficas
REM
REM Autores: J. Salas-García et al.
REM Fecha: 2025-11-22
REM ##############################################################################

echo ==========================================================================
echo CASO 2: Ajuste de Parámetros Cinéticos
echo ==========================================================================
echo.

REM Variables de configuración
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..\
set INPUT_FILE=%SCRIPT_DIR%datos\datos_kouzu_4temps.json
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
echo    - Datos:    Kouzu et al. (2008^), 4 temperaturas, 28 puntos
echo.

echo 🔬 Ejecutando ajuste de parámetros cinéticos...
echo    - Parámetros a ajustar: A (factor preexponencial^), Ea (energía activación^)
echo    - Algoritmo: Levenberg-Marquardt (leastsq^)
echo    - Modelo: 1-paso reversible
echo.

REM Registrar tiempo de inicio
set START_TIME=%TIME%

REM Ejecutar main.py con modo fit_params
cd /d "%ROOT_DIR%"
python main.py --mode fit_params --input "%INPUT_FILE%" --output "%OUTPUT_DIR%" --model-type 1-step --verbose

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

REM Registrar tiempo de finalización
set END_TIME=%TIME%

echo.
echo ==========================================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ CASO 2 COMPLETADO EXITOSAMENTE
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Fin:    %END_TIME%
    echo.
    echo 📊 Resultados generados en: %OUTPUT_DIR%
    echo.
    echo Archivos esperados:
    echo    - parametros_calibrados.json     (A, Ea calibrados^)
    echo    - metricas_ajuste.xlsx           (R², RMSE, MAE, etc.^)
    echo    - ajuste_experimental_vs_modelo.png (Validación visual^)
    echo    - analisis_residuales.png        (Normalidad, homocedasticidad^)
    echo    - intervalos_confianza.png       (IC 95%% para A y Ea^)
    echo.
    echo 🎯 Criterios de aceptación:
    echo    - R² ^> 0.98 ✓
    echo    - RMSE ^< 5%% ✓
    echo.
    echo 📈 Parámetros calibrados esperados:
    echo    - A ≈ 8.0×10⁵ L/(mol·min^)
    echo    - Ea ≈ 50.0 kJ/mol
) else (
    echo ❌ ERROR: El ajuste falló con código %EXIT_CODE%
    echo ⏱️  Inicio: %START_TIME%
    echo ⏱️  Error:  %END_TIME%
)
echo ==========================================================================
echo.

REM Retornar al directorio del caso
cd /d "%SCRIPT_DIR%"

exit /b %EXIT_CODE%
