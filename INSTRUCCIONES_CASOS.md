# Instrucciones para Ejecutar Casos de Uso

Este documento explica cómo ejecutar los 4 casos de uso del sistema para generar los resultados del artículo RICI.

## 📋 Pre-requisitos

1. **Python 3.8+** instalado
2. **Dependencias instaladas**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Git** configurado (para commits)

## 🔄 Orden de Ejecución

Los casos deben ejecutarse en orden secuencial para aprovechar outputs previos:

```
Caso 1 → Caso 2 → Caso 3 → Caso 4
```

---

## 🎯 Caso 1: Procesamiento GC-FID

**Ubicación**: `Casos/caso1_procesamiento_gc/`

**Comando**:
```bash
cd /home/user/modelo_esterificacion
bash Casos/caso1_procesamiento_gc/ejecutar_caso1.sh
```

**Tiempo esperado**: 3-5 segundos

**Outputs esperados** (en `Casos/caso1_procesamiento_gc/resultados/`):
- `processed_gc_data.csv` - Datos procesados
- `concentrations.png` - Gráfica de concentraciones
- `conversion_curve.png` - Curva de conversión vs tiempo

**Figuras necesarias para el artículo**:
- [ ] `conversion_curve.png` → Copiar a `Paper_ICI/figuras/caso1_conversion.png`

**Captura de pantalla**:
- [ ] Terminal mostrando tiempo de ejecución y resumen de resultados

---

## 🎯 Caso 2: Ajuste de Parámetros

**Ubicación**: `Casos/caso2_ajuste_parametros/`

**Comando**:
```bash
cd /home/user/modelo_esterificacion
bash Casos/caso2_ajuste_parametros/ejecutar_caso2.sh
```

**Tiempo esperado**: 20-30 segundos

**Outputs esperados** (en `Casos/caso2_ajuste_parametros/resultados/`):
- `parametros_calibrados.json` - A, Ea calibrados con IC
- `metricas_ajuste.xlsx` - R², RMSE, MAE
- `ajuste_experimental_vs_modelo.png` - Validación visual
- `analisis_residuales.png` - Normalidad residuales
- `intervalos_confianza.png` - IC 95% para parámetros

**Figuras necesarias para el artículo**:
- [ ] `ajuste_experimental_vs_modelo.png` → Copiar a `Paper_ICI/figuras/caso2_ajuste.png`
- [ ] `intervalos_confianza.png` → Copiar a `Paper_ICI/figuras/caso2_ic.png`

**Datos para tablas**:
- [ ] Abrir `parametros_calibrados.json` y extraer valores de A, Ea, R², RMSE
- [ ] Verificar que R² > 0.98 y RMSE < 5%

---

## 🎯 Caso 3: Optimización

**Ubicación**: `Casos/caso3_optimizacion/`

**Comando**:
```bash
cd /home/user/modelo_esterificacion
bash Casos/caso3_optimizacion/ejecutar_caso3.sh
```

**Tiempo esperado**: 1-3 minutos

**Outputs esperados** (en `Casos/caso3_optimizacion/resultados/`):
- `condiciones_optimas.json` - T, RM, Cat, RPM óptimos
- `superficie_T_vs_RM.png` - Superficie 3D
- `superficie_Cat_vs_RPM.png` - Superficie 3D
- `sensibilidad_parametros.xlsx` - Análisis sensibilidad
- `convergencia_optimizacion.png` - Evolución algoritmo

**Figuras necesarias para el artículo**:
- [ ] `superficie_T_vs_RM.png` → Copiar a `Paper_ICI/figuras/caso3_superficie.png`
- [ ] `convergencia_optimizacion.png` → Copiar a `Paper_ICI/figuras/caso3_convergencia.png`

**Datos para tablas**:
- [ ] Abrir `condiciones_optimas.json` y extraer valores óptimos
- [ ] Verificar que conversión predicha > 99%

---

## 🎯 Caso 4: Comparación de Modelos

**Ubicación**: `Casos/caso4_comparacion_modelos/`

**Comando**:
```bash
cd /home/user/modelo_esterificacion
bash Casos/caso4_comparacion_modelos/ejecutar_caso4.sh
```

**Tiempo esperado**: 5-10 segundos

**Outputs esperados** (en `Casos/caso4_comparacion_modelos/resultados/`):
- `tabla_comparacion.xlsx` - Métricas comparativas
- `perfiles_1paso_vs_3pasos.png` - Superposición perfiles
- `conversion_1paso_vs_3pasos.png` - Curvas comparadas
- `intermediarios_DG_MG.png` - DG, MG en modelo 3-pasos
- `benchmark_tiempo.json` - Tiempos de cómputo

**Figuras necesarias para el artículo**:
- [ ] `perfiles_1paso_vs_3pasos.png` → Copiar a `Paper_ICI/figuras/caso4_perfiles.png`
- [ ] `intermediarios_DG_MG.png` → Copiar a `Paper_ICI/figuras/caso4_intermediarios.png`

**Datos para tablas**:
- [ ] Abrir `tabla_comparacion.xlsx` y verificar diferencia en conversión < 2%
- [ ] Anotar tiempos de cómputo de ambos modelos

---

## 📊 Resumen de Figuras para el Artículo

Copiar las siguientes figuras a `Paper_ICI/figuras/`:

| Figura | Origen | Destino |
|--------|--------|---------|
| Caso 1: Conversión | `Casos/caso1_.../resultados/conversion_curve.png` | `Paper_ICI/figuras/caso1_conversion.png` |
| Caso 2: Ajuste | `Casos/caso2_.../resultados/ajuste_experimental_vs_modelo.png` | `Paper_ICI/figuras/caso2_ajuste.png` |
| Caso 3: Superficie | `Casos/caso3_.../resultados/superficie_T_vs_RM.png` | `Paper_ICI/figuras/caso3_superficie.png` |
| Caso 4: Perfiles | `Casos/caso4_.../resultados/perfiles_1paso_vs_3pasos.png` | `Paper_ICI/figuras/caso4_perfiles.png` |
| Caso 4: Intermediarios | `Casos/caso4_.../resultados/intermediarios_DG_MG.png` | `Paper_ICI/figuras/caso4_intermediarios.png` |

**Comando para copiar todas**:
```bash
cp Casos/caso1_procesamiento_gc/resultados/conversion_curve.png Paper_ICI/figuras/caso1_conversion.png
cp Casos/caso2_ajuste_parametros/resultados/ajuste_experimental_vs_modelo.png Paper_ICI/figuras/caso2_ajuste.png
cp Casos/caso3_optimizacion/resultados/superficie_T_vs_RM.png Paper_ICI/figuras/caso3_superficie.png
cp Casos/caso4_comparacion_modelos/resultados/perfiles_1paso_vs_3pasos.png Paper_ICI/figuras/caso4_perfiles.png
cp Casos/caso4_comparacion_modelos/resultados/intermediarios_DG_MG.png Paper_ICI/figuras/caso4_intermediarios.png
```

---

## 🔍 Validación de Resultados

Después de ejecutar los 4 casos, verificar:

### Caso 1:
- ✅ Conversión final ≈ 92% (esperado: 92.0%)
- ✅ Tiempo de ejecución < 10 segundos
- ✅ No outliers detectados

### Caso 2:
- ✅ R² > 0.98 (objetivo: 0.9844)
- ✅ RMSE < 5% (objetivo: 3.85%)
- ✅ A ≈ 8.0×10⁵ L/(mol·min)
- ✅ Ea ≈ 50 kJ/mol

### Caso 3:
- ✅ Temperatura óptima ≈ 58-60°C
- ✅ Relación molar óptima ≈ 6:1
- ✅ Conversión predicha > 99%
- ✅ Convergencia < 200 iteraciones

### Caso 4:
- ✅ Diferencia conversión (1-paso vs 3-pasos) < 2%
- ✅ Modelo 1-paso 2-4× más rápido
- ✅ Modelo 3-pasos muestra DG, MG

---

## 🐛 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'numpy'`**
```bash
pip install -r requirements.txt
```

**Error: `Permission denied` al ejecutar scripts bash**
```bash
chmod +x Casos/caso*/ejecutar_caso*.sh
```

**Error: `FileNotFoundError` al buscar datos de entrada**
- Verificar que estés en el directorio raíz: `/home/user/modelo_esterificacion`
- Verificar que existan los archivos en `Casos/casoX/datos/`

**Resultados vacíos o incorrectos**
- Verificar que `variables_esterificacion_dataset.json` existe en raíz
- Revisar logs en terminal para errores específicos

---

## 📝 Notas para el Artículo

Después de ejecutar todos los casos, documentar en el artículo:

1. **Tiempos de ejecución reales** (pueden variar ligeramente)
2. **Valores exactos de parámetros calibrados** (A, Ea con decimales)
3. **Condiciones óptimas exactas** (no redondeadas)
4. **Capturas de pantalla** de terminales mostrando ejecuciones exitosas

---

## 📧 Contacto

Para preguntas sobre ejecución de casos:
- J. Salas-García: proyectos@javiersalasg.com
- Repositorio GitHub: https://github.com/JavierSalasGarcia/modelo_esterificacion
