"""
Imports comunes centralizados
Reduce la duplicación de imports repetidos en múltiples módulos
"""

# =================== IMPORTS DE PYQT5 ===================
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QSpinBox,
    QDoubleSpinBox, QTextEdit, QPlainTextEdit, QTableWidget, QTreeWidget,
    QListWidget, QTabWidget, QGroupBox, QFrame, QSplitter,
    QMenuBar, QToolBar, QStatusBar, QProgressBar,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QCheckBox, QRadioButton, QSlider, QScrollArea,
    QSizePolicy, QGraphicsView, QGraphicsScene
)

from PyQt5.QtCore import (
    Qt, QThread, QTimer, QDate, QTime, QDateTime, QUrl,
    QObject, QEvent, QSize, QPoint, QRect,
    pyqtSignal, pyqtSlot, QPropertyAnimation, QEasingCurve
)

from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QBrush, QPen, QLinearGradient, QRadialGradient,
    QKeySequence, QCursor, QValidator, QRegExpValidator
)

# =================== IMPORTS DE PYTHON ESTÁNDAR ===================
import os
import sys
import json
import traceback
import time
import datetime
import re
import shutil
import subprocess
import webbrowser
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, date, time
from dataclasses import dataclass, field
from enum import Enum

# =================== IMPORTS DE TERCEROS ===================
try:
    import openpyxl
    from openpyxl import Workbook, load_workbook
    OPENPYXL_DISPONIBLE = True
except ImportError:
    OPENPYXL_DISPONIBLE = False

try:
    import docx2pdf
    DOCX2PDF_DISPONIBLE = True
except ImportError:
    DOCX2PDF_DISPONIBLE = False

try:
    from lxml import etree
    LXML_DISPONIBLE = True
except ImportError:
    LXML_DISPONIBLE = False

# =================== IMPORTS DE LA APLICACIÓN ===================
try:
    from modelos_py import (
        Proyecto, DatosContrato, Empresa, Oferta, DatosLiquidacion,
        TipoContrato, EstadoOferta, Constantes
    )
    MODELOS_DISPONIBLE = True
except ImportError:
    MODELOS_DISPONIBLE = False

try:
    from helpers_py import (
        resource_path, abrir_archivo, abrir_carpeta, crear_carpeta_si_no_existe,
        formatear_numero_espanol, parsear_numero_espanol, validar_nif_basico,
        validar_email_basico, es_numero_valido
    )
    HELPERS_DISPONIBLE = True
except ImportError:
    HELPERS_DISPONIBLE = False

try:
    from utils import (
        calcular_iva, calcular_total_con_iva, formatear_euro_espanol,
        validar_datos_empresa, crear_copia_respaldo
    )
    UTILS_DISPONIBLE = True
except ImportError:
    UTILS_DISPONIBLE = False

# =================== FUNCIONES DE UTILIDAD ===================

def verificar_dependencias() -> Dict[str, bool]:
    """Verificar qué dependencias están disponibles"""
    return {
        'openpyxl': OPENPYXL_DISPONIBLE,
        'docx2pdf': DOCX2PDF_DISPONIBLE,
        'lxml': LXML_DISPONIBLE,
        'modelos': MODELOS_DISPONIBLE,
        'helpers': HELPERS_DISPONIBLE,
        'utils': UTILS_DISPONIBLE
    }

def mostrar_estado_dependencias():
    """Mostrar estado de todas las dependencias"""
    dependencias = verificar_dependencias()
    print("[imports_comunes] Estado de dependencias:")
    for nombre, disponible in dependencias.items():
        estado = "✅" if disponible else "❌"
        print(f"  {estado} {nombre}")

# =================== CONFIGURACIÓN GLOBAL ===================

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configurar Qt para alta resolución
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)