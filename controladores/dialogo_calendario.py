from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QCalendarWidget, QLabel, QListWidget, QInputDialog, 
                             QMessageBox, QFrame, QListWidgetItem, QSplitter,
                             QScrollArea, QGridLayout, QWidget, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QRect
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QPainter, QPen

class CalendarioConEventos(QCalendarWidget):
    """Calendario personalizado que muestra nombres de eventos en los dias"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.eventos = {}
    
    def setEventos(self, eventos):
        """Establecer el diccionario de eventos"""
        self.eventos = eventos
        self.update()
    
    def paintCell(self, painter, rect, date):
        """Pintar cada celda del calendario con eventos"""
        # Pintar el dia normal primero
        super().paintCell(painter, rect, date)
        
        # Verificar si hay evento en esta fecha
        fecha_str = date.toString("yyyy-MM-dd")
        if fecha_str in self.eventos:
            evento_nombre = self.eventos[fecha_str]
            
            # Configurar el painter para el texto del evento
            painter.save()
            
            # Configurar fuente pequeña para el evento
            font = QFont()
            font.setPixelSize(8)
            font.setBold(True)
            painter.setFont(font)
            
            # Color del texto del evento
            painter.setPen(QPen(QColor("#E65100")))  # Naranja oscuro
            
            # Calcular area disponible para el texto del evento
            texto_rect = QRect(rect.x() + 2, rect.y() + rect.height() - 15, 
                              rect.width() - 4, 12)
            
            # Truncar texto si es muy largo
            texto_mostrar = evento_nombre
            if len(texto_mostrar) > 12:
                texto_mostrar = texto_mostrar[:10] + "..."
            
            # Dibujar el texto del evento
            painter.drawText(texto_rect, Qt.AlignCenter, texto_mostrar)
            
            painter.restore()

class VistaAnualEventos(QDialog):
    """Dialogo que muestra todos los eventos de un anio completo"""
    
    def __init__(self, parent=None, eventos=None, anio=None):
        super().__init__(parent)
        self.eventos = eventos or {}
        self.anio_actual = anio or QDate.currentDate().year()
        
        self.setWindowTitle("Vista Anual {} - Eventos ADIF".format(self.anio_actual))
        self.setModal(True)
        self.resize(900, 700)
        
        # Aplicar estilo ADIF
        self.setStyleSheet("""
            QDialog {
                background: #e8f5e8;
                border: 2px solid #2E7D32;
                border-radius: 12px;
            }
            
            QLabel {
                color: #1B5E20;
                font-weight: 600;
                font-size: 11pt;
                padding: 4px;
            }
            
            QLabel[objetoEvento="true"] {
                background: #FFEB3B;
                border: 1px solid #FFC107;
                border-radius: 4px;
                color: #E65100;
                font-size: 9pt;
                padding: 2px 4px;
                margin: 1px;
            }
            
            QSpinBox {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 4px;
                font-size: 10pt;
                font-weight: 600;
                color: #1B5E20;
            }
            
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #388E3C);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 9pt;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #66BB6A, stop:1 #4CAF50);
            }
            
            QScrollArea {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                background: white;
            }
        """)
        
        self.setupUI()
        self.cargar_eventos_anio()
    
    def setupUI(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        
        # Titulo y selector de año
        layout_titulo = QHBoxLayout()
        
        label_titulo = QLabel("Eventos del Año {}".format(self.anio_actual))
        label_titulo.setAlignment(Qt.AlignLeft)
        layout_titulo.addWidget(label_titulo)
        
        layout_titulo.addStretch()
        
        # Selector de año
        label_anio = QLabel("Anio:")
        layout_titulo.addWidget(label_anio)
        
        self.spin_anio = QSpinBox()
        self.spin_anio.setRange(2020, 2030)
        self.spin_anio.setValue(self.anio_actual)
        self.spin_anio.valueChanged.connect(self.cambiar_anio)
        layout_titulo.addWidget(self.spin_anio)
        
        layout_principal.addLayout(layout_titulo)
        
        # Área scrolleable para los meses
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.layout_meses = QGridLayout(scroll_widget)
        
        # Configurar el layout de meses (3 columnas x 4 filas)
        self.layout_meses.setSpacing(20)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout_principal.addWidget(scroll_area)
        
        # Boton cerrar
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout_botones.addWidget(btn_cerrar)
        
        layout_principal.addLayout(layout_botones)
    
    def cambiar_anio(self, nuevo_anio):
        """Cambiar el anio mostrado"""
        self.anio_actual = nuevo_anio
        self.setWindowTitle("Vista Anual {} - Eventos ADIF".format(self.anio_actual))
        self.cargar_eventos_anio()
    
    def cargar_eventos_anio(self):
        """Cargar y mostrar todos los eventos del anio"""
        # Limpiar layout anterior
        for i in reversed(range(self.layout_meses.count())): 
            self.layout_meses.itemAt(i).widget().setParent(None)
        
        # Nombres de meses
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        # Crear widgets para cada mes
        for mes_num in range(1, 13):
            mes_widget = self.crear_widget_mes(mes_num, meses[mes_num - 1])
            
            # Calcular posicion en el grid (3 columnas)
            fila = (mes_num - 1) // 3
            columna = (mes_num - 1) % 3
            
            self.layout_meses.addWidget(mes_widget, fila, columna)
    
    def crear_widget_mes(self, mes_num, nombre_mes):
        """Crear widget para mostrar un mes con sus eventos"""
        mes_frame = QFrame()
        mes_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        mes_frame.setMinimumSize(250, 200)
        
        layout_mes = QVBoxLayout(mes_frame)
        
        # Titulo del mes
        titulo_mes = QLabel("{} {}".format(nombre_mes, self.anio_actual))
        titulo_mes.setAlignment(Qt.AlignCenter)
        titulo_mes.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
                padding: 6px;
                margin-bottom: 8px;
            }
        """)
        layout_mes.addWidget(titulo_mes)
        
        # Buscar eventos de este mes
        eventos_mes = self.obtener_eventos_mes(mes_num)
        
        if eventos_mes:
            for fecha_str, evento_nombre in sorted(eventos_mes.items()):
                fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
                if fecha.isValid():
                    # Crear label para cada evento
                    evento_label = QLabel("{:02d}: {}".format(fecha.day(), evento_nombre))
                    evento_label.setProperty("objetoEvento", "true")
                    evento_label.setWordWrap(True)
                    layout_mes.addWidget(evento_label)
        else:
            # Sin eventos
            sin_eventos = QLabel("Sin eventos este mes")
            sin_eventos.setAlignment(Qt.AlignCenter)
            sin_eventos.setStyleSheet("color: #757575; font-style: italic;")
            layout_mes.addWidget(sin_eventos)
        
        layout_mes.addStretch()
        return mes_frame
    
    def obtener_eventos_mes(self, mes_num):
        """Obtener eventos de un mes especifico"""
        eventos_mes = {}
        
        for fecha_str, evento_nombre in self.eventos.items():
            fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
            if fecha.isValid() and fecha.year() == self.anio_actual and fecha.month() == mes_num:
                eventos_mes[fecha_str] = evento_nombre
        
        return eventos_mes

class DialogoCalendario(QDialog):
    fecha_seleccionada = pyqtSignal(QDate)
    
    def __init__(self, parent=None, fecha_inicial=None, eventos_iniciales=None):
        super().__init__(parent)
        self.setWindowTitle(" Calendario ADIF")
        self.setModal(True)
        self.resize(700, 450)
        
        # Diccionario para almacenar eventos (modo alive + eventos de firmas)
        self.eventos = eventos_iniciales.copy() if eventos_iniciales else {}
        
        # Aplicar estilo ADIF
        self.setStyleSheet("""
            QDialog {
                background: #e8f5e8;
                border: 2px solid #2E7D32;
                border-radius: 12px;
            }
            
            QLabel {
                color: #1B5E20;
                font-weight: 600;
                font-size: 12pt;
                padding: 8px;
            }
            
            QCalendarWidget {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                selection-background-color: #2E7D32;
                color: #1B5E20;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                color: #1B5E20;
                background-color: white;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
            
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #388E3C);
            }
            
            QCalendarWidget QToolButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-weight: 600;
            }
            
            QCalendarWidget QToolButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #66BB6A, stop:1 #4CAF50);
            }
            
            QCalendarWidget QSpinBox {
                background: white;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 2px;
                color: #1B5E20;
            }
            
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #388E3C);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 9pt;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #66BB6A, stop:1 #4CAF50);
            }
            
            QPushButton:pressed {
                background: #388E3C;
            }
            
            QPushButton#btn_cancelar {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #757575, stop:1 #616161);
            }
            
            QPushButton#btn_cancelar:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #9E9E9E, stop:1 #757575);
            }
            
            QListWidget {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 4px;
                color: #1B5E20;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            
            QListWidget::item:selected {
                background: #E8F5E8;
                color: #2E7D32;
            }
            
            QListWidget::item:hover {
                background: #F1F8E9;
            }
        """)
        
        self.setupUI()
        
        # Establecer fecha inicial si se proporciona
        if fecha_inicial:
            self.calendario.setSelectedDate(fecha_inicial)
        else:
            self.calendario.setSelectedDate(QDate.currentDate())
    
    def setupUI(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        
        # Titulo
        label_titulo = QLabel(" Calendario ADIF - Gestión de Eventos")
        label_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(label_titulo)
        
        # Splitter para dividir calendario y eventos
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Calendario
        panel_calendario = QFrame()
        layout_calendario = QVBoxLayout(panel_calendario)
        
        self.calendario = CalendarioConEventos()
        self.calendario.setGridVisible(True)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendario.setFirstDayOfWeek(Qt.Monday)
        layout_calendario.addWidget(self.calendario)
        
        splitter.addWidget(panel_calendario)
        
        # Panel derecho - Eventos
        panel_eventos = QFrame()
        panel_eventos.setMinimumWidth(250)
        layout_eventos = QVBoxLayout(panel_eventos)
        
        label_eventos = QLabel("Eventos Especiales")
        label_eventos.setAlignment(Qt.AlignCenter)
        layout_eventos.addWidget(label_eventos)
        
        # Lista de eventos
        self.lista_eventos = QListWidget()
        layout_eventos.addWidget(self.lista_eventos)
        
        # Botones de gestion de eventos
        layout_btn_eventos = QHBoxLayout()
        
        btn_crear_evento = QPushButton(" Crear Evento")
        btn_crear_evento.clicked.connect(self.crear_evento)
        layout_btn_eventos.addWidget(btn_crear_evento)
        
        btn_eliminar_evento = QPushButton(" Eliminar")
        btn_eliminar_evento.clicked.connect(self.eliminar_evento_seleccionado)
        layout_btn_eventos.addWidget(btn_eliminar_evento)
        
        layout_eventos.addLayout(layout_btn_eventos)
        
        # Boton Vista Anual
        btn_vista_anual = QPushButton(" Vista Anual")
        btn_vista_anual.clicked.connect(self.abrir_vista_anual)
        layout_eventos.addWidget(btn_vista_anual)
        
        splitter.addWidget(panel_eventos)
        splitter.setSizes([400, 250])
        
        layout_principal.addWidget(splitter)
        
        # Botones principales
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        btn_cancelar = QPushButton(" Cancelar")
        btn_cancelar.setObjectName("btn_cancelar")
        btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(btn_cancelar)
        
        btn_aceptar = QPushButton(" Seleccionar Fecha")
        btn_aceptar.clicked.connect(self.aceptar_fecha)
        btn_aceptar.setDefault(True)
        layout_botones.addWidget(btn_aceptar)
        
        layout_principal.addLayout(layout_botones)
        
        # Conectar eventos del calendario
        self.calendario.activated.connect(self.aceptar_fecha)
        self.calendario.clicked.connect(self.mostrar_eventos_dia)
        
        # Actualizar visualizacion inicial
        self.actualizar_eventos_visuales()
        self.calendario.setEventos(self.eventos)
    
    def crear_evento(self):
        """Crear un nuevo evento especial"""
        try:
            fecha_actual = self.calendario.selectedDate()
            
            # Pedir el nombre del evento
            nombre_evento, ok = QInputDialog.getText(
                self,
                "Crear Evento",
                f"Nombre del evento para el {fecha_actual.toString('dd/MM/yyyy')}:",
                text=""
            )
            
            if ok and nombre_evento.strip():
                fecha_str = fecha_actual.toString("yyyy-MM-dd")
                
                # Verificar si ya existe un evento en esa fecha
                if fecha_str in self.eventos:
                    respuesta = QMessageBox.question(
                        self,
                        "Fecha ocupada",
                        f"Ya existe un evento el {fecha_actual.toString('dd/MM/yyyy')}: '{self.eventos[fecha_str]}'\n\n¿Deseas reemplazarlo?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if respuesta != QMessageBox.Yes:
                        return
                
                # Guardar el evento
                self.eventos[fecha_str] = nombre_evento.strip()
                
                # Actualizar la visualizacion
                self.actualizar_lista_eventos()
                self.actualizar_eventos_visuales()
                self.calendario.setEventos(self.eventos)
                
                QMessageBox.information(
                    self,
                    "Evento creado",
                    f" Evento '{nombre_evento}' creado para el {fecha_actual.toString('dd/MM/yyyy')}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear evento: {str(e)}")
    
    def eliminar_evento_seleccionado(self):
        """Eliminar el evento seleccionado de la lista"""
        try:
            item_actual = self.lista_eventos.currentItem()
            if not item_actual:
                QMessageBox.warning(self, "Advertencia", " Selecciona un evento para eliminar")
                return
            
            # Extraer la fecha del texto del item
            texto = item_actual.text()
            fecha_inicio = texto.find("(") + 1
            fecha_fin = texto.find(")")
            
            if fecha_inicio > 0 and fecha_fin > fecha_inicio:
                fecha_str_display = texto[fecha_inicio:fecha_fin]
                
                # Convertir formato dd/MM/yyyy a yyyy-MM-dd
                partes_fecha = fecha_str_display.split("/")
                if len(partes_fecha) == 3:
                    fecha_str_key = f"{partes_fecha[2]}-{partes_fecha[1]:0>2}-{partes_fecha[0]:0>2}"
                    
                    if fecha_str_key in self.eventos:
                        respuesta = QMessageBox.question(
                            self,
                            "Eliminar evento",
                            f"Estas seguro de eliminar el evento:\n'{self.eventos[fecha_str_key]}'?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if respuesta == QMessageBox.Yes:
                            del self.eventos[fecha_str_key]
                            self.actualizar_lista_eventos()
                            self.actualizar_eventos_visuales()
                            self.calendario.setEventos(self.eventos)
                            QMessageBox.information(self, "Evento eliminado", " Evento eliminado correctamente")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar evento: {str(e)}")
    
    def mostrar_eventos_dia(self, fecha):
        """Mostrar eventos del dia seleccionado"""
        fecha_str = fecha.toString("yyyy-MM-dd")
        if fecha_str in self.eventos:
            evento = self.eventos[fecha_str]
            QMessageBox.information(
                self,
                "Evento del dia",
                "{}\n{}".format(fecha.toString('dd/MM/yyyy'), evento)
            )
    
    def actualizar_lista_eventos(self):
        """Actualizar la lista visual de eventos"""
        self.lista_eventos.clear()
        
        if len(self.eventos) == 0:
            # Mostrar mensaje cuando no hay eventos
            item_vacio = QListWidgetItem("No hay eventos registrados")
            item_vacio.setTextAlignment(1)  # Centrado
            # Aplicar estilo especial para el mensaje de estado vacio
            font = item_vacio.font()
            font.setItalic(True)
            item_vacio.setFont(font)
            self.lista_eventos.addItem(item_vacio)
            
            item_info = QListWidgetItem("Usa 'Crear Evento' para agregar")
            item_info.setTextAlignment(1)  # Centrado
            item_info.setFont(font)
            self.lista_eventos.addItem(item_info)
        else:
            # Ordenar eventos por fecha
            eventos_ordenados = sorted(self.eventos.items())
            
            for fecha_str, nombre in eventos_ordenados:
                fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
                if fecha.isValid():
                    texto = "{} ({})".format(nombre, fecha.toString('dd/MM/yyyy'))
                    item = QListWidgetItem(texto)
                    self.lista_eventos.addItem(item)
    
    def actualizar_eventos_visuales(self):
        """Actualizar la visualizacion de eventos en el calendario"""
        # Crear formato para dias con eventos
        formato_evento = QTextCharFormat()
        formato_evento.setBackground(QColor("#FFEB3B"))  # Amarillo para eventos
        formato_evento.setForeground(QColor("#E65100"))  # Naranja oscuro para texto
        
        # Limpiar formatos anteriores
        self.calendario.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Aplicar formato a dias con eventos
        for fecha_str in self.eventos:
            fecha = QDate.fromString(fecha_str, "yyyy-MM-dd")
            if fecha.isValid():
                self.calendario.setDateTextFormat(fecha, formato_evento)
        
        # Actualizar lista de eventos y sincronizar con calendario personalizado
        self.actualizar_lista_eventos()
        self.calendario.setEventos(self.eventos)
    
    def aceptar_fecha(self):
        fecha_elegida = self.calendario.selectedDate()
        self.fecha_seleccionada.emit(fecha_elegida)
        self.accept()
    
    def abrir_vista_anual(self):
        """Abrir la vista anual de eventos"""
        try:
            anio_actual = self.calendario.selectedDate().year()
            vista_anual = VistaAnualEventos(self, self.eventos, anio_actual)
            vista_anual.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir vista anual: {str(e)}")
    
    def mostrar_mensaje_sin_firmas(self):
        """Mostrar mensaje informativo cuando no hay firmas registradas"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Sin firmas registradas",
            "No se encontraron fechas de firma en el proyecto actual.\n\n"
            "Puedes crear eventos manualmente usando el boton 'Crear Evento' "
            "o registrar firmas en las fases del proyecto."
        )
    
    def get_fecha_seleccionada(self):
        return self.calendario.selectedDate()