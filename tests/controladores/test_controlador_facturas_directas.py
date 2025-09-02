#!/usr/bin/env python3
"""
Tests para controlador_facturas_directas.py
Pruebas unitarias completas para gestión de facturas directas ADIF
"""

import pytest
import os
import sys
import json
import shutil
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, date
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Configurar ruta de importación
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from controladores.controlador_facturas_directas import (
    ControladorFacturasDirectas,
    DialogoFacturasDirectas,
    DialogoCrearFactura,
    DialogoTablaResumen
)


class TestControladorFacturasDirectas:
    """Tests para la clase ControladorFacturasDirectas"""
    
    @pytest.fixture
    def temp_dir(self):
        """Directorio temporal para tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def controlador(self, temp_dir):
        """Fixture de controlador con directorio temporal"""
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = temp_dir
            mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas_directas.json")
            controlador = ControladorFacturasDirectas()
            return controlador
    
    @pytest.fixture
    def sample_factura(self):
        """Factura de ejemplo para tests"""
        return {
            "empresa": "Empresa Test S.L.",
            "cif": "B12345678",
            "importe": 1500.50,
            "categoria": "Agua",
            "localidad": "Madrid",
            "estado": "Emitida",
            "identificador_especial": "ESP001",
            "identificacion_admycont": "ADM001",
            "fecha_validacion": "2024-01-15",
            "comentarios": "Factura de prueba",
            "gped": "GPED001"
        }
    
    def test_init_controlador(self, temp_dir):
        """Test inicialización del controlador"""
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = temp_dir
            mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas_directas.json")
            
            controlador = ControladorFacturasDirectas()
            
            assert controlador.directorio_base == temp_dir
            assert controlador.archivo_json.endswith("facturas_directas.json")
            assert controlador.carpeta_pdfs.endswith("pdfactura directa")
    
    def test_obtener_directorio_base_normal(self):
        """Test obtener directorio base en modo desarrollo"""
        controlador = ControladorFacturasDirectas()
        directorio = controlador._obtener_directorio_base()
        
        assert os.path.exists(directorio) or directorio == os.getcwd()
    
    @patch('sys._MEIPASS', '/temp_meipass', create=True)
    @patch('sys.executable', '/app/programa.exe')
    def test_obtener_directorio_base_pyinstaller(self):
        """Test obtener directorio base en PyInstaller"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            controlador = ControladorFacturasDirectas()
            directorio = controlador._obtener_directorio_base()
            
            assert directorio == os.path.dirname('/app/programa.exe')
    
    def test_inicializar_archivos_nuevo(self, controlador, temp_dir):
        """Test inicialización de archivos cuando no existen"""
        # Verificar que se creó el JSON
        assert os.path.exists(controlador.archivo_json)
        
        # Verificar contenido del JSON
        datos = controlador.leer_datos_json()
        assert "version" in datos
        assert "facturas" in datos
        assert "configuracion" in datos
        assert datos["configuracion"]["ultimo_id"] == 0
        
        # Verificar que se creó la carpeta PDF
        assert os.path.exists(controlador.carpeta_pdfs)
    
    def test_inicializar_archivos_existente(self, controlador):
        """Test inicialización cuando los archivos ya existen"""
        # Datos existentes
        datos_existentes = {
            "version": "1.0",
            "facturas": [{"id": 1, "empresa": "Test"}],
            "configuracion": {"ultimo_id": 1}
        }
        
        with open(controlador.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_existentes, f)
        
        # Re-inicializar
        controlador._inicializar_archivos()
        
        # Verificar que no se sobreescribió
        datos = controlador.leer_datos_json()
        assert datos["version"] == "1.0"
        assert len(datos["facturas"]) == 1
    
    def test_leer_datos_json_valido(self, controlador, sample_factura):
        """Test leer JSON válido"""
        datos = {
            "facturas": [sample_factura],
            "configuracion": {"ultimo_id": 1}
        }
        
        with open(controlador.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f)
        
        resultado = controlador.leer_datos_json()
        assert resultado == datos
    
    def test_leer_datos_json_error(self, controlador):
        """Test leer JSON con error"""
        # Escribir JSON inválido
        with open(controlador.archivo_json, 'w') as f:
            f.write("JSON inválido")
        
        resultado = controlador.leer_datos_json()
        assert "facturas" in resultado
        assert "configuracion" in resultado
        assert resultado["facturas"] == []
    
    def test_guardar_datos_json(self, controlador):
        """Test guardar datos en JSON"""
        datos = {
            "facturas": [{"id": 1, "empresa": "Test"}],
            "configuracion": {"ultimo_id": 1}
        }
        
        resultado = controlador.guardar_datos_json(datos)
        assert resultado is True
        
        # Verificar que se guardó correctamente
        datos_leidos = controlador.leer_datos_json()
        assert datos_leidos == datos
    
    def test_guardar_datos_json_error(self, controlador):
        """Test error al guardar JSON"""
        with patch('builtins.open', side_effect=PermissionError("No se puede escribir")):
            resultado = controlador.guardar_datos_json({})
            assert resultado is False
    
    def test_agregar_factura_exitosa(self, controlador, sample_factura):
        """Test agregar factura exitosamente"""
        resultado = controlador.agregar_factura(sample_factura)
        assert resultado is True
        
        # Verificar que se agregó
        facturas = controlador.obtener_facturas()
        assert len(facturas) == 1
        assert facturas[0]["empresa"] == sample_factura["empresa"]
        assert facturas[0]["id"] == 1
        assert facturas[0]["activa"] is True
    
    def test_agregar_factura_campos_completos(self, controlador):
        """Test agregar factura con todos los campos"""
        datos = {
            "empresa": "Test Corp",
            "cif": "A12345678",
            "importe": 2500.75,
            "categoria": "Limpieza",
            "localidad": "Barcelona",
            "estado": "Tramitada",
            "identificador_especial": "SPEC123",
            "identificacion_admycont": "ADM456",
            "fecha_validacion": "2024-02-01",
            "comentarios": "Comentario de prueba",
            "gped": "GP789",
            "archivo_pdf": "factura.pdf"
        }
        
        resultado = controlador.agregar_factura(datos)
        assert resultado is True
        
        factura = controlador.obtener_facturas()[0]
        assert factura["empresa"] == "Test Corp"
        assert factura["cif"] == "A12345678"
        assert factura["importe"] == 2500.75
        assert factura["categoria"] == "Limpieza"
        assert factura["estado"] == "Tramitada"
        assert factura["identificador_especial"] == "SPEC123"
        assert factura["identificacion_admycont"] == "ADM456"
        assert factura["comentarios"] == "Comentario de prueba"
        assert factura["gped"] == "GP789"
        assert factura["archivo_pdf"] == "factura.pdf"
    
    def test_agregar_factura_error(self, controlador, sample_factura):
        """Test error al agregar factura"""
        with patch.object(controlador, 'guardar_datos_json', return_value=False):
            resultado = controlador.agregar_factura(sample_factura)
            assert resultado is False
    
    def test_obtener_facturas_activas(self, controlador):
        """Test obtener solo facturas activas"""
        # Agregar facturas
        facturas_datos = [
            {"empresa": "Empresa 1", "importe": 100, "activa": True},
            {"empresa": "Empresa 2", "importe": 200, "activa": False},
            {"empresa": "Empresa 3", "importe": 300, "activa": True}
        ]
        
        datos = {
            "facturas": facturas_datos,
            "configuracion": {"ultimo_id": 3}
        }
        controlador.guardar_datos_json(datos)
        
        facturas = controlador.obtener_facturas()
        assert len(facturas) == 2
        assert facturas[0]["empresa"] == "Empresa 1"
        assert facturas[1]["empresa"] == "Empresa 3"
    
    def test_obtener_facturas_error(self, controlador):
        """Test error al obtener facturas"""
        with patch.object(controlador, 'leer_datos_json', side_effect=Exception("Error")):
            facturas = controlador.obtener_facturas()
            assert facturas == []
    
    def test_eliminar_factura_exitosa(self, controlador, sample_factura):
        """Test eliminar factura exitosamente"""
        # Agregar factura primero
        controlador.agregar_factura(sample_factura)
        facturas = controlador.obtener_facturas()
        factura_id = facturas[0]["id"]
        
        # Eliminar factura
        resultado = controlador.eliminar_factura(factura_id)
        assert resultado is True
        
        # Verificar que se marcó como inactiva
        datos = controlador.leer_datos_json()
        factura = next(f for f in datos["facturas"] if f["id"] == factura_id)
        assert factura["activa"] is False
        assert "fecha_eliminacion" in factura
    
    def test_eliminar_factura_no_existe(self, controlador):
        """Test eliminar factura que no existe"""
        resultado = controlador.eliminar_factura(999)
        assert resultado is False
    
    def test_eliminar_factura_error(self, controlador, sample_factura):
        """Test error al eliminar factura"""
        controlador.agregar_factura(sample_factura)
        facturas = controlador.obtener_facturas()
        factura_id = facturas[0]["id"]
        
        with patch.object(controlador, 'guardar_datos_json', return_value=False):
            resultado = controlador.eliminar_factura(factura_id)
            assert resultado is False
    
    def test_actualizar_estado_factura(self, controlador, sample_factura):
        """Test actualizar estado de factura"""
        # Agregar factura
        controlador.agregar_factura(sample_factura)
        facturas = controlador.obtener_facturas()
        factura_id = facturas[0]["id"]
        
        # Actualizar estado
        resultado = controlador.actualizar_estado_factura(factura_id, "Pagada")
        assert resultado is True
        
        # Verificar cambio
        facturas = controlador.obtener_facturas()
        assert facturas[0]["estado"] == "Pagada"
        assert "fecha_modificacion_estado" in facturas[0]
    
    def test_actualizar_estado_factura_inactiva(self, controlador, sample_factura):
        """Test actualizar estado de factura inactiva"""
        # Agregar y eliminar factura
        controlador.agregar_factura(sample_factura)
        facturas = controlador.obtener_facturas()
        factura_id = facturas[0]["id"]
        controlador.eliminar_factura(factura_id)
        
        # Intentar actualizar estado
        resultado = controlador.actualizar_estado_factura(factura_id, "Pagada")
        assert resultado is False
    
    def test_generar_nombre_pdf(self, controlador):
        """Test generar nombre de PDF"""
        nombre = controlador.generar_nombre_pdf(1, "Empresa Test S.L.", 1500.75)
        assert nombre == "1_Empresa_Test_S_L__1500,75.pdf"
        
        # Test con empresa sin caracteres especiales
        nombre = controlador.generar_nombre_pdf(2, "TestCorp", 250.00)
        assert nombre == "2_TestCorp_250,00.pdf"
        
        # Test con empresa vacía
        nombre = controlador.generar_nombre_pdf(3, "", 100.50)
        assert nombre == "3_SinEmpresa_100,50.pdf"
    
    def test_generar_nombre_pdf_error(self, controlador):
        """Test error al generar nombre de PDF"""
        with patch('builtins.str', side_effect=Exception("Error")):
            nombre = controlador.generar_nombre_pdf(1, "Test", 100)
            assert nombre == "1_factura.pdf"
    
    def test_gestionar_pdf_exitoso(self, controlador, temp_dir):
        """Test gestión de PDF exitosa"""
        # Crear archivo PDF temporal
        pdf_origen = os.path.join(temp_dir, "factura_origen.pdf")
        with open(pdf_origen, 'w') as f:
            f.write("PDF content")
        
        datos_factura = {
            "id": 1,
            "empresa": "Test Corp",
            "importe": 500.25
        }
        
        resultado = controlador.gestionar_pdf(pdf_origen, datos_factura)
        expected_name = "1_Test_Corp_500,25.pdf"
        
        assert resultado == expected_name
        assert os.path.exists(os.path.join(controlador.carpeta_pdfs, expected_name))
    
    def test_gestionar_pdf_archivo_no_existe(self, controlador):
        """Test gestión de PDF con archivo inexistente"""
        datos_factura = {"id": 1, "empresa": "Test", "importe": 100}
        resultado = controlador.gestionar_pdf("/archivo/inexistente.pdf", datos_factura)
        assert resultado == ""
    
    def test_gestionar_pdf_reemplazar_existente(self, controlador, temp_dir):
        """Test reemplazar PDF existente"""
        # Crear archivos
        pdf_origen = os.path.join(temp_dir, "factura_origen.pdf")
        with open(pdf_origen, 'w') as f:
            f.write("PDF nuevo")
        
        expected_name = "1_TestCorp_100,00.pdf"
        pdf_existente = os.path.join(controlador.carpeta_pdfs, expected_name)
        os.makedirs(controlador.carpeta_pdfs, exist_ok=True)
        with open(pdf_existente, 'w') as f:
            f.write("PDF viejo")
        
        datos_factura = {"id": 1, "empresa": "TestCorp", "importe": 100.0}
        resultado = controlador.gestionar_pdf(pdf_origen, datos_factura)
        
        assert resultado == expected_name
        # Verificar que se reemplazó
        with open(pdf_existente, 'r') as f:
            assert f.read() == "PDF nuevo"
    
    def test_eliminar_pdf_exitoso(self, controlador):
        """Test eliminar PDF existente"""
        # Crear PDF
        os.makedirs(controlador.carpeta_pdfs, exist_ok=True)
        pdf_path = os.path.join(controlador.carpeta_pdfs, "test.pdf")
        with open(pdf_path, 'w') as f:
            f.write("PDF content")
        
        resultado = controlador.eliminar_pdf("test.pdf")
        assert resultado is True
        assert not os.path.exists(pdf_path)
    
    def test_eliminar_pdf_no_existe(self, controlador):
        """Test eliminar PDF que no existe"""
        resultado = controlador.eliminar_pdf("inexistente.pdf")
        assert resultado is False
    
    def test_eliminar_pdf_error(self, controlador):
        """Test error al eliminar PDF"""
        with patch('os.remove', side_effect=PermissionError("No se puede eliminar")):
            resultado = controlador.eliminar_pdf("test.pdf")
            assert resultado is False
    
    @patch('controladores.controlador_facturas_directas.DOCX_AVAILABLE', True)
    def test_generar_informe_word_exitoso(self, controlador, sample_factura):
        """Test generar informe Word exitosamente"""
        with patch('controladores.controlador_facturas_directas.Document') as mock_doc:
            mock_document = Mock()
            mock_doc.return_value = mock_document
            mock_document.add_heading.return_value = Mock(runs=[Mock()], alignment=None)
            mock_document.add_paragraph.return_value = Mock(runs=[], alignment=None)
            mock_document.add_table.return_value = Mock(
                rows=[Mock(cells=[Mock() for _ in range(8)])],
                columns=[Mock(width=None) for _ in range(8)],
                alignment=None,
                style=None
            )
            
            # Configurar mock para add_row
            mock_row = Mock()
            mock_row.cells = [Mock() for _ in range(8)]
            mock_document.add_table.return_value.add_row.return_value = mock_row
            
            facturas = [sample_factura]
            resultado = controlador.generar_informe_word(facturas)
            
            assert resultado != ""
            assert resultado.endswith('.docx')
            mock_document.save.assert_called_once()
    
    @patch('controladores.controlador_facturas_directas.DOCX_AVAILABLE', False)
    def test_generar_informe_word_sin_docx(self, controlador):
        """Test generar informe sin python-docx"""
        resultado = controlador.generar_informe_word([])
        assert resultado == ""
    
    def test_mostrar_popup_principal(self, controlador, qtbot):
        """Test mostrar popup principal"""
        parent = Mock()
        with patch('controladores.controlador_facturas_directas.DialogoFacturasDirectas') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec_.return_value = QDialog.Accepted
            mock_dialog.return_value = mock_dialog_instance
            
            resultado = controlador.mostrar_popup_principal()
            
            mock_dialog.assert_called_once_with(None, controlador)
            mock_dialog_instance.exec_.assert_called_once()
            assert resultado == QDialog.Accepted
    
    def test_mostrar_popup_principal_error(self, controlador):
        """Test error al mostrar popup principal"""
        with patch('controladores.controlador_facturas_directas.DialogoFacturasDirectas', side_effect=Exception("Error")):
            with patch('controladores.controlador_facturas_directas.QMessageBox.critical') as mock_critical:
                resultado = controlador.mostrar_popup_principal()
                
                mock_critical.assert_called_once()
                assert resultado is False


class TestDialogoFacturasDirectas:
    """Tests para DialogoFacturasDirectas"""
    
    @pytest.fixture
    def controlador_mock(self):
        """Mock del controlador"""
        mock = Mock()
        mock.obtener_facturas.return_value = [
            {
                "id": 1,
                "empresa": "Test Corp",
                "categoria": "Agua",
                "estado": "Emitida",
                "importe": 1500.50
            }
        ]
        return mock
    
    def test_init_dialogo(self, qtbot, controlador_mock):
        """Test inicialización del diálogo"""
        parent = Mock()
        dialog = DialogoFacturasDirectas(parent, controlador_mock)
        qtbot.addWidget(dialog)
        
        assert dialog.controlador == controlador_mock
        assert dialog.windowTitle() == "Facturas Directas - ADIF"
    
    def test_crear_factura(self, qtbot, controlador_mock):
        """Test crear nueva factura"""
        dialog = DialogoFacturasDirectas(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.DialogoCrearFactura') as mock_crear:
            mock_crear_instance = Mock()
            mock_crear_instance.exec_.return_value = QDialog.Accepted
            mock_crear.return_value = mock_crear_instance
            
            with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
                dialog.crear_factura()
                
                mock_crear.assert_called_once_with(dialog, controlador_mock)
                mock_info.assert_called_once()
    
    def test_editar_factura_sin_facturas(self, qtbot):
        """Test editar factura cuando no hay facturas"""
        mock_controlador = Mock()
        mock_controlador.obtener_facturas.return_value = []
        
        dialog = DialogoFacturasDirectas(None, mock_controlador)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
            dialog.editar_factura()
            mock_info.assert_called_once()
    
    def test_borrar_factura_confirmacion(self, qtbot, controlador_mock):
        """Test borrar factura con confirmación"""
        dialog = DialogoFacturasDirectas(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.QInputDialog.getItem') as mock_input:
            mock_input.return_value = ("ID: 1 - Test Corp - Agua - Emitida - 1500.5€", True)
            
            with patch('controladores.controlador_facturas_directas.QMessageBox.question') as mock_question:
                mock_question.return_value = QMessageBox.Yes
                
                controlador_mock.eliminar_factura.return_value = True
                
                with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
                    dialog.borrar_factura()
                    
                    controlador_mock.eliminar_factura.assert_called_once_with(1)
                    mock_info.assert_called_once()
    
    def test_resumen_facturacion(self, qtbot, controlador_mock):
        """Test mostrar resumen de facturación"""
        dialog = DialogoFacturasDirectas(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.DialogoTablaResumen') as mock_tabla:
            mock_tabla_instance = Mock()
            mock_tabla.return_value = mock_tabla_instance
            
            dialog.resumen_facturacion()
            
            mock_tabla.assert_called_once_with(dialog, controlador_mock.obtener_facturas.return_value)
            mock_tabla_instance.exec_.assert_called_once()
    
    @patch('controladores.controlador_facturas_directas.DOCX_AVAILABLE', True)
    def test_informe_facturacion_exitoso(self, qtbot, controlador_mock):
        """Test generar informe de facturación exitoso"""
        dialog = DialogoFacturasDirectas(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        controlador_mock.generar_informe_word.return_value = "/path/informe.docx"
        
        with patch('controladores.controlador_facturas_directas.QProgressDialog') as mock_progress:
            mock_progress_instance = Mock()
            mock_progress.return_value = mock_progress_instance
            
            with patch('os.path.exists', return_value=True):
                with patch('controladores.controlador_facturas_directas.QMessageBox.question') as mock_question:
                    mock_question.return_value = QMessageBox.No
                    
                    dialog.informe_facturacion()
                    
                    controlador_mock.generar_informe_word.assert_called_once()


class TestDialogoCrearFactura:
    """Tests para DialogoCrearFactura"""
    
    @pytest.fixture
    def controlador_mock(self):
        """Mock del controlador"""
        mock = Mock()
        mock.leer_datos_json.return_value = {"configuracion": {"ultimo_id": 5}}
        mock.gestionar_pdf.return_value = "factura.pdf"
        mock.agregar_factura.return_value = True
        return mock
    
    def test_init_crear_factura(self, qtbot, controlador_mock):
        """Test inicialización para crear factura"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        assert dialog.controlador == controlador_mock
        assert dialog.datos_factura is None
        assert dialog.windowTitle() == "Crear Factura"
    
    def test_init_editar_factura(self, qtbot, controlador_mock):
        """Test inicialización para editar factura"""
        datos_factura = {
            "id": 1,
            "empresa": "Test Corp",
            "cif": "B12345678",
            "importe": 1500.50,
            "categoria": "Agua",
            "estado": "Emitida"
        }
        
        dialog = DialogoCrearFactura(None, controlador_mock, datos_factura)
        qtbot.addWidget(dialog)
        
        assert dialog.datos_factura == datos_factura
        assert dialog.windowTitle() == "Editar Factura"
        assert dialog.empresa_edit.text() == "Test Corp"
        assert dialog.cif_edit.text() == "B12345678"
        assert dialog.importe_spinbox.value() == 1500.50
    
    def test_cargar_datos_existentes(self, qtbot, controlador_mock):
        """Test cargar datos de factura existente"""
        datos_factura = {
            "empresa": "Test Corp",
            "cif": "A12345678",
            "identificador_especial": "ESP001",
            "identificacion_admycont": "ADM001",
            "importe": 2500.75,
            "categoria": "Limpieza",
            "localidad": "Barcelona",
            "estado": "Tramitada",
            "gped": "GP123",
            "comentarios": "Comentario de prueba",
            "fecha_validacion": "2024-02-15",
            "archivo_pdf": "factura_test.pdf"
        }
        
        dialog = DialogoCrearFactura(None, controlador_mock, datos_factura)
        qtbot.addWidget(dialog)
        
        assert dialog.empresa_edit.text() == "Test Corp"
        assert dialog.cif_edit.text() == "A12345678"
        assert dialog.identificador_edit.text() == "ESP001"
        assert dialog.identificacion_admycont_edit.text() == "ADM001"
        assert dialog.importe_spinbox.value() == 2500.75
        assert dialog.categoria_combo.currentText() == "Limpieza"
        assert dialog.localidad_edit.text() == "Barcelona"
        assert dialog.estado_combo.currentText() == "Tramitada"
        assert dialog.gped_edit.text() == "GP123"
        assert dialog.comentarios_edit.toPlainText() == "Comentario de prueba"
        assert dialog.archivo_pdf_seleccionado == "factura_test.pdf"
    
    def test_seleccionar_pdf_sin_empresa(self, qtbot, controlador_mock):
        """Test seleccionar PDF sin empresa"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.warning') as mock_warning:
            dialog.seleccionar_pdf()
            mock_warning.assert_called_once()
    
    def test_seleccionar_pdf_sin_importe(self, qtbot, controlador_mock):
        """Test seleccionar PDF sin importe válido"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        dialog.empresa_edit.setText("Test Corp")
        # importe_spinbox por defecto es 0
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.warning') as mock_warning:
            dialog.seleccionar_pdf()
            mock_warning.assert_called_once()
    
    def test_seleccionar_pdf_exitoso(self, qtbot, controlador_mock):
        """Test seleccionar PDF exitosamente"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        dialog.empresa_edit.setText("Test Corp")
        dialog.importe_spinbox.setValue(1500.50)
        
        with patch('controladores.controlador_facturas_directas.QFileDialog.getOpenFileName') as mock_file:
            mock_file.return_value = ("/path/factura.pdf", "")
            
            dialog.seleccionar_pdf()
            
            assert dialog.archivo_pdf_seleccionado == "factura.pdf"
            assert dialog.btn_quitar_pdf.isEnabled()
            controlador_mock.gestionar_pdf.assert_called_once()
    
    def test_quitar_pdf(self, qtbot, controlador_mock):
        """Test quitar PDF seleccionado"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        dialog.archivo_pdf_seleccionado = "test.pdf"
        dialog.btn_quitar_pdf.setEnabled(True)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            
            dialog.quitar_pdf()
            
            assert dialog.archivo_pdf_seleccionado == ""
            assert not dialog.btn_quitar_pdf.isEnabled()
            controlador_mock.eliminar_pdf.assert_called_once_with("test.pdf")
    
    def test_guardar_factura_campos_vacios(self, qtbot, controlador_mock):
        """Test guardar factura con campos obligatorios vacíos"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.warning') as mock_warning:
            dialog.guardar_factura()
            mock_warning.assert_called_once()
    
    def test_guardar_factura_nueva_exitosa(self, qtbot, controlador_mock):
        """Test guardar nueva factura exitosamente"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        # Llenar campos obligatorios
        dialog.empresa_edit.setText("Test Corp")
        dialog.localidad_edit.setText("Madrid")
        dialog.importe_spinbox.setValue(1500.50)
        dialog.cif_edit.setText("B12345678")
        dialog.categoria_combo.setCurrentText("Agua")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog.guardar_factura()
            
            controlador_mock.agregar_factura.assert_called_once()
            mock_accept.assert_called_once()
    
    def test_guardar_factura_edicion(self, qtbot, controlador_mock):
        """Test guardar factura en modo edición"""
        datos_factura = {"id": 1, "empresa": "Old Corp"}
        dialog = DialogoCrearFactura(None, controlador_mock, datos_factura)
        qtbot.addWidget(dialog)
        
        dialog.empresa_edit.setText("Test Corp")
        dialog.localidad_edit.setText("Madrid")
        dialog.importe_spinbox.setValue(1500.50)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
            dialog.guardar_factura()
            mock_info.assert_called_once()
    
    def test_guardar_factura_error(self, qtbot, controlador_mock):
        """Test error al guardar factura"""
        dialog = DialogoCrearFactura(None, controlador_mock)
        qtbot.addWidget(dialog)
        
        dialog.empresa_edit.setText("Test Corp")
        dialog.localidad_edit.setText("Madrid")
        dialog.importe_spinbox.setValue(1500.50)
        
        controlador_mock.agregar_factura.return_value = False
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.critical') as mock_critical:
            dialog.guardar_factura()
            mock_critical.assert_called_once()


class TestDialogoTablaResumen:
    """Tests para DialogoTablaResumen"""
    
    @pytest.fixture
    def sample_facturas(self):
        """Facturas de ejemplo"""
        return [
            {
                "id": 1,
                "fecha_creacion": "2024-01-15T10:30:00",
                "empresa": "Corp A",
                "cif": "A12345678",
                "importe": 1500.50,
                "estado": "Emitida",
                "categoria": "Agua",
                "localidad": "Madrid",
                "gped": "GP001",
                "identificador_especial": "ESP001",
                "identificacion_admycont": "ADM001",
                "fecha_validacion": "2024-01-15",
                "comentarios": "Comentario largo de prueba para ver truncado",
                "archivo_pdf": "factura1.pdf"
            },
            {
                "id": 2,
                "fecha_creacion": "2024-01-20T14:15:00",
                "empresa": "Corp B",
                "cif": "B87654321",
                "importe": 2500.75,
                "estado": "Pagada",
                "categoria": "Limpieza",
                "localidad": "Barcelona",
                "gped": "GP002",
                "identificador_especial": "ESP002",
                "identificacion_admycont": "ADM002",
                "fecha_validacion": "2024-01-20",
                "comentarios": "Comentario breve",
                "archivo_pdf": ""
            }
        ]
    
    def test_init_dialogo_tabla(self, qtbot, sample_facturas):
        """Test inicialización del diálogo de tabla"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        assert dialog.facturas == sample_facturas
        assert dialog.todas_facturas == sample_facturas
        assert dialog.windowTitle() == "Resumen de Facturación"
        assert dialog.tabla.rowCount() == 2
        assert dialog.tabla.columnCount() == 14
    
    def test_cargar_datos_tabla(self, qtbot, sample_facturas):
        """Test cargar datos en la tabla"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        # Verificar datos de primera fila
        assert dialog.tabla.item(0, 0).text() == "1"  # ID
        assert dialog.tabla.item(0, 1).text() == "2024-01-15"  # Fecha
        assert dialog.tabla.item(0, 2).text() == "Corp A"  # Empresa
        assert dialog.tabla.item(0, 3).text() == "A12345678"  # CIF
        assert dialog.tabla.item(0, 4).text() == "1500.50 €"  # Importe
        assert dialog.tabla.item(0, 5).text() == "Emitida"  # Estado
        assert dialog.tabla.item(0, 6).text() == "Agua"  # Categoría
        
        # Verificar colores de estado
        estado_item = dialog.tabla.item(1, 5)  # Estado "Pagada"
        assert estado_item.text() == "Pagada"
        # Verificar que tiene color de fondo (verde claro para "Pagada")
    
    def test_aplicar_filtros_empresa(self, qtbot, sample_facturas):
        """Test aplicar filtro por empresa"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        dialog.filtro_empresa.setText("Corp A")
        dialog.aplicar_filtros()
        
        assert dialog.tabla.rowCount() == 1
        assert dialog.tabla.item(0, 2).text() == "Corp A"
    
    def test_aplicar_filtros_estado(self, qtbot, sample_facturas):
        """Test aplicar filtro por estado"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        dialog.filtro_estado.setCurrentText("Pagada")
        dialog.aplicar_filtros()
        
        assert dialog.tabla.rowCount() == 1
        assert dialog.tabla.item(0, 5).text() == "Pagada"
    
    def test_aplicar_filtros_fecha(self, qtbot, sample_facturas):
        """Test aplicar filtro por fecha"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        # Filtrar solo enero 16-31 (debe mostrar solo segunda factura)
        dialog.filtro_fecha_desde.setDate(QDate(2024, 1, 16))
        dialog.filtro_fecha_hasta.setDate(QDate(2024, 1, 31))
        dialog.aplicar_filtros()
        
        assert dialog.tabla.rowCount() == 1
        assert dialog.tabla.item(0, 2).text() == "Corp B"
    
    def test_limpiar_filtros(self, qtbot, sample_facturas):
        """Test limpiar todos los filtros"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        # Aplicar filtros
        dialog.filtro_empresa.setText("Corp A")
        dialog.filtro_estado.setCurrentText("Emitida")
        dialog.aplicar_filtros()
        
        assert dialog.tabla.rowCount() == 1
        
        # Limpiar filtros
        dialog.limpiar_filtros()
        
        assert dialog.tabla.rowCount() == 2
        assert dialog.filtro_empresa.text() == ""
        assert dialog.filtro_estado.currentText() == "Todos"
    
    def test_editar_estado_celda_estado(self, qtbot, sample_facturas):
        """Test editar estado haciendo doble clic en columna estado"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        # Mock del parent con controlador
        mock_parent = Mock()
        mock_controlador = Mock()
        mock_controlador.actualizar_estado_factura.return_value = True
        mock_parent.controlador = mock_controlador
        dialog.parent = Mock(return_value=mock_parent)
        
        with patch('controladores.controlador_facturas_directas.QInputDialog.getItem') as mock_input:
            mock_input.return_value = ("Tramitada", True)
            
            with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
                dialog.editar_estado_celda(0, 5)  # Fila 0, columna Estado (5)
                
                mock_controlador.actualizar_estado_factura.assert_called_once_with(1, "Tramitada")
                mock_info.assert_called_once()
    
    def test_editar_estado_celda_otra_columna(self, qtbot, sample_facturas):
        """Test hacer doble clic en otra columna"""
        dialog = DialogoTablaResumen(None, sample_facturas)
        qtbot.addWidget(dialog)
        
        with patch('controladores.controlador_facturas_directas.QMessageBox.information') as mock_info:
            dialog.editar_estado_celda(0, 2)  # Fila 0, columna Empresa (2)
            mock_info.assert_called_once()


@pytest.mark.integration
class TestIntegrationFacturasDirectas:
    """Tests de integración para el sistema de facturas directas"""
    
    @pytest.fixture
    def temp_env(self):
        """Entorno temporal completo"""
        temp_dir = tempfile.mkdtemp()
        
        # Crear estructura de carpetas
        pdf_dir = os.path.join(temp_dir, "pdfactura directa")
        os.makedirs(pdf_dir, exist_ok=True)
        
        yield temp_dir, pdf_dir
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_flujo_completo_factura(self, temp_env):
        """Test flujo completo: crear, listar, actualizar, eliminar factura"""
        temp_dir, pdf_dir = temp_env
        
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = temp_dir
            mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas.json")
            
            controlador = ControladorFacturasDirectas()
            
            # 1. Crear factura
            datos_factura = {
                "empresa": "Empresa Integration Test",
                "cif": "B98765432",
                "importe": 3500.25,
                "categoria": "Actuaciones mantenimiento",
                "localidad": "Valencia",
                "estado": "Emitida",
                "identificador_especial": "INT001",
                "identificacion_admycont": "ADMINT001",
                "fecha_validacion": "2024-03-01",
                "comentarios": "Factura de prueba de integración",
                "gped": "GPINT001"
            }
            
            resultado = controlador.agregar_factura(datos_factura)
            assert resultado is True
            
            # 2. Verificar que se creó
            facturas = controlador.obtener_facturas()
            assert len(facturas) == 1
            factura = facturas[0]
            assert factura["empresa"] == "Empresa Integration Test"
            assert factura["id"] == 1
            
            # 3. Actualizar estado
            resultado = controlador.actualizar_estado_factura(1, "Tramitada")
            assert resultado is True
            
            # 4. Verificar actualización
            facturas = controlador.obtener_facturas()
            assert facturas[0]["estado"] == "Tramitada"
            assert "fecha_modificacion_estado" in facturas[0]
            
            # 5. Eliminar factura
            resultado = controlador.eliminar_factura(1)
            assert resultado is True
            
            # 6. Verificar eliminación (no aparece en activas)
            facturas = controlador.obtener_facturas()
            assert len(facturas) == 0
            
            # 7. Verificar que existe en JSON pero inactiva
            datos = controlador.leer_datos_json()
            factura_eliminada = next(f for f in datos["facturas"] if f["id"] == 1)
            assert factura_eliminada["activa"] is False
            assert "fecha_eliminacion" in factura_eliminada
    
    def test_gestion_pdf_completa(self, temp_env):
        """Test gestión completa de archivos PDF"""
        temp_dir, pdf_dir = temp_env
        
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = temp_dir
            mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas.json")
            
            controlador = ControladorFacturasDirectas()
            
            # 1. Crear archivo PDF temporal
            pdf_origen = os.path.join(temp_dir, "factura_test.pdf")
            with open(pdf_origen, 'w') as f:
                f.write("PDF content test")
            
            # 2. Agregar factura con PDF
            datos_factura = {
                "id": 1,
                "empresa": "PDF Test Corp",
                "importe": 1250.75
            }
            
            nombre_pdf = controlador.gestionar_pdf(pdf_origen, datos_factura)
            expected_name = "1_PDF_Test_Corp_1250,75.pdf"
            assert nombre_pdf == expected_name
            
            # 3. Verificar que se copió correctamente
            pdf_destino = os.path.join(pdf_dir, expected_name)
            assert os.path.exists(pdf_destino)
            
            with open(pdf_destino, 'r') as f:
                assert f.read() == "PDF content test"
            
            # 4. Eliminar PDF
            resultado = controlador.eliminar_pdf(expected_name)
            assert resultado is True
            assert not os.path.exists(pdf_destino)
    
    def test_multiples_facturas_filtros(self, temp_env):
        """Test con múltiples facturas y filtros"""
        temp_dir, pdf_dir = temp_env
        
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = temp_dir
            mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas.json")
            
            controlador = ControladorFacturasDirectas()
            
            # Crear múltiples facturas con diferentes características
            facturas_test = [
                {
                    "empresa": "Agua Madrid S.L.",
                    "categoria": "Agua",
                    "estado": "Emitida",
                    "importe": 1500.00,
                    "localidad": "Madrid",
                    "fecha_validacion": "2024-01-15"
                },
                {
                    "empresa": "Limpieza Barcelona S.A.",
                    "categoria": "Limpieza", 
                    "estado": "Pagada",
                    "importe": 2300.50,
                    "localidad": "Barcelona",
                    "fecha_validacion": "2024-02-01"
                },
                {
                    "empresa": "Mantenimiento Valencia",
                    "categoria": "Actuaciones mantenimiento",
                    "estado": "Tramitada",
                    "importe": 3200.75,
                    "localidad": "Valencia",
                    "fecha_validacion": "2024-02-15"
                }
            ]
            
            # Agregar todas las facturas
            for datos in facturas_test:
                controlador.agregar_factura(datos)
            
            # Verificar que se agregaron todas
            todas_facturas = controlador.obtener_facturas()
            assert len(todas_facturas) == 3
            
            # Verificar total de importes
            total_importe = sum(f["importe"] for f in todas_facturas)
            assert total_importe == 7000.25
            
            # Verificar que los IDs son consecutivos
            ids = [f["id"] for f in todas_facturas]
            assert ids == [1, 2, 3]
            
            # Test estados diversos
            estados = [f["estado"] for f in todas_facturas]
            assert "Emitida" in estados
            assert "Pagada" in estados
            assert "Tramitada" in estados