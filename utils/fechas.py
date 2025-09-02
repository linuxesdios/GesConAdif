"""
Utilidades de fechas centralizadas
Manejo de fechas PyQt5, formateo español, conversiones
"""

from datetime import datetime, date
from typing import Optional

def formatear_fecha_espanol(fecha: date, formato: str = "completo") -> str:
    """Formatea fecha en español"""
    if formato == "corto":
        return fecha.strftime("%d/%m/%Y")
    elif formato == "iso":
        return fecha.strftime("%Y-%m-%d")
    else:  # completo
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"

def convertir_qdate_a_python(qdate) -> Optional[date]:
    """Convierte QDate a date de Python"""
    try:
        from PyQt5.QtCore import QDate
        if isinstance(qdate, QDate) and qdate.isValid():
            return date(qdate.year(), qdate.month(), qdate.day())
        return None
    except ImportError:
        return None

def convertir_python_a_qdate(fecha: date):
    """Convierte date de Python a QDate"""
    try:
        from PyQt5.QtCore import QDate
        return QDate(fecha.year, fecha.month, fecha.day)
    except ImportError:
        return None