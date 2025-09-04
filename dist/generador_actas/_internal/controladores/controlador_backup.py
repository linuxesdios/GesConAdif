#!/usr/bin/env python3
"""
Controlador de Backup para BaseDatos.json
Mantiene las últimas 5 copias de seguridad con timestamp
"""
import os
import shutil
import json
from datetime import datetime
from typing import List, Optional
import re
import logging
logger = logging.getLogger(__name__)


class ControladorBackup:
    """Gestor de backups automáticos para BaseDatos.json"""
    
    def __init__(self, base_path: str = None):
        """
        🔧 INICIALIZACIÓN UNIFICADA con ControladorRutas
        
        Args:
            base_path: Ruta base donde está BaseDatos.json (opcional, usado como fallback)
        """
        # 🆕 USAR CONTROLADOR DE RUTAS CENTRALIZADO
        try:
            from .controlador_routes import ControladorRutas
            self._rutas = ControladorRutas()
            
            # Usar rutas centralizadas
            self.basedatos_path = self._rutas.get_ruta_base_datos()
            self.basededatos_dir = self._rutas.get_ruta_backups()
            self._es_ejecutable = self._rutas._es_ejecutable
            self.base_path = self._rutas.get_base_path()
            
            logger.info("Usando ControladorRutas centralizado")
            
        except ImportError:
            # 🔧 FALLBACK: Lógica antigua si no se puede importar ControladorRutas
            logger.warning("Fallback: No se pudo importar ControladorRutas")
            self.base_path = base_path or os.getcwd()
            
            # Detectar si estamos en un ejecutable PyInstaller
            import sys
            self._es_ejecutable = (
                getattr(sys, 'frozen', False) or  # PyInstaller
                hasattr(sys, '_MEIPASS') or      # PyInstaller temp folder
                'python.exe' not in sys.executable.lower()  # Ejecutable directo
            )
            
            # Configurar rutas según el contexto de ejecución
            if self._es_ejecutable:
                if "_internal" in self.base_path:
                    self.basededatos_dir = os.path.join(self.base_path, "BaseDatos")
                else:
                    self.basededatos_dir = os.path.join(self.base_path, "_internal", "BaseDatos")
                os.makedirs(self.basededatos_dir, exist_ok=True)
                self.basedatos_path = os.path.join(self.basededatos_dir, "BaseDatos.json")
            else:
                self.basededatos_dir = self.base_path
                self.basedatos_path = os.path.join(self.base_path, "BaseDatos.json")
        
        self.max_backups = 5
        self.backup_pattern = r"^BaseDatos(\d{8}_\d{6})\.json$"
        
        logger.debug(f"Inicializado - Ruta: {self.base_path}")
        logger.debug(f"BaseDatos dir: {self.basededatos_dir}")
        logger.debug(f"Es ejecutable: {self._es_ejecutable}")
    
    def crear_backup_inicial(self) -> bool:
        """
        Crear backup automático al inicio de la aplicación
        Mantiene solo las últimas 5 copias
        
        Returns:
            bool: True si el backup fue exitoso, False en caso contrario
        """
        try:
            if not os.path.exists(self.basedatos_path):
                logger.info("BaseDatos.json no existe, no se crea backup")
                return False
            
            logger.info("Iniciando sistema de backup automático")
            
            # 1. Obtener lista de backups existentes
            backups_existentes = self._obtener_backups_existentes()
            logger.debug(f"Backups existentes: {len(backups_existentes)}")
            
            # 2. Si hay 5 o más backups, eliminar los más antiguos
            if len(backups_existentes) >= self.max_backups:
                backups_a_eliminar = len(backups_existentes) - self.max_backups + 1
                self._eliminar_backups_antiguos(backups_existentes, backups_a_eliminar)
            
            # 3. Crear nuevo backup con timestamp actual
            timestamp_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nuevo_backup = f"BaseDatos{timestamp_actual}.json"
            nuevo_backup_path = os.path.join(self.basededatos_dir, nuevo_backup)
            
            # 4. Copiar BaseDatos.json al nuevo backup
            shutil.copy2(self.basedatos_path, nuevo_backup_path)
            
            # 5. Verificar que el backup se creó correctamente
            if os.path.exists(nuevo_backup_path):
                size_original = os.path.getsize(self.basedatos_path)
                size_backup = os.path.getsize(nuevo_backup_path)
                
                if size_original == size_backup:
                    logger.info(f"Backup creado: {nuevo_backup} ({size_backup} bytes)")
                    
                    # 6. Mostrar estado actual de backups
                    backups_actuales = self._obtener_backups_existentes()
                    self._mostrar_estado_backups(backups_actuales)
                    
                    return True
                else:
                    logger.error(f"Tamaños diferentes - Original: {size_original}, Backup: {size_backup}")
                    return False
            else:
                logger.error(f"No se pudo crear el backup: {nuevo_backup}")
                return False
                
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def _obtener_backups_existentes(self) -> List[tuple]:
        """
        Obtener lista de backups existentes ordenados por fecha
        
        Returns:
            List[tuple]: Lista de tuplas (nombre_archivo, timestamp, path_completo)
        """
        try:
            backups = []
            
            # Buscar archivos que coincidan con el patrón BaseDatos{timestamp}.json
            for filename in os.listdir(self.basededatos_dir):
                match = re.match(self.backup_pattern, filename)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        # Convertir timestamp a datetime para ordenar
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        path_completo = os.path.join(self.basededatos_dir, filename)
                        backups.append((filename, timestamp, path_completo))
                    except ValueError:
                        logger.warning(f"Timestamp inválido en: {filename}")
                        continue
            
            # Ordenar por timestamp (más antiguo primero)
            backups.sort(key=lambda x: x[1])
            
            return backups
            
        except Exception as e:
            logger.error(f"Error obteniendo backups: {e}")
            return []
    
    def _eliminar_backups_antiguos(self, backups_existentes: List[tuple], cantidad_a_eliminar: int):
        """
        Eliminar los backups más antiguos
        
        Args:
            backups_existentes: Lista de backups existentes
            cantidad_a_eliminar: Número de backups a eliminar
        """
        try:
            logger.info(f"Eliminando {cantidad_a_eliminar} backup(s) antiguo(s)")
            
            # Los backups ya están ordenados por fecha (más antiguo primero)
            for i in range(cantidad_a_eliminar):
                if i < len(backups_existentes):
                    nombre_archivo, timestamp, path_completo = backups_existentes[i]
                    
                    if os.path.exists(path_completo):
                        os.remove(path_completo)
                        fecha_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        logger.info(f"Eliminado: {nombre_archivo} (del {fecha_str})")
                    else:
                        logger.warning(f"Backup no existe: {path_completo}")
                        
        except Exception as e:
            logger.error(f"Error eliminando backups antiguos: {e}")
    
    def _mostrar_estado_backups(self, backups: List[tuple]):
        """
        Mostrar estado actual de los backups
        
        Args:
            backups: Lista de backups existentes
        """
        try:
            logger.debug(f"Estado actual de backups ({len(backups)}/{self.max_backups}):")
            
            if not backups:
                logger.debug("No hay backups disponibles")
                return
            
            # Mostrar backups del más reciente al más antiguo
            backups_recientes = sorted(backups, key=lambda x: x[1], reverse=True)
            
            for i, (nombre_archivo, timestamp, path_completo) in enumerate(backups_recientes, 1):
                fecha_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                size_kb = os.path.getsize(path_completo) / 1024 if os.path.exists(path_completo) else 0
                logger.debug(f"  {i}. {nombre_archivo} - {fecha_str} ({size_kb:.1f} KB)")
                
        except Exception as e:
            logger.error(f"Error mostrando estado: {e}")
    
    def listar_backups_disponibles(self) -> List[dict]:
        """
        Obtener lista de backups disponibles para restauración
        
        Returns:
            List[dict]: Lista de diccionarios con información de cada backup
        """
        try:
            backups_existentes = self._obtener_backups_existentes()
            backups_info = []
            
            # Ordenar del más reciente al más antiguo
            backups_recientes = sorted(backups_existentes, key=lambda x: x[1], reverse=True)
            
            for nombre_archivo, timestamp, path_completo in backups_recientes:
                if os.path.exists(path_completo):
                    size_bytes = os.path.getsize(path_completo)
                    backups_info.append({
                        'nombre': nombre_archivo,
                        'timestamp': timestamp,
                        'fecha_str': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'path': path_completo,
                        'size_bytes': size_bytes,
                        'size_kb': size_bytes / 1024
                    })
            
            return backups_info
            
        except Exception as e:
            logger.error(f"Error listando backups: {e}")
            return []
    
    def restaurar_backup(self, nombre_backup: str) -> bool:
        """
        Restaurar un backup específico
        
        Args:
            nombre_backup: Nombre del archivo de backup a restaurar
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        try:
            backup_path = os.path.join(self.basededatos_dir, nombre_backup)
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup no encontrado: {nombre_backup}")
                return False
            
            # Crear backup del archivo actual antes de restaurar
            if os.path.exists(self.basedatos_path):
                backup_previo = f"BaseDatos_antes_restauracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_previo_path = os.path.join(self.basededatos_dir, backup_previo)
                shutil.copy2(self.basedatos_path, backup_previo_path)
                logger.info(f"Archivo actual respaldado como: {backup_previo}")
            
            # Restaurar el backup seleccionado
            shutil.copy2(backup_path, self.basedatos_path)
            
            # Verificar restauración
            if os.path.exists(self.basedatos_path):
                size_restaurado = os.path.getsize(self.basedatos_path)
                logger.info(f"Backup restaurado: {nombre_backup} ({size_restaurado} bytes)")
                return True
            else:
                logger.error("No se pudo restaurar el backup")
                return False
                
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
    
    def validar_integridad_backup(self, nombre_backup: str) -> bool:
        """
        Validar que un backup tiene estructura JSON válida
        
        Args:
            nombre_backup: Nombre del archivo de backup a validar
            
        Returns:
            bool: True si el backup es válido
        """
        try:
            backup_path = os.path.join(self.basededatos_dir, nombre_backup)
            
            if not os.path.exists(backup_path):
                return False
            
            # Intentar cargar el JSON
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificaciones básicas de estructura
            if not isinstance(data, dict):
                return False
            
            # Verificar campos esperados (opcional)
            expected_fields = ['firmantes', 'obras']  # Ajustar según tu estructura
            for field in expected_fields:
                if field not in data:
                    logger.warning(f"Campo faltante en {nombre_backup}: {field}")
            
            return True
            
        except json.JSONDecodeError:
            logger.error(f"JSON inválido en: {nombre_backup}")
            return False
        except Exception as e:
            logger.error(f"Error validando backup: {e}")
            return False


# =================== FUNCIÓN DE CONVENIENCIA ===================

def crear_backup_automatico(base_path: str = None) -> bool:
    """
    Función de conveniencia para crear backup automático al inicio de la aplicación
    
    Args:
        base_path: Ruta base donde está BaseDatos.json (opcional)
        
    Returns:
        bool: True si el backup fue exitoso
    """
    try:
        controlador = ControladorBackup(base_path)
        return controlador.crear_backup_inicial()
    except Exception as e:
        logger.error(f"Error en backup automático: {e}")
        return False


# =================== TESTING ===================

if __name__ == "__main__":
    # Test del controlador de backup
    test_logger = logging.getLogger(__name__)
    test_logger.info("=" * 60)
    test_logger.info("TESTING CONTROLADOR DE BACKUP")
    test_logger.info("=" * 60)
    
    controlador = ControladorBackup()
    
    # Crear backup de prueba
    success = controlador.crear_backup_inicial()
    test_logger.info(f"Backup creado: {success}")
    
    # Listar backups
    backups = controlador.listar_backups_disponibles()
    test_logger.info(f"Backups disponibles: {len(backups)}")
    
    for backup in backups:
        test_logger.info(f"  - {backup['nombre']} ({backup['fecha_str']}) - {backup['size_kb']:.1f} KB")