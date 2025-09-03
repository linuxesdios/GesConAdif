"""
Funciones auxiliares y utilidades para la aplicación Generador de Actas ADIF
Incluye funciones para gestión de archivos, rutas, conversiones y utilidades generales
🆕 INCLUYE: Funciones de validación consolidadas de múltiples controladores
"""
import os
import sys
import webbrowser
import subprocess
import shutil
import json
import time
import glob
import re
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

# =================== 🆕 VALIDACIONES CONSOLIDADAS ===================

def es_numero_valido(valor_str: str) -> bool:
    """
    Validar si string es número válido - CONSOLIDADO DE MÚLTIPLES CONTROLADORES
    
    Anteriormente duplicado en:
    - controlador_calculos.py:582-600
    - controlador_eventos_ui.py (indirectamente)
    """
    try:
        if not valor_str or not valor_str.strip():
            return False
        
        valor_str = valor_str.strip().replace(',', '.')
        
        # Rechazar strings especiales antes de la conversión
        if valor_str.lower() in ['nan', 'inf', '-inf', 'infinity', '-infinity']:
            return False
        
        # Verificar formato básico
        if valor_str.count('.') > 1:
            return False
        
        # Intentar conversión
        numero = float(valor_str)
        
        # Verificar que no sea NaN o infinito
        if str(numero).lower() in ['nan', 'inf', '-inf'] or numero != numero:  # NaN != NaN es True
            return False
            
        return True
        
    except (ValueError, TypeError):
        return False

def validar_nif_basico(nif: str) -> bool:
    """Validación básica de NIF español"""
    if not nif or len(nif.strip()) < 8:
        return False
    
    nif = nif.strip().upper().replace(" ", "")
    
    # Patrón básico: 8 dígitos + 1 letra
    patron = re.compile(r'^\d{8}[A-Z]$')
    return bool(patron.match(nif))

def validar_email_basico(email: str) -> bool:
    """Validación básica de email"""
    if not email or not email.strip():
        return False
    
    email = email.strip().lower()
    
    # Rechazar patrones problemáticos
    if '..' in email:  # Puntos consecutivos
        return False
    if email.startswith('.') or email.endswith('.'):  # Empieza o termina con punto
        return False
    if '@.' in email or '.@' in email:  # Punto inmediato al @
        return False
    
    # Patrón básico de email
    patron = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(patron.match(email))

def validar_datos_empresa(datos_empresa: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validar datos completos de empresa - CONSOLIDADO
    
    Args:
        datos_empresa: Diccionario con datos de empresa
        
    Returns:
        Tuple (es_valido, errores)
    """
    errores = []
    
    # Validar nombre (obligatorio)
    if not datos_empresa.get('nombre', '').strip():
        errores.append("Nombre de empresa es obligatorio")
    
    # Validar NIF si está presente
    nif = datos_empresa.get('nif', '').strip()
    if nif and not validar_nif_basico(nif):
        errores.append(f"NIF inválido: {nif}")
    
    # Validar email si está presente
    email = datos_empresa.get('email', '').strip()
    if email and not validar_email_basico(email):
        errores.append(f"Email inválido: {email}")
    
    return len(errores) == 0, errores

def validar_oferta_economica(valor_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validar oferta económica - CONSOLIDADO
    
    Returns:
        Tuple (es_valido, valor_float, mensaje_error)
    """
    if not es_numero_valido(valor_str):
        return False, None, f"Valor no numérico: '{valor_str}'"
    
    try:
        valor = float(valor_str.replace(',', '.'))
        
        if valor < 0:
            return False, None, "Las ofertas no pueden ser negativas"
        
        if valor > 10000000:  # 10 millones
            return False, None, "Valor excesivamente alto"
        
        return True, valor, ""
        
    except Exception as e:
        return False, None, f"Error de conversión: {e}"


def resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta a un recurso
    Funciona tanto en desarrollo como en ejecutable PyInstaller
    
    Args:
        relative_path: Ruta relativa al recurso
        
    Returns:
        Ruta absoluta al recurso
    """
    try:
        # PyInstaller crea un atributo _MEIPASS cuando está empaquetado
        base_path = sys._MEIPASS
    except AttributeError:
        # En desarrollo normal, usar el directorio del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_ui_file_path() -> Optional[str]:
    """
    Busca el archivo actas.ui en una única ubicación fija.
    Returns:
        Ruta al archivo UI o None si no se encuentra.
    """
    ui_path = Path(__file__).parent / "ui" / "actas.ui"
    return str(ui_path) if ui_path.exists() else None

def setup_ui_with_new_structure(main_window_instance) -> bool:
    """
    Configura la UI usando la nueva estructura de archivos
    
    Args:
        main_window_instance: Instancia de la ventana principal
        
    Returns:
        True si se cargó correctamente
    """
    ui_path = get_ui_file_path()
    if ui_path:
        try:
            from PyQt5 import uic
            uic.loadUi(ui_path, main_window_instance)
            return True
        except Exception as e:
            print(f"[helpers_py] ❌ Error cargando UI: {e}")
            return False
    else:
        return False





# =================== GESTIÓN DE ARCHIVOS ===================

def abrir_archivo(ruta_archivo: str) -> bool:
    """
    Abre un archivo con la aplicación predeterminada del sistema
    
    Args:
        ruta_archivo: Ruta del archivo a abrir
        
    Returns:
        True si se abrió correctamente
    """
    try:
        if not os.path.exists(ruta_archivo):
            print(f"[ERROR] Archivo no existe: {ruta_archivo}")
            return False
        
        if sys.platform.startswith('win'):
            os.startfile(ruta_archivo)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', ruta_archivo])
        else:
            subprocess.run(['xdg-open', ruta_archivo])
        
        return True
        
    except Exception as e:
        print(f"[helpers_py] ❌ Error abriendo archivo: {e}")
        return False


def abrir_carpeta(ruta_carpeta: str) -> bool:
    """
    Abre una carpeta en el explorador de archivos
    
    Args:
        ruta_carpeta: Ruta de la carpeta a abrir
        
    Returns:
        True si se abrió correctamente
    """
    try:
        if not os.path.exists(ruta_carpeta):
            print(f"[ERROR] Carpeta no existe: {ruta_carpeta}")
            return False
        
        if sys.platform.startswith('win'):
            subprocess.run(['explorer', ruta_carpeta])
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', ruta_carpeta])
        else:
            subprocess.run(['xdg-open', ruta_carpeta])
        
        return True
        
    except Exception as e:
        print(f"[helpers_py] ❌ Error abriendo carpeta: {e}")
        return False


def abrir_url(url: str) -> bool:
    """
    Abre una URL en el navegador predeterminado
    
    Args:
        url: URL a abrir
        
    Returns:
        True si se abrió correctamente
    """
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"[helpers_py] ❌ Error abriendo URL: {e}")
        return False


def crear_carpeta_si_no_existe(ruta_carpeta: str) -> bool:
    """
    Crea una carpeta si no existe
    
    Args:
        ruta_carpeta: Ruta de la carpeta a crear
        
    Returns:
        True si se creó o ya existía
    """
    try:
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
        return True
    except Exception as e:
        print(f"[helpers_py] ❌ Error creando carpeta: {e}")
        return False





# =================== UTILIDADES DE TEXTO ===================

def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un nombre para usarlo como nombre de archivo
    
    Args:
        nombre: Nombre a limpiar
        
    Returns:
        Nombre limpio para archivo
    """
    # Caracteres no permitidos en nombres de archivo
    caracteres_prohibidos = '<>:"/\\|?*'
    
    nombre_limpio = nombre
    for char in caracteres_prohibidos:
        nombre_limpio = nombre_limpio.replace(char, '_')
    
    # Remover caracteres de control
    nombre_limpio = ''.join(c for c in nombre_limpio if ord(c) >= 32)
    
    # Normalizar espacios
    nombre_limpio = ' '.join(nombre_limpio.split())
    
    # Limitar longitud
    if len(nombre_limpio) > 100:
        nombre_limpio = nombre_limpio[:100]
    
    return nombre_limpio.strip()


def truncar_texto(texto: str, longitud_maxima: int, sufijo: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        texto: Texto a truncar
        longitud_maxima: Longitud máxima
        sufijo: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if len(texto) <= longitud_maxima:
        return texto
    
    return texto[:longitud_maxima - len(sufijo)] + sufijo


def limpiar_texto_para_json(texto: str) -> str:
    """
    Limpia texto para almacenar en JSON
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    # Remover caracteres de control excepto saltos de línea y tabs
    texto_limpio = ''.join(c for c in texto if ord(c) >= 32 or c in '\n\t')
    
    # Normalizar saltos de línea
    texto_limpio = texto_limpio.replace('\r\n', '\n').replace('\r', '\n')
    
    return texto_limpio.strip()


def extraer_numeros_de_texto(texto: str) -> str:
    """
    Extrae solo los números de un texto
    
    Args:
        texto: Texto del cual extraer números
        
    Returns:
        String con solo números
    """
    return ''.join(c for c in texto if c.isdigit())


# =================== UTILIDADES NUMÉRICAS ===================

def formatear_numero_espanol(numero: float, decimales: int = 2) -> str:
    """
    Formatea un número al estilo español (coma decimal, punto miles)
    
    Args:
        numero: Número a formatear
        decimales: Número de decimales
        
    Returns:
        Número formateado
    """
    if abs(numero) >= 1000:
        # Formatear con separadores de miles
        formatted = f"{numero:,.{decimales}f}"
        # Cambiar separadores al formato español
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{numero:.{decimales}f}".replace(".", ",")


def parsear_numero_espanol(texto: str) -> Optional[float]:
    """
    Parsea un número en formato español a float
    
    Args:
        texto: Texto con número en formato español
        
    Returns:
        Número parseado o None si no es válido
    """
    try:
        # Limpiar texto
        texto_limpio = texto.replace("€", "").replace(" ", "").strip()
        
        # Formato español: 1.234,56 → 1234.56
        if "," in texto_limpio:
            texto_limpio = texto_limpio.replace(".", "").replace(",", ".")
        
        return float(texto_limpio)
        
    except (ValueError, AttributeError):
        return None


def convertir_numero_espanol_a_float(texto: str) -> float:
    """
    Convierte número en formato español a float
    Versión robusta con manejo de errores
    
    Args:
        texto: Texto con número
        
    Returns:
        Número convertido o 0.0 si hay error
    """
    if not texto or not str(texto).strip():
        return 0.0
    
    try:
        texto = str(texto).strip()
        
        # Formato español con coma: 1.200,50
        if ',' in texto:
            return round(float(texto.replace(".", "").replace(",", ".")), 2)
        
        # Con punto: verificar si es decimal inglés o miles español
        elif '.' in texto:
            parts = texto.split('.')
            # Si después del punto hay 1-2 dígitos = decimal inglés
            if len(parts) == 2 and len(parts[1]) <= 2:
                return round(float(texto), 2)
            else:
                # Miles español: 1.200
                return round(float(texto.replace(".", "")), 2)
        
        # Solo números
        else:
            return round(float(texto), 2)
            
    except (ValueError, AttributeError):
        return 0.0


# =================== VALIDACIONES ===================

def validar_extension_archivo(ruta_archivo: str, extensiones_validas: List[str]) -> bool:
    """
    Valida que un archivo tenga una extensión válida
    
    Args:
        ruta_archivo: Ruta del archivo
        extensiones_validas: Lista de extensiones válidas (con punto)
        
    Returns:
        True si la extensión es válida
    """
    _, extension = os.path.splitext(ruta_archivo.lower())
    return extension in [ext.lower() for ext in extensiones_validas]


def es_ruta_valida(ruta: str) -> bool:
    """
    Verifica si una ruta es válida (sintácticamente)
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        True si la ruta es válida
    """
    try:
        # Normalizar la ruta
        ruta_normalizada = os.path.normpath(ruta)
        
        # Verificar que no esté vacía
        if not ruta_normalizada or ruta_normalizada in ['.', '..']:
            return False
        
        # Verificar caracteres prohibidos
        caracteres_prohibidos = '<>"|?*'
        if any(char in ruta for char in caracteres_prohibidos):
            return False
        
        return True
        
    except Exception:
        return False




# =================== INFORMACIÓN DEL SISTEMA ===================

def obtener_tamano_archivo_legible(ruta_archivo: str) -> str:
    """
    Obtiene el tamaño de un archivo en formato legible
    
    Args:
        ruta_archivo: Ruta del archivo
        
    Returns:
        Tamaño en formato legible (ej: "1.5 MB")
    """
    try:
        tamano_bytes = os.path.getsize(ruta_archivo)
        
        if tamano_bytes < 1024:
            return f"{tamano_bytes} B"
        elif tamano_bytes < 1024 ** 2:
            return f"{tamano_bytes / 1024:.1f} KB"
        elif tamano_bytes < 1024 ** 3:
            return f"{tamano_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{tamano_bytes / (1024 ** 3):.1f} GB"
            
    except Exception:
        return "Desconocido"


def es_archivo_reciente(ruta_archivo: str, dias: int = 7) -> bool:
    """
    Verifica si un archivo fue modificado recientemente
    
    Args:
        ruta_archivo: Ruta del archivo
        dias: Número de días para considerar "reciente"
        
    Returns:
        True si el archivo es reciente
    """
    try:
        tiempo_modificacion = os.path.getmtime(ruta_archivo)
        tiempo_actual = time.time()
        diferencia_dias = (tiempo_actual - tiempo_modificacion) / (24 * 3600)
        
        return diferencia_dias <= dias
        
    except Exception:
        return False








# =================== GESTIÓN DE BACKUPS ===================

def generar_nombre_archivo_unico(directorio: str, nombre_base: str, extension: str) -> str:
    """
    Genera un nombre de archivo único en un directorio
    
    Args:
        directorio: Directorio donde verificar
        nombre_base: Nombre base del archivo
        extension: Extensión del archivo (con punto)
        
    Returns:
        Nombre de archivo único
    """
    contador = 1
    nombre_actual = f"{nombre_base}{extension}"
    
    while os.path.exists(os.path.join(directorio, nombre_actual)):
        nombre_actual = f"{nombre_base}_{contador}{extension}"
        contador += 1
    
    return nombre_actual




def limpiar_respaldos_antiguos(directorio: str, nombre_base: str, extension: str, max_respaldos: int = 5):
    """
    Limpia respaldos antiguos manteniendo solo los más recientes
    
    Args:
        directorio: Directorio de respaldos
        nombre_base: Nombre base del archivo
        extension: Extensión del archivo
        max_respaldos: Número máximo de respaldos a mantener
    """
    try:
        patron = f"{nombre_base}_backup_*{extension}"
        archivos_respaldo = glob.glob(os.path.join(directorio, patron))
        
        if len(archivos_respaldo) > max_respaldos:
            # Ordenar por fecha de modificación (más reciente primero)
            archivos_respaldo.sort(key=os.path.getmtime, reverse=True)
            
            # Eliminar los más antiguos
            for archivo_antiguo in archivos_respaldo[max_respaldos:]:
                try:
                    os.remove(archivo_antiguo)
                    print(f"[INFO] Respaldo antiguo eliminado: {archivo_antiguo}")
                except Exception as e:
                    print(f"[WARNING] No se pudo eliminar respaldo: {e}")
                    
    except Exception as e:
        print(f"[WARNING] Error limpiando respaldos antiguos: {e}")


def crear_copia_respaldo_proyecto(ruta_archivo: str, directorio_respaldos: str = None) -> str:
    """
    Crea una copia de respaldo de un proyecto con rotación automática
    
    Args:
        ruta_archivo: Ruta del archivo de proyecto
        directorio_respaldos: Directorio donde guardar respaldos
        
    Returns:
        Ruta del archivo de respaldo creado
    """
    try:
        if not os.path.exists(ruta_archivo):
            print(f"[WARNING] Archivo no existe para respaldo: {ruta_archivo}")
            return ""
        
        # Determinar directorio de respaldos
        if not directorio_respaldos:
            proyecto_dir = os.path.dirname(ruta_archivo)
            directorio_respaldos = os.path.join(proyecto_dir, "9_Guardado_seguridad")
        
        # Crear directorio si no existe
        if not crear_carpeta_si_no_existe(directorio_respaldos):
            return ""
        
        # Generar nombre con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_base, extension = os.path.splitext(nombre_archivo)
        nombre_respaldo = f"{nombre_base}_backup_{timestamp}{extension}"
        
        # Crear respaldo
        ruta_respaldo = os.path.join(directorio_respaldos, nombre_respaldo)
        shutil.copy2(ruta_archivo, ruta_respaldo)
        
        # Limpiar respaldos antiguos (mantener solo 5)
        limpiar_respaldos_antiguos(directorio_respaldos, nombre_base, extension, max_respaldos=5)
        
        print(f"[SUCCESS] Respaldo del proyecto creado: {ruta_respaldo}")
        return ruta_respaldo
        
    except Exception as e:
        print(f"[ERROR] Error creando respaldo del proyecto: {e}")
        return ""




# =================== CONVERSIÓN DE DOCUMENTOS ===================

def convertir_docx_a_pdf(ruta_docx: str, cerrar_word: bool = True) -> Optional[str]:
    """
    Convierte archivo .docx a .pdf con manejo robusto de Word
    
    Args:
        ruta_docx: Ruta del archivo Word
        cerrar_word: Si debe cerrar Word antes de convertir
        
    Returns:
        Ruta del PDF creado o None si hay error
    """
    try:
        if not os.path.exists(ruta_docx):
            print(f"[WARNING] Archivo DOCX no existe: {ruta_docx}")
            return None
            
        ruta_pdf = ruta_docx.replace('.docx', '.pdf')
        
        # Esperar un poco después de crear el Word
        time.sleep(0.5)
        
        # Cerrar Word si está ejecutándose y se solicita
        if cerrar_word:
            try:
                subprocess.run(['taskkill', '/f', '/im', 'WINWORD.EXE'], 
                             capture_output=True, timeout=3)
                print("[INFO] Word cerrado antes de conversión")
                time.sleep(0.5)
            except:
                # Si no se puede cerrar, no es problema crítico
                pass
        
        # Convertir a PDF
        from docx2pdf import convert
        convert(ruta_docx, ruta_pdf)
        
        print(f"[SUCCESS] PDF creado: {ruta_pdf}")
        return ruta_pdf
        
    except Exception as e:
        print(f"[ERROR] Error convirtiendo a PDF: {e}")
        
        # Intentar una vez más sin cerrar Word
        try:
            time.sleep(1)
            from docx2pdf import convert
            convert(ruta_docx, ruta_pdf)
            print(f"[SUCCESS] PDF creado en segundo intento: {ruta_pdf}")
            return ruta_pdf
        except Exception as e2:
            print(f"[ERROR] Segundo intento también falló: {e2}")
            return None


# =================== UTILIDADES DE FECHA Y HORA ===================

def formatear_fecha_espanol(fecha: datetime, formato: str = "completo") -> str:
    """
    Formatea una fecha en español
    
    Args:
        fecha: Fecha a formatear
        formato: Tipo de formato ("corto", "completo", "iso")
        
    Returns:
        Fecha formateada en español
    """
    if formato == "corto":
        return fecha.strftime("%d/%m/%Y")
    elif formato == "iso":
        return fecha.strftime("%Y-%m-%d")
    else:  # completo
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        dia = fecha.day
        mes = meses[fecha.month - 1]
        año = fecha.year
        
        return f"{dia} de {mes} de {año}"




# =================== UTILIDADES DE JSON ===================

def cargar_json_seguro(ruta_archivo: str) -> Optional[Dict[str, Any]]:
    """
    Carga un archivo JSON de forma segura
    
    Args:
        ruta_archivo: Ruta del archivo JSON
        
    Returns:
        Datos del JSON o None si hay error
    """
    try:
        if not os.path.exists(ruta_archivo):
            print(f"[WARNING] Archivo JSON no existe: {ruta_archivo}")
            return None
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"[SUCCESS] JSON cargado: {ruta_archivo}")
        return datos
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error de formato JSON: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Error cargando JSON: {e}")
        return None


def guardar_json_seguro(datos: Dict[str, Any], ruta_archivo: str, crear_backup: bool = True) -> bool:
    """
    Guarda datos a JSON de forma segura
    
    Args:
        datos: Datos a guardar
        ruta_archivo: Ruta del archivo JSON
        crear_backup: Si debe crear backup antes de guardar
        
    Returns:
        True si se guardó correctamente
    """
    try:
        # Crear backup del archivo existente
        if crear_backup and os.path.exists(ruta_archivo):
            backup_archivo(ruta_archivo)
        
        # Crear directorio si no existe
        directorio = os.path.dirname(ruta_archivo)
        if directorio and not crear_carpeta_si_no_existe(directorio):
            return False
        
        # Guardar archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] JSON guardado: {ruta_archivo}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error guardando JSON: {e}")
        return False


# =================== NORMALIZACIÓN DE RUTAS ===================

def normalizar_ruta(ruta: str) -> str:
    """
    Normaliza una ruta para el sistema operativo actual
    
    Args:
        ruta: Ruta a normalizar
        
    Returns:
        Ruta normalizada
    """
    return os.path.normpath(ruta)


def ruta_relativa_a_absoluta(ruta_relativa: str, base: str = None) -> str:
    """
    Convierte una ruta relativa a absoluta
    
    Args:
        ruta_relativa: Ruta relativa
        base: Directorio base (por defecto el actual)
        
    Returns:
        Ruta absoluta
    """
    if base is None:
        base = os.getcwd()
    
    return os.path.abspath(os.path.join(base, ruta_relativa))


# =================== UTILIDADES DE CONFIGURACIÓN ===================



if __name__ == "__main__":
    pass
    