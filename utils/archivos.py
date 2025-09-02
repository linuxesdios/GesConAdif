"""
Utilidades de archivos centralizadas
Operaciones comunes de archivos, backups, creación de directorios
"""

import os
import shutil
import json
from datetime import datetime
from typing import Optional, Dict, Any

def crear_copia_respaldo(ruta_archivo: str, directorio_respaldos: str = None) -> str:
    """Crea copia de respaldo con timestamp"""
    try:
        if not os.path.exists(ruta_archivo):
            return ""
        
        if not directorio_respaldos:
            proyecto_dir = os.path.dirname(ruta_archivo)
            directorio_respaldos = os.path.join(proyecto_dir, "9_Guardado_seguridad")
        
        os.makedirs(directorio_respaldos, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_base, extension = os.path.splitext(nombre_archivo)
        nombre_respaldo = f"{nombre_base}_backup_{timestamp}{extension}"
        
        ruta_respaldo = os.path.join(directorio_respaldos, nombre_respaldo)
        shutil.copy2(ruta_archivo, ruta_respaldo)
        
        return ruta_respaldo
    except Exception:
        return ""

def cargar_json_seguro(ruta_archivo: str) -> Optional[Dict[str, Any]]:
    """Carga archivo JSON de forma segura"""
    try:
        if not os.path.exists(ruta_archivo):
            return None
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return None

def guardar_json_seguro(datos: Dict[str, Any], ruta_archivo: str, crear_backup: bool = True) -> bool:
    """Guarda datos a JSON de forma segura"""
    try:
        if crear_backup and os.path.exists(ruta_archivo):
            crear_copia_respaldo(ruta_archivo)
        
        directorio = os.path.dirname(ruta_archivo)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception:
        return False

def crear_estructura_carpetas(base_path: str, carpetas: list) -> bool:
    """Crea estructura de carpetas del proyecto"""
    try:
        for carpeta in carpetas:
            ruta_completa = os.path.join(base_path, carpeta)
            os.makedirs(ruta_completa, exist_ok=True)
        return True
    except Exception:
        return False