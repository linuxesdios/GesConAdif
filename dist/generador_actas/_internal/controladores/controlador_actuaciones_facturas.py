
            
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controladorhe para gestión de actuaciones y facturas
"""
import os
import json
import subprocess
import webbrowser
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QComboBox, QPushButton, QFileDialog, 
                           QMessageBox, QListWidget, QLabel, QTableWidget,
                           QTableWidgetItem, QHeaderView, QAbstractItemView,
                           QWidget,QSizePolicy, QTextEdit)
from PyQt5.QtCore import QMargins
from PyQt5.QtCore import Qt
from .dialogo_gestionar_contratos import DialogoCrearContrato, DialogoBorrarContrato
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QColor

class DialogoActuacion(QDialog):
    """Diálogo para agregar/editar actuación"""
    
    def __init__(self, parent=None, actuacion_data=None):
        super().__init__(parent)
        self.actuacion_data = actuacion_data
        self.archivos_pdf = []
        self.setup_ui()
        
        if actuacion_data:
            self.cargar_datos(actuacion_data)
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("Agregar/Editar Actuación")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.le_actuacion = QLineEdit()
        self.le_actuacion.setPlaceholderText("Descripción de la actuación")
        form_layout.addRow("Actuación:", self.le_actuacion)
        
        self.le_localidad = QLineEdit()
        self.le_localidad.setPlaceholderText("Madrid, Barcelona, etc.")
        form_layout.addRow("Localidad:", self.le_localidad)
        
        self.le_gped = QLineEdit()
        self.le_gped.setPlaceholderText("Número GPED")
        form_layout.addRow("GPED:", self.le_gped)
        
        layout.addLayout(form_layout)
        
        # Sección PDFs
        layout.addWidget(QLabel("Archivos PDF:"))
        
        pdf_layout = QHBoxLayout()
        self.btn_agregar_pdf = QPushButton("📄 Agregar PDF")
        self.btn_agregar_pdf.clicked.connect(self.agregar_pdf)
        pdf_layout.addWidget(self.btn_agregar_pdf)
        
        self.btn_quitar_pdf = QPushButton("🗑️ Quitar PDF")
        self.btn_quitar_pdf.clicked.connect(self.quitar_pdf)
        pdf_layout.addWidget(self.btn_quitar_pdf)
        
        layout.addLayout(pdf_layout)
        
        # Lista de PDFs
        self.list_pdfs = QListWidget()
        layout.addWidget(self.list_pdfs)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)
    
    def agregar_pdf(self):
        """Agregar archivo PDF"""
        archivos, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos PDF", "", "Archivos PDF (*.pdf)"
        )
        
        for archivo in archivos:
            if archivo not in self.archivos_pdf:
                self.archivos_pdf.append(archivo)
                nombre_archivo = os.path.basename(archivo)
                self.list_pdfs.addItem(f"📄 {nombre_archivo}")
    
    def quitar_pdf(self):
        """Quitar archivo PDF seleccionado"""
        fila_actual = self.list_pdfs.currentRow()
        if fila_actual >= 0:
            self.archivos_pdf.pop(fila_actual)
            self.list_pdfs.takeItem(fila_actual)
    
    def cargar_datos(self, datos):
        """Cargar datos en el formulario"""
        self.le_actuacion.setText(datos.get('actuacion', ''))
        self.le_localidad.setText(datos.get('localidad', ''))
        self.le_gped.setText(datos.get('gped', ''))
        
        # Cargar PDFs (si existen)
        pdfs = datos.get('archivos_pdf', [])
        for pdf in pdfs:
            self.archivos_pdf.append(pdf)
            nombre = os.path.basename(pdf)
            self.list_pdfs.addItem(f"📄 {nombre}")
    
    def obtener_datos(self):
        """Obtener datos del formulario"""
        return {
            'actuacion': self.le_actuacion.text().strip(),
            'localidad': self.le_localidad.text().strip(),
            'gped': self.le_gped.text().strip(),
            'archivos_pdf': self.archivos_pdf.copy(),
            'fecha_creacion': datetime.now().isoformat(),
            'facturas_asociadas': [],
            'id': datetime.now().strftime("%Y%m%d_%H%M%S")
        }


class DialogoActuacionMail(DialogoActuacion):
    """Diálogo para agregar actuación con funcionalidad de email"""
    
    def __init__(self, parent=None, actuacion_data=None):
        super().__init__(parent, actuacion_data)
        self.setWindowTitle("Agregar Actuación con Email")
    
    def setup_ui(self):
        """Configurar interfaz con campos adicionales de email"""
        super().setup_ui()
        
        # Encontrar el layout del formulario
        form_layout = None
        main_layout = self.layout()
        if main_layout is not None:
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if item is not None and hasattr(item, 'layout') and callable(item.layout):
                    sub_layout = item.layout()
                    if isinstance(sub_layout, QFormLayout):
                        form_layout = sub_layout
                        break
        
        if form_layout:
            # Añadir campos de email
            self.le_email = QLineEdit()
            self.le_email.setPlaceholderText("destinatario@ejemplo.com")
            form_layout.addRow("Email:", self.le_email)
            
            self.te_mensaje = QTextEdit()
            self.te_mensaje.setPlaceholderText("Mensaje del email...")
            self.te_mensaje.setMaximumHeight(80)
            form_layout.addRow("Mensaje:", self.te_mensaje)
        
        # Cambiar el botón guardar por "Enviar mail y guardar"
        self.btn_guardar.setText("📧 Enviar mail y guardar")
    
    def obtener_datos(self):
        """Obtener datos incluyendo campos de email"""
        datos = super().obtener_datos()
        datos['email'] = self.le_email.text().strip()
        datos['mensaje'] = self.te_mensaje.toPlainText().strip()
        return datos
    
    def cargar_datos(self, datos):
        """Cargar datos incluyendo campos de email"""
        super().cargar_datos(datos)
        self.le_email.setText(datos.get('email', ''))
        self.te_mensaje.setPlainText(datos.get('mensaje', ''))


class DialogoFactura(QDialog):
    """Diálogo para agregar/editar factura"""
    
    def __init__(self, parent=None, factura_data=None, actuaciones_disponibles=None):
        super().__init__(parent)
        self.factura_data = factura_data
        self.actuaciones_disponibles = actuaciones_disponibles or []
        self.archivos_pdf = []
        self.setup_ui()
        
        if factura_data:
            self.cargar_datos(factura_data)
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        self.setWindowTitle("Agregar/Editar Factura")
        self.setModal(True)
        self.resize(500, 450)
        
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        self.le_nombre = QLineEdit()
        self.le_nombre.setPlaceholderText("Nombre/descripción de la factura")
        form_layout.addRow("Nombre:", self.le_nombre)
        
        self.le_importe = QLineEdit()
        self.le_importe.setPlaceholderText("0.00")
        form_layout.addRow("Importe (€):", self.le_importe)
        
        layout.addLayout(form_layout)
        
        # Actuaciones asociadas
        layout.addWidget(QLabel("Actuaciones Asociadas:"))
        self.combo_actuaciones = QComboBox()
        self.combo_actuaciones.addItem("-- Seleccionar Actuación --")
        
        for actuacion in self.actuaciones_disponibles:
            texto = f"{actuacion.get('id', '')} - {actuacion.get('actuacion', '')}"
            self.combo_actuaciones.addItem(texto, actuacion.get('id'))
        
        actuaciones_layout = QHBoxLayout()
        actuaciones_layout.addWidget(self.combo_actuaciones)
        
        self.btn_asociar = QPushButton("➕ Asociar")
        self.btn_asociar.clicked.connect(self.asociar_actuacion)
        actuaciones_layout.addWidget(self.btn_asociar)
        
        layout.addLayout(actuaciones_layout)
        
        # Lista de actuaciones asociadas
        self.list_actuaciones = QListWidget()
        layout.addWidget(self.list_actuaciones)
        
        # Sección PDFs
        layout.addWidget(QLabel("Archivos PDF:"))
        
        pdf_layout = QHBoxLayout()
        self.btn_agregar_pdf = QPushButton("📄 Agregar PDF")
        self.btn_agregar_pdf.clicked.connect(self.agregar_pdf)
        pdf_layout.addWidget(self.btn_agregar_pdf)
        
        self.btn_quitar_pdf = QPushButton("🗑️ Quitar PDF")
        self.btn_quitar_pdf.clicked.connect(self.quitar_pdf)
        pdf_layout.addWidget(self.btn_quitar_pdf)
        
        layout.addLayout(pdf_layout)
        
        # Lista de PDFs
        self.list_pdfs = QListWidget()
        layout.addWidget(self.list_pdfs)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)
    
    def asociar_actuacion(self):
        """Asociar actuación seleccionada"""
        if self.combo_actuaciones.currentIndex() > 0:
            texto = self.combo_actuaciones.currentText()
            actuacion_id = self.combo_actuaciones.currentData()
            
            # Verificar que no esté ya asociada
            for i in range(self.list_actuaciones.count()):
                item = self.list_actuaciones.item(i)
                if item is not None and item.data(Qt.ItemDataRole.UserRole) == actuacion_id:
                    QMessageBox.warning(self, "Advertencia", "Esta actuación ya está asociada")
                    return
            
            self.list_actuaciones.addItem(f"🔗 {texto}")
            item = self.list_actuaciones.item(self.list_actuaciones.count()-1)
            if item is not None:
                item.setData(Qt.ItemDataRole.UserRole, actuacion_id)
    
    def agregar_pdf(self):
        """Agregar archivo PDF"""
        archivos, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos PDF", "", "Archivos PDF (*.pdf)"
        )
        
        for archivo in archivos:
            if archivo not in self.archivos_pdf:
                self.archivos_pdf.append(archivo)
                nombre_archivo = os.path.basename(archivo)
                self.list_pdfs.addItem(f"📄 {nombre_archivo}")
    
    def quitar_pdf(self):
        """Quitar archivo PDF seleccionado"""
        fila_actual = self.list_pdfs.currentRow()
        if fila_actual >= 0:
            self.archivos_pdf.pop(fila_actual)
            self.list_pdfs.takeItem(fila_actual)
    
    def cargar_datos(self, datos):
        """Cargar datos en el formulario"""
        self.le_nombre.setText(datos.get('nombre', ''))
        self.le_importe.setText(str(datos.get('importe', '0.00')))
        
        # Limpiar listas previas
        self.list_actuaciones.clear()
        self.list_pdfs.clear()
        self.archivos_pdf.clear()
        
        # Cargar actuaciones asociadas
        for actuacion_id in datos.get('actuaciones_asociadas', []):
            for actuacion in self.actuaciones_disponibles:
                if actuacion.get('id') == actuacion_id:
                    texto = f"{actuacion_id} - {actuacion.get('actuacion', '')}"
                    self.list_actuaciones.addItem(f"🔗 {texto}")
                    self.list_actuaciones.item(self.list_actuaciones.count()-1).setData(Qt.UserRole, actuacion_id)
                    break
        
        # Cargar PDFs
        pdfs = datos.get('archivos_pdf', [])
        for pdf in pdfs:
            self.archivos_pdf.append(pdf)
            nombre = os.path.basename(pdf)
            self.list_pdfs.addItem(f"📄 {nombre}")
        


    
    def obtener_datos(self):
        """Obtener datos del formulario"""
        # Obtener IDs de actuaciones asociadas
        actuaciones_asociadas = []
        for i in range(self.list_actuaciones.count()):
            actuacion_id = self.list_actuaciones.item(i).data(Qt.UserRole)
            if actuacion_id:
                actuaciones_asociadas.append(actuacion_id)
        
        # Convertir importe a float
        try:
            importe = float(self.le_importe.text().replace(',', '.'))
        except ValueError:
            importe = 0.0
        
        return {
            'nombre': self.le_nombre.text().strip(),
            'importe': importe,
            'actuaciones_asociadas': actuaciones_asociadas,
            'archivos_pdf': self.archivos_pdf.copy(),
            'fecha_creacion': datetime.now().isoformat(),
            'id': datetime.now().strftime("%Y%m%d_%H%M%S")
        }


class ControladorActuacionesFacturas:
    """Controlador principal para gestión de actuaciones y facturas"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.proyecto_actual = None
        self.ruta_carpeta_obra = None
        self.label_presupuesto_total = getattr(main_window, 'presupuesto_total', None)
        self.label_presupuesto_gastado = getattr(main_window, 'presupuesto_gastado', None) 
        self.label_presupuesto_disponible = getattr(main_window, 'presupuesto_disponible', None)
        self.contract_manager = getattr(main_window, 'contract_manager', None)


        # Datos
        self.actuaciones = []
        self.facturas = []
        
        # Referencias a elementos UI - CORREGIR NOMBRES
        self.table_actuaciones = getattr(main_window, 'tableActuaciones', None)
        self.table_facturas = getattr(main_window, 'tableFactura', None)
        
        # Guardar referencia a main_window para re-búsquedas posteriores
        self.main_window = main_window
        
        # Debug: Verificar que se encontraron las tablas


        
        # Si no se encuentran, intentar buscar de forma alternativa
        if not self.table_actuaciones:

            # Buscar en todos los widgets hijos
            for child in main_window.findChildren(QTableWidget):
                if child.objectName() == 'tableActuaciones':
                    self.table_actuaciones = child

                    break
                    
        if not self.table_facturas:

            # Buscar en todos los widgets hijos
            for child in main_window.findChildren(QTableWidget):
                if child.objectName() == 'tableFactura':
                    self.table_facturas = child

                    break  
        self.btn_add_actuacion = getattr(main_window, 'add_actuacion', None)
        self.btn_add_factura = getattr(main_window, 'add_factura', None)
        self.graphics_view = getattr(main_window, 'graphicsView', None)
        
        # Debug: Verificar graphics_view

        
        # Si no se encuentra, buscar de forma alternativa
        if not self.graphics_view:

            from PyQt5.QtWidgets import QGraphicsView
            for child in main_window.findChildren(QGraphicsView):
                if child.objectName() == 'graphicsView':
                    self.graphics_view = child

                    break
        # AGREGAR: Botones de borrar
        self.btn_borrar_actuacion = getattr(main_window, 'borrar_actuacion', None)
        self.btn_borrar_factura = getattr(main_window, 'borrar_factura', None)

        pass
        
        self.setup_connections_facturas()
        self.setup_tables()
    
    def setup_connections_facturas(self):
        """Configurar conexiones de botones"""
        try:
            if self.btn_add_actuacion:
                self.btn_add_actuacion.clicked.connect(self.agregar_actuacion)
            
            if self.btn_add_factura:
                self.btn_add_factura.clicked.connect(self.agregar_factura)
            
            if self.btn_borrar_actuacion:
                self.btn_borrar_actuacion.clicked.connect(self.borrar_actuacion)
            
            if self.btn_borrar_factura:
                self.btn_borrar_factura.clicked.connect(self.borrar_factura)
            

                
        except Exception:
            pass
    
    def setup_tables(self):
        """Configurar tablas"""

        logging.debug(f"[ActuacionesFacturas] table_actuaciones: {self.table_actuaciones is not None}")
        logging.debug(f"[ActuacionesFacturas] table_facturas: {self.table_facturas is not None}")
        
        # Configurar tabla actuaciones
        if self.table_actuaciones:
            headers_actuaciones = ["Actuación", "Localidad", "GPED", "Facturas Asociadas", "Acciones"]
            self.table_actuaciones.setColumnCount(len(headers_actuaciones))
            self.table_actuaciones.setHorizontalHeaderLabels(headers_actuaciones)

            
            # Configurar anchos de columna
            header = self.table_actuaciones.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Actuación
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Localidad
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # GPED
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Facturas
            header.setSectionResizeMode(4, QHeaderView.Interactive)
            
            self.table_actuaciones.cellDoubleClicked.connect(self.editar_actuacion_doble_clic)
        
        # Configurar tabla facturas
        if self.table_facturas:
            headers_facturas = ["Nombre", "Importe (€)", "Actuaciones Asociadas", "Acciones"]
            self.table_facturas.setColumnCount(len(headers_facturas))
            self.table_facturas.setHorizontalHeaderLabels(headers_facturas)

            
            # Configurar anchos de columna
            header = self.table_facturas.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Importe
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Actuaciones
            header.setSectionResizeMode(3, QHeaderView.Interactive)  # Acciones

            self.table_facturas.cellDoubleClicked.connect(self.editar_factura_doble_clic)
    
    def set_proyecto_actual(self, nombre_proyecto, contract_data=None):
        """Establecer el proyecto actual"""
        try:
            if not nombre_proyecto or not nombre_proyecto.strip():
                return
            
            self.proyecto_actual = nombre_proyecto.strip()
            self.contract_data = contract_data or {}
            
            self._cargar_datos_desde_json()
            self._actualizar_labels_presupuesto()
            self._actualizar_graficos()
            self._actualizar_estado_botones()
            
        except Exception:
            pass
    def _ejecutar_con_carpeta(self, accion_callback, nombre_accion="Acción"):
        """
        Ejecutar una acción que requiere carpeta, creándola si es necesario
        
        Args:
            accion_callback: Función a ejecutar que recibe (carpeta_path)
            nombre_accion: Nombre de la acción para logs
        """
        try:
            if not self.proyecto_actual:
                logging.warning(f"[ActuacionesFacturas] {nombre_accion}: No hay proyecto actual")
                return False
            
            # Obtener/crear carpeta
            carpeta = self.obtener_carpeta_proyecto(crear_si_no_existe=True)
            
            if not carpeta:
                logging.error(f"[ActuacionesFacturas] {nombre_accion}: No se pudo obtener carpeta")
                return False
            
            # Ejecutar acción
            return accion_callback(carpeta)
            
        except Exception as e:
            logging.error(f"[ActuacionesFacturas] Error en {nombre_accion}: {e}")
            return False
    
    
    def _cargar_datos_desde_json(self):
        """Cargar datos desde el JSON del contrato"""
        try:
            if not self.contract_data:
                return
            
            # Cargar actuaciones
            self.actuaciones = self.contract_data.get('actuaciones', [])

            
            # Cargar facturas
            self.facturas = self.contract_data.get('facturas', [])

            
            # Debug: Mostrar primer elemento si existe

            
            # Actualizar tablas
            self._actualizar_tabla_actuaciones()
            self._actualizar_tabla_facturas()
            
            
        except Exception as e:
            logging.error(f"[ActuacionesFacturas] Error cargando datos: {e}")
    
    def _actualizar_tabla_actuaciones(self):
        """Actualizar tabla de actuaciones"""

        logging.debug(f"[ActuacionesFacturas] table_actuaciones: {self.table_actuaciones is not None}")

        
        if not self.table_actuaciones:


            # Intentar re-encontrar la tabla
            if hasattr(self, 'main_window') and self.main_window:
                for child in self.main_window.findChildren(QTableWidget):
                    if child.objectName() == 'tableActuaciones':
                        self.table_actuaciones = child

                        break
            if not self.table_actuaciones:
                return
        
        self.table_actuaciones.setRowCount(len(self.actuaciones))

        
        for i, actuacion in enumerate(self.actuaciones):
            # Usar el campo 'actuacion' en lugar de 'nombre' para coincidir con el JSON
            self.table_actuaciones.setItem(i, 0, QTableWidgetItem(actuacion.get('actuacion', '')))
            self.table_actuaciones.setItem(i, 1, QTableWidgetItem(actuacion.get('localidad', '')))
            self.table_actuaciones.setItem(i, 2, QTableWidgetItem(str(actuacion.get('gped', ''))))
            self.table_actuaciones.setItem(i, 3, QTableWidgetItem(str(len(actuacion.get('facturas_asociadas', [])))))
    
    def _actualizar_tabla_facturas(self):
        """Actualizar tabla de facturas"""

        logging.debug(f"[ActuacionesFacturas] table_facturas: {self.table_facturas is not None}")

        
        if not self.table_facturas:

            # Intentar re-encontrar la tabla
            if hasattr(self, 'main_window') and self.main_window:
                for child in self.main_window.findChildren(QTableWidget):
                    if child.objectName() == 'tableFactura':
                        self.table_facturas = child

                        break
            if not self.table_facturas:
                return
        
        self.table_facturas.setRowCount(len(self.facturas))
        
        for i, factura in enumerate(self.facturas):
            self.table_facturas.setItem(i, 0, QTableWidgetItem(factura.get('nombre', '')))
            self.table_facturas.setItem(i, 1, QTableWidgetItem(f"{factura.get('importe', 0):.2f}"))
            self.table_facturas.setItem(i, 2, QTableWidgetItem(str(len(factura.get('actuaciones_asociadas', [])))))
    
    def _actualizar_labels_presupuesto(self):
        """Actualizar labels de presupuesto"""
        try:
            if not self.contract_data:
                return
            
            # Buscar presupuesto en diferentes ubicaciones posibles
            presupuesto_total = 0
            if 'basePresupuesto' in self.contract_data:
                presupuesto_total = float(self.contract_data.get('basePresupuesto', 0))
            elif 'datos_contrato' in self.contract_data and 'basePresupuesto' in self.contract_data['datos_contrato']:
                presupuesto_total = float(self.contract_data['datos_contrato'].get('basePresupuesto', 0))
            

            presupuesto_gastado = sum(float(f.get('importe', 0)) for f in self.facturas)
            presupuesto_disponible = presupuesto_total - presupuesto_gastado
            
            if self.label_presupuesto_total:
                self.label_presupuesto_total.setText(f"{presupuesto_total:.2f} €")
            
            if self.label_presupuesto_gastado:
                self.label_presupuesto_gastado.setText(f"{presupuesto_gastado:.2f} €")
            
            if self.label_presupuesto_disponible:
                self.label_presupuesto_disponible.setText(f"{presupuesto_disponible:.2f} €")
            
        except Exception as e:
            logging.error(f"[ActuacionesFacturas] Error actualizando presupuesto: {e}")
    
    def _actualizar_graficos(self):
        """Actualizar gráficos al cargar contrato"""
        try:

            
            if not self.graphics_view:

                return
            
            if not self.contract_data:

                return
            
            # Obtener presupuesto total
            presupuesto_total = 0
            if 'basePresupuesto' in self.contract_data:
                presupuesto_total = float(self.contract_data.get('basePresupuesto', 0))
            elif 'datos_contrato' in self.contract_data and 'basePresupuesto' in self.contract_data['datos_contrato']:
                presupuesto_total = float(self.contract_data['datos_contrato'].get('basePresupuesto', 0))
            
            # Calcular total gastado de las facturas
            total_gastado = sum(float(f.get('importe', 0)) for f in self.facturas)
            

            
            # Actualizar el gráfico quesito
            self._actualizar_grafico_quesito(presupuesto_total, total_gastado)
            
        except Exception as e:
            logging.error(f"[ActuacionesFacturas] Error actualizando gráficos: {e}")
    
 
    
   

    def crear_carpeta_proyecto_si_no_existe(self):
        """Crear carpeta del proyecto actual si no existe"""
        try:
            carpeta = self.obtener_carpeta_proyecto(crear_si_no_existe=True)
            if carpeta:
                return carpeta
            else:
                print(f"[ActuacionesFacturas] ❌ No se pudo crear/obtener carpeta")
                return None
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error creando carpeta: {e}")
            return None
            
    def _actualizar_labels_presupuesto(self):
        """Actualizar labels de presupuesto"""
        try:
            if not self.contract_data:
                return
            
            # Obtener presupuesto base
            presupuesto_base = self.contract_data.get('basePresupuesto', 0)
            if isinstance(presupuesto_base, str):
                try:
                    presupuesto_base = float(presupuesto_base)
                except:
                    presupuesto_base = 0
            
            # Calcular gastado (suma de facturas)
            facturas = self.contract_data.get('facturas', [])
            total_gastado = 0
            
            for factura in facturas:
                try:
                    importe = factura.get('importe', 0)
                    if isinstance(importe, str):
                        importe = float(importe)
                    total_gastado += importe
                except:
                    continue
            
            # Calcular disponible
            disponible = presupuesto_base - total_gastado
            

            
            # Actualizar labels en la UI si existen
            if hasattr(self, 'label_presupuesto_total') and self.label_presupuesto_total is not None:
                self.label_presupuesto_total.setText(f"{presupuesto_base:.2f}€")
            
            if hasattr(self, 'label_presupuesto_gastado') and self.label_presupuesto_gastado is not None:
                self.label_presupuesto_gastado.setText(f"{total_gastado:.2f}€")
            
            if hasattr(self, 'label_presupuesto_disponible') and self.label_presupuesto_disponible is not None:
                self.label_presupuesto_disponible.setText(f"{disponible:.2f}€")
            
        except Exception as e:
            logging.error(f"[ActuacionesFacturas] Error actualizando labels presupuesto: {e}")
    # Método debug eliminado - innecesario en producción

    # TAMBIÉN AGREGA ESTE MÉTODO AL ContractManagerQt5 PARA VERIFICAR RÁPIDAMENTE

    
    def _actualizar_graficos_duplicado(self):
        """Método duplicado - eliminar o renombrar"""
        # Este método parece ser duplicado, manteniendo para compatibilidad
        self._actualizar_graficos()

    def _actualizar_estado_botones(self):
        """Actualizar estado de botones"""
        try:
            # Habilitar botones si hay proyecto actual
            tiene_proyecto = bool(self.proyecto_actual)
            
            # Buscar botones y habilitar/deshabilitar
            botones = ['add_actuacion', 'add_factura', 'btn_abrir_carpeta']
            
            for nombre_boton in botones:
                if hasattr(self, nombre_boton):
                    boton = getattr(self, nombre_boton)
                    if hasattr(boton, 'setEnabled'):
                        boton.setEnabled(tiene_proyecto)
            
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error actualizando botones: {e}")

    


    def _buscar_carpeta_existente(self, controlador_archivos, nombre_proyecto, numero_expediente, alias, nombre_carpeta):
        """Buscar carpeta existente con múltiples criterios"""
        try:
            # Usar método extendido si existe
            if hasattr(controlador_archivos, 'verificar_carpeta_obra_extendida'):
                return controlador_archivos.verificar_carpeta_obra_extendida(
                    nombre_proyecto, numero_expediente, alias, nombre_carpeta
                )
            else:
                # Fallback al método básico
                return controlador_archivos.verificar_carpeta_obra(nombre_proyecto, numero_expediente)
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error buscando carpeta: {e}")
            return False, "", "error"
    def obtener_carpeta_proyecto(self, crear_si_no_existe=False):
        """
        Obtener carpeta del proyecto actual - DELEGANDO AL GESTOR UNIFICADO
        
        Args:
            crear_si_no_existe: Si True, crea la carpeta usando el gestor unificado
            
        Returns:
            str: Path de la carpeta o None
        """
        try:
            if not self.proyecto_actual:

                return None
            
            # MÉTODO 1: Usar gestor de archivos unificado (PRIORITARIO)
            if hasattr(self.main_window, 'gestor_archivos_unificado') and self.main_window.gestor_archivos_unificado:
                
                # Obtener datos del contrato actual
                contract_data = None
                if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                    contract_data = self.main_window.contract_manager.get_current_contract_data()
                
                if contract_data:
                    gestor = self.main_window.gestor_archivos_unificado
                    
                    if crear_si_no_existe:
                        # Crear carpeta usando gestor unificado
                        carpeta_path = gestor.obtener_carpeta_obra(contract_data, crear_si_no_existe=True)
                        if carpeta_path:
                            return carpeta_path
                    else:
                        # Solo verificar si existe
                        carpeta_path = gestor.buscar_carpeta_existente(contract_data)
                        if carpeta_path:
                            return carpeta_path
            
            # MÉTODO 2: Usar contract_manager como fallback
            if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                
                if crear_si_no_existe:
                    return self.main_window.contract_manager.crear_carpeta_para_contrato_actual()
                else:
                    # Solo verificar existencia básica
                    contract_data = self.main_window.contract_manager.get_current_contract_data()
                    if contract_data:
                        nombre_carpeta = contract_data.get('nombreCarpeta', '')
                        if nombre_carpeta:
                            current_dir = os.path.dirname(os.path.dirname(__file__))
                            obras_dir = os.path.join(current_dir, "obras")
                            carpeta_path = os.path.join(obras_dir, nombre_carpeta)
                            
                            if os.path.exists(carpeta_path):
                                return carpeta_path
            
            print("[ActuacionesFacturas] ❌ No se pudo obtener carpeta")
            return None
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error obteniendo carpeta: {e}")
            return None


    # def _crear_carpeta_automatica(self, nombre_proyecto, numero_expediente, alias, nombre_carpeta):
    #     """Crear carpeta automáticamente para el proyecto"""
    #     try:
    #         print(f"[ActuacionesFacturas] 🏗️ Creando carpeta automática...")
            
    #         # Determinar nombre de carpeta a crear
    #         if nombre_carpeta and nombre_carpeta.strip():
    #             nombre_final = nombre_carpeta.strip()
    #         elif numero_expediente and numero_expediente.strip():
    #             nombre_final = numero_expediente.strip().replace('/', '_').replace('\\', '_')
    #         else:
    #             nombre_final = nombre_proyecto
            
    #         # Limpiar nombre para sistema de archivos
    #         nombre_final = self._limpiar_nombre_para_carpeta(nombre_final)
            
    #         # Determinar ruta base
    #         script_dir = os.path.dirname(os.path.abspath(__file__))
    #         parent_dir = os.path.dirname(script_dir)
    #         obras_dir = os.path.join(parent_dir, "obras")
            
    #         # Crear directorio obras si no existe
    #         os.makedirs(obras_dir, exist_ok=True)
            
    #         # Crear ruta final evitando duplicados
    #         carpeta_path = os.path.join(obras_dir, nombre_final)
    #         contador = 1
    #         carpeta_path_original = carpeta_path
            
    #         while os.path.exists(carpeta_path):
    #             carpeta_path = f"{carpeta_path_original}_{contador}"
    #             contador += 1
            
    #         # Crear carpeta principal
    #         os.makedirs(carpeta_path)
            
    #         # Crear estructura completa
    #         subcarpetas = [
    #             "01-proyecto",
    #             "02-documentacion-finales", 
    #             "03-cartas-finales",
    #             "04-documentos-sin-firmar",
    #             "05-cartas-sin-firmar",
    #             "06-ofertas",
    #             "07-seguridad-y-salud",
    #             "08-actuaciones",
    #             "09-facturas",
    #             "10-otros"
    #         ]
            
    #         for subcarpeta in subcarpetas:
    #             subcarpeta_path = os.path.join(carpeta_path, subcarpeta)
    #             os.makedirs(subcarpeta_path)
                
    #             # Crear archivo informativo
    #             info_path = os.path.join(subcarpeta_path, "INFO.txt")
    #             with open(info_path, "w", encoding="utf-8") as f:
    #                 f.write(f"Proyecto: {nombre_proyecto}\n")
    #                 f.write(f"Carpeta: {subcarpeta}\n")
    #                 f.write(f"Creado automáticamente: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            
    #         return carpeta_path
            
    #     except Exception as e:
    #         print(f"[ActuacionesFacturas] ❌ Error creando carpeta automática: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return None


    # def _limpiar_nombre_para_carpeta(self, nombre):
    #     """Limpiar nombre para usar como carpeta"""
    #     import re
    #     # Reemplazar caracteres problemáticos
    #     nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre)
    #     nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio)
    #     nombre_limpio = nombre_limpio.strip()
        
    #     # Truncar si es muy largo
    #     if len(nombre_limpio) > 80:
    #         nombre_limpio = nombre_limpio[:77] + "..."
        
    #     return nombre_limpio


    # def _verificar_y_crear_subcarpetas(self, ruta_carpeta):
    #     """Verificar y crear subcarpetas estándar si no existen"""
    #     try:
    #         subcarpetas_requeridas = [
    #             "01-proyecto", "02-documentacion-finales", "03-cartas-finales",
    #             "04-documentos-sin-firmar", "05-cartas-sin-firmar", "06-ofertas",
    #             "07-seguridad-y-salud", "08-actuaciones", "09-facturas", "10-otros"
    #         ]
            
    #         subcarpetas_creadas = 0
    #         for subcarpeta in subcarpetas_requeridas:
    #             ruta_subcarpeta = os.path.join(ruta_carpeta, subcarpeta)
    #             if not os.path.exists(ruta_subcarpeta):
    #                 os.makedirs(ruta_subcarpeta)
    #                 subcarpetas_creadas += 1
            
    #         if subcarpetas_creadas > 0:
    #             pass
    #         else:
    #             pass
                
    #     except Exception as e:
    #         print(f"[ActuacionesFacturas] ❌ Error verificando subcarpetas: {e}")


    def _actualizar_json_con_carpeta(self, datos_proyecto, ruta_carpeta):
        """Actualizar JSON con el nombre de carpeta creada"""
        try:
            nombre_carpeta = os.path.basename(ruta_carpeta)
            nombre_proyecto = datos_proyecto.get('nombreObra', '')
            
            
            # Buscar el archivo JSON
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            json_path = os.path.join(parent_dir, "BaseDatos.json")
            
            # Cargar JSON
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Buscar y actualizar la obra
            obras = data.get("obras", [])
            for obra in obras:
                if obra.get("nombreObra") == nombre_proyecto:
                    obra["nombreCarpeta"] = nombre_carpeta
                    break
            
            # Guardar JSON actualizado
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error actualizando JSON: {e}")

    # ===== MODIFICACIÓN 3: Mejorar mostrar_dialogo_crear_contrato =====
    def mostrar_dialogo_crear_contrato(self):
        """Mostrar diálogo para crear nuevo contrato con recarga automática"""
        try:

            dialogo = DialogoCrearContrato(self)
            
            if dialogo.exec_() == QDialog.Accepted and dialogo.result:

                
                # Llamar al método crear_contrato MEJORADO
                exito, mensaje = self.crear_contrato_con_carpetas(dialogo.result)
                
                if exito:

                    
                    # IMPORTANTE: Recargar COMPLETAMENTE el contract manager
                    if self.contract_manager:

                        
                        # Recargar datos del gestor JSON
                        if hasattr(self.contract_manager, 'gestor_json'):
                            self.contract_manager.gestor_json.datos = self.contract_manager.gestor_json.cargar_datos_json()
                        
                        # Recargar lista de contratos
                        self.contract_manager.load_contracts_from_json()
                        

                    
                    QMessageBox.information(self.main_window, "Contrato Creado", mensaje)
                    
                    # Seleccionar el nuevo contrato creado
                    nuevo_nombre = dialogo.result.get("nombreObra") if dialogo.result else None
                    if nuevo_nombre and hasattr(self.main_window, 'comboBox') and self.main_window.comboBox:
                        # Buscar el nuevo contrato en la lista
                        for i in range(self.main_window.comboBox.count()):
                            texto_item = self.main_window.comboBox.itemText(i)
                            if nuevo_nombre in texto_item or texto_item in nuevo_nombre:
                                self.main_window.comboBox.setCurrentIndex(i)
                                break
                            
                else:
                    print(f"[ControladorGrafica] ❌ Error creando contrato: {mensaje}")
                    QMessageBox.critical(self, "Error", mensaje)
            else:
                pass
                        
        except Exception as e:
            print(f"[ControladorGrafica] ❌ Error creando contrato: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.main_window, "Error", f"Error inesperado: {e}")
    def _verificar_subcarpetas_estandar(self):
        """Verificar y crear subcarpetas estándar si no existen"""
        if not self.ruta_carpeta_obra:
            return
        
        subcarpetas_requeridas = [
            "08-actuaciones",
            "09-facturas"
        ]
        
        for subcarpeta in subcarpetas_requeridas:
            ruta_subcarpeta = os.path.join(self.ruta_carpeta_obra, subcarpeta)
            try:
                if not os.path.exists(ruta_subcarpeta):
                    os.makedirs(ruta_subcarpeta)
            except Exception as e:
                print(f"[ActuacionesFacturas] ❌ Error creando subcarpeta {subcarpeta}: {e}")

    def crear_contrato_con_carpetas(self, datos_contrato):
        """
        Crear un nuevo contrato y su estructura de carpetas.
        Args:
            datos_contrato (dict): Datos del contrato a crear.
        Returns:
            (bool, str): (Éxito, Mensaje)
        """
        try:
            # Guardar el contrato en el gestor JSON
            if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                contract_manager = self.main_window.contract_manager
                if hasattr(contract_manager, 'crear_contrato'):
                    exito, mensaje = contract_manager.crear_contrato(datos_contrato)
                else:
                    return False, "El gestor de contratos no soporta creación de contratos."
            else:
                return False, "No se encontró el gestor de contratos."

            if not exito:
                return False, mensaje

            # Crear estructura de carpetas para el contrato
            nombre_carpeta = datos_contrato.get("nombreCarpeta") or datos_contrato.get("nombreObra")
            if not nombre_carpeta:
                return False, "No se especificó el nombre de la carpeta del contrato."

            # Limpiar nombre para carpeta
            nombre_limpio = "".join(c for c in nombre_carpeta if c.isalnum() or c in (' ', '-', '_')).strip()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            obras_dir = os.path.join(parent_dir, "obras")
            os.makedirs(obras_dir, exist_ok=True)
            carpeta_proyecto = os.path.join(obras_dir, nombre_limpio)
            os.makedirs(carpeta_proyecto, exist_ok=True)
            for subcarpeta in ["08-actuaciones", "09-facturas"]:
                os.makedirs(os.path.join(carpeta_proyecto, subcarpeta), exist_ok=True)

            # Actualizar el campo nombreCarpeta en el JSON si es necesario
            if hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json:
                gestor = self.main_window.controlador_json.gestor
                if gestor and 'obras' in gestor.datos:
                    for obra in gestor.datos['obras'].values():
                        if obra.get('nombreObra') == datos_contrato.get('nombreObra'):
                            obra['nombreCarpeta'] = nombre_limpio
                    gestor.guardar_datos()

            return True, f"Contrato y estructura de carpetas creados correctamente en:\n{carpeta_proyecto}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error creando contrato y carpetas: {e}"


    def _mostrar_dialogo_carpeta_no_encontrada(self):
        """Mostrar diálogo cuando no se encuentra la carpeta de obra"""
        try:
            respuesta = QMessageBox.question(
                self.main_window, 
                "Carpeta de Obra No Encontrada",
                f"⚠️ No se encontró la carpeta para el proyecto:\n"
                f"'{self.proyecto_actual}'\n\n"
                f"¿Deseas crear la estructura de carpetas automáticamente?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if respuesta == QMessageBox.Yes:
                self._crear_estructura_carpetas_obra()
            else:
                QMessageBox.information(
                    self.main_window,
                    "Funcionalidad Limitada",
                    "⚠️ Sin carpeta de obra, las funciones de archivos PDF estarán limitadas."
                )
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error mostrando diálogo: {e}")

    
    def _crear_estructura_carpetas_obra(self):
        """Crear estructura de carpetas para la obra"""
        try:
            # Determinar nombre de carpeta
            nombre_limpio = "".join(c for c in (self.proyecto_actual or "") if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Ruta base de obras
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            obras_dir = os.path.join(parent_dir, "obras")
            
            # Crear directorio obras si no existe
            os.makedirs(obras_dir, exist_ok=True)
            
            # Crear carpeta del proyecto
            carpeta_proyecto = os.path.join(obras_dir, nombre_limpio)
            os.makedirs(carpeta_proyecto, exist_ok=True)
            
            # Crear subcarpetas requeridas
            subcarpetas = ["08-actuaciones", "09-facturas"]
            for subcarpeta in subcarpetas:
                os.makedirs(os.path.join(carpeta_proyecto, subcarpeta), exist_ok=True)
            
            # Actualizar ruta
            self.ruta_carpeta_obra = carpeta_proyecto
            
            QMessageBox.information(
                self.main_window,
                "Estructura Creada",
                f"✅ Estructura de carpetas creada:\n{carpeta_proyecto}"
            )
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error creando estructura: {e}")
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Error creando estructura de carpetas:\n{e}"
            )


  
   
    
    def borrar_actuacion(self):
        """Borrar actuación seleccionada"""
        try:
            if not self.table_actuaciones:
                return
            
            fila_actual = self.table_actuaciones.currentRow()
            if fila_actual < 0 or fila_actual >= len(self.actuaciones):
                QMessageBox.warning(self.main_window, "Advertencia", "Selecciona una actuación para borrar")
                return
            
            # Confirmar borrado
            actuacion = self.actuaciones[fila_actual]
            respuesta = QMessageBox.question(
                self.main_window, "Confirmar Borrado",
                f"¿Estás seguro de borrar la actuación?\n\n'{actuacion.get('actuacion', 'Sin nombre')}'",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Borrar de la lista
                self.actuaciones.pop(fila_actual)
                # Actualizar tabla
                self.actualizar_tabla_actuaciones()
                # Guardar cambios
                self.guardar_en_json()
                QMessageBox.information(self.main_window, "Éxito", "Actuación borrada correctamente")
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error borrando actuación: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Error borrando actuación: {e}")
    
    def borrar_factura(self):
        """Borrar factura seleccionada"""
        try:
            if not self.table_facturas:
                return
            
            fila_actual = self.table_facturas.currentRow()
            if fila_actual < 0 or fila_actual >= len(self.facturas):
                QMessageBox.warning(self.main_window, "Advertencia", "Selecciona una factura para borrar")
                return
            
            # Confirmar borrado
            factura = self.facturas[fila_actual]
            respuesta = QMessageBox.question(
                self.main_window, "Confirmar Borrado",
                f"¿Estás seguro de borrar la factura?\n\n'{factura.get('nombre', 'Sin nombre')}'",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                # Borrar de la lista
                self.facturas.pop(fila_actual)
                # Actualizar tabla
                self.actualizar_tabla_facturas()
                # Guardar cambios
                self.guardar_en_json()
                QMessageBox.information(self.main_window, "Éxito", "Factura borrada correctamente")
                self.actualizar_labels_presupuesto()
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error borrando factura: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Error borrando factura: {e}")
    def limpiar_proyecto_actual(self):
        """Limpiar proyecto actual y deshabilitar botones"""
        self.proyecto_actual = None
        self.ruta_carpeta_obra = None
        self.actuaciones = []
        self.facturas = []
        
        # Limpiar tablas
        if self.table_actuaciones:
            self.table_actuaciones.setRowCount(0)
        if self.table_facturas:
            self.table_facturas.setRowCount(0)
        
        # Deshabilitar botones
        self._limpiar_labels_presupuesto()
    
    def cargar_datos_desde_json(self, datos_proyecto: Dict[str, Any]):
        """Cargar actuaciones y facturas desde datos del proyecto"""
        self.actuaciones = datos_proyecto.get('actuaciones', [])
        self.facturas = datos_proyecto.get('facturas', [])
        
    def actualizar_labels_presupuesto(self):
        """Actualizar labels de presupuesto basado en datos actuales"""
        try:
            if not self.proyecto_actual:
                self._limpiar_labels_presupuesto()
                return
            
            # Obtener presupuesto de adjudicación desde el contract manager
            presupuesto_adjudicacion = self._obtener_presupuesto_adjudicacion()
            
            # Calcular total gastado (suma de todas las facturas)
            total_gastado = sum(factura.get('importe', 0.0) for factura in self.facturas)
            
            # Calcular disponible
            disponible = presupuesto_adjudicacion - total_gastado if presupuesto_adjudicacion > 0 else 0.0
            
            # Actualizar labels
            self._actualizar_label_presupuesto_total(presupuesto_adjudicacion)
            self._actualizar_label_presupuesto_gastado(total_gastado)
            self._actualizar_label_presupuesto_disponible(disponible)
            




            # Solo mostrar gráfica si hay al menos una factura
            if len(self.facturas) >= 1:

                self._actualizar_grafico_quesito(presupuesto_adjudicacion, total_gastado)
            else:

                self._mostrar_grafico_sin_datos()
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error actualizando presupuesto: {e}")

    def _obtener_presupuesto_adjudicacion(self) -> float:
        """Obtener presupuesto de adjudicación del contrato actual"""
        try:
            if not hasattr(self.main_window, 'contract_manager') or not self.main_window.contract_manager:
                return 0.0
            
            datos_contrato = self.main_window.contract_manager.get_current_contract_data()
            if not datos_contrato:
                return 0.0
            
            # Buscar en diferentes posibles campos
            campos_posibles = ['basePresupuesto', 'importe_adjudicacion', 'importe_licitacion', 'presupuesto']
            
            for campo in campos_posibles:
                valor = datos_contrato.get(campo, 0)
                if isinstance(valor, str):
                    try:
                        # Convertir de formato español a float
                        valor_limpio = valor.replace('.', '').replace(',', '.').replace('€', '').strip()
                        return float(valor_limpio)
                    except:
                        continue
                elif isinstance(valor, (int, float)) and valor > 0:
                    return float(valor)
            
            return 0.0
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error obteniendo presupuesto: {e}")
            return 0.0
    def copiar_archivos_pdf(self, archivos_originales, tipo_carpeta):
        """
        Copiar archivos PDF a la carpeta correspondiente del proyecto
        
        Args:
            archivos_originales: Lista de rutas de archivos originales
            tipo_carpeta: 'actuaciones' o 'facturas'
        
        Returns:
            Lista de rutas de archivos copiados
        """
        try:
            if not archivos_originales:
                return []
            
            # Obtener carpeta del proyecto
            carpeta_proyecto = self.obtener_carpeta_proyecto(crear_si_no_existe=True)
            
            if not carpeta_proyecto:
                print(f"[ActuacionesFacturas] ❌ No se pudo obtener carpeta del proyecto")
                return archivos_originales  # Devolver originales si no se puede copiar
            
            # Determinar carpeta destino
            if tipo_carpeta == 'actuaciones':
                carpeta_destino = os.path.join(carpeta_proyecto, "08-actuaciones")
            elif tipo_carpeta == 'facturas':
                carpeta_destino = os.path.join(carpeta_proyecto, "09-facturas")
            else:
                carpeta_destino = os.path.join(carpeta_proyecto, "10-otros")
            
            # Crear carpeta destino si no existe
            os.makedirs(carpeta_destino, exist_ok=True)
            
            archivos_copiados = []
            
            for archivo_original in archivos_originales:
                if not os.path.exists(archivo_original):
    
                    continue
                
                # Generar nombre único para evitar conflictos
                nombre_archivo = os.path.basename(archivo_original)
                nombre_base, extension = os.path.splitext(nombre_archivo)
                
                # Si el archivo ya existe, agregar timestamp
                archivo_destino = os.path.join(carpeta_destino, nombre_archivo)
                contador = 1
                
                while os.path.exists(archivo_destino):
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nuevo_nombre = f"{nombre_base}_{timestamp}_{contador}{extension}"
                    archivo_destino = os.path.join(carpeta_destino, nuevo_nombre)
                    contador += 1
                
                # Copiar archivo
                try:
                    import shutil
                    shutil.copy2(archivo_original, archivo_destino)
                    archivos_copiados.append(archivo_destino)
                    
                except Exception as e:
                    print(f"[ActuacionesFacturas] ❌ Error copiando {nombre_archivo}: {e}")
                    # Si no se puede copiar, usar el original
                    archivos_copiados.append(archivo_original)
            
            return archivos_copiados
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error general copiando archivos: {e}")
            # En caso de error, devolver archivos originales
            return archivos_originales
    def _actualizar_label_presupuesto_total(self, importe: float):
        """Actualizar label de presupuesto total"""
        if self.label_presupuesto_total:
            if importe > 0:
                texto = f"{importe:,.2f} €".replace(',', '.')
                self.label_presupuesto_total.setText(texto)
                self.label_presupuesto_total.setStyleSheet("color: black;")
            else:
                self.label_presupuesto_total.setText("— — —")
                self.label_presupuesto_total.setStyleSheet("color: gray;")

    def _actualizar_label_presupuesto_gastado(self, importe: float):
        """Actualizar label de presupuesto gastado"""
        if self.label_presupuesto_gastado:
            texto = f"{importe:,.2f} €".replace(',', '.')
            color = "red" if importe > 0 else "gray"
            self.label_presupuesto_gastado.setText(texto)
            self.label_presupuesto_gastado.setStyleSheet(f"color: {color};")

    def _actualizar_label_presupuesto_disponible(self, importe: float):
        """Actualizar label de presupuesto disponible"""
        if self.label_presupuesto_disponible:
            texto = f"{importe:,.2f} €".replace(',', '.')
            if importe > 0:
                color = "green"
            elif importe < 0:
                color = "red"
                texto = f"-{abs(importe):,.2f} €".replace(',', '.')
            else:
                color = "gray"
            
            self.label_presupuesto_disponible.setText(texto)
            self.label_presupuesto_disponible.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _limpiar_labels_presupuesto(self):
        """Limpiar labels cuando no hay proyecto"""
        labels = [self.label_presupuesto_total, self.label_presupuesto_gastado, self.label_presupuesto_disponible]
        for label in labels:
            if label:
                label.setText("— — —")
                label.setStyleSheet("color: gray;")
        self._mostrar_grafico_sin_datos()

    def _actualizar_grafico_quesito(self, presupuesto_total: float, presupuesto_gastado: float):
        """Actualizar gráfico de quesito QUE RELLENA TODO EL CUADRADO"""
        try:
            if not self.graphics_view:
                return
            
            # Limpiar
            if self.graphics_view.scene():
                self.graphics_view.scene().clear()
            
            # Si no hay presupuesto
            if presupuesto_total <= 0:
                self._mostrar_grafico_sin_datos()
                return
            
            # Calcular valores
            gastado = min(presupuesto_gastado, presupuesto_total)
            disponible = presupuesto_total - gastado
            exceso = max(0, presupuesto_gastado - presupuesto_total)
            
            # Crear serie
            series = QPieSeries()
            
            # ✅ ESTAS LÍNEAS HACEN QUE EL QUESITO SEA GIGANTE:
            series.setPieSize(0.95)  # 95% del espacio disponible
            series.setHoleSize(0.0)  # Sin agujero central
            
            # Agregar slices - SIEMPRE mostrar algo
            if disponible > 0:
                slice_disp = series.append("Disponible", disponible)
                if slice_disp is not None:
                    slice_disp.setBrush(QColor("#2ecc71"))
                    slice_disp.setLabelVisible(False)
            
            if gastado > 0:
                slice_gast = series.append("Gastado", gastado)
                if slice_gast is not None:
                    slice_gast.setBrush(QColor("#e74c3c"))
                    slice_gast.setLabelVisible(False)
            
            if exceso > 0:
                slice_exc = series.append("EXCESO", exceso)
                if slice_exc is not None:
                    slice_exc.setBrush(QColor("#9b59b6"))
                    slice_exc.setLabelVisible(False)
                    slice_exc.setExploded(True)
            
            # Si no hay gastado ni exceso, mostrar todo como disponible
            if gastado == 0 and exceso == 0 and disponible > 0:
                # El slice de disponible ya se agregó arriba
                pass

            elif gastado == 0 and exceso == 0 and disponible == 0:
                # Caso especial: sin presupuesto, agregar slice placeholder
                slice_placeholder = series.append("Sin datos", 1)
                if slice_placeholder is not None:
                    slice_placeholder.setBrush(QColor("#95a5a6"))
                    slice_placeholder.setLabelVisible(False)
            
            # Configurar chart para usar TODO el espacio
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            legend = chart.legend()
            if legend is not None:
                legend.hide()
            chart.setBackgroundBrush(QColor("white"))
            chart.setMargins(QMargins(0, 0, 0, 0))  # Sin márgenes
            chart.setPlotAreaBackgroundVisible(False)  # Sin área extra
            
            # ✅ CONFIGURAR PARA QUE USE TODO EL ESPACIO:
            chart.setContentsMargins(0, 0, 0, 0)  # Sin márgenes de contenido
            
            # Configurar chart view
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setStyleSheet("border: none; background: white; margin: 0px; padding: 0px;")
            chart_view.setContentsMargins(0, 0, 0, 0)  # Sin márgenes del view
            
            # Agregar a graphics view
            from PyQt5.QtWidgets import QGraphicsScene
            scene = QGraphicsScene()
            scene.addWidget(chart_view)
            self.graphics_view.setScene(scene)
            
            # ✅ CONFIGURAR GRAPHICS VIEW PARA USAR TODO EL ESPACIO:
            self.graphics_view.setContentsMargins(0, 0, 0, 0)
            self.graphics_view.setStyleSheet("border: none; background: white; margin: 0px; padding: 0px;")
            
            # Ajustar tamaño para llenar completamente
            self.graphics_view.fitInView(scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error en gráfico: {e}")
            self._mostrar_grafico_sin_datos()

    def _mostrar_grafico_sin_datos(self):
        """Mostrar gráfico cuando no hay datos - RELLENA TODO"""
        try:
            if not self.graphics_view:
                return
            
            # Gráfico simple gris
            series = QPieSeries()
            
            # ✅ CONFIGURAR TAMAÑO GIGANTE:
            series.setPieSize(0.95)  # 95% del espacio
            series.setHoleSize(0.0)  # Sin agujero
            
            slice_vacio = series.append("Sin datos", 1)
            if slice_vacio is not None:
                slice_vacio.setBrush(QColor("#ecf0f1"))
                slice_vacio.setLabelVisible(False)
            
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("")
            legend = chart.legend()
            if legend is not None:
                legend.hide()
            chart.setBackgroundBrush(QColor("white"))
            chart.setMargins(QMargins(0, 0, 0, 0))
            chart.setPlotAreaBackgroundVisible(False)
            chart.setContentsMargins(0, 0, 0, 0)  # Sin márgenes
            
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setStyleSheet("border: none; background: white; margin: 0px; padding: 0px;")
            chart_view.setContentsMargins(0, 0, 0, 0)
            
            from PyQt5.QtWidgets import QGraphicsScene
            scene = QGraphicsScene()
            scene.addWidget(chart_view)
            self.graphics_view.setScene(scene)
            
            self.graphics_view.setContentsMargins(0, 0, 0, 0)
            self.graphics_view.setStyleSheet("border: none; background: white; margin: 0px; padding: 0px;")
            self.graphics_view.fitInView(scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error gráfico vacío: {e}")


    def agregar_actuacion(self):
        """Agregar nueva actuación"""
        dialogo = DialogoActuacion(self.main_window)
        
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtener_datos()
            
            if not datos['actuacion']:
                QMessageBox.warning(self.main_window, "Error", "El campo 'Actuación' es obligatorio")
                return
            
            # Copiar archivos PDF
            datos['archivos_pdf'] = self.copiar_archivos_pdf(datos['archivos_pdf'], 'actuaciones')
            
            # Agregar a la lista
            self.actuaciones.append(datos)
            
            # Guardar en JSON
            self.guardar_en_json()
            
            # Actualizar tabla
            self.actualizar_tabla_actuaciones()
            
            QMessageBox.information(self.main_window, "Éxito", "Actuación agregada correctamente")
    
    def agregar_actuacion_mail(self):
        """Agregar nueva actuación con funcionalidad de email"""
        dialogo = DialogoActuacionMail(self.main_window)
        
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtener_datos()
            
            if not datos['actuacion']:
                QMessageBox.warning(self.main_window, "Error", "El campo 'Actuación' es obligatorio")
                return
            
            # Copiar archivos PDF
            datos['archivos_pdf'] = self.copiar_archivos_pdf(datos['archivos_pdf'], 'actuaciones')
            
            # Agregar a la lista
            self.actuaciones.append(datos)
            
            # Guardar en JSON
            self.guardar_en_json()
            
            # Actualizar tabla
            self.actualizar_tabla_actuaciones()
            
            # Enviar email si se proporcionó
            if datos.get('email') and datos.get('mensaje'):
                self.enviar_email_actuacion(datos)
            
            QMessageBox.information(self.main_window, "Éxito", "Actuación agregada y email enviado correctamente")
    
    def enviar_email_actuacion(self, datos):
        """Enviar email usando el gestor predeterminado del sistema"""
        try:
            email = datos['email']
            asunto = f"Actuación: {datos['actuacion']}"
            mensaje = datos['mensaje']
            
            # Crear mensaje completo con datos de la actuación
            mensaje_completo = f"""
Estimado/a destinatario/a,

{mensaje}

Detalles de la actuación:
- Actuación: {datos['actuacion']}
- Localidad: {datos['localidad']}
- GPED: {datos['gped']}
- Fecha: {datos['fecha_creacion'][:10]}

Saludos cordiales,
Sistema ADIF
"""
            
            # Crear URL mailto
            import urllib.parse
            mailto_url = f"mailto:{email}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(mensaje_completo)}"
            
            # Abrir cliente de email predeterminado
            webbrowser.open(mailto_url)
            
        except Exception as e:
            QMessageBox.warning(self.main_window, "Error", f"Error enviando email: {str(e)}")
    
    def agregar_factura(self):
        """Agregar nueva factura"""
        dialogo = DialogoFactura(self.main_window, actuaciones_disponibles=self.actuaciones)
        
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtener_datos()
            
            if not datos['nombre']:
                QMessageBox.warning(self.main_window, "Error", "El campo 'Nombre' es obligatorio")
                return
            
            # Copiar archivos PDF
            datos['archivos_pdf'] = self.copiar_archivos_pdf(datos['archivos_pdf'], 'facturas')
            
            # Agregar a la lista
            self.facturas.append(datos)
            
            # Actualizar facturas asociadas en actuaciones
            self.actualizar_asociaciones_actuaciones(datos)
            
            # Guardar en JSON
            self.guardar_en_json()
            
            # Actualizar tablas
            self.actualizar_tabla_facturas()
            self.actualizar_tabla_actuaciones()
            
            QMessageBox.information(self.main_window, "Éxito", "Factura agregada correctamente")
            self.actualizar_labels_presupuesto()
  
    def actualizar_asociaciones_actuaciones(self, datos_factura: Dict[str, Any]):
        """Actualizar asociaciones en actuaciones cuando se agrega una factura"""
        factura_id = datos_factura['id']
        
        for actuacion in self.actuaciones:
            if actuacion['id'] in datos_factura['actuaciones_asociadas']:
                if 'facturas_asociadas' not in actuacion:
                    actuacion['facturas_asociadas'] = []
                
                if factura_id not in actuacion['facturas_asociadas']:
                    actuacion['facturas_asociadas'].append(factura_id)
    
    def actualizar_tabla_actuaciones(self):
        """Actualizar tabla de actuaciones"""



        
        if not self.table_actuaciones:

            return
        
        self.table_actuaciones.setRowCount(len(self.actuaciones))
        
        for row, actuacion in enumerate(self.actuaciones):
            # Actuación
            self.table_actuaciones.setItem(row, 0, QTableWidgetItem(actuacion.get('actuacion', '')))
            
            # Localidad
            self.table_actuaciones.setItem(row, 1, QTableWidgetItem(actuacion.get('localidad', '')))
            
            # GPED
            self.table_actuaciones.setItem(row, 2, QTableWidgetItem(actuacion.get('gped', '')))
            
            # Facturas asociadas (contar)
            num_facturas = len(actuacion.get('facturas_asociadas', []))
            self.table_actuaciones.setItem(row, 3, QTableWidgetItem(str(num_facturas)))
            
            # Acciones (botones)
            btn_acciones = QPushButton("⚙️ Acciones")
            self.table_actuaciones.setCellWidget(row, 4, btn_acciones)
    
    def cambiar_pdfs_factura(self, fila: int):
        """Cambiar PDFs de una factura"""
        try:
            if fila < 0 or fila >= len(self.facturas):
                return
            
            factura = self.facturas[fila]
            
            # Abrir diálogo para seleccionar nuevos PDFs
            archivos, _ = QFileDialog.getOpenFileNames(
                self.main_window, "Seleccionar nuevos PDFs", "", "Archivos PDF (*.pdf)"
            )
            
            if archivos:
                # Copiar nuevos archivos
                nuevos_pdfs = self.copiar_archivos_pdf(archivos, 'facturas')
                # Actualizar datos
                factura['archivos_pdf'] = nuevos_pdfs
                # Guardar cambios
                self.guardar_en_json()
                QMessageBox.information(self.main_window, "Éxito", f"PDFs actualizados: {len(nuevos_pdfs)} archivos")
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error cambiando PDFs factura: {e}")
    
    def abrir_pdf_seleccionado(self, lista_widget, pdfs_list):
        """Abrir PDF seleccionado en la lista"""
        try:
            fila_actual = lista_widget.currentRow()
            if fila_actual < 0 or fila_actual >= len(pdfs_list):
                QMessageBox.warning(self.main_window, "Advertencia", "Selecciona un PDF para abrir")
                return
            
            ruta_pdf = pdfs_list[fila_actual]
            
            if os.path.exists(ruta_pdf):
                # Abrir PDF con aplicación por defecto
                import subprocess
                import platform
                
                sistema = platform.system()
                if sistema == "Windows":
                    os.startfile(ruta_pdf)
                elif sistema == "Darwin":  # macOS
                    subprocess.run(["open", ruta_pdf])
                else:  # Linux
                    subprocess.run(["xdg-open", ruta_pdf])
                    
            else:
                QMessageBox.warning(self.main_window, "Error", f"No se encontró el archivo:\n{ruta_pdf}")
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error abriendo PDF: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Error abriendo PDF: {e}")
    
    def guardar_en_json(self):
        """Guardar datos en JSON del proyecto"""
        try:
            if not self.proyecto_actual:

                return
            
            # Acceder al controlador JSON principal
            if hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json:
                gestor = self.main_window.controlador_json.gestor
                
                if gestor:
                    
                    # Obtener datos actuales del proyecto
                    datos_proyecto = gestor.cargar_datos_obra(self.proyecto_actual)
                    
                    if not datos_proyecto:
                        print(f"[ActuacionesFacturas] ❌ No se pudieron cargar datos del proyecto: {self.proyecto_actual}")
                        return
                    
                    # Actualizar con nuevos datos
                    datos_proyecto['actuaciones'] = self.actuaciones
                    datos_proyecto['facturas'] = self.facturas
                    
                    # CRÍTICO: Actualizar los datos en el gestor
                    gestor.datos['obras'][self.proyecto_actual] = datos_proyecto
                    
                    # Guardar en el gestor
                    if gestor.guardar_datos():
                        pass  # JSON guardado exitosamente
                    else:
                        print(f"[ActuacionesFacturas] ❌ Error guardando archivo JSON")
                else:
                    print("[ActuacionesFacturas] ❌ Gestor no disponible")
            else:
                print("[ActuacionesFacturas] ❌ Controlador JSON no disponible")
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error guardando en JSON: {e}")
            import traceback
            traceback.print_exc()
    def actualizar_tabla_actuaciones(self):
        """Actualizar tabla de actuaciones con botones modernos."""
        if not self.table_actuaciones:
            return

        self.table_actuaciones.setRowCount(len(self.actuaciones))
        self.table_actuaciones.setColumnWidth(4, 200)
        estilo_boton = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #47cf73, stop:1 #209150);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 0px;
            margin-left: 8px;
            margin-right: 8px;
        }
        QPushButton:hover {
            background-color: #58d68d;
            color: #117a65;
        }
        QPushButton:pressed {
            background-color: #138d75;
            color: #d5f5e3;
        }
        """

        estilo_boton_azul = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5dade2, stop:1 #2471a3);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 0px;
            margin-left: 8px;
            margin-right: 8px;
        }
        QPushButton:hover {
            background-color: #85c1e9;
            color: #154360;
        }
        QPushButton:pressed {
            background-color: #21618c;
            color: #d6eaf8;
        }
        """

        for row, actuacion in enumerate(self.actuaciones):
            self.table_actuaciones.setItem(row, 0, QTableWidgetItem(actuacion.get('actuacion', '')))
            self.table_actuaciones.setItem(row, 1, QTableWidgetItem(actuacion.get('localidad', '')))
            self.table_actuaciones.setItem(row, 2, QTableWidgetItem(actuacion.get('gped', '')))
            num_facturas = len(actuacion.get('facturas_asociadas', []))
            self.table_actuaciones.setItem(row, 3, QTableWidgetItem(str(num_facturas)))
            self.table_actuaciones.setRowHeight(row, 100)

            # -- Acciones: botones modernos --
            widget_acciones = QWidget()
            layout_acciones = QVBoxLayout(widget_acciones)
            layout_acciones.setContentsMargins(0, 6, 0, 6)
            layout_acciones.setSpacing(8)

            # Botón Ver PDFs (verde)
            btn_ver_pdf = QPushButton("📄 Ver PDF")
            btn_ver_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn_ver_pdf.setStyleSheet(estilo_boton)
            btn_ver_pdf.clicked.connect(lambda checked, r=row: self.ver_pdfs_actuacion(r))
            layout_acciones.addWidget(btn_ver_pdf)

            # Botón Cambiar PDFs (azul)
            btn_cambiar_pdf = QPushButton("🔄 Cambiar PDF")
            btn_cambiar_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn_cambiar_pdf.setStyleSheet(estilo_boton_azul)
            btn_cambiar_pdf.clicked.connect(lambda checked, r=row: self.cambiar_pdfs_actuacion(r))
            layout_acciones.addWidget(btn_cambiar_pdf)

            self.table_actuaciones.setCellWidget(row, 4, widget_acciones)

    def actualizar_tabla_facturas(self):
        """Actualizar tabla de facturas con botones modernos (mismos textos que antes)."""
        if not self.table_facturas:
            return

        self.table_facturas.setRowCount(len(self.facturas))
        self.table_facturas.setColumnWidth(3, 200)  # Ajusta el ancho de la columna de botones

        estilo_boton_ver = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #47cf73, stop:1 #209150);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 0px;
            margin-left: 8px;
            margin-right: 8px;
        }
        QPushButton:hover {
            background-color: #58d68d;
            color: #117a65;
        }
        QPushButton:pressed {
            background-color: #138d75;
            color: #d5f5e3;
        }
        """

        estilo_boton_cambiar = """
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5dade2, stop:1 #2471a3);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: bold;
            padding: 10px 0px;
            margin-left: 8px;
            margin-right: 8px;
        }
        QPushButton:hover {
            background-color: #85c1e9;
            color: #154360;
        }
        QPushButton:pressed {
            background-color: #21618c;
            color: #d6eaf8;
        }
        """

        for row, factura in enumerate(self.facturas):
            self.table_facturas.setItem(row, 0, QTableWidgetItem(factura.get('nombre', '')))
            importe = factura.get('importe', 0.0)
            self.table_facturas.setItem(row, 1, QTableWidgetItem(f"{importe:.2f} €"))
            num_actuaciones = len(factura.get('actuaciones_asociadas', []))
            self.table_facturas.setItem(row, 2, QTableWidgetItem(str(num_actuaciones)))
            self.table_facturas.setRowHeight(row, 100)

            # -- Acciones: botones modernos (mismos textos) --
            widget_acciones = QWidget()
            layout_acciones = QVBoxLayout(widget_acciones)
            layout_acciones.setContentsMargins(0, 6, 0, 6)
            layout_acciones.setSpacing(8)

            # Botón Ver PDFs (verde, mismo texto)
            btn_ver_pdf = QPushButton("📄 Ver")
            btn_ver_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn_ver_pdf.setStyleSheet(estilo_boton_ver)
            btn_ver_pdf.clicked.connect(lambda checked, r=row: self.ver_pdfs_factura(r))
            layout_acciones.addWidget(btn_ver_pdf)

            # Botón Cambiar PDFs (azul, mismo texto)
            btn_cambiar_pdf = QPushButton("🔄 Cambiar")
            btn_cambiar_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn_cambiar_pdf.setStyleSheet(estilo_boton_cambiar)
            btn_cambiar_pdf.clicked.connect(lambda checked, r=row: self.cambiar_pdfs_factura(r))
            layout_acciones.addWidget(btn_cambiar_pdf)

            self.table_facturas.setCellWidget(row, 3, widget_acciones)

    def ver_pdfs_actuacion(self, fila: int):
        """Ver PDFs de una actuación"""
        try:
            if fila < 0 or fila >= len(self.actuaciones):
                return
            
            actuacion = self.actuaciones[fila]
            pdfs = actuacion.get('archivos_pdf', [])
            
            if not pdfs:
                QMessageBox.information(self.main_window, "Sin PDFs", "Esta actuación no tiene PDFs asociados")
                return
            
            # Mostrar lista de PDFs y permitir abrir
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
            
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle(f"PDFs - {actuacion.get('actuacion', 'Actuación')}")
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            lista = QListWidget()
            for pdf in pdfs:
                nombre = os.path.basename(pdf)
                lista.addItem(f"📄 {nombre}")
            layout.addWidget(lista)
            
            btn_layout = QHBoxLayout()
            btn_abrir = QPushButton("🔍 Abrir Seleccionado")
            btn_abrir.clicked.connect(lambda: self.abrir_pdf_seleccionado(lista, pdfs))
            btn_cerrar = QPushButton("❌ Cerrar")
            btn_cerrar.clicked.connect(dialog.close)
            
            btn_layout.addWidget(btn_abrir)
            btn_layout.addWidget(btn_cerrar)
            layout.addLayout(btn_layout)
            
            dialog.exec_()
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error viendo PDFs actuación: {e}")
    
    def ver_pdfs_factura(self, fila: int):
        """Ver PDFs de una factura"""
        try:
            if fila < 0 or fila >= len(self.facturas):
                return
            
            factura = self.facturas[fila]
            pdfs = factura.get('archivos_pdf', [])
            
            if not pdfs:
                QMessageBox.information(self.main_window, "Sin PDFs", "Esta factura no tiene PDFs asociados")
                return
            
            # Mostrar lista de PDFs y permitir abrir
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
            
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle(f"PDFs - {factura.get('nombre', 'Factura')}")
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            lista = QListWidget()
            for pdf in pdfs:
                nombre = os.path.basename(pdf)
                lista.addItem(f"📄 {nombre}")
            layout.addWidget(lista)
            
            btn_layout = QHBoxLayout()
            btn_abrir = QPushButton("🔍 Abrir Seleccionado")
            btn_abrir.clicked.connect(lambda: self.abrir_pdf_seleccionado(lista, pdfs))
            btn_cerrar = QPushButton("❌ Cerrar")
            btn_cerrar.clicked.connect(dialog.close)
            
            btn_layout.addWidget(btn_abrir)
            btn_layout.addWidget(btn_cerrar)
            layout.addLayout(btn_layout)
            
            dialog.exec_()
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error viendo PDFs factura: {e}")
    
    def cambiar_pdfs_actuacion(self, fila: int):
        """Cambiar PDFs de una actuación"""
        try:
            if fila < 0 or fila >= len(self.actuaciones):
                return
            
            actuacion = self.actuaciones[fila]
            
            # Abrir diálogo para seleccionar nuevos PDFs
            archivos, _ = QFileDialog.getOpenFileNames(
                self.main_window, "Seleccionar nuevos PDFs", "", "Archivos PDF (*.pdf)"
            )
            
            if archivos:
                # Copiar nuevos archivos
                nuevos_pdfs = self.copiar_archivos_pdf(archivos, 'actuaciones')
                # Actualizar datos
                actuacion['archivos_pdf'] = nuevos_pdfs
                # Guardar cambios
                self.guardar_en_json()
                QMessageBox.information(self.main_window, "Éxito", f"PDFs actualizados: {len(nuevos_pdfs)} archivos")
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error cambiando PDFs actuación: {e}")
    
    def cambiar_pdfs_factura_simple(self, fila: int):
        """Cambiar PDFs de una factura (versión simple, renombrada para evitar duplicidad)"""

        if fila < 0 or fila >= len(self.facturas):
            return
        
        factura = self.facturas[fila]
    def editar_actuacion_doble_clic(self, row, column):
        """Editar actuación por doble clic"""
        try:
            # Verificar que la fila es válida
            if row < 0 or row >= len(self.actuaciones):
                print(f"[ActuacionesFacturas] ⚠️ Fila inválida: {row}")
                return
            
            # No permitir edición en la columna de acciones (columna 4)
            if column == 4:  # Columna de acciones
                print("[ActuacionesFacturas] ℹ️ Doble clic en columna de acciones ignorado")
                return
            

            
            # Obtener datos de la actuación
            actuacion_data = self.actuaciones[row].copy()
            
            # Crear diálogo en modo edición
            dialogo = DialogoActuacion(self.main_window, actuacion_data)
            dialogo.setWindowTitle("Editar Actuación")
            
            # Ejecutar diálogo
            if dialogo.exec_() == QDialog.Accepted:
                datos_actualizados = dialogo.obtener_datos()
                
                if not datos_actualizados['actuacion']:
                    QMessageBox.warning(self.main_window, "Error", "El campo 'Actuación' es obligatorio")
                    return
                
                # Conservar datos importantes del original
                datos_actualizados['id'] = actuacion_data['id']  # Mantener ID original
                datos_actualizados['fecha_creacion'] = actuacion_data['fecha_creacion']  # Mantener fecha original
                datos_actualizados['facturas_asociadas'] = actuacion_data.get('facturas_asociadas', [])  # Mantener asociaciones
                
                # Copiar archivos PDF si hay nuevos
                if datos_actualizados['archivos_pdf'] != actuacion_data.get('archivos_pdf', []):
                    datos_actualizados['archivos_pdf'] = self.copiar_archivos_pdf(
                        datos_actualizados['archivos_pdf'], 'actuaciones'
                    )
                
                # Actualizar en la lista
                self.actuaciones[row] = datos_actualizados
                
                # Guardar cambios
                self.guardar_en_json()
                
                # Actualizar tabla
                self.actualizar_tabla_actuaciones()
                
                QMessageBox.information(self.main_window, "Éxito", "Actuación actualizada correctamente")
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error editando actuación: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Error editando actuación: {e}")


    def editar_factura_doble_clic(self, row, column):
        """Editar factura por doble clic"""
        try:
            # Verificar que la fila es válida
            if row < 0 or row >= len(self.facturas):
                print(f"[ActuacionesFacturas] ⚠️ Fila inválida: {row}")
                return
            
            # No permitir edición en la columna de acciones (columna 3)
            if column == 3:  # Columna de acciones
                print("[ActuacionesFacturas] ℹ️ Doble clic en columna de acciones ignorado")
                return
            

            
            # Obtener datos de la factura
            factura_data = self.facturas[row].copy()
            
            # Crear diálogo en modo edición
            dialogo = DialogoFactura(self.main_window, factura_data, self.actuaciones)
            dialogo.setWindowTitle("Editar Factura")
            
            # Ejecutar diálogo
            if dialogo.exec_() == QDialog.Accepted:
                datos_actualizados = dialogo.obtener_datos()
                
                if not datos_actualizados['nombre']:
                    QMessageBox.warning(self.main_window, "Error", "El campo 'Nombre' es obligatorio")
                    return
                
                # Conservar datos importantes del original
                datos_actualizados['id'] = factura_data['id']  # Mantener ID original
                datos_actualizados['fecha_creacion'] = factura_data['fecha_creacion']  # Mantener fecha original
                
                # Copiar archivos PDF si hay nuevos
                if datos_actualizados['archivos_pdf'] != factura_data.get('archivos_pdf', []):
                    datos_actualizados['archivos_pdf'] = self.copiar_archivos_pdf(
                        datos_actualizados['archivos_pdf'], 'facturas'
                    )
                
                # Obtener asociaciones anteriores para limpiar referencias
                asociaciones_anteriores = set(factura_data.get('actuaciones_asociadas', []))
                asociaciones_nuevas = set(datos_actualizados['actuaciones_asociadas'])
                
                # Limpiar referencias de actuaciones que ya no están asociadas
                for actuacion_id in asociaciones_anteriores - asociaciones_nuevas:
                    for actuacion in self.actuaciones:
                        if actuacion['id'] == actuacion_id:
                            facturas_asociadas = actuacion.get('facturas_asociadas', [])
                            if factura_data['id'] in facturas_asociadas:
                                facturas_asociadas.remove(factura_data['id'])
                            break
                
                # Actualizar en la lista
                self.facturas[row] = datos_actualizados
                
                # Actualizar asociaciones en actuaciones
                self.actualizar_asociaciones_actuaciones(datos_actualizados)
                
                # Guardar cambios
                self.guardar_en_json()
                
                # Actualizar tablas
                self.actualizar_tabla_facturas()
                self.actualizar_tabla_actuaciones()
                
                QMessageBox.information(self.main_window, "Éxito", "Factura actualizada correctamente")
                self.actualizar_labels_presupuesto()
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error editando factura: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Error editando factura: {e}")


    # (Método cargar_datos eliminado porque no corresponde a ControladorActuacionesFacturas)
        


    def limpiar_asociaciones_factura_actuaciones(self, factura_id: str, actuaciones_anteriores: List[str]):
        """Limpiar asociaciones de factura en actuaciones"""
        try:
            for actuacion_id in actuaciones_anteriores:
                for actuacion in self.actuaciones:
                    if actuacion['id'] == actuacion_id:
                        facturas_asociadas = actuacion.get('facturas_asociadas', [])
                        if factura_id in facturas_asociadas:
                            facturas_asociadas.remove(factura_id)

                        break
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error limpiando asociaciones: {e}")

    def crear_carpeta_proyecto(self):
        """Crear carpeta del proyecto actual si no existe"""
        try:
            carpeta = self.obtener_carpeta_proyecto(crear_si_no_existe=True)
            if carpeta:
                return carpeta
            else:
                print(f"[ActuacionesFacturas] ❌ No se pudo crear/obtener carpeta")
                return None
                
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error creando carpeta: {e}")
            return None

    def _ejecutar_con_carpeta(self, accion_callback, nombre_accion="Acción"):
        """
        Ejecutar una acción que requiere carpeta, creándola si es necesario
        """
        try:
            if not self.proyecto_actual:
                print(f"[ActuacionesFacturas] ⚠️ {nombre_accion}: No hay proyecto actual")
                return
            
            # Obtener/crear carpeta
            carpeta = self.obtener_carpeta_proyecto(crear_si_no_existe=True)
            
            if not carpeta:
                print(f"[ActuacionesFacturas] ❌ {nombre_accion}: No se pudo obtener carpeta")
                return
            
            # Ejecutar acción
            accion_callback(carpeta)
            
        except Exception as e:
            print(f"[ActuacionesFacturas] ❌ Error en {nombre_accion}: {e}")
            return

    def abrir_carpeta_actuaciones(self):
        """Abrir carpeta de actuaciones en el explorador"""
        def abrir_carpeta(carpeta_path):
            actuaciones_path = os.path.join(carpeta_path, "08-actuaciones")
            if os.path.exists(actuaciones_path):
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.Popen(['explorer', actuaciones_path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(['open', actuaciones_path])
                else:  # Linux
                    subprocess.Popen(['xdg-open', actuaciones_path])
            else:
                print(f"[ActuacionesFacturas] ❌ Carpeta actuaciones no existe")
        
        self._ejecutar_con_carpeta(abrir_carpeta, "Abrir Carpeta")
