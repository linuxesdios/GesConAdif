#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diálogo para Actuaciones Especiales - Gestión de JSON y backups
"""
import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QTextEdit, QSplitter, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DialogoActuacionesEspeciales(QDialog):
    """Diálogo para gestionar actuaciones especiales con JSON"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.json_actual = None
        self.datos_json = {}
        self.setup_ui()
        self.cargar_json_actual()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("🔧 Actuaciones Especiales - Gestión JSON")
        self.setGeometry(200, 200, 800, 600)
        self.setModal(True)
        
        # Layout principal
        layout_principal = QVBoxLayout(self)
        
        # Header con información
        self.crear_header(layout_principal)
        
        # Splitter para dividir la vista
        splitter = QSplitter(Qt.Horizontal)
        layout_principal.addWidget(splitter)
        
        # Panel izquierdo - Botones principales
        panel_izquierdo = self.crear_panel_botones()
        splitter.addWidget(panel_izquierdo)
        
        # Panel derecho - Visualización de datos
        panel_derecho = self.crear_panel_visualizacion()
        splitter.addWidget(panel_derecho)
        
        # Establecer proporciones del splitter
        splitter.setSizes([300, 500])
        
        # Botón cerrar
        layout_botones_inferior = QHBoxLayout()
        btn_cerrar = QPushButton("❌ Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout_botones_inferior.addStretch()
        layout_botones_inferior.addWidget(btn_cerrar)
        layout_principal.addLayout(layout_botones_inferior)
    
    def crear_header(self, layout_padre):
        """Crear header con información del estado actual"""
        frame_header = QFrame()
        frame_header.setFrameStyle(QFrame.StyledPanel)
        layout_header = QVBoxLayout(frame_header)
        
        # Título
        titulo = QLabel("🔧 Actuaciones Especiales")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout_header.addWidget(titulo)
        
        # Información del JSON actual
        self.label_json_actual = QLabel("📄 JSON Actual: Cargando...")
        self.label_json_actual.setStyleSheet("color: #666; font-size: 10pt;")
        layout_header.addWidget(self.label_json_actual)
        
        layout_padre.addWidget(frame_header)
    
    def crear_panel_botones(self):
        """Crear panel con los tres botones principales"""
        frame_botones = QFrame()
        frame_botones.setFrameStyle(QFrame.StyledPanel)
        layout_botones = QVBoxLayout(frame_botones)
        
        # Título del panel
        titulo_panel = QLabel("📋 Opciones Disponibles")
        titulo_panel.setFont(QFont("Arial", 12, QFont.Bold))
        layout_botones.addWidget(titulo_panel)
        
        # Botón 1: Mostrar todas las actuaciones
        btn_mostrar_actuaciones = QPushButton("📊 Mostrar Todas las Actuaciones")
        btn_mostrar_actuaciones.setMinimumHeight(40)
        btn_mostrar_actuaciones.setToolTip("Ver todas las actuaciones registradas en el JSON actual")
        btn_mostrar_actuaciones.clicked.connect(self.mostrar_todas_actuaciones)
        layout_botones.addWidget(btn_mostrar_actuaciones)
        
        # Botón 2: Abrir JSON diferente
        btn_abrir_json = QPushButton("📂 Abrir JSON Diferente")
        btn_abrir_json.setMinimumHeight(40)
        btn_abrir_json.setToolTip("Seleccionar y abrir un archivo JSON diferente")
        btn_abrir_json.clicked.connect(self.abrir_json_diferente)
        layout_botones.addWidget(btn_abrir_json)
        
        # Botón 3: Seleccionar backup
        btn_seleccionar_backup = QPushButton("🔄 Seleccionar Backup")
        btn_seleccionar_backup.setMinimumHeight(40)
        btn_seleccionar_backup.setToolTip("Seleccionar un archivo de backup para cargar")
        btn_seleccionar_backup.clicked.connect(self.seleccionar_backup)
        layout_botones.addWidget(btn_seleccionar_backup)
        
        # Lista de backups disponibles
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("📁 Backups Disponibles:"))
        
        # Botón refrescar backups
        btn_refrescar = QPushButton("🔄")
        btn_refrescar.setMaximumSize(25, 25)
        btn_refrescar.setToolTip("Refrescar lista de backups")
        btn_refrescar.clicked.connect(self.refrescar_backups)
        label_layout.addWidget(btn_refrescar)
        label_layout.addStretch()
        
        layout_botones.addLayout(label_layout)
        
        self.lista_backups = QListWidget()
        self.lista_backups.setMaximumHeight(200)
        self.lista_backups.itemDoubleClicked.connect(self.cargar_backup_seleccionado)
        layout_botones.addWidget(self.lista_backups)
        
        layout_botones.addStretch()
        return frame_botones
    
    def crear_panel_visualizacion(self):
        """Crear panel para visualizar datos JSON"""
        frame_visualizacion = QFrame()
        frame_visualizacion.setFrameStyle(QFrame.StyledPanel)
        layout_visualizacion = QVBoxLayout(frame_visualizacion)
        
        # Título del panel
        self.titulo_visualizacion = QLabel("📄 Contenido JSON")
        self.titulo_visualizacion.setFont(QFont("Arial", 12, QFont.Bold))
        layout_visualizacion.addWidget(self.titulo_visualizacion)
        
        # Área de texto para mostrar JSON
        self.area_contenido = QTextEdit()
        self.area_contenido.setFont(QFont("Consolas", 10))
        self.area_contenido.setPlainText("Seleccione una opción para ver el contenido...")
        layout_visualizacion.addWidget(self.area_contenido)
        
        return frame_visualizacion
    
    def cargar_json_actual(self):
        """Cargar el JSON actual desde el controlador principal"""
        try:
            if hasattr(self.parent, 'controlador_json') and self.parent.controlador_json:
                # Obtener ruta del archivo JSON actual
                ruta_json = self.parent.controlador_json.ruta_archivo
                
                if ruta_json and os.path.exists(ruta_json):
                    self.json_actual = ruta_json
                    
                    # Cargar datos
                    with open(ruta_json, 'r', encoding='utf-8') as f:
                        self.datos_json = json.load(f)
                    
                    # Actualizar interfaz
                    nombre_archivo = os.path.basename(ruta_json)
                    self.label_json_actual.setText(f"📄 JSON Actual: {nombre_archivo}")
                    
                    # Cargar lista de backups
                    self.cargar_lista_backups()
                    
                else:
                    self.label_json_actual.setText("⚠️ JSON Actual: No encontrado")
            else:
                self.label_json_actual.setText("❌ Controlador JSON no disponible")
                
        except Exception as e:
            logger.error(f"Error cargando JSON actual: {e}")
            self.label_json_actual.setText("❌ Error cargando JSON actual")
    
    def cargar_lista_backups(self):
        """Cargar lista de archivos de backup disponibles"""
        try:
            if not self.json_actual:
                return
            
            # Buscar backups en el mismo directorio
            directorio = os.path.dirname(self.json_actual)
            patron_backup = os.path.join(directorio, "BaseDatos*.json")
            archivos_backup = glob.glob(patron_backup)
            
            # Filtrar el archivo actual
            nombre_actual = os.path.basename(self.json_actual)
            backups_filtrados = [f for f in archivos_backup 
                               if os.path.basename(f) != nombre_actual]
            
            # Ordenar por fecha de modificación (más reciente primero)
            backups_filtrados.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Limpiar lista y agregar backups
            self.lista_backups.clear()
            
            for backup_path in backups_filtrados:
                try:
                    nombre_archivo = os.path.basename(backup_path)
                    fecha_mod = datetime.fromtimestamp(os.path.getmtime(backup_path))
                    tamaño_kb = os.path.getsize(backup_path) / 1024
                    
                    texto_item = f"{nombre_archivo}\n📅 {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')} ({tamaño_kb:.1f} KB)"
                    
                    item = QListWidgetItem(texto_item)
                    item.setData(Qt.UserRole, backup_path)  # Guardar ruta completa
                    item.setToolTip(f"Ruta: {backup_path}")
                    
                    self.lista_backups.addItem(item)
                    
                except Exception as e:
                    logger.error(f"Error procesando backup {backup_path}: {e}")
            
            logger.info(f"Cargados {self.lista_backups.count()} backups")
            
        except Exception as e:
            logger.error(f"Error cargando backups: {e}")
    
    def refrescar_backups(self):
        """Refrescar manualmente la lista de backups"""
        try:
            logger.debug("Refrescando lista de backups manualmente...")
            self.cargar_lista_backups()
            
            # Mostrar mensaje temporal de confirmación
            count = self.lista_backups.count()
            mensaje_temp = f"🔄 Lista refrescada: {count} backup{'s' if count != 1 else ''} encontrado{'s' if count != 1 else ''}"
            
            # Actualizar temporalmente el área de contenido si está vacía o con mensaje por defecto
            contenido_actual = self.area_contenido.toPlainText()
            if "Seleccione una opción" in contenido_actual or not contenido_actual.strip():
                self.area_contenido.setPlainText(f"{contenido_actual}\n\n{mensaje_temp}")
            
        except Exception as e:
            logger.error(f"Error refrescando backups: {e}")
            QMessageBox.critical(self, "Error", f"Error refrescando backups: {e}")
    
    def mostrar_todas_actuaciones(self):
        """Botón 1: Mostrar todas las actuaciones del JSON actual"""
        try:
            if not self.datos_json:
                QMessageBox.warning(self, "Sin Datos", "No hay datos JSON cargados")
                return
            
            # Extraer información de actuaciones
            actuaciones_info = self.extraer_actuaciones(self.datos_json)
            
            # Mostrar en el área de contenido
            self.titulo_visualizacion.setText("📊 Todas las Actuaciones Encontradas")
            self.area_contenido.setPlainText(actuaciones_info)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando actuaciones: {e}")
    
    def extraer_actuaciones(self, datos_json: Dict[str, Any]) -> str:
        """Extraer y formatear información de actuaciones del JSON"""
        try:
            resultado = []
            resultado.append("=" * 60)
            resultado.append("🔍 ANÁLISIS DE ACTUACIONES EN JSON")
            resultado.append("=" * 60)
            resultado.append("")
            
            # Información general
            obras = datos_json.get('obras', [])
            firmantes = datos_json.get('firmantes', {})
            
            resultado.append(f"📊 Resumen General:")
            resultado.append(f"   • Total de obras/contratos: {len(obras)}")
            resultado.append(f"   • Firmantes configurados: {len(firmantes)}")
            resultado.append("")
            
            # Análizar cada obra
            if obras:
                resultado.append("📋 OBRAS/CONTRATOS ENCONTRADOS:")
                resultado.append("-" * 40)
                
                for i, obra in enumerate(obras, 1):
                    nombre = obra.get('nombreObra', 'Sin nombre')
                    tipo = obra.get('tipoActuacion', 'Sin especificar')
                    expediente = obra.get('numeroExpediente', 'Sin expediente')
                    
                    resultado.append(f"{i}. {nombre}")
                    resultado.append(f"   📄 Expediente: {expediente}")
                    resultado.append(f"   🏷️  Tipo: {tipo}")
                    
                    # Buscar actuaciones específicas
                    actuaciones_obra = []
                    
                    # Fechas importantes (actuaciones implícitas)
                    fechas_relevantes = {
                        'fechaInicio': 'Inicio de obra',
                        'fechaReplanteo': 'Replanteo',
                        'fechaRecepcion': 'Recepción',
                        'fechaFinalizacion': 'Finalización',
                        'fechaAdjudicacion': 'Adjudicación'
                    }
                    
                    for campo_fecha, descripcion in fechas_relevantes.items():
                        if campo_fecha in obra and obra[campo_fecha]:
                            actuaciones_obra.append(f"   ✅ {descripcion}: {obra[campo_fecha]}")
                    
                    # Empresas participantes
                    empresas = obra.get('empresas', [])
                    if empresas:
                        actuaciones_obra.append(f"   🏢 Empresas: {len(empresas)} registradas")
                        for empresa in empresas[:3]:  # Mostrar solo las primeras 3
                            nombre_empresa = empresa.get('nombre', 'Sin nombre')
                            actuaciones_obra.append(f"      • {nombre_empresa}")
                    
                    # Liquidación
                    liquidacion = obra.get('liquidacion', {})
                    if liquidacion:
                        actuaciones_obra.append("   💰 Liquidación: Datos disponibles")
                    
                    # Facturas (si existen)
                    facturas = obra.get('facturas', [])
                    if facturas:
                        actuaciones_obra.append(f"   🧾 Facturas: {len(facturas)} registradas")
                    
                    if actuaciones_obra:
                        resultado.extend(actuaciones_obra)
                    else:
                        resultado.append("   ⚪ Sin actuaciones específicas registradas")
                    
                    resultado.append("")
            
            # Información de firmantes
            if firmantes:
                resultado.append("✍️ FIRMANTES CONFIGURADOS:")
                resultado.append("-" * 30)
                for cargo, nombre in firmantes.items():
                    if nombre:
                        resultado.append(f"   • {cargo}: {nombre}")
                resultado.append("")
            
            # Estadísticas adicionales
            resultado.append("📈 ESTADÍSTICAS:")
            resultado.append("-" * 20)
            
            tipos_actuacion = {}
            obras_con_empresas = 0
            obras_con_fechas = 0
            
            for obra in obras:
                tipo = obra.get('tipoActuacion', 'Sin especificar')
                tipos_actuacion[tipo] = tipos_actuacion.get(tipo, 0) + 1
                
                if obra.get('empresas'):
                    obras_con_empresas += 1
                
                fechas = [obra.get(f) for f in ['fechaInicio', 'fechaReplanteo', 'fechaRecepcion']]
                if any(fechas):
                    obras_con_fechas += 1
            
            for tipo, cantidad in tipos_actuacion.items():
                resultado.append(f"   • {tipo}: {cantidad} obras")
            
            resultado.append(f"   • Obras con empresas: {obras_con_empresas}/{len(obras)}")
            resultado.append(f"   • Obras con fechas: {obras_con_fechas}/{len(obras)}")
            
            return "\n".join(resultado)
            
        except Exception as e:
            return f"Error analizando actuaciones: {e}"
    
    def abrir_json_diferente(self):
        """Botón 2: Abrir un archivo JSON diferente"""
        try:
            # Diálogo para seleccionar archivo
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo JSON",
                os.path.dirname(self.json_actual) if self.json_actual else "",
                "Archivos JSON (*.json);;Todos los archivos (*.*)"
            )
            
            if archivo and os.path.exists(archivo):
                self.cargar_json_externo(archivo)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo JSON diferente: {e}")
    
    def seleccionar_backup(self):
        """Botón 3: Seleccionar un backup de la lista"""
        try:
            item_actual = self.lista_backups.currentItem()
            if not item_actual:
                QMessageBox.information(self, "Sin Selección", "Selecciona un backup de la lista")
                return
            
            self.cargar_backup_seleccionado(item_actual)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error seleccionando backup: {e}")
    
    def cargar_backup_seleccionado(self, item):
        """Cargar el backup seleccionado"""
        try:
            ruta_backup = item.data(Qt.UserRole)
            if ruta_backup and os.path.exists(ruta_backup):
                self.cargar_json_externo(ruta_backup)
            else:
                QMessageBox.warning(self, "Error", "Archivo de backup no encontrado")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando backup: {e}")
    
    def cargar_json_externo(self, ruta_archivo: str):
        """Cargar un archivo JSON externo"""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_externos = json.load(f)
            
            # Mostrar información del archivo cargado
            nombre_archivo = os.path.basename(ruta_archivo)
            self.titulo_visualizacion.setText(f"📄 Contenido de: {nombre_archivo}")
            
            # Extraer y mostrar actuaciones
            actuaciones_info = self.extraer_actuaciones(datos_externos)
            self.area_contenido.setPlainText(actuaciones_info)
            
            # Preguntar si quiere cambiar al JSON cargado
            respuesta = QMessageBox.question(
                self, 
                "JSON Cargado",
                f"Archivo cargado: {nombre_archivo}\n\n"
                f"¿Desea cambiar la aplicación a este archivo JSON?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                self.cambiar_json_aplicacion(ruta_archivo)
            else:
                # 🆕 INCLUSO SI NO CAMBIA LA APLICACIÓN, REFRESCAR BACKUPS
                # por si el archivo cargado está en el mismo directorio
                directorio_cargado = os.path.dirname(ruta_archivo)
                directorio_actual = os.path.dirname(self.json_actual) if self.json_actual else ""
                
                if directorio_cargado == directorio_actual:
                    logger.debug("Refrescando backups por archivo en mismo directorio")
                    self.cargar_lista_backups()
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error JSON", f"Error en formato JSON:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando archivo:\n{e}")
    
    def cambiar_json_aplicacion(self, nueva_ruta: str):
        """Cambiar la aplicación para usar el nuevo archivo JSON"""
        try:
            if hasattr(self.parent, 'controlador_json') and self.parent.controlador_json:
                # Cambiar el archivo JSON del controlador
                exito = self.parent.controlador_json.cambiar_archivo_json(nueva_ruta)
                
                if exito:
                    # Recargar contratos en la aplicación principal
                    if hasattr(self.parent, 'contract_manager') and self.parent.contract_manager:
                        self.parent.contract_manager.reload_contracts()
                    
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Aplicación cambiada al archivo:\n{os.path.basename(nueva_ruta)}\n\n"
                        f"La lista de contratos se ha actualizado."
                    )
                    
                    # 🆕 ACTUALIZAR COMPLETAMENTE LA INFORMACIÓN LOCAL
                    self.json_actual = nueva_ruta
                    self.cargar_json_actual()  # Esto también recargará la lista de backups
                    
                    # 🆕 REFRESCAR LA INTERFAZ DEL DIÁLOGO
                    self.refrescar_interfaz_completa()
                    
                else:
                    QMessageBox.critical(self, "Error", "No se pudo cambiar el archivo JSON")
            else:
                QMessageBox.critical(self, "Error", "Controlador JSON no disponible")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cambiando JSON: {e}")
    
    def refrescar_interfaz_completa(self):
        """Refrescar completamente la interfaz del diálogo después de cambiar JSON"""
        try:
            logger.debug("Refrescando interfaz completa...")
            
            # Limpiar el área de contenido
            self.area_contenido.clear()
            self.area_contenido.setPlainText("Archivo JSON cambiado. Seleccione una opción para ver el contenido...")
            
            # Resetear el título de visualización
            self.titulo_visualizacion.setText("📄 Contenido JSON")
            
            # Recargar y refrescar la lista de backups
            self.cargar_lista_backups()
            
            # Mostrar mensaje de confirmación en el área de contenido
            nombre_archivo = os.path.basename(self.json_actual) if self.json_actual else "Desconocido"
            mensaje_refresh = f"""
🔄 INTERFAZ ACTUALIZADA

✅ JSON actual cambiado a: {nombre_archivo}
✅ Lista de backups refrescada
✅ Contratos recargados en la aplicación principal

📋 Opciones disponibles:
• Mostrar Todas las Actuaciones
• Abrir JSON Diferente 
• Seleccionar Backup

Seleccione una opción para continuar...
            """.strip()
            
            self.area_contenido.setPlainText(mensaje_refresh)
            
            logger.info("Interfaz refrescada completamente")
            
        except Exception as e:
            logger.error(f"Error refrescando interfaz: {e}")