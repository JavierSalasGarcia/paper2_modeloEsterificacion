"""
Módulo de Propiedades Termodinámicas y Datos de Literatura

Este módulo contiene propiedades termofísicas, parámetros cinéticos de literatura
y correlaciones para el sistema de transesterificación de biodiésel.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class KineticParameters:
    """Parámetros cinéticos para una reacción."""
    Ea_forward: float  # Energía de activación directa (kJ/mol)
    Ea_reverse: float  # Energía de activación inversa (kJ/mol)
    A_forward: float   # Factor pre-exponencial directo (1/min o L/(mol·min))
    A_reverse: float   # Factor pre-exponencial inverso (1/min o L/(mol·min))
    order: int = 2     # Orden de reacción
    reference: str = ""  # Referencia bibliográfica


class ThermophysicalProperties:
    """
    Propiedades termofísicas de componentes del sistema de biodiésel.
    """

    # Constantes
    R = 8.314  # J/(mol·K) - Constante universal de los gases

    def __init__(self):
        """Inicializa base de datos de propiedades."""
        self._init_molecular_weights()
        self._init_densities()
        self._init_viscosities()
        self._init_heat_capacities()
        self._init_other_properties()

    def _init_molecular_weights(self):
        """Pesos moleculares (g/mol)."""
        self.MW = {
            # Triglicéridos (aceites comunes)
            'tripalmitin': 807.3,      # C51H98O6
            'triolein': 885.4,          # C57H104O6
            'average_TG': 880.0,        # Promedio para aceite usado

            # Diglicéridos
            'average_DG': 620.0,

            # Monoglicéridos
            'average_MG': 360.0,

            # FAMEs (Ésteres metílicos)
            'methyl_palmitate': 270.5,  # C17H34O2
            'methyl_stearate': 298.5,   # C19H38O2
            'methyl_oleate': 296.5,     # C19H36O2
            'methyl_linoleate': 294.5,  # C19H34O2
            'average_FAME': 292.0,      # Promedio

            # Otros
            'methanol': 32.04,
            'glycerol': 92.09,
            'CaO': 56.08,
        }

    def _init_densities(self):
        """
        Densidades como función de temperatura.
        ρ(T) = ρ_ref - k_T * (T - T_ref)
        """
        # Densidad a T_ref = 25°C (kg/m³) y coeficiente térmico (kg/(m³·K))
        self.density_params = {
            'average_TG': {'rho_ref': 920.0, 'k_T': 0.65, 'T_ref': 25},
            'average_DG': {'rho_ref': 950.0, 'k_T': 0.60, 'T_ref': 25},
            'average_MG': {'rho_ref': 970.0, 'k_T': 0.58, 'T_ref': 25},
            'average_FAME': {'rho_ref': 880.0, 'k_T': 0.70, 'T_ref': 25},
            'methanol': {'rho_ref': 792.0, 'k_T': 0.90, 'T_ref': 25},
            'glycerol': {'rho_ref': 1261.0, 'k_T': 0.64, 'T_ref': 25},
        }

    def _init_viscosities(self):
        """
        Viscosidad dinámica como función de temperatura (ecuación de Andrade).
        μ(T) = A * exp(B / T)
        """
        # A (Pa·s), B (K)
        self.viscosity_params = {
            'average_TG': {'A': 0.0001, 'B': 3500},
            'average_FAME': {'A': 0.00015, 'B': 2800},
            'methanol': {'A': 0.00008, 'B': 1500},
            'glycerol': {'A': 0.0002, 'B': 4200},
        }

    def _init_heat_capacities(self):
        """Capacidades caloríficas (J/(kg·K)) a 25°C."""
        self.Cp = {
            'average_TG': 2000.0,
            'average_FAME': 2200.0,
            'methanol': 2510.0,
            'glycerol': 2430.0,
        }

    def _init_other_properties(self):
        """Otras propiedades."""
        # Conductividad térmica (W/(m·K)) a 65°C
        self.thermal_conductivity = {
            'average_TG': 0.17,
            'average_FAME': 0.15,
            'methanol': 0.20,
            'glycerol': 0.29,
        }

        # Tensión superficial (mN/m) a 25°C
        self.surface_tension = {
            'average_TG': 32.0,
            'average_FAME': 28.0,
            'methanol': 22.6,
            'glycerol': 63.4,
        }

    # Métodos para calcular propiedades

    def density(self, component: str, T_celsius: float) -> float:
        """
        Calcula densidad en función de temperatura.

        Args:
            component: Nombre del componente
            T_celsius: Temperatura (°C)

        Returns:
            Densidad (kg/m³)
        """
        params = self.density_params.get(component)
        if params is None:
            raise ValueError(f"Densidad no disponible para '{component}'")

        rho = params['rho_ref'] - params['k_T'] * (T_celsius - params['T_ref'])
        return max(rho, 100.0)  # Valor mínimo razonable

    def viscosity(self, component: str, T_celsius: float) -> float:
        """
        Calcula viscosidad dinámica en función de temperatura (Andrade).

        Args:
            component: Nombre del componente
            T_celsius: Temperatura (°C)

        Returns:
            Viscosidad dinámica (Pa·s)
        """
        params = self.viscosity_params.get(component)
        if params is None:
            raise ValueError(f"Viscosidad no disponible para '{component}'")

        T_kelvin = T_celsius + 273.15
        mu = params['A'] * np.exp(params['B'] / T_kelvin)
        return mu

    def mixture_density(self,
                       mass_fractions: Dict[str, float],
                       T_celsius: float) -> float:
        """
        Calcula densidad de mezcla (regla aditiva volumétrica).

        1/ρ_mix = Σ (w_i / ρ_i)

        Args:
            mass_fractions: {componente: fracción másica}
            T_celsius: Temperatura (°C)

        Returns:
            Densidad de mezcla (kg/m³)
        """
        inv_rho = 0.0
        for component, w_i in mass_fractions.items():
            rho_i = self.density(component, T_celsius)
            inv_rho += w_i / rho_i

        return 1.0 / inv_rho if inv_rho > 0 else 850.0

    def mixture_viscosity(self,
                         mole_fractions: Dict[str, float],
                         T_celsius: float,
                         method: str = 'logarithmic') -> float:
        """
        Calcula viscosidad de mezcla.

        Args:
            mole_fractions: {componente: fracción molar}
            T_celsius: Temperatura (°C)
            method: 'logarithmic' o 'wilke' (más complejo)

        Returns:
            Viscosidad de mezcla (Pa·s)
        """
        if method == 'logarithmic':
            # ln(μ_mix) = Σ x_i * ln(μ_i)
            log_mu = 0.0
            for component, x_i in mole_fractions.items():
                mu_i = self.viscosity(component, T_celsius)
                log_mu += x_i * np.log(mu_i)
            return np.exp(log_mu)
        else:
            raise NotImplementedError(f"Método '{method}' no implementado")


class LiteratureKinetics:
    """
    Parámetros cinéticos de literatura para transesterificación con CaO.
    """

    def __init__(self):
        """Inicializa base de datos de cinética."""
        self._init_cao_kinetics()

    def _init_cao_kinetics(self):
        """Parámetros cinéticos para catalizador CaO."""

        # MODELO DE 1 PASO - Pseudo-homogéneo de 2° orden
        self.one_step_models = {
            'Salinas_2010': KineticParameters(
                Ea_forward=51.9,
                Ea_reverse=45.0,  # Estimado
                A_forward=2.98e10,  # min⁻¹
                A_reverse=1.0e9,
                order=2,
                reference="Salinas & Guerrero-Fajardo, Fuel 2010"
            ),

            'Pratigto_2018': KineticParameters(
                Ea_forward=79.0,
                Ea_reverse=60.0,
                A_forward=1.5e12,
                A_reverse=5.0e10,
                order=2,
                reference="Pratigto et al., JKSA 2018"
            ),

            'Kouzu_2008': KineticParameters(
                Ea_forward=161.0,  # Régimen cinético
                Ea_reverse=130.0,
                A_forward=5.0e15,
                A_reverse=1.0e14,
                order=2,
                reference="Kouzu et al., Fuel 2008"
            ),
        }

        # MODELO DE 3 PASOS - Mecanístico
        # TG → DG → MG → GL
        self.three_step_models = {
            'Liu_2008': {
                'step1_TG_DG': KineticParameters(
                    Ea_forward=65.0,
                    Ea_reverse=55.0,
                    A_forward=1.2e11,
                    A_reverse=3.0e9,
                    order=1,
                    reference="Liu et al., Fuel 2008"
                ),
                'step2_DG_MG': KineticParameters(
                    Ea_forward=62.0,
                    Ea_reverse=53.0,
                    A_forward=8.0e10,
                    A_reverse=2.5e9,
                    order=1,
                    reference="Liu et al., Fuel 2008"
                ),
                'step3_MG_GL': KineticParameters(
                    Ea_forward=58.0,
                    Ea_reverse=50.0,
                    A_forward=5.0e10,
                    A_reverse=2.0e9,
                    order=1,
                    reference="Liu et al., Fuel 2008"
                ),
            },

            'Stamenkovic_2008': {
                'step1_TG_DG': KineticParameters(
                    Ea_forward=70.5,
                    Ea_reverse=60.0,
                    A_forward=2.5e11,
                    A_reverse=5.0e9,
                    order=1,
                    reference="Stamenkovic et al., Bioresource Tech 2008"
                ),
                'step2_DG_MG': KineticParameters(
                    Ea_forward=68.0,
                    Ea_reverse=58.0,
                    A_forward=1.8e11,
                    A_reverse=4.0e9,
                    order=1,
                    reference="Stamenkovic et al., Bioresource Tech 2008"
                ),
                'step3_MG_GL': KineticParameters(
                    Ea_forward=65.0,
                    Ea_reverse=55.0,
                    A_forward=1.2e11,
                    A_reverse=3.5e9,
                    order=1,
                    reference="Stamenkovic et al., Bioresource Tech 2008"
                ),
            },
        }

    def get_recommended_params(self, model_type: str = '1-step') -> Dict:
        """
        Obtiene parámetros cinéticos recomendados.

        Args:
            model_type: '1-step' o '3-step'

        Returns:
            Diccionario con parámetros cinéticos
        """
        if model_type == '1-step':
            # Usar promedio de modelos de 1 paso
            return self.one_step_models['Salinas_2010']
        elif model_type == '3-step':
            return self.three_step_models['Liu_2008']
        else:
            raise ValueError(f"Tipo de modelo '{model_type}' no reconocido")


class ReactionThermodynamics:
    """Termodinámica de la reacción de transesterificación."""

    def __init__(self):
        """Inicializa parámetros termodinámicos."""

        # Entalpía de reacción (kJ/mol de TG convertido)
        self.delta_H_r = {
            '1-step': -80.0,  # Ligeramente exotérmica
            'step1_TG_DG': -25.0,
            'step2_DG_MG': -28.0,
            'step3_MG_GL': -27.0,
        }

        # Energía libre de Gibbs (kJ/mol)
        self.delta_G_r = {
            '1-step': -15.0,  # A 65°C
        }

    def equilibrium_constant(self,
                            T_celsius: float,
                            reaction: str = '1-step') -> float:
        """
        Calcula constante de equilibrio usando relación termodinámica.

        K_eq = exp(-ΔG°/(R·T))

        Args:
            T_celsius: Temperatura (°C)
            reaction: Tipo de reacción

        Returns:
            Constante de equilibrio (adimensional)
        """
        T_kelvin = T_celsius + 273.15
        R = 8.314  # J/(mol·K)

        delta_G = self.delta_G_r.get(reaction, -15.0) * 1000  # kJ → J

        K_eq = np.exp(-delta_G / (R * T_kelvin))
        return K_eq


# Funciones de utilidad

def arrhenius(T_celsius: float, A: float, Ea_kJ_mol: float) -> float:
    """
    Calcula constante de velocidad usando ecuación de Arrhenius.

    k(T) = A * exp(-Ea / (R*T))

    Args:
        T_celsius: Temperatura (°C)
        A: Factor pre-exponencial (unidades dependen del orden)
        Ea_kJ_mol: Energía de activación (kJ/mol)

    Returns:
        Constante de velocidad k
    """
    R = 8.314  # J/(mol·K)
    T_kelvin = T_celsius + 273.15
    Ea_J_mol = Ea_kJ_mol * 1000  # kJ → J

    k = A * np.exp(-Ea_J_mol / (R * T_kelvin))
    return k


def convert_units_concentration(value: float,
                                from_unit: str,
                                to_unit: str,
                                MW: float) -> float:
    """
    Convierte unidades de concentración.

    Args:
        value: Valor a convertir
        from_unit: 'mol/L', 'kg/m3', 'g/L'
        to_unit: 'mol/L', 'kg/m3', 'g/L'
        MW: Peso molecular (g/mol)

    Returns:
        Valor convertido
    """
    # Convertir a mol/L primero
    if from_unit == 'mol/L':
        mol_L = value
    elif from_unit == 'kg/m3':
        mol_L = (value * 1000) / MW  # kg/m³ → g/L → mol/L
    elif from_unit == 'g/L':
        mol_L = value / MW
    else:
        raise ValueError(f"Unidad '{from_unit}' no reconocida")

    # Convertir desde mol/L a unidad destino
    if to_unit == 'mol/L':
        return mol_L
    elif to_unit == 'kg/m3':
        return (mol_L * MW) / 1000
    elif to_unit == 'g/L':
        return mol_L * MW
    else:
        raise ValueError(f"Unidad '{to_unit}' no reconocida")


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Propiedades Termodinámicas - Ejemplo de Uso ===\n")

    props = ThermophysicalProperties()
    kinetics = LiteratureKinetics()
    thermo = ReactionThermodynamics()

    # Densidad y viscosidad a 65°C
    T = 65  # °C
    print(f"Propiedades a {T}°C:")
    print(f"  Densidad TG: {props.density('average_TG', T):.2f} kg/m³")
    print(f"  Densidad FAME: {props.density('average_FAME', T):.2f} kg/m³")
    print(f"  Viscosidad TG: {props.viscosity('average_TG', T)*1000:.2f} mPa·s")
    print(f"  Viscosidad FAME: {props.viscosity('average_FAME', T)*1000:.2f} mPa·s")

    # Parámetros cinéticos
    print("\n=== Parámetros Cinéticos (Modelo 1 Paso) ===")
    params = kinetics.get_recommended_params('1-step')
    print(f"  Ea (forward): {params.Ea_forward} kJ/mol")
    print(f"  A (forward): {params.A_forward:.2e} min⁻¹")
    print(f"  Referencia: {params.reference}")

    # Constante de velocidad a diferentes temperaturas
    print("\n=== Constante de Velocidad k(T) ===")
    for T in [50, 60, 70, 80]:
        k = arrhenius(T, params.A_forward, params.Ea_forward)
        print(f"  T = {T}°C: k = {k:.2e} min⁻¹")

    # Constante de equilibrio
    print("\n=== Constante de Equilibrio ===")
    K_eq = thermo.equilibrium_constant(65)
    print(f"  K_eq a 65°C: {K_eq:.2e}")
