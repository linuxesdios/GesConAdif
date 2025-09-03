"""
Controlador especializado SOLO para eventos de interfaz de usuario
Solo detecta eventos y llama funciones del controlador de cálculos
VERSIÓN COMPLETA CORREGIDA - CON IMPORTACIONES OPCIONALES
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Importaciones opcionales de PyQt5
try:
    from PyQt5.QtWidgets import QLineEdit, QTextEdit, QTableWidgetItem, QDateEdit, QTimeEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTableWidget, QMessageBox
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5 import QtCore
    PYQT5_AVAILABLE = True
except ImportError:
    logger.warning("PyQt5 no disponible, usando modo compatibilidad")
    PYQT5_AVAILABLE = False
    # Clases mock para compatibilidad
    QLineEdit = QTextEdit = QTableWidgetItem = QDateEdit = QTimeEdit = None
    QDoubleSpinBox = QSpinBox = QComboBox = QTableWidget = QMessageBox = None
    Qt = QtCore = QTimer = None


class ControladorEventosUI:
    """Controlador especializado SOLO para eventos de interfaz de usuario"""
    


    def set_controlador_calculos(self, controlador_calculos):
        """Establecer referencia al controlador de cálculos"""
        self.controlador_calculos = controlador_calculos
        logger.info("Controlador de cálculos conectado")
        
        # CRÍTICO: Re-setup de eventos después de conectar el controlador
        if self.controlador_calculos:
            logger.debug("Re-configurando eventos tras conexión de controlador_calculos")
            self.setup_event_handlers()
        
    def iniciar_carga_datos(self):
        """Pausar eventos durante carga"""
        self.cargando_datos = True
        
    def finalizar_carga_datos(self):
        """Reactivar eventos después de carga"""
        self.cargando_datos = False
        
    def setup_event_handlers(self):
        """Configurar todos los manejadores de eventos - VERSIÓN CORREGIDA"""
        logger.debug("Iniciando setup_event_handlers")
        try:
            if not PYQT5_AVAILABLE:
                logger.warning("PyQt5 no disponible - saltando configuración eventos")
                return
                
            if not self.main_window:
                logger.error("main_window es None")
                return
                
            logger.debug("Ventana principal encontrada")
            
            # 1. CONFIGURAR CAMPOS ESPECÍFICOS
            self._setup_campos_especificos()

            # 2. CONFIGURAR EVENTOS DE LIQUIDACIÓN
            self.configurar_eventos_liquidacion(self.main_window)

            # 3. CONFIGURAR TABLAS ESPECÍFICAS
            self._setup_tablas_especificas()
            
            # 4. CONFIGURAR EVENTOS GENERALES
            self._setup_eventos_generales()
            
            # 5. CONECTAR TODOS LOS BOTONES
            self._conectar_todos_los_botones()
            
            # 6. CONECTAR BOTONES ESPECÍFICOS DEL RESUMEN Y TABLAS
            self._setup_botones_resumen_y_tablas()
            
            # 7. CONFIGURAR JUSTIFICACIÓN INICIAL
            self.setup_justificacion_inicial()
            
            logger.info("Setup de eventos completado exitosamente")
            
            # Configurar eventos específicos después de un delay
            QTimer.singleShot(1000, self._setup_eventos_tardios)

        except Exception as e:
            logger.error(f"Error en setup_event_handlers: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_eventos_tardios(self):
        """Configurar eventos que requieren widgets completamente inicializados"""
        try:
            logger.debug("Configurando eventos tardíos...")
            
            # numEmpresasPresentadas - AUTO-GUARDADO TARDÍO
            if hasattr(self.main_window, 'numEmpresasPresentadas'):
                widget = self.main_window.numEmpresasPresentadas
                logger.debug(f"Conectando tardío numEmpresasPresentadas (tipo: {type(widget).__name__})")
                # NO desconectar - usar el sistema general que ya funciona
                # Solo verificar que el widget existe y está disponible
                logger.debug("numEmpresasPresentadas verificado - usando sistema general")
            else:
                logger.warning("numEmpresasPresentadas no encontrado en setup tardío")

            # numEmpresasSolicitadas - AUTO-GUARDADO TARDÍO  
            if hasattr(self.main_window, 'numEmpresasSolicitadas'):
                widget = self.main_window.numEmpresasSolicitadas
                logger.debug(f"Conectando tardío numEmpresasSolicitadas (tipo: {type(widget).__name__})")
                # NO desconectar - usar el sistema general que ya funciona
                # Solo verificar que el widget existe y está disponible
                logger.debug("numEmpresasSolicitadas verificado - usando sistema general")
            else:
                logger.warning("numEmpresasSolicitadas no encontrado en setup tardío")
                
            # Verificar plazoEjecucion para debugging de carga
            if hasattr(self.main_window, 'plazoEjecucion'):
                widget = self.main_window.plazoEjecucion
                valor_actual = widget.value() if hasattr(widget, 'value') else widget.text() if hasattr(widget, 'text') else 'N/A'
                logger.debug(f"plazoEjecucion actual: '{valor_actual}' (tipo: {type(widget).__name__})")
            
            # Verificar si existe plazoActuacion
            if hasattr(self.main_window, 'plazoActuacion'):
                widget = self.main_window.plazoActuacion
                logger.debug(f"Encontrado plazoActuacion (tipo: {type(widget).__name__})")
                # NO desconectar - usar el sistema general que ya funciona
                logger.debug("plazoActuacion verificado - usando sistema general")
            else:
                logger.warning("plazoActuacion no encontrado")
                
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error en setup tardío: {e}")
    
    def verificar_carga_campo(self, nombre_campo):
        """Método para verificar si un campo se carga correctamente"""
        try:
            if hasattr(self.main_window, nombre_campo):
                widget = getattr(self.main_window, nombre_campo)
                if hasattr(widget, 'value'):
                    valor = widget.value()
                elif hasattr(widget, 'text'):
                    valor = widget.text()
                else:
                    valor = 'N/A'
                print(f"[CAMBIO_CONTRATO] 🔍 VERIFICACIÓN {nombre_campo}: '{valor}' (tipo: {type(widget).__name__})")
                
                # FORZAR ACTUALIZACIÓN VISUAL si el valor no es vacío
                if valor and valor != 'N/A' and valor != '' and valor != 0:
                    print(f"[CAMBIO_CONTRATO] 🔄 Repaint visual de {nombre_campo} (SIN setValue/setText para evitar loops)")
                    try:
                        # ❌ COMENTADO: NO forzar setValue/setText que puede causar loops de datos
                        # if hasattr(widget, 'setValue'):
                        #     widget.setValue(valor)
                        # elif hasattr(widget, 'setText'):
                        #     widget.setText(str(valor))
                        
                        # Forzar repaint
                        if hasattr(widget, 'repaint'):
                            widget.repaint()
                        if hasattr(widget, 'update'):
                            widget.update()
                            
                        print(f"[CAMBIO_CONTRATO] ✅ Repaint visual completado para {nombre_campo} (datos preservados)")
                    except Exception as e:
                        print(f"[CAMBIO_CONTRATO] ❌ Error en actualización visual: {e}")
                
                return valor
            else:
                print(f"[CAMBIO_CONTRATO] ❌ VERIFICACIÓN {nombre_campo}: NO ENCONTRADO")
                return None
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ❌ Error verificando {nombre_campo}: {e}")
            return None
    
    def _on_plazo_actuacion_changed(self):
        """Evento: plazoActuacion cambió - AUTO-GUARDADO"""
        print(f"[CAMBIO_CONTRATO] 🔥 _on_plazo_actuacion_changed EJECUTADO - cargando_datos={self.cargando_datos}")
        
        if self.cargando_datos:
            print(f"[CAMBIO_CONTRATO] ⏸️ SKIP - cargando datos")
            return
        
        try:
            if hasattr(self.main_window, 'plazoActuacion'):
                widget = self.main_window.plazoActuacion
                valor = widget.text() if hasattr(widget, 'text') else str(widget.value() if hasattr(widget, 'value') else '')
                print(f"[CAMBIO_CONTRATO] ⏱️ plazoActuacion = '{valor}' - GUARDANDO")
                self._guardar_campo_en_json('plazoActuacion', valor)
            else:
                print(f"[CAMBIO_CONTRATO] ❌ Widget plazoActuacion no encontrado")
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_plazo_actuacion_changed: {e}")

    def _conectar_todos_los_botones(self):
        """Conectar TODOS los botones de la aplicación"""
        print("[ControladorEventosUI] 🔘 Iniciando conexión de botones...")
        
        try:
            # BOTONES CRÍTICOS
            self._conectar_botones_criticos()
            
            # BOTONES DE NAVEGACIÓN
            self._setup_botones_navegacion()
            
            # BOTONES DE DOCUMENTOS
            self._setup_botones_documentos()
            
            # BOTONES DE ARCHIVOS
            self._setup_botones_gestion_archivo()
            
            # BOTONES DE EMPRESAS
            self._setup_botones_gestion_empresas()
            
            # BOTONES ESPECIALES
            self._setup_botones_especiales()
            
            
            print("[ControladorEventosUI] OK Todos los botones conectados")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error conectando botones: {e}")
    
    def _conectar_botones_criticos(self):
        """Conectar botones críticos (cerrar y minimizar)"""
        try:
            # Botón cerrar
            if hasattr(self.main_window, 'cerrar_app') and self.main_window.cerrar_app:
                try:
                    self.main_window.cerrar_app.clicked.disconnect()
                except:
                    pass
                self.main_window.cerrar_app.clicked.connect(self.main_window.close)
                print("[ControladorEventosUI] OK cerrar_app conectado")
            
            # Botón minimizar
            if hasattr(self.main_window, 'minimizar_app') and self.main_window.minimizar_app:
                try:
                    self.main_window.minimizar_app.clicked.disconnect()
                except:
                    pass
                self.main_window.minimizar_app.clicked.connect(self.main_window.showMinimized)
                print("[ControladorEventosUI] OK minimizar_app conectado")
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error conectando botones críticos: {e}")
    
   

    def _setup_botones_navegacion(self):
        """Configurar botones de navegación y contratos"""
        botones_navegacion = [
            ('Cambiar_tipo', '_cambiar_tipo_contrato'),
            ('btn_crear_contrato', 'mostrar_dialogo_crear_contrato'),
            ('btn_borrar_contrato', 'mostrar_dialogo_borrar_contrato'),
            ('btn_Clonar_contrato', 'mostrar_dialogo_clonar_contrato')
        ]
        
        for boton_name, metodo_name in botones_navegacion:
            self._conectar_boton_simple(boton_name, metodo_name)

    def _setup_botones_documentos(self):
        """Configurar botones de generación de documentos"""
        botones_documentos = [
            ('Generar_Acta_Inicio', 'comprobar_generar_acta_inicio'),
            ('Generar_Cartas_inv', 'comprobar_generar_cartas_invitacion'),
            ('Generar_acta_adj', 'comprobar_generar_acta_adjudicacion'),
            ('Generar_carta_adj', 'comprobar_generar_cartas_adjudicacion'),
            ('Generar_acta_liq', 'comprobar_generar_acta_liquidacion'),
            ('Generar_replanteo', 'comprobar_generar_acta_replanteo'),
            ('Generar_recepcion', 'comprobar_generar_acta_recepcion'),
            ('Generar_Director', 'comprobar_generar_nombramiento_director'),
            ('Generar_Contrato', 'comprobar_generar_contrato')
        ]
        
        for boton_name, metodo_name in botones_documentos:
            self._conectar_boton_documento(boton_name, metodo_name)

    def _conectar_boton_documento(self, boton_name, metodo_name):
        """Conectar un botón de documento específico"""
        try:
            if not hasattr(self.main_window, boton_name):
                return
                
            if not hasattr(self.main_window, 'controlador_documentos'):
                return
                
            if not hasattr(self.main_window.controlador_documentos, metodo_name):
                return
                
            boton = getattr(self.main_window, boton_name)
            metodo = getattr(self.main_window.controlador_documentos, metodo_name)
            
            # Desconectar conexiones anteriores
            try:
                boton.clicked.disconnect()
            except:
                pass
                
            # Conectar
            boton.clicked.connect(metodo)
            print(f"[ControladorEventosUI] ✅ {boton_name} -> {metodo_name} conectado")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando {boton_name}: {e}")

    def _setup_botones_gestion_archivo(self):
        """Configurar botones de gestión de archivos"""
        botones_archivo = [
            ('Guardar', '_guardar_proyecto'),
            ('Pb_add_excel', '_abrir_excel_y_procesar'),
            ('Abrir_portafirmas', '_abrir_portafirmas')
        ]
        
        for boton_name, metodo_name in botones_archivo:
            self._conectar_boton_simple(boton_name, metodo_name)
        
        # Botón especial de abrir carpeta
        self._setup_abrir_carpeta()
        
        # Botón especial de Excel (Importar/Exportar)
        self._setup_boton_excel()
    
    def _setup_boton_excel(self):
        """Configurar botón especial de Excel con menú desplegable"""
        try:
            if hasattr(self.main_window, 'Pb_Imp_Exp_excel'):
                boton = self.main_window.Pb_Imp_Exp_excel
                if boton is not None:
                    try:
                        boton.clicked.disconnect()
                    except:
                        pass
                    boton.clicked.connect(self.on_pb_imp_exp_excel_clicked)
                    print("[ControladorEventosUI] ✅ Pb_Imp_Exp_excel conectado")
                else:
                    print("[ControladorEventosUI] ⚠️ Pb_Imp_Exp_excel es None")
            else:
                print("[ControladorEventosUI] ⚠️ Pb_Imp_Exp_excel no encontrado")
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando Pb_Imp_Exp_excel: {e}")

    def _setup_botones_gestion_empresas(self):
        """Configurar botones de gestión de empresas"""
        botones_empresas = [
            ('Pb_add', '_agregar_empresa'),
            ('Pb_remove', '_quitar_empresa')
        ]
        
        for boton_name, metodo_name in botones_empresas:
            self._conectar_boton_simple(boton_name, metodo_name)

    def _setup_botones_especiales(self):
        """Configurar botones con lógica especial"""
        # ComboBox
        try:
            if hasattr(self.main_window, 'comboBox') and self.main_window.comboBox:
                try:
                    self.main_window.comboBox.currentTextChanged.disconnect()
                except:
                    pass
                    
                self.main_window.comboBox.currentTextChanged.connect(
                    self._on_combo_changed
                )
                print("[ControladorEventosUI] ✅ comboBox conectado")
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando comboBox: {e}")

        # Botón cambio expediente
        try:
            if hasattr(self.main_window, 'btn_cambio_exp'):
                try:
                    self.main_window.btn_cambio_exp.clicked.disconnect()
                except:
                    pass
                    
                self.main_window.btn_cambio_exp.clicked.connect(
                    self._ejecutar_cambio_expediente
                )
                print("[ControladorEventosUI] ✅ btn_cambio_exp conectado")
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando btn_cambio_exp: {e}")
            
        # Botón editar firmantes
        try:
            if hasattr(self.main_window, 'actionEditar_firmantes') and self.main_window.actionEditar_firmantes:
                try:
                    self.main_window.actionEditar_firmantes.triggered.disconnect()
                except:
                    pass
                    
                self.main_window.actionEditar_firmantes.triggered.connect(
                    self._ejecutar_editar_firmantes
                )
                print("[ControladorEventosUI] ✅ actionEditar_firmantes conectado")
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando actionEditar_firmantes: {e}")
    
    def _setup_botones_resumen_y_tablas(self):
        """Configurar botones específicos del resumen y tablas"""
        try:
            # Botones de actuaciones y facturas
            botones_actuaciones = [
                ('add_actuacion', 'agregar_actuacion'),
                ('add_factura', 'agregar_factura'),
                ('borrar_actuacion', 'borrar_actuacion'),
                ('borrar_factura', 'borrar_factura')
            ]
            
            for boton_name, metodo_name in botones_actuaciones:
                self._conectar_boton_actuacion(boton_name, metodo_name)
            
            print("[ControladorEventosUI] ✅ Botones de resumen y tablas configurados")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error configurando botones resumen: {e}")
    
    def _conectar_boton_actuacion(self, boton_name, metodo_name):
        """Conectar un botón de actuación específico"""
        try:
            if not hasattr(self.main_window, boton_name):
                return
                
            if not (hasattr(self.main_window, 'controlador_actuaciones_facturas') and 
                   self.main_window.controlador_actuaciones_facturas):
                return
                
            if not hasattr(self.main_window.controlador_actuaciones_facturas, metodo_name):
                return
                
            boton = getattr(self.main_window, boton_name)
            metodo = getattr(self.main_window.controlador_actuaciones_facturas, metodo_name)
            
            # Desconectar conexiones anteriores
            try:
                boton.clicked.disconnect()
            except:
                pass
                
            # Conectar
            boton.clicked.connect(metodo)
            print(f"[ControladorEventosUI] ✅ {boton_name} -> {metodo_name} conectado")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando {boton_name}: {e}")

    def _conectar_boton_simple(self, boton_name, metodo_name):
        """Conectar un botón con su método correspondiente"""
        try:
            if not hasattr(self.main_window, boton_name):
                return
                
            if not hasattr(self.main_window, metodo_name):
                return
            
            boton = getattr(self.main_window, boton_name)
            metodo = getattr(self.main_window, metodo_name)
            
            # Desconectar conexiones anteriores
            try:
                boton.clicked.disconnect()
            except:
                pass
                
            # Conectar
            boton.clicked.connect(metodo)
            print(f"[ControladorEventosUI] ✅ {boton_name} -> {metodo_name} conectado")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando {boton_name}: {e}")

    def _conectar_accion_simple(self, accion_name, metodo_name):
        """Conectar una acción de menú con su método correspondiente"""
        try:
            if not hasattr(self.main_window, accion_name):
                return
                
            if not hasattr(self.main_window, metodo_name):
                return
            
            accion = getattr(self.main_window, accion_name)
            metodo = getattr(self.main_window, metodo_name)
            
            # Desconectar conexiones anteriores
            try:
                accion.triggered.disconnect()
            except:
                pass
                
            # Conectar
            accion.triggered.connect(metodo)
            print(f"[ControladorEventosUI] ✅ {accion_name} -> {metodo_name} conectado")
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando {accion_name}: {e}")

    def _setup_abrir_carpeta(self):
        """Configurar botón especial de abrir carpeta"""
        try:
            if (hasattr(self.main_window, 'Abrir_carpeta') and 
                hasattr(self.main_window, 'controlador_archivos')):
                
                def abrir_carpeta_wrapper():
                    contract_data = {
                        'nombreObra': getattr(self.main_window.nombreObra, 'text', lambda: '')(),
                        'numeroExpediente': getattr(self.main_window.numeroExpediente, 'text', lambda: '')()
                    }
                    self.main_window.controlador_archivos.abrir_carpeta_contrato(contract_data)
                
                try:
                    self.main_window.Abrir_carpeta.clicked.disconnect()
                except:
                    pass
                    
                self.main_window.Abrir_carpeta.clicked.connect(abrir_carpeta_wrapper)
                print("[ControladorEventosUI] OK Abrir_carpeta conectado")
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error conectando Abrir_carpeta: {e}")

    # === FUNCIONES EXCEL ===
    
    def conectar_boton_excel(self):
        """Conectar el botón Excel"""
        try:
            if hasattr(self.main_window, 'Pb_Imp_Exp_excel'):
                boton = self.main_window.Pb_Imp_Exp_excel
                if boton is not None:
                    try:
                        boton.clicked.disconnect()
                    except:
                        pass
                    boton.clicked.connect(self.on_pb_imp_exp_excel_clicked)
        except Exception as e:
            print(f"[Excel] ERROR conectando botón: {e}")
    
    def conectar_boton_actuacion_mail(self):
        """Conectar el botón crear_actuacion_mail"""
        try:
            if hasattr(self.main_window, 'crear_actuacion_mail'):
                boton = self.main_window.crear_actuacion_mail
                if boton is not None:
                    try:
                        boton.clicked.disconnect()
                    except:
                        pass
                    boton.clicked.connect(self.on_crear_actuacion_mail_clicked)
        except Exception as e:
            print(f"[ActuacionMail] ERROR conectando botón: {e}")

    def on_pb_imp_exp_excel_clicked(self):
        """Disparador del botón Importar/Exportar Excel"""
        try:
            from PyQt5.QtWidgets import QMenu
            from PyQt5.QtCore import QPoint
            from controladores.ventana_doble_tabla import gestionar_importacion_exportacion_excel
            
            menu = QMenu(self.main_window)
            accion_importar = menu.addAction("Importar desde Excel")
            accion_exportar = menu.addAction("Exportar a Excel")
            menu.addSeparator()
            accion_cancelar = menu.addAction("Cancelar")
            
            boton = self.main_window.Pb_Imp_Exp_excel
            menu_pos = boton.mapToGlobal(QPoint(0, boton.height()))
            accion_elegida = menu.exec_(menu_pos)
            
            if accion_elegida == accion_importar:
                gestionar_importacion_exportacion_excel(self.main_window, "importar")
            elif accion_elegida == accion_exportar:
                gestionar_importacion_exportacion_excel(self.main_window, "exportar")
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error en gestión Excel:\n{str(e)}")

    def on_crear_actuacion_mail_clicked(self):
        """Disparador del botón crear_actuacion_mail"""
        try:
            if hasattr(self.main_window, 'controlador_actuaciones_facturas') and self.main_window.controlador_actuaciones_facturas:
                self.main_window.controlador_actuaciones_facturas.agregar_actuacion_mail()
            else:
                QMessageBox.warning(self.main_window, "Error", "Controlador de actuaciones no disponible")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error en actuación con email:\n{str(e)}")

    def obtener_empresas_actuales(self):
        """Obtiene empresas del sistema"""
        try:
            empresas = []
            
            if not self.main_window or not hasattr(self.main_window, 'TwEmpresas'):
                return []
            
            tabla = self.main_window.TwEmpresas
            if not tabla or tabla.rowCount() == 0:
                return []
            
            for fila in range(tabla.rowCount()):
                nombre_item = tabla.item(fila, 0)
                if not nombre_item:
                    continue
                
                nombre = nombre_item.text().strip()
                if not nombre:
                    continue
                
                empresa = {
                    'nombre': nombre,
                    'nif': tabla.item(fila, 1).text().strip() if tabla.item(fila, 1) else '',
                    'email': tabla.item(fila, 2).text().strip() if tabla.item(fila, 2) else '',
                    'contacto': tabla.item(fila, 3).text().strip() if tabla.item(fila, 3) else ''
                }
                
                empresas.append(empresa)
            
            return empresas
            
        except Exception as e:
            print(f"[Excel] Error en obtener_empresas_actuales: {e}")
            return []

    def aplicar_empresas_importadas(self, empresas_importadas):
        """Aplica empresas importadas al sistema"""
        try:
            if hasattr(self.main_window, 'TwEmpresas'):
                tabla = self.main_window.TwEmpresas
                tabla.setRowCount(len(empresas_importadas))
                
                for fila, empresa in enumerate(empresas_importadas):
                    tabla.setItem(fila, 0, QTableWidgetItem(empresa.get('nombre', '')))
                    tabla.setItem(fila, 1, QTableWidgetItem(empresa.get('nif', '')))
                    tabla.setItem(fila, 2, QTableWidgetItem(empresa.get('email', '')))
                    tabla.setItem(fila, 3, QTableWidgetItem(empresa.get('contacto', '')))
            
            if hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json:
                contrato_actual = None
                if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                    contrato_actual = self.main_window.contract_manager.get_current_contract()
                
                if contrato_actual:
                    self.main_window.controlador_json.guardar_empresas_unificadas_en_json(
                        contrato_actual, empresas_importadas
                    )
            
        except Exception as e:
            print(f"[Excel] Error aplicando empresas: {e}")
            raise

    

    def _actualizar_tabla_empresas(self, empresas):
        """Actualiza tabla de empresas en la UI"""
        try:
            if not hasattr(self.main_window, 'TwEmpresas'):
                return
                
            tabla = self.main_window.TwEmpresas
            tabla.setRowCount(len(empresas))
            
            for fila, empresa in enumerate(empresas):
                tabla.setItem(fila, 0, QTableWidgetItem(empresa.get('nombre', '')))
                tabla.setItem(fila, 1, QTableWidgetItem(empresa.get('nif', '')))
                tabla.setItem(fila, 2, QTableWidgetItem(empresa.get('email', '')))
                tabla.setItem(fila, 3, QTableWidgetItem(empresa.get('contacto', '')))
            
            print(f"[Excel] Tabla actualizada con {len(empresas)} empresas")
            
        except Exception as e:
            print(f"[Excel] Error actualizando tabla: {e}")
                
    def _setup_campos_especificos(self):
        """Configurar campos que disparan cálculos específicos"""
        try:
            # basePresupuesto - calcula IVA base
            if hasattr(self.main_window, 'basePresupuesto'):
                widget = self.main_window.basePresupuesto
                try:
                    widget.editingFinished.disconnect()
                except:
                    pass
                widget.editingFinished.connect(lambda: self._on_base_presupuesto_changed())
                
            # precioAdjudicacion - calcula IVA adjudicación + LICITACIONES
            if hasattr(self.main_window, 'precioAdjudicacion'):
                widget = self.main_window.precioAdjudicacion
                try:
                    widget.editingFinished.disconnect()
                except:
                    pass
                widget.editingFinished.connect(lambda: self._on_precio_adjudicacion_changed())
                
            # certBase - calcula IVA + liquidación
            if hasattr(self.main_window, 'certBase'):
                widget = self.main_window.certBase
                try:
                    widget.editingFinished.disconnect()
                except:
                    pass
                widget.editingFinished.connect(lambda: self._on_cert_base_changed())

            # fechaContrato
            if hasattr(self.main_window, 'fechaContrato'):
                widget = self.main_window.fechaContrato
                if hasattr(widget, 'dateChanged'):
                    try:
                        widget.dateChanged.disconnect()
                    except:
                        pass
                    widget.dateChanged.connect(lambda _: self._on_fecha_contrato_changed())
                elif hasattr(widget, 'editingFinished'):
                    try:
                        widget.editingFinished.disconnect()
                    except:
                        pass
                    widget.editingFinished.connect(lambda: self._on_fecha_contrato_changed())

        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en campos específicos: {e}")

    def _on_precio_adjudicacion_changed(self):
        """Evento: precioAdjudicacion cambió - CON CÁLCULOS Y AUTO-GUARDADO"""
        if self.cargando_datos or not self.controlador_calculos:
            return
        
        try:
            # Ejecutar cálculos
            self.controlador_calculos.calcular_iva_adjudicacion(self.main_window)
            self.controlador_calculos.calcular_anualidades(self.main_window)
            
            # AUTO-GUARDADO: Guardar el valor modificado
            if hasattr(self.main_window, 'precioAdjudicacion'):
                widget = self.main_window.precioAdjudicacion
                valor = str(widget.value()) if hasattr(widget, 'value') else widget.text()
                self._guardar_campo_en_json('precioAdjudicacion', valor)
                self._guardar_cambios_pendientes()
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en precio_adjudicacion_changed: {e}")
    
    def _setup_tablas_especificas(self):
        """Configurar tablas que disparan cálculos"""
        try:
            # TwEmpresas
            if hasattr(self.main_window, 'TwEmpresas'):
                tabla = self.main_window.TwEmpresas
                try:
                    tabla.itemChanged.disconnect()
                except:
                    pass
                try:
                    tabla.itemSelectionChanged.disconnect()
                except:
                    pass
                tabla.itemChanged.connect(self._on_tw_empresas_changed)
                tabla.itemSelectionChanged.connect(self._on_tw_empresas_selection_changed)
                print("[ControladorEventosUI] ✅ TwEmpresas conectado (cambios + selección)")
            
            # TwOfertas
            if hasattr(self.main_window, 'TwOfertas'):
                tabla = self.main_window.TwOfertas
                try:
                    tabla.itemChanged.disconnect()
                except:
                    pass
                tabla.itemChanged.connect(self._on_tw_ofertas_changed)
                print("[ControladorEventosUI] ✅ TwOfertas conectado")
                
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error en tablas específicas: {e}")
    
    def configurar_eventos_liquidacion(self, window):
        """Configura los eventos para disparar cálculo de liquidación"""
        try:
            if not self.controlador_calculos:
                return

            campos = ['certBase', 'precioEjecucionContrata', 'presupuestoVigente']
            for campo in campos:
                widget = getattr(window, campo, None)
                if widget is None:
                    continue

                try:
                    if hasattr(widget, 'valueChanged'):
                        widget.valueChanged.disconnect()
                    elif hasattr(widget, 'textChanged'):
                        widget.textChanged.disconnect()
                except:
                    pass

                if hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(lambda: self.controlador_calculos.calcular_liquidacion(window))
                elif hasattr(widget, 'textChanged'):
                    widget.textChanged.connect(lambda: self.controlador_calculos.calcular_liquidacion(window))

        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error conectando eventos de liquidación: {e}")
    
    def setup_justificacion_inicial(self):
        """Configurar justificación inicial con valores actuales"""
        try:
            if self.controlador_calculos:
                self.controlador_calculos.actualizar_justificacion_limites(self.main_window)
            else:
                print("[ControladorEventosUI] ⚠️ Controlador de cálculos no disponible para justificación inicial")
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error configurando justificación inicial: {e}")
    
    def _setup_eventos_generales(self):
        """Configurar eventos generales (tabs, botones, etc)"""
        try:
            # Tabs
            if hasattr(self.main_window, 'tabWidget'):
                try:
                    self.main_window.tabWidget.currentChanged.disconnect()
                except:
                    pass
                self.main_window.tabWidget.currentChanged.connect(self._on_tab_changed)
                print("[ControladorEventosUI] ✅ tabWidget conectado")
            
            # Resto de widgets
            self._setup_widgets_generales()
            
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error en eventos generales: {e}")

    def _setup_widgets_generales(self):
        """Configurar widgets con eventos de foco"""
        try:
            # QLineEdit generales
            line_edits = self.main_window.findChildren(QLineEdit)
            campos_especiales = ['basePresupuesto', 'certBase', 'fechaContrato']
            
            for widget in line_edits:
                nombre = widget.objectName()
                if nombre and not nombre.startswith('qt_') and nombre not in campos_especiales:
                    # Solo editingFinished (pérdida de foco)
                    try:
                        widget.editingFinished.disconnect()
                    except:
                        pass
                    widget.editingFinished.connect(lambda w=widget, n=nombre: self._on_focus_lost(n, w))
            
            # QDoubleSpinBox generales
            spinboxes = self.main_window.findChildren(QDoubleSpinBox)
            for widget in spinboxes:
                nombre = widget.objectName()
                if nombre and not nombre.startswith('qt_') and nombre not in campos_especiales:
                    # Solo editingFinished (pérdida de foco)
                    try:
                        widget.editingFinished.disconnect()
                    except:
                        pass
                    widget.editingFinished.connect(lambda w=widget, n=nombre: self._on_focus_lost(n, w))
            
            # QSpinBox generales
            from PyQt5.QtWidgets import QSpinBox
            spinboxes_int = self.main_window.findChildren(QSpinBox)
            for widget in spinboxes_int:
                nombre = widget.objectName()
                if nombre and not nombre.startswith('qt_'):
                    try:
                        widget.editingFinished.disconnect()
                    except:
                        pass
                    widget.editingFinished.connect(lambda w=widget, n=nombre: self._on_focus_lost(n, w))
            
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en widgets generales: {e}")

    # =================== CALLBACKS ESPECÍFICOS ===================
    
    def _on_base_presupuesto_changed(self):
        """Evento: basePresupuesto cambió - CON CÁLCULOS Y AUTO-GUARDADO"""
        if self.cargando_datos or not self.controlador_calculos:
            return
        
        try:
            # Ejecutar cálculos
            self.controlador_calculos.calcular_iva_base_presupuesto(self.main_window)
            self.controlador_calculos.actualizar_justificacion_limites(self.main_window)
            
            # AUTO-GUARDADO: Guardar el valor modificado
            if hasattr(self.main_window, 'basePresupuesto'):
                widget = self.main_window.basePresupuesto
                valor = str(widget.value()) if hasattr(widget, 'value') else widget.text()
                self._guardar_campo_en_json('basePresupuesto', valor)
                self._guardar_cambios_pendientes()
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_base_presupuesto_changed: {e}")

    def _on_cert_base_changed(self):
        """Evento: certBase cambió - CON CÁLCULOS Y AUTO-GUARDADO"""
        if self.cargando_datos or not self.controlador_calculos:
            return
        
        try:
            # Ejecutar cálculos
            self.controlador_calculos.calcular_certificacion_completa(self.main_window)
            
            # AUTO-GUARDADO: Guardar el valor modificado
            if hasattr(self.main_window, 'certBase'):
                widget = self.main_window.certBase
                valor = str(widget.value()) if hasattr(widget, 'value') else widget.text()
                self._guardar_campo_en_json('certBase', valor)
                self._guardar_cambios_pendientes()
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_cert_base_changed: {e}")
    
    def _on_tw_empresas_changed(self, item):
        """Evento: TwEmpresas cambió - CON GUARDADO AUTOMÁTICO"""
        if self.cargando_datos or not item or not self.controlador_calculos:
            return
        
        try:
            fila = item.row()
            columna = item.column()
            valor = item.text()
            
            print(f"[ControladorEventosUI] TwEmpresas[{fila},{columna}] = '{valor}'")
            
            # 🔄 SINCRONIZAR SIEMPRE QUE CAMBIE CUALQUIER COLUMNA DE EMPRESAS
            # Esto asegura que los nombres en la tabla de ofertas estén actualizados
            self.controlador_calculos.sincronizar_empresas_ofertas(self.main_window)
            
            if columna == 1:  # Segunda columna
                self.controlador_calculos.validar_datos_empresas(self.main_window, fila, valor)
            
            # GUARDAR AUTOMÁTICAMENTE EN JSON
            self._guardar_tabla_empresas_en_json()
            
        except Exception as e:
            print(f"[ControladorEventosUI] Error en _on_tw_empresas_changed: {e}")

    def _on_tw_empresas_selection_changed(self):
        """Evento: Selección en TwEmpresas cambió - sincronizar con TwOfertas"""
        if self.cargando_datos:
            return
            
        try:
            if not hasattr(self.main_window, 'TwEmpresas') or not hasattr(self.main_window, 'TwOfertas'):
                return
                
            tabla_empresas = self.main_window.TwEmpresas
            tabla_ofertas = self.main_window.TwOfertas
            
            # Obtener filas seleccionadas
            filas_seleccionadas = tabla_empresas.selectionModel().selectedRows()
            
            if filas_seleccionadas:
                fila_seleccionada = filas_seleccionadas[0].row()
                print(f"[ControladorEventosUI] 🏢 Empresa seleccionada fila: {fila_seleccionada}")
                
                # Obtener nombre de la empresa seleccionada
                nombre_item = tabla_empresas.item(fila_seleccionada, 0)
                nombre_empresa = nombre_item.text().strip() if nombre_item else ""
                
                if nombre_empresa:
                    print(f"[ControladorEventosUI] 🔍 Buscando oferta para: '{nombre_empresa}'")
                    
                    # Buscar la empresa correspondiente en la tabla de ofertas
                    for row in range(tabla_ofertas.rowCount()):
                        oferta_empresa_item = tabla_ofertas.item(row, 0)
                        if oferta_empresa_item and oferta_empresa_item.text().strip() == nombre_empresa:
                            # Seleccionar la fila correspondiente en ofertas
                            tabla_ofertas.selectRow(row)
                            # Hacer foco en la celda de la oferta (columna 1) para facilitar edición
                            tabla_ofertas.setCurrentCell(row, 1)
                            print(f"[ControladorEventosUI] ✅ Oferta seleccionada fila {row}, enfocada para edición")
                            return
                    
                    # Si no se encuentra, limpiar selección
                    tabla_ofertas.clearSelection()
                    print(f"[ControladorEventosUI] ⚠️ No se encontró oferta para '{nombre_empresa}'")
                    
        except Exception as e:
            print(f"[ControladorEventosUI] ❌ Error en _on_tw_empresas_selection_changed: {e}")

    def _guardar_tabla_empresas_en_json(self):
        """Guardar tabla de empresas - OPTIMIZADO"""
        try:
            if not hasattr(self.main_window, 'TwEmpresas'):
                return
            
            contrato_actual = None
            if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                contrato_actual = self.main_window.contract_manager.get_current_contract()
            
            if not contrato_actual:
                return
            
            # Leer datos de la tabla
            tabla = self.main_window.TwEmpresas
            empresas_data = []
            mapeo_columnas = {0: 'nombre', 1: 'nif', 2: 'email', 3: 'contacto'}
            
            for fila in range(tabla.rowCount()):
                nombre_item = tabla.item(fila, 0)
                if nombre_item and nombre_item.text().strip():
                    empresa = {}
                    for col in range(min(tabla.columnCount(), len(mapeo_columnas))):
                        campo_json = mapeo_columnas[col]
                        item = tabla.item(fila, col)
                        valor = item.text().strip() if item else ''
                        empresa[campo_json] = valor
                    empresas_data.append(empresa)
            
            # Usar guardado diferido
            self._cambios_pendientes['empresas'] = empresas_data
                
        except Exception as e:
            print(f"[ControladorEventosUI] Error guardando empresas: {e}")
    
    def _on_tw_ofertas_changed(self, item):
        """Evento: TwOfertas cambió"""
        if self.cargando_datos or not item or not self.controlador_calculos:
            return

        try:
            fila = item.row()
            columna = item.column()
            valor = item.text()
            
            print(f"[ControladorEventosUI] TwOfertas[{fila},{columna}] = '{valor}'")

            if columna == 1:
                resultado = self.controlador_calculos.calcular_ofertas_completo(self.main_window)
                
                if hasattr(self.main_window, 'controlador_autosave'):
                    self.main_window.controlador_autosave.guardar_tabla_ofertas_en_json()
        except Exception as e:
            print(f"[ControladorEventosUI] Error en _on_tw_ofertas_changed: {e}")

    def _on_tab_changed(self, index):
        """Evento: Tab cambió"""
        if self.cargando_datos:
            return
        
        try:
            if hasattr(self.main_window, 'tabWidget') and self.main_window.tabWidget:
                tab_name = self.main_window.tabWidget.tabText(index)
                widget_name = self.main_window.tabWidget.widget(index).objectName() if self.main_window.tabWidget.widget(index) else None
                
                print(f"[ControladorEventosUI] Cambio a tab {index}: '{tab_name}' ({widget_name})")
                
                self._ejecutar_funcion_tab(index, tab_name, widget_name)
        except Exception as e:
            print(f"[ControladorEventosUI] Error en _on_tab_changed: {e}")

    def _ejecutar_funcion_tab(self, index, tab_name, widget_name):
        """Ejecuta la función específica según el tab seleccionado"""
        try:
            if index == 6 or widget_name == 'Resumen':  # Tab Resumen
                if (hasattr(self.main_window, 'integrador_resumen') and 
                    self.main_window.integrador_resumen):
                    print("[ControladorEventosUI] Reconectando botones del resumen...")
                    self.main_window.integrador_resumen.reconectar_botones_si_es_necesario()
                    print("[ControladorEventosUI] Botones del resumen reconectados")
                
        except Exception as e:
            print(f"[ControladorEventosUI] Error ejecutando función de tab: {e}")

    def _on_focus_lost(self, nombre, widget):
        """Evento: Widget perdió el foco - GUARDAR CAMBIOS"""
        if self.cargando_datos:
            return
        try:
            if hasattr(widget, 'value'):
                valor = str(widget.value())
            elif hasattr(widget, 'text'):
                valor = widget.text()
            else:
                valor = str(widget)
            
            self._guardar_campo_en_json(nombre, valor)
            self._guardar_cambios_pendientes()
            
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_focus_lost: {e}")
    
    def _on_radiobutton_changed(self):
        """Evento: RadioButton cambió"""
        if self.cargando_datos or not self.controlador_calculos:
            return
        
        try:
            self.controlador_calculos.actualizar_justificacion_limites(self.main_window)
        except Exception as e:
            print(f"[ControladorEventosUI] Error en _on_radiobutton_changed: {e}")



    def _on_fecha_contrato_changed(self):
        """Evento: fechaContrato cambió"""
        if self.cargando_datos or not self.controlador_calculos:
            return
        
        try:
            self.controlador_calculos.calcular_anualidades(self.main_window)
            
            # AUTO-GUARDADO: Guardar la fecha modificada
            if hasattr(self.main_window, 'fechaContrato'):
                widget = self.main_window.fechaContrato
                if hasattr(widget, 'date'):
                    fecha = widget.date()
                    valor = fecha.toString('yyyy-MM-dd') if hasattr(fecha, 'toString') else str(fecha)
                    self._guardar_campo_en_json('fechaContrato', valor)
                    self._guardar_cambios_pendientes()
                    
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_fecha_contrato_changed: {e}")



    def _on_num_empresas_presentadas_changed(self):
        """Evento: numEmpresasPresentadas cambió - AUTO-GUARDADO"""
        print(f"[CAMBIO_CONTRATO] 🔥 _on_num_empresas_presentadas_changed EJECUTADO - cargando_datos={self.cargando_datos}")
        
        if self.cargando_datos:
            print(f"[CAMBIO_CONTRATO] ⏸️ SKIP - cargando datos")
            return
        
        try:
            if hasattr(self.main_window, 'numEmpresasPresentadas'):
                widget = self.main_window.numEmpresasPresentadas
                valor = widget.text() if hasattr(widget, 'text') else str(widget.value() if hasattr(widget, 'value') else '')
                print(f"[CAMBIO_CONTRATO] 🏢 numEmpresasPresentadas = '{valor}' - GUARDANDO")
                self._guardar_campo_en_json('numEmpresasPresentadas', valor)
            else:
                print(f"[CAMBIO_CONTRATO] ❌ Widget numEmpresasPresentadas no encontrado")
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_num_empresas_presentadas_changed: {e}")
            import traceback
            traceback.print_exc()

    def _on_num_empresas_solicitadas_changed(self):
        """Evento: numEmpresasSolicitadas cambió - AUTO-GUARDADO"""
        print(f"[CAMBIO_CONTRATO] 🔥 _on_num_empresas_solicitadas_changed EJECUTADO - cargando_datos={self.cargando_datos}")
        
        if self.cargando_datos:
            print(f"[CAMBIO_CONTRATO] ⏸️ SKIP - cargando datos")
            return
        
        try:
            if hasattr(self.main_window, 'numEmpresasSolicitadas'):
                widget = self.main_window.numEmpresasSolicitadas
                valor = widget.text() if hasattr(widget, 'text') else str(widget.value() if hasattr(widget, 'value') else '')
                print(f"[CAMBIO_CONTRATO] 🏢 numEmpresasSolicitadas = '{valor}' - GUARDANDO")
                self._guardar_campo_en_json('numEmpresasSolicitadas', valor)
            else:
                print(f"[CAMBIO_CONTRATO] ❌ Widget numEmpresasSolicitadas no encontrado")
                
        except Exception as e:
            print(f"[ControladorEventosUI] ERROR Error en _on_num_empresas_solicitadas_changed: {e}")
            import traceback
            traceback.print_exc()

    def _on_combo_changed(self, nuevo_contrato: str):
        """Evento: ComboBox de contratos cambió"""
        try:
            if self.cargando_datos:
                return
                
            print(f"[ControladorEventosUI] Cambio de contrato a: {nuevo_contrato}")
            
            # Ejecutar función original de crear carpeta
            if hasattr(self.main_window, '_crear_carpeta_con_controlador_archivos'):
                self.main_window._crear_carpeta_con_controlador_archivos()
            
            # Actualizar cronograma visual
            if (hasattr(self.main_window, 'integrador_resumen') and 
                self.main_window.integrador_resumen and
                nuevo_contrato):
                
                QTimer.singleShot(500, lambda: self._actualizar_cronograma_on_combo_change(nuevo_contrato))
                
        except Exception as e:
            print(f"[ControladorEventosUI] Error en cambio de ComboBox: {e}")
    
    def _actualizar_cronograma_on_combo_change(self, nombre_contrato: str):
        """Actualizar el cronograma cuando cambia el contrato seleccionado"""
        try:
            print(f"[ControladorEventosUI] Actualizando cronograma para contrato: {nombre_contrato}")
            
            if (hasattr(self.main_window, 'integrador_resumen') and 
                self.main_window.integrador_resumen and
                hasattr(self.main_window.integrador_resumen, '_actualizar_cronograma_visual')):
                
                self.main_window.integrador_resumen._actualizar_cronograma_visual(nombre_contrato)
                print("[ControladorEventosUI] Cronograma actualizado tras cambio de contrato")
            else:
                print("[ControladorEventosUI] Integrador de resumen no disponible para actualizar cronograma")
                
        except Exception as e:
            print(f"[ControladorEventosUI] Error actualizando cronograma en cambio de contrato: {e}")

    def _ejecutar_cambio_expediente(self):
        """Ejecutar cambio de expediente con indicación visual de resultado"""
        try:
            if (hasattr(self.main_window, 'gestor_archivos_unificado') and
                hasattr(self.main_window.gestor_archivos_unificado, 'renombrar_carpeta_por_expediente')):
                
                resultado = self.main_window.gestor_archivos_unificado.renombrar_carpeta_por_expediente()
                
                # Solo mostrar mensaje de éxito si realmente fue exitoso
                if resultado:
                    QMessageBox.information(
                        self.main_window,
                        "✅ Cambio de Expediente Exitoso",
                        "El cambio de expediente se completó correctamente.\n\n"
                        "✓ Carpeta renombrada\n"
                        "✓ Datos actualizados"
                    )
                    print("[ControladorEventosUI] Cambio de expediente ejecutado exitosamente")
                else:
                    # No mostrar mensaje adicional porque ya se mostró el error específico
                    print("[ControladorEventosUI] Cambio de expediente cancelado o falló")
                
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Error - Cambio de Expediente",
                    "No se encontró el gestor de archivos o la función de cambio de expediente."
                )
                print("[ControladorEventosUI] Error: gestor_archivos_unificado o función no encontrada")
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error - Cambio de Expediente",
                f"Error ejecutando el cambio de expediente:\n\n{str(e)}"
            )
            print(f"[ControladorEventosUI] Error ejecutando cambio de expediente: {e}")
    
    def _ejecutar_editar_firmantes(self):
        """Ejecutar editor de firmantes - delega a main_window"""
        try:
            if self.main_window and hasattr(self.main_window, 'abrir_editor_firmantes'):
                self.main_window.abrir_editor_firmantes()
                print("[ControladorEventosUI] Editor de firmantes ejecutado")
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Error - Editor de Firmantes",
                    "No se pudo abrir el editor de firmantes."
                )
                print("[ControladorEventosUI] Error: main_window o función no encontrada")
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error - Editor de Firmantes",
                f"Error abriendo el editor de firmantes:\n\n{str(e)}"
            )
            print(f"[ControladorEventosUI] Error ejecutando editor de firmantes: {e}")

    # =================== MÉTODOS DE CONTROL ===================
    
    def pausar_eventos(self):
        """Pausar eventos"""
        self.cargando_datos = True
        print("[ControladorEventosUI] Pausado")
    
    def reanudar_eventos(self):
        """Reanudar eventos"""
        self.cargando_datos = False
        print("[ControladorEventosUI] Reanudado")
    
    def esta_pausado(self) -> bool:
        """Verificar si está pausado"""
        return self.cargando_datos
    
    def configurar_eventos_perdida_foco(self):
        """Configurar eventos de pérdida de foco"""
        try:
            widgets_con_foco = []
            
            if hasattr(self.main_window, 'findChildren'):
                widgets_con_foco.extend(self.main_window.findChildren(QLineEdit))
                widgets_con_foco.extend(self.main_window.findChildren(QTextEdit))
                widgets_con_foco.extend(self.main_window.findChildren(QDoubleSpinBox))
            
            for widget in widgets_con_foco:
                if widget.objectName() and not widget.objectName().startswith('qt_'):
                    try:
                        original_focus_out = getattr(widget, 'focusOutEvent', None)
                        if original_focus_out:
                            def create_focus_out_handler(w, orig_handler):
                                def handler(event):
                                    if orig_handler:
                                        orig_handler(event)
                                    # 🆕 SOLUCIÓN CONFLICTO: Llamar también al auto-guardado
                                    if (hasattr(self.main_window, 'controlador_autosave') and 
                                        self.main_window.controlador_autosave and
                                        hasattr(self.main_window.controlador_autosave, '_guardar_campo_inmediato') and
                                        not self.main_window.controlador_autosave.cargando_datos):
                                        nombre_widget = w.objectName()
                                        if nombre_widget and not nombre_widget.startswith('qt_'):
                                            self.main_window.controlador_autosave._guardar_campo_inmediato(nombre_widget, w)
                                return handler
                            
                            widget.focusOutEvent = create_focus_out_handler(widget, original_focus_out)
                    except Exception:
                        pass
            
            print("[ControladorEventosUI] Eventos de pérdida de foco configurados")
            
        except Exception as e:
            print(f"[ControladorEventosUI] Error configurando eventos de pérdida de foco: {e}")

    def verificar_conexiones_botones(self):
        """Método de diagnóstico para verificar que los botones estén conectados"""
        print("\n[ControladorEventosUI] VERIFICANDO CONEXIONES DE BOTONES:")
        print("=" * 60)
        
        botones_criticos = ['cerrar_app', 'minimizar_app']
        acciones_navegacion = ['actionCambiar_tipo', 'actionCrear_Proyecto', 'actionBorrar_Proyecto']
        botones_documentos = ['Generar_Acta_Inicio', 'Generar_Cartas_inv', 'Generar_acta_adj']
        
        total_encontrados = 0
        total_verificados = 0
        
        # Verificar botones críticos
        print("BOTONES CRÍTICOS:")
        for boton_name in botones_criticos:
            total_verificados += 1
            if hasattr(self.main_window, boton_name):
                boton = getattr(self.main_window, boton_name)
                if boton and hasattr(boton, 'clicked'):
                    print(f"  {boton_name}: ENCONTRADO y CONECTADO")
                    total_encontrados += 1
                else:
                    print(f"  {boton_name}: ENCONTRADO pero SIN CLICKED")
            else:
                print(f"  {boton_name}: NO ENCONTRADO")
        
        # Verificar botones de navegación
        print("\nBOTONES DE NAVEGACIÓN:")
        for boton_name in botones_navegacion:
            total_verificados += 1
            if hasattr(self.main_window, boton_name):
                boton = getattr(self.main_window, boton_name)
                if boton and hasattr(boton, 'clicked'):
                    print(f"  {boton_name}: ENCONTRADO y CONECTADO")
                    total_encontrados += 1
                else:
                    print(f"  {boton_name}: ENCONTRADO pero SIN CLICKED")
            else:
                print(f"  {boton_name}: NO ENCONTRADO")
        
        # Verificar botones de documentos
        print("\nBOTONES DE DOCUMENTOS:")
        for boton_name in botones_documentos:
            total_verificados += 1
            if hasattr(self.main_window, boton_name):
                boton = getattr(self.main_window, boton_name)
                if boton and hasattr(boton, 'clicked'):
                    print(f"  {boton_name}: ENCONTRADO y CONECTADO")
                    total_encontrados += 1
                else:
                    print(f"  {boton_name}: ENCONTRADO pero SIN CLICKED")
            else:
                print(f"  {boton_name}: NO ENCONTRADO")
        
        # Resumen
        print(f"\nRESUMEN: {total_encontrados}/{total_verificados} botones verificados correctamente")
        print("=" * 60)
        
        return total_encontrados, total_verificados
    
    def verificar_campos_criticos_tras_carga(self):
        """Verificar campos críticos después de cargar un contrato"""
        print(f"[CAMBIO_CONTRATO] 🔍 VERIFICANDO CAMPOS CRÍTICOS TRAS CARGA:")
        self.verificar_carga_campo('plazoEjecucion')
        self.verificar_carga_campo('numEmpresasPresentadas')
        self.verificar_carga_campo('numEmpresasSolicitadas')
        self.verificar_carga_campo('basePresupuesto')
        self.verificar_carga_campo('precioAdjudicacion')
    
    def cargar_empresas_desde_json(self, nombre_contrato):
        """Cargar empresas desde JSON - OPTIMIZADO"""
        try:
            if not hasattr(self.main_window, 'TwEmpresas'):
                return
            
            # Pausar eventos
            self.cargando_datos = True
            
            # FORZAR RECARGA DE DATOS FRESCOS DEL JSON
            if (hasattr(self.main_window, 'controlador_json') and 
                self.main_window.controlador_json):
                
                contrato_data = self.main_window.controlador_json.leer_contrato_completo(nombre_contrato)
                
                if contrato_data and 'empresas' in contrato_data:
                    tabla = self.main_window.TwEmpresas
                    empresas = contrato_data['empresas']
                    
                    # BLOQUEAR SEÑALES DE LA TABLA
                    tabla.blockSignals(True)
                    
                    # MAPEO CORRECTO DE CAMPOS JSON A COLUMNAS
                    mapeo_columnas = {0: 'nombre', 1: 'nif', 2: 'email', 3: 'contacto'}
                    
                    # LIMPIAR Y RECARGAR TODO
                    tabla.setRowCount(len(empresas))
                    
                    for i, empresa in enumerate(empresas):
                        for col in range(min(tabla.columnCount(), len(mapeo_columnas))):
                            campo_json = mapeo_columnas[col]
                            valor = empresa.get(campo_json, '')
                            tabla.setItem(i, col, QTableWidgetItem(valor))
                    
                    # DESBLOQUEAR SEÑALES DE LA TABLA
                    tabla.blockSignals(False)
                           
                    print(f"[ControladorEventosUI] Cargadas {len(empresas)} empresas")
                else:
                    # LIMPIAR TABLA SI NO HAY EMPRESAS
                    tabla = self.main_window.TwEmpresas
                    tabla.blockSignals(True)
                    tabla.setRowCount(0)
                    tabla.blockSignals(False)
            
        except Exception as e:
            print(f"[ControladorEventosUI] Error cargando empresas: {e}")
        finally:
            # Reactivar eventos
            self.cargando_datos = False
    
    # =================== AUTO-GUARDADO ===================
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.cargando_datos = False
        self.controlador_calculos = None
        self.conectar_boton_actuacion_mail()
        # SISTEMA DE GUARDADO POR FOCO
        self._cambios_pendientes = {}
        print("[ControladorEventosUI] [INIT] Inicializado - Solo Eventos")

    def _guardar_campo_en_json(self, nombre_campo: str, valor: str):
        """Acumular campo para guardado por foco"""
        self._cambios_pendientes[nombre_campo] = valor
    
    def _guardar_cambios_pendientes(self):
        """Guardar todos los cambios pendientes inmediatamente"""
        if not self._cambios_pendientes or self.cargando_datos:
            return
            
        try:
            if not (hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json):
                return
                
            if not (hasattr(self.main_window, 'contract_manager') and 
                   self.main_window.contract_manager and
                   hasattr(self.main_window.contract_manager, 'current_contract') and
                   self.main_window.contract_manager.current_contract):
                return
            
            contrato_actual = self.main_window.contract_manager.current_contract
            
            # Separar empresas de otros campos
            empresas_data = self._cambios_pendientes.pop('empresas', None)
            
            # Guardar campos normales
            if self._cambios_pendientes:
                self.main_window.controlador_json.actualizar_contrato(
                    contrato_actual, self._cambios_pendientes, guardar_inmediato=True
                )
            
            # Guardar empresas por separado
            if empresas_data:
                self.main_window.controlador_json.guardar_empresas_unificadas_en_json(
                    contrato_actual, empresas_data
                )
            
            # Limpiar cambios pendientes
            self._cambios_pendientes.clear()
                
        except Exception as e:
            print(f"[CAMBIO_CONTRATO] ERROR Error guardando: {e}")
    
