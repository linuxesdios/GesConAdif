"""
Gestor de contratos para PyQt5 - VERSIÓN LIMPIA SIN DUPLICACIONES
"""

import json
import os
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QComboBox, QLabel
from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from PyQt5.QtWidgets import QMessageBox

# IMPORTAR EL CONTROLADOR DE RUTAS CENTRALIZADO
try:
    from .controlador_routes import rutas
except (ImportError, ValueError):
    from controlador_routes import rutas

class ContractManagerQt5(QObject):
    """Gestor de contratos y configuraciones para PyQt5"""
    
    # Señales para comunicación con la interfaz
    contract_loaded = pyqtSignal(dict)
    contract_type_changed = pyqtSignal(str)
    
    def __init__(self, combo_box: QComboBox, label_tipo: QLabel, label_expediente: QLabel = None):
        super().__init__()
        self.combo_box = combo_box
        self.label_tipo = label_tipo
        self.label_expediente = label_expediente
        
        # Datos de contratos
        self.contracts_list = []
        self.contracts_mapping = {}
        self.current_contract = None
        self._updating = False
        
        # Inicializar gestor JSON
        self._init_json_manager()
        
        # CAMBIO CRÍTICO: Verificar que el gestor existe antes de cargar
        if self.gestor_json:
            self.load_contracts_from_json()
        else:
            print(f"[ContractManager] ❌ Error: No se pudo inicializar gestor JSON")
            self._load_empty_contracts()
            self._update_combo_box()
        
        # Conectar señales y estado inicial
        self._connect_signals()
        self._set_initial_state()

    # AÑADIR ESTE MÉTODO SI NO EXISTE:
    def _load_empty_contracts(self):
        """Cargar lista vacía si no hay JSON"""
        self.contracts_list = []
        self.contracts_mapping = {}
        print(f"[ContractManager] ⚠️ Cargando lista vacía de contratos")

    def _init_json_manager(self):
        """Inicializar gestor JSON USANDO CONTROLADOR DE RUTAS CENTRALIZADO"""
        try:
            from .controlador_json import GestorContratosJSON
            
            # USAR CONTROLADOR DE RUTAS UNIFICADO - UNA SOLA FUENTE DE VERDAD
            json_path = rutas.get_ruta_base_datos()
            print(f"[ContractManager] Ruta unificada: {json_path}")
            
            self.gestor_json = GestorContratosJSON(json_path)
            print(f"[ContractManager] Gestor JSON inicializado correctamente")
            
        except Exception as e:
            print(f"[ContractManager] Error inicializando gestor JSON: {e}")
            self.gestor_json = None
    def _connect_signals(self):
        """Conectar señales del ComboBox"""
        try:
            self.combo_box.currentTextChanged.connect(self._on_text_changed)
            self.combo_box.currentIndexChanged.connect(self._on_index_changed)
        except Exception as e:
            print(f"[ContractManager] ❌ Error conectando señales: {e}")
    
    def _set_initial_state(self):
        """Establecer estado inicial de los labels"""
        if self.combo_box.currentIndex() <= 0:
            self._update_labels("-", "-")
        else:
            current_text = self.combo_box.currentText()
            if current_text and not current_text.startswith("Seleccionar"):
                self._process_contract_selection(current_text)
    
    def _on_text_changed(self, text: str):
        """Callback para cambio de texto"""
        if not self._updating:
            self._process_contract_selection(text)
        else:
            print(f"[ContractManager] ⏭️ Text change ignorado: '{text}' (updating={self._updating})")

    def _on_index_changed(self, index: int):
        """Callback para cambio de índice"""
        if not self._updating and index >= 0:
            text = self.combo_box.itemText(index) if index < self.combo_box.count() else ""
            self._process_contract_selection(text)
        else:
            print(f"[ContractManager] ⏭️ Index change ignorado: {index} (updating={self._updating})")
    
    def _validate_contract_type(self, tipo: str) -> str:
        """Validar y normalizar tipo de contrato"""
        tipos_validos = ["obras", "servicios", "mantenimiento", "facturas"]
        tipo_lower = tipo.lower()
        
        # Mapear variaciones comunes
        mapeo_tipos = {
            "obra": "obras",
            "servicio": "servicios", 
            "factura": "facturas",
            "mantenimientos": "mantenimiento"
        }
        
        tipo_normalizado = mapeo_tipos.get(tipo_lower, tipo_lower)
        
        if tipo_normalizado in tipos_validos:
            return tipo_normalizado.title()
        else:
            print(f"[ContractManager] ⚠️ Tipo no válido: {tipo}, usando 'Servicios' por defecto")
            return "Servicios"

    

    # =================== MÉTODOS DE INTERFAZ BÁSICOS ===================

    def _update_labels(self, tipo: str, expediente: str):
        """Actualizar labels con nueva información"""
        print(f"[CONTRACT_MANAGER] 🏷️ _update_labels llamado con tipo: '{tipo}', expediente: '{expediente}'")
        try:
            if self.label_tipo:
                texto_anterior = self.label_tipo.text()
                print(f"[CONTRACT_MANAGER] 🏷️ Label Tipo ANTES: '{texto_anterior}'")
                
                self.label_tipo.setText(f"{tipo}")
                self.label_tipo.update()
                
                texto_nuevo = self.label_tipo.text()
                print(f"[CONTRACT_MANAGER] 🏷️ Label Tipo DESPUÉS: '{texto_nuevo}'")
                
                if texto_nuevo == tipo:
                    print(f"[CONTRACT_MANAGER] ✅ Label Tipo actualizado correctamente")
                else:
                    print(f"[CONTRACT_MANAGER] ❌ Label Tipo NO se actualizó correctamente")
            else:
                print(f"[CONTRACT_MANAGER] ❌ label_tipo es None")
            
            if self.label_expediente:
                self.label_expediente.setText(f"{expediente}")
                self.label_expediente.update()
                print(f"[CONTRACT_MANAGER] ✅ Label Expediente actualizado")
            else:
                print(f"[CONTRACT_MANAGER] ⚠️ label_expediente es None")
            
        except Exception as e:
            print(f"[CONTRACT_MANAGER] ❌ Error al actualizar labels: {e}")
            import traceback
            traceback.print_exc()

    def _update_combo_box(self):
        """Actualizar contenido del ComboBox"""
        try:
            self.combo_box.blockSignals(True)
            self.combo_box.clear()
            
            items = ["Seleccionar contrato..."] + self.contracts_list
            
            for i, item in enumerate(items):
                self.combo_box.addItem(item)
            
            self.combo_box.blockSignals(False)
            
        except Exception as e:
            print(f"[ContractManager] ERROR al actualizar contenido del ComboBox: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.combo_box.blockSignals(False)
    
    # =================== MÉTODOS PÚBLICOS ===================
    
    def get_current_contract(self) -> Optional[str]:
        """Obtener el contrato actual"""
        return self.current_contract
    
    def get_current_contract_data(self) -> Optional[Dict[str, Any]]:
        """Obtener datos del contrato actual - SIEMPRE FRESCO"""
        if self.current_contract and self.gestor_json:
            try:
                # CAMBIO MÍNIMO: usar el método correcto
                return self.gestor_json.buscar_contrato_por_nombre(self.current_contract)
            except Exception as e:
                print(f"[ContractManager] ❌ Error cargando datos: {e}")
                return None
        return None
    
    def reload_contracts(self):
        """Recargar contratos desde el JSON"""
        current_selection = self.combo_box.currentText()
        
        if self.gestor_json:
            self.gestor_json.recargar_datos()
        
        self.load_contracts_from_json()
        
        if current_selection and current_selection != "Seleccionar contrato...":
            index = self.combo_box.findText(current_selection)
            if index >= 0:
                self.combo_box.setCurrentIndex(index)
            elif self.combo_box.count() > 1:
                self.combo_box.setCurrentIndex(self.combo_box.count() - 1)

    # =================== MÉTODOS DE UTILIDAD ===================

    def _get_current_datetime(self):
        """Obtener fecha y hora actual como string"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def _load_empty_contracts_and_update(self):
        """Método temporal mientras se implementa load_contracts_from_json"""
        self.contracts_list = []
        self.contracts_mapping = {}
        self._update_combo_box()
    
    
    def load_contracts_from_json(self):
            """Cargar contratos con verificación mejorada"""
            try:
                # BLOQUEAR SEÑALES AL INICIO
                self.combo_box.blockSignals(True)
                
                if not self.gestor_json:
                    print(f"[ContractManager] No hay gestor JSON disponible")
                    self._load_empty_contracts()
                    self._update_combo_box()
                    return
                
                print(f"[ContractManager] Iniciando carga de contratos...")
                
                # Forzar recarga de datos del archivo
                print(f"[ContractManager] Recargando datos del JSON...")
                self.gestor_json.recargar_datos()
                
                # Obtener nombres de obras
                contract_names = self.gestor_json.obtener_todos_nombres_obras()
                
                if contract_names:
                    self.contracts_list = []
                    self.contracts_mapping = {}
                    
                    for nombre_completo in contract_names:
                        if nombre_completo and nombre_completo.strip():
                            # Crear nombre display
                            nombre_display = nombre_completo[:77] + "..." if len(nombre_completo) > 80 else nombre_completo
                            
                            # Obtener datos completos
                            contract_data = self.gestor_json.cargar_datos_obra(nombre_completo)
                            
                            if contract_data:
                                self.contracts_list.append(nombre_display)
                                self.contracts_mapping[nombre_display] = {
                                    'data': contract_data,
                                    'nombre_completo': nombre_completo
                                }


                else:
                    print(f"[ContractManager] No se encontraron contratos")
                    self._load_empty_contracts()
                
                self._update_combo_box()
                
            except Exception as e:
                print(f"[ContractManager] Error cargando contratos: {e}")
                import traceback
                traceback.print_exc()
                self._load_empty_contracts()
                self._update_combo_box()
            finally:
                self.combo_box.blockSignals(False)

    def _process_contract_selection(self, contract_name: str):
        """Procesar selección de contrato - CON VERIFICACIÓN DE ESTRUCTURA"""
        try:
            self._updating = True
            
            # Los campos se guardan automáticamente al perder foco
            
            # Limpiar si es selección por defecto
            if not contract_name or contract_name.strip().lower().startswith("seleccionar"):
                self._clear_contract_info()
                return
            
            # Obtener datos del contrato usando el mapping corregido
            contract_info = self.contracts_mapping.get(contract_name)
            
            if contract_info and isinstance(contract_info, dict):
                # Obtener nombre completo
                nombre_completo = contract_info.get('nombre_completo', contract_name)
                
                # FORZAR RECARGA COMPLETA DEL JSON
                contract_data = None
                if self.gestor_json:
                    try:
                        # FORZAR RECARGA DEL ARCHIVO JSON
                        self.gestor_json.recargar_datos()
                        contract_data = self.gestor_json.cargar_datos_obra(nombre_completo)
                        if contract_data:
                            # Actualizar el mapping con datos frescos
                            contract_info['data'] = contract_data
                            print(f"[ContractManager] 🔄 Datos JSON recargados para: {nombre_completo}")
                    except Exception as e:
                        print(f"[ContractManager] ⚠️ Error recargando datos frescos: {e}")
                        contract_data = contract_info.get('data', {})
                else:
                    contract_data = contract_info.get('data', {})
                
                if contract_data:
                    tipo_actuacion = contract_data.get('tipoActuacion', 'Sin tipo')
                    numero_expediente = contract_data.get('numeroExpediente', 'Sin expediente')
                    
                    # Actualizar labels
                    self._update_labels(tipo_actuacion, numero_expediente)
                    
                    # Usar el nombre completo para el estado interno
                    self.current_contract = nombre_completo
                    
                    # 🆕 NUEVO: Verificar y crear estructura de carpetas
                    self._verificar_y_crear_estructura_carpeta(contract_data)
                    
                    # Emitir señales
                    self.contract_loaded.emit(contract_data)
                    self.contract_type_changed.emit(tipo_actuacion)
                    
                    # Mostrar tab widget
                    self._mostrar_tab_widget()
                    
                    # Actualizar pestañas según tipo de contrato
                    main_window = self._get_main_window()
                    if main_window and hasattr(main_window, '_actualizar_pestanas_por_tipo'):
                        tipo_normalizado = self._validate_contract_type(tipo_actuacion)
                        main_window._actualizar_pestanas_por_tipo(tipo_normalizado.lower())
                        print(f"[ContractManager] 🏷️ Pestañas actualizadas para tipo: {tipo_normalizado.lower()}")
                    
                    # 🆕 FORZAR RECARGA DE EMPRESAS DESDE JSON
                    if (main_window and 
                        hasattr(main_window, 'controlador_eventos_ui') and 
                        main_window.controlador_eventos_ui and
                        hasattr(main_window.controlador_eventos_ui, 'cargar_empresas_desde_json')):
                        main_window.controlador_eventos_ui.cargar_empresas_desde_json(nombre_completo)
                        print(f"[ContractManager] 🏢 Empresas recargadas para: {nombre_completo}")
                    
                else:
                    self._update_labels("Error", "Error")
            else:
                self._update_labels("Error", "Error")
                
        except Exception as e:
            print(f"[ContractManager] ❌ Error procesando selección: {e}")
        finally:
            self._updating = False
    # ===== NUEVA FUNCIÓN A AÑADIR =====
    def _verificar_y_crear_estructura_carpeta(self, contract_data):
        """Verificar y crear estructura de carpetas automáticamente"""
        try:
            
            # Obtener main window para acceder al gestor
            main_window = self._get_main_window()
            if not main_window:
                print(f"[ContractManager] ❌ No se pudo obtener main window")
                return
            
            # Verificar si tiene gestor de archivos unificado
            if not hasattr(main_window, 'gestor_archivos_unificado'):
                print(f"[ContractManager] ❌ Main window no tiene gestor_archivos_unificado")
                return
            
            gestor = main_window.gestor_archivos_unificado
            if not gestor:
                print(f"[ContractManager] ❌ Gestor de archivos es None")
                return
            
            # Verificar/crear carpeta
            carpeta_path, fue_creada, operacion = gestor.verificar_o_crear_carpeta(
                contract_data, 
                modo="auto"  # Crear automáticamente
            )
            
            if fue_creada:
                # Mostrar notificación de que se creó la estructura
                self._mostrar_notificacion_estructura_creada(carpeta_path, contract_data)
            else:
                pass  # Carpeta ya existía
                
        except Exception as e:
            print(f"[ContractManager] ❌ Error verificando estructura: {e}")

    # ===== NUEVA FUNCIÓN A AÑADIR =====
    def _mostrar_notificacion_estructura_creada(self, carpeta_path, contract_data):
        """Mostrar notificación cuando se crea estructura"""
        try:
            nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
            
            # Buscar ventana principal para el popup
            main_window = self._get_main_window()
            parent = main_window if main_window else None
            
            
            # Crear mensaje informativo
            mensaje = (
                f"📁 ESTRUCTURA DE CARPETAS CREADA AUTOMÁTICAMENTE\n\n"
                f"📂 Proyecto: {nombre_obra[:50]}{'...' if len(nombre_obra) > 50 else ''}\n"
                f"📍 Ubicación: {carpeta_path}\n\n"
                f"✅ Se han creado 12 subcarpetas organizadas\n"
                f"📄 Cada subcarpeta incluye archivo README\n\n"
                f"La estructura está lista para guardar documentos."
            )
            
            # Mostrar popup
            QMessageBox.information(
                parent, "📁 Estructura Creada", mensaje
            )
            
        except Exception as e:
            print(f"[ContractManager] ❌ Error mostrando notificación: {e}")
    


    def _clear_contract_info(self):
        """Limpiar información del contrato"""
        self.current_contract = None
        self._update_labels("-", "-")
        
        # Ocultar tabWidget cuando no hay selección
        self._ocultar_tab_widget()
        
        # Emitir señal de limpieza
        try:
            main_window = self._get_main_window()
            if main_window and hasattr(main_window, 'on_contract_cleared'):
                main_window.on_contract_cleared()
        except Exception as e:
            print(f"[ContractManager] ❌ Error emitiendo señal de limpieza: {e}")
    def _get_main_window(self):
        """Obtener referencia a la ventana principal - VERSIÓN ROBUSTA"""
        try:
            # Método 1: Buscar hacia arriba en la jerarquía
            parent = self.parent()
            while parent:
                if hasattr(parent, 'tabWidget') and hasattr(parent, 'controlador_autosave'):
                    return parent
                parent = parent.parent()
            
            # Método 2: Buscar mediante el combo_box
            if hasattr(self, 'combo_box') and self.combo_box:
                parent = self.combo_box.parent()
                while parent:
                    if hasattr(parent, 'tabWidget') and hasattr(parent, 'controlador_autosave'):
                        return parent
                    parent = parent.parent()
            
            # Método 3: Buscar mediante QApplication
            from PyQt5.QtWidgets import QApplication
            for widget in QApplication.allWidgets():
                if hasattr(widget, 'tabWidget') and hasattr(widget, 'controlador_autosave'):
                    return widget
            
            print("[ContractManager] ⚠️ No se encontró ventana principal con tabWidget")
            return None
            
        except Exception as e:
            print(f"[ContractManager] ❌ Error buscando ventana principal: {e}")
            return None

    def _mostrar_tab_widget(self):
        """Mostrar tabWidget cuando se selecciona una obra - VERSIÓN ROBUSTA"""
        try:
            main_window = self._get_main_window()
            
            if not main_window:
                print("[ContractManager] ❌ No se pudo encontrar ventana principal")
                return
                
            if not hasattr(main_window, 'tabWidget'):
                print("[ContractManager] ❌ Ventana principal no tiene tabWidget")
                return
            
            tab_widget = main_window.tabWidget
            if not tab_widget:
                print("[ContractManager] ❌ tabWidget es None")
                return
            
            # Mostrar tabWidget
            tab_widget.setVisible(True)

            for i in range(tab_widget.count()):
                if "Inicio" in tab_widget.tabText(i):
                    tab_widget.setCurrentIndex(i)
                    print(f"[ContractManager] Pestaña 'Inicio' abierta automáticamente")
                    break   
                
        except Exception as e:
            print(f"[ContractManager] ❌ Error mostrando tabWidget: {e}")

            traceback.print_exc()
    def obtener_nombre_contrato_actual(self) -> str:
        """Obtener nombre del contrato actualmente seleccionado"""
        try:
            if hasattr(self, 'current_contract') and self.current_contract:
                return self.current_contract
            return ""
        except Exception as e:
            print(f"[ControladorSelector] ❌ Error obteniendo nombre contrato: {e}")
            return ""
    def _ocultar_tab_widget(self):
        """Ocultar tabWidget cuando no hay obra seleccionada - VERSIÓN ROBUSTA"""
        try:
            main_window = self._get_main_window()
            
            if not main_window:
                print("[ContractManager] ❌ No se pudo encontrar ventana principal")
                return
                
            if not hasattr(main_window, 'tabWidget'):
                print("[ContractManager] ❌ Ventana principal no tiene tabWidget")
                return
            
            tab_widget = main_window.tabWidget
            if not tab_widget:
                print("[ContractManager] ❌ tabWidget es None")
                return
            
            # Ocultar tabWidget
            tab_widget.setVisible(False)
            
        except Exception as e:
            print(f"[ContractManager] ❌ Error ocultando tabWidget: {e}")

            traceback.print_exc()

    def _guardar_campo_con_foco_actual(self, main_window):
        """Guardar solo el campo que tiene el foco actualmente"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            # Obtener el widget que tiene el foco
            widget_con_foco = QApplication.focusWidget()
            
            if not widget_con_foco:
                return
            
            nombre_widget = widget_con_foco.objectName()
            if not nombre_widget:
                return
            
            # Solo procesar si es un campo de entrada
            valor = None
            
            # Determinar tipo de widget y obtener valor
            if hasattr(widget_con_foco, 'text'):  # QLineEdit
                valor = widget_con_foco.text().strip()
            elif hasattr(widget_con_foco, 'toPlainText'):  # QTextEdit
                valor = widget_con_foco.toPlainText().strip()
            elif hasattr(widget_con_foco, 'value'):  # QDoubleSpinBox
                valor = str(widget_con_foco.value())
            elif hasattr(widget_con_foco, 'date'):  # QDateEdit
                valor = widget_con_foco.date().toString("yyyy-MM-dd")
            
            # Guardar si hay valor y controladores disponibles
            if valor and hasattr(main_window, 'controlador_json') and main_window.controlador_json:
                # Determinar método de guardado según tipo
                if hasattr(widget_con_foco, 'toPlainText'):  # Texto largo
                    exito = main_window.controlador_json.guardar_texto_largo_en_json(
                        self.current_contract, nombre_widget, valor
                    )
                elif hasattr(widget_con_foco, 'date'):  # Fecha
                    exito = main_window.controlador_json.guardar_fecha_en_json(
                        self.current_contract, nombre_widget, valor
                    )
                else:  # Campo normal
                    exito = main_window.controlador_json.guardar_campo_en_json(
                        self.current_contract, nombre_widget, valor
                    )
                
                if exito:
                    pass  # Guardado exitoso
                
        except Exception as e:
            print(f"[ContractManager] ❌ Error guardando campo con foco: {e}")



def setup_contract_manager(main_window) -> ContractManagerQt5:
    """
    REEMPLAZAR SOLO ESTA FUNCIÓN en Controlador_selector.py
    """
    try:
        print("[ContractManager] 🔧 Setup contract manager...")
        
        # Buscar combo box
        combo_box = None
        if hasattr(main_window, 'comboBox'):
            combo_box = main_window.comboBox
        else:
            from PyQt5.QtWidgets import QComboBox
            combos = main_window.findChildren(QComboBox)
            if combos:
                combo_box = combos[0]
        
        if not combo_box:
            print("[ContractManager] ❌ No ComboBox encontrado")
            return None
        
        # Buscar labels
        label_tipo = getattr(main_window, 'Tipo', None)
        label_expediente = getattr(main_window, 'expediente', None)
        
        if not label_tipo:
            print("[ContractManager] ❌ No label 'Tipo' encontrado")
            return None
        
        # Crear ContractManager
        contract_manager = ContractManagerQt5(combo_box, label_tipo, label_expediente)
        
        # Conectar señales básicas
        if hasattr(main_window, 'on_contract_loaded'):
            contract_manager.contract_loaded.connect(main_window.on_contract_loaded)
        
        if hasattr(main_window, 'on_contract_type_changed'):
            contract_manager.contract_type_changed.connect(main_window.on_contract_type_changed)
        
        print("[ContractManager] ✅ Contract manager configurado")
        return contract_manager
        
    except Exception as e:
        print(f"[ContractManager] ❌ Error: {e}")
        return None
    