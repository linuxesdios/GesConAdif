#!/usr/bin/env python3
"""
Controlador de Fases de Documentos para ADIF
Maneja el seguimiento automático de las fases del proyecto y actualización de fechas
"""
import os
import json
import logging
from datetime import datetime

from typing import Dict, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class FaseDocumento(Enum):
    """Enum para las fases de documentos"""
    CREACION = "creacion"
    INICIO = "inicio"
    CARTASINVITACION = "cartas_invitacion"
    ADJUDICACION = "adjudicacion"
    CARTASADJUDICACION = "cartas_adjudicacion"
    FIRMA_CONTRATO = "firma_contrato"
    REPLANTEO = "replanteo"
    ACTUACION = "actuacion"
    RECEPCION = "recepcion"
    FINALIZACION = "finalizacion"

class ControladorFasesDocumentos:
    """Controlador para gestionar las fases de documentos del proyecto"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.fases_config = {
            FaseDocumento.CREACION: {
                "nombre": "📋 Creación Proyecto",
                "generado_field": "dateEdit_gen_creacion", 
                "firmado_field": "dateEdit_fir_creacion",
                "auto_generado": True,  # Se marca automáticamente al crear proyecto
                "documentos_relacionados": ["proyecto","pliego","Proyecto","Pliego"]
            },
            FaseDocumento.INICIO: {
                "nombre": "🚀 Inicio",
                "generado_field": "dateEdit_gen_inicio",
                "firmado_field": "dateEdit_fir_inicio", 
                "auto_generado": True,
                "documentos_relacionados": ["acta_inicio"]
            },
            FaseDocumento.CARTASINVITACION: {
                "nombre": "📧 Cartas Invitación",
                "generado_field": "dateEdit_gen_cartas_invitacion",
                "firmado_field": "dateEdit_fir_cartas_invitacion",
                "auto_generado": True,
                "documentos_relacionados": ["invitacion", "cartas_invitacion", "carta_invitacion"]
            },
            FaseDocumento.ADJUDICACION: {
                "nombre": "🏆 Adjudicación", 
                "generado_field": "dateEdit_gen_adjudicacion",
                "firmado_field": "dateEdit_fir_adjudicacion",
                "auto_generado": True,
                "documentos_relacionados": ["adjudicacion"]
            },
            FaseDocumento.CARTASADJUDICACION: {
                "nombre": "📧 Cartas Adjudicación",
                "generado_field": "dateEdit_gen_cartas_adjudicacion",
                "firmado_field": "dateEdit_fir_cartas_adjudicacion",
                "auto_generado": True,
                "documentos_relacionados": ["carta_adjudicacion", "cartas_adjudicacion"]
            },
            FaseDocumento.FIRMA_CONTRATO: {
                "nombre": "✍️ Firma Contrato",
                "generado_field": "dateEdit_gen_firma_contrato",
                "firmado_field": "dateEdit_fir_firma_contrato",
                "auto_generado": True,
                "documentos_relacionados": ["contrato", "firma_contrato"]
            },
            FaseDocumento.REPLANTEO: {
                "nombre": "📐 Replanteo",
                "generado_field": "dateEdit_gen_replanteo", 
                "firmado_field": "dateEdit_fir_replanteo",
                "auto_generado": True,
                "documentos_relacionados": ["acta_replanteo"]
            },
            FaseDocumento.ACTUACION: {
                "nombre": "⚡ Actuación",
                "generado_field": "dateEdit_gen_actuacion",
                "firmado_field": "dateEdit_fir_actuacion",
                "auto_generado": True,
                "documentos_relacionados": ["actuacion", "ejecucion"]
            },
            FaseDocumento.RECEPCION: {
                "nombre": "✅ Recepción",
                "generado_field": "dateEdit_gen_recepcion",
                "firmado_field": "dateEdit_fir_recepcion", 
                "auto_generado": True,
                "documentos_relacionados": ["acta_recepcion"]
            },
            FaseDocumento.FINALIZACION: {
                "nombre": "🏁 Finalización",
                "generado_field": "dateEdit_gen_finalizacion",
                "firmado_field": "dateEdit_fir_finalizacion",
                "auto_generado": True,
                "documentos_relacionados": ["acta_finalizacion", "liquidacion"]
            }
        }
        
        logger.info("[ControladorFases] ✅ Inicializado con 11 fases configuradas")
    
    def forzar_actualizar_cartas_invitacion(self, nombre_contrato: str):
        """Forzar la actualización de la fase de cartas invitación si se detecta que se generaron"""
        try:
            logger.info(f"[ControladorFases] 🔧 Forzando actualización de cartas invitación para {nombre_contrato}")
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            self._actualizar_fecha_generado(nombre_contrato, FaseDocumento.CARTASINVITACION, fecha_actual)
            logger.info(f"[ControladorFases] ✅ Cartas invitación marcadas como generadas: {fecha_actual}")
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error forzando actualización de cartas invitación: {e}")
    
    def forzar_actualizar_cartas_adjudicacion(self, nombre_contrato: str):
        """Forzar la actualización de la fase de cartas adjudicación si se detecta que se generaron"""
        try:
            logger.info(f"[ControladorFases] 🔧 Forzando actualización de cartas adjudicación para {nombre_contrato}")
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            self._actualizar_fecha_generado(nombre_contrato, FaseDocumento.CARTASADJUDICACION, fecha_actual)
            logger.info(f"[ControladorFases] ✅ Cartas adjudicación marcadas como generadas: {fecha_actual}")
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error forzando actualización de cartas adjudicación: {e}")
    
    def conectar_campos_ui(self):
        """Conectar los campos de fecha de la UI"""
        if not self.main_window:
            logger.warning("[ControladorFases] ⚠️ No hay ventana principal para conectar")
            return
        
        try:
            from PyQt5.QtWidgets import QDateEdit
            from PyQt5.QtCore import QDate
            
            # Conectar todos los campos de firmado (manuales)
            campos_conectados = 0
            for fase, config in self.fases_config.items():
                firmado_field = config["firmado_field"]
                widget = self.main_window.findChild(QDateEdit, firmado_field)
                if widget:
                    # Conectar señal de cambio para guardar automáticamente
                    widget.dateChanged.connect(lambda date, f=fase: self._on_fecha_firmado_cambiada(f, date))
                    campos_conectados += 1
                    
            logger.info(f"[ControladorFases] ✅ {campos_conectados} campos de firmado conectados")
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error conectando campos: {e}")
    
    def cargar_fases_desde_json(self, nombre_contrato: str):
        """Cargar las fases desde el JSON y actualizar la UI"""
        try:
            # Obtener datos del contrato
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                logger.warning(f"[ControladorFases] ⚠️ No se encontraron datos para {nombre_contrato}")
                return
                
            # 🆕 INICIALIZAR estructura de fases si no existe
            if "fases_documentos" not in datos_contrato:
                logger.info(f"[ControladorFases] 🆕 Inicializando estructura de fases para {nombre_contrato}")
                datos_contrato["fases_documentos"] = {}
                # Inicializar todas las fases vacías
                for fase in FaseDocumento:
                    datos_contrato["fases_documentos"][fase.value] = {
                        "generado": None,
                        "firmado": None
                    }
                # Guardar la estructura inicializada
                self._guardar_datos_contrato(nombre_contrato, datos_contrato)
                logger.info(f"[ControladorFases] ✅ Estructura de fases inicializada y guardada")
            
            # Obtener fases_documentos del JSON
            fases_datos = datos_contrato.get("fases_documentos", {})
            
            # Actualizar campos en la UI
            self._actualizar_campos_ui(fases_datos)
            
            logger.info(f"[ControladorFases] ✅ Fases cargadas para {nombre_contrato}")
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error cargando fases: {e}")
    
    def marcar_documento_generado(self, tipo_documento: str, nombre_contrato: str = None):
        """Marcar un documento como generado automáticamente"""
        try:
            logger.info(f"[ControladorFases] 📥 Recibiendo notificación: {tipo_documento} para contrato: {nombre_contrato}")
            
            if not nombre_contrato and self.main_window:
                # Intentar obtener el contrato actual
                if hasattr(self.main_window, 'comboBox'):
                    nombre_contrato = self.main_window.comboBox.currentText()
                    logger.debug(f"[ControladorFases] 🔍 Contrato obtenido desde comboBox: {nombre_contrato}")
            
            if not nombre_contrato:
                logger.warning("[ControladorFases] ⚠️ No se pudo determinar el contrato actual")
                return
            
            # Encontrar la fase correspondiente al tipo de documento
            fase_encontrada = None
            logger.debug(f"[ControladorFases] 🔍 Buscando fase para documento: {tipo_documento}")
            
            # Obtener el valor correcto del tipo de documento
            if hasattr(tipo_documento, 'value'):
                documento_valor = tipo_documento.value
            else:
                documento_valor = str(tipo_documento)
            
            logger.debug(f"[ControladorFases] 🔍 Valor del documento: {documento_valor}")
            
            for fase, config in self.fases_config.items():
                logger.debug(f"[ControladorFases] 🔍 Verificando fase {fase.value}: {config['documentos_relacionados']}")
                if documento_valor.lower() in config["documentos_relacionados"]:
                    fase_encontrada = fase
                    logger.info(f"[ControladorFases] ✅ Fase encontrada: {fase.value}")
                    break
            
            if not fase_encontrada:
                logger.warning(f"[ControladorFases] ⚠️ No se encontró fase para documento: {tipo_documento}")
                logger.warning(f"[ControladorFases] 📋 Fases disponibles:")
                for fase, config in self.fases_config.items():
                    logger.warning(f"[ControladorFases]    {fase.value}: {config['documentos_relacionados']}")
                return
            
            # Marcar como generado
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            logger.info(f"[ControladorFases] 💾 Marcando documento como generado: {fecha_actual}")
            self._actualizar_fecha_generado(nombre_contrato, fase_encontrada, fecha_actual)
            
            logger.info(f"[ControladorFases] ✅ Documento {tipo_documento} marcado como generado en fase {fase_encontrada.value}")
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error marcando documento: {e}")
            import traceback
            traceback.print_exc()
    
    def marcar_creacion_proyecto(self, nombre_contrato: str):
        """Marcar la fase de creación del proyecto"""
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            self._actualizar_fecha_generado(nombre_contrato, FaseDocumento.CREACION, fecha_actual)
            logger.info(f"[ControladorFases] ✅ Proyecto {nombre_contrato} marcado como creado")
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error marcando creación: {e}")
    
    def obtener_resumen_progreso(self, nombre_contrato: str) -> Dict:
        """Obtener resumen del progreso del proyecto"""
        try:
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                return {"generados": 0, "firmados": 0, "total": 11, "proxima_fase": None}
            
            fases_datos = datos_contrato.get("fases_documentos", {})
            
            generados = 0
            firmados = 0
            proxima_fase = None
            
            for fase in FaseDocumento:
                fase_data = fases_datos.get(fase.value, {})
                
                if fase_data.get("generado"):
                    generados += 1
                else:
                    if not proxima_fase:
                        proxima_fase = self.fases_config[fase]["nombre"]
                
                if fase_data.get("firmado"):
                    firmados += 1
            
            return {
                "generados": generados,
                "firmados": firmados, 
                "total": len(FaseDocumento),
                "proxima_fase": proxima_fase,
                "porcentaje_generados": round((generados / len(FaseDocumento)) * 100),
                "porcentaje_firmados": round((firmados / len(FaseDocumento)) * 100)
            }
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error obteniendo resumen: {e}")
            return {"generados": 0, "firmados": 0, "total": 11, "proxima_fase": None}
    
    def obtener_historial_actividad(self, nombre_contrato: str, limite: int = 10) -> List[Dict]:
        """Obtener historial de actividad de las fases"""
        try:
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                return []
            
            fases_datos = datos_contrato.get("fases_documentos", {})
            actividades = []
            
            for fase in FaseDocumento:
                fase_data = fases_datos.get(fase.value, {})
                nombre_fase = self.fases_config[fase]["nombre"]
                
                # Agregar actividad de generado
                if fase_data.get("generado"):
                    actividades.append({
                        "fecha": fase_data["generado"],
                        "tipo": "generado",
                        "descripcion": f"📅 Documento \"{nombre_fase}\" generado",
                        "fase": fase.value
                    })
                
                # Agregar actividad de firmado  
                if fase_data.get("firmado"):
                    actividades.append({
                        "fecha": fase_data["firmado"],
                        "tipo": "firmado", 
                        "descripcion": f"✍️ Documento \"{nombre_fase}\" firmado",
                        "fase": fase.value
                    })
            
            # Ordenar por fecha descendente
            actividades.sort(key=lambda x: x["fecha"], reverse=True)
            
            return actividades[:limite]
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error obteniendo historial: {e}")
            return []
    
    def _actualizar_fecha_generado(self, nombre_contrato: str, fase: FaseDocumento, fecha: str):
        """Actualizar fecha de generado en JSON y UI"""
        try:
            # Actualizar JSON PRIMERO
            self._actualizar_json(nombre_contrato, fase.value, "generado", fecha)
            
            # Actualizar UI SIN TRIGGERAR AUTO-GUARDADO
            if self.main_window:
                from PyQt5.QtWidgets import QDateEdit
                from PyQt5.QtCore import QDate
                
                field_name = self.fases_config[fase]["generado_field"]
                widget = self.main_window.findChild(QDateEdit, field_name)
                if widget:
                    # 🚫 BLOQUEAR señales para evitar auto-guardado
                    widget.blockSignals(True)
                    fecha_qt = QDate.fromString(fecha, "yyyy-MM-dd")
                    widget.setDate(fecha_qt)
                    # ✅ REACTIVAR señales
                    widget.blockSignals(False)
                    logger.debug(f"[ControladorFases] 🎯 UI actualizada para {field_name}: {fecha}")
                    
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error actualizando fecha generado: {e}")
    
    def _on_fecha_firmado_cambiada(self, fase: FaseDocumento, fecha):
        """Callback cuando cambia una fecha de firmado"""
        try:
            if not self.main_window or not hasattr(self.main_window, 'comboBox'):
                return
                
            nombre_contrato = self.main_window.comboBox.currentText()
            if not nombre_contrato:
                return
            
            fecha_str = fecha.toString("yyyy-MM-dd")
            self._actualizar_json(nombre_contrato, fase.value, "firmado", fecha_str)
            
            logger.info(f"[ControladorFases] ✅ Fecha firmado actualizada: {fase.value} -> {fecha_str}")
            
        except Exception as e:
            logger.error(f"[ControladorFases] ❌ Error actualizando fecha firmado: {e}")
    
    def _actualizar_campos_ui(self, fases_datos: Dict):
        """Actualizar todos los campos de la UI con datos del JSON"""
        if not self.main_window:
            return
            
        try:
            from PyQt5.QtWidgets import QDateEdit
            from PyQt5.QtCore import QDate
            
            for fase, config in self.fases_config.items():
                fase_data = fases_datos.get(fase.value, {})
                
                # Actualizar campo generado SIN TRIGGERAR AUTO-GUARDADO
                gen_field = config["generado_field"] 
                gen_widget = self.main_window.findChild(QDateEdit, gen_field)
                if gen_widget and fase_data.get("generado"):
                    gen_widget.blockSignals(True)
                    fecha_gen = QDate.fromString(fase_data["generado"], "yyyy-MM-dd")
                    gen_widget.setDate(fecha_gen)
                    gen_widget.blockSignals(False)
                
                # Actualizar campo firmado SIN TRIGGERAR AUTO-GUARDADO
                fir_field = config["firmado_field"]
                fir_widget = self.main_window.findChild(QDateEdit, fir_field)
                if fir_widget and fase_data.get("firmado"):
                    fir_widget.blockSignals(True)
                    fecha_fir = QDate.fromString(fase_data["firmado"], "yyyy-MM-dd")
                    fir_widget.setDate(fecha_fir)
                    fir_widget.blockSignals(False)
                    
        except Exception as e:
            print(f"[ControladorFases] ❌ Error actualizando campos UI: {e}")
    
    def _actualizar_json(self, nombre_contrato: str, fase: str, tipo: str, fecha: str):
        """Actualizar el JSON con una nueva fecha"""
        try:
            # Obtener datos actuales
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                print(f"[ControladorFases] ⚠️ No se encontró contrato: {nombre_contrato}")
                return
            
            # Inicializar fases_documentos si no existe
            if "fases_documentos" not in datos_contrato:
                datos_contrato["fases_documentos"] = {}
            
            # Inicializar fase si no existe
            if fase not in datos_contrato["fases_documentos"]:
                datos_contrato["fases_documentos"][fase] = {"generado": None, "firmado": None}
            
            # Actualizar fecha - usar el mismo nombre que el campo UI
            datos_contrato["fases_documentos"][fase][tipo] = fecha
            
            # Guardar de vuelta al JSON
            self._guardar_datos_contrato(nombre_contrato, datos_contrato)
            print(f"[ControladorFases] 💾 JSON actualizado: {fase}.{tipo} = {fecha}")
            
        except Exception as e:
            print(f"[ControladorFases] ❌ Error actualizando JSON: {e}")
    
    def reparar_sincronizacion_fases(self, nombre_contrato: str):
        """Función de reparación para sincronizar fases faltantes de UI a JSON"""
        try:
            print(f"[ControladorFases] 🔧 REPARANDO sincronización para {nombre_contrato}")
            
            # Obtener datos del contrato
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                print(f"[ControladorFases] ❌ No se pudo obtener el contrato para reparar")
                return
            
            # Inicializar estructura si no existe
            if "fases_documentos" not in datos_contrato:
                datos_contrato["fases_documentos"] = {}
                print(f"[ControladorFases] 🆕 Creando estructura fases_documentos")
            
            # Verificar todas las fases y corregir
            if not self.main_window:
                return
                
            from PyQt5.QtWidgets import QDateEdit
            from PyQt5.QtCore import QDate
            
            reparaciones = 0
            
            for fase, config in self.fases_config.items():
                # Inicializar fase si no existe
                if fase.value not in datos_contrato["fases_documentos"]:
                    datos_contrato["fases_documentos"][fase.value] = {"generado": None, "firmado": None}
                    print(f"[ControladorFases] 🆕 Creando estructura para fase {fase.value}")
                
                fase_data = datos_contrato["fases_documentos"][fase.value]
                
                # Verificar campo generado
                gen_field = config["generado_field"]
                gen_widget = self.main_window.findChild(QDateEdit, gen_field)
                if gen_widget:
                    fecha_gen_ui = gen_widget.date().toString("yyyy-MM-dd")
                    fecha_gen_json = fase_data.get("generado")
                    
                    # Si la UI tiene una fecha válida pero JSON no
                    if fecha_gen_ui != "2000-01-01" and not fecha_gen_json:
                        fase_data["generado"] = fecha_gen_ui
                        print(f"[ControladorFases] 🔧 REPARADO {fase.value}.generado: {fecha_gen_ui}")
                        reparaciones += 1
                    # Si JSON tiene fecha pero UI no
                    elif fecha_gen_json and fecha_gen_ui == "2000-01-01":
                        gen_widget.blockSignals(True)
                        fecha_qt = QDate.fromString(fecha_gen_json, "yyyy-MM-dd")
                        gen_widget.setDate(fecha_qt)
                        gen_widget.blockSignals(False)
                        print(f"[ControladorFases] 🔧 REPARADO UI {gen_field}: {fecha_gen_json}")
                        reparaciones += 1
                
                # Verificar campo firmado
                fir_field = config["firmado_field"]
                fir_widget = self.main_window.findChild(QDateEdit, fir_field)
                if fir_widget:
                    fecha_fir_ui = fir_widget.date().toString("yyyy-MM-dd")
                    fecha_fir_json = fase_data.get("firmado")
                    
                    # Si la UI tiene una fecha válida pero JSON no
                    if fecha_fir_ui != "2000-01-01" and not fecha_fir_json:
                        fase_data["firmado"] = fecha_fir_ui
                        print(f"[ControladorFases] 🔧 REPARADO {fase.value}.firmado: {fecha_fir_ui}")
                        reparaciones += 1
                    # Si JSON tiene fecha pero UI no
                    elif fecha_fir_json and fecha_fir_ui == "2000-01-01":
                        fir_widget.blockSignals(True)
                        fecha_qt = QDate.fromString(fecha_fir_json, "yyyy-MM-dd")
                        fir_widget.setDate(fecha_qt)
                        fir_widget.blockSignals(False)
                        print(f"[ControladorFases] 🔧 REPARADO UI {fir_field}: {fecha_fir_json}")
                        reparaciones += 1
            
            # Guardar si hubo reparaciones
            if reparaciones > 0:
                self._guardar_datos_contrato(nombre_contrato, datos_contrato)
                print(f"[ControladorFases] ✅ REPARACIÓN COMPLETA: {reparaciones} correcciones")
            else:
                print(f"[ControladorFases] ✅ No se necesitaron reparaciones")
                
        except Exception as e:
            print(f"[ControladorFases] ❌ Error en reparación: {e}")
            import traceback
            traceback.print_exc()
    
    def sincronizar_todas_fechas_a_json(self, nombre_contrato: str):
        """Sincronizar todas las fechas de la UI al JSON (útil para botón actualizar)"""
        try:
            if not self.main_window:
                return
                
            from PyQt5.QtWidgets import QDateEdit
            from PyQt5.QtCore import QDate
            
            print(f"[ControladorFases] 🔄 Sincronizando todas las fechas al JSON para {nombre_contrato}")
            
            # Obtener datos del contrato
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                return
            
            # Inicializar estructura si no existe
            if "fases_documentos" not in datos_contrato:
                datos_contrato["fases_documentos"] = {}
            
            campos_sincronizados = 0
            
            for fase, config in self.fases_config.items():
                # Inicializar fase si no existe
                if fase.value not in datos_contrato["fases_documentos"]:
                    datos_contrato["fases_documentos"][fase.value] = {"generado": None, "firmado": None}
                
                # Sincronizar campo generado
                gen_field = config["generado_field"]
                gen_widget = self.main_window.findChild(QDateEdit, gen_field)
                if gen_widget:
                    fecha_gen = gen_widget.date().toString("yyyy-MM-dd")
                    # Solo actualizar si no es la fecha por defecto (2000-01-01)
                    if fecha_gen != "2000-01-01":
                        datos_contrato["fases_documentos"][fase.value]["generado"] = fecha_gen
                        campos_sincronizados += 1
                        print(f"[ControladorFases] ✅ Sincronizado {gen_field}: {fecha_gen}")
                
                # Sincronizar campo firmado
                fir_field = config["firmado_field"]
                fir_widget = self.main_window.findChild(QDateEdit, fir_field)
                if fir_widget:
                    fecha_fir = fir_widget.date().toString("yyyy-MM-dd")
                    # Solo actualizar si no es la fecha por defecto (2000-01-01)
                    if fecha_fir != "2000-01-01":
                        datos_contrato["fases_documentos"][fase.value]["firmado"] = fecha_fir
                        campos_sincronizados += 1
                        print(f"[ControladorFases] ✅ Sincronizado {fir_field}: {fecha_fir}")
            
            # Guardar todos los cambios
            self._guardar_datos_contrato(nombre_contrato, datos_contrato)
            print(f"[ControladorFases] 🎯 Sincronización completa: {campos_sincronizados} campos actualizados")
            
        except Exception as e:
            print(f"[ControladorFases] ❌ Error sincronizando fechas: {e}")
    
    def obtener_datos_fases_para_resumen(self, nombre_contrato: str) -> Dict:
        """Obtener datos completos de las fases para el resumen (incluyendo nombres UI)"""
        try:
            datos_contrato = self._obtener_datos_contrato(nombre_contrato)
            if not datos_contrato:
                return {}
            
            fases_datos = datos_contrato.get("fases_documentos", {})
            datos_resumen = {}
            
            for fase, config in self.fases_config.items():
                fase_data = fases_datos.get(fase.value, {})
                
                # Incluir tanto los nombres de los campos UI como los datos
                datos_resumen[fase.value] = {
                    "nombre": config["nombre"],
                    "generado_field": config["generado_field"],
                    "firmado_field": config["firmado_field"],
                    "generado": fase_data.get("generado"),
                    "firmado": fase_data.get("firmado"),
                    "documentos_relacionados": config["documentos_relacionados"]
                }
            
            return datos_resumen
            
        except Exception as e:
            print(f"[ControladorFases] ❌ Error obteniendo datos para resumen: {e}")
            return {}
    
    def _obtener_datos_contrato(self, nombre_contrato: str) -> Optional[Dict]:
        """Obtener datos del contrato desde el JSON"""
        try:
            # Intentar usar el gestor de contratos si está disponible
            if self.main_window and hasattr(self.main_window, 'gestor_contratos'):
                return self.main_window.gestor_contratos.obtener_datos_obra(nombre_contrato)
            
            # Fallback: leer directamente del archivo
            base_datos_path = os.path.join(os.getcwd(), "BaseDatos.json")
            if os.path.exists(base_datos_path):
                with open(base_datos_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                obras = data.get('obras', [])
                for obra in obras:
                    if obra.get('nombreObra') == nombre_contrato:
                        return obra
            
            return None
            
        except Exception as e:
            print(f"[ControladorFases] ❌ Error obteniendo datos: {e}")
            return None
    
    def _guardar_datos_contrato(self, nombre_contrato: str, datos_contrato: Dict):
        """Guardar datos del contrato al JSON usando el gestor unificado"""
        try:
            # SIEMPRE usar el gestor de contratos si está disponible
            if self.main_window and hasattr(self.main_window, 'gestor_contratos'):
                print(f"[ControladorFases] 💾 Guardando usando gestor unificado: {nombre_contrato}")
                
                # Verificar que las fases_documentos están en los datos
                if "fases_documentos" in datos_contrato:
                    print(f"[ControladorFases] 📋 Guardando fases_documentos: {len(datos_contrato['fases_documentos'])} fases")
                    for fase, datos_fase in datos_contrato["fases_documentos"].items():
                        if datos_fase.get("generado") or datos_fase.get("firmado"):
                            print(f"[ControladorFases] 📝 Fase {fase}: gen={datos_fase.get('generado')}, firm={datos_fase.get('firmado')}")
                
                # Actualizar la copia en memoria del gestor
                self.main_window.gestor_contratos.actualizar_obra(nombre_contrato, datos_contrato)
                # Forzar guardado inmediato
                self.main_window.gestor_contratos.guardar_datos()
                print(f"[ControladorFases] ✅ Guardado exitoso via gestor unificado")
                
                # Verificar que se guardó correctamente
                datos_verificacion = self.main_window.gestor_contratos.obtener_datos_obra(nombre_contrato)
                if datos_verificacion and "fases_documentos" in datos_verificacion:
                    print(f"[ControladorFases] ✅ Verificación: {len(datos_verificacion['fases_documentos'])} fases guardadas")
                else:
                    print(f"[ControladorFases] ❌ Verificación falló: datos no encontrados")
                
                return
            
            # Fallback: escribir directamente al archivo (solo si no hay gestor)
            print(f"[ControladorFases] ⚠️ Usando fallback - escribiendo directamente al JSON")
            base_datos_path = os.path.join(os.getcwd(), "BaseDatos.json") 
            if os.path.exists(base_datos_path):
                with open(base_datos_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                obras = data.get('obras', [])
                for i, obra in enumerate(obras):
                    if obra.get('nombreObra') == nombre_contrato:
                        obras[i] = datos_contrato
                        break
                
                with open(base_datos_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print(f"[ControladorFases] ✅ Fallback guardado completado")
                    
        except Exception as e:
            print(f"[ControladorFases] ❌ Error guardando datos: {e}")
            import traceback
            traceback.print_exc()


# Función de integración global
def integrar_controlador_fases(main_window):
    """Integrar el controlador de fases en la aplicación principal"""
    try:
        controlador = ControladorFasesDocumentos(main_window)
        controlador.conectar_campos_ui()
        
        # Hacer referencia en la ventana principal
        main_window.controlador_fases = controlador
        
        # Conectar con el cambio de contrato para cargar datos automáticamente
        if hasattr(main_window, 'comboBox'):
            main_window.comboBox.currentTextChanged.connect(
                lambda texto: controlador.cargar_fases_desde_json(texto) if texto else None
            )
        
        # ✨ CONECTAR CON CONTROLADOR DE DOCUMENTOS para auto-marcar documentos
        if hasattr(main_window, 'controlador_documentos'):
            # Intentar conectar la señal de documento generado
            try:
                # Buscar método de notificación en controlador_documentos
                if hasattr(main_window.controlador_documentos, 'documento_generado'):
                    main_window.controlador_documentos.documento_generado.connect(
                        lambda tipo, nombre, contrato=None: controlador.marcar_documento_generado(tipo, contrato)
                    )
                    print("[ControladorFases] ✅ Conectado con controlador de documentos")
            except Exception as e:
                print(f"[ControladorFases] ⚠️ No se pudo conectar con controlador de documentos: {e}")
        
        print("[ControladorFases] 🎉 Integrado exitosamente en la aplicación")
        return controlador
        
    except Exception as e:
        print(f"[ControladorFases] ❌ Error integrando: {e}")
        return None

def integrar_sistema_completo_fases_resumen(main_window):
    """Integrar el sistema completo de fases y resúmenes"""
    try:
        print("🚀 Integrando sistema completo de fases y resúmenes...")
        
        # 1. Integrar controlador de fases
        controlador_fases = integrar_controlador_fases(main_window)
        
        # 2. Integrar resumen si está disponible
        try:
            from controladores.controlador_resumen import integrar_resumen_completo
            integrador_resumen = integrar_resumen_completo(main_window)
            print("✅ Sistema de resúmenes integrado")
        except ImportError:
            print("⚠️ Módulo de resumen no encontrado - continuando sin resúmenes")
            integrador_resumen = None
        
        # 3. Cargar datos del contrato actual si hay uno seleccionado
        if hasattr(main_window, 'comboBox'):
            contrato_actual = main_window.comboBox.currentText()
            if contrato_actual and controlador_fases:
                print(f"📋 Cargando datos para contrato actual: {contrato_actual}")
                controlador_fases.cargar_fases_desde_json(contrato_actual)
        
        print("🎉 SISTEMA COMPLETO INTEGRADO EXITOSAMENTE")
        print("   ✅ Controlador de fases activo")
        print("   ✅ Sincronización UI ↔ JSON configurada")
        print("   ✅ Auto-marcado de documentos activado")
        if integrador_resumen:
            print("   ✅ Sistema de resúmenes activo")
        
        return {
            'controlador_fases': controlador_fases,
            'integrador_resumen': integrador_resumen
        }
        
    except Exception as e:
        print(f"❌ Error integrando sistema completo: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📋 CONTROLADOR DE FASES DE DOCUMENTOS")
    print("=" * 60)
    print()
    print("🔄 FASES CONFIGURADAS:")
    for fase in FaseDocumento:
        print(f"   {fase.value}")
    print()
    print("📝 PARA USAR:")
    print("   from controladores.controlador_fases_documentos import integrar_controlador_fases")
    print("   controlador = integrar_controlador_fases(self)")
    print()
    print("   # Para marcar documento generado:")
    print("   controlador.marcar_documento_generado('acta_inicio')")
    print("=" * 60)