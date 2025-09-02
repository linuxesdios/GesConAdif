"""
Utilidades financieras centralizadas
Consolida cálculos de IVA, formateo de euros y conversiones
"""

def calcular_iva(importe: float, porcentaje: float = 0.21) -> float:
    """Calcula IVA de un importe"""
    return importe * porcentaje

def calcular_total_con_iva(importe: float, porcentaje: float = 0.21) -> float:
    """Calcula total con IVA incluido"""
    return importe * (1 + porcentaje)

def formatear_euro_espanol(importe: float, incluir_simbolo: bool = True) -> str:
    """Formatea importe en formato español"""
    if importe >= 1000:
        formatted = f"{importe:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        formatted = f"{importe:.2f}".replace(".", ",")
    
    return f"{formatted} €" if incluir_simbolo else formatted

def parsear_euro_espanol(texto: str) -> float:
    """Convierte texto en formato español a float"""
    try:
        texto_limpio = texto.replace("€", "").replace(" ", "").strip()
        if "," in texto_limpio:
            texto_limpio = texto_limpio.replace(".", "").replace(",", ".")
        return float(texto_limpio)
    except (ValueError, AttributeError):
        return 0.0