"""
Paquete de controladores para la aplicación Generador de Actas ADIF
Contiene todos los controladores que manejan la lógica de la aplicación
"""

from .controlador_grafica import ControladorGrafica
from .controlador_json import ControladorJson
from .controlador_documentos import ControladorDocumentos
from .controlador_tablas import ControladorTablas
from .Controlador_selector import ContractManagerQt5
from .controlador_archivos_unificado import GestorArchivos
__all__ = [
    'ControladorGrafica',
    'ControladorJson', 
    'ControladorDocumentos',
    'ControladorTablas',
    'ControladorArchivos',
    'ContractManagerQt5',
    'GestorArchivos'
]

__version__ = "3.0.0"