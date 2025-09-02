#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador especializado OPTIMIZADO para auto-guardado automático
Reduce guardados innecesarios y mejora rendimiento
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from typing import Optional


class ControladorAutoGuardado:
    """Controlador especializado OPTIMIZADO para auto-guardado automático"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.cargando_datos = False
        self.controlador_json = None
        self.contract_manager = None
        self.guardando_en_proceso = False
        
        # 🆕 OPTIMIZACIONES ANTI-SPAM
        self.ultimo_guardado = {}  # Cache de últimos valores guardados
        self.timer_guardado = QTimer()  # Timer para agrupar guardados
        self.timer_guardado.setSingleShot(True)
        self.timer_guardado.timeout.connect(self._ejecutar_guardado_agrupado)
        self.campos_pendientes = set()  # Campos que necesitan guardado
        


    def set_dependencies(self, controlador_json, contract_manager):
        """Establecer dependencias necesarias para el guardado"""
        self.controlador_json = controlador_json
        self.contract_manager = contract_manager


    def iniciar_carga_datos(self):
        """Pausar auto-guardado durante carga de datos"""
        self.cargando_datos = True
        self.timer_guardado.stop()  # 🆕 Cancelar guardados pendientes
        
    def finalizar_carga_datos(self):
        """Reactivar auto-guardado después de carga"""
        self.cargando_datos = False
        self.ultimo_guardado.clear()  # 🆕 Limpiar cache al cambiar contrato
        self.campos_pendientes.clear()  # 🔧 Limpiar campos pendientes también


    def configurar_auto_guardado_completo(self):
        """Configurar auto-guardado para todos los widgets"""
        try:
            self.configurar_auto_guardado_campos()
            self.configurar_auto_guardado_tablas()
            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error configurando auto-guardado: {e}")

    def configurar_auto_guardado_campos(self):
        """Configurar auto-guardado para campos editables - OPTIMIZADO"""
        try:
            tipos_soportados = (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QDateEdit, 
                              QtWidgets.QTimeEdit, QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox, QtWidgets.QComboBox)
            
            widgets = self.main_window.findChildren(tipos_soportados)
            widgets_configurados = 0

            for widget in widgets:
                nombre = widget.objectName()
                if not nombre or nombre.startswith('qt_'):
                    continue
                
                # EXCLUIR campos con handlers especiales para evitar conflictos
                campos_con_handlers_especiales = ['plazoEjecucion', 'numEmpresasPresentadas', 'numEmpresasSolicitadas']
                if nombre in campos_con_handlers_especiales:
                    print(f"[ControladorAutoGuardado] ⚠️ Omitiendo {nombre} - tiene handler especializado")
                    continue

                # USAR GUARDADO INMEDIATO AL PERDER FOCO
                if isinstance(widget, QtWidgets.QLineEdit):
                    # NUEVO: Guardar inmediatamente al perder foco
                    self._configurar_lineedit_con_focusout(widget, nombre)
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QTextEdit):
                    self._configurar_textedit_con_focusout(widget, nombre)
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QDateEdit):
                    widget.dateChanged.connect(self._crear_callback_agrupado(nombre, widget))
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QTimeEdit):
                    widget.timeChanged.connect(self._crear_callback_agrupado(nombre, widget))
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                    widget.editingFinished.connect(self._crear_callback_agrupado(nombre, widget))
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QSpinBox):
                    widget.editingFinished.connect(self._crear_callback_agrupado(nombre, widget))
                    widgets_configurados += 1
                    
                elif isinstance(widget, QtWidgets.QComboBox):
                    widget.activated.connect(self._crear_callback_agrupado(nombre, widget))
                    widgets_configurados += 1


            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error configurando campos: {e}")

    def _crear_callback_agrupado(self, nombre_campo, widget):
        """Crear callback que agrupa guardados en lugar de ejecutar inmediatamente"""
        def callback(*args):
            self._agendar_guardado_campo(nombre_campo, widget)
        return callback
    
    def _crear_callback_inmediato_plazo(self, nombre_campo, widget):
        """Crear callback especial para plazoEjecucion que guarda inmediatamente"""
        def callback(valor):
            if not self.cargando_datos:
                self._guardar_plazo_inmediato(nombre_campo, widget, valor)
        return callback

    def _guardar_plazo_inmediato(self, nombre_campo: str, widget, valor):
        """Guardar plazoEjecucion inmediatamente sin delay"""
        try:
            if not self._verificar_dependencias():
                return False

            contrato = self.contract_manager.get_current_contract()
            if not contrato:
                return False

            # Convertir a string para consistencia
            valor_str = str(int(valor))
            
            # Verificar si realmente cambió
            cache_key = f"{contrato}_{nombre_campo}"
            if cache_key in self.ultimo_guardado and self.ultimo_guardado[cache_key] == valor_str:
                return True

            # Guardar inmediatamente
            resultado = self.controlador_json.guardar_campo_en_json(contrato, nombre_campo, valor_str)
            
            if resultado:
                self.ultimo_guardado[cache_key] = valor_str
                return True
            else:
                print(f"[ControladorAutoGuardado] ❌ Error guardando {nombre_campo}")
                return False
                
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error en guardado inmediato plazo: {e}")
            return False
    
    def _agendar_guardado_campo(self, nombre_campo: str, widget):
        """Agendar guardado de campo para ejecución agrupada"""
        # SILENCIAR LOGS EXCESIVOS - solo errores importantes
        
        try:
            # Verificar si estamos cargando datos
            if self.cargando_datos:
                return
            
            # Verificar si el valor realmente cambió
            valor = self._extraer_valor_widget(widget)
            
            if valor is None:
                return

            # 🔧 CACHE MEJORADO: Incluir contrato actual en la clave
            contrato_actual = self.contract_manager.get_current_contract() if self.contract_manager else ""
            cache_key = f"{contrato_actual}_{nombre_campo}"
            
            if cache_key in self.ultimo_guardado and self.ultimo_guardado[cache_key] == valor:
                return  # Valor no cambió, no guardar

            # 🔧 PREVENIR DUPLICADOS: Remover campo existente antes de agregar
            self.campos_pendientes = {(campo, w, v) for campo, w, v in self.campos_pendientes if campo != nombre_campo}
            
            # Agendar para guardado agrupado
            self.campos_pendientes.add((nombre_campo, widget, valor))
            
            # Reiniciar timer (esperar 1 segundo sin cambios)
            self.timer_guardado.stop()
            self.timer_guardado.start(1000)  # 1 segundo de delay
            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error agendando guardado: {e}")

    def _ejecutar_guardado_agrupado(self):
        """Ejecutar guardado agrupado de todos los campos pendientes"""
        if self.cargando_datos or not self.campos_pendientes:
            return

        try:
            # Verificar dependencias
            if not self._verificar_dependencias():
                self.campos_pendientes.clear()
                return

            contrato = self.contract_manager.get_current_contract()
            if not contrato:
                self.campos_pendientes.clear()
                return

            # Procesar todos los campos pendientes de una vez
            guardados_exitosos = 0
            
            for nombre_campo, widget, valor in self.campos_pendientes:
                try:
                    exito = self._guardar_campo_obra(nombre_campo, valor, widget)
                    
                    if exito:
                        # Actualizar cache con clave mejorada
                        cache_key = f"{contrato}_{nombre_campo}"
                        self.ultimo_guardado[cache_key] = valor
                        guardados_exitosos += 1
                        
                except Exception as e:
                    print(f"[ControladorAutoGuardado] ❌ Error guardando {nombre_campo}: {e}")


            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error en guardado agrupado: {e}")
        finally:
            self.campos_pendientes.clear()



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
        """Configurar auto-guardado para tablas específicas - OPTIMIZADO"""
        try:
            tablas_configuradas = 0
            
            # Configurar tabla de empresas con delay
            if hasattr(self.main_window, 'TwEmpresas'):
                self._configurar_tabla_con_delay('TwEmpresas', self._auto_guardar_tabla_empresas)
                tablas_configuradas += 1
            
            # Configurar tabla de ofertas con delay
            if hasattr(self.main_window, 'TwOfertas'):
                self._configurar_tabla_con_delay('TwOfertas', self._auto_guardar_tabla_ofertas)
                tablas_configuradas += 1
            

            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error configurando tablas: {e}")

    def _configurar_tabla_con_delay(self, nombre_tabla, callback):
        """Configurar tabla con delay para evitar guardados excesivos"""
        tabla = getattr(self.main_window, nombre_tabla)
        
        # Timer específico para esta tabla
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        
        def on_item_changed(item):
            if not self.cargando_datos:
                timer.stop()
                timer.start(2000)  # 2 segundos de delay para tablas
        
        tabla.itemChanged.connect(on_item_changed)
        setattr(tabla, '_autosave_timer', timer)


    def _guardar_campo_inmediato(self, nombre_campo: str, widget) -> bool:
        """Guardar campo inmediatamente al perder foco"""
        try:
            if not self._verificar_dependencias():
                return False

            # OBTENER CONTRATO ACTUAL SIEMPRE FRESCO
            contrato = self.contract_manager.get_current_contract()
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
            print(f"[ControladorAutoGuardado] ❌ Error guardando inmediato: {e}")
            return False
    
    def _guardar_campo_obra(self, nombre_campo: str, valor: str, widget) -> bool:
        """Guardar campo en obra individual - OPTIMIZADO"""
        try:
            if not self._verificar_dependencias():
                return False

            # OBTENER CONTRATO ACTUAL SIEMPRE FRESCO
            contrato = self.contract_manager.get_current_contract()
            if not contrato:
                return False

            # SIMPLIFICACION: Usar solo el método básico para todos
            resultado = self.controlador_json.guardar_campo_en_json(contrato, nombre_campo, valor)
            
            return resultado
                
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error guardando campo obra: {e}")
            return False

    def _auto_guardar_tabla_empresas(self):
        """MODIFICADA: Guardar estructura unificada"""
        if self.cargando_datos:
            return
            
        try:
            if not self._verificar_dependencias():
                return

            contrato = self.contract_manager.get_current_contract()
            if not contrato:
                return
            
            # Extraer datos unificados
            empresas_data = self._extraer_datos_tabla_empresas()
            
            # Verificar cambios reales
            cache_key = "empresas_unificadas"
            if cache_key in self.ultimo_guardado and self.ultimo_guardado[cache_key] == empresas_data:
                return  # Sin cambios

            # ✅ GUARDAR ESTRUCTURA UNIFICADA
            if self.controlador_json.guardar_empresas_unificadas_en_json(contrato, empresas_data):
                self.ultimo_guardado[cache_key] = empresas_data
            
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error guardando empresas unificadas: {e}")

    def _auto_guardar_tabla_ofertas(self):
        """MODIFICADA: Las ofertas se guardan junto con empresas"""
        # ✅ NO HACER NADA - Las ofertas se guardan en _auto_guardar_tabla_empresas
        pass

    def forzar_guardado_completo(self):
        """Forzar guardado completo - OPTIMIZADO"""
        try:
            if self.guardando_en_proceso or self.cargando_datos:
                return False
            
            self.guardando_en_proceso = True
            
            # 🆕 EJECUTAR GUARDADO AGRUPADO PENDIENTE PRIMERO
            if self.campos_pendientes:
                self.timer_guardado.stop()
                self._ejecutar_guardado_agrupado()
            
            # Solo guardar tablas (los campos ya se guardaron en tiempo real)
            self._forzar_guardado_tablas()
            return True
           
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error en guardado forzado: {e}")
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
            print(f"[ControladorAutoGuardado] ❌ Error extrayendo empresas unificadas: {e}")
        
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
            print(f"[ControladorAutoGuardado] ❌ Error extrayendo datos tabla ofertas: {e}")
        
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
            print(f"[ControladorAutoGuardado] ❌ Error guardado forzado tablas: {e}")

    def esta_pausado(self) -> bool:
        """Verificar si el auto-guardado está pausado"""
        return self.cargando_datos
    def _obtener_nombre_contrato_actual(self) -> str:
        """Obtener nombre del contrato usando el selector"""
        try:
            if (hasattr(self.main_window, 'contract_manager') and 
                self.main_window.contract_manager):
                # USAR EL MÉTODO CORRECTO
                return self.main_window.contract_manager.get_current_contract() or ""
            return ""
        except Exception as e:
            print(f"[ControladorAutoGuardado] ❌ Error obteniendo nombre contrato: {e}")
            return ""
    def guardar_tabla_ofertas_en_json(self):
        """Guardar tabla TwOfertas en la estructura empresas unificada"""
        try:
            if not hasattr(self.main_window, 'TwOfertas'):
                return

            tabla = self.main_window.TwOfertas
            
            # Obtener nombre del contrato activo
            nombre_contrato = self._obtener_nombre_contrato_actual()
            if not nombre_contrato:
                print("[AutoGuardado] ❌ No se pudo guardar ofertas: contrato no definido")
                return

            # Obtener datos actuales del contrato
            contract_data = self.controlador_json.leer_contrato_completo(nombre_contrato)
            if not contract_data:
                print("[AutoGuardado] ❌ No se encontró el contrato")
                return

            # Obtener empresas actuales
            empresas_actuales = contract_data.get('empresas', [])
            if not empresas_actuales:
                print("[AutoGuardado] ❌ No hay empresas en el contrato")
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
            print(f"[ControladorAutoGuardado] ❌ Error guardando ofertas en empresas: {e}")