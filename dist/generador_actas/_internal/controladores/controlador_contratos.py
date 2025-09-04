"""
Controlador especializado para gestión de contratos
Maneja ContractManager, tipos de contrato y lógica relacionada
"""
import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets
import logging

logger = logging.getLogger(__name__)


class ControladorContratos:
    """Controlador especializado para gestión de contratos"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.contract_manager = None
        logger.info("Inicializado")
        

    
    def _conectar_callbacks(self):
        """Conectar callbacks del ContractManager"""
        try:
            if self.contract_manager:
                # Conectar señales
                self.contract_manager.contract_loaded.connect(self.on_contract_loaded)
                self.contract_manager.contract_type_changed.connect(self.on_contract_type_changed)
                logger.debug("Callbacks conectados")
                
        except Exception as e:
            logger.error(f"Error conectando callbacks: {e}")


    def on_contract_type_changed(self, tipo_contrato):
        """Callback cuando cambia el tipo de contrato - ACTUALIZADO PARA MÚLTIPLES TIPOS"""
        try:
            logger.info(f"Cambiando tipo de contrato a: {tipo_contrato}")
            
            tipo_lower = tipo_contrato.lower()
            
            if tipo_lower in ["obras", "obra"]:
                self.activar_modo_obras()
            elif tipo_lower in ["servicios", "servicio"]:
                self.activar_modo_servicios()
            elif tipo_lower in ["mantenimiento"]:
                self.activar_modo_mantenimiento()
            elif tipo_lower in ["facturas", "factura"]:
                self.activar_modo_facturas()
            else:
                logger.warning(f"Tipo de contrato no reconocido: {tipo_contrato}")
                
        except Exception as e:
            logger.error(f"Error configurando tipo de contrato: {e}")


    def activar_modo_servicios(self):
        """Activa modo servicios"""
        try:
            pass
            
        except Exception as e:
            logger.error(f"Error activando modo servicios: {e}")

    def activar_modo_obras(self):
        """Activa modo obras"""
        try:
            pass
            
        except Exception as e:
            logger.error(f"Error activando modo obras: {e}")

    def activar_modo_mantenimiento(self):
        """Activa modo mantenimiento"""
        try:
            logger.info("Activando modo MANTENIMIENTO")
            
            # Aplicar configuraciones específicas de mantenimiento
            if hasattr(self.main_window, '_configurar_campos_mantenimiento'):
                self.main_window._configurar_campos_mantenimiento()
            
            logger.info("Modo mantenimiento activado")
            
        except Exception as e:
            logger.error(f"Error activando modo mantenimiento: {e}")

    def activar_modo_facturas(self):
        """Activa modo facturas"""
        try:
            logger.info("Activando modo FACTURAS")
            
            # Configuraciones específicas para facturas
            if hasattr(self.main_window, 'controlador_actuaciones_facturas'):
                # Activar específicamente el controlador de facturas
                if hasattr(self.main_window.controlador_actuaciones_facturas, 'activar_modo_facturas'):
                    self.main_window.controlador_actuaciones_facturas.activar_modo_facturas()
            
            # Configurar campos específicos de facturas
            if hasattr(self.main_window, '_configurar_campos_facturas'):
                self.main_window._configurar_campos_facturas()
            
            logger.info("Modo facturas activado")
            
        except Exception as e:
            logger.error(f"Error activando modo facturas: {e}")

    # =================== MÉTODOS DE ACCESO PÚBLICO ===================
    
    def get_current_contract_manager(self):
        """Obtener el gestor de contratos actual"""
        return self.contract_manager

    def get_current_contract_data(self):
        """Obtener datos del contrato actualmente seleccionado"""
        if self.contract_manager:
            return self.contract_manager.get_current_contract_data()
        return None

    def reload_contracts_list(self):
        """Recargar la lista de contratos"""
        try:
            if self.contract_manager:
                logger.info("Recargando lista de contratos...")
                self.contract_manager.reload_contracts()
                logger.info("Lista de contratos recargada")
            else:
                logger.warning("ContractManager no disponible para recargar")
                
        except Exception as e:
            logger.error(f"Error recargando contratos: {e}")

    def get_current_contract_name(self):
        """Obtener el nombre del contrato actual"""
        if self.contract_manager:
            return self.contract_manager.get_current_contract()
        return None

    def is_contract_manager_ready(self):
        """Verificar si el ContractManager está listo"""
        return self.contract_manager is not None

    def get_contracts_count(self):
        """Obtener cantidad de contratos disponibles"""
        if self.contract_manager:
            return len(self.contract_manager.contracts_list)
        return 0
    
    # Método debug eliminado - innecesario en producción

    def force_contract_selection(self, contract_name: str = None):
        """Forzar selección de un contrato específico"""
        try:
            if not self.contract_manager:
                logger.error("ContractManager no disponible")
                return False
                
            if contract_name is None:
                # Seleccionar el primer contrato disponible
                if self.contract_manager.contracts_list:
                    contract_name = self.contract_manager.contracts_list[0]
                else:
                    logger.error("No hay contratos disponibles")
                    return False
            
            logger.info(f"Forzando selección de: '{contract_name}'")
            
            # Buscar índice del contrato en el ComboBox
            index = self.main_window.comboBox.findText(contract_name)
            if index >= 0:
                self.main_window.comboBox.setCurrentIndex(index)
                logger.info(f"Contrato seleccionado en índice {index}")
                return True
            else:
                logger.error(f"Contrato '{contract_name}' no encontrado en ComboBox")
                return False
                
        except Exception as e:
            logger.error(f"Error forzando selección: {e}")
            return False