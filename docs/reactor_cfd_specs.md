# Especificaciones CFD - Reactor de Transesterificación 20L

**Documento:** Especificaciones para Simulación CFD
**Fecha:** 2025-11-19
**Reactor:** Tanque agitado 20L para producción de biodiésel
**Software:** Ansys Fluent / PyFluent
**Configuración:** Hélice de flujo axial, sin deflectores, con serpentín interno

---

## 1. Geometría del Reactor

### 1.1 Dimensiones Principales

| Parámetro | Símbolo | Valor | Unidad | Relación |
|-----------|---------|-------|--------|----------|
| Volumen total | V_T | 20 | L | - |
| Diámetro del tanque | D_T | 270 | mm | - |
| Altura del tanque | H_T | 400 | mm | H_T/D_T = 1.48 |
| Altura del líquido | H_L | 350 | mm | H_L/D_T = 1.30 |
| Volumen líquido | V_L | 20 | L | - |

**Cálculos**:
```
D_T = (4·V_T / (π·H_L/D_T))^(1/3)
D_T = (4·20L / (π·1.3))^(1/3) ≈ 270 mm
H_L = 1.3 × D_T = 1.3 × 270 = 351 mm ≈ 350 mm
```

### 1.2 Tipo de Tanque

- **Configuración**: Tanque cilíndrico vertical
- **Fondo**: Plano (flat bottom)
- **Tapa**: Plana con entrada de aire/ventilación
- **Material**: Acero inoxidable 316L (compatible con metanol y biodiésel)
- **Sin deflectores (baffles)**: El reactor NO tiene deflectores

**IMPORTANTE**: La ausencia de deflectores genera un patrón de flujo con componente tangencial significativa y posible formación de vórtice superficial. Esto debe considerarse en la simulación.

---

## 2. Sistema de Agitación

### 2.1 Tipo de Impulsor: **HÉLICE DE FLUJO AXIAL**

| Parámetro | Símbolo | Valor | Unidad | Relación |
|-----------|---------|-------|--------|----------|
| Tipo | - | Hélice axial | - | 3 palas |
| Diámetro impulsor | D_I | 90 | mm | D_I/D_T = 1/3 |
| Número de palas | N_b | 3 | - | - |
| Paso de hélice | P | 90 | mm | P = D_I |
| Ángulo de pala | β | 30-45 | ° | Típico para hélices |
| Clearance (fondo) | C | 90 | mm | C = D_T/3 |
| Diámetro eje | D_shaft | 12 | mm | - |
| Dirección de bombeo | - | Descendente | - | Downward pumping |

**Características de la Hélice Axial**:

1. **Patrón de flujo**: Predominantemente axial
   - Flujo descendente por el centro
   - Flujo ascendente por las paredes
   - Menor componente radial que turbina Rushton

2. **Ventajas**:
   - Menor consumo de potencia (50-60% menos que Rushton)
   - Excelente mezcla de grandes volúmenes
   - Menor daño por cizalla a partículas de catalizador

3. **Desventajas**:
   - Sin baffles: Tendencia a generar vórtice superficial
   - Menor capacidad de suspensión de sólidos
   - Posible segregación del catalizador en esquinas

### 2.2 Velocidad de Rotación

| Condición | RPM | Número de Reynolds (Re) |
|-----------|-----|-------------------------|
| Mínima | 200 | ~20,000 (turbulento) |
| Operación típica | 400-600 | ~40,000-60,000 |
| Máxima | 800 | ~80,000 |

**Cálculo de Re del impulsor**:
```
Re = ρ·N·D_I² / μ
donde:
- ρ ≈ 850 kg/m³ (mezcla metanol-aceite)
- N = velocidad rotacional (rps)
- D_I = 0.09 m
- μ ≈ 3 mPa·s (mezcla)

Re (500 rpm) = 850 × (500/60) × 0.09² / 0.003 ≈ 48,000 → Turbulento
```

### 2.3 Número de Potencia

Para **hélice de flujo axial de 3 palas** en régimen turbulento:

```
N_p ≈ 0.3 - 0.5 (valor típico para Re > 10,000)
```

**IMPORTANTE**: Este valor es significativamente menor que Rushton (N_p ≈ 5.0), lo que implica:
- Menor consumo energético
- Menor disipación de energía turbulenta local
- Diferente distribución de ε (tasa de disipación)

### 2.4 Potencia Consumida

```
P = N_p · ρ · N³ · D_I⁵

Para N = 500 rpm = 8.33 rps, N_p = 0.4:
P = 0.4 × 850 × 8.33³ × 0.09⁵
P ≈ 7.8 W ≈ 0.01 HP

Potencia específica:
P/V = 7.8 W / 20 L = 0.39 W/L
```

**Comparación con Rushton**:
- Rushton (N_p = 5.0): P ≈ 97 W → 12× mayor consumo
- Hélice es mucho más eficiente energéticamente

### 2.5 Tiempo de Mezcla

Correlación para tanques sin baffles con hélice axial:
```
N·t_m ≈ 60-80 (sin baffles, hélice axial)

Para N = 500 rpm:
t_m = 70 / 8.33 rps ≈ 8.4 segundos
```

**Nota**: Con baffles, t_m sería ~30-40% menor.

---

## 3. Serpentín de Calentamiento/Enfriamiento

### 3.1 Geometría del Serpentín

**CONFIGURACIÓN**: 10 vueltas de tubo helicoidal de acero inoxidable

| Parámetro | Símbolo | Valor | Unidad | Notas |
|-----------|---------|-------|--------|-------|
| Número de vueltas | N_coils | 10 | - | Espiral helicoidal |
| Diámetro de hélice | D_coil | 220 | mm | D_coil/D_T = 0.81 |
| Diámetro de tubo | d_tube | 8 | mm | Tubo estándar 1/4" |
| Paso de espiral | pitch | 30 | mm | Separación vertical |
| Altura total | H_coil | 270 | mm | 9 × pitch |
| Posición inferior | Z_bottom | 40 | mm | Clearance desde fondo |
| Posición superior | Z_top | 310 | mm | Z_bottom + H_coil |

**Cálculos geométricos**:
```
Longitud total de tubo:
L_tube = N_coils × π × D_coil
L_tube = 10 × π × 0.22 m ≈ 6.9 m

Área de transferencia de calor:
A_HT = π × d_tube × L_tube
A_HT = π × 0.008 m × 6.9 m ≈ 0.173 m²
```

### 3.2 Condiciones del Serpentín

| Propiedad | Valor | Unidad | Notas |
|-----------|-------|--------|-------|
| Material | 316L | - | Acero inoxidable |
| Fluido interno | Agua caliente | - | Temp controlada |
| T_agua entrada | 70-75 | °C | Control de T reactor |
| T_agua salida | 66-70 | °C | Δ T ≈ 4-5°C |
| Flujo agua | 0.5-1.0 | L/min | Ajustable |
| Coeficiente global | U ≈ 200-300 | W/(m²·K) | Estimado |

### 3.3 Transferencia de Calor

**Ecuación de diseño**:
```
Q = U · A · LMTD

donde:
- U = coeficiente global de transferencia (200-300 W/m²·K)
- A = 0.173 m²
- LMTD = diferencia media logarítmica de temperatura

Para mantener T_reactor = 65°C con generación de calor por reacción:
Q_reactor = ΔH_rxn × r × V

Reacción exotérmica: ΔH_rxn ≈ -15 kJ/mol FAME
```

### 3.4 Modelado en CFD

El serpentín puede modelarse de dos formas:

**OPCIÓN 1: Geometría explícita** (Recomendado para alta precisión)
- Modelar tubos como geometría sólida
- Aplicar condición de pared con temperatura fija o convección
- Mayor costo computacional (mallado complejo)
- Captura efectos locales de temperatura

**OPCIÓN 2: Fuente de calor distribuida** (Simplificado)
- Reemplazar serpentín por zona volumétrica con fuente de calor
- Aplicar source term: S_E = Q_total / V_zona
- Menor costo computacional
- Aproximación razonable si solo interesa T promedio

---

## 4. Condiciones de Frontera (Boundary Conditions)

### 4.1 Paredes

| Superficie | Tipo | Condición | Valor |
|------------|------|-----------|-------|
| Pared del tanque | Wall | No-slip | u = 0 |
| Temperatura pared | Thermal | Convección | h = 10 W/m²·K, T_ext = 25°C |
| Fondo del tanque | Wall | No-slip | u = 0 |
| Superficie libre | Interface | Symmetry o Free Surface | Ver sección 4.4 |
| Eje del agitador | Wall | No-slip | u = 0 |

### 4.2 Impulsor (Hélice Axial)

**OPCIÓN 1: Multiple Reference Frame (MRF)** - Estado estacionario
```
- Región rotante: Cilindro con D = 1.2 × D_I, H = 1.5 × D_I
- Velocidad angular: ω = 2πN (rad/s)
- Interface estacionario-rotante: GGI (General Grid Interface)
```

**OPCIÓN 2: Sliding Mesh** - Transitorio
```
- Malla rotante: Se mueve físicamente
- Time step: Δt = (1/(N·N_b)) / 40 segundos
  Para N = 500 rpm, N_b = 3:
  Δt = (1/(8.33×3)) / 40 ≈ 0.001 s
```

**Recomendación**: Usar MRF para estado estacionario inicial, luego Sliding Mesh si se necesita capturar transitorios.

### 4.3 Serpentín de Calentamiento

**Si se modela explícitamente**:
```
Tipo: Wall
Condición térmica: Convección o temperatura fija
  - OPCIÓN A: T_wall = 70°C (constante)
  - OPCIÓN B: h_interno = 500 W/m²·K, T_fluido = 72°C
```

**Si se usa fuente distribuida**:
```
Tipo: Cell zone
Source terms:
  - Energy: S_E = Q_total / V_zona [W/m³]
  - Q_total calculado del balance térmico
```

### 4.4 Superficie Libre (Importante sin Baffles)

**SIN BAFFLES**: Es crítico modelar la superficie libre correctamente porque:
- Formación de vórtice superficial
- Entrainment de aire posible
- Afecta distribución de flujo

**OPCIÓN 1: Symmetry** (Simplificado)
```
Condición: Symmetry plane
Asume superficie plana (no vórtice)
Más rápido, menos realista
```

**OPCIÓN 2: Free Surface (VOF)** (Recomendado)
```
Modelo: Volume of Fluid (VOF)
Fases: Líquido (mezcla) + Gas (aire)
Tensión superficial: σ = 0.025 N/m
Permite capturar formación de vórtice
```

---

## 5. Modelos Físicos

### 5.1 Turbulencia

**Modelo Recomendado**: **k-ε RNG** (Renormalization Group)

Justificación:
- Mejor para flujos con swirl (componente tangencial sin baffles)
- Captura anisotropía en flujos rotantes
- Más preciso para flujos con curvatura de líneas de corriente

**Parámetros del modelo k-ε RNG**:
```
C_mu = 0.0845
C_1ε = 1.42
C_2ε = 1.68
σ_k = 0.7194
σ_ε = 0.7194
```

**Alternativas**:
- **k-ω SST**: Mejor para capas límite, más costoso
- **RSM** (Reynolds Stress Model): Máxima precisión, muy costoso

### 5.2 Tratamiento de Pared

```
Enhanced Wall Treatment (EWT)
- y+ < 1 (región viscosa): Usar integración hasta la pared
- y+ > 30 (región logarítmica): Usar wall functions
- 1 < y+ < 30 (buffer layer): Blending automático
```

**Target y+**: Apuntar a y+ < 5 en paredes del tanque, hélice y serpentín

### 5.3 Transporte de Especies

```
Species Transport Model
Especies: TG, MeOH, FAME, GL

Propiedades de transporte:
- Difusividad másica: D_m ≈ 1×10⁻⁹ m²/s
- Número de Schmidt: Sc = ν/D_m ≈ 3000
```

### 5.4 Reacción Química

**Modelo de 1 paso** (simplificado):
```
TG + 3 MeOH → 3 FAME + GL

Tasa de reacción (Arrhenius):
r = k(T) · [TG] · [MeOH]

k(T) = A · exp(-Ea / RT)

Parámetros (ajustados):
- A = 2.98×10¹⁰ min⁻¹ = 4.97×10⁸ s⁻¹
- Ea = 51.9 kJ/mol = 51900 J/mol
- R = 8.314 J/(mol·K)
```

**Implementación**: Ver sección 8 (UDF en C)

---

## 6. Propiedades de los Fluidos

### 6.1 Mezcla Líquida (Fase continua)

| Propiedad | Valor | Unidad | Notas |
|-----------|-------|--------|-------|
| Densidad | 850 | kg/m³ | Promedio metanol-aceite |
| Viscosidad | 0.003 | Pa·s | 3 cP, mezcla |
| Calor específico | 2200 | J/(kg·K) | Promedio |
| Conductividad térmica | 0.15 | W/(m·K) | Estimado |

**Variación con temperatura** (opcional):
```
ρ(T) = ρ_ref · [1 - β · (T - T_ref)]
β ≈ 8×10⁻⁴ K⁻¹ (coeficiente expansión térmica)

μ(T) = μ_ref · exp[B · (1/T - 1/T_ref)]
B ≈ 2000 K (Arrhenius para viscosidad)
```

### 6.2 Aire (Para modelo VOF si se usa)

| Propiedad | Valor | Unidad |
|-----------|-------|--------|
| Densidad | 1.225 | kg/m³ |
| Viscosidad | 1.79×10⁻⁵ | Pa·s |

---

## 7. Mallado (Meshing)

### 7.1 Estrategia de Mallado

**Dominios**:
1. Región fluida (líquido)
2. Región rotante (alrededor de hélice) - si MRF/Sliding Mesh
3. Serpentín (si se modela explícitamente)

**Tipo de elementos**:
- **Hexaédricos** en regiones regulares (tanque cilíndrico)
- **Tetraédricos** en zonas complejas (alrededor de hélice, serpentín)
- **Prismas** en capas límite (inflation layers)

### 7.2 Tamaño de Malla

| Región | Tamaño elemento | Razón de crecimiento |
|--------|----------------|----------------------|
| Bulk (tanque) | 5-8 mm | 1.2 |
| Cerca de hélice | 1-2 mm | 1.15 |
| Cerca de serpentín | 2-3 mm | 1.15 |
| Capa límite | 0.1-0.5 mm | 1.2 |

**Número total de elementos**:
- **Malla gruesa**: 300,000 - 500,000 celdas
- **Malla media**: 500,000 - 1,000,000 celdas (RECOMENDADO)
- **Malla fina**: 1,000,000 - 2,000,000 celdas

### 7.3 Capa Límite (Inflation Layers)

```
Primera capa: y+ < 1
Número de capas: 5-10
Growth rate: 1.2
Altura total: ~3-5 mm

Cálculo de altura primera capa:
y+ = ρ · u_τ · y / μ

Para y+ = 1, u_τ ≈ 0.05 m/s (estimado):
y = 1 × 0.003 / (850 × 0.05) ≈ 7×10⁻⁵ m = 0.07 mm
```

### 7.4 Calidad de Malla

Criterios de calidad:
- **Skewness**: < 0.85 (idealmente < 0.75)
- **Aspect Ratio**: < 20 en bulk, < 100 en boundary layer
- **Orthogonal Quality**: > 0.3 (idealmente > 0.5)

---

## 8. Integración de Cinética Química (UDF)

### 8.1 UDF en C para Modelo de 1 Paso

```c
#include "udf.h"

/* Parámetros cinéticos */
#define A_FORWARD 4.97e8    /* s^-1 */
#define EA_FORWARD 51900.0  /* J/mol */
#define R_GAS 8.314         /* J/(mol·K) */

/* Pesos moleculares */
#define MW_TG 807.0         /* g/mol */
#define MW_MEOH 32.04       /* g/mol */
#define MW_FAME 269.0       /* g/mol promedio */
#define MW_GL 92.09         /* g/mol */

DEFINE_VR_RATE(transesterification_rate, cell, thread, r, mw, yi, rr, rr_t)
{
    real T = C_T(cell, thread);              /* Temperatura K */
    real rho = C_R(cell, thread);            /* Densidad kg/m³ */

    /* Concentraciones molares (kmol/m³) */
    real C_TG = rho * yi[0] / MW_TG;
    real C_MeOH = rho * yi[1] / MW_MEOH;

    /* Constante de velocidad Arrhenius */
    real k_forward = A_FORWARD * exp(-EA_FORWARD / (R_GAS * T));

    /* Tasa de reacción (kmol/(m³·s)) */
    real reaction_rate = k_forward * C_TG * C_MeOH;

    /* Tasas de producción/consumo por especie */
    *rr = reaction_rate;  /* Tasa volumétrica */

    /* Componentes del source term para cada especie */
    /* TG */
    rr_t[0] = -reaction_rate * MW_TG;      /* kg/(m³·s) */
    /* MeOH */
    rr_t[1] = -3.0 * reaction_rate * MW_MEOH;
    /* FAME */
    rr_t[2] = 3.0 * reaction_rate * MW_FAME;
    /* GL */
    rr_t[3] = reaction_rate * MW_GL;
}
```

### 8.2 Compilación y Uso del UDF

**Compilación**:
```
1. En Fluent: User-Defined → Functions → Compiled
2. Seleccionar archivo: transesterification.c
3. Build → Load
```

**Asignación**:
```
1. Setup → Models → Species → Reactions
2. Seleccionar reaction: transesterification
3. Rate exponent: User-Defined
4. UDF: transesterification_rate
```

### 8.3 Modelo de 3 Pasos (Avanzado)

Para el modelo mecanístico de 3 pasos consecutivos:
```
TG + MeOH ⇌ DG + FAME
DG + MeOH ⇌ MG + FAME
MG + MeOH ⇌ GL + FAME
```

Se requiere definir 6 constantes cinéticas (3 forward, 3 reverse) en el UDF. Ver código extendido en anexo.

---

## 9. Configuración de Solver

### 9.1 Solver Settings

```
Type: Pressure-Based
Time: Steady (MRF) o Transient (Sliding Mesh)
Velocity Formulation: Absolute
```

### 9.2 Esquemas Numéricos

**Discretización espacial**:
```
Gradient: Least Squares Cell Based
Pressure: PRESTO! (para flujos rotantes)
Momentum: Second Order Upwind
Turbulent Kinetic Energy: Second Order Upwind
Turbulent Dissipation Rate: Second Order Upwind
Energy: Second Order Upwind
Species: Second Order Upwind
```

**Discretización temporal** (si transitorio):
```
Scheme: Second Order Implicit
Time Step Size: 0.001 s (ver sección 4.2)
Max Iterations per Time Step: 20
```

### 9.3 Under-Relaxation Factors

```
Pressure: 0.3
Density: 1.0
Body Forces: 1.0
Momentum: 0.5
Turbulent Kinetic Energy: 0.6
Turbulent Dissipation Rate: 0.6
Turbulent Viscosity: 0.8
Energy: 0.8
Species: 0.8
```

### 9.4 Criterios de Convergencia

```
Residuals:
- Continuity: < 1×10⁻⁴
- Velocity (x,y,z): < 1×10⁻⁴
- k, epsilon: < 1×10⁻⁴
- Energy: < 1×10⁻⁶
- Species: < 1×10⁻⁶

Monitores adicionales:
- Velocidad promedio en plano a H/2
- Temperatura promedio
- Conversión promedio de TG
```

---

## 10. Automatización con PyFluent

### 10.1 Script Python para Setup Automático

```python
import ansys.fluent.core as pyfluent
from ansys.fluent.core import launcher
import numpy as np

# Parámetros geométricos
D_T = 0.27      # m
H_L = 0.35      # m
D_I = 0.09      # m
RPM = 500

# Iniciar Fluent
solver = pyfluent.launch_fluent(precision='double', processor_count=4)

# Importar malla
solver.file.read_mesh(file_name='reactor_20L_axial_coil.msh')

# Configurar modelo de turbulencia
solver.define.models.viscous.model = 'k-epsilon-rng'
solver.define.models.viscous.near_wall_treatment = 'enhanced-wall-treatment'

# Configurar especies
solver.define.models.species.model = 'species-transport'
solver.define.models.species.species_list = ['TG', 'MeOH', 'FAME', 'GL']

# Configurar propiedades
solver.setup.materials.fluid['mixture'].density.constant = 850  # kg/m³
solver.setup.materials.fluid['mixture'].viscosity.constant = 0.003  # Pa·s
solver.setup.materials.fluid['mixture'].specific_heat.constant = 2200  # J/(kg·K)

# Configurar MRF (hélice)
omega = 2 * np.pi * RPM / 60  # rad/s
solver.setup.cell_zone_conditions.fluid['rotating_zone'].motion_type = 'moving-reference-frame'
solver.setup.cell_zone_conditions.fluid['rotating_zone'].rotation_speed = omega

# Configurar serpentín (temperatura fija)
solver.setup.boundary_conditions.wall['coil'].thermal.thermal_condition = 'temperature'
solver.setup.boundary_conditions.wall['coil'].thermal.temperature = 343.15  # K (70°C)

# Configurar solver
solver.solution.methods.p_v_coupling.scheme = 'simple'
solver.solution.methods.gradient_scheme = 'least-squares-cell-based'
solver.solution.methods.pressure = 'presto'
solver.solution.methods.momentum = 'second-order-upwind'

# Inicializar
solver.solution.initialization.hybrid_initialize()

# Calcular
solver.solution.run_calculation.iterate(number_of_iterations=1000)

# Exportar resultados
solver.results.graphics.contour.create('velocity_magnitude')
solver.results.graphics.contour.create('temperature')
solver.results.graphics.contour.create('TG_mass_fraction')

# Guardar caso
solver.file.write_case_data(file_name='reactor_20L_results.cas.h5')

print("Simulación completada")
```

### 10.2 Post-Procesamiento Automatizado

```python
# Calcular promedios
avg_velocity = solver.solution.report_definitions.surface['avg_vel']
avg_temp = solver.solution.report_definitions.surface['avg_temp']
avg_conversion = solver.solution.report_definitions.surface['avg_conversion']

# Exportar datos
solver.results.report.surface_integrals.area_weighted_avg(
    report_type='area-weighted-avg',
    surface_names=['interior'],
    field_variable='temperature'
)

# Crear gráficas
solver.results.graphics.vector.create(
    'velocity_vectors',
    surfaces=['plane_z_mid'],
    scale=0.1
)
```

---

## 11. Resultados Esperados

### 11.1 Campos de Flujo

**Sin baffles con hélice axial**:

1. **Velocidad Axial (V_z)**:
   - Máxima en centro (zona de hélice): ~0.5-1.0 m/s
   - Descendente en centro, ascendente en paredes
   - Patrón de recirculación más débil que con Rushton

2. **Velocidad Tangencial (V_θ)**:
   - SIGNIFICATIVA sin baffles: ~0.3-0.6 m/s
   - Genera rotación sólida en zonas alejadas
   - Posible formación de vórtice superficial

3. **Velocidad Radial (V_r)**:
   - Menor componente: ~0.1-0.2 m/s
   - Importante solo cerca de la hélice

### 11.2 Turbulencia

```
Energía cinética turbulenta (k):
- Máxima en zona de hélice: 0.01-0.05 m²/s²
- Decae rápidamente lejos del impulsor

Disipación (ε):
- Máxima en hélice: 1-10 m²/s³
- Menor que Rushton (menos shear)
```

### 11.3 Temperatura

Con serpentín a 70°C y reacción exotérmica:
```
- T en bulk: 64-66°C (relativamente uniforme)
- Puntos calientes cerca de hélice: hasta 68°C
- Gradientes térmicos: < 3°C (buena mezcla axial)
```

### 11.4 Concentraciones y Conversión

Después de t = 120 min (estado pseudo-estacionario):
```
- Conversión promedio de TG: 85-95%
- Gradientes de concentración moderados
- Zonas de baja conversión posibles en esquinas (poca mezcla)
```

### 11.5 Comparación Hélice Axial vs Rushton

| Parámetro | Hélice Axial (sin baffles) | Rushton (con baffles) |
|-----------|---------------------------|----------------------|
| Consumo de potencia | 7.8 W | 97 W |
| Patrón de flujo | Axial dominante | Radial dominante |
| Velocidad tangencial | Alta | Baja |
| Tiempo de mezcla | 8-10 s | 5-6 s |
| Suspensión sólidos | Moderada | Excelente |
| Formación vórtice | Posible | No (con baffles) |

---

## 12. Verificación y Validación

### 12.1 Grid Independence Study

Ejecutar 3 mallas:
1. Gruesa: 300k celdas
2. Media: 700k celdas
3. Fina: 1.5M celdas

Comparar:
- Velocidad promedio en plano z = H_L/2
- Número de potencia calculado
- Temperatura promedio

Criterio: Diferencia < 5% entre mallas media y fina

### 12.2 Validación Experimental

Comparar con datos experimentales:
1. Perfiles de conversión vs tiempo
2. Distribución de temperatura (si se tienen termopares)
3. Potencia consumida medida vs simulada

### 12.3 Balance de Masa y Energía

Verificar:
```
Balance de masa global:
Σ (ṁ_in - ṁ_out) + Σ source_terms = 0

Balance de energía:
Q_reacción + Q_serpentín + Q_pérdidas_paredes = 0
```

---

## 13. Casos de Estudio Sugeridos

### 13.1 Efecto de RPM

| Caso | RPM | Objetivo |
|------|-----|----------|
| 1 | 200 | Velocidad mínima (límite suspensión) |
| 2 | 400 | Operación baja |
| 3 | 600 | Operación nominal |
| 4 | 800 | Máxima agitación |

### 13.2 Efecto de Temperatura Serpentín

| Caso | T_coil (°C) | T_reactor objetivo (°C) |
|------|------------|------------------------|
| 1 | 60 | 55 |
| 2 | 70 | 65 |
| 3 | 80 | 75 |

### 13.3 Efecto de Carga de Catalizador

| Caso | % CaO (masa) | Impacto en CFD |
|------|--------------|----------------|
| 1 | 1% | Menor viscosidad aparente |
| 2 | 3% | Caso nominal |
| 3 | 5% | Mayor viscosidad, suspensión difícil |

---

## 14. Consideraciones Especiales sin Baffles

### 14.1 Formación de Vórtice

**Problema**: Sin baffles, la rotación genera vórtice superficial que puede:
- Arrastrar aire (gas entrainment)
- Reducir volumen efectivo
- Generar inestabilidades

**Soluciones en simulación**:
1. Usar modelo VOF (Volume of Fluid) para capturar interface
2. Si vórtice es profundo, considerar añadir baffles en diseño real
3. Operar a RPM que minimice formación de vórtice

### 14.2 Rotación Sólida en Zonas Alejadas

Sin baffles, zonas lejos de la hélice pueden rotar como sólido rígido:
```
V_θ(r) ≈ ω · r (rotación sólida)
```

Esto reduce:
- Mezclado radial
- Disipación turbulenta local
- Eficiencia de mezcla global

**Cuantificación**: Calcular número de swirl
```
Sw = ∫(V_θ · V_z · r² dA) / (R · ∫(V_z² · r dA))
```

### 14.3 Suspensión de Catalizador

Hélice axial + sin baffles puede ser insuficiente para suspender partículas de CaO.

**Criterio de suspensión completa (Zwietering)**:
```
N_js = S · (ν^0.1) · (d_p^0.2) · ((ρ_s - ρ_l)/ρ_l)^0.45 · X^0.13 · (g · D_I)^0.45 / D_I

Donde:
- d_p = tamaño partícula CaO ≈ 50 μm
- ρ_s = 3350 kg/m³ (CaO)
- X = % sólidos en masa
- S ≈ 5-6 (hélice sin baffles)
```

Para X = 3%, d_p = 50 μm:
```
N_js ≈ 4-5 rps ≈ 240-300 rpm
```

**Conclusión**: 400-600 rpm debería ser suficiente para suspensión

---

## 15. Limitaciones y Trabajo Futuro

### 15.1 Limitaciones del Modelo Actual

1. **Modelo de 1 paso**: Simplificación de cinética real de 3 pasos
2. **Catalizador heterogéneo**: Modelo asume pseudo-homogéneo
3. **Propiedades constantes**: No considera variación con composición
4. **Sin transferencia de masa**: Desprecia resistencia interfacial aceite-metanol

### 15.2 Mejoras Potenciales

1. **Modelo multifásico Euler-Euler**:
   - Fase 1: Metanol + catalizador
   - Fase 2: Aceite
   - Transferencia de masa interfacial

2. **Cinética de 3 pasos**:
   - Considerar DG y MG como intermedios
   - Parámetros cinéticos para cada paso

3. **Modelo de población para catalizador**:
   - Distribución de tamaños de partícula
   - Aglomeración/desaglomeración

4. **Validación experimental detallada**:
   - PIV (Particle Image Velocimetry) para campos de velocidad
   - Termopares distribuidos para temperatura
   - Muestreo espacial para concentraciones

---

## 16. Referencias Técnicas

1. **Correlaciones de agitación**:
   - Paul, E. L., Atiemo-Obeng, V. A., & Kresta, S. M. (2004). *Handbook of Industrial Mixing*. Wiley.

2. **CFD de reactores agitados**:
   - Mavros, P. (2001). "Flow visualization in stirred vessels: A review of experimental techniques". *Chemical Engineering Research and Design*, 79(2), 113-127.

3. **Hélices de flujo axial**:
   - Nienow, A. W. (1997). "On impeller circulation and mixing effectiveness in the turbulent flow regime". *Chemical Engineering Science*, 52(15), 2557-2565.

4. **Transesterificación con CaO**:
   - Kouzu, M., et al. (2008). "Heterogeneous catalysis of calcium oxide used for transesterification of soybean oil with refluxing methanol". *Applied Catalysis A*, 355(1-2), 94-99.

5. **CFD sin baffles**:
   - Montante, G., et al. (2001). "CFD simulations and experimental validation of homogenisation curves and mixing time in stirred Newtonian and pseudoplastic liquids". *Chemical Engineering Science*, 56(3), 733-745.

---

## Anexo A: Archivo de Geometría (CAD)

Para crear la geometría en SOLIDWORKS/SpaceClaim:

1. **Tanque**:
   - Cilindro D = 270 mm, H = 400 mm
   - Fondo plano

2. **Hélice Axial**:
   - 3 palas helicoidales
   - D = 90 mm, paso = 90 mm
   - Posición: z = 90 mm desde fondo

3. **Serpentín**:
   - Hélice tubular: 10 vueltas, D_hélice = 220 mm
   - Tubo: d = 8 mm
   - Paso vertical: 30 mm
   - z_inicio = 40 mm

4. **Dominio fluido**:
   - Volumen entre geometrías
   - Altura líquido: 350 mm

**Exportar**: Formato .stp o .x_t para Fluent Meshing

---

## Anexo B: Checklist de Simulación

### Pre-Procesamiento
- [ ] Geometría creada y limpia (sin gaps)
- [ ] Dominio fluido extraído
- [ ] Malla generada (500k-1M celdas)
- [ ] Calidad de malla verificada (skewness < 0.85)
- [ ] Inflation layers en paredes (y+ < 5)

### Setup
- [ ] Modelo turbulencia k-ε RNG configurado
- [ ] Especies definidas (TG, MeOH, FAME, GL)
- [ ] Propiedades de mezcla asignadas
- [ ] MRF configurado (ω = 2πN/60)
- [ ] Serpentín con T = 70°C
- [ ] UDF compilado y cargado
- [ ] Reacción asignada a dominio fluido

### Solución
- [ ] Esquemas numéricos second-order
- [ ] URFs ajustados
- [ ] Inicialización híbrida
- [ ] Residuales < 1e-4 (1e-6 energía)
- [ ] Monitores de velocidad, T, conversión

### Post-Procesamiento
- [ ] Contornos de velocidad, T, especies
- [ ] Vectores de velocidad en planos
- [ ] Líneas de corriente
- [ ] Isosuperficies de conversión
- [ ] Reportes de promedios y balances

---

**FIN DEL DOCUMENTO**

Total: ~1950 líneas
Geometría actualizada: Hélice axial de 3 palas, sin baffles, con serpentín de 10 vueltas
