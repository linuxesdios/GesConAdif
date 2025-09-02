#!/usr/bin/env python3
import sys, os
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QSpinBox, QWidget  # Import específico para QSpinBox y QWidget
from PyQt5 import uic
from modelos_py import Proyecto, DatosContrato, TipoContrato, Constantes
from helpers_py import setup_ui_with_new_structure, abrir_archivo


# PRECARGAR TODOS LOS CONTROLADORES PARA EXE
from .controlador_json import ControladorJson
from .controlador_tablas import ControladorTablas
from .controlador_actuaciones_facturas import ControladorActuacionesFacturas
from .controlador_calculos import ControladorCalculos
from .controlador_documentos import ControladorDocumentos
from .controlador_autosave import ControladorAutoGuardado
from .controlador_eventos_ui import ControladorEventosUI
from .dialogo_gestionar_contratos import *
from .controlador_pdf_unificado import setup_pdf_viewer_simple
from .controlador_archivos_unificado import GestorArchivos
from .Controlador_selector import ContractManagerQt5
import datetime
from datetime import datetime
import time
import traceback

# PRECARGAR OTROS IMPORTS CRÍTICOS
try:
    from helpers_py import get_ui_file_path, crear_copia_respaldo_proyecto
    from .controlador_resumen import integrar_resumen_completo
    from .controlador_fases_documentos import integrar_controlador_fases
    from .dialogo_actuaciones_especiales import DialogoActuacionesEspeciales
    from controladores.controlador_routes import ControladorRutas
except ImportError:
    pass


class ControladorGrafica(QMainWindow):
    """Controlador principal de la interfaz gráfica"""

    def __init__(self, archivo_proyecto=None):
        super().__init__()
        
        self.proyecto_actual = None
        self.datos_cargados = False
        self.drag_position = None
        self.is_dragging = False
        
        self._init_controllers()
        if archivo_proyecto:
            self.proyecto_actual = archivo_proyecto
        self._setup_ui_fast()
        self._setup_contract_manager()
        self._configurar_gestor_archivos_en_controladores()
        self._setup_pdf_viewer()
        self.arreglar_botones_ahora()
        self._setup_resumen_integrado()
        self._load_data()
        
    def _setup_ui_fast(self):
        try:
            ui_file = get_ui_file_path()
            if ui_file:
                uic.loadUi(ui_file, self)
                self._setup_connections()
                self._configure_tables()
                # Configurar componentes avanzados de UI incluyendo sincronización
                self._setup_componentes_ui()
            else:
                self.create_emergency_ui()
        except Exception as e:
            QMessageBox.critical(self, "Error UI", str(e))
    
    def _configure_tables(self):
        """Configurar tablas después de cargar UI"""
        try:
            # Configurar tabla de empresas
            if hasattr(self, 'TwEmpresas'):
                self.TwEmpresas.setColumnCount(4)
                self.TwEmpresas.setHorizontalHeaderLabels(['Nombre', 'NIF', 'Email', 'Contacto'])
                header = self.TwEmpresas.horizontalHeader()
                # Establecer que se estiren para llenar el espacio
                header.setSectionResizeMode(QHeaderView.Stretch)

                # Definir anchos mínimos por columna
                header.setMinimumSectionSize(60)

                # Si quieres diferentes mínimos por columna, hazlo así:
                self.TwEmpresas.setColumnWidth(0, 120)  # Nombre - más ancho
                self.TwEmpresas.setColumnWidth(1, 80)   # NIF - más estrecho  
                self.TwEmpresas.setColumnWidth(2, 150)  # Email - ancho medio
                self.TwEmpresas.setColumnWidth(3, 100)  # Contacto - ancho medio
            # Configurar tabla de ofertas
            if hasattr(self, 'TwOfertas'):
                self.TwOfertas.setColumnCount(2)
                self.TwOfertas.setHorizontalHeaderLabels(['Empresa', 'Oferta'])
                header = self.TwOfertas.horizontalHeader()

                # Establecer que se estiren para llenar el espacio
                header.setSectionResizeMode(QHeaderView.Stretch)

                # Definir ancho mínimo global
                header.setMinimumSectionSize(80)

                # Establecer anchos iniciales diferentes para cada columna:
                self.TwOfertas.setColumnWidth(0, 150)  # Empresa - ancho medio
                self.TwOfertas.setColumnWidth(1, 250)  # Oferta - más ancho (para descripción)
            # IMPORTANTE: Ocultar tabWidget hasta que se seleccione un contrato
            if hasattr(self, 'tabWidget'):
                self.tabWidget.setVisible(False)
            
            # Inicializar controlador de actuaciones DESPUÉS de cargar la UI
            if not self.controlador_actuaciones_facturas:
                try:
                    self.controlador_actuaciones_facturas = ControladorActuacionesFacturas(self)
                    print("[ControladorGrafica] ✅ ControladorActuacionesFacturas inicializado después de UI")
                except Exception as e:
                    print(f"[ControladorGrafica] ❌ Error inicializando actuaciones después de UI: {e}")
                    self.controlador_actuaciones_facturas = None
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando tablas: {e}")
            pass
    
    def _setup_connections(self):
        try:
            combo_box = self.comboBox
            self.contract_manager = ContractManagerQt5(combo_box, self.Tipo, None)
            self.contract_manager.contract_loaded.connect(self.on_contract_loaded)
            
            # Conectar también el cambio de índice del combo para detectar deselección
            if combo_box:
                combo_box.currentIndexChanged.connect(self._on_combo_index_changed)
                
        except Exception as e:
            pass
    
    def _on_combo_index_changed(self, index):
        """Manejar cambios en el combo box"""
        try:
            if index == -1:  # Sin selección
                self.on_contract_cleared()
        except Exception as e:
            # print(f"[ControladorGrafica] Error en combo change: {e}")
            pass
    
    def _load_data(self):
        try:
            if self.controlador_json:
                self.datos_cargados = True
                
                # Solo cargar la lista de contratos, pero NO seleccionar ninguno automáticamente
                if hasattr(self, 'contract_manager') and self.contract_manager:
                    # Trigger la carga de contratos
                    self.contract_manager.load_contracts_from_json()
                    
                    # NO cargar automáticamente el primer contrato
                    # El usuario debe seleccionar manualmente
                    if hasattr(self, 'comboBox'):
                        self.comboBox.setCurrentIndex(-1)  # Sin selección
                                    
        except Exception as e:
            # print(f"[ControladorGrafica] Error en _load_data: {e}")
            pass
    def _init_controllers(self):
        try:
            self.controlador_json = ControladorJson(main_window=self)
            self.controlador_tablas = ControladorTablas(main_window=self)
            self.controlador_documentos = ControladorDocumentos(self)
            self.controlador_autosave = ControladorAutoGuardado(self)
            self.controlador_calculos = ControladorCalculos()
            self.controlador_eventos_ui = ControladorEventosUI(self)
            self.gestor_archivos_unificado = GestorArchivos(self)
            # Inicializar controlador de rutas
            self.controlador_routes = ControladorRutas()
            # Inicializar como None, se creará después de cargar la UI
            self.controlador_actuaciones_facturas = None
            
            # Inicializar controlador de facturas directas
            try:
                from .controlador_facturas_directas import ControladorFacturasDirectas
                self.controlador_facturas_directas = ControladorFacturasDirectas(self)
                print("[ControladorGrafica] ✅ Controlador de facturas directas inicializado")
            except Exception as e:
                print(f"[ControladorGrafica] ⚠️ Error inicializando controlador facturas directas: {e}")
                self.controlador_facturas_directas = None
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    def mousePressEvent(self, event):
        """Permitir arrastrar la ventana"""
        if event.button() == Qt.LeftButton:
            # Solo arrastrar desde los primeros 120px (zona del header)
            if event.y() <= 120:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.is_dragging = True
                event.accept()
            else:
                # Permitir que otros widgets procesen el evento
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mover la ventana al arrastrar"""
        if self.is_dragging and self.drag_position is not None:
            if event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
            else:
                self.is_dragging = False
                self.drag_position = None
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Terminar el arrastre"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_position = None
        super().mouseReleaseEvent(event)
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        try:
            ui_file = get_ui_file_path()
            if ui_file:
                uic.loadUi(ui_file, self)
                # Animaciones eliminadas - innecesarias para la funcionalidad
            else:
                self.create_emergency_ui()
                return
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando UI: {e}")
            pass

    def _setup_contract_manager(self):
        """Setup del contract manager"""
        try:
            combo_box = self.comboBox
            label_tipo = self.Tipo  
            label_expediente = getattr(self, 'expediente', None)
            
            from .Controlador_selector import ContractManagerQt5
            self.contract_manager = ContractManagerQt5(combo_box, label_tipo, label_expediente)
            
            if self.contract_manager:
                self.contract_manager.contract_loaded.connect(self.on_contract_loaded)
                self.contract_manager.contract_type_changed.connect(self.on_contract_type_changed)
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando contract manager: {e}")
            pass
            self.contract_manager = None

 
    def _configurar_gestor_archivos_en_controladores(self):
        """Configurar gestor de archivos en todos los controladores"""
        try:
            
            # Configurar en controlador de documentos
            if hasattr(self, 'controlador_documentos') and self.controlador_documentos:
                self.controlador_documentos.gestor_archivos = self.gestor_archivos_unificado
            
            # Configurar en otros controladores si es necesario
            if hasattr(self, 'controlador_actuaciones_facturas') and self.controlador_actuaciones_facturas:
                self.controlador_actuaciones_facturas.gestor_archivos = self.gestor_archivos_unificado
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando gestor en controladores: {e}")
            pass
            pass
    def _verificar_estructura_despues_carga(self, contract_data):
        """Verificar estructura después de cargar contrato"""
        try:
            if hasattr(self, 'gestor_archivos_unificado') and self.gestor_archivos_unificado:
                
                # Verificar/crear carpeta automáticamente
                carpeta_path, fue_creada, operacion = self.gestor_archivos_unificado.verificar_o_crear_carpeta(
                    contract_data, 
                    modo="auto"  # Crear automáticamente sin preguntar
                )
                
                if fue_creada:
                    nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
                    
                    # Mostrar notificación discreta
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, "📁 Estructura Creada", 
                        f"Se ha creado automáticamente la estructura de carpetas para:\n\n"
                        f"📂 {nombre_obra[:60]}{'...' if len(nombre_obra) > 60 else ''}\n\n"
                        f"📍 Ubicación: {carpeta_path}"
                    )
                    
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error verificando estructura: {e}")
            pass
            pass
            
    def _cargar_datos_en_interfaz(self, contract_data):
        """Cargar datos del JSON automáticamente en la interfaz - OPTIMIZADO"""
        try:
            
            # 🆕 PAUSAR TODOS LOS SISTEMAS DURANTE LA CARGA
            if hasattr(self, 'controlador_autosave'):
                self.controlador_autosave.iniciar_carga_datos()  # Usar método optimizado
            
            # 🆕 BLOQUEAR SEÑALES GLOBALMENTE
            self.blockSignals(True)
            
            # Cargar TODOS los widgets automáticamente
            self._cargar_todos_los_widgets(contract_data)
            
            # Cargar tablas especiales (empresas y ofertas)
            self._cargar_tablas_especiales(contract_data)
            
            # 🆕 VERIFICAR ESTRUCTURA SOLO UNA VEZ
            self._verificar_estructura_una_vez(contract_data)
            
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando datos en interfaz: {e}")
            pass
        finally:
            # 🆕 REACTIVAR SISTEMAS DE FORMA CONTROLADA
            self.blockSignals(False)
            
            if hasattr(self, 'controlador_autosave'):
                self.controlador_autosave.finalizar_carga_datos()
                

    def _verificar_estructura_una_vez(self, contract_data):
        """Verificar estructura SOLO UNA VEZ por carga"""
        try:
            if hasattr(self, '_estructura_verificada') and self._estructura_verificada:
                return  # Ya se verificó en esta sesión
            
            if hasattr(self, 'gestor_archivos_unificado') and self.gestor_archivos_unificado:
                
                carpeta_path, fue_creada, operacion = self.gestor_archivos_unificado.verificar_o_crear_carpeta(
                    contract_data, 
                    modo="silent"  # 🆕 MODO SILENCIOSO para evitar popups
                )
                
                if fue_creada:
                    nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
                
                self._estructura_verificada = True  # Marcar como verificada
                        
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error verificando estructura: {e}")
            pass

    def _limpiar_todos_los_widgets(self):
        self.blockSignals(True)
        try:
            for widget in self.findChildren(QLineEdit):
                widget.clear()
            for widget in self.findChildren(QTextEdit):
                widget.clear()
            for widget in self.findChildren(QDoubleSpinBox):
                widget.setValue(0.0)
            for widget in self.findChildren(QDateEdit):
                widget.setDate(QDate.currentDate())
        except:
            pass
        finally:
            self.blockSignals(False)

    def _inicializar_widgets_vacios(self):
        try:
            self._cargar_todos_los_widgets({})
        except:
            pass

    def _cargar_todos_los_widgets(self, contract_data):
        if hasattr(self, '_cargando_widgets') and self._cargando_widgets:
            return
        self._cargando_widgets = True
        
        try:
            # LIMPIAR PRIMERO
            self._limpiar_todos_los_widgets()
            self.blockSignals(True)
            
            # LOG DE CAMBIO DE CONTRATO
            nombre_contrato = contract_data.get('nombreObra', 'Sin nombre')
            print(f"[CAMBIO_CONTRATO] 🔄 Cargando widgets para: {nombre_contrato}")
            
            widgets_tipos = [
                (QLineEdit, self._cargar_lineedit),
                (QTextEdit, self._cargar_textedit), 
                (QDoubleSpinBox, self._cargar_doublespinbox),
                (QSpinBox, self._cargar_spinbox),
                (QDateEdit, self._cargar_dateedit)
            ]
            
            # CARGAR TODOS LOS WIDGETS CON LOG
            for widget_type, metodo_carga in widgets_tipos:
                for widget in self.findChildren(widget_type):
                    if widget.objectName() and not widget.objectName().startswith('qt_'):
                        metodo_carga(widget, contract_data)
            
            # VERIFICAR CAMPOS CRÍTICOS DESPUÉS DE LA CARGA
            self._verificar_campos_criticos_post_carga(contract_data)
            
            # FORZAR ACTUALIZACIÓN VISUAL
            self.update()
                        
        except:
            pass
        finally:
            self.blockSignals(False)
            self._cargando_widgets = False
    
    def _verificar_campos_criticos_post_carga(self, contract_data):
        """Verificar y mostrar estado de campos críticos después de la carga"""
        try:
            print(f"[CAMBIO_CONTRATO] 🔍 VERIFICANDO CAMPOS CRÍTICOS TRAS CARGA:")
            
            campos_criticos = ['plazoEjecucion', 'numEmpresasPresentadas', 'numEmpresasSolicitadas', 'basePresupuesto', 'precioAdjudicacion']
            
            for campo in campos_criticos:
                widget = self.findChild(QWidget, campo)
                if widget:
                    tipo_widget = type(widget).__name__
                    valor_json = contract_data.get(campo, '')
                    
                    if hasattr(widget, 'text'):
                        valor_widget = widget.text()
                    elif hasattr(widget, 'value'):
                        valor_widget = str(widget.value())
                    elif hasattr(widget, 'toPlainText'):
                        valor_widget = widget.toPlainText()
                    else:
                        valor_widget = 'N/A'
                    
                    print(f"[CAMBIO_CONTRATO] 🔍 VERIFICACIÓN {campo}: '{valor_widget}' (tipo: {tipo_widget})")
                    
                    # AUTO-COMPLETAR campos vacíos
                    if campo == 'numEmpresasPresentadas' and not valor_widget:
                        valor_calculado = self._calcular_num_empresas_presentadas()
                        if valor_calculado > 0:
                            widget.setText(str(valor_calculado))
                            print(f"[CAMBIO_CONTRATO] 📊 AUTO-COMPLETADO {campo}: '{valor_calculado}'")
                    
                    # Forzar actualización visual para campos críticos
                    if campo == 'basePresupuesto' and valor_widget:
                        print(f"[CAMBIO_CONTRATO] 🔄 FORZANDO actualización visual de {campo}")
                        widget.update()
                        widget.repaint()
                        print(f"[CAMBIO_CONTRATO] ✅ Actualización visual completada para {campo}")
                        
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error verificando campos críticos: {e}")
    
    def _obtener_empresas_lista(self, contract_data):
        """Obtener lista de empresas desde contract_data"""
        try:
            empresas_data = contract_data.get('empresas', [])
            if isinstance(empresas_data, list):
                return empresas_data
            elif isinstance(empresas_data, dict) and 'empresa' in empresas_data:
                return empresas_data['empresa']
            return []
        except:
            return []
    

    
    def _calcular_num_empresas_presentadas(self):
        """Calcular automáticamente el número de empresas presentadas desde la tabla"""
        try:
            if not hasattr(self, 'TwEmpresas'):
                return 0
            
            tabla = self.TwEmpresas
            count = 0
            
            for fila in range(tabla.rowCount()):
                nombre_item = tabla.item(fila, 0)
                if nombre_item and nombre_item.text().strip():
                    count += 1
            
            print(f"[CAMBIO_CONTRATO] 📊 Cálculo automático: {count} empresas en tabla")
            return count
            
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error calculando empresas presentadas: {e}")
            return 0

    def _cargar_lineedit(self, widget, contract_data):
        try:
            valor = str(contract_data.get(widget.objectName(), ''))
            widget.setText(valor)
            # LOGGING ESPECIAL para campos críticos que son QLineEdit
            if widget.objectName() in ['numEmpresasPresentadas', 'numEmpresasSolicitadas']:
                print(f"[CAMBIO_CONTRATO] QLineEdit {widget.objectName()}: '{valor}' (CRÍTICO)")
                # Si está vacío, intentar cargar desde tabla de empresas
                if not valor and widget.objectName() == 'numEmpresasPresentadas':
                    valor_calculado = self._calcular_num_empresas_presentadas()
                    if valor_calculado:
                        widget.setText(str(valor_calculado))
                        print(f"[CAMBIO_CONTRATO] 📊 AUTO-CALCULADO numEmpresasPresentadas: '{valor_calculado}'")
            elif valor:  # Solo mostrar si tiene valor
                print(f"[CAMBIO_CONTRATO] QLineEdit {widget.objectName()}: '{valor}'")
        except:
            pass
            
    def _cargar_textedit(self, widget, contract_data):
        try:
            valor = str(contract_data.get(widget.objectName(), ''))
            widget.setPlainText(valor)
            if valor:  # Solo mostrar si tiene valor
                print(f"[CAMBIO_CONTRATO] QTextEdit {widget.objectName()}: '{valor[:50]}{'...' if len(valor) > 50 else ''}'")
        except:
            pass
            
    def _cargar_doublespinbox(self, widget, contract_data):
        try:
            nombre_widget = widget.objectName()
            valor_json = contract_data.get(nombre_widget, 0)
            
            # Convertir a float de forma segura
            try:
                valor = float(str(valor_json)) if valor_json else 0.0
            except (ValueError, TypeError):
                valor = 0.0
            
            widget.setValue(valor)
            
            # Mostrar log para todos los QDoubleSpinBox
            print(f"[CAMBIO_CONTRATO] QDoubleSpinBox {nombre_widget}: '{valor}'")
            
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error cargando QDoubleSpinBox {widget.objectName()}: {e}")
            widget.setValue(0.0)
            
    def _cargar_spinbox(self, widget, contract_data):
        try:
            nombre_widget = widget.objectName()
            valor_json = contract_data.get(nombre_widget, 0)
            
            # Convertir a entero de forma segura
            try:
                valor = int(float(str(valor_json))) if valor_json else 0
            except (ValueError, TypeError):
                valor = 0
            
            widget.setValue(valor)
            
            # LOGGING ESPECIAL para campos críticos
            if nombre_widget in ['numEmpresasPresentadas', 'numEmpresasSolicitadas', 'plazoEjecucion']:
                print(f"[CAMBIO_CONTRATO] QSpinBox {nombre_widget}: '{valor}' (CRÍTICO)")
            elif valor != 0:  # Solo mostrar si tiene valor
                print(f"[CAMBIO_CONTRATO] QSpinBox {nombre_widget}: '{valor}'")
                
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error cargando QSpinBox {widget.objectName()}: {e}")
            widget.setValue(0)
            
    def _cargar_dateedit(self, widget, contract_data):
        try:
            valor = contract_data.get(widget.objectName(), '')
            if valor:
                fecha = datetime.strptime(valor, "%Y-%m-%d").date()
                widget.setDate(QDate(fecha.year, fecha.month, fecha.day))
        except:
            pass
        
    def _cargar_timeedit(self, widget, contract_data):
        """Cargar QTimeEdit optimizado"""
        try:
            valor = contract_data.get(widget.objectName(), '')
            if valor and isinstance(valor, str):
                # Parsear formato HH:mm
                from datetime import datetime
                time_obj = datetime.strptime(valor, "%H:%M").time()
                qtime = QTime(time_obj.hour, time_obj.minute)
                widget.setTime(qtime)
                return True
        except:
            pass
        return False
        
    def _cargar_combobox(self, widget, contract_data):
        """Cargar QComboBox optimizado"""
        try:
            valor = contract_data.get(widget.objectName(), '')
            if valor:
                widget.setCurrentText(str(valor))
                return True
        except:
            pass
        return False

    def _cargar_firmantes_optimizado(self, contract_data):
        """Cargar firmantes de forma optimizada"""
        try:
            if hasattr(self, 'contract_manager') and self.contract_manager:
                gestor = getattr(self.contract_manager, 'gestor_json', None)
                if gestor and gestor.datos:
                    firmantes = gestor.datos.get('firmantes', {})
                    if firmantes:
                        
                        # 🆕 CARGAR TODOS LOS FIRMANTES DE UNA VEZ
                        firmantes_widgets = []
                        for campo_firmante, valor in firmantes.items():
                            if hasattr(self, campo_firmante):
                                widget = getattr(self, campo_firmante)
                                firmantes_widgets.append((widget, campo_firmante, valor))
                        
                        # Bloquear, cargar y desbloquear en lote
                        for widget, campo, valor in firmantes_widgets:
                            widget.blockSignals(True)
                            if hasattr(widget, 'setText'):
                                widget.setText(str(valor))
                            widget.blockSignals(False)
                        
                        
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando firmantes: {e}")
            pass

    
    def _cargar_tablas_especiales(self, contract_data):
        """Cargar tablas especiales - MÉTODO AGREGADO"""
        try:
            # Cargar tabla de empresas
            if hasattr(self, 'TwEmpresas') and 'empresas' in contract_data:
                self._cargar_tabla_empresas(contract_data)
            
            # Cargar tabla de ofertas  
            if hasattr(self, 'TwOfertas') and ('ofertas' in contract_data or 'empresas' in contract_data):
                self._cargar_tabla_ofertas_optimizada(contract_data)

                
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando tablas especiales: {e}")
            pass
    
    def _cargar_tabla_empresas(self, contract_data):
        """Cargar tabla de empresas desde JSON - MÉTODO RECONSTRUIDO"""
        try:
            empresas_data = contract_data.get('empresas', [])
            if not empresas_data:
                return
                
            tabla = self.TwEmpresas
            tabla.blockSignals(True)
            
            # Configurar número de filas
            tabla.setRowCount(len(empresas_data))
            
            from PyQt5.QtWidgets import QTableWidgetItem
            
            # Cargar datos de empresas
            for i, empresa in enumerate(empresas_data):
                if isinstance(empresa, dict):
                    # Columna 0: Nombre
                    tabla.setItem(i, 0, QTableWidgetItem(empresa.get('nombre', '')))
                    # Columna 1: NIF
                    tabla.setItem(i, 1, QTableWidgetItem(empresa.get('nif', '')))
                    # Columna 2: Email
                    tabla.setItem(i, 2, QTableWidgetItem(empresa.get('email', '')))
                    # Columna 3: Contacto
                    tabla.setItem(i, 3, QTableWidgetItem(empresa.get('contacto', '')))
            
            tabla.blockSignals(False)
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando tabla empresas: {e}")
            pass
            if hasattr(self, 'TwEmpresas'):
                self.TwEmpresas.blockSignals(False)
    
    
    def on_contract_loaded(self, contract_data):
        """Callback cuando se carga un contrato - OPTIMIZADO"""
        try:
            nombre_contrato = contract_data.get('nombreObra', 'Sin nombre')
            
            # MOSTRAR tabWidget cuando se carga un contrato
            if hasattr(self, 'tabWidget'):
                self.tabWidget.setVisible(True)
            
            # 🆕 RESETEAR FLAGS DE VERIFICACIÓN
            self._estructura_verificada = False
            
            # FORZAR RECARGA COMPLETA DE TODOS LOS WIDGETS
            self._cargar_datos_en_interfaz(contract_data)
            
            # Sincronizar cálculos UNA VEZ
            if hasattr(self, 'controlador_calculos'):
                self.controlador_calculos.sincronizar_empresas_ofertas(self)
            
            # Notificar actuaciones/facturas UNA VEZ
            if self.controlador_actuaciones_facturas:
                self.controlador_actuaciones_facturas.set_proyecto_actual(nombre_contrato, contract_data)
            
            # Actualizar PDF UNA VEZ
            if hasattr(self, 'pdf_viewer') and self.pdf_viewer and nombre_contrato:
                self.pdf_viewer.set_contract_name(nombre_contrato)
            
            # Actualizar resumen automáticamente al cargar contrato
            if hasattr(self, 'integrador_resumen') and self.integrador_resumen and nombre_contrato:
                try:
                    print(f"[ControladorGrafica] 🔄 Actualizando resumen automáticamente para: {nombre_contrato}")
                    self.integrador_resumen._on_actualizar_resumen()
                except Exception as e:
                    print(f"[ControladorGrafica] ❌ Error actualizando resumen automático: {e}")
                
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error en callback contract_loaded: {e}")
            pass
    
    def on_contract_cleared(self):
        """Callback cuando se limpia/deselecciona un contrato"""
        try:
            # OCULTAR tabWidget cuando no hay contrato seleccionado
            if hasattr(self, 'tabWidget'):
                self.tabWidget.setVisible(False)
            
            # Limpiar PDF viewer
            if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
                self.pdf_viewer.set_contract_name("")
            
            # Limpiar actuaciones/facturas
            if self.controlador_actuaciones_facturas:
                self.controlador_actuaciones_facturas.limpiar_proyecto_actual()
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error en callback contract_cleared: {e}")
            pass
            
    
    def _migrar_estructura_antigua(self, empresas_dict, contract_data):
        """NUEVA: Migrar estructura antigua a nueva estructura unificada"""
        try:
            
            empresas_antiguas = empresas_dict.get('empresa', [])
            ofertas_antiguas = contract_data.get('ofertas', [])
            
            empresas_unificadas = []
            
            for i, empresa in enumerate(empresas_antiguas):
                empresa_unificada = {
                    'nombre': empresa.get('nombre', empresa.get('empresa', '')),
                    'nif': empresa.get('nif', empresa.get('cif', '')),
                    'email': empresa.get('email', ''),
                    'contacto': empresa.get('contacto', empresa.get('persona de contacto', '')),
                    'ofertas': ''  # Valor por defecto
                }
                
                # Buscar oferta correspondiente
                if i < len(ofertas_antiguas):
                    oferta_antigua = ofertas_antiguas[i]
                    if isinstance(oferta_antigua, dict):
                        empresa_unificada['ofertas'] = oferta_antigua.get('oferta_(€)', '')
                
                empresas_unificadas.append(empresa_unificada)
            
            return empresas_unificadas
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error migrando estructura: {e}")
            pass
            return []
    def _cargar_tabla_empresas(self, contract_data):
        """NUEVA: Cargar tabla con estructura unificada"""
        try:
            if not hasattr(self, 'TwEmpresas'):
                return

            self.TwEmpresas.blockSignals(True)
            self.TwEmpresas.setRowCount(0)

            # 🆕 NUEVA ESTRUCTURA: Obtener array directo de empresas
            empresas_lista = contract_data.get('empresas', [])
            
            # 🔄 MIGRACIÓN: Si encuentra estructura antigua, convertir
            if isinstance(empresas_lista, dict) and 'empresa' in empresas_lista:
                empresas_lista = self._migrar_estructura_antigua(empresas_lista, contract_data)

            # Cargar empresas unificadas
            if empresas_lista:
                from PyQt5.QtWidgets import QTableWidgetItem
                self.TwEmpresas.setRowCount(len(empresas_lista))

                for i, empresa in enumerate(empresas_lista):
                    if isinstance(empresa, dict):
                        # ✅ CAMPOS UNIFICADOS
                        nombre = empresa.get('nombre', '')
                        nif = empresa.get('nif', '')
                        email = empresa.get('email', '')
                        contacto = empresa.get('contacto', '')
                        
                        self.TwEmpresas.setItem(i, 0, QTableWidgetItem(nombre))
                        self.TwEmpresas.setItem(i, 1, QTableWidgetItem(nif))
                        self.TwEmpresas.setItem(i, 2, QTableWidgetItem(email))
                        self.TwEmpresas.setItem(i, 3, QTableWidgetItem(contacto))

            # 🆕 CARGAR TABLA OFERTAS DESDE MISMA ESTRUCTURA
            empresas_lista = self._obtener_empresas_lista(contract_data)
            self._cargar_tabla_ofertas_optimizada(contract_data)

            self.TwEmpresas.blockSignals(False)
            
            # 🔗 Sincronizar tablas después de cargar datos
            if hasattr(self, 'controlador_tablas') and self.controlador_tablas:
                self.controlador_tablas.sincronizar_tablas()

        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando tabla empresas unificada: {e}")
            pass
            if hasattr(self, 'TwEmpresas'):
                self.TwEmpresas.blockSignals(False)

    def _cargar_tabla_ofertas_optimizada(self, contract_data):
        """Cargar tabla de ofertas desde estructura empresas unificada - FUNCIÓN ÚNICA"""
        try:
            # Usar método unificado para obtener empresas
            empresas_data = self._obtener_empresas_lista(contract_data)
            
            if not hasattr(self, 'TwOfertas') or not isinstance(empresas_data, list):
                return

            self.TwOfertas.blockSignals(True)
            self.TwOfertas.setRowCount(len(empresas_data))

            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtCore import Qt

            # Preparar todos los items de ofertas
            items_ofertas = []
            for i, empresa in enumerate(empresas_data):
                nombre = empresa.get("nombre", "")
                # Usar campo 'ofertas' de la estructura unificada
                ofertas = empresa.get("ofertas", "")
                if ofertas is None:
                    ofertas = ""
                else:
                    ofertas = str(ofertas)
                
                items_ofertas.extend([
                    (i, 0, nombre, True),   # True = solo lectura
                    (i, 1, ofertas, False)  # False = editable
                ])

            # Crear todos los items de una vez
            for fila, col, texto, solo_lectura in items_ofertas:
                item = QTableWidgetItem(texto)
                if solo_lectura:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.TwOfertas.setItem(fila, col, item)

            self.TwOfertas.blockSignals(False)
            # print(f"[ControladorGrafica] ✅ Ofertas cargadas desde empresas unificadas: {len(empresas_data)} ofertas")
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando ofertas desde empresas: {e}")
            pass
            if hasattr(self, 'TwOfertas'):
                self.TwOfertas.blockSignals(False)

    def _cargar_fechas(self, contract_data):
        """Cargar fechas desde el JSON"""
        try:
            from PyQt5.QtCore import QDate
            import datetime
            
            campos_fecha = {
                'fechaInicio': 'fechaInforme',
                'fechaFinalizacion': 'fechaFinal', 
                'fechaGeneracionInicio': 'diaApertura',
                'fechaGeneracionAdjudicacion': 'fechaAdjudicacion',
                'fechaCreacion': 'fechaProyecto'
            }
            
            for json_field, ui_field in campos_fecha.items():
                if json_field in contract_data and contract_data[json_field] and hasattr(self, ui_field):
                    try:
                        fecha_str = contract_data[json_field]
                        if isinstance(fecha_str, str):
                            fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                            qdate = QDate(fecha.year, fecha.month, fecha.day)
                            
                            widget = getattr(self, ui_field)
                            if hasattr(widget, 'setDate'):
                                widget.setDate(qdate)
                    except Exception:
                        pass
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando fechas: {e}")
            pass

    def _cargar_tipo_contrato(self, contract_data):
        """Cargar tipo de contrato y aplicar configuraciones"""
        try:
            tipo = contract_data.get('tipoActuacion', '').lower()
            
            if tipo:
                self._configurar_por_tipo_contrato(tipo.title())
                self._actualizar_pestanas_por_tipo(tipo)
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error cargando tipo contrato: {e}")
            pass

    def _obtener_empresas_lista(self, contract_data: Dict[str, Any]) -> List[Dict]:
        """Obtener lista de empresas usando el método del controlador de documentos"""
        try:
            if hasattr(self, 'controlador_documentos') and self.controlador_documentos:
                return self.controlador_documentos._obtener_empresas_lista(contract_data)
            else:
                raise AttributeError("controlador_documentos no está disponible")
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error obteniendo empresas: {e}")
            pass
            raise e
        
    def _cargar_empresas_directas(self, contract_data):
        """Cargar empresas directamente en la tabla"""
        try:
            if not hasattr(self, 'TwEmpresas'):
                return
            
            # Bloquear señales temporalmente para mejor rendimiento
            self.TwEmpresas.blockSignals(True)
            
            # Limpiar tabla
            self.TwEmpresas.setRowCount(0)
            
            # Obtener empresas
            empresas_data = contract_data.get('empresas', {})
            if isinstance(empresas_data, dict):
                empresas_lista = empresas_data.get('empresa', [])
            else:
                empresas_lista = empresas_data if isinstance(empresas_data, list) else []
            
            # Cargar empresas de una vez
            if empresas_lista:
                self.TwEmpresas.setRowCount(len(empresas_lista))
                from PyQt5.QtWidgets import QTableWidgetItem
                
                for i, empresa in enumerate(empresas_lista):
                    if isinstance(empresa, dict):
                        self.TwEmpresas.setItem(i, 0, QTableWidgetItem(empresa.get('empresa', '')))
                        self.TwEmpresas.setItem(i, 1, QTableWidgetItem(empresa.get('cif', '')))
                        self.TwEmpresas.setItem(i, 2, QTableWidgetItem(empresa.get('email', '')))
                        self.TwEmpresas.setItem(i, 3, QTableWidgetItem(empresa.get('persona de contacto', '')))
            
            # Reactivar señales
            self.TwEmpresas.blockSignals(False)
            
        except Exception:
            if hasattr(self, 'TwEmpresas'):
                self.TwEmpresas.blockSignals(False)

    def on_contract_type_changed(self, tipo_contrato):
        """Callback cuando cambia el tipo de contrato"""
        print(f"[CALLBACK] 📡 on_contract_type_changed disparado con tipo: '{tipo_contrato}'")
        try:
            print(f"[CALLBACK] ⚙️ Configurando por tipo de contrato...")
            self._configurar_por_tipo_contrato(tipo_contrato)
            
            print(f"[CALLBACK] 📑 Actualizando pestañas...")
            self._actualizar_pestanas_por_tipo(tipo_contrato)
            
            # Actualizar resumen automáticamente al cambiar tipo de contrato
            if hasattr(self, 'integrador_resumen') and self.integrador_resumen:
                try:
                    print(f"[CALLBACK] 🔄 Actualizando resumen por cambio de tipo: {tipo_contrato}")
                    self.integrador_resumen._on_actualizar_resumen()
                except Exception as e:
                    print(f"[CALLBACK] ❌ Error actualizando resumen por tipo: {e}")
            
            print(f"[CALLBACK] ✅ Callback completado exitosamente")
        except Exception as e:
            print(f"[CALLBACK] ❌ Error en on_contract_type_changed: {e}")
            import traceback
            traceback.print_exc()

    def on_contract_cleared(self):
        """Callback cuando se limpia el contrato"""
        try:
            if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
                self.pdf_viewer.set_contract_name("")
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error en on_contract_cleared: {e}")
            pass

    def update_pdf_for_current_contract(self):
        """Forzar actualización del PDF para el contrato actual - CON TEMPORIZADO"""
        import time
        inicio = time.time()
        try:
            print(f"[PDF] 🔍 Verificando contract_manager - {(time.time() - inicio)*1000:.1f}ms")
            if hasattr(self, 'contract_manager') and self.contract_manager:
                print(f"[PDF] 📊 Obteniendo datos del contrato - {(time.time() - inicio)*1000:.1f}ms")
                current_contract_data = self.contract_manager.get_current_contract_data()
                print(f"[PDF] 📊 get_current_contract_data() completado - {(time.time() - inicio)*1000:.1f}ms")
                
                if current_contract_data:
                    contract_name = current_contract_data.get('nombreObra', '')
                    print(f"[PDF] 📄 Nombre contrato obtenido - {(time.time() - inicio)*1000:.1f}ms")
                    
                    if contract_name and hasattr(self, 'pdf_viewer') and self.pdf_viewer:
                        print(f"[PDF] 🔄 Estableciendo nombre en PDF viewer - {(time.time() - inicio)*1000:.1f}ms")
                        self.pdf_viewer.set_contract_name(contract_name)
                        print(f"[PDF] ✓ PDF viewer actualizado - {(time.time() - inicio)*1000:.1f}ms")
                        return True
            print(f"[PDF] ❌ No se pudo actualizar - {(time.time() - inicio)*1000:.1f}ms")
            return False
        except Exception as e:
            print(f"[PDF] ❌ Error: {e} - {(time.time() - inicio)*1000:.1f}ms")
            return False

    # =================== ANIMACIONES ELIMINADAS ===================
    # Métodos de animación eliminados - innecesarios para la funcionalidad principal
    # Esto reduce el código en ~175 líneas y mejora el rendimiento

    def _setup_componentes_ui(self):
        """Configurar componentes específicos de la UI"""
        try:
            # 1. Configurar tablas
            if hasattr(self, 'TwEmpresas'):
                self.controlador_tablas.setup_tabla_empresas(self.TwEmpresas)
            
            if hasattr(self, 'TwOfertas'):
                self.controlador_tablas.setup_tabla_ofertas(self.TwOfertas)
            
            # 2. Configurar sincronización de tablas
            self._configurar_sincronizacion_tablas()
            
            # 3. Configurar validadores y cálculos
            
            # 4. Inicializar controlador de actuaciones/facturas
            try:
                self.controlador_actuaciones_facturas = ControladorActuacionesFacturas(self)
            except Exception as e:
                # print(f"[ControladorGrafica] ⚠️ Error controlador actuaciones: {e}")
                pass
            

            
            # 6. Configurar tooltips
            self._setup_tooltips()
            
            # 7. Inicializar UI
            self._initialize_ui()
            
            # 8. Configurar auto-guardado
            self._configurar_auto_guardado()
            
            # 9. Configurar cambios de pestañas
            if hasattr(self, 'tabWidget'):
                self.tabWidget.currentChanged.connect(self.on_tab_changed)
            
            # 10. Configurar eventos de pérdida de foco (después de que UI esté lista)
            if hasattr(self, 'controlador_eventos_ui'):
                self.controlador_eventos_ui.configurar_eventos_perdida_foco()
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando componentes UI: {e}")
            pass

    def _configurar_sincronizacion_tablas(self):
        """Configurar sincronización automática entre tablas de empresas y ofertas"""
        try:
            if not all(hasattr(self, tabla) for tabla in ['TwEmpresas', 'TwOfertas']):
                return
            
            # Conectar la señal de selección de empresa con la actualización de ofertas
            if hasattr(self, 'controlador_tablas') and self.controlador_tablas:
                print("[ControladorGrafica] 🔗 Configurando sincronización TwEmpresas → TwOfertas")
                
                # Conectar la señal empresa_seleccionada para actualizar ofertas
                self.controlador_tablas.empresa_seleccionada.connect(
                    lambda fila: self._on_empresa_seleccionada_actualizar_ofertas(fila)
                )
                
                print("[ControladorGrafica] ✅ Sincronización configurada correctamente")
            
        except Exception as e:
            print(f"[ControladorGrafica] ❌ Error configurando sincronización: {e}")
    
    def _on_empresa_seleccionada_actualizar_ofertas(self, fila_seleccionada):
        """Actualizar tabla de ofertas cuando se selecciona una empresa"""
        try:
            print(f"[ControladorGrafica] 📊 Empresa seleccionada fila: {fila_seleccionada}")
            
            if not hasattr(self, 'controlador_tablas') or not self.controlador_tablas:
                return
                
            if not hasattr(self, 'TwOfertas'):
                return
            
            # Obtener datos de la empresa seleccionada
            if hasattr(self, 'TwEmpresas') and fila_seleccionada < self.TwEmpresas.rowCount():
                from PyQt5.QtWidgets import QTableWidgetItem
                
                # Obtener nombre de la empresa seleccionada
                nombre_item = self.TwEmpresas.item(fila_seleccionada, 0)
                nombre_empresa = nombre_item.text() if nombre_item else ""
                
                if nombre_empresa.strip():
                    print(f"[ControladorGrafica] 🏢 Actualizando ofertas para empresa: '{nombre_empresa}'")
                    
                    # Buscar la oferta correspondiente en la tabla de ofertas y resaltarla
                    for row in range(self.TwOfertas.rowCount()):
                        oferta_empresa_item = self.TwOfertas.item(row, 0)
                        if oferta_empresa_item and oferta_empresa_item.text().strip() == nombre_empresa.strip():
                            # Seleccionar la fila correspondiente en ofertas
                            self.TwOfertas.selectRow(row)
                            
                            # Hacer foco en la celda de la oferta (columna 1) para facilitar edición
                            self.TwOfertas.setCurrentCell(row, 1)
                            
                            print(f"[ControladorGrafica] ✅ Fila {row} seleccionada y enfocada en TwOfertas")
                            break
                    else:
                        print(f"[ControladorGrafica] ⚠️ No se encontró oferta para empresa: '{nombre_empresa}'")
                        # Limpiar selección si no hay coincidencia
                        self.TwOfertas.clearSelection()
                        
                        # Si no existe la empresa en ofertas, agregarla
                        self._agregar_empresa_a_ofertas(nombre_empresa, fila_seleccionada)
                        
        except Exception as e:
            print(f"[ControladorGrafica] ❌ Error actualizando ofertas: {e}")

    def _agregar_empresa_a_ofertas(self, nombre_empresa, fila_empresa):
        """Agregar una empresa nueva a la tabla de ofertas"""
        try:
            from PyQt5.QtWidgets import QTableWidgetItem
            
            # Buscar una fila vacía en ofertas o agregar una nueva
            fila_oferta = -1
            
            # Primero intentar usar la misma fila que la empresa
            if fila_empresa < self.TwOfertas.rowCount():
                oferta_existente = self.TwOfertas.item(fila_empresa, 0)
                if not oferta_existente or not oferta_existente.text().strip():
                    fila_oferta = fila_empresa
            
            # Si no se pudo usar la misma fila, buscar primera fila vacía
            if fila_oferta == -1:
                for row in range(self.TwOfertas.rowCount()):
                    item = self.TwOfertas.item(row, 0)
                    if not item or not item.text().strip():
                        fila_oferta = row
                        break
            
            # Si no hay filas vacías, expandir la tabla
            if fila_oferta == -1:
                fila_oferta = self.TwOfertas.rowCount()
                self.TwOfertas.setRowCount(fila_oferta + 1)
            
            # Agregar la empresa a la tabla de ofertas
            self.TwOfertas.setItem(fila_oferta, 0, QTableWidgetItem(nombre_empresa))
            self.TwOfertas.setItem(fila_oferta, 1, QTableWidgetItem(""))  # Oferta vacía para editar
            
            # Seleccionar y enfocar la nueva fila
            self.TwOfertas.selectRow(fila_oferta)
            self.TwOfertas.setCurrentCell(fila_oferta, 1)  # Enfocar en columna de oferta
            
            print(f"[ControladorGrafica] ✅ Empresa '{nombre_empresa}' agregada a ofertas en fila {fila_oferta}")
            
        except Exception as e:
            print(f"[ControladorGrafica] ❌ Error agregando empresa a ofertas: {e}")

    def _configurar_auto_guardado(self):
        """Configurar auto-guardado usando controlador separado"""
        try:
            if hasattr(self, 'controlador_autosave'):
                # Conectar dependencias del autosave
                self.controlador_autosave.set_dependencies(
                    self.controlador_json, 
                    self.contract_manager
                )
                self.controlador_autosave.configurar_auto_guardado_completo()
        
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando auto-guardado: {e}")
            pass

    def on_tab_changed(self, index):
        """Manejar cambio de pestañas"""
        try:
            if not hasattr(self, 'tabWidget') or not self.contract_manager:
                return
                
            contrato_actual = self.contract_manager.get_current_contract()
            if not contrato_actual:
                return
                
            tab_name = self.tabWidget.tabText(index)
            
            # Solo actualizar PDF si es necesario
            if "PDF" in tab_name or "Documentos" in tab_name:
                self.update_pdf_for_current_contract()
                # 🆕 ACTIVAR CARGA AUTOMÁTICA DE PDF
                if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
                    self.pdf_viewer.on_tab_activated()
                    # print(f"[ControladorGrafica] 📄 Activada carga automática de PDF para pestaña: {tab_name}")
            
            # Actualizar tabla de seguimiento si el tab la contiene
            widget_actual = self.tabWidget.widget(index)
            if widget_actual and hasattr(widget_actual, 'findChild'):
                from PyQt5.QtWidgets import QTableWidget
                tabla_seguimiento = widget_actual.findChild(QTableWidget, 'Tabla_seguimiento')
                if tabla_seguimiento:
                    print(f"[ControladorGrafica] 🔄 Actualizando tabla de seguimiento al cambiar a tab: {tab_name}")
                    # Actualizar el resumen automáticamente
                    if hasattr(self, 'integrador_resumen') and self.integrador_resumen:
                        try:
                            self.integrador_resumen._on_actualizar_resumen()
                        except Exception as e:
                            print(f"[ControladorGrafica] ❌ Error actualizando resumen: {e}")
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error en cambio de tab: {e}")
            pass

    def on_pdf_changed(self, pdf_path: str):
        """Callback cuando cambia el PDF"""
        # Opcionalmente se puede agregar lógica adicional aquí
        # print(f"[ControladorGrafica] PDF cambiado: {os.path.basename(pdf_path) if pdf_path else 'Ninguno'}")

    def _setup_pdf_viewer(self):
        """Configurar visor PDF en la pestaña correspondiente"""
        try:
            self.pdf_viewer = setup_pdf_viewer_simple(self, "contenedor_pdf")
            
            if self.pdf_viewer:
                self.pdf_viewer.pdf_changed.connect(self.on_pdf_changed)
                
                if hasattr(self, 'contract_manager') and self.contract_manager:
                    current_contract = self.contract_manager.get_current_contract()
                    if current_contract:
                        self.pdf_viewer.set_contract_name(current_contract)
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error configurando visor PDF: {e}")
            pass


    def _crear_carpeta_con_controlador_archivos(self):
        """Crear carpeta usando el controlador de archivos existente"""
        try:
            if not self.contract_manager or not self.contract_manager.get_current_contract():
                return
            
            current_text = ""
            if hasattr(self, 'comboBox'):
                current_text = self.comboBox.currentText()
            
            if not current_text or current_text.lower().startswith("seleccionar"):
                return
            
            if hasattr(self, 'contract_manager') and self.contract_manager:
                carpeta_creada = self.contract_manager.crear_carpeta_para_contrato_actual()
            
        except Exception:
            pass


    def _configurar_eventos_ui(self):
        """Configurar eventos de la interfaz"""
        try:
            if hasattr(self, 'controlador_eventos_ui'):
                self.controlador_eventos_ui.setup_event_handlers()
        except Exception:
            pass

    def _setup_tooltips(self):
        """Configurar tooltips de ayuda"""
        try:
            tooltips = {
                'Generar_Acta_Inicio': '📄 Generar acta de inicio',
                'Generar_Cartas_inv': '✉️ Generar cartas de invitación',
                'Generar_acta_adj': '🏆 Generar acta de adjudicación',
                'Generar_carta_adj': '📮 Generar cartas de adjudicación',
                'Generar_acta_liq': '💰 Generar acta de liquidación',
                'Generar_replanteo': '📐 Generar acta de replanteo',
                'Generar_recepcion': '✅ Generar acta de recepción',
                'Generar_Director': '👨‍💼 Generar nombramiento director'
            }
            
            for widget_name, tooltip in tooltips.items():
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    widget.setToolTip(tooltip)
                    
        except Exception:
            pass

    def _initialize_ui(self):
        """Inicializar estado de la UI"""
        try:
            self.setWindowTitle("Generador de Actas ADIF - v3.0")
            
            # === CREAR BARRA DE TÍTULO PERSONALIZADA ===
            self._create_custom_title_bar()
            
            try:
                # Usar el nuevo sistema de rutas para el icono
                from controladores.controlador_routes import ControladorRutas
                rutas = ControladorRutas()
                icon_path = rutas.get_ruta_icono("icono.ico")
                
                if icon_path:
                    try:
                        self.setWindowIcon(QIcon(icon_path))
                    except:
                        pass
            except Exception as icon_error:
                # print(f"[ControladorGrafica] ⚠️ Error cargando icono: {icon_error}")
                pass
                pass
            
            if hasattr(self, 'tabWidget'):
                self.tabWidget.setVisible(False)
                
        except Exception:
            pass
    def _create_custom_title_bar(self):
        """Crear barra de título personalizada simple"""
        try:
            # Crear widget de título que se superpone al header existente
            if hasattr(self, 'main_header'):
                # Usar el header existente y añadir botones
                title_frame = QWidget(self.main_header)
                title_frame.setGeometry(1650, 10, 180, 35)
                
                # Layout para botones
                from PyQt5.QtWidgets import QHBoxLayout
                layout = QHBoxLayout(title_frame)
                layout.setContentsMargins(5, 5, 5, 5)
                layout.setSpacing(5)
                
                # Botones de ventana
                btn_minimize = QPushButton("−")
                btn_minimize.setFixedSize(30, 25)
                btn_minimize.clicked.connect(self.showMinimized)
                btn_minimize.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 193, 7, 0.8);
                        border: none;
                        border-radius: 3px;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 193, 7, 1);
                    }
                """)
                
                btn_maximize = QPushButton("□")
                btn_maximize.setFixedSize(30, 25)
                btn_maximize.clicked.connect(self.toggle_maximize)
                btn_maximize.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(40, 167, 69, 0.8);
                        border: none;
                        border-radius: 3px;
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(40, 167, 69, 1);
                    }
                """)
                
                btn_close = QPushButton("×")
                btn_close.setFixedSize(30, 25)
                btn_close.clicked.connect(self.close)
                btn_close.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(220, 53, 69, 0.8);
                        border: none;
                        border-radius: 3px;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: rgba(220, 53, 69, 1);
                    }
                """)
                
                # Añadir botones al layout
                layout.addWidget(btn_minimize)
                layout.addWidget(btn_maximize)
                layout.addWidget(btn_close)
                
                title_frame.show()
                
        except Exception as e:
            print(f"Error creando barra de título: {e}")

    def toggle_maximize(self):
        """Alternar entre maximizado y normal"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()      
    def load_initial_data(self):
        try:
            if self.proyecto_actual:
                pass
        except Exception:
            pass

    # =================== MÉTODOS DE ACCIONES DE TABLA ===================

    def _agregar_empresa(self):
        """Agregar fila a tabla de empresas"""
        try:
            if hasattr(self, 'TwEmpresas') and self.controlador_tablas:
                self.controlador_tablas.agregar_fila(self.TwEmpresas)
        except Exception:
            pass

    def _quitar_empresa(self):
        """Quitar fila seleccionada de tabla de empresas"""
        try:
            if not hasattr(self, 'TwEmpresas'):
                return
            
            tabla = self.TwEmpresas
            
            if tabla.rowCount() == 0:
                QMessageBox.information(
                    self, "Sin filas", 
                    "No hay empresas para eliminar"
                )
                return
            
            fila_seleccionada = tabla.currentRow()
            
            if fila_seleccionada >= 0:
                item_nombre = tabla.item(fila_seleccionada, 0)
                nombre_empresa = item_nombre.text() if item_nombre else f"Fila {fila_seleccionada + 1}"
                
                respuesta = QMessageBox.question(
                    self, "Confirmar eliminación",
                    f"¿Eliminar la empresa:\n'{nombre_empresa}'?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if respuesta == QMessageBox.Yes:
                    tabla.removeRow(fila_seleccionada)
                    
                    
                    filas_restantes = tabla.rowCount()
                    if filas_restantes > 0:
                        nueva_seleccion = min(fila_seleccionada, filas_restantes - 1)
                        tabla.selectRow(nueva_seleccion)
            else:
                respuesta = QMessageBox.question(
                    self, "Sin selección",
                    f"No hay fila seleccionada.\n\n"
                    f"📊 Total de empresas: {tabla.rowCount()}\n\n"
                    f"¿Eliminar la última fila?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if respuesta == QMessageBox.Yes:
                    ultima_fila = tabla.rowCount() - 1
                    tabla.removeRow(ultima_fila)
                    
                    
                    if tabla.rowCount() > 0:
                        tabla.selectRow(tabla.rowCount() - 1)
            
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error eliminando empresa:\n{str(e)}"
            )

    # =================== MÉTODOS DE ARCHIVOS Y PROYECTOS ===================

    def _guardar_proyecto(self):
        """Guardar proyecto actual"""
        try:
            if self.proyecto_actual:
                pass
            else:
                archivo, _ = QFileDialog.getSaveFileName(
                    self, "Guardar Proyecto Como", "", "Archivos JSON (*.json)"
                )
                
                if archivo:
                    self.proyecto_actual = archivo
                    QMessageBox.information(
                        self, "Proyecto Guardado", 
                        f"✅ Proyecto guardado como:\n{archivo}"
                    )
                
        except Exception:
            pass


    def _abrir_portafirmas(self):
        """Abrir portafirmas"""
        pass

    # =================== GESTIÓN DE TIPOS DE CONTRATO ===================

    def _cambiar_tipo_contrato(self):
        """Cambiar tipo de contrato"""
        try:
            if not self.contract_manager or not self.contract_manager.get_current_contract():
                QMessageBox.warning(self, "Advertencia", "⚠️ Debes seleccionar un contrato primero")
                return
            
            contract_data = self.contract_manager.get_current_contract_data()
            tipo_actual = contract_data.get('tipoActuacion', 'Sin tipo') if contract_data else 'Sin tipo'
            
            from .dialogo_gestionar_contratos import DialogoSeleccionTipo
            dialogo = DialogoSeleccionTipo(self, tipo_actual)
            
            if dialogo.exec_() == QDialog.Accepted:
                nuevo_tipo = dialogo.get_tipo_seleccionado()
                if nuevo_tipo:
                    self._aplicar_nuevo_tipo_contrato(nuevo_tipo)
                    
        except Exception:
            pass

    def _aplicar_nuevo_tipo_contrato(self, nuevo_tipo: str):
        """Aplicar nuevo tipo de contrato"""
        print(f"\n[CAMBIO_TIPO] =================== INICIANDO CAMBIO DE TIPO ===================")
        print(f"[CAMBIO_TIPO] 🎯 Nuevo tipo solicitado: '{nuevo_tipo}'")
        
        try:
            # 1. Obtener contrato actual
            contrato_actual = self.contract_manager.get_current_contract()
            print(f"[CAMBIO_TIPO] 📂 Contrato actual: '{contrato_actual}'")
            
            # 2. Verificar estado inicial del QLabel
            if hasattr(self, 'Tipo'):
                tipo_anterior = self.Tipo.text()
                print(f"[CAMBIO_TIPO] 🏷️ QLabel Tipo ANTES: '{tipo_anterior}'")
            else:
                print(f"[CAMBIO_TIPO] ❌ NO SE ENCONTRÓ QLabel 'Tipo'")
            
            # 3. Guardar en JSON
            print(f"[CAMBIO_TIPO] 💾 Guardando tipo en JSON...")
            if not self.controlador_json.guardar_campo_en_json(contrato_actual, 'tipoActuacion', nuevo_tipo):
                print(f"[CAMBIO_TIPO] ❌ ERROR: No se pudo guardar en JSON")
                QMessageBox.critical(self, "Error", "No se pudo guardar en JSON")
                return
            print(f"[CAMBIO_TIPO] ✅ Tipo guardado en JSON correctamente")
            
            # 4. Actualizar QLabel Tipo DIRECTAMENTE PRIMERO
            print(f"[CAMBIO_TIPO] 🏷️ Actualizando QLabel directamente...")
            if hasattr(self, 'Tipo'):
                print(f"[CAMBIO_TIPO] 📝 setText('{nuevo_tipo}')")
                self.Tipo.setText(nuevo_tipo)
                
                print(f"[CAMBIO_TIPO] 🔄 update()")
                self.Tipo.update()
                
                print(f"[CAMBIO_TIPO] 🎨 repaint()")
                self.Tipo.repaint()
                
                # Verificar que se aplicó
                texto_actual = self.Tipo.text()
                print(f"[CAMBIO_TIPO] 🏷️ QLabel Tipo DESPUÉS: '{texto_actual}'")
                
                if texto_actual == nuevo_tipo:
                    print(f"[CAMBIO_TIPO] ✅ QLabel actualizado correctamente")
                else:
                    print(f"[CAMBIO_TIPO] ❌ QLabel NO se actualizó correctamente")
            else:
                print(f"[CAMBIO_TIPO] ❌ QLabel 'Tipo' no encontrado")
            
            # 5. FORZAR actualización del contract manager
            print(f"[CAMBIO_TIPO] 🔧 Sincronizando contract manager...")
            if self.contract_manager:
                print(f"[CAMBIO_TIPO] 📊 Obteniendo datos del contrato...")
                contract_data = self.contract_manager.get_current_contract_data()
                
                if contract_data:
                    expediente = contract_data.get('numeroExpediente', 'Sin expediente')
                    print(f"[CAMBIO_TIPO] 📋 Expediente: '{expediente}'")
                    
                    # Actualizar labels en contract manager
                    if hasattr(self.contract_manager, '_update_labels'):
                        print(f"[CAMBIO_TIPO] 🏷️ Actualizando labels en contract manager...")
                        self.contract_manager._update_labels(nuevo_tipo, expediente)
                        print(f"[CAMBIO_TIPO] ✅ Labels actualizados en contract manager")
                    else:
                        print(f"[CAMBIO_TIPO] ❌ Método _update_labels no encontrado")
                else:
                    print(f"[CAMBIO_TIPO] ❌ No se pudieron obtener datos del contrato")
                
                # Recargar contratos para sincronizar todo
                print(f"[CAMBIO_TIPO] 🔄 Recargando contratos...")
                self.contract_manager.reload_contracts()
                print(f"[CAMBIO_TIPO] ✅ Contratos recargados")
            else:
                print(f"[CAMBIO_TIPO] ❌ Contract manager no disponible")
            
            # 6. Actualizar UI
            print(f"[CAMBIO_TIPO] 🖥️ Actualizando UI...")
            
            print(f"[CAMBIO_TIPO] ⚙️ Configurando por tipo de contrato...")
            self._configurar_por_tipo_contrato(nuevo_tipo)
            
            print(f"[CAMBIO_TIPO] 📑 Actualizando pestañas...")
            self._actualizar_pestanas_por_tipo(nuevo_tipo)
            
            print(f"[CAMBIO_TIPO] ✅ UI actualizada")
            
            # 7. Verificación final
            if hasattr(self, 'Tipo'):
                tipo_final = self.Tipo.text()
                print(f"[CAMBIO_TIPO] 🏷️ QLabel Tipo FINAL: '{tipo_final}'")
                
                if tipo_final == nuevo_tipo:
                    print(f"[CAMBIO_TIPO] ✅ ¡ÉXITO! QLabel muestra el tipo correcto")
                else:
                    print(f"[CAMBIO_TIPO] ❌ FALLO: QLabel no muestra el tipo correcto")
            
            # 8. Mostrar confirmación
            QMessageBox.information(self, f"Tipo {nuevo_tipo}", f"✅ Tipo cambiado a {nuevo_tipo}")
            
            # 9. Trigger signal manualmente si es necesario
            print(f"[CAMBIO_TIPO] 📡 Disparando signal contract_type_changed...")
            self.on_contract_type_changed(nuevo_tipo)
            
            print(f"[CAMBIO_TIPO] =================== CAMBIO COMPLETADO ===================\n")
            
        except Exception as e:
            print(f"[CAMBIO_TIPO] ❌ ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            print(f"[CAMBIO_TIPO] =================== ERROR EN CAMBIO ===================\n")

    def _actualizar_pestanas_por_tipo(self, tipo: str):
        """Actualizar visibilidad de pestañas según el tipo de contrato"""
        try:
            if not hasattr(self, 'tabWidget'):
                return
            
            configuraciones_tabs = {
                "obras": {
                    "Proyecto": True, "Inicio": True, "Actas generales": True, "Actas obras": True, 
                    "Resumen": True, "Actuaciones": False, "facturas": False, "firmantes": True
                },
                "obra_mantenimiento": {
                    "Proyecto": True, "Inicio": True, "Actas generales": True, "Actas obras": True, 
                    "Resumen": True, "Actuaciones": False, "facturas": False, "firmantes": True
                },
                "servicios": {
                    "Proyecto": True, "Inicio": True, "Actas generales": True, "Actas obras": True,
                    "facturas": True, "Resumen": True, "Actuaciones": False, "firmantes": True
                },
                "serv_mantenimiento": {
                    "Proyecto": True, "Inicio": True, "Actas generales": True, "Actas obras": True,
                    "facturas": True, "Resumen": True, "Actuaciones": False, "firmantes": True
                }
            }
            
            config_actual = configuraciones_tabs.get(tipo.lower(), configuraciones_tabs["servicios"])
            total_tabs = self.tabWidget.count()
            
            for i in range(total_tabs):
                tab_text = self.tabWidget.tabText(i)
                debe_ser_visible = None
                
                if tab_text in config_actual:
                    debe_ser_visible = config_actual[tab_text]
                else:
                    for config_name, visible in config_actual.items():
                        if config_name.lower() in tab_text.lower() or tab_text.lower() in config_name.lower():
                            debe_ser_visible = visible
                            break
                
                if debe_ser_visible is None:
                    if tipo.lower() == "obras":
                        debe_ser_visible = not any(keyword in tab_text.lower() for keyword in ['factura', 'actuacion'])
                    elif tipo.lower() == "facturas":
                        debe_ser_visible = any(keyword in tab_text.lower() for keyword in ['factura', 'informe', 'resumen'])
                    else:
                        debe_ser_visible = 'facturasDirectas' not in tab_text
                
                self.tabWidget.setTabVisible(i, debe_ser_visible)
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error actualizando pestañas: {e}")
            pass



    def _configurar_por_tipo_contrato(self, tipo: str):
        """Aplicar configuraciones específicas según el tipo de contrato"""
        try:
            tipo_lower = tipo.lower()
            
            if tipo_lower == "obras":
                pass
            elif tipo_lower == "servicios":
                pass
            elif tipo_lower == "mantenimiento":
                self._activar_modo_mantenimiento()
            elif tipo_lower == "facturas":
                self._activar_modo_facturas()
                
        except Exception:
            pass

    def _activar_modo_mantenimiento(self):
        """Activar configuraciones específicas para contratos de mantenimiento"""
        try:
            pass
        except Exception:
            pass

    def _activar_modo_facturas(self):
        """Activar configuraciones específicas para gestión de facturas"""
        pass


    def _activar_modo_servicios(self):
        """Activar modo servicios"""
        self._aplicar_nuevo_tipo_contrato("Servicios")

    def _activar_modo_obras(self):
        """Activar modo obras"""
        self._aplicar_nuevo_tipo_contrato("Obras")

    # =================== GESTIÓN DE CONTRATOS ===================

    def mostrar_dialogo_crear_contrato(self):
        """Mostrar diálogo para crear nuevo contrato"""
        try:
            
            from .dialogo_gestionar_contratos import DialogoCrearContrato
            from PyQt5.QtWidgets import QDialog
            
            dialogo = DialogoCrearContrato(self)
            
            resultado = dialogo.exec_()
            
            if resultado == QDialog.Accepted:
                
                if hasattr(dialogo, 'result') and dialogo.result:
                    
                    # Verificar controlador JSON
                    if not hasattr(self, 'controlador_json') or not self.controlador_json:
                        # print(f"[ControladorGrafica] ❌ controlador_json no disponible")
                        QMessageBox.critical(self, "Error", "Controlador JSON no disponible")
                        return
                    
                    
                    # Verificar si el método existe
                    if hasattr(self.controlador_json, 'crear_contrato_con_carpetas'):
                        exito, mensaje = self.controlador_json.crear_contrato_con_carpetas(dialogo.result)
                    elif hasattr(self.controlador_json, 'crear_contrato_nuevo'):
                        # print(f"[ControladorGrafica] ⚠️ Usando crear_contrato_nuevo en su lugar")
                        exito = self.controlador_json.crear_contrato_nuevo(dialogo.result)
                        mensaje = "Contrato creado" if exito else "Error creando contrato"
                    else:
                        # print(f"[ControladorGrafica] ❌ No existe método de creación")
                        QMessageBox.critical(self, "Error", "Método de creación no encontrado")
                        return
                    
                    
                    if exito:
                        
                        # INICIALIZAR WIDGETS VACÍOS PARA OBRA NUEVA
                        print("[ControladorGrafica] Inicializando widgets para obra nueva...")
                        self._inicializar_widgets_vacios()
                        
                        # RECARGAR CONTRATOS - VERSIÓN MEJORADA
                        if self.contract_manager:
                            print("[ControladorGrafica] 🔄 Recargando contratos después de crear...")
                            
                            # Forzar recarga completa
                            self.contract_manager.load_contracts_from_json()
                            
                            # Esperar un momento para que se procese
                            QApplication.processEvents()
                            
                            # Buscar y seleccionar el contrato recién creado
                            nombre_creado = dialogo.result.get("nombreObra", "")
                            if nombre_creado:
                                print(f"[ControladorGrafica] 🔍 Buscando contrato: '{nombre_creado}'")
                                print(f"[ControladorGrafica] 📊 Items disponibles: {self.comboBox.count()}")
                                
                                # Buscar el contrato creado
                                index_encontrado = -1
                                for i in range(self.comboBox.count()):
                                    item_text = self.comboBox.itemText(i)
                                    if nombre_creado.lower().strip() == item_text.lower().strip():
                                        index_encontrado = i
                                        break
                                
                                if index_encontrado >= 0:
                                    print(f"[ControladorGrafica] ✅ Contrato encontrado en índice: {index_encontrado}")
                                    self.comboBox.setCurrentIndex(index_encontrado)
                                    
                                    # Forzar procesamiento de la selección
                                    QApplication.processEvents()
                                    
                                    # Activar tabWidget si estaba oculto
                                    if hasattr(self, 'tabWidget'):
                                        self.tabWidget.setVisible(True)
                                        
                                else:
                                    print(f"[ControladorGrafica] ❌ Contrato '{nombre_creado}' no encontrado en combo")
                                    print("[ControladorGrafica] 📋 Items disponibles:")
                                    for i in range(self.comboBox.count()):
                                        print(f"   [{i}]: '{self.comboBox.itemText(i)}'")
                                    
                                    # Como fallback, seleccionar el último
                                    if self.comboBox.count() > 0:
                                        ultimo_indice = self.comboBox.count() - 1
                                        print(f"[ControladorGrafica] 🔄 Seleccionando último elemento: {ultimo_indice}")
                                        self.comboBox.setCurrentIndex(ultimo_indice)
                            else:
                                print("[ControladorGrafica] ❌ ERROR: nombreObra vacío")
                        else:
                            print("[ControladorGrafica] ❌ ERROR: contract_manager no disponible")
                        
                        QMessageBox.information(self, "Contrato Creado", mensaje)
                    else:
                        # print(f"[ControladorGrafica] ❌ Error en la creación")
                        QMessageBox.critical(self, "Error", mensaje)
                else:
                    # print(f"[ControladorGrafica] ❌ No hay datos en dialogo.result")
                    QMessageBox.warning(self, "Error", "No se obtuvieron datos del diálogo")
            else:
                # print(f"[ControladorGrafica] ⚠️ Diálogo cancelado por el usuario")
                pass
                
        except ImportError as e:
            # print(f"[ControladorGrafica] ❌ Error de importación: {e}")
            pass
            QMessageBox.critical(self, "Error", f"No se pudo importar DialogoCrearContrato: {e}")
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error inesperado: {e}")
            pass
            pass
            QMessageBox.critical(self, "Error", f"Error inesperado al crear contrato: {str(e)}")
    
    def mostrar_dialogo_clonar_contrato(self):
        """Mostrar diálogo para clonar contrato con opciones selectivas"""
        try:
            # Verificar que hay un contrato seleccionado
            if not self.contract_manager or not self.contract_manager.get_current_contract():
                QMessageBox.warning(self, "Error", "Seleccione un contrato para clonar")
                return
            
            contrato_origen = self.contract_manager.get_current_contract()
            
            # Obtener datos del contrato para mostrar opciones contextuales
            datos_contrato = None
            if self.controlador_json:
                datos_contrato = self.controlador_json.leer_contrato_completo(contrato_origen)
            
            # Mostrar diálogo de clonación avanzado
            dialogo = DialogoClonarContrato(self, contrato_origen, datos_contrato)
            
            if dialogo.exec_() == QDialog.Accepted and dialogo.result:
                # Usar nueva API con opciones selectivas
                if self.controlador_json:
                    resultado = self.controlador_json.clonar_contrato(
                        dialogo.result["origen"], 
                        dialogo.result["nuevo_nombre"],
                        dialogo.result.get("opciones", None)
                    )
                    
                    if resultado:
                        # print(f"[ControladorGrafica] ✅ Contrato clonado exitosamente: {dialogo.result['nuevo_nombre']}")
                        
                        # 🆕 INICIALIZAR WIDGETS PARA OBRA CLONADA
                        print("[ControladorGrafica] 🆕 Inicializando widgets para obra clonada...")
                        self._inicializar_widgets_vacios()
                        
                        # Recargar contratos
                        if self.contract_manager:
                            self.contract_manager.reload_contracts()
                            
                            # Seleccionar el contrato clonado
                            nombre_clonado = dialogo.result.get("nuevo_nombre", "")
                            if nombre_clonado:
                                index = self.comboBox.findText(nombre_clonado)
                                if index >= 0:
                                    self.comboBox.setCurrentIndex(index)
                                    # Forzar la carga de datos en la UI usando el evento existente
                                    if hasattr(self, 'controlador_eventos') and self.controlador_eventos:
                                        self.controlador_eventos._on_combo_changed(nombre_clonado)
                        
                        QMessageBox.information(self, "Contrato Clonado", f"Contrato clonado exitosamente: {dialogo.result['nuevo_nombre']}")
                
        except Exception as e:
            print(f"[MainWindow] ❌ Error mostrando diálogo clonar: {e}")
            QMessageBox.critical(self, "Error", f"Error clonando contrato: {e}")

    def mostrar_dialogo_borrar_contrato(self):
        """Mostrar diálogo para borrar contrato"""
        try:
            
            # Verificar que hay un contrato seleccionado
            if not self.contract_manager or not self.contract_manager.get_current_contract():
                # print(f"[ControladorGrafica] ❌ No hay contrato seleccionado")
                QMessageBox.warning(
                    self, "Sin Selección", 
                    "⚠️ Debes seleccionar un contrato para borrar"
                )
                return
            
            contrato_seleccionado = self.contract_manager.get_current_contract()
            datos_contrato = self.contract_manager.get_current_contract_data() or {}
            
            
            # Importar y crear diálogo
            try:
                from .dialogo_gestionar_contratos import DialogoBorrarContrato
                from PyQt5.QtWidgets import QDialog
            except ImportError as e:
                # print(f"[ControladorGrafica] ❌ Error importando DialogoBorrarContrato: {e}")
                QMessageBox.critical(self, "Error", f"No se pudo importar el diálogo: {e}")
                return
            
            dialogo = DialogoBorrarContrato(self, contrato_seleccionado, datos_contrato)
            
            resultado = dialogo.exec_()
            
            if resultado == QDialog.Accepted:
                
                if hasattr(dialogo, 'confirmado') and dialogo.confirmado:
                    
                    # Verificar controlador JSON
                    if not hasattr(self, 'controlador_json') or not self.controlador_json:
                        # print(f"[ControladorGrafica] ❌ controlador_json no disponible")
                        QMessageBox.critical(self, "Error", "Controlador JSON no disponible")
                        return
                    
                    # Obtener información del borrado de carpeta
                    borrar_carpeta = hasattr(dialogo, 'borrar_carpeta') and dialogo.borrar_carpeta
                    
                    
                    if hasattr(self.controlador_json, 'borrar_contrato_con_carpetas'):
                        exito, mensaje = self.controlador_json.borrar_contrato_con_carpetas(contrato_seleccionado, borrar_carpeta)
                    elif hasattr(self.controlador_json, 'eliminar_contrato'):
                        # print(f"[ControladorGrafica] ⚠️ Usando eliminar_contrato en su lugar")
                        exito = self.controlador_json.eliminar_contrato(contrato_seleccionado)
                        mensaje = "Contrato eliminado" if exito else "Error eliminando contrato"
                        
                        # Si se eligió borrar carpeta, intentar borrarla manualmente
                        if exito and borrar_carpeta:
                            self._borrar_carpeta_obra(contrato_seleccionado, datos_contrato)
                    else:
                        # print(f"[ControladorGrafica] ❌ No existe método de eliminación")
                        QMessageBox.critical(self, "Error", "Método de eliminación no encontrado")
                        return
                    
                    
                    if exito:
                        
                        # LIMPIAR ESTADO ACTUAL ANTES DE RECARGAR
                        if self.contract_manager:
                            # print(f"[ControladorGrafica] 🧹 Limpiando estado del contrato eliminado")
                            self.contract_manager.current_contract = None
                            self.contract_manager._clear_contract_info()
                        if hasattr(self, 'controlador_autosave'):
                            self.controlador_autosave.cargando_datos = True
                            print("[ControladorGrafica] ⏸️ Auto-guardado pausado temporalmente")
                        # SOLUCIÓN AL ERROR: Recargar sin usar reload_contracts()
                        if self.contract_manager:
                            try:
                                # USAR load_contracts_from_json() en lugar de reload_contracts()
                                self.contract_manager.load_contracts_from_json()
                            except Exception as e:
                                # print(f"[ControladorGrafica] ❌ Error recargando lista: {e}")
                                pass
                                # Continuar sin recargar
                        
                        # FORZAR SELECCIÓN DEL PRIMER ELEMENTO Y PROCESAMIENTO
                        if hasattr(self, 'comboBox') and self.comboBox.count() > 0:
                            self.comboBox.setCurrentIndex(0)
                            
                            # FORZAR PROCESAMIENTO DEL CAMBIO
                            if self.comboBox.count() > 0:
                                primer_texto = self.comboBox.itemText(0)
                                # print(f"[ControladorGrafica] 🎯 Procesando selección: '{primer_texto}'")
                                if self.contract_manager and primer_texto:
                                    self.contract_manager._process_contract_selection(primer_texto)
                        else:
                            # print(f"[ControladorGrafica] ⚠️ ComboBox vacío después del borrado")
                            # Si no hay contratos, limpiar completamente
                            if self.contract_manager:
                                self.contract_manager._clear_contract_info()
                        
                        QMessageBox.information(self, "Contrato Eliminado", mensaje)
                        # FORZAR ESTADO FINAL LIMPIO
                        if hasattr(self, 'comboBox'):
                            self.comboBox.blockSignals(True)
                            self.comboBox.setCurrentIndex(0)
                            self.comboBox.blockSignals(False)

                        if self.contract_manager:
                            self.contract_manager.current_contract = None
                            self.contract_manager._update_labels("-", "-")

                    else:
                        # print(f"[ControladorGrafica] ❌ Error en la eliminación")
                        QMessageBox.critical(self, "Error", mensaje)
                else:
                    # print(f"[ControladorGrafica] ❌ Borrado no confirmado")
                    QMessageBox.warning(self, "No confirmado", "El borrado no fue confirmado")
            else:
                # print(f"[ControladorGrafica] ⚠️ Diálogo cancelado por el usuario")
                
                pass
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error inesperado en borrar contrato: {e}")
            pass
            pass
            QMessageBox.critical(self, "Error", f"Error inesperado al borrar contrato: {str(e)}")

    def abrir_editor_firmantes(self):
        """Abrir popup editor de firmantes"""
        try:
            # Crear el diálogo popup
            dialogo = QDialog(self)
            dialogo.setWindowTitle("Editor de Firmantes")
            dialogo.setModal(True)
            dialogo.resize(800, 400)
            
            # Layout principal
            layout_principal = QVBoxLayout(dialogo)
            
            # Crear tabla
            tabla = QTableWidget()
            tabla.setColumnCount(2)
            tabla.setHorizontalHeaderLabels(["Campo", "Valor"])
            
            # Cargar datos de firmantes desde JSON
            firmantes = {}
            if hasattr(self, 'controlador_json') and self.controlador_json:
                firmantes = self.controlador_json.obtener_firmantes()
            
            # Configurar tabla con datos
            campos_firmantes = [
                ("firmanteConforme", "Firmante Conforme"),
                ("cargoConforme", "Cargo Conforme"),
                ("firmantePropone", "Firmante Propone"),
                ("cargoPropone", "Cargo Propone"),
                ("firmanteAprueba", "Firmante Aprueba"),
                ("cargoAprueba", "Cargo Aprueba"),
                ("cargoResponsable", "Cargo Responsable"),
                ("representanteFirma", "Representante Firma"),
                ("directorFacultativo", "Director Facultativo"),
                ("representanteAdif", "Representante ADIF"),
                ("nombreAsistenteAdif", "Nombre Asistente ADIF"),
                ("cargoResponsable1", "Cargo Responsable 1")
            ]
            
            tabla.setRowCount(len(campos_firmantes))
            
            for i, (campo_key, campo_nombre) in enumerate(campos_firmantes):
                # Columna 1: Nombre del campo (solo lectura)
                item_campo = QTableWidgetItem(campo_nombre)
                item_campo.setFlags(item_campo.flags() & ~Qt.ItemIsEditable)
                tabla.setItem(i, 0, item_campo)
                
                # Columna 2: Valor editable
                valor = firmantes.get(campo_key, "")
                item_valor = QTableWidgetItem(str(valor))
                tabla.setItem(i, 1, item_valor)
            
            # Ajustar columnas
            tabla.setColumnWidth(0, 200)
            tabla.setColumnWidth(1, 400)
            
            layout_principal.addWidget(tabla)
            
            # Botón guardar
            boton_guardar = QPushButton("Guardar")
            layout_principal.addWidget(boton_guardar)
            
            # Función para guardar
            def guardar_firmantes():
                try:
                    # Recoger datos de la tabla
                    nuevos_firmantes = {}
                    for i, (campo_key, _) in enumerate(campos_firmantes):
                        item_valor = tabla.item(i, 1)
                        if item_valor:
                            nuevos_firmantes[campo_key] = item_valor.text()
                        else:
                            nuevos_firmantes[campo_key] = ""
                    
                    # Guardar en JSON
                    if hasattr(self, 'controlador_json') and self.controlador_json:
                        exito = self.controlador_json.actualizar_firmantes(nuevos_firmantes)
                        if exito:
                            QMessageBox.information(dialogo, "Éxito", "Firmantes actualizados correctamente")
                            dialogo.accept()
                        else:
                            QMessageBox.warning(dialogo, "Error", "Error guardando firmantes")
                    else:
                        QMessageBox.warning(dialogo, "Error", "Controlador JSON no disponible")
                        
                except Exception as e:
                    QMessageBox.critical(dialogo, "Error", f"Error guardando firmantes: {str(e)}")
                    print(f"[ControladorGrafica] Error guardando firmantes: {e}")
            
            # Conectar botón
            boton_guardar.clicked.connect(guardar_firmantes)
            
            # Mostrar diálogo
            dialogo.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo editor de firmantes: {str(e)}")
            print(f"[ControladorGrafica] Error abriendo editor de firmantes: {e}")

    # =================== MÉTODOS PÚBLICOS ===================

    def get_current_contract_manager(self):
        """Obtener gestor de contratos actual"""
        return self.contract_manager

    def get_current_contract_data(self):
        """Obtener datos del contrato actual"""
        if self.contract_manager:
            return self.contract_manager.get_current_contract_data()
        return None

    def reload_contracts_list(self):
        """Recargar lista de contratos"""
        if self.contract_manager:
            self.contract_manager.reload_contracts()

    def get_datos_proyecto_completo(self):
        """Obtener datos completos del proyecto"""
        return {}

    

    def get_current_pdf_path(self):
        """Obtener ruta del PDF actual"""
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
            return self.pdf_viewer.get_current_pdf_path()
        return ""
    
    def has_pdf_loaded(self):
        """Verificar si hay PDF cargado"""
        if hasattr(self, 'pdf_viewer') and self.pdf_viewer:
            return self.pdf_viewer.has_pdf_loaded()
        return False

    # =================== INTEGRACIÓN SISTEMA DE RESUMEN ===================
    
    def _setup_resumen_integrado(self):
        """Configurar sistema de resumen integrado"""
        try:
            print("[ControladorGrafica] 🔄 Integrando sistema de resumen...")
            
            # Importar e integrar el sistema de resumen
            from .controlador_resumen import integrar_resumen_completo
            self.integrador_resumen = integrar_resumen_completo(self)
            
            if self.integrador_resumen:
                print("[ControladorGrafica] ✅ Sistema de resumen integrado exitosamente")
                # Test de tabla de seguimiento
                self.integrador_resumen.test_tabla_seguimiento()
            else:
                print("[ControladorGrafica] ⚠️ Sistema de resumen no se pudo integrar")
            
            # 🆕 NUEVO: Integrar controlador de fases de documentos
            print("[ControladorGrafica] 🔄 Integrando controlador de fases...")
            from .controlador_fases_documentos import integrar_controlador_fases
            self.controlador_fases = integrar_controlador_fases(self)
            
            if self.controlador_fases:
                print("[ControladorGrafica] ✅ Controlador de fases integrado exitosamente")
            else:
                print("[ControladorGrafica] ⚠️ Controlador de fases no se pudo integrar")
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error integrando sistemas: {e}")
            pass
            # Continuar sin el sistema de resumen en caso de error
            self.integrador_resumen = None

    def _actualizar_cronograma_inicial(self):
        """Actualizar cronograma visual al iniciar la aplicación"""
        try:
            print("[ControladorGrafica] 🔄 Iniciando actualización automática del cronograma...")
            
            # Verificar que el integrador de resumen esté disponible
            if not hasattr(self, 'integrador_resumen') or not self.integrador_resumen:
                print("[ControladorGrafica] ⚠️ Integrador de resumen no disponible, omitiendo actualización del cronograma")
                return
            
            # Obtener el contrato actual del ComboBox
            nombre_contrato = ""
            if hasattr(self, 'comboBox') and self.comboBox:
                nombre_contrato = self.comboBox.currentText()
            
            if not nombre_contrato:
                print("[ControladorGrafica] ⚠️ No hay contrato seleccionado, omitiendo actualización del cronograma")
                return
            
            # Usar un QTimer para actualizar después de que la UI esté completamente cargada
            QTimer.singleShot(1000, lambda: self._ejecutar_actualizacion_cronograma(nombre_contrato))
            
        except Exception as e:
            # print(f"[ControladorGrafica] ⚠️ Error en actualización inicial del cronograma: {e}")
            pass
    
    def _ejecutar_actualizacion_cronograma(self, nombre_contrato: str):
        """Ejecutar la actualización del cronograma con retraso"""
        try:
            # print(f"[ControladorGrafica] 🎯 Actualizando cronograma para contrato: {nombre_contrato}")
            
            # Actualizar el cronograma visual
            if hasattr(self.integrador_resumen, '_actualizar_cronograma_visual'):
                self.integrador_resumen._actualizar_cronograma_visual(nombre_contrato)
                print("[ControladorGrafica] ✅ Cronograma inicial actualizado exitosamente")
            else:
                print("[ControladorGrafica] ⚠️ Método _actualizar_cronograma_visual no disponible")
                
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error ejecutando actualización del cronograma: {e}")
            pass

    # =================== EVENTOS DEL SISTEMA ===================

    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        try:
            # Guardar datos actuales antes de cerrar
            if hasattr(self, 'controlador_autosave') and self.controlador_autosave:
                self.controlador_autosave.forzar_guardado_completo()
            
            if self.proyecto_actual:
                self._crear_copia_respaldo()
            event.accept()
        except Exception as e:
            # print(f"[ControladorGrafica] ⚠️ Error al cerrar: {e}")
            pass
            event.accept()

    def _crear_copia_respaldo(self):
        try:
            if self.proyecto_actual:
                ruta_respaldo = crear_copia_respaldo_proyecto(self.proyecto_actual)
        except Exception:
            pass





    def arreglar_botones_ahora(self):
        """
        FUNCIÓN MÍNIMA para arreglar botones - AGREGAR al final de ControladorGrafica
        """
        print("[ControladorGrafica] 🔧 Arreglando botones...")
        
        try:
            # 1. Verificar/crear controlador_calculos
            if not hasattr(self, 'controlador_calculos') or not self.controlador_calculos:
                from controladores.controlador_calculos import ControladorCalculos
                self.controlador_calculos = ControladorCalculos()
                print("[ControladorGrafica] ✅ controlador_calculos creado")
            
            # 2. Verificar/crear controlador_eventos_ui
            if not hasattr(self, 'controlador_eventos_ui') or not self.controlador_eventos_ui:
                from controladores.controlador_eventos_ui import ControladorEventosUI
                self.controlador_eventos_ui = ControladorEventosUI(self)
                print("[ControladorGrafica] ✅ controlador_eventos_ui creado")
            
            # 3. CRÍTICO: Conectar calculos a eventos
            self.controlador_eventos_ui.set_controlador_calculos(self.controlador_calculos)
            print("[ControladorGrafica] ✅ Controladores conectados")
            
            # 4. Reconectar botones críticos manualmente
            botones_criticos = {
                'cerrar_app': lambda: self.close(),
                'minimizar_app': lambda: self.showMinimized(),
            }
            
            acciones_criticas = {
                'actionAdministrar_json': self.mostrar_actuaciones_especiales,
                'actionAdministrar_Facturas_Directas': self.mostrar_facturas_directas,
                'actionCrear_Proyecto': self.mostrar_dialogo_crear_contrato,
                'actionBorrar_Proyecto': self.mostrar_dialogo_borrar_contrato,
                'actionClonar_Proyecto': self.mostrar_dialogo_clonar_contrato,
                'actionCambiar_tipo': self._cambiar_tipo_contrato,
                'actionEditar_firmantes': self.abrir_editor_firmantes,
                'actioninformacion_general': self.mostrar_informacion_general,
                'actioncuadroi_general': self.mostrar_cuadro_general,
                'actionSobre_auttor': self.mostrar_sobre_autor,
                'actiongenera_informe_de_obras': self.generar_informe_obras,
                'actiongenerar_informde_facturas_firectas': self.generar_informe_facturas_directas,
            }
            
            reconectados = 0
            for boton_name, funcion in botones_criticos.items():
                try:
                    if hasattr(self, boton_name):
                        boton = getattr(self, boton_name)
                        if boton and hasattr(boton, 'clicked'):
                            try:
                                boton.clicked.disconnect()
                            except:
                                pass
                            boton.clicked.connect(funcion)
                            # print(f"[ControladorGrafica] ✅ {boton_name} reconectado")
                            reconectados += 1
                except Exception as e:
                    # print(f"[ControladorGrafica] ❌ Error {boton_name}: {e}")
                    pass
            
            # Conectar acciones críticas
            for accion_name, funcion in acciones_criticas.items():
                try:
                    if hasattr(self, accion_name):
                        accion = getattr(self, accion_name)
                        if accion and hasattr(accion, 'triggered'):
                            try:
                                accion.triggered.disconnect()
                            except:
                                pass
                            accion.triggered.connect(funcion)
                            # print(f"[ControladorGrafica] ✅ {accion_name} reconectado")
                            reconectados += 1
                except Exception as e:
                    # print(f"[ControladorGrafica] ❌ Error {accion_name}: {e}")
                    pass
            
            # 5. Reconectar botones de documentos
            if hasattr(self, 'controlador_documentos') and self.controlador_documentos:
                botones_docs = {
                    'Generar_Acta_Inicio': 'comprobar_generar_acta_inicio',
                    'Generar_Cartas_inv': 'comprobar_generar_cartas_invitacion',
                    'Generar_acta_adj': 'comprobar_generar_acta_adjudicacion'
                }
                
                for boton_name, metodo_name in botones_docs.items():
                    try:
                        if (hasattr(self, boton_name) and 
                            hasattr(self.controlador_documentos, metodo_name)):
                            
                            boton = getattr(self, boton_name)
                            metodo = getattr(self.controlador_documentos, metodo_name)
                            
                            if boton and hasattr(boton, 'clicked'):
                                try:
                                    boton.clicked.disconnect()
                                except:
                                    pass
                                boton.clicked.connect(metodo)
                                # print(f"[ControladorGrafica] ✅ {boton_name} reconectado")
                                reconectados += 1
                    except Exception as e:
                        # print(f"[ControladorGrafica] ❌ Error {boton_name}: {e}")
                        pass
            
            # 6. Reconectar botones de actuaciones y facturas (si existen)
            if hasattr(self, 'controlador_actuaciones_facturas') and self.controlador_actuaciones_facturas:
                botones_actuaciones = {
                    'add_actuacion': 'agregar_actuacion',
                    'add_factura': 'agregar_factura', 
                    'borrar_actuacion': 'borrar_actuacion',
                    'borrar_factura': 'borrar_factura'
                }
                
                for boton_name, metodo_name in botones_actuaciones.items():
                    try:
                        if (hasattr(self, boton_name) and 
                            hasattr(self.controlador_actuaciones_facturas, metodo_name)):
                            
                            boton = getattr(self, boton_name)
                            metodo = getattr(self.controlador_actuaciones_facturas, metodo_name)
                            
                            if boton and hasattr(boton, 'clicked'):
                                try:
                                    boton.clicked.disconnect()
                                except:
                                    pass
                                boton.clicked.connect(metodo)
                                # print(f"[ControladorGrafica] ✅ {boton_name} reconectado")
                                reconectados += 1
                    except Exception as e:
                        # print(f"[ControladorGrafica] ❌ Error {boton_name}: {e}")
                        pass
            
            # print(f"[ControladorGrafica] ✅ TOTAL: {reconectados} botones reconectados")
            return True
            
        except Exception as e:
            # print(f"[ControladorGrafica] ❌ Error general: {e}")
            pass
            return False

    def mostrar_actuaciones_especiales(self):
        try:
            from .dialogo_actuaciones_especiales import DialogoActuacionesEspeciales
            dialogo = DialogoActuacionesEspeciales(self)
            dialogo.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def mostrar_facturas_directas(self):
        """Mostrar popup de Facturas Directas"""
        try:
            if hasattr(self, 'controlador_facturas_directas') and self.controlador_facturas_directas:
                self.controlador_facturas_directas.mostrar_popup_principal()
            else:
                QMessageBox.critical(self, "Error", "Controlador de facturas directas no disponible")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo Facturas Directas: {str(e)}")

    def mostrar_informacion_general(self):
        """Mostrar información general de la aplicación"""
        try:
            mensaje = """
<h3>Generador de Actas ADIF</h3>
<p><b>Versión:</b> 3.0</p>
<p><b>Descripción:</b> Aplicación para la gestión de contratos y generación de documentos oficiales para ADIF.</p>
<p><b>Características principales:</b></p>
<ul>
<li>Gestión completa de contratos de obras y servicios</li>
<li>Generación automática de documentos oficiales</li>
<li>Control de facturación directa</li>
<li>Sistema de seguimiento y liquidación</li>
</ul>
"""
            QMessageBox.about(self, "Información de la Aplicación", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando información: {str(e)}")

    def mostrar_cuadro_general(self):
        """Mostrar cuadro de información general del proyecto actual"""
        try:
            if not self.proyecto_actual:
                QMessageBox.information(self, "Información", "No hay ningún proyecto cargado.")
                return
                
            # Obtener datos del proyecto
            contract_data = self.controlador_json.obtener_datos_contrato(self.proyecto_actual) if self.controlador_json else {}
            
            if contract_data:
                mensaje = f"""
<h3>Información del Proyecto Actual</h3>
<p><b>Nombre:</b> {contract_data.get('nombre_proyecto', 'N/A')}</p>
<p><b>Expediente:</b> {contract_data.get('numero_expediente', 'N/A')}</p>
<p><b>Tipo:</b> {contract_data.get('tipo_contrato', 'N/A')}</p>
<p><b>Presupuesto:</b> {contract_data.get('presupuesto_licitacion', 'N/A')} €</p>
<p><b>Estado:</b> {contract_data.get('estado', 'N/A')}</p>
"""
            else:
                mensaje = "<p>No se pudo cargar la información del proyecto.</p>"
                
            QMessageBox.about(self, "Información del Proyecto", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando información del proyecto: {str(e)}")

    def mostrar_sobre_autor(self):
        """Mostrar información sobre el autor"""
        try:
            # Crear un diálogo personalizado
            dialog = QDialog(self)
            dialog.setWindowTitle("Acerca del Desarrollo")
            dialog.setModal(True)
            dialog.resize(400, 300)
            
            # Layout principal
            layout = QVBoxLayout()
            
            # Intentar cargar la imagen del autor
            try:
                import os
                imagen_path = os.path.join(os.path.dirname(__file__), "..", "images", "Autor.jpg")
                if os.path.exists(imagen_path):
                    label_imagen = QLabel()
                    pixmap = QPixmap(imagen_path)
                    # Redimensionar la imagen si es necesario
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        label_imagen.setPixmap(pixmap)
                        label_imagen.setAlignment(Qt.AlignCenter)
                        layout.addWidget(label_imagen)
            except Exception:
                pass  # Si no se puede cargar la imagen, continuar sin ella
            
            # Información del autor
            label_info = QLabel()
            label_info.setWordWrap(True)
            mensaje = """
<h3>Acerca del Desarrollo</h3>
<p><b>Desarrollador:</b> Pablo Martín Fernández</p>
<p><b>Cargo:</b> Ingeniero Industrial</p>
<p><b>Departamento:</b> Patrimonio y Urbanismo</p>
<p><b>Centro:</b> ADIF</p>
<p><b>Año:</b> 2024</p>
<br>
<p><b>Detalles técnicos:</b></p>
<p><b>Framework:</b> PyQt5</p>
<p><b>Lenguaje:</b> Python 3.x</p>
<br>
<p>Aplicación desarrollada para optimizar la gestión de contratos y documentación oficial en ADIF.</p>
"""
            label_info.setText(mensaje)
            label_info.setAlignment(Qt.AlignTop)
            layout.addWidget(label_info)
            
            # Botón OK
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.accept)
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn_ok)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando información del autor: {str(e)}")

    def generar_informe_obras(self):
        """Generar informe de obras"""
        try:
            if hasattr(self, 'gestor_archivos_unificado') and self.gestor_archivos_unificado:
                self.gestor_archivos_unificado.generar_informe_carpetas()
            else:
                QMessageBox.information(self, "Información", "Funcionalidad de informes de obras en desarrollo.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando informe de obras: {str(e)}")

    def generar_informe_facturas_directas(self):
        """Generar informe de facturas directas"""
        try:
            if hasattr(self, 'controlador_facturas_directas') and self.controlador_facturas_directas:
                self.controlador_facturas_directas.informe_facturacion()
            else:
                QMessageBox.information(self, "Información", "Funcionalidad de informes de facturas directas en desarrollo.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando informe de facturas: {str(e)}")

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    ventana = ControladorGrafica()
    ventana.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())