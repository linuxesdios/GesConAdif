#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador especializado para auto-guardado en pérdida de foco
"""
from PyQt5 import QtWidgets
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ControladorAutoGuardado:
    """Controlador especializado para auto-guardado en pérdida de foco"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.cargando_datos = False
        self.controlador_json = None
        self.contract_manager = None
        self.guardando_en_proceso = False
        self.ultimo_guardado = {}
        


    def set_dependencies(self, controlador_json, contract_manager):
        """Establecer dependencias necesarias para el guardado"""
        self.controlador_json = controlador_json
        self.contract_manager = contract_manager


    def iniciar_carga_datos(self):
        """Pausar auto-guardado durante carga de datos"""
        self.cargando_datos = True
        logger.info(f"🔒 DIAGNÓSTICO: cargando_datos = TRUE - auto-guardado PAUSADO")
        
    def finalizar_carga_datos(self):
        """Reactivar auto-guardado después de carga"""
        self.cargando_datos = False
        self.ultimo_guardado.clear()
        logger.info(f"🔓 DIAGNÓSTICO: cargando_datos = FALSE - auto-guardado ACTIVADO")


    def configurar_auto_guardado_completo(self):
        """Configurar auto-guardado para todos los widgets"""
        try:
            logger.info(f"🔧 DIAGNÓSTICO: Iniciando configuración auto-guardado completo")
            self.configurar_auto_guardado_campos()
            self.configurar_auto_guardado_tablas()
            logger.info(f"✅ DIAGNÓSTICO: Configuración auto-guardado completo terminada")
            
        except Exception as e:
            logger.error(f"Error configurando auto-guardado: {e}")

    def configurar_auto_guardado_campos(self):
        """Configurar auto-guardado para campos editables en pérdida de foco"""
        try:
            tipos_soportados = (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QDateEdit, 
                              QtWidgets.QTimeEdit, QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox, QtWidgets.QComboBox)
            
            widgets = self.main_window.findChildren(tipos_soportados)

            for widget in widgets:
                nombre = widget.objectName()
                if not nombre or nombre.startswith('qt_'):
                    continue

                if isinstance(widget, QtWidgets.QLineEdit):
                    self._configurar_lineedit_con_focusout(widget, nombre)
                elif isinstance(widget, QtWidgets.QTextEdit):
                    self._configurar_textedit_con_focusout(widget, nombre)
                elif isinstance(widget, (QtWidgets.QDateEdit, QtWidgets.QTimeEdit, 
                                        QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox)):
                    widget.editingFinished.connect(lambda w=widget, n=nombre: self._guardar_campo_inmediato(n, w))
                elif isinstance(widget, QtWidgets.QComboBox):
                    # EXCLUIR EL COMBO SELECTOR PRINCIPAL PARA EVITAR BUCLES
                    if nombre == 'comboBox' and hasattr(self.main_window, 'comboBox'):
                        # Este es el selector principal de contratos, NO guardarlo automáticamente
                        logger.info(f"⚠️ AUTOSAVE: Excluyendo comboBox selector principal del auto-guardado")
                        continue
                    widget.activated.connect(lambda _, w=widget, n=nombre: self._guardar_campo_inmediato(n, w))
            
        except Exception as e:
            logger.error(f"Error configurando campos: {e}")




    def _configurar_textedit_con_focusout(self, widget, nombre):
        """Configurar QTextEdit usando focusOutEvent - INMEDIATO"""
        original_focus_out = widget.focusOutEvent
        
        def custom_focus_out(event):
            # Llamar al evento original primero
            if original_focus_out:
                original_focus_out(event)
            
            # Guardar inmediatamente al perder foco
            if not self.cargando_datos:
                self._guardar_campo_inmediato(nombre, widget)
        
        widget.focusOutEvent = custom_focus_out

    def _configurar_lineedit_con_focusout(self, widget, nombre):
        """Configurar QLineEdit usando focusOutEvent - INMEDIATO"""
        original_focus_out = widget.focusOutEvent
        
        def custom_focus_out(event):
            # Llamar al evento original primero
            if original_focus_out:
                original_focus_out(event)
            
            # Guardar inmediatamente al perder foco
            if not self.cargando_datos:
                self._guardar_campo_inmediato(nombre, widget)
        
        widget.focusOutEvent = custom_focus_out

    def configurar_auto_guardado_tablas(self):
        """Configurar auto-guardado para tablas en pérdida de foco"""
        try:
            logger.info(f"🔧 DIAGNÓSTICO: Configurando auto-guardado de tablas")
            
            if hasattr(self.main_window, 'TwEmpresas'):
                tabla = self.main_window.TwEmpresas
                tabla.itemChanged.connect(lambda item: self._auto_guardar_tabla_empresas() if not self.cargando_datos else None)
                logger.info(f"✅ DIAGNÓSTICO: TwEmpresas configurada para auto-guardado")
            else:
                logger.warning(f"⚠️ DIAGNÓSTICO: TwEmpresas NO encontrada")
            
            if hasattr(self.main_window, 'TwOfertas'):
                tabla = self.main_window.TwOfertas
                tabla.itemChanged.connect(lambda item: self._auto_guardar_tabla_ofertas() if not self.cargando_datos else None)
                logger.info(f"✅ DIAGNÓSTICO: TwOfertas configurada para auto-guardado")
            else:
                logger.warning(f"⚠️ DIAGNÓSTICO: TwOfertas NO encontrada")
            
        except Exception as e:
            logger.error(f"Error configurando tablas: {e}")


    def _guardar_campo_inmediato(self, nombre_campo: str, widget) -> bool:
        """Guardar campo inmediatamente al perder foco"""
        try:
            if not self._verificar_dependencias():
                return False

            # USAR ÚNICA FUENTE DE VERDAD
            contrato = self.obtener_contrato_actual()
            if not contrato:
                return False

            # Extraer valor del widget
            valor = self._extraer_valor_widget(widget)
            if valor is None:
                return False

            # Verificar si el valor realmente cambió
            cache_key = f"{contrato}_{nombre_campo}"
            if cache_key in self.ultimo_guardado and self.ultimo_guardado[cache_key] == valor:
                return True  # No cambio, pero no es error

            # Guardar inmediatamente
            resultado = self.controlador_json.guardar_campo_en_json(contrato, nombre_campo, valor)
            
            if resultado:
                self.ultimo_guardado[cache_key] = valor
            
            return resultado
                
        except Exception as e:
            logger.error(f"Error guardando inmediato: {e}")
            return False
    
    def _guardar_campo_obra(self, nombre_campo: str, valor: str, widget) -> bool:
        """Guardar campo en obra individual - OPTIMIZADO"""
        try:
            if not self._verificar_dependencias():
                return False

            # USAR ÚNICA FUENTE DE VERDAD
            contrato = self.obtener_contrato_actual()
            if not contrato:
                return False

            # SIMPLIFICACION: Usar solo el método básico para todos
            resultado = self.controlador_json.guardar_campo_en_json(contrato, nombre_campo, valor)
            
            return resultado
                
        except Exception as e:
            logger.error(f"Error guardando campo obra: {e}")
            return False

    def _auto_guardar_tabla_empresas(self):
        """MODIFICADA: Guardar estructura unificada"""
        logger.info(f"🔥 DIAGNÓSTICO: _auto_guardar_tabla_empresas() LLAMADO")
        
        if self.cargando_datos:
            logger.warning(f"⚠️ DIAGNÓSTICO: Guardado bloqueado - cargando_datos = {self.cargando_datos}")
            return
            
        try:
            if not self._verificar_dependencias():
                logger.warning(f"⚠️ DIAGNÓSTICO: Dependencias no verificadas")
                return

            # USAR ÚNICA FUENTE DE VERDAD
            contrato = self.obtener_contrato_actual()
            if not contrato:
                logger.warning(f"⚠️ DIAGNÓSTICO: No hay contrato actual")
                return
            
            logger.info(f"📊 DIAGNÓSTICO: Guardando empresas para contrato: '{contrato}'")
            
            # Extraer datos unificados
            empresas_data = self._extraer_datos_tabla_empresas()
            logger.info(f"📊 DIAGNÓSTICO: Extraídas {len(empresas_data)} empresas de la tabla")
            
            # Verificar cambios reales
            cache_key = "empresas_unificadas"
            if cache_key in self.ultimo_guardado and self.ultimo_guardado[cache_key] == empresas_data:
                logger.info(f"📊 DIAGNÓSTICO: Sin cambios en empresas - no guardando")
                return  # Sin cambios

            # ✅ GUARDAR ESTRUCTURA UNIFICADA
            if self.controlador_json.guardar_empresas_unificadas_en_json(contrato, empresas_data):
                self.ultimo_guardado[cache_key] = empresas_data
                logger.info(f"✅ DIAGNÓSTICO: Empresas guardadas exitosamente")
            else:
                logger.error(f"❌ DIAGNÓSTICO: Error guardando empresas en JSON")
            
        except Exception as e:
            logger.error(f"Error guardando empresas unificadas: {e}")

    def _auto_guardar_tabla_ofertas(self):
        """MODIFICADA: Las ofertas se guardan junto con empresas"""
        # ✅ NO HACER NADA - Las ofertas se guardan en _auto_guardar_tabla_empresas
        pass

    def forzar_guardado_completo(self):
        """Forzar guardado completo"""
        try:
            if self.guardando_en_proceso or self.cargando_datos:
                return False
            
            self.guardando_en_proceso = True
            self._forzar_guardado_tablas()
            return True
           
        except Exception as e:
            logger.error(f"Error en guardado forzado: {e}")
            return False
        finally:
            self.guardando_en_proceso = False

    def _extraer_valor_widget(self, widget) -> Optional[str]:
        """Extraer valor de un widget según su tipo"""
        try:
            if isinstance(widget, QtWidgets.QLineEdit):
                return widget.text().strip()
            elif isinstance(widget, QtWidgets.QTextEdit):
                return widget.toPlainText().strip()
            elif isinstance(widget, QtWidgets.QDateEdit):
                return widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QtWidgets.QTimeEdit):
                return widget.time().toString("HH:mm")
            
            elif isinstance(widget, QtWidgets.QSpinBox):
                return str(int(widget.value()))  # ENTERO para QSpinBox
            elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                return str(widget.value())  # DECIMAL para QDoubleSpinBox
                
            elif isinstance(widget, QtWidgets.QComboBox):
                return widget.currentText().strip()
            else:
                return None
        except Exception:
            return None

    def _extraer_datos_tabla_empresas(self) -> list:
        """NUEVA: Extraer datos unificados de ambas tablas"""
        empresas_data = []
        
        try:
            tabla_empresas = self.main_window.TwEmpresas
            tabla_ofertas = getattr(self.main_window, 'TwOfertas', None)
            
            for row in range(tabla_empresas.rowCount()):
                # Extraer datos de tabla empresas
                item_nombre = tabla_empresas.item(row, 0)
                item_nif = tabla_empresas.item(row, 1)
                item_email = tabla_empresas.item(row, 2)
                item_contacto = tabla_empresas.item(row, 3)
                
                nombre = item_nombre.text().strip() if item_nombre else ""
                nif = item_nif.text().strip() if item_nif else ""
                email = item_email.text().strip() if item_email else ""
                contacto = item_contacto.text().strip() if item_contacto else ""
                
                # Extraer oferta de tabla ofertas (misma fila)
                ofertas = ""
                if tabla_ofertas and row < tabla_ofertas.rowCount():
                    item_ofertas = tabla_ofertas.item(row, 1)
                    ofertas = item_ofertas.text().strip() if item_ofertas else ""
                
                # ✅ ESTRUCTURA UNIFICADA
                empresa_unificada = {
                    'nombre': nombre,
                    'nif': nif,
                    'email': email,
                    'contacto': contacto,
                    'ofertas': ofertas
                }
                
                # Solo agregar si tiene contenido
                if nombre or nif or email or contacto or ofertas:
                    empresas_data.append(empresa_unificada)
            

            
        except Exception as e:
            logger.error(f"Error extrayendo empresas unificadas: {e}")
        
        return empresas_data
    def _extraer_datos_tabla_ofertas(self) -> list:
        """Extraer todos los datos de la tabla de ofertas"""
        ofertas_data = []
        
        try:
            tabla = self.main_window.TwOfertas
            
            for row in range(tabla.rowCount()):
                fila_data = {}
                fila_vacia = True
                
                for col in range(tabla.columnCount()):
                    item = tabla.item(row, col)
                    valor = item.text().strip() if item else ""
                    
                    # Usar nombres específicos para ofertas
                    if col == 0:
                        nombre_columna = "empresa"
                    elif col == 1:
                        nombre_columna = "oferta_(€)"
                    else:
                        nombre_columna = f"columna_{col}"
                    
                    fila_data[nombre_columna] = valor
                    if valor:
                        fila_vacia = False
                
                if not fila_vacia:
                    ofertas_data.append(fila_data)
            
        except Exception as e:
            logger.error(f"Error extrayendo datos tabla ofertas: {e}")
        
        return ofertas_data

    def _verificar_dependencias(self) -> bool:
        """Verificar que las dependencias están disponibles"""
        if self.controlador_json and self.contract_manager:
            return True
        
        if hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json:
            self.controlador_json = self.main_window.controlador_json
        
        if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
            self.contract_manager = self.main_window.contract_manager
        
        return bool(self.controlador_json and self.contract_manager)

    def _forzar_guardado_tablas(self):
        """Forzar guardado de todas las tablas configuradas"""
        try:
            if hasattr(self.main_window, 'TwEmpresas'):
                self._auto_guardar_tabla_empresas()
            
            if hasattr(self.main_window, 'TwOfertas'):
                self._auto_guardar_tabla_ofertas()
            
        except Exception as e:
            logger.error(f"Error guardado forzado tablas: {e}")

    def actualizar(self, nombre_contrato: str):
        """Actualizar todos los campos y tablas desde el JSON para el contrato especificado"""
        try:
            if not self._verificar_dependencias():
                logger.error("Dependencias no disponibles")
                return False

            self.iniciar_carga_datos()
            
            # Leer datos del contrato
            contract_data = self.controlador_json.leer_contrato_completo(nombre_contrato)
            if not contract_data:
                logger.error(f"No se encontró el contrato: {nombre_contrato}")
                self.finalizar_carga_datos()
                return False

            # AÑADIDO: Actualizar justificación de límites ANTES de cálculos
            self._actualizar_justificacion_limites(nombre_contrato)
            
            # CONFIGURAR EVENTO DIRECTO PARA TABLA EMPRESAS
            self.configurar_evento_tabla_empresas()
            
            # Actualizar campos de texto
            self._actualizar_campos_desde_json(contract_data)
            
            # Actualizar tablas
            self._actualizar_tablas_desde_json(contract_data)
            
            self.finalizar_carga_datos()
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando: {e}")
            self.finalizar_carga_datos()
            return False

    def _actualizar_campos_desde_json(self, contract_data):
        """Actualizar campos desde JSON"""
        tipos_soportados = (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QDateEdit, 
                          QtWidgets.QTimeEdit, QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox, QtWidgets.QComboBox)
        
        widgets = self.main_window.findChildren(tipos_soportados)
        
        for widget in widgets:
            nombre = widget.objectName()
            if not nombre or nombre.startswith('qt_'):
                continue
                
            valor = contract_data.get(nombre, "")
            if valor:
                logger.info(f"Cargando campo {nombre}: {valor}")
                self._establecer_valor_widget(widget, str(valor))

    def _actualizar_tablas_desde_json(self, contract_data):
        """Actualizar tablas desde JSON"""
        # Actualizar tabla empresas
        if hasattr(self.main_window, 'TwEmpresas') and 'empresas' in contract_data:
            self._actualizar_tabla_empresas(contract_data['empresas'])
            
        # Actualizar tabla ofertas UNIFICADO
        if hasattr(self.main_window, 'TwOfertas') and 'empresas' in contract_data:
            self.actualizar_tabla_ofertas_unificado(contract_data['empresas'])

    def _actualizar_tabla_empresas(self, empresas_data):
        """Actualizar tabla de empresas"""
        tabla = self.main_window.TwEmpresas
        tabla.setRowCount(len(empresas_data))
        
        for row, empresa in enumerate(empresas_data):
            tabla.setItem(row, 0, QtWidgets.QTableWidgetItem(empresa.get('nombre', '')))
            tabla.setItem(row, 1, QtWidgets.QTableWidgetItem(empresa.get('nif', '')))
            tabla.setItem(row, 2, QtWidgets.QTableWidgetItem(empresa.get('email', '')))
            tabla.setItem(row, 3, QtWidgets.QTableWidgetItem(empresa.get('contacto', '')))

    def actualizar_tabla_ofertas_unificado(self, source_data=None, source_type="auto"):
        """FUNCIÓN UNIFICADA: Actualizar tabla ofertas desde cualquier fuente"""
        try:
            if not hasattr(self.main_window, 'TwOfertas'):
                logger.warning("TwOfertas no encontrada")
                return False
                
            tabla = self.main_window.TwOfertas
            
            # Determinar fuente de datos
            if source_data is None:
                # Auto-detectar: leer desde tabla empresas actual
                source_type = "tabla_empresas"
                source_data = self._extraer_nombres_tabla_empresas()
            elif isinstance(source_data, list) and len(source_data) > 0:
                if isinstance(source_data[0], dict):
                    source_type = "empresas_data"
                else:
                    source_type = "nombres_lista"
            
            logger.info(f"📊 Actualizando tabla ofertas - tipo: {source_type}, elementos: {len(source_data) if source_data else 0}")
            
            # Bloquear señales
            tabla.blockSignals(True)
            
            # Guardar ofertas existentes
            ofertas_existentes = {}
            for fila in range(tabla.rowCount()):
                oferta_item = tabla.item(fila, 1)
                nombre_item = tabla.item(fila, 0)
                if nombre_item and oferta_item and oferta_item.text().strip():
                    ofertas_existentes[nombre_item.text().strip()] = oferta_item.text().strip()
            
            # Procesar según tipo de fuente
            if source_type == "empresas_data":
                tabla.setRowCount(len(source_data))
                for row, empresa in enumerate(source_data):
                    nombre = empresa.get('nombre', '')
                    ofertas = empresa.get('ofertas', ofertas_existentes.get(nombre, ''))
                    self._crear_fila_tabla_ofertas(tabla, row, nombre, ofertas)
                    
            else:  # nombres_lista o tabla_empresas
                tabla.setRowCount(len(source_data))
                for row, nombre in enumerate(source_data):
                    ofertas = ofertas_existentes.get(nombre, '')
                    self._crear_fila_tabla_ofertas(tabla, row, nombre, ofertas)
            
            tabla.blockSignals(False)
            logger.info(f"✅ Tabla ofertas actualizada - {len(source_data)} filas")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando tabla ofertas: {e}")
            if tabla:
                tabla.blockSignals(False)
            return False

    def _extraer_nombres_tabla_empresas(self):
        """Extraer nombres desde tabla empresas actual"""
        nombres = []
        if hasattr(self.main_window, 'TwEmpresas'):
            tabla = self.main_window.TwEmpresas
            for fila in range(tabla.rowCount()):
                nombre_item = tabla.item(fila, 0)
                if nombre_item and nombre_item.text().strip():
                    nombres.append(nombre_item.text().strip())
        return nombres

    def _crear_fila_tabla_ofertas(self, tabla, row, nombre, ofertas):
        """Crear fila en tabla ofertas con formato consistente"""
        # Nombre (solo lectura, fondo gris)
        item_nombre = QtWidgets.QTableWidgetItem(nombre)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)
        item_nombre.setBackground(QColor('lightgray'))
        tabla.setItem(row, 0, item_nombre)
        
        # Ofertas (editable)
        item_ofertas = QtWidgets.QTableWidgetItem(str(ofertas))
        tabla.setItem(row, 1, item_ofertas)

    def _establecer_valor_widget(self, widget, valor):
        """Establecer valor en widget según su tipo"""
        try:
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.setText(valor)
            elif isinstance(widget, QtWidgets.QTextEdit):
                widget.setPlainText(valor)
            elif isinstance(widget, QtWidgets.QComboBox):
                index = widget.findText(valor)
                if index >= 0:
                    widget.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"Error estableciendo valor: {e}")

    def esta_pausado(self) -> bool:
        """Verificar si el auto-guardado está pausado"""
        return self.cargando_datos
    
    def guardar_tabla_ofertas_en_json(self):
        """Guardar tabla TwOfertas en la estructura empresas unificada"""
        try:
            if not hasattr(self.main_window, 'TwOfertas'):
                return

            tabla = self.main_window.TwOfertas
            
            # Obtener nombre del contrato activo
            nombre_contrato = self.obtener_contrato_actual()
            if not nombre_contrato:
                logger.error("No se pudo guardar ofertas: contrato no definido")
                return

            # Obtener datos actuales del contrato
            contract_data = self.controlador_json.leer_contrato_completo(nombre_contrato)
            if not contract_data:
                logger.error("No se encontró el contrato")
                return

            # Obtener empresas actuales
            empresas_actuales = contract_data.get('empresas', [])
            if not empresas_actuales:
                logger.warning("No hay empresas en el contrato")
                return

            # Actualizar ofertas en la estructura empresas
            for fila in range(tabla.rowCount()):
                item_empresa = tabla.item(fila, 0)
                item_oferta = tabla.item(fila, 1)

                nombre_empresa = item_empresa.text().strip() if item_empresa else ""
                oferta_valor = item_oferta.text().strip() if item_oferta else ""

                # Buscar la empresa correspondiente y actualizar su oferta
                for empresa in empresas_actuales:
                    if empresa.get('nombre') == nombre_empresa:
                        empresa['ofertas'] = oferta_valor if oferta_valor else ""
                        break

            # CAMBIO: Usar método unificado
            self.controlador_json.guardar_empresas_unificadas_en_json(nombre_contrato, empresas_actuales)

        except Exception as e:
            logger.error(f"Error guardando ofertas en empresas: {e}")

    def _actualizar_justificacion_limites(self, nombre_contrato: str):
        """Actualizar justificación de límites al seleccionar proyecto"""
        try:
            if (hasattr(self.main_window, 'controlador_eventos_ui') and 
                self.main_window.controlador_eventos_ui and
                hasattr(self.main_window.controlador_eventos_ui, 'controlador_calculos')):
                
                self.main_window.controlador_eventos_ui.controlador_calculos.actualizar_justificacion_limites(self.main_window)
                logger.info(f"✅ AUTOSAVE: Justificación de límites actualizada para: {nombre_contrato}")
                
            else:
                logger.warning("No se pudo acceder al controlador_calculos para actualizar justificación")
                
        except Exception as e:
            logger.error(f"Error actualizando justificación de límites: {e}")

    def configurar_evento_tabla_empresas(self):
        """Configurar evento directo para itemChanged en tabla empresas"""
        try:
            if hasattr(self.main_window, 'TwEmpresas'):
                tabla = self.main_window.TwEmpresas
                
                # Desconectar eventos previos para evitar duplicados
                try:
                    tabla.itemChanged.disconnect()
                except:
                    pass  # No había conexiones previas
                
                # Conectar evento directo
                tabla.itemChanged.connect(self.on_tabla_empresas_changed)
                logger.info(f"✅ Evento directo configurado para TwEmpresas")
                
            else:
                logger.warning(f"⚠️ TwEmpresas no encontrada para configurar evento")
                
        except Exception as e:
            logger.error(f"Error configurando evento tabla empresas: {e}")

    def on_tabla_empresas_changed(self, item):
        """Evento directo cuando cambia un item en la tabla empresas"""
        try:
            logger.info(f"🔥 EVENTO DIRECTO: itemChanged en tabla empresas - fila: {item.row()}, col: {item.column()}")
            
            # Sincronizar tabla ofertas automáticamente
            self.actualizar_tabla_ofertas_unificado()
            
            # Llamar directamente al guardado
            self._auto_guardar_tabla_empresas()
            
        except Exception as e:
            logger.error(f"Error en evento tabla empresas: {e}")

    def obtener_contrato_actual(self) -> Optional[str]:
        """ÚNICA FUENTE DE VERDAD GLOBAL - SOLO EL COMBO"""
        try:
            if (hasattr(self.main_window, 'comboBox') and 
                self.main_window.comboBox):
                texto = self.main_window.comboBox.currentText()
                if texto and not texto.startswith("Seleccionar"):
                    return texto
            return None
        except Exception as e:
            logger.error(f"Error obteniendo contrato: {e}")
            return None