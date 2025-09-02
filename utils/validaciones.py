"""
Validaciones centralizadas
Consolida todas las validaciones de NIF, email, números, etc.
"""

import re
from typing import Tuple, List, Dict

def validar_nif_basico(nif: str) -> bool:
    """Validación básica de NIF español"""
    if not nif or len(nif.strip()) < 8:
        return False
    
    nif = nif.strip().upper().replace(" ", "")
    patron = re.compile(r'^\d{8}[A-Z]$')
    return bool(patron.match(nif))

def validar_email_basico(email: str) -> bool:
    """Validación básica de email"""
    if not email or not email.strip():
        return False
    
    email = email.strip().lower()
    patron = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(patron.match(email))

def es_numero_valido(valor_str: str) -> bool:
    """Validar si string es número válido"""
    try:
        if not valor_str or not valor_str.strip():
            return False
        
        valor_str = valor_str.strip().replace(',', '.')
        if valor_str.count('.') > 1:
            return False
        
        float(valor_str)
        return True
    except (ValueError, TypeError):
        return False

def validar_datos_empresa(datos_empresa: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validar datos completos de empresa"""
    errores = []
    
    if not datos_empresa.get('nombre', '').strip():
        errores.append("Nombre de empresa es obligatorio")
    
    nif = datos_empresa.get('nif', '').strip()
    if nif and not validar_nif_basico(nif):
        errores.append(f"NIF inválido: {nif}")
    
    email = datos_empresa.get('email', '').strip()
    if email and not validar_email_basico(email):
        errores.append(f"Email inválido: {email}")
    
    return len(errores) == 0, errores