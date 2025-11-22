"""
Módulo de Visualización de Resultados

Genera gráficas para análisis de resultados de transesterificación.

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from mpl_toolkits.mplot3d import Axes3D


class ResultsPlotter:
    """Generador de gráficas para resultados de transesterificación."""

    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """Inicializa el plotter con estilo."""
        try:
            plt.style.use(style)
        except:
            pass  # Usar estilo por defecto si falla

        sns.set_palette("husl")
        self.figures = []

    def plot_conversion_vs_time(self,
                               results_dict: Dict,
                               labels: Optional[List[str]] = None,
                               experimental_data: Optional[Dict] = None,
                               save_path: Optional[str] = None):
        """
        Plotea conversión vs tiempo para uno o más modelos.

        Args:
            results_dict: {label: results}
            labels: Etiquetas personalizadas
            experimental_data: Datos experimentales {'t': [...], 'conversion': [...]}
            save_path: Ruta para guardar figura
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, (label, results) in enumerate(results_dict.items()):
            ax.plot(results['t'], results['conversion_%'],
                   label=labels[i] if labels else label,
                   linewidth=2, marker='o', markersize=4)

        if experimental_data:
            ax.scatter(experimental_data['t'], experimental_data['conversion'],
                      color='black', s=100, marker='s', label='Experimental',
                      zorder=10)

        ax.set_xlabel('Tiempo (min)', fontsize=12)
        ax.set_ylabel('Conversión (%)', fontsize=12)
        ax.set_title('Conversión de Triglicéridos vs Tiempo', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(0, 100)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        self.figures.append(fig)
        return fig

    def plot_concentration_profiles(self, results: Dict, save_path: Optional[str] = None):
        """Plotea perfiles de concentración de todas las especies."""
        fig, ax = plt.subplots(figsize=(12, 6))

        species = [k for k in results.keys() if k.startswith('C_')]

        for sp in species:
            label = sp.replace('C_', '')
            ax.plot(results['t'], results[sp], label=label, linewidth=2, marker='o', markersize=3)

        ax.set_xlabel('Tiempo (min)', fontsize=12)
        ax.set_ylabel('Concentración (mol/L)', fontsize=12)
        ax.set_title('Perfiles de Concentración', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        self.figures.append(fig)
        return fig

    def plot_parity(self, y_true: np.ndarray, y_pred: np.ndarray,
                   labels: Tuple[str, str] = ('Modelo 1', 'Modelo 2'),
                   save_path: Optional[str] = None):
        """Genera parity plot."""
        fig, ax = plt.subplots(figsize=(8, 8))

        ax.scatter(y_true, y_pred, alpha=0.6, s=50, edgecolors='k')

        # Línea de paridad
        max_val = max(y_true.max(), y_pred.max())
        min_val = min(y_true.min(), y_pred.min())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2, label='Paridad')

        # Bandas ±10%
        ax.fill_between([min_val, max_val],
                       [min_val*0.9, max_val*0.9],
                       [min_val*1.1, max_val*1.1],
                       alpha=0.2, color='gray', label='±10%')

        ax.set_xlabel(labels[0], fontsize=12)
        ax.set_ylabel(labels[1], fontsize=12)
        ax.set_title('Parity Plot', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_aspect('equal')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        self.figures.append(fig)
        return fig

    def plot_response_surface(self, surface_data: Dict, save_path: Optional[str] = None):
        """Genera superficie de respuesta 3D."""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        var1_name = [k for k in surface_data.keys() if k not in ['conversion_%', 'FAME_yield_%', 'fixed_vars']][0]
        var2_name = [k for k in surface_data.keys() if k not in ['conversion_%', 'FAME_yield_%', 'fixed_vars', var1_name]][0]

        X = surface_data[var1_name]
        Y = surface_data[var2_name]
        Z = surface_data['conversion_%']

        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        ax.contour(X, Y, Z, zdir='z', offset=Z.min(), cmap='viridis', alpha=0.5)

        ax.set_xlabel(var1_name.replace('_', ' ').title(), fontsize=10)
        ax.set_ylabel(var2_name.replace('_', ' ').title(), fontsize=10)
        ax.set_zlabel('Conversión (%)', fontsize=10)
        ax.set_title('Superficie de Respuesta', fontsize=14, fontweight='bold')

        fig.colorbar(surf, ax=ax, shrink=0.5)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        self.figures.append(fig)
        return fig

    def close_all(self):
        """Cierra todas las figuras."""
        for fig in self.figures:
            plt.close(fig)
        self.figures = []
