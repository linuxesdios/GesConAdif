#!/usr/bin/env python3
"""
Interfaz de doble tabla con flechas para importar/exportar empresas desde/hacia Excel
Incluye funciones de eventos para integración con el sistema principal
"""

from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
                            QMessageBox, QHeaderView, QFileDialog, QMenu)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from typing import List, Dict, Optional
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class VentanaDobleTabla(QDialog):
    """Ventana con doble tabla y flechas para gestionar empresas desde/hacia Excel"""
    
    def __init__(self, empresas_aplicacion: List[Dict], archivo_excel: str = None, modo="importar"):
        super().__init__()
        
        self.empresas_aplicacion = empresas_aplicacion.copy()
        self.archivo_excel = archivo_excel
        self.empresas_excel = []
        self.modo = modo  # "exportar" o "importar"
        
        # Cargar empresas desde Excel si se proporciona archivo
        if archivo_excel and os.path.exists(archivo_excel):
            self.empresas_excel = self.leer_empresas_excel(archivo_excel)
        
        self.initUI()
        self.cargar_datos()
    
    def leer_empresas_excel(self, archivo_excel: str) -> List[Dict]:
        """Lee empresas desde archivo Excel"""
        try:
            # Intentar leer el Excel
            df = pd.read_excel(archivo_excel, engine='openpyxl')
            
            # Mapear columnas del Excel a nuestros campos
            # Buscar columnas que contengan estos términos
            columnas_mapeadas = {}
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'nombre' in col_lower or 'empresa' in col_lower or 'razón' in col_lower:
                    columnas_mapeadas['nombre'] = col
                elif 'nif' in col_lower or 'cif' in col_lower or 'rfc' in col_lower:
                    columnas_mapeadas['nif'] = col
                elif 'email' in col_lower or 'correo' in col_lower or 'mail' in col_lower:
                    columnas_mapeadas['email'] = col
                elif 'contacto' in col_lower or 'teléfono' in col_lower or 'telefono' in col_lower:
                    columnas_mapeadas['contacto'] = col
            
            empresas = []
            for _, row in df.iterrows():
                empresa = {
                    'nombre': str(row.get(columnas_mapeadas.get('nombre', ''), '')).strip(),
                    'nif': str(row.get(columnas_mapeadas.get('nif', ''), '')).strip(),
                    'email': str(row.get(columnas_mapeadas.get('email', ''), '')).strip(),
                    'contacto': str(row.get(columnas_mapeadas.get('contacto', ''), '')).strip()
                }
                
                # Solo agregar si tiene al menos nombre o NIF
                if empresa['nombre'] or empresa['nif']:
                    empresas.append(empresa)
            
            logger.info(f"Leídas {len(empresas)} empresas desde {os.path.basename(archivo_excel)}")
            return empresas
            
        except Exception as e:
            QMessageBox.warning(self, "Error leyendo Excel", 
                              f"No se pudo leer el archivo Excel:\n{str(e)}")
            logger.error(f"Error leyendo {archivo_excel}: {e}")
            return []
    
    def guardar_empresas_excel(self, empresas: List[Dict], archivo_excel: str) -> bool:
        """Guarda empresas en archivo Excel"""
        try:
            # Crear DataFrame con las empresas
            data = {
                'Nombre Empresa': [emp.get('nombre', '') for emp in empresas],
                'NIF/CIF': [emp.get('nif', '') for emp in empresas],
                'Email': [emp.get('email', '') for emp in empresas],
                'Contacto': [emp.get('contacto', '') for emp in empresas]
            }
            
            df = pd.DataFrame(data)
            
            # Guardar en Excel
            df.to_excel(archivo_excel, index=False, engine='openpyxl')
            
            logger.info(f"Guardadas {len(empresas)} empresas en {os.path.basename(archivo_excel)}")
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Error guardando Excel", 
                              f"No se pudo guardar el archivo Excel:\n{str(e)}")
            logger.error(f"Error guardando {archivo_excel}: {e}")
            return False
    
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de ventana
        self.setWindowTitle(f"{'Exportar hacia' if self.modo == 'exportar' else 'Importar desde'} Excel - Gestión de Empresas")
        self.setGeometry(100, 100, 1400, 700)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel(f"Gestión de Empresas - {'Exportación hacia' if self.modo == 'exportar' else 'Importación desde'} Excel")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            color: #1565c0;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(titulo)
        
        # Información del archivo Excel
        if self.archivo_excel:
            info_archivo = QLabel(f"Archivo: {os.path.basename(self.archivo_excel)}")
            info_archivo.setStyleSheet("""
                background-color: #f0f0f0;
                padding: 8px;
                border-radius: 3px;
                color: #333;
                font-size: 11px;
            """)
            main_layout.addWidget(info_archivo)
        
        # Instrucciones
        if self.modo == "exportar":
            instrucciones = """EXPORTAR A EXCEL: Izquierda: Empresas en la aplicación | Derecha: Empresas para exportar | Use las flechas para seleccionar"""
        else:
            instrucciones = """IMPORTAR DESDE EXCEL: Izquierda: Empresas en la aplicación | Derecha: Empresas del Excel | Use las flechas para seleccionar"""
        
        label_instrucciones = QLabel(instrucciones)
        label_instrucciones.setStyleSheet("""
            background-color: #fff3e0;
            padding: 10px;
            border-radius: 5px;
            color: #e65100;
            font-size: 11px;
        """)
        main_layout.addWidget(label_instrucciones)
        
        # Layout principal con las dos tablas
        tablas_layout = QHBoxLayout()
        
        # === TABLA IZQUIERDA ===
        left_layout = QVBoxLayout()
        
        # Título tabla izquierda
        titulo_izq = QLabel("Empresas en la Aplicación")
        titulo_izq.setFont(QFont("Arial", 12, QFont.Bold))
        titulo_izq.setStyleSheet("color: #2e7d32; padding: 5px;")
        left_layout.addWidget(titulo_izq)
        
        # Tabla izquierda
        self.tabla_izquierda = QTableWidget()
        self.tabla_izquierda.setColumnCount(4)
        self.tabla_izquierda.setHorizontalHeaderLabels(['Nombre', 'NIF/CIF', 'Email', 'Contacto'])
        self.tabla_izquierda.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_izquierda.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_izquierda.setAlternatingRowColors(True)
        self.tabla_izquierda.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 2px solid #28a745;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
        left_layout.addWidget(self.tabla_izquierda)
        
        tablas_layout.addLayout(left_layout)
        
        # === BOTONES DE FLECHAS ===
        flechas_layout = QVBoxLayout()
        flechas_layout.addStretch()
        
        # Mover a derecha
        if self.modo == "exportar":
            texto_btn = "Exportar"
            tooltip = "Añadir empresa seleccionada para exportar a Excel"
        else:
            texto_btn = "Importar"
            tooltip = "Importar empresa seleccionada desde Excel"
            
        self.btn_mover_derecha = QPushButton(f"▶\n{texto_btn}")
        self.btn_mover_derecha.setFixedSize(80, 60)
        self.btn_mover_derecha.clicked.connect(self.mover_a_derecha)
        self.btn_mover_derecha.setToolTip(tooltip)
        self.btn_mover_derecha.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        flechas_layout.addWidget(self.btn_mover_derecha)
        
        # Mover todas a derecha
        self.btn_mover_todas_derecha = QPushButton("⩸\nTodas")
        self.btn_mover_todas_derecha.setFixedSize(80, 50)
        self.btn_mover_todas_derecha.clicked.connect(self.mover_todas_derecha)
        self.btn_mover_todas_derecha.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        flechas_layout.addWidget(self.btn_mover_todas_derecha)
        
        # Separador
        flechas_layout.addWidget(QLabel(""))
        
        # Quitar todas
        self.btn_mover_todas_izquierda = QPushButton("⪷\nQuitar\nTodas")
        self.btn_mover_todas_izquierda.setFixedSize(80, 60)
        self.btn_mover_todas_izquierda.clicked.connect(self.mover_todas_izquierda)
        self.btn_mover_todas_izquierda.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        flechas_layout.addWidget(self.btn_mover_todas_izquierda)
        
        # Quitar seleccionada
        self.btn_mover_izquierda = QPushButton("◀\nQuitar")
        self.btn_mover_izquierda.setFixedSize(80, 50)
        self.btn_mover_izquierda.clicked.connect(self.mover_a_izquierda)
        self.btn_mover_izquierda.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        flechas_layout.addWidget(self.btn_mover_izquierda)
        
        flechas_layout.addStretch()
        tablas_layout.addLayout(flechas_layout)
        
        # === TABLA DERECHA ===
        right_layout = QVBoxLayout()
        
        # Título tabla derecha
        if self.modo == "exportar":
            titulo_der = QLabel("Para Exportar a Excel")
        else:
            titulo_der = QLabel("Empresas en Excel")
        titulo_der.setFont(QFont("Arial", 12, QFont.Bold))
        titulo_der.setStyleSheet("color: #d32f2f; padding: 5px;")
        right_layout.addWidget(titulo_der)
        
        # Tabla derecha
        self.tabla_derecha = QTableWidget()
        self.tabla_derecha.setColumnCount(4)
        self.tabla_derecha.setHorizontalHeaderLabels(['Nombre', 'NIF/CIF', 'Email', 'Contacto'])
        self.tabla_derecha.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_derecha.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_derecha.setAlternatingRowColors(True)
        self.tabla_derecha.setStyleSheet("""
            QTableWidget {
                background-color: #fff5f5;
                border: 2px solid #dc3545;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
        right_layout.addWidget(self.tabla_derecha)
        
        tablas_layout.addLayout(right_layout)
        main_layout.addLayout(tablas_layout)
        
        # === BOTONES INFERIORES ===
        botones_layout = QHBoxLayout()
        
        # Estadísticas
        self.label_stats = QLabel("")
        self.label_stats.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        botones_layout.addWidget(self.label_stats)
        
        botones_layout.addStretch()
        
        # Seleccionar archivo Excel (solo modo exportar)
        if self.modo == "exportar":
            btn_seleccionar_excel = QPushButton("Seleccionar Excel")
            btn_seleccionar_excel.setFixedSize(130, 40)
            btn_seleccionar_excel.clicked.connect(self.seleccionar_archivo_excel)
            btn_seleccionar_excel.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            botones_layout.addWidget(btn_seleccionar_excel)
        
        # Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(120, 40)
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        botones_layout.addWidget(btn_cancelar)
        
        # Ejecutar acción
        if self.modo == "exportar":
            texto_ejecutar = "Exportar a Excel"
        else:
            texto_ejecutar = "Importar a App"
            
        self.btn_ejecutar = QPushButton(texto_ejecutar)
        self.btn_ejecutar.setFixedSize(140, 40)
        self.btn_ejecutar.clicked.connect(self.ejecutar_accion)
        self.btn_ejecutar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        botones_layout.addWidget(self.btn_ejecutar)
        
        main_layout.addLayout(botones_layout)
    
    def seleccionar_archivo_excel(self):
        """Permite seleccionar archivo Excel para exportar"""
        archivo, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Excel como...", 
            "empresas_exportadas.xlsx",
            "Archivos Excel (*.xlsx);;Todos los archivos (*)"
        )
        
        if archivo:
            self.archivo_excel = archivo
            self.setWindowTitle(f"Exportar hacia Excel - {os.path.basename(archivo)}")
    
    def cargar_datos(self):
        """Carga los datos en las tablas según el modo"""
        if self.modo == "exportar":
            self.llenar_tabla(self.tabla_izquierda, self.empresas_aplicacion)
            self.llenar_tabla(self.tabla_derecha, [])
        else:
            self.llenar_tabla(self.tabla_izquierda, self.empresas_aplicacion)
            self.llenar_tabla(self.tabla_derecha, self.empresas_excel)
        
        self.actualizar_estadisticas()
    
    def llenar_tabla(self, tabla: QTableWidget, empresas: List[Dict]):
        """Llena una tabla con la lista de empresas"""
        tabla.setRowCount(len(empresas))
        
        for fila, empresa in enumerate(empresas):
            tabla.setItem(fila, 0, QTableWidgetItem(empresa.get('nombre', '')))
            tabla.setItem(fila, 1, QTableWidgetItem(empresa.get('nif', '')))
            tabla.setItem(fila, 2, QTableWidgetItem(empresa.get('email', '')))
            tabla.setItem(fila, 3, QTableWidgetItem(empresa.get('contacto', '')))
    
    def mover_a_derecha(self):
        """Mueve empresas seleccionadas de izquierda a derecha"""
        if self.modo == "exportar":
            self._mover_seleccionadas(self.tabla_izquierda, self.tabla_derecha, "añadir para exportar")
        else:
            self._mover_seleccionadas(self.tabla_derecha, self.tabla_izquierda, "importar")
    
    def mover_a_izquierda(self):
        """Quita empresas seleccionadas de la tabla derecha"""
        if self.modo == "exportar":
            self._quitar_seleccionadas(self.tabla_derecha, "lista de exportación")
        else:
            self._mover_seleccionadas(self.tabla_izquierda, self.tabla_derecha, "quitar de aplicación")
    
    def mover_todas_derecha(self):
        """Mueve todas las empresas de izquierda a derecha"""
        if self.modo == "exportar":
            self._mover_todas(self.tabla_izquierda, self.tabla_derecha, "exportar")
        else:
            self._mover_todas(self.tabla_derecha, self.tabla_izquierda, "importar")
    
    def mover_todas_izquierda(self):
        """Quita todas las empresas de la tabla derecha"""
        if self.modo == "exportar":
            self._vaciar_tabla(self.tabla_derecha)
        else:
            self._vaciar_tabla(self.tabla_izquierda)
        self.actualizar_estadisticas()
    
    def _mover_seleccionadas(self, tabla_origen: QTableWidget, tabla_destino: QTableWidget, accion: str):
        """Mueve empresas seleccionadas entre tablas"""
        filas_seleccionadas = tabla_origen.selectionModel().selectedRows()
        
        if not filas_seleccionadas:
            QMessageBox.warning(self, "Sin selección", "Seleccione una o más empresas")
            return
        
        empresas_origen = self.obtener_empresas_tabla(tabla_origen)
        empresas_destino = self.obtener_empresas_tabla(tabla_destino)
        
        empresas_movidas = 0
        for index in sorted(filas_seleccionadas, reverse=True):
            fila = index.row()
            if fila < len(empresas_origen):
                empresa = empresas_origen[fila]
                
                if not self.empresa_existe(empresa, empresas_destino):
                    empresas_destino.append(empresa)
                    empresas_movidas += 1
        
        if empresas_movidas > 0:
            self.llenar_tabla(tabla_destino, empresas_destino)
            QMessageBox.information(self, "Completado", f"{empresas_movidas} empresa(s) movidas para {accion}")
        else:
            QMessageBox.information(self, "Sin cambios", "Las empresas seleccionadas ya existen en el destino")
        
        self.actualizar_estadisticas()
    
    def _mover_todas(self, tabla_origen: QTableWidget, tabla_destino: QTableWidget, accion: str):
        """Mueve todas las empresas entre tablas sin duplicados"""
        empresas_origen = self.obtener_empresas_tabla(tabla_origen)
        empresas_destino = self.obtener_empresas_tabla(tabla_destino)
        
        empresas_movidas = 0
        for empresa in empresas_origen:
            if not self.empresa_existe(empresa, empresas_destino):
                empresas_destino.append(empresa)
                empresas_movidas += 1
        
        if empresas_movidas > 0:
            self.llenar_tabla(tabla_destino, empresas_destino)
            QMessageBox.information(self, "Completado", f"{empresas_movidas} empresa(s) preparadas para {accion}")
        else:
            QMessageBox.information(self, "Sin cambios", "Todas las empresas ya existen en el destino")
        
        self.actualizar_estadisticas()
    
    def _quitar_seleccionadas(self, tabla: QTableWidget, descripcion: str):
        """Quita empresas seleccionadas de una tabla"""
        filas_seleccionadas = tabla.selectionModel().selectedRows()
        
        if not filas_seleccionadas:
            QMessageBox.warning(self, "Sin selección", "Seleccione una o más empresas para quitar")
            return
        
        empresas = self.obtener_empresas_tabla(tabla)
        
        for index in sorted(filas_seleccionadas, reverse=True):
            fila = index.row()
            if fila < len(empresas):
                empresas.pop(fila)
        
        self.llenar_tabla(tabla, empresas)
        QMessageBox.information(self, "Completado", f"{len(filas_seleccionadas)} empresa(s) quitadas de {descripcion}")
        self.actualizar_estadisticas()
    
    def _vaciar_tabla(self, tabla: QTableWidget):
        """Vacía completamente una tabla"""
        tabla.setRowCount(0)
    
    def obtener_empresas_tabla(self, tabla: QTableWidget) -> List[Dict]:
        """Obtiene las empresas de una tabla"""
        empresas = []
        for fila in range(tabla.rowCount()):
            empresa = {
                'nombre': tabla.item(fila, 0).text() if tabla.item(fila, 0) else '',
                'nif': tabla.item(fila, 1).text() if tabla.item(fila, 1) else '',
                'email': tabla.item(fila, 2).text() if tabla.item(fila, 2) else '',
                'contacto': tabla.item(fila, 3).text() if tabla.item(fila, 3) else ''
            }
            empresas.append(empresa)
        
        return empresas
    
    def empresa_existe(self, empresa_buscar: Dict, lista_empresas: List[Dict]) -> bool:
        """Verifica si una empresa ya existe en la lista (por NIF o nombre)"""
        nif_buscar = empresa_buscar.get('nif', '').strip().upper()
        nombre_buscar = empresa_buscar.get('nombre', '').strip().upper()
        
        for empresa in lista_empresas:
            nif_existente = empresa.get('nif', '').strip().upper()
            nombre_existente = empresa.get('nombre', '').strip().upper()
            
            if nif_buscar and nif_existente and nif_buscar == nif_existente:
                return True
            
            if not nif_buscar and not nif_existente and nombre_buscar == nombre_existente:
                return True
        
        return False
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        total_izq = self.tabla_izquierda.rowCount()
        total_der = self.tabla_derecha.rowCount()
        
        if self.modo == "exportar":
            texto = f"En aplicación: {total_izq} | Para exportar: {total_der}"
        else:
            texto = f"En aplicación: {total_izq} | En Excel: {total_der}"
        
        self.label_stats.setText(texto)
    
    def ejecutar_accion(self):
        """Ejecuta la acción principal (importar o exportar)"""
        if self.modo == "exportar":
            self._ejecutar_exportacion()
        else:
            self._ejecutar_importacion()
    
    def _ejecutar_exportacion(self):
        """Ejecuta la exportación a Excel"""
        empresas_a_exportar = self.obtener_empresas_tabla(self.tabla_derecha)
        
        if not empresas_a_exportar:
            QMessageBox.warning(self, "Sin datos", "No hay empresas seleccionadas para exportar")
            return
        
        if not self.archivo_excel:
            QMessageBox.warning(self, "Sin archivo", "Seleccione un archivo Excel de destino")
            return
        
        if self.guardar_empresas_excel(empresas_a_exportar, self.archivo_excel):
            self.empresas_resultado = empresas_a_exportar
            self.archivo_resultado = self.archivo_excel
            self.result_accepted = True
            
            QMessageBox.information(self, "Exportación Completada",
                                  f"{len(empresas_a_exportar)} empresas exportadas exitosamente a:\n"
                                  f"{os.path.basename(self.archivo_excel)}")
            self.accept()
    
    def _ejecutar_importacion(self):
        """Ejecuta la importación desde Excel"""
        empresas_actualizadas = self.obtener_empresas_tabla(self.tabla_izquierda)
        empresas_originales = len(self.empresas_aplicacion)
        empresas_nuevas = len(empresas_actualizadas) - empresas_originales
        
        if empresas_nuevas <= 0:
            QMessageBox.information(self, "Sin cambios", "No se han añadido nuevas empresas para importar")
            return
        
        respuesta = QMessageBox.question(self, "Confirmar Importación",
                                       f"¿Importar {empresas_nuevas} nueva(s) empresa(s) a la aplicación?",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if respuesta == QMessageBox.Yes:
            self.empresas_resultado = empresas_actualizadas
            self.result_accepted = True
            
            QMessageBox.information(self, "Importación Completada",
                                  f"{empresas_nuevas} empresas importadas exitosamente")
            self.accept()
    
    def get_resultado(self):
        """Obtiene el resultado de la operación"""
        if hasattr(self, 'result_accepted') and self.result_accepted:
            return {
                'empresas': getattr(self, 'empresas_resultado', []),
                'archivo': getattr(self, 'archivo_resultado', ''),
                'modo': self.modo
            }
        return None
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de ventana"""
        if not hasattr(self, 'result_accepted'):
            self.result_accepted = False
        event.accept()


# === FUNCIONES PRINCIPALES PARA INTEGRACIÓN ===

def mostrar_ventana_importar_exportar_excel(parent, empresas_aplicacion, archivo_excel=None, modo="importar"):
    """Función principal para mostrar la ventana de importación/exportación"""
    try:
        ventana = VentanaDobleTabla(empresas_aplicacion, archivo_excel, modo)
        resultado = ventana.exec_()
        
        if resultado == QDialog.Accepted:
            return ventana.get_resultado()
        else:
            return None
            
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Error abriendo ventana de gestión Excel:\n{str(e)}")
        return None



def obtener_empresas_actuales(self):
    """Obtiene empresas del sistema con logs de diagnóstico"""
    try:
        logger.debug("Iniciando diagnóstico de empresas")
        empresas = []
        
        # Verificar que existe main_window
        if not self.main_window:
            logger.error("self.main_window es None")
            return []
        
        logger.debug(f"main_window existe: {type(self.main_window)}")
        
        # Verificar que existe TwEmpresas
        if not hasattr(self.main_window, 'TwEmpresas'):
            logger.error("main_window no tiene atributo 'TwEmpresas'")
            logger.debug(f"Atributos disponibles: {[attr for attr in dir(self.main_window) if not attr.startswith('_')]}")
            return []
        
        logger.debug("TwEmpresas encontrada")
        tabla = self.main_window.TwEmpresas
        
        # Verificar estado de la tabla
        if not tabla:
            logger.error("TwEmpresas es None")
            return []
        
        logger.debug(f"Tipo de tabla: {type(tabla)}")
        
        # Verificar filas y columnas
        num_filas = tabla.rowCount()
        num_columnas = tabla.columnCount()
        logger.debug(f"Tabla: {num_filas} filas x {num_columnas} columnas")
        
        if num_filas == 0:
            logger.warning("La tabla está vacía (0 filas)")
            return []
        
        # Examinar cada fila en detalle
        for fila in range(num_filas):
            logger.debug(f"Procesando fila {fila}")
            
            # Verificar cada item de la fila
            items = []
            for col in range(4):  # 4 columnas: nombre, nif, email, contacto
                item = tabla.item(fila, col)
                if item:
                    texto = item.text().strip()
                    items.append(f"Col{col}: '{texto}'")
                else:
                    items.append(f"Col{col}: None")
            
            logger.debug(f"Fila {fila}: {' | '.join(items)}")
            
            # Obtener nombre
            nombre_item = tabla.item(fila, 0)
            if not nombre_item:
                logger.debug(f"Fila {fila}: nombre_item es None - SALTANDO")
                continue
            
            nombre = nombre_item.text().strip()
            if not nombre:
                logger.debug(f"Fila {fila}: nombre está vacío - SALTANDO")
                continue
            
            logger.debug(f"Fila {fila}: Nombre válido: '{nombre}'")
            
            # Crear empresa
            empresa = {
                'nombre': nombre,
                'nif': tabla.item(fila, 1).text().strip() if tabla.item(fila, 1) else '',
                'email': tabla.item(fila, 2).text().strip() if tabla.item(fila, 2) else '',
                'contacto': tabla.item(fila, 3).text().strip() if tabla.item(fila, 3) else ''
            }
            
            empresas.append(empresa)
            logger.debug(f"Fila {fila}: Empresa añadida: {empresa}")
        
        logger.info(f"Total empresas válidas encontradas: {len(empresas)}")
        
        for i, emp in enumerate(empresas):
            logger.debug(f"Empresa {i}: {emp['nombre']} | {emp['nif']}")
        
        logger.debug("Fin diagnóstico")
        return empresas
        
    except Exception as e:
        logger.error(f"Excepción en obtener_empresas_actuales: {e}")
        import traceback
        traceback.print_exc()
        return []
def aplicar_empresas_importadas(main_window, empresas_importadas):
    """Aplica empresas importadas al sistema"""
    try:
        # Actualizar tabla TwEmpresas
        if hasattr(main_window, 'TwEmpresas'):
            tabla = main_window.TwEmpresas
            tabla.setRowCount(len(empresas_importadas))
            
            for fila, empresa in enumerate(empresas_importadas):
                tabla.setItem(fila, 0, QTableWidgetItem(empresa.get('nombre', '')))
                tabla.setItem(fila, 1, QTableWidgetItem(empresa.get('nif', '')))
                tabla.setItem(fila, 2, QTableWidgetItem(empresa.get('email', '')))
                tabla.setItem(fila, 3, QTableWidgetItem(empresa.get('contacto', '')))
            
            logger.info(f"Tabla actualizada con {len(empresas_importadas)} empresas")
        
        # Guardar en JSON si existe el controlador
        if hasattr(main_window, 'controlador_json') and main_window.controlador_json:
            # Obtener contrato actual
            contrato_actual = None
            if hasattr(main_window, 'contract_manager') and main_window.contract_manager:
                contrato_actual = main_window.contract_manager.get_current_contract()
            
            if contrato_actual:
                exito = main_window.controlador_json.guardar_empresas_unificadas_en_json(
                    contrato_actual, empresas_importadas
                )
                if exito:
                    logger.info(f"Empresas guardadas en JSON para: {contrato_actual}")
        
        logger.info(f"Aplicadas {len(empresas_importadas)} empresas")
        
    except Exception as e:
        logger.error(f"Error aplicando empresas: {e}")
        raise

def actualizar_tabla_empresas(main_window, empresas):
    """
    Actualiza la tabla de empresas en la interfaz
    PERSONALIZAR SEGÚN TU TABLA
    """
    try:
        if not hasattr(main_window, 'tabla_empresas'):
            return
            
        tabla = main_window.tabla_empresas
        tabla.setRowCount(len(empresas))
        
        for fila, empresa in enumerate(empresas):
            tabla.setItem(fila, 0, QTableWidgetItem(empresa.get('nombre', '')))
            tabla.setItem(fila, 1, QTableWidgetItem(empresa.get('nif', '')))
            tabla.setItem(fila, 2, QTableWidgetItem(empresa.get('email', '')))
            tabla.setItem(fila, 3, QTableWidgetItem(empresa.get('contacto', '')))
        
        logger.info(f"Tabla actualizada con {len(empresas)} empresas")
        
    except Exception as e:
        logger.error(f"Error actualizando tabla: {e}")

# === FUNCIÓN DE PRUEBA ===

def test_ventana_excel():
    """Función para probar la ventana de forma independiente"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Datos de prueba
    empresas_prueba = [
        {'nombre': 'Constructora ABC', 'nif': '12345678A', 'email': 'info@abc.com', 'contacto': '600111222'},
        {'nombre': 'Ingeniería XYZ', 'nif': '87654321B', 'email': 'contacto@xyz.com', 'contacto': '600333444'},
        {'nombre': 'Arquitectos DEF', 'nif': '11223344C', 'email': 'estudio@def.com', 'contacto': '600555666'}
    ]
    
    # Probar modo importar
    ventana = VentanaDobleTabla(empresas_prueba, None, "importar")
    ventana.show()
    
    sys.exit(app.exec_())

# === FUNCIÓN PRINCIPAL PARA EVENTOS ===

def gestionar_importacion_exportacion_excel(main_window, modo):
    """
    Función principal llamada desde eventos.py
    Gestiona todo el proceso de importación/exportación
    """
    try:
        if hasattr(main_window, 'controlador_eventos_ui') and main_window.controlador_eventos_ui:
            empresas_actuales = main_window.controlador_eventos_ui.obtener_empresas_actuales()
        else:
            empresas_actuales = []
        
        if modo == "importar":
            _procesar_importacion(main_window, empresas_actuales)
        elif modo == "exportar":
            _procesar_exportacion(main_window, empresas_actuales)
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Error en gestión Excel:\n{str(e)}")

def _procesar_importacion(main_window, empresas_actuales):
    """Procesa la importación desde Excel"""
    try:
        # Seleccionar archivo Excel
        archivo_excel, _ = QFileDialog.getOpenFileName(
            main_window, "Seleccionar Excel para importar", "",
            "Archivos Excel (*.xlsx *.xls);;Todos (*)"
        )
        
        if not archivo_excel or not os.path.exists(archivo_excel):
            return
        
        # Mostrar ventana de importación
        resultado = mostrar_ventana_importar_exportar_excel(
            main_window, empresas_actuales, archivo_excel, "importar"
        )
        
        if resultado and resultado.get('empresas'):
            empresas_importadas = resultado['empresas']
            empresas_nuevas = len(empresas_importadas) - len(empresas_actuales)
            
            if empresas_nuevas > 0:
                # Usar el método de la ventana principal para aplicar cambios
                if hasattr(main_window, 'controlador_eventos_ui') and main_window.controlador_eventos_ui:
                    main_window.controlador_eventos_ui.aplicar_empresas_importadas(empresas_importadas)
                QMessageBox.information(main_window, "Importación Exitosa",
                    f"Se importaron {empresas_nuevas} nuevas empresas desde:\n{os.path.basename(archivo_excel)}")
            else:
                QMessageBox.information(main_window, "Sin cambios", "No se importaron empresas nuevas")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error de Importación", f"Error importando:\n{str(e)}")

def _procesar_exportacion(main_window, empresas_actuales):
    """Procesa la exportación hacia Excel"""
    try:
        if not empresas_actuales:
            QMessageBox.information(main_window, "Sin datos", "No hay empresas para exportar")
            return
        
        # Mostrar ventana de exportación
        resultado = mostrar_ventana_importar_exportar_excel(
            main_window, empresas_actuales, None, "exportar"
        )
        
        if resultado:
            empresas_exportadas = resultado.get('empresas', [])
            archivo_destino = resultado.get('archivo', '')
            
            if empresas_exportadas and archivo_destino:
                QMessageBox.information(main_window, "Exportación Exitosa",
                    f"Se exportaron {len(empresas_exportadas)} empresas a:\n{os.path.basename(archivo_destino)}")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error de Exportación", f"Error exportando:\n{str(e)}")


if __name__ == "__main__":
    test_ventana_excel()