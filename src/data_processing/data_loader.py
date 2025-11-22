"""
Módulo de Carga de Datos desde JSON

Carga y valida datos experimentales desde variables_esterificacion_dataset.json

Author: Salas-García, J., et. al
Date: 2025-11-19
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path


class DataLoader:
    """Cargador y validador de datos experimentales."""

    def __init__(self, filepath: Optional[str] = None):
        """
        Inicializa el cargador de datos.

        Args:
            filepath: Ruta al archivo JSON (opcional)
        """
        self.filepath = filepath
        self.data = None
        self.variables_info = None

    def load_json(self, filepath: Optional[str] = None) -> Dict:
        """
        Carga datos desde archivo JSON.

        Args:
            filepath: Ruta al archivo (si None, usa self.filepath)

        Returns:
            Diccionario con datos cargados
        """
        if filepath:
            self.filepath = filepath

        if not self.filepath:
            raise ValueError("Debe proporcionar filepath")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        return self.data

    def load_variables_schema(self) -> pd.DataFrame:
        """
        Carga esquema de variables desde JSON.

        Returns:
            DataFrame con información de variables
        """
        if self.data is None:
            raise ValueError("Debe cargar datos primero con load_json()")

        if 'variables' in self.data:
            self.variables_info = pd.DataFrame(self.data['variables'])
        else:
            # Inferir del propio dataset
            self.variables_info = pd.DataFrame([
                {'name': key, 'category': 'unknown'}
                for key in self.data.keys()
            ])

        return self.variables_info

    def extract_experiment_data(self, experiment_id: Optional[str] = None) -> Dict:
        """
        Extrae datos de un experimento específico.

        Args:
            experiment_id: ID del experimento (si None, retorna primer experimento)

        Returns:
            Diccionario con datos del experimento
        """
        if 'experiments' in self.data:
            experiments = self.data['experiments']
            if experiment_id:
                exp = [e for e in experiments if e.get('id') == experiment_id]
                if not exp:
                    raise ValueError(f"Experimento '{experiment_id}' no encontrado")
                return exp[0]
            else:
                return experiments[0]
        else:
            return self.data

    def get_by_category(self, category: str) -> Dict:
        """
        Obtiene variables de una categoría específica.

        Args:
            category: Nombre de categoría ('reactivos', 'condiciones_reaccion', etc.)

        Returns:
            Diccionario con variables de esa categoría
        """
        if self.variables_info is None:
            self.load_variables_schema()

        vars_in_category = self.variables_info[
            self.variables_info['category'] == category
        ]['name'].tolist()

        return {var: self.data.get(var) for var in vars_in_category}


if __name__ == "__main__":
    print("=== Data Loader - Ejemplo ===\n")

    # Crear loader
    loader = DataLoader()

    # Cargar datos de ejemplo
    example_file = "variables_esterificacion_dataset.json"

    try:
        data = loader.load_json(example_file)
        print(f"Datos cargados: {len(data)} entradas")

        # Cargar esquema de variables
        schema = loader.load_variables_schema()
        print(f"\nVariables: {len(schema)}")
        print(schema[['name', 'category', 'unit']].head())

    except FileNotFoundError:
        print(f"Archivo '{example_file}' no encontrado")
