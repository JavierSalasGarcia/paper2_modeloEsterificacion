# Módulo de Optimización

Este directorio contiene módulos para optimización de condiciones operacionales en transesterificación.

## Archivos Principales (USADOS en runtime)

### `fuzzy_weight_optimizer.py` ✅ **EN USO**
- **Descripción**: Sistema de lógica difusa para optimización multi-objetivo
- **Usado por**: `main.py` (línea 47 import, línea 510 usage)
- **Propósito**: Calcula pesos de penalización con transiciones suaves entre regímenes operacionales
- **Regímenes definidos**:
  - CORTO (60-70 min): Prioriza conversión
  - MEDIO (70-100 min): Balance conversión-costo
  - LARGO (100-120 min): Prioriza ahorro energético
- **Uso**:
  ```python
  from src.optimization.fuzzy_weight_optimizer import FuzzyWeightOptimizer

  fuzzy = FuzzyWeightOptimizer(time_range=(60, 120))
  result = fuzzy.get_weights(t_reaction=90)
  energy_weight = result['energy_weight']
  catalyst_weight = result['catalyst_weight']
  ```

### `optimizer.py` ✅ **EN USO**
- **Descripción**: Optimizador operacional usando algoritmos de evolución diferencial
- **Usado por**: `main.py` (import y uso en optimize_mode)
- **Propósito**: Encuentra condiciones óptimas (T, RPM, catalizador) que maximizan conversión

## Utilidades (NO usadas en runtime de main.py)

### `utils/calibrate_weights.py` ⚠️ **DESARROLLO/ANÁLISIS**
- **Descripción**: Script standalone para calibrar funciones de pesos usando Machine Learning
- **NO importado por main.py**
- **Propósito**: Herramienta de desarrollo para encontrar funciones de pesos óptimas mediante minimización de discontinuidades
- **Uso**: Ejecutar standalone cuando se necesite re-calibrar pesos
  ```bash
  python src/optimization/utils/calibrate_weights.py
  ```
- **Salidas**:
  - `weight_calibration_results.png` - Gráficas de calibración
  - `calibrated_weights.json` - Parámetros calibrados

### `utils/bifurcation_sensitivity.py` ⚠️ **ANÁLISIS AVANZADO**
- **Descripción**: Análisis de sensibilidad del punto de bifurcación entre regímenes
- **NO importado por main.py**
- **Propósito**: Investigar cómo diferentes parámetros afectan la transición entre regímenes RÁPIDO y ECONÓMICO
- **Dependencias**: Importa `fuzzy_weight_optimizer`
- **Uso**: Ejecutar standalone para análisis de sensibilidad
  ```bash
  python src/optimization/utils/bifurcation_sensitivity.py
  ```
- **Salidas**:
  - `exp1_fuzzy_peak2.json` - Sensibilidad a peak2
  - `exp2_penalty_weights.json` - Sensibilidad a pesos
  - `exp3_rpm_bounds.json` - Sensibilidad a límites RPM
  - `sensitivity_summary.png` - Resumen visual
  - `SENSITIVITY_REPORT.md` - Reporte markdown

## Flujo de Trabajo Recomendado

1. **Uso normal**: Importar solo `FuzzyWeightOptimizer` y `OperationalOptimizer` desde main.py
2. **Desarrollo/calibración**: Ejecutar `utils/calibrate_weights.py` cuando se necesiten nuevos pesos
3. **Análisis avanzado**: Ejecutar `utils/bifurcation_sensitivity.py` para estudiar transiciones

## Notas Importantes

- ✅ Los archivos marcados con ✅ **deben mantenerse** - son esenciales para funcionamiento
- ⚠️ Los archivos marcados con ⚠️ **pueden eliminarse** si no se planea desarrollo/análisis futuro
- Los archivos en `utils/` son scripts de análisis standalone, no módulos importables por main.py
- Si eliminas archivos de `utils/`, el sistema principal seguirá funcionando normalmente

## Limpieza de Código

Para limpiar el código sin afectar funcionalidad:
```bash
# Opción 1: Eliminar archivos de análisis (si no se necesitan)
rm -rf src/optimization/utils/

# Opción 2: Mantenerlos para referencia futura (recomendado)
# No hacer nada - están organizados y documentados
```

---
**Última actualización**: 2025-11-22
**Autor**: J. Salas-García et al.
