"""
Controlador de Rutas Centralizado
Maneja todas las rutas de archivos para desarrollo y PyInstaller
"""
import os
import sys
from pathlib import Path
from typing import Optional


class ControladorRutas:
    """Gestor centralizado de rutas para la aplicación"""
    
    def __init__(self):
        self._base_path = None
        self._es_ejecutable = self._detectar_si_es_ejecutable()
        self._inicializar_rutas()
        
        print(f"[ControladorRutas] Inicializado")
        print(f"[ControladorRutas] Base path: {self.get_base_path()}")
        print(f"[ControladorRutas] Es ejecutable: {self._es_ejecutable}")
    
    def _detectar_si_es_ejecutable(self) -> bool:
        """Detectar si estamos ejecutándose desde un ejecutable empaquetado"""
        return (
            getattr(sys, 'frozen', False) or  # PyInstaller
            hasattr(sys, '_MEIPASS') or      # PyInstaller temp folder
            'python.exe' not in sys.executable.lower()  # Ejecutable directo
        )
    
    def _inicializar_rutas(self):
        """Inicializar rutas base según el contexto de ejecución"""
        if self._es_ejecutable:
            # Ejecutable empaquetado
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller: usar carpeta temporal para recursos internos
                # pero la carpeta de trabajo para datos
                self._base_path = os.getcwd()
                self._recursos_internos = sys._MEIPASS
            else:
                # Ejecutable directo
                self._base_path = os.path.dirname(sys.executable)
                self._recursos_internos = self._base_path
        else:
            # Desarrollo: usar directorio del script principal
            if hasattr(sys.modules['__main__'], '__file__'):
                script_dir = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
            else:
                # Fallback para entornos como Jupyter
                script_dir = os.getcwd()
            
            self._base_path = script_dir
            self._recursos_internos = script_dir
    
    def get_base_path(self) -> str:
        """Obtener ruta base de la aplicación"""
        return self._base_path
    
    def get_recursos_path(self) -> str:
        """Obtener ruta de recursos internos"""
        return getattr(self, '_recursos_internos', self._base_path)
    
    # =================== RUTAS DE ARCHIVOS DE DATOS ===================
    
    def get_ruta_base_datos(self) -> str:
        """Ruta del archivo BaseDatos.json - EN CARPETA basedatos"""
        if self._es_ejecutable:
            # FORZAR: SIEMPRE en _internal/BaseDatos.json
            return os.path.join(self._base_path, "_internal", "BaseDatos.json")
        else:
            # Para desarrollo, en carpeta basedatos
            return os.path.join(self._base_path, "basedatos", "BaseDatos.json")
    
    def get_ruta_backups(self) -> str:
        """🆕 Ruta de la carpeta de backups centralizada - SIMPLIFICADA"""
        if self._es_ejecutable:
            # 🔧 BACKUPS JUNTO AL BaseDatos.json principal
            if "_internal" in self._base_path:
                backups_dir = self._base_path  # Mismo directorio que BaseDatos.json
            else:
                backups_dir = os.path.join(self._base_path, "_internal")
            os.makedirs(backups_dir, exist_ok=True)
            return backups_dir
        else:
            # Para desarrollo, en carpeta basedatos
            backups_dir = os.path.join(self._base_path, "basedatos")
            os.makedirs(backups_dir, exist_ok=True)
            return backups_dir
    
    def get_ruta_carpeta_obras(self) -> str:
        """Ruta de la carpeta obras"""
        ruta = os.path.join(self._base_path, "obras")
        os.makedirs(ruta, exist_ok=True)
        return ruta
    
    def get_ruta_carpeta_informes(self) -> str:
        """Ruta de la carpeta informes - Compatible con EXE y desarrollo"""
        ruta = os.path.join(self._base_path, "informes")
        os.makedirs(ruta, exist_ok=True)
        return ruta
    
    def get_ruta_facturas_directas(self) -> str:
        """Ruta del archivo facturas_directas.json - EN CARPETA basedatos"""
        if self._es_ejecutable:
            # FORZAR: SIEMPRE en _internal/facturas_directas.json
            ruta = os.path.join(self._base_path, "_internal", "facturas_directas.json")
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            return ruta
        else:
            # Para desarrollo, en carpeta basedatos
            return os.path.join(self._base_path, "basedatos", "facturas_directas.json")
    
    def get_ruta_historial_documentos(self) -> str:
        """Ruta del archivo historial_documentos.json - EN CARPETA basedatos"""
        if self._es_ejecutable:
            # FORZAR: SIEMPRE en _internal/historial_documentos.json
            ruta = os.path.join(self._base_path, "_internal", "historial_documentos.json")
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            return ruta
        else:
            # Para desarrollo, en carpeta basedatos
            return os.path.join(self._base_path, "basedatos", "historial_documentos.json")
    
    # =================== RUTAS DE PLANTILLAS ===================
    
    def get_ruta_plantillas(self) -> str:
        """Ruta base de plantillas"""
        # Buscar en múltiples ubicaciones
        posibles_rutas = [
            os.path.join(self._recursos_internos, "plantillas"),
            os.path.join(self._base_path, "plantillas"),
            os.path.join(self._base_path, "templates"),
            "plantillas",
            "templates"
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        # Si no existe, crear en base_path
        ruta_default = os.path.join(self._base_path, "plantillas")
        os.makedirs(ruta_default, exist_ok=True)
        return ruta_default
    
    def get_ruta_plantilla(self, nombre_plantilla: str) -> Optional[str]:
        """Obtener ruta completa de una plantilla específica"""
        plantillas_dir = self.get_ruta_plantillas()
        
        # Lista de posibles ubicaciones
        posibles_rutas = [
            os.path.join(plantillas_dir, nombre_plantilla),
            os.path.join(self._recursos_internos, "plantillas", nombre_plantilla),
            os.path.join(self._base_path, "plantillas", nombre_plantilla),
            os.path.join(self._base_path, "templates", nombre_plantilla),
            os.path.join(self._base_path, nombre_plantilla),  # En raíz
            nombre_plantilla  # Ruta relativa
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                print(f"[ControladorRutas] Plantilla encontrada: {nombre_plantilla} -> {ruta}")
                return ruta
        
        print(f"[ControladorRutas] Plantilla no encontrada: {nombre_plantilla}")
        print(f"[ControladorRutas] Buscado en: {posibles_rutas}")
        return None
    
    # =================== RUTAS DE INTERFAZ UI ===================
    
    def get_ruta_ui(self, nombre_archivo: str = None) -> Optional[str]:
        """Obtener ruta de archivos UI"""
        nombres_posibles = nombre_archivo or [
            "ventana_principal.ui",
            "actas.ui",
            "main.ui"
        ]
        
        if isinstance(nombres_posibles, str):
            nombres_posibles = [nombres_posibles]
        
        directorios_ui = [
            os.path.join(self._recursos_internos, "ui"),
            os.path.join(self._base_path, "ui"),
            os.path.join(self._base_path, "interfaces"),
            self._base_path
        ]
        
        for directorio in directorios_ui:
            for nombre in nombres_posibles:
                ruta_completa = os.path.join(directorio, nombre)
                if os.path.exists(ruta_completa):
                    return ruta_completa
        
        return None
    
    # =================== RUTAS DE RECURSOS ===================
    
    def get_ruta_icono(self, nombre_icono: str = "icono.ico") -> Optional[str]:
        """Obtener ruta del icono de la aplicación"""
        posibles_rutas = [
            # Nueva ubicación en la estructura reorganizada
            os.path.join(self._recursos_internos, "otros", "images", nombre_icono),
            os.path.join(self._base_path, "_internal", "otros", "images", nombre_icono),
            # Ubicaciones originales para compatibilidad
            os.path.join(self._recursos_internos, "resources", "icons", nombre_icono),
            os.path.join(self._base_path, "resources", "icons", nombre_icono),
            os.path.join(self._base_path, "icons", nombre_icono),
            os.path.join(self._base_path, "images", nombre_icono),
            os.path.join(self._base_path, nombre_icono)
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        return None
    
    def get_ruta_imagen_autor(self, nombre_imagen: str = "autor.jpg") -> Optional[str]:
        """Obtener ruta de la imagen del autor para splash screen"""
        posibles_rutas = [
            # Nueva ubicación en la estructura reorganizada
            os.path.join(self._recursos_internos, "otros", "images", nombre_imagen),
            os.path.join(self._base_path, "_internal", "otros", "images", nombre_imagen),
            # Ubicaciones alternativas
            os.path.join(self._base_path, "images", nombre_imagen),
            os.path.join(self._base_path, "resources", "images", nombre_imagen),
            os.path.join(self._base_path, nombre_imagen)
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        return None
    
    def get_ruta_resource(self, ruta_relativa: str) -> str:
        """Obtener ruta de cualquier recurso"""
        # Para PyInstaller, usar _MEIPASS si está disponible
        if hasattr(sys, '_MEIPASS'):
            ruta_recurso = os.path.join(sys._MEIPASS, ruta_relativa)
            if os.path.exists(ruta_recurso):
                return ruta_recurso
        
        # Buscar en ubicaciones estándar
        posibles_rutas = [
            os.path.join(self._recursos_internos, ruta_relativa),
            os.path.join(self._base_path, ruta_relativa),
            ruta_relativa
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        # Fallback: retornar ruta en base_path
        return os.path.join(self._base_path, ruta_relativa)
    
    # =================== RUTAS DE SALIDA Y TEMPORALES ===================
    
    def get_ruta_salida_documentos(self, nombre_contrato: str = "") -> str:
        """Obtener ruta para documentos generados"""
        if nombre_contrato:
            # Limpiar nombre para usar como carpeta
            import re
            nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre_contrato)
            nombre_limpio = re.sub(r'\s+', '_', nombre_limpio)[:50]
            
            ruta = os.path.join(self.get_ruta_carpeta_obras(), nombre_limpio)
        else:
            ruta = os.path.join(self._base_path, "documentos_generados")
        
        os.makedirs(ruta, exist_ok=True)
        return ruta
    
    def get_ruta_temp(self) -> str:
        """Obtener ruta de archivos temporales"""
        import tempfile
        return tempfile.gettempdir()
    
    # =================== MÉTODOS DE VALIDACIÓN ===================
    
    def validar_estructura_basica(self) -> bool:
        """Validar que existe la estructura básica de carpetas"""
        carpetas_requeridas = [
            "obras",
            "plantillas"
        ]
        
        # Los archivos requeridos dependen del contexto de ejecución
        if self._es_ejecutable:
            archivos_requeridos = []  # BaseDatos.json se crea automáticamente en _internal/BaseDeDatos/
        else:
            archivos_requeridos = [
                "BaseDatos.json"
            ]
        
        # Verificar carpetas
        for carpeta in carpetas_requeridas:
            ruta_carpeta = os.path.join(self._base_path, carpeta)
            if not os.path.exists(ruta_carpeta):
                print(f"[ControladorRutas] Creando carpeta faltante: {carpeta}")
                os.makedirs(ruta_carpeta, exist_ok=True)
        
        # Verificar archivos críticos
        for archivo in archivos_requeridos:
            if archivo == "BaseDatos.json":
                # Usar la función get_ruta_base_datos para obtener la ruta correcta
                ruta_archivo = self.get_ruta_base_datos()
            else:
                ruta_archivo = os.path.join(self._base_path, archivo)
            
            if not os.path.exists(ruta_archivo):
                print(f"[ControladorRutas] Archivo crítico faltante: {archivo}")
                return False
        
        return True
    
    def crear_estructura_basica(self):
        """Crear estructura básica de carpetas si no existe"""
        carpetas = [
            "obras",
            "plantillas", 
            "resources/icons",
            "ui",
            "backups"
        ]
        
        for carpeta in carpetas:
            ruta_completa = os.path.join(self._base_path, carpeta)
            os.makedirs(ruta_completa, exist_ok=True)
            
        # Crear BaseDatos.json básico si no existe
        ruta_bd = self.get_ruta_base_datos()
        if not os.path.exists(ruta_bd):
            estructura_basica = {
                "firmantes": {},
                "obras": []
            }
            
            import json
            with open(ruta_bd, 'w', encoding='utf-8') as f:
                json.dump(estructura_basica, f, ensure_ascii=False, indent=2)
    
    # =================== MÉTODOS DE DEBUG ===================
    
    # Método debug eliminado - innecesario en producción
    
    def listar_plantillas_disponibles(self):
        """Listar todas las plantillas disponibles"""
        plantillas_dir = self.get_ruta_plantillas()
        
        if not os.path.exists(plantillas_dir):
            print(f"Directorio de plantillas no existe: {plantillas_dir}")
            return []
        
        archivos = []
        for archivo in os.listdir(plantillas_dir):
            if archivo.endswith('.docx'):
                archivos.append(archivo)
        
        print(f"\nPLANTILLAS DISPONIBLES en {plantillas_dir}:")
        for i, archivo in enumerate(archivos, 1):
            print(f"  {i}. {archivo}")
        
        return archivos


# =================== INSTANCIA GLOBAL ===================

# Crear instancia global para usar en toda la aplicación
rutas = ControladorRutas()


# =================== FUNCIONES DE CONVENIENCIA ===================

def get_base_path() -> str:
    """Función de conveniencia para obtener ruta base"""
    return rutas.get_base_path()

def get_plantilla_path(nombre: str) -> Optional[str]:
    """Función de conveniencia para obtener ruta de plantilla"""
    return rutas.get_ruta_plantilla(nombre)

def get_obras_path() -> str:
    """Función de conveniencia para obtener ruta de obras"""
    return rutas.get_ruta_carpeta_obras()

def resource_path(relative_path: str) -> str:
    """Función de conveniencia compatible con helpers_py"""
    return rutas.get_ruta_resource(relative_path)

def validar_y_crear_estructura():
    """Validar y crear estructura básica de la aplicación"""
    if not rutas.validar_estructura_basica():
        print("[ControladorRutas] Creando estructura básica...")
        rutas.crear_estructura_basica()
    
    return rutas.validar_estructura_basica()


# =================== TESTING ===================

if __name__ == "__main__":
    # Test del controlador de rutas
    print("TESTING CONTROLADOR DE RUTAS")
    
    rutas.debug_rutas()
    rutas.listar_plantillas_disponibles()
    
    # Test de funciones de conveniencia
    print(f"\nFUNCIONES DE CONVENIENCIA:")
    print(f"  get_base_path(): {get_base_path()}")
    print(f"  get_obras_path(): {get_obras_path()}")
    print(f"  resource_path('test'): {resource_path('test')}")
    
    # Validar estructura
    print(f"\nVALIDACION ESTRUCTURA:")
    print(f"  Estructura valida: {validar_y_crear_estructura()}")
