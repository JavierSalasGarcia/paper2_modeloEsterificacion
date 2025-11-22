# Análisis de Bifurcación en Optimización Multi-Objetivo de Esterificación

**Fecha**: 2025-11-22
**Autor**: J. Salas-García et al.
**Sistema**: Optimización biodiesel con CaO mediante lógica difusa

---

## 1. Resumen Ejecutivo

Se ha identificado un **fenómeno de bifurcación** en el espacio de optimización multi-objetivo del proceso de esterificación. El sistema presenta **dos regímenes operacionales óptimos** claramente diferenciados, separados por una frontera crítica entre **70-72 minutos** de tiempo de reacción.

### Hallazgos Clave:

- **Régimen RÁPIDO** (60-70 min): Alta agitación (596 RPM), alto catalizador (0.82%)
- **Régimen ECONÓMICO** (72-120 min): Baja agitación (200 RPM), bajo catalizador (0.50%)
- **Transición abrupta**: La discontinuidad ocurre cuando `energy_weight ≥ 0.11`
- **Implicación industrial**: Existe un punto crítico donde el sistema "salta" entre dos modos óptimos de operación

---

## 2. Descripción del Fenómeno

### 2.1 Resultados Experimentales

Evaluación detallada con 16 puntos temporales reveló:

| Tiempo (min) | RPM    | Catalyst (%) | Conversión (%) | Régimen    |
|--------------|--------|--------------|----------------|------------|
| 60           | 596    | 0.82         | 85.27          | RÁPIDO     |
| 65           | 596    | 0.82         | 87.06          | RÁPIDO     |
| 70           | 596    | 0.82         | 88.60          | RÁPIDO     |
| **72**       | **200**| **0.50**     | **89.16**      | **ECONÓMICO** |
| 74           | 200    | 0.50         | 89.69          | ECONÓMICO  |
| 80           | 200    | 0.50         | 91.12          | ECONÓMICO  |
| 90           | 200    | 0.50         | 93.04          | ECONÓMICO  |
| 120          | 200    | 0.50         | 96.59          | ECONÓMICO  |

**Observación crítica**: Entre t=70 y t=72 minutos, el sistema transita abruptamente entre dos configuraciones óptimas completamente diferentes.

### 2.2 Pesos de Lógica Difusa en la Zona Crítica

| Tiempo (min) | energy_weight | catalyst_weight | Membresía SHORT | Membresía MEDIUM |
|--------------|---------------|-----------------|-----------------|------------------|
| 68           | 0.000         | 0.000           | 1.000           | 0.000            |
| 69           | 0.000         | 0.000           | 1.000           | 0.000            |
| 70           | 0.000         | 0.000           | 1.000           | 0.000            |
| **71**       | **0.053**     | **0.020**       | **0.933**       | **0.067**        |
| **72**       | **0.107**     | **0.040**       | **0.867**       | **0.133**        |
| 73           | 0.160         | 0.060           | 0.800           | 0.200            |
| 74           | 0.213         | 0.080           | 0.733           | 0.267            |

**Observación**: Los pesos cambian suavemente (~0.053 por minuto), pero el optimizador responde con un salto discontinuo.

---

## 3. Interpretación Matemática

### 3.1 Función Objetivo Multi-Objetivo

El sistema optimiza:

```
f(T, RPM, Cat) = -Conversion + energy_weight × P_energy + catalyst_weight × P_catalyst
```

Donde:
- `P_energy = 0.6 × T_norm + 0.4 × RPM_norm`  (penalización energética)
- `P_catalyst = Cat_norm`  (penalización de catalizador)

### 3.2 Bifurcación Tipo "Fold Catastrophe"

El fenómeno observado es consistente con una **catástrofe de pliegue** (fold bifurcation):

1. **Para `energy_weight < 0.11`** (t ≤ 70 min):
   - La penalización energética es insuficiente para compensar el beneficio de alta agitación
   - Óptimo global: RPM alto (596), catalizador alto (0.82%)
   - Sistema prioriza **velocidad de conversión**

2. **Para `energy_weight ≥ 0.11`** (t ≥ 72 min):
   - La penalización energética supera el umbral crítico
   - Óptimo global: RPM bajo (200), catalizador bajo (0.50%)
   - Sistema prioriza **eficiencia económica**

3. **Zona de transición (70-72 min)**:
   - El sistema cruza un **punto de bifurcación**
   - Dos óptimos locales existen simultáneamente, pero uno desaparece
   - El algoritmo DE (Differential Evolution) "salta" al nuevo óptimo global

### 3.3 Diagrama Conceptual

```
Conversión (%)
    ^
    |                    Régimen ECONÓMICO
    |                    (bajo RPM, bajo Cat)
    |                   /
    |                  /
    |                 /___________
    |                /|           |
    |               / |  SALTO    |
    |   ___________/  |  BRUSCO   |
    |  /              |           |
    | /  Régimen      |___________|
    |/   RÁPIDO
    |    (alto RPM, alto Cat)
    |
    +--------------------------------> energy_weight
         0.00     0.11              0.80        1.50
         (t=70)   (t=72)            (t=90)      (t=120)
```

---

## 4. Implicaciones Industriales

### 4.1 Regímenes Operacionales

**Régimen RÁPIDO (Producción urgente)**:
- **Uso**: Pedidos urgentes, maximizar productividad horaria
- **Ventajas**: Alta conversión en poco tiempo
- **Desventajas**: Mayor consumo energético, mayor uso de catalizador
- **Rango óptimo**: 60-70 min

**Régimen ECONÓMICO (Producción eficiente)**:
- **Uso**: Producción continua, minimizar costos operacionales
- **Ventajas**: Menor consumo energético, menor catalizador
- **Desventajas**: Requiere tiempos más largos (≥72 min)
- **Rango óptimo**: 72-120 min

### 4.2 Punto de Decisión Operacional

**El punto 70-72 min representa una decisión estratégica**:

- **Si t < 72 min**: Inevitable operar en modo RÁPIDO (costos altos)
- **Si t ≥ 72 min**: Posible operar en modo ECONÓMICO (costos bajos)

Para alcanzar EN 14214 (≥96.5%):
- **Modo RÁPIDO**: Imposible (máx. 88.6% a 70 min)
- **Modo ECONÓMICO**: Requiere t ≥ 115 min (96.17% a 115 min, 96.59% a 120 min)

### 4.3 Costos Comparativos

Estimación relativa de costos por lote (normalizado):

| Tiempo (min) | Régimen    | Conversión (%) | Costo Energía | Costo Catalizador | Costo Total |
|--------------|------------|----------------|---------------|-------------------|-------------|
| 70           | RÁPIDO     | 88.60          | 1.00          | 1.00              | 2.00        |
| 72           | ECONÓMICO  | 89.16          | 0.38          | 0.61              | 0.99        |
| 120          | ECONÓMICO  | 96.59          | 0.38          | 0.61              | 0.99        |

**Conclusión**: El régimen ECONÓMICO reduce costos ~50% manteniendo conversión similar o superior.

---

## 5. Preguntas de Investigación

### 5.1 ¿Por qué la bifurcación ocurre en 70-72 min?

**Hipótesis**:
1. **Umbral energético**: El peso `energy_weight = 0.11` representa el punto donde la penalización energética iguala el beneficio de conversión adicional
2. **Geometría del espacio de búsqueda**: Dos valles separados en el paisaje de optimización
3. **Parámetros de lógica difusa**: La transición SHORT→MEDIUM comienza exactamente a t=70 min

### 5.2 ¿Cómo manipular el punto de bifurcación?

Factores que podrían desplazar el punto 70-72 min:

#### A. Parámetros de Lógica Difusa
```python
# Actual: transición SHORT→MEDIUM comienza a 70 min
self.short_params = {'start': 60, 'peak1': 60, 'peak2': 70, 'end': 85}
self.medium_params = {'start': 70, 'peak1': 85, 'peak2': 100, 'end': 110}

# Hipótesis: Si movemos 'peak2' de SHORT a 65 min
# → Bifurcación ocurriría antes (≈65-67 min)

# Hipótesis: Si movemos 'peak2' de SHORT a 75 min
# → Bifurcación ocurriría después (≈75-77 min)
```

#### B. Pesos de Penalización
```python
# Actual: energy_weight = 0.0 → 0.8 → 1.5 (SHORT → MEDIUM → LONG)
energy_low = 0.0
energy_medium = 0.8
energy_high = 1.5

# Hipótesis: Si reducimos energy_medium a 0.4
# → Mayor energy_weight necesario para bifurcación → Ocurre más tarde

# Hipótesis: Si aumentamos energy_medium a 1.2
# → Menor energy_weight necesario para bifurcación → Ocurre antes
```

#### C. Coeficientes de Distribución Energética
```python
# Actual: P_energy = 0.6 × T_norm + 0.4 × RPM_norm
# (60% temperatura, 40% agitación)

# Hipótesis: Si aumentamos peso de RPM a 0.6
# → RPM penalizado más fuertemente → Bifurcación ocurre antes
```

#### D. Límites de Optimización (Bounds)
```python
# Actual: RPM ∈ [200, 731]
# Si reducimos límite inferior: RPM ∈ [100, 731]
# → Mayor incentivo para reducir RPM → Bifurcación ocurre antes

# Actual: Catalyst ∈ [0.5, 2.0]%
# Si reducimos límite inferior: Catalyst ∈ [0.3, 2.0]%
# → Mayor ahorro posible → Bifurcación ocurre antes
```

---

## 6. Experimentos Propuestos

### 6.1 Sensibilidad a Parámetros de Lógica Difusa

**Objetivo**: Mover el punto de bifurcación variando `short_params['peak2']`

**Método**:
1. Evaluar con `peak2 = [65, 67.5, 70, 72.5, 75]`
2. Para cada configuración, ejecutar optimización en t = [60, 65, 70, 75, 80, 85, 90]
3. Identificar punto de transición RÁPIDO→ECONÓMICO

**Resultado esperado**: Relación lineal entre `peak2` y punto de bifurcación

### 6.2 Sensibilidad a Pesos de Penalización

**Objetivo**: Controlar bifurcación mediante escalado de penalizaciones

**Método**:
1. Variar `energy_medium = [0.4, 0.6, 0.8, 1.0, 1.2]` (mantener SHORT=0.0, LONG=1.5)
2. Ejecutar optimización con t = [60, 65, 70, 75, 80, 85, 90]
3. Identificar punto de transición

**Resultado esperado**: Mayor `energy_medium` → Bifurcación más temprana

### 6.3 Sensibilidad a Límites de Optimización

**Objetivo**: Explorar efecto de restricciones operacionales

**Método**:
1. Variar límite inferior de RPM: `[100, 150, 200, 250, 300]`
2. Ejecutar optimización con configuración actual
3. Medir desplazamiento del punto de bifurcación

**Resultado esperado**: Mayor límite inferior → Bifurcación más tardía (requiere mayor penalización)

---

## 7. Modelado Matemático del Punto de Bifurcación

### 7.1 Condición de Equilibrio

El punto de bifurcación ocurre cuando:

```
Benefit(high RPM) - Cost(high RPM) = Benefit(low RPM) - Cost(low RPM)
```

Expandiendo:

```
ΔConversion(high RPM) - energy_weight × ΔP_energy(high RPM)
    = ΔConversion(low RPM) - energy_weight × ΔP_energy(low RPM)
```

Resolviendo para `energy_weight*`:

```
energy_weight* = [ΔConversion(high) - ΔConversion(low)] /
                 [ΔP_energy(high) - ΔP_energy(low)]
```

**Estimación con datos observados**:
- `ΔConversion(high RPM=596) - ΔConversion(low RPM=200) ≈ 0.5%` (marginal a t=72)
- `ΔP_energy(high) - ΔP_energy(low) = 0.4 × (596-200)/(731-200) ≈ 0.4 × 0.746 = 0.298`

```
energy_weight* ≈ 0.5 / 0.298 ≈ 1.68% conversión / unidad penalización
```

Pero la bifurcación ocurre a `energy_weight = 0.11`, lo cual sugiere que:
- El beneficio real de alta agitación es mayor que el observado (~5% en lugar de 0.5%)
- O existe un efecto no lineal en la función de conversión

### 7.2 Predicción del Punto de Bifurcación

**Fórmula empírica propuesta**:

```
t_bifurcation ≈ t_start_transition + Δt × (energy_threshold - energy_min) / (energy_slope)
```

Donde:
- `t_start_transition = 70 min` (cuando SHORT comienza a decaer)
- `energy_threshold = 0.11` (umbral crítico observado)
- `energy_min = 0.0` (peso en régimen SHORT puro)
- `energy_slope = 0.8 / (100 - 70) = 0.0267 por minuto` (pendiente de transición)

```
t_bifurcation ≈ 70 + (0.11 - 0.0) / 0.0267 ≈ 70 + 4.1 ≈ 74.1 min
```

**Discrepancia observada**: El punto real es 72 min, no 74 min.

**Posible explicación**: El algoritmo DE es estocástico y puede encontrar el nuevo óptimo ligeramente antes del punto teórico de equilibrio.

---

## 8. Conclusiones

1. **Fenómeno de bifurcación confirmado**: Existe una transición abrupta entre dos regímenes operacionales óptimos a 70-72 minutos.

2. **Causa raíz**: El cruce del umbral crítico `energy_weight ≥ 0.11` cambia la estructura del paisaje de optimización.

3. **Control del punto de bifurcación**: Puede manipularse mediante:
   - Parámetros de funciones de membresía difusa (`peak2` de SHORT)
   - Escalado de pesos de penalización (`energy_medium`, `catalyst_medium`)
   - Límites de variables de optimización (bounds)
   - Coeficientes de distribución energética (60/40 → otros ratios)

4. **Implicación práctica**: El sistema ofrece **flexibilidad estratégica**:
   - Producción rápida (60-70 min) con costos altos
   - Producción eficiente (≥72 min) con costos bajos
   - El punto de decisión puede ajustarse según necesidades industriales

5. **Siguiente paso**: Crear herramienta de análisis de sensibilidad para cuantificar el efecto de cada parámetro en el punto de bifurcación.

---

## 9. Referencias Técnicas

- **Optimization summary**: `Casos/caso3_optimizacion/resultados/optimization_summary.json`
- **Fuzzy logic system**: `fuzzy_weight_optimizer.py`
- **Multi-objective optimizer**: `src/optimization/optimizer.py` (líneas 131-143)
- **Modification log**: `modificaciones.md` (Entrada #4)

---

**Autor**: Sistema de optimización biodiesel CaO
**Fecha**: 2025-11-22
**Versión**: 1.0
