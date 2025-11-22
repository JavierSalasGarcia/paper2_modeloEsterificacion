# Casos de Uso del Sistema de Modelado de Biodiésel

Este directorio contiene **6 casos de uso** diseñados para demostrar las capacidades completas del sistema de modelado cinético de transesterificación. Estos casos fueron utilizados para el artículo científico publicado en la revista "Ideas en Ciencias de la Ingeniería".

## 📋 Resumen de Casos

| Caso | Nombre | Complejidad | Objetivo | Módulos evaluados |
|------|--------|-------------|----------|-------------------|
| 1 | Procesamiento GC-FID | Básico | Automatización de datos experimentales | `gc_processor` |
| 2 | Ajuste de Parámetros | Intermedio | Calibración con datos de literatura | `parameter_fitting` |
| 3 | Optimización Multi-objetivo | Avanzado | Búsqueda de condiciones óptimas | `optimizer` |
| 4 | Comparación de Modelos | Analítico | Evaluación 1-paso vs 3-pasos | `kinetic_model`, `comparison` |
| 5 | Análisis de Sensibilidad | Avanzado | Identificar variables críticas | Diseño factorial, ANOVA |
| 6 | Escalado de Reactores | Ingenieril | Diseño reactor piloto desde lab | Hidrodinámica, similitud |

---

## 🎯 Caso 1: Procesamiento Automatizado de Datos GC-FID

**Objetivo**: Demostrar la facilidad de procesamiento de datos cromatográficos vs métodos manuales (Excel/MATLAB).

**Entrada**:
- Archivo CSV de cromatógrafo con áreas de picos
- Factores de respuesta relativos
- Concentración inicial de triglicérido

**Salida**:
- Concentraciones de todas las especies
- Curvas de conversión vs tiempo
- Estadísticas descriptivas
- Detección de outliers

**Ejecución**:
```bash
cd caso1_procesamiento_gc/
bash ejecutar_caso1.sh
```

**Métricas de evaluación**:
- Tiempo de ejecución: < 5 segundos
- Pasos necesarios: 1 comando vs ~20 pasos manuales en Excel
- Reproducibilidad: 100%

---

## 🎯 Caso 2: Ajuste de Parámetros con Datos de Literatura

**Objetivo**: Calibrar el modelo cinético usando datos experimentales de Kouzu et al. (2008).

**Entrada**:
- Datos de conversión a 4 temperaturas (60, 65, 70, 75°C)
- Condiciones experimentales (relación molar, catalizador)
- Límites de búsqueda para A y Ea

**Salida**:
- Parámetros cinéticos calibrados (A, Ea)
- Métricas de bondad de ajuste (R², RMSE, MAE)
- Intervalos de confianza al 95%
- Gráficas de ajuste experimental vs modelo

**Ejecución**:
```bash
cd caso2_ajuste_parametros/
bash ejecutar_caso2.sh
```

**Métricas de evaluación**:
- R² obtenido: 0.9844
- RMSE: 3.85%
- Tiempo de convergencia: < 30 segundos

---

## 🎯 Caso 3: Optimización de Condiciones Operacionales

**Objetivo**: Encontrar condiciones óptimas de operación usando parámetros calibrados del Caso 2.

**Entrada**:
- Parámetros cinéticos calibrados
- Rangos de búsqueda (T: 50-80°C, RM: 3-15, Cat: 0.5-5%)
- Función objetivo: maximizar conversión

**Salida**:
- Condiciones óptimas (T, relación molar, catalizador, RPM)
- Conversión predicha en condiciones óptimas
- Superficies de respuesta 2D y 3D
- Análisis de sensibilidad

**Ejecución**:
```bash
cd caso3_optimizacion/
bash ejecutar_caso3.sh
```

**Métricas de evaluación**:
- Convergencia del algoritmo: < 100 iteraciones
- Conversión óptima alcanzada: > 99%
- Tiempo de optimización: < 2 minutos

---

## 🎯 Caso 4: Comparación de Modelos Mecanísticos

**Objetivo**: Evaluar diferencias entre modelo simplificado (1-paso) vs completo (3-pasos).

**Entrada**:
- Parámetros cinéticos calibrados
- Condiciones de reacción idénticas para ambos modelos

**Salida**:
- Predicciones de ambos modelos
- Diferencias en conversión final
- Perfiles de intermediarios (DG, MG) solo en modelo 3-pasos
- Tabla comparativa de tiempos de cómputo

**Ejecución**:
```bash
cd caso4_comparacion_modelos/
bash ejecutar_caso4.sh
```

**Métricas de evaluación**:
- Diferencia en conversión final: < 2%
- Tiempo modelo 1-paso: ~0.5 s
- Tiempo modelo 3-pasos: ~1.5 s
- Capacidad analítica: Modelo 3-pasos provee información de intermediarios

---

## 🎯 Caso 5: Análisis de Sensibilidad Global

**Objetivo**: Identificar qué variables operacionales (T, RM, catalizador, RPM) tienen mayor influencia en la conversión de TG mediante diseño factorial completo.

**Entrada**:
- Parámetros cinéticos calibrados (del Caso 2)
- Rangos de 4 variables con múltiples niveles (192 experimentos simulados)

**Salida**:
- Tabla ANOVA con contribución de cada variable
- Diagrama de Pareto identificando variables críticas
- Gráficas de efectos principales
- Análisis de interacciones de 2° orden

**Ejecución**:
```bash
cd caso5_analisis_sensibilidad/
bash ejecutar_caso5.sh
```

**Métricas de evaluación**:
- Tiempo total: < 5 minutos (192 simulaciones)
- Identificar top 3 variables críticas
- p-value < 0.05 para significancia estadística

---

## 🎯 Caso 6: Escalado de Reactores

**Objetivo**: Diseñar reactor piloto de 20 L a partir de reactor de laboratorio de 350 mL usando criterios de similitud hidrodinámica.

**Entrada**:
- Configuración reactor laboratorio (volumen, geometría, RPM)
- Volumen objetivo reactor piloto

**Salida**:
- Comparación de 4 criterios de escalado (Np, P/V, vtip, tm)
- Diseño detallado del reactor piloto (geometría, RPM, Reynolds)
- Validación mediante simulación (conversión lab vs piloto)
- Especificaciones para fabricación

**Ejecución**:
```bash
cd caso6_escalado_reactores/
bash ejecutar_caso6.sh
```

**Métricas de evaluación**:
- Tiempo de cálculo: < 10 segundos
- Número de Reynolds > 10,000 (turbulento)
- Diferencia en conversión lab vs piloto < 5%

---

## 📊 Workflow General de Ejecución

Para reproducir los resultados del artículo, ejecutar en orden:

```bash
# Paso 1: Procesar datos experimentales
cd /home/user/modelo_esterificacion/Casos/caso1_procesamiento_gc/
bash ejecutar_caso1.sh

# Paso 2: Calibrar parámetros con datos procesados
cd ../caso2_ajuste_parametros/
bash ejecutar_caso2.sh

# Paso 3: Optimizar condiciones con parámetros calibrados
cd ../caso3_optimizacion/
bash ejecutar_caso3.sh

# Paso 4: Comparar modelos
cd ../caso4_comparacion_modelos/
bash ejecutar_caso4.sh

# Paso 5: Análisis de sensibilidad
cd ../caso5_analisis_sensibilidad/
bash ejecutar_caso5.sh

# Paso 6: Escalado de reactores
cd ../caso6_escalado_reactores/
bash ejecutar_caso6.sh
```

---

## 📁 Estructura de Cada Caso

```
casoX_nombre/
├── datos/                    # Datos de entrada
│   └── archivo_entrada.csv/json
├── config_casoX.json         # Configuración del caso
├── ejecutar_casoX.sh         # Script de ejecución
├── resultados/               # Outputs generados
│   ├── figuras/
│   ├── tablas/
│   └── metricas.json
└── README_casoX.md           # Documentación específica
```

---

## 🔬 Validación Científica

Los resultados obtenidos fueron validados mediante:

1. **Validación primaria**: Datos de Kouzu et al. (2008) - Fuel 87:2798-2806
2. **Validación cruzada**: Comparación con Liu et al. (2008) y Granados et al. (2007)
3. **Consistencia interna**: Coherencia entre casos (Caso 2 → Caso 3)

---

## 📖 Referencia al Artículo

**Artículo asociado**:
- Salas-García, J., Moran Gonzalez, M., Durán García, M.D., Romero Romero, R., Natividad Rangel, R. (2026). "Sistema Open-Source Especializado para Modelado Cinético de Transesterificación: Una Alternativa Accesible al Software Comercial". *Ideas en Ciencias de la Ingeniería*, Vol. 4, No. 1.

**Artículo de prácticas educativas** (referencia):
- Salas-García, J. et al. (2025). "Sistema Integrado de Modelado de Esterificación: Prácticas Educativas Progresivas". *Informaticae Abstracta*, Vol. 3, No. 1.

---

## 👥 Autores

**Facultad de Ingeniería, UAEMEX:**
- J. Salas-García (proyectos@javiersalasg.com)
- M. Moran Gonzalez (miguel@poilower.com)
- M.D. Durán García (mddurang@uaemex.mx)

**CCIQS UAEM-UNAM:**
- R. Romero Romero (rromeror@uaemex.mx)
- R. Natividad Rangel (rnatividadr@uaemex.mx)

---

## 📄 Licencia

MIT License - Ver archivo LICENSE en el directorio raíz del proyecto.
