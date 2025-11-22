"""
Módulo de Modelos Cinéticos para Transesterificación de Biodiésel

Implementa modelos cinéticos de 1 paso (simplificado) y 3 pasos (mecanístico)
para la reacción de transesterificación catalizada por CaO.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Optional, Callable
import warnings

from .properties import ThermophysicalProperties, LiteratureKinetics, arrhenius


class KineticModel:
    """
    Clase base para modelos cinéticos de transesterificación.

    Attributes:
        model_type (str): Tipo de modelo ('1-step' o '3-step')
        reversible (bool): Si el modelo considera reversibilidad
        params (Dict): Parámetros cinéticos (Ea, A para cada reacción)
        properties (ThermophysicalProperties): Propiedades del sistema
    """

    def __init__(self,
                 model_type: str = '1-step',
                 reversible: bool = True,
                 kinetic_params: Optional[Dict] = None,
                 temperature: float = 65.0):
        """
        Inicializa el modelo cinético.

        Args:
            model_type: Tipo de modelo ('1-step' o '3-step')
            reversible: Si considerar reacciones reversibles
            kinetic_params: Parámetros cinéticos personalizados
            temperature: Temperatura de operación (°C)
        """
        if model_type not in ['1-step', '3-step']:
            raise ValueError("model_type debe ser '1-step' o '3-step'")

        self.model_type = model_type
        self.reversible = reversible
        self.temperature = temperature

        # Inicializar propiedades y cinética de literatura
        self.properties = ThermophysicalProperties()
        self.lit_kinetics = LiteratureKinetics()

        # Cargar parámetros cinéticos
        if kinetic_params is None:
            self.params = self._load_default_params()
        else:
            self.params = kinetic_params

        # Constantes de velocidad actuales (se actualizan con temperatura)
        self.k = {}
        self._update_rate_constants(temperature)

    def _load_default_params(self) -> Dict:
        """Carga parámetros cinéticos por defecto de literatura."""
        if self.model_type == '1-step':
            # Usar modelo de Salinas 2010 por defecto
            params_obj = self.lit_kinetics.one_step_models['Salinas_2010']
            return {
                'Ea_forward': params_obj.Ea_forward,
                'Ea_reverse': params_obj.Ea_reverse,
                'A_forward': params_obj.A_forward,
                'A_reverse': params_obj.A_reverse,
            }
        else:  # 3-step
            # Usar modelo de Liu 2008 por defecto
            model = self.lit_kinetics.three_step_models['Liu_2008']
            return {
                'step1': {
                    'Ea_forward': model['step1_TG_DG'].Ea_forward,
                    'Ea_reverse': model['step1_TG_DG'].Ea_reverse,
                    'A_forward': model['step1_TG_DG'].A_forward,
                    'A_reverse': model['step1_TG_DG'].A_reverse,
                },
                'step2': {
                    'Ea_forward': model['step2_DG_MG'].Ea_forward,
                    'Ea_reverse': model['step2_DG_MG'].Ea_reverse,
                    'A_forward': model['step2_DG_MG'].A_forward,
                    'A_reverse': model['step2_DG_MG'].A_reverse,
                },
                'step3': {
                    'Ea_forward': model['step3_MG_GL'].Ea_forward,
                    'Ea_reverse': model['step3_MG_GL'].Ea_reverse,
                    'A_forward': model['step3_MG_GL'].A_forward,
                    'A_reverse': model['step3_MG_GL'].A_reverse,
                },
            }

    def _update_rate_constants(self, T_celsius: float):
        """
        Actualiza constantes de velocidad usando Arrhenius.

        Args:
            T_celsius: Temperatura (°C)
        """
        self.temperature = T_celsius

        if self.model_type == '1-step':
            self.k['forward'] = arrhenius(
                T_celsius,
                self.params['A_forward'],
                self.params['Ea_forward']
            )
            if self.reversible:
                self.k['reverse'] = arrhenius(
                    T_celsius,
                    self.params['A_reverse'],
                    self.params['Ea_reverse']
                )
        else:  # 3-step
            for step in ['step1', 'step2', 'step3']:
                self.k[f'{step}_forward'] = arrhenius(
                    T_celsius,
                    self.params[step]['A_forward'],
                    self.params[step]['Ea_forward']
                )
                if self.reversible:
                    self.k[f'{step}_reverse'] = arrhenius(
                        T_celsius,
                        self.params[step]['A_reverse'],
                        self.params[step]['Ea_reverse']
                    )

    def set_temperature(self, T_celsius: float):
        """
        Establece nueva temperatura y actualiza constantes de velocidad.

        Args:
            T_celsius: Nueva temperatura (°C)
        """
        self._update_rate_constants(T_celsius)

    def odes(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Sistema de ecuaciones diferenciales ordinarias.

        Args:
            t: Tiempo (min)
            y: Vector de concentraciones

        Returns:
            dydt: Derivadas de concentraciones
        """
        if self.model_type == '1-step':
            return self._odes_1step(t, y)
        else:
            return self._odes_3step(t, y)

    def _odes_1step(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        EDOs para modelo de 1 paso.

        Reacción: TG + 3 MeOH ⇌ 3 FAME + GL

        y = [C_TG, C_MeOH, C_FAME, C_GL]
        """
        C_TG, C_MeOH, C_FAME, C_GL = y

        # Evitar concentraciones negativas
        C_TG = max(0, C_TG)
        C_MeOH = max(0, C_MeOH)
        C_FAME = max(0, C_FAME)
        C_GL = max(0, C_GL)

        # Velocidad de reacción (pseudo-2° orden)
        r_forward = self.k['forward'] * C_TG * C_MeOH

        r_reverse = 0.0
        if self.reversible:
            r_reverse = self.k['reverse'] * (C_FAME ** 3) * C_GL

        r_net = r_forward - r_reverse

        # Balances de materia
        dC_TG_dt = -r_net
        dC_MeOH_dt = -3.0 * r_net
        dC_FAME_dt = 3.0 * r_net
        dC_GL_dt = r_net

        return np.array([dC_TG_dt, dC_MeOH_dt, dC_FAME_dt, dC_GL_dt])

    def _odes_3step(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        EDOs para modelo de 3 pasos.

        Reacciones:
        1) TG + MeOH ⇌ DG + FAME
        2) DG + MeOH ⇌ MG + FAME
        3) MG + MeOH ⇌ GL + FAME

        y = [C_TG, C_DG, C_MG, C_GL, C_FAME, C_MeOH]
        """
        C_TG, C_DG, C_MG, C_GL, C_FAME, C_MeOH = y

        # Evitar concentraciones negativas
        C_TG = max(0, C_TG)
        C_DG = max(0, C_DG)
        C_MG = max(0, C_MG)
        C_GL = max(0, C_GL)
        C_FAME = max(0, C_FAME)
        C_MeOH = max(0, C_MeOH)

        # Velocidades de cada paso
        # Paso 1: TG + MeOH ⇌ DG + FAME
        r1_forward = self.k['step1_forward'] * C_TG * C_MeOH
        r1_reverse = 0.0
        if self.reversible:
            r1_reverse = self.k['step1_reverse'] * C_DG * C_FAME
        r1_net = r1_forward - r1_reverse

        # Paso 2: DG + MeOH ⇌ MG + FAME
        r2_forward = self.k['step2_forward'] * C_DG * C_MeOH
        r2_reverse = 0.0
        if self.reversible:
            r2_reverse = self.k['step2_reverse'] * C_MG * C_FAME
        r2_net = r2_forward - r2_reverse

        # Paso 3: MG + MeOH ⇌ GL + FAME
        r3_forward = self.k['step3_forward'] * C_MG * C_MeOH
        r3_reverse = 0.0
        if self.reversible:
            r3_reverse = self.k['step3_reverse'] * C_GL * C_FAME
        r3_net = r3_forward - r3_reverse

        # Balances de materia
        dC_TG_dt = -r1_net
        dC_DG_dt = r1_net - r2_net
        dC_MG_dt = r2_net - r3_net
        dC_GL_dt = r3_net
        dC_FAME_dt = r1_net + r2_net + r3_net
        dC_MeOH_dt = -(r1_net + r2_net + r3_net)

        return np.array([dC_TG_dt, dC_DG_dt, dC_MG_dt, dC_GL_dt, dC_FAME_dt, dC_MeOH_dt])

    def simulate(self,
                 t_span: Tuple[float, float],
                 C0: Dict[str, float],
                 method: str = 'Radau',
                 t_eval: Optional[np.ndarray] = None,
                 rtol: float = 1e-6,
                 atol: float = 1e-8) -> Dict:
        """
        Simula la cinética de reacción integrando las EDOs.

        Args:
            t_span: Tupla (t_initial, t_final) en minutos
            C0: Condiciones iniciales {componente: concentración (mol/L)}
            method: Método de integración ('Radau', 'BDF', 'LSODA')
            t_eval: Tiempos específicos para evaluar la solución
            rtol: Tolerancia relativa
            atol: Tolerancia absoluta

        Returns:
            Dict con resultados de la simulación
        """
        # Preparar vector de condiciones iniciales
        if self.model_type == '1-step':
            y0 = np.array([
                C0.get('TG', 0),
                C0.get('MeOH', 0),
                C0.get('FAME', 0),
                C0.get('GL', 0),
            ])
            species_names = ['TG', 'MeOH', 'FAME', 'GL']
        else:  # 3-step
            y0 = np.array([
                C0.get('TG', 0),
                C0.get('DG', 0),
                C0.get('MG', 0),
                C0.get('GL', 0),
                C0.get('FAME', 0),
                C0.get('MeOH', 0),
            ])
            species_names = ['TG', 'DG', 'MG', 'GL', 'FAME', 'MeOH']

        # Integrar EDOs
        solution = solve_ivp(
            fun=self.odes,
            t_span=t_span,
            y0=y0,
            method=method,
            t_eval=t_eval,
            rtol=rtol,
            atol=atol,
            dense_output=True
        )

        if not solution.success:
            warnings.warn(f"Integración falló: {solution.message}")

        # Organizar resultados
        results = {
            't': solution.t,
            'success': solution.success,
            'message': solution.message,
            'nfev': solution.nfev,  # Número de evaluaciones de función
        }

        # Agregar concentraciones por especie
        for i, species in enumerate(species_names):
            results[f'C_{species}'] = solution.y[i]

        # Calcular conversión y rendimiento
        C_TG0 = C0.get('TG', 0)
        if C_TG0 > 0:
            results['conversion_%'] = (C_TG0 - results['C_TG']) / C_TG0 * 100
            results['FAME_yield_%'] = results['C_FAME'] / (3.0 * C_TG0) * 100

        return results

    def calculate_equilibrium(self, C0: Dict[str, float], T_celsius: Optional[float] = None) -> Dict:
        """
        Calcula concentraciones de equilibrio (simulación a tiempo largo).

        Args:
            C0: Condiciones iniciales
            T_celsius: Temperatura (°C), si None usa la actual

        Returns:
            Concentraciones de equilibrio
        """
        if T_celsius is not None:
            self.set_temperature(T_celsius)

        # Simular hasta t = 10000 min (tiempo muy largo)
        results = self.simulate(
            t_span=(0, 10000),
            C0=C0,
            method='Radau'
        )

        # Extraer valores finales
        equilibrium = {}
        for key, value in results.items():
            if key.startswith('C_') or key.endswith('_%'):
                if isinstance(value, np.ndarray):
                    equilibrium[key] = value[-1]

        equilibrium['t_equilibrium'] = results['t'][-1]
        equilibrium['temperature'] = self.temperature

        return equilibrium

    def sensitivity_analysis(self,
                           t_span: Tuple[float, float],
                           C0: Dict[str, float],
                           param_name: str,
                           perturbation: float = 0.01) -> Dict:
        """
        Análisis de sensibilidad local para un parámetro.

        S = (dY/Y) / (dP/P) ≈ (ΔY/Y) / (ΔP/P)

        Args:
            t_span: Rango de tiempo
            C0: Condiciones iniciales
            param_name: Nombre del parámetro (ej. 'Ea_forward', 'A_forward')
            perturbation: Fracción de perturbación (default 1%)

        Returns:
            Diccionario con sensibilidades para cada especie
        """
        # Simulación base
        results_base = self.simulate(t_span, C0)

        # Guardar parámetro original
        if self.model_type == '1-step':
            original_value = self.params[param_name]
        else:
            # Para 3-step, asumir formato 'step1_Ea_forward'
            step, param = param_name.split('_', 1)
            original_value = self.params[step][param]

        # Perturbar parámetro
        perturbed_value = original_value * (1 + perturbation)

        if self.model_type == '1-step':
            self.params[param_name] = perturbed_value
        else:
            self.params[step][param] = perturbed_value

        # Actualizar constantes de velocidad
        self._update_rate_constants(self.temperature)

        # Simulación perturbada
        results_pert = self.simulate(t_span, C0, t_eval=results_base['t'])

        # Restaurar parámetro original
        if self.model_type == '1-step':
            self.params[param_name] = original_value
        else:
            self.params[step][param] = original_value
        self._update_rate_constants(self.temperature)

        # Calcular sensibilidades
        sensitivities = {'t': results_base['t']}

        for key in results_base.keys():
            if key.startswith('C_'):
                Y_base = results_base[key]
                Y_pert = results_pert[key]

                # Evitar división por cero
                with np.errstate(divide='ignore', invalid='ignore'):
                    S = ((Y_pert - Y_base) / Y_base) / perturbation
                    S = np.nan_to_num(S, nan=0.0, posinf=0.0, neginf=0.0)

                sensitivities[f'S_{key}'] = S

        return sensitivities

    def get_info(self) -> Dict:
        """Retorna información del modelo."""
        info = {
            'model_type': self.model_type,
            'reversible': self.reversible,
            'temperature': self.temperature,
            'rate_constants': self.k.copy(),
            'parameters': self.params.copy(),
        }
        return info


# Funciones auxiliares

def batch_reactor(model: KineticModel,
                  V_reactor: float,
                  n0: Dict[str, float],
                  t_span: Tuple[float, float],
                  **kwargs) -> Dict:
    """
    Simula un reactor batch a partir de moles iniciales.

    Args:
        model: Instancia de KineticModel
        V_reactor: Volumen del reactor (L)
        n0: Moles iniciales {componente: moles}
        t_span: Rango de tiempo (min)
        **kwargs: Argumentos adicionales para simulate()

    Returns:
        Resultados de la simulación
    """
    # Convertir moles a concentraciones
    C0 = {component: moles / V_reactor for component, moles in n0.items()}

    # Simular
    results = model.simulate(t_span, C0, **kwargs)

    # Agregar información del reactor
    results['V_reactor'] = V_reactor
    results['n0'] = n0

    return results


def residence_time_distribution(model: KineticModel,
                                C0: Dict[str, float],
                                tau_mean: float,
                                num_points: int = 100) -> Dict:
    """
    Calcula la distribución de tiempos de residencia (RTD) para un CSTR.

    Para CSTR ideal: E(t) = (1/τ) * exp(-t/τ)

    Args:
        model: Instancia de KineticModel
        C0: Concentraciones de entrada
        tau_mean: Tiempo de residencia promedio (min)
        num_points: Número de puntos para integración

    Returns:
        Distribución de concentraciones de salida
    """
    t_max = 5 * tau_mean  # 5 veces tau para cubrir >99%
    t_values = np.linspace(0, t_max, num_points)

    # Función RTD para CSTR ideal
    E_t = (1 / tau_mean) * np.exp(-t_values / tau_mean)

    # Simular para cada tiempo
    C_out = {key: 0.0 for key in C0.keys()}

    for i, t in enumerate(t_values):
        if t == 0:
            continue

        # Simular hasta tiempo t
        result = model.simulate((0, t), C0)

        # Ponderar por RTD
        weight = E_t[i] * (t_values[1] - t_values[0] if i < len(t_values) - 1 else 0)

        for key in C_out.keys():
            if f'C_{key}' in result:
                C_out[key] += result[f'C_{key}'][-1] * weight

    return {
        't_values': t_values,
        'E_t': E_t,
        'C_out': C_out,
        'tau_mean': tau_mean
    }


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Modelo Cinético - Ejemplo de Uso ===\n")

    # Crear modelo de 1 paso
    model_1step = KineticModel(model_type='1-step', reversible=True, temperature=65)

    print(f"Modelo: {model_1step.model_type}")
    print(f"Temperatura: {model_1step.temperature}°C")
    print(f"k_forward: {model_1step.k['forward']:.4e} L/(mol·min)")
    print(f"k_reverse: {model_1step.k['reverse']:.4e} (L/mol)³/min")

    # Condiciones iniciales
    C0 = {
        'TG': 0.5,      # mol/L
        'MeOH': 4.5,    # Relación molar 9:1 (3x estequiométrico)
        'FAME': 0.0,
        'GL': 0.0,
    }

    # Simular
    print("\n=== Simulación (0-120 min) ===")
    results = model_1step.simulate(
        t_span=(0, 120),
        C0=C0,
        t_eval=np.linspace(0, 120, 13)  # Cada 10 min
    )

    print(f"Convergencia: {results['success']}")
    print(f"Evaluaciones de función: {results['nfev']}")

    print("\nResultados:")
    for i, t in enumerate(results['t']):
        print(f"t={t:5.0f} min: C_TG={results['C_TG'][i]:.4f} mol/L, "
              f"Conversión={results['conversion_%'][i]:5.1f}%, "
              f"Rendimiento FAME={results['FAME_yield_%'][i]:5.1f}%")

    # Modelo de 3 pasos
    print("\n\n=== Modelo 3 Pasos ===")
    model_3step = KineticModel(model_type='3-step', reversible=True, temperature=65)

    C0_3step = {
        'TG': 0.5,
        'DG': 0.0,
        'MG': 0.0,
        'GL': 0.0,
        'FAME': 0.0,
        'MeOH': 4.5,
    }

    results_3step = model_3step.simulate(
        t_span=(0, 120),
        C0=C0_3step,
        t_eval=np.array([0, 30, 60, 90, 120])
    )

    print("\nConcentraciones intermedias:")
    for i, t in enumerate(results_3step['t']):
        print(f"t={t:5.0f} min: TG={results_3step['C_TG'][i]:.3f}, "
              f"DG={results_3step['C_DG'][i]:.3f}, "
              f"MG={results_3step['C_MG'][i]:.3f}, "
              f"GL={results_3step['C_GL'][i]:.3f}")
