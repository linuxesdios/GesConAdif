import logging

logger = logging.getLogger(__name__)

"""
Controlador para gestión de tablas de la interfaz de usuario
Maneja las tablas de empresas, ofertas y sus interacciones
"""
from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QStyledItemDelegate, 
    QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QDoubleValidator

from modelos_py import Empresa, Oferta, Constantes
from helpers_py import (
    convertir_numero_espanol_a_float, formatear_numero_espanol, 
    validar_nif_basico, validar_email_basico
)


class ControladorTablas(QObject):
    """Controlador para gestión de tablas de la interfaz"""
    
    # Señales
    datos_modificados = pyqtSignal()
    empresa_seleccionada = pyqtSignal(int)
    oferta_modificada = pyqtSignal(int, float)
    
    def __init__(self, main_window=None):
        super().__init__()
        self.tabla_empresas = None
        self.tabla_ofertas = None
        self.sincronizacion_activa = True
        self.main_window = main_window
        
    def setup_tabla_empresas(self, tabla: QTableWidget):
        """
        Configura la tabla de empresas
        
        Args:
            tabla: Widget de tabla para empresas
        """
        try:
            logger.info("[DEBUG] 📊 Configurando tabla de empresas...")
            
            self.tabla_empresas = tabla
            
            # Configuración básica
            tabla.setColumnCount(4)
            tabla.setRowCount(5)  # Filas iniciales
            
            # Encabezados
            encabezados = ['Empresa', 'NIF', 'Email', 'Persona de Contacto']
            tabla.setHorizontalHeaderLabels(encabezados)
            
            # Etiquetas de filas
            tabla.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(5)])
            
            # Configurar redimensionamiento con proporciones específicas
            header = tabla.horizontalHeader()
            
            # Configurar cada columna individualmente
            header.setSectionResizeMode(0, QHeaderView.Stretch)      # Empresa - se estira
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # NIF - tamaño de contenido (más pequeño)
            header.setSectionResizeMode(2, QHeaderView.Stretch)      # Email - se estira
            header.setSectionResizeMode(3, QHeaderView.Stretch)      # Contacto - se estira
            
            # Establecer ancho mínimo y máximo para el NIF
            tabla.setColumnWidth(1, 120)  # NIF más estrecho
            
            # Configurar selección
            tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
            tabla.setSelectionMode(QAbstractItemView.SingleSelection)
            
            # Conectar señales
            tabla.itemChanged.connect(self._on_empresa_item_changed)
            tabla.itemSelectionChanged.connect(self._on_empresa_selection_changed)
            
            logger.info("[SUCCESS] ✅ Tabla de empresas configurada")
            
        except Exception as e:
            logger.error(f"[ERROR] Error configurando tabla empresas: {e}")
    
    def setup_tabla_ofertas(self, tabla: QTableWidget):
        """
        Configura la tabla de ofertas
        
        Args:
            tabla: Widget de tabla para ofertas
        """
        try:
            logger.info("[DEBUG] 📊 Configurando tabla de ofertas...")
            
            self.tabla_ofertas = tabla
            
            # Configuración básica
            tabla.setColumnCount(2)
            encabezados = ['Empresa', 'Oferta (€)']
            tabla.setHorizontalHeaderLabels(encabezados)
            
            # Configurar redimensionamiento
            header = tabla.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            
            # Configurar validador para columna de ofertas
            validator = QDoubleValidator()
            validator.setDecimals(2)
            validator.setRange(0.0, 999999999.99)
            delegate = QStyledItemDelegate()
            tabla.setItemDelegateForColumn(1, delegate)
            
            # Conectar señales
            tabla.itemChanged.connect(self._on_oferta_item_changed)
            
            logger.info("[SUCCESS] ✅ Tabla de ofertas configurada")
            
        except Exception as e:
            logger.error(f"[ERROR] Error configurando tabla ofertas: {e}")
    
    def agregar_fila(self, tabla: QTableWidget):
        """
        Agrega una nueva fila a la tabla
        
        Args:
            tabla: Tabla donde agregar la fila
        """
        try:
            row_count = tabla.rowCount()
            tabla.insertRow(row_count)
            
            # Actualizar etiquetas de filas si es tabla de empresas
            if tabla == self.tabla_empresas:
                tabla.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(row_count + 1)])
                
                # Sincronizar con tabla de ofertas
                if self.tabla_ofertas and self.sincronizacion_activa:
                    self.sincronizar_tablas()
            
            logger.info(f"[DEBUG] ➕ Fila agregada. Total: {row_count + 1}")
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error agregando fila: {e}")
    
    def quitar_fila(self, tabla: QTableWidget):
        """
        Elimina la última fila de la tabla
        
        Args:
            tabla: Tabla de donde eliminar la fila
        """
        try:
            row_count = tabla.rowCount()
            if row_count > 1:  # Mantener al menos una fila
                tabla.removeRow(row_count - 1)
                
                # Actualizar etiquetas si es tabla de empresas
                if tabla == self.tabla_empresas:
                    nueva_cantidad = row_count - 1
                    tabla.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(nueva_cantidad)])
                    
                    # Sincronizar con tabla de ofertas
                    if self.tabla_ofertas and self.sincronizacion_activa:
                        self.sincronizar_tablas()
                
                logger.info(f"[DEBUG] 🗑️ Fila eliminada. Total: {row_count - 1}")
                self.datos_modificados.emit()
            else:
                logger.info("[WARNING] ⚠️ No se puede eliminar la última fila")
                
        except Exception as e:
            logger.error(f"[ERROR] Error eliminando fila: {e}")
    
    def agregar_fila_con_datos(self, tabla: QTableWidget, datos: List[str]):
        """
        Agrega una fila con datos específicos
        
        Args:
            tabla: Tabla donde agregar
            datos: Lista de valores para las columnas
        """
        try:
            row_count = tabla.rowCount()
            tabla.insertRow(row_count)
            
            # Llenar datos
            for col, valor in enumerate(datos):
                if col < tabla.columnCount():
                    item = QTableWidgetItem(str(valor))
                    tabla.setItem(row_count, col, item)
            
            # Actualizar etiquetas si es tabla de empresas
            if tabla == self.tabla_empresas:
                tabla.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(row_count + 1)])
                
                # Sincronizar
                if self.tabla_ofertas and self.sincronizacion_activa:
                    self.sincronizar_tablas()
            
            #logger.info(f"[DEBUG] ➕ Fila con datos agregada: {datos}")
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error agregando fila con datos: {e}")
    
    def eliminar_filas_vacias(self, tabla: QTableWidget):
        """
        Elimina las filas que no tienen datos
        
        Args:
            tabla: Tabla a limpiar
        """
        try:
            filas_a_eliminar = []
            
            for fila in range(tabla.rowCount()):
                es_vacia = True
                for columna in range(tabla.columnCount()):
                    item = tabla.item(fila, columna)
                    if item and item.text().strip():
                        es_vacia = False
                        break
                
                if es_vacia:
                    filas_a_eliminar.append(fila)
            
            # Eliminar en orden inverso para evitar problemas de índices
            for fila in reversed(filas_a_eliminar):
                tabla.removeRow(fila)
            
            if filas_a_eliminar:
                logger.info(f"[DEBUG] 🧹 {len(filas_a_eliminar)} filas vacías eliminadas")
                
                # Actualizar etiquetas si es tabla de empresas
                if tabla == self.tabla_empresas:
                    nueva_cantidad = tabla.rowCount()
                    tabla.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(nueva_cantidad)])
                    
                    # Sincronizar
                    if self.tabla_ofertas and self.sincronizacion_activa:
                        self.sincronizar_tablas()
                
                self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error eliminando filas vacías: {e}")
    
    def sincronizar_tablas(self):
        """Sincroniza la tabla de ofertas con la de empresas"""
        try:
            if not self.tabla_empresas or not self.tabla_ofertas or not self.sincronizacion_activa:
                return
            
            # Obtener empresas de la tabla
            empresas = self.obtener_empresas()
            
            # Ajustar filas en tabla de ofertas
            self.tabla_ofertas.setRowCount(len(empresas))
            
            # Llenar nombres de empresas (columna 0, solo lectura)
            for i, empresa in enumerate(empresas):
                nombre_item = QTableWidgetItem(empresa.nombre)
                nombre_item.setFlags(nombre_item.flags() & ~Qt.ItemIsEditable)  # Solo lectura
                nombre_item.setBackground(Qt.lightGray)
                self.tabla_ofertas.setItem(i, 0, nombre_item)
                
                # Mantener oferta existente si la hay
                oferta_item = self.tabla_ofertas.item(i, 1)
                if not oferta_item:
                    oferta_item = QTableWidgetItem("")
                    self.tabla_ofertas.setItem(i, 1, oferta_item)
            
           # logger.info(f"[DEBUG] Tablas sincronizadas: {len(empresas)} empresas")
            
        except Exception as e:
            logger.error(f"[ERROR] Error sincronizando tablas: {e}")
    
    def obtener_empresas(self) -> List[Empresa]:
        """
        Obtiene la lista de empresas desde la tabla
        
        Returns:
            Lista de objetos Empresa
        """
        empresas = []
        
        if not self.tabla_empresas:
            return empresas
        
        try:
            for fila in range(self.tabla_empresas.rowCount()):
                # Obtener datos de cada columna
                nombre_item = self.tabla_empresas.item(fila, 0)
                nif_item = self.tabla_empresas.item(fila, 1)
                email_item = self.tabla_empresas.item(fila, 2)
                contacto_item = self.tabla_empresas.item(fila, 3)
                
                # Crear empresa solo si tiene nombre
                nombre = nombre_item.text().strip() if nombre_item else ""
                if nombre:
                    empresa = Empresa(
                        nombre=nombre,
                        nif=nif_item.text().strip() if nif_item else "",
                        email=email_item.text().strip() if email_item else "",
                        contacto=contacto_item.text().strip() if contacto_item else ""
                    )
                    
                    # Obtener oferta si existe
                    if self.tabla_ofertas and fila < self.tabla_ofertas.rowCount():
                        oferta_item = self.tabla_ofertas.item(fila, 1)
                        if oferta_item and oferta_item.text().strip():
                            try:
                                empresa.oferta = convertir_numero_espanol_a_float(oferta_item.text())
                            except:
                                empresa.oferta = None
                    
                    empresas.append(empresa)
            
           # logger.info(f"[DEBUG] {len(empresas)} empresas obtenidas")
            return empresas
            
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo empresas: {e}")
            return []
    
    def limpiar_tablas(self):
        """
        Limpia completamente ambas tablas (empresas y ofertas)
        """
        try:
            logger.info("[DEBUG] 🧹 Limpiando tablas...")
            
            # Desactivar sincronización temporal
            self.sincronizacion_activa = False
            
            # Limpiar tabla de empresas
            if self.tabla_empresas:
                self.tabla_empresas.setRowCount(5)  # Resetear a 5 filas vacías
                for row in range(5):
                    for col in range(4):
                        self.tabla_empresas.setItem(row, col, QTableWidgetItem(""))
                
                # Actualizar etiquetas
                self.tabla_empresas.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(5)])
                logger.info("[DEBUG] ✅ Tabla empresas limpiada")
            
            # Limpiar tabla de ofertas
            if self.tabla_ofertas:
                self.tabla_ofertas.setRowCount(5)  # Resetear a 5 filas vacías
                for row in range(5):
                    for col in range(2):
                        self.tabla_ofertas.setItem(row, col, QTableWidgetItem(""))
                
                # Actualizar etiquetas
                self.tabla_ofertas.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(5)])
                logger.info("[DEBUG] ✅ Tabla ofertas limpiada")
            
            # Reactivar sincronización
            self.sincronizacion_activa = True
            logger.info("[SUCCESS] ✅ Tablas limpiadas")
            
        except Exception as e:
            logger.error(f"[ERROR] Error limpiando tablas: {e}")
            # Reactivar sincronización en caso de error
            self.sincronizacion_activa = True

    def obtener_ofertas(self) -> List[Oferta]:
        """
        Obtiene la lista de ofertas desde la tabla
        
        Returns:
            Lista de objetos Oferta
        """
        ofertas = []
        
        if not self.tabla_ofertas:
            return ofertas
        
        try:
            for fila in range(self.tabla_ofertas.rowCount()):
                nombre_item = self.tabla_ofertas.item(fila, 0)
                oferta_item = self.tabla_ofertas.item(fila, 1)
                
                if nombre_item and nombre_item.text().strip():
                    empresa_nombre = nombre_item.text().strip()
                    
                    # Procesar oferta
                    importe = 0.0
                    presenta_oferta = False
                    
                    if oferta_item and oferta_item.text().strip():
                        try:
                            importe = convertir_numero_espanol_a_float(oferta_item.text())
                            presenta_oferta = importe > 0
                        except:
                            importe = 0.0
                            presenta_oferta = False
                    
                    oferta = Oferta(
                        empresa=empresa_nombre,
                        importe=importe,
                        presenta_oferta=presenta_oferta
                    )
                    ofertas.append(oferta)
            
            logger.info(f"[DEBUG] 💰 {len(ofertas)} ofertas obtenidas")
            return ofertas
            
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo ofertas: {e}")
            return []
    
    def cargar_empresas(self, empresas: List[Empresa]):
        """
        Carga una lista de empresas en la tabla
        
        Args:
            empresas: Lista de empresas a cargar
        """
        try:
            if not self.tabla_empresas:
                return
            
            # Desactivar sincronización temporal
            self.sincronizacion_activa = False
            
            # Ajustar número de filas
            self.tabla_empresas.setRowCount(max(len(empresas), 1))
            
            # Cargar datos
            for i, empresa in enumerate(empresas):
                self.tabla_empresas.setItem(i, 0, QTableWidgetItem(empresa.nombre))
                self.tabla_empresas.setItem(i, 1, QTableWidgetItem(empresa.nif))
                self.tabla_empresas.setItem(i, 2, QTableWidgetItem(empresa.email))
                self.tabla_empresas.setItem(i, 3, QTableWidgetItem(empresa.contacto))
            
            # Actualizar etiquetas
            self.tabla_empresas.setVerticalHeaderLabels([f'Emp{i+1}' for i in range(len(empresas))])
            
            # Reactivar sincronización y sincronizar
            self.sincronizacion_activa = True
            if self.tabla_ofertas:
                self.sincronizar_tablas()
                
                # Cargar ofertas si las empresas las tienen
                for i, empresa in enumerate(empresas):
                    if empresa.oferta and i < self.tabla_ofertas.rowCount():
                        oferta_formatted = formatear_numero_espanol(empresa.oferta)
                        self.tabla_ofertas.setItem(i, 1, QTableWidgetItem(oferta_formatted))
            
            logger.info(f"[SUCCESS] {len(empresas)} empresas cargadas")
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error cargando empresas: {e}")
            self.sincronizacion_activa = True
    
    def cargar_ofertas(self, ofertas: List[Oferta]):
        """
        Carga una lista de ofertas en la tabla
        
        Args:
            ofertas: Lista de ofertas a cargar
        """
        try:
            if not self.tabla_ofertas:
                return
            
            for i, oferta in enumerate(ofertas):
                if i < self.tabla_ofertas.rowCount():
                    if oferta.presenta_oferta and oferta.importe > 0:
                        oferta_formatted = formatear_numero_espanol(oferta.importe)
                        self.tabla_ofertas.setItem(i, 1, QTableWidgetItem(oferta_formatted))
            
            logger.info(f"[SUCCESS] {len(ofertas)} ofertas cargadas")
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error cargando ofertas: {e}")
    
    
    
    # =================== MÉTODOS PRIVADOS ===================
    
    def _guardar_tablas_automaticamente(self):
        """Guarda automáticamente los datos de las tablas en JSON"""
        try:
            if not self.main_window or not hasattr(self.main_window, 'controlador_json'):
                return
            
            if not hasattr(self.main_window, 'contract_manager') or not self.main_window.contract_manager:
                return
                
            contrato = self.main_window.contract_manager.get_current_contract()
            if not contrato:
                return
            
            # Obtener empresas actuales de la tabla
            empresas = self.obtener_empresas()
            
            # Convertir a formato JSON
            empresas_data = []
            for empresa in empresas:
                empresa_dict = {
                    'nombre': empresa.nombre,
                    'nif': empresa.nif,
                    'email': empresa.email,
                    'contacto': empresa.contacto,
                    'oferta': empresa.oferta if empresa.oferta else None
                }
                empresas_data.append(empresa_dict)
            
            # Guardar en JSON usando el controlador
            self.main_window.controlador_json.guardar_empresas_en_json(contrato, empresas_data)
            logger.info(f"[AUTOSAVE] Datos de {len(empresas_data)} empresas guardados automáticamente")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando tablas automáticamente: {e}")
    
    def _ejecutar_calculos_completos_si_disponible(self):
        """Ejecutar cálculos completos si el controlador está disponible"""
        logger.info("[ControladorTablas] 🔄 Ejecutando cálculos automáticos...")
        try:
            if not self.main_window:
                logger.info("[ControladorTablas] ❌ main_window no disponible")
                return
                
            if not hasattr(self.main_window, 'controlador_calculos'):
                logger.info("[ControladorTablas] ❌ controlador_calculos no disponible")
                return
                
            # Ejecutar cálculo de ofertas completo para recalcular adjudicación
            if hasattr(self.main_window.controlador_calculos, 'calcular_ofertas_completo'):
                logger.info("[ControladorTablas] 🚀 Ejecutando calcular_ofertas_completo...")
                self.main_window.controlador_calculos.calcular_ofertas_completo(self.main_window)
                logger.info("[ControladorTablas] ✅ Cálculos de adjudicación ejecutados automáticamente")
                
                # Verificar que se rellenaron los campos
                if hasattr(self.main_window, 'empresaAdjudicada'):
                    empresa_actual = self.main_window.empresaAdjudicada.text()
                    logger.info(f"[ControladorTablas] 📋 Empresa adjudicada actual: '{empresa_actual}'")
                
                if hasattr(self.main_window, 'contratistaCIF'):
                    cif_actual = self.main_window.contratistaCIF.text()
                    logger.info(f"[ControladorTablas] 🆔 CIF adjudicada actual: '{cif_actual}'")
                    
            else:
                logger.info("[ControladorTablas] ⚠️ Método calcular_ofertas_completo no disponible")
                
        except Exception as e:
            logger.error(f"[ControladorTablas] Error ejecutando cálculos automáticos: {e}")
            import traceback
            logger.exception("Error completo:")
    
    def _on_empresa_item_changed(self, item):
        """Maneja cambios en items de la tabla de empresas"""
        try:
            row = item.row()
            col = item.column()
            texto = item.text().strip()
            
            # Validaciones específicas por columna
            if col == 1 and texto:  # NIF
                if not validar_nif_basico(texto):
                    item.setBackground(Qt.yellow)
                    item.setToolTip("⚠️ Formato de NIF puede ser incorrecto")
                else:
                    item.setBackground(Qt.white)
                    item.setToolTip("")
                    
            elif col == 2 and texto:  # Email
                if not validar_email_basico(texto):
                    item.setBackground(Qt.yellow)
                    item.setToolTip("⚠️ Formato de email puede ser incorrecto")
                else:
                    item.setBackground(Qt.white)
                    item.setToolTip("")
            else:
                item.setBackground(Qt.white)
                item.setToolTip("")
            
            # Sincronizar si cambió el nombre (columna 0)
            if col == 0 and self.sincronizacion_activa:
                self.sincronizar_tablas()
            
            # Guardar automáticamente los datos
            self._guardar_tablas_automaticamente()
            
            # Ejecutar cálculos completos si hay controlador de cálculos
            self._ejecutar_calculos_completos_si_disponible()
            
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error en cambio de empresa: {e}")
    
    def _on_empresa_selection_changed(self):
        """Maneja cambios de selección en tabla de empresas"""
        try:
            if self.tabla_empresas:
                filas_seleccionadas = self.tabla_empresas.selectionModel().selectedRows()
                if filas_seleccionadas:
                    fila = filas_seleccionadas[0].row()
                    self.empresa_seleccionada.emit(fila)
                    
        except Exception as e:
            logger.error(f"[ERROR] Error en selección de empresa: {e}")
    
    def _on_oferta_item_changed(self, item):
        """Maneja cambios en items de la tabla de ofertas"""
        try:
            if item.column() == 1:  # Solo columna de ofertas
                texto = item.text().strip()
                
                if texto:
                    try:
                        # Validar y formatear número
                        valor = convertir_numero_espanol_a_float(texto)
                        if valor >= 0:
                            # Formatear y actualizar
                            texto_formateado = formatear_numero_espanol(valor)
                            if texto_formateado != texto:
                                item.setText(texto_formateado)
                            
                            item.setBackground(Qt.white)
                            item.setToolTip("")
                            
                            # Emitir señal
                            self.oferta_modificada.emit(item.row(), valor)
                        else:
                            item.setBackground(Qt.red)
                            item.setToolTip("❌ El valor debe ser positivo")
                            
                    except ValueError:
                        item.setBackground(Qt.red)
                        item.setToolTip("❌ Formato numérico inválido")
                        
                else:
                    item.setBackground(Qt.white)
                    item.setToolTip("")
                    self.oferta_modificada.emit(item.row(), 0.0)
            
            # Guardar automáticamente los datos
            self._guardar_tablas_automaticamente()
            
            # Ejecutar cálculos completos si hay controlador de cálculos
            self._ejecutar_calculos_completos_si_disponible()
            
            self.datos_modificados.emit()
            
        except Exception as e:
            logger.error(f"[ERROR] Error en cambio de oferta: {e}")
    
    def validar_datos_tablas(self) -> tuple[bool, List[str]]:
        """
        Valida los datos de las tablas
        
        Returns:
            Tupla (es_valido, lista_errores)
        """
        errores = []
        
        try:
            # Validar empresas
            empresas = self.obtener_empresas()
            
            if not empresas:
                errores.append("Debe haber al menos una empresa")
            else:
                nombres_vistos = set()
                nifs_vistos = set()
                
                for i, empresa in enumerate(empresas):
                    prefijo = f"Empresa {i+1}:"
                    
                    # Validar nombre único
                    if empresa.nombre in nombres_vistos:
                        errores.append(f"{prefijo} Nombre duplicado")
                    nombres_vistos.add(empresa.nombre)
                    
                    # Validar NIF único si se proporciona
                    if empresa.nif:
                        if empresa.nif in nifs_vistos:
                            errores.append(f"{prefijo} NIF duplicado")
                        nifs_vistos.add(empresa.nif)
            
            # Validar ofertas
            ofertas = self.obtener_ofertas()
            ofertas_validas = [o for o in ofertas if o.presenta_oferta and o.importe > 0]
            
            if ofertas_validas:
                # Verificar ofertas duplicadas en el mínimo
                menor_importe = min(o.importe for o in ofertas_validas)
                ofertas_minimas = [o for o in ofertas_validas if abs(o.importe - menor_importe) < 0.01]
                
                if len(ofertas_minimas) > 1:
                    empresas_minimas = [o.empresa for o in ofertas_minimas]
                    errores.append(f"Múltiples empresas con la oferta mínima ({menor_importe:.2f}€): {', '.join(empresas_minimas)}")
            
            es_valido = len(errores) == 0
            return es_valido, errores
            
        except Exception as e:
            errores.append(f"Error validando tablas: {str(e)}")
            return False, errores
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las tablas
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            empresas = self.obtener_empresas()
            ofertas = self.obtener_ofertas()
            ofertas_validas = [o for o in ofertas if o.presenta_oferta and o.importe > 0]
            
            estadisticas = {
                'total_empresas': len(empresas),
                'empresas_con_oferta': len(ofertas_validas),
                'total_ofertas': len(ofertas),
                'menor_oferta': min(o.importe for o in ofertas_validas) if ofertas_validas else 0.0,
                'mayor_oferta': max(o.importe for o in ofertas_validas) if ofertas_validas else 0.0,
                'promedio_ofertas': sum(o.importe for o in ofertas_validas) / len(ofertas_validas) if ofertas_validas else 0.0,
                'empresas_sin_datos': len([e for e in empresas if not e.nif and not e.email]),
                'empresas_con_nif': len([e for e in empresas if e.nif.strip()]),
                'empresas_con_email': len([e for e in empresas if e.email.strip()]),
                'empresas_con_contacto': len([e for e in empresas if e.contacto.strip()])
            }
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo estadísticas: {e}")
            return {}
    
    


# =================== FUNCIONES DE COMPATIBILIDAD ===================
# (Eliminadas - no se usaban)