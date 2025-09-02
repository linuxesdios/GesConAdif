"""
Tests comprehensivos para helpers_py.py
Cobertura objetivo: >90%
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock

# Agregar el directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers_py import (
    es_numero_valido, validar_nif_basico, validar_email_basico,
    validar_datos_empresa, validar_oferta_economica,
    limpiar_nombre_archivo, formatear_numero_espanol,
    resource_path, get_ui_file_path, crear_copia_respaldo_proyecto,
    setup_ui_with_new_structure, abrir_archivo
)


class TestValidaciones:
    """Tests para funciones de validación"""

    @pytest.mark.unit
    def test_es_numero_valido_numeros_correctos(self):
        """Test números válidos"""
        numeros_validos = [
            "123",
            "123.45",
            "0.5",
            "1000000",
            "0",
            "0.0",
            "999999.99",
            "  123.45  ",  # Con espacios
            "123,45"      # Con coma (debe convertirse)
        ]
        
        for numero in numeros_validos:
            assert es_numero_valido(numero) is True, f"Número '{numero}' debería ser válido"

    @pytest.mark.unit
    def test_es_numero_valido_numeros_incorretos(self):
        """Test números inválidos"""
        numeros_invalidos = [
            "",
            "   ",
            "abc",
            "12.34.56",  # Múltiples puntos
            "12..34",     # Puntos consecutivos
            "12,34,56",   # Múltiples comas
            "12.34.56",
            None,
            "NaN",
            "infinity",
            "12a34"
        ]
        
        for numero in numeros_invalidos:
            assert es_numero_valido(numero) is False, f"Número '{numero}' debería ser inválido"

    @pytest.mark.unit
    def test_es_numero_valido_edge_cases(self):
        """Test casos límite"""
        # Números muy grandes
        assert es_numero_valido("999999999999999999") is True
        
        # Números muy pequeños
        assert es_numero_valido("0.000000001") is True
        
        # Números negativos
        assert es_numero_valido("-123.45") is True
        assert es_numero_valido("-0") is True

    @pytest.mark.unit
    def test_validar_nif_basico_nifs_validos(self):
        """Test NIFs con formato válido"""
        nifs_validos = [
            "12345678A",
            "87654321B",
            "11111111H",
            "22222222J",
            "  12345678A  ",  # Con espacios
            "12345678a",      # Minúscula (se convierte)
            "12 345 678 A"    # Con espacios intermedios
        ]
        
        for nif in nifs_validos:
            assert validar_nif_basico(nif) is True, f"NIF '{nif}' debería ser válido"

    @pytest.mark.unit
    def test_validar_nif_basico_nifs_invalidos(self):
        """Test NIFs con formato inválido"""
        nifs_invalidos = [
            "",
            "   ",
            "1234567A",     # 7 dígitos
            "123456789A",   # 9 dígitos
            "12345678",     # Sin letra
            "A12345678",    # Letra al principio
            "1234567AA",    # Dos letras
            "abcdefghA",    # Letras en lugar de números
            "12345678@",    # Carácter especial
            None
        ]
        
        for nif in nifs_invalidos:
            assert validar_nif_basico(nif) is False, f"NIF '{nif}' debería ser inválido"

    @pytest.mark.unit
    def test_validar_email_basico_emails_validos(self):
        """Test emails válidos"""
        emails_validos = [
            "usuario@dominio.com",
            "test@example.org",
            "admin@subdomain.domain.co.uk",
            "user.name@domain.com",
            "user+tag@domain.com",
            "user123@domain123.com",
            "a@b.co"
        ]
        
        for email in emails_validos:
            assert validar_email_basico(email) is True, f"Email '{email}' debería ser válido"

    @pytest.mark.unit
    def test_validar_email_basico_emails_invalidos(self):
        """Test emails inválidos"""
        emails_invalidos = [
            "",
            "   ",
            "usuario",
            "@dominio.com",
            "usuario@",
            "usuario@dominio",
            "usuario.dominio.com",
            "usuario@@dominio.com",
            "usuario@dominio..com",
            "usuario@.dominio.com",
            None
        ]
        
        for email in emails_invalidos:
            assert validar_email_basico(email) is False, f"Email '{email}' debería ser inválido"

    @pytest.mark.unit
    def test_validar_datos_empresa_empresa_valida(self):
        """Test validación de empresa válida"""
        empresa_valida = {
            "nombre": "CONSTRUCTORA EJEMPLO S.L.",
            "nif": "12345678A",
            "email": "contacto@ejemplo.com",
            "contacto": "Juan Pérez"
        }
        
        es_valido, errores = validar_datos_empresa(empresa_valida)
        assert es_valido is True
        assert len(errores) == 0

    @pytest.mark.unit
    def test_validar_datos_empresa_nombre_obligatorio(self):
        """Test empresa sin nombre (obligatorio)"""
        empresa_sin_nombre = {
            "nombre": "",
            "nif": "12345678A",
            "email": "contacto@ejemplo.com"
        }
        
        es_valido, errores = validar_datos_empresa(empresa_sin_nombre)
        assert es_valido is False
        assert "Nombre de empresa es obligatorio" in errores

    @pytest.mark.unit
    def test_validar_datos_empresa_nif_invalido(self):
        """Test empresa con NIF inválido"""
        empresa_nif_invalido = {
            "nombre": "EMPRESA TEST",
            "nif": "123INVALID",
            "email": "contacto@ejemplo.com"
        }
        
        es_valido, errores = validar_datos_empresa(empresa_nif_invalido)
        assert es_valido is False
        assert any("NIF inválido" in error for error in errores)

    @pytest.mark.unit
    def test_validar_datos_empresa_email_invalido(self):
        """Test empresa con email inválido"""
        empresa_email_invalido = {
            "nombre": "EMPRESA TEST",
            "nif": "12345678A",
            "email": "email-invalido"
        }
        
        es_valido, errores = validar_datos_empresa(empresa_email_invalido)
        assert es_valido is False
        assert any("Email inválido" in error for error in errores)

    @pytest.mark.unit
    def test_validar_datos_empresa_multiples_errores(self):
        """Test empresa con múltiples errores"""
        empresa_multiple_errores = {
            "nombre": "",
            "nif": "INVALID",
            "email": "invalid-email"
        }
        
        es_valido, errores = validar_datos_empresa(empresa_multiple_errores)
        assert es_valido is False
        assert len(errores) == 3  # Nombre, NIF y email inválidos

    @pytest.mark.unit
    def test_validar_oferta_economica_ofertas_validas(self):
        """Test ofertas económicas válidas"""
        ofertas_validas = [
            "50000.00",
            "1000",
            "999999.99",
            "0.01",
            "  1500.50  "
        ]
        
        for oferta in ofertas_validas:
            es_valido, valor, mensaje = validar_oferta_economica(oferta)
            assert es_valido is True, f"Oferta '{oferta}' debería ser válida"
            assert isinstance(valor, float)
            assert valor >= 0

    @pytest.mark.unit
    def test_validar_oferta_economica_ofertas_invalidas(self):
        """Test ofertas económicas inválidas"""
        ofertas_invalidas = [
            "",
            "abc",
            "-1000",  # Negativo
            "0",      # Cero
            None
        ]
        
        for oferta in ofertas_invalidas:
            es_valido, valor, mensaje = validar_oferta_economica(oferta)
            assert es_valido is False, f"Oferta '{oferta}' debería ser inválida"
            assert valor is None
            assert isinstance(mensaje, str)


class TestUtilidades:
    """Tests para funciones utilitarias"""

    @pytest.mark.unit
    def test_limpiar_nombre_archivo_caracteres_especiales(self):
        """Test limpieza de nombres de archivo"""
        nombres_sucios = [
            "archivo<>test.pdf",
            'archivo"test".docx',
            "archivo|test.xlsx",
            "archivo?test.txt",
            "archivo*test.pdf"
        ]
        
        for nombre in nombres_sucios:
            nombre_limpio = limpiar_nombre_archivo(nombre)
            # No debe contener caracteres especiales problemáticos
            caracteres_problematicos = '<>:"/\\|?*'
            for char in caracteres_problematicos:
                assert char not in nombre_limpio

    @pytest.mark.unit
    def test_limpiar_nombre_archivo_espacios(self):
        """Test limpieza de espacios en nombres de archivo"""
        assert limpiar_nombre_archivo("archivo con espacios.pdf") == "archivo_con_espacios.pdf"
        assert limpiar_nombre_archivo("  archivo  ") == "archivo"

    @pytest.mark.unit
    def test_limpiar_nombre_archivo_longitud_maxima(self):
        """Test límite de longitud de nombres de archivo"""
        nombre_largo = "a" * 300 + ".pdf"
        nombre_limpio = limpiar_nombre_archivo(nombre_largo, max_length=50)
        assert len(nombre_limpio) <= 50

    @pytest.mark.unit
    def test_formatear_numero_espanol_enteros(self):
        """Test formateo de números enteros al español"""
        assert formatear_numero_espanol(1000) == "1.000"
        assert formatear_numero_espanol(1000000) == "1.000.000"
        assert formatear_numero_espanol(123) == "123"

    @pytest.mark.unit
    def test_formatear_numero_espanol_decimales(self):
        """Test formateo de números decimales al español"""
        assert formatear_numero_espanol(1000.50) == "1.000,50"
        assert formatear_numero_espanol(1234.56) == "1.234,56"
        assert formatear_numero_espanol(0.5) == "0,50"

    @pytest.mark.unit
    def test_formatear_numero_espanol_casos_especiales(self):
        """Test casos especiales de formateo"""
        assert formatear_numero_espanol(0) == "0"
        assert formatear_numero_espanol(-1000) == "-1.000"
        assert formatear_numero_espanol(-1234.56) == "-1.234,56"


class TestGestionArchivos:
    """Tests para gestión de archivos"""

    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_resource_path_archivo_existente(self, mock_isfile, mock_exists):
        """Test resource_path con archivo existente"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        path = resource_path("test_file.txt")
        assert path is not None

    @pytest.mark.unit
    @patch('os.path.exists')
    def test_resource_path_archivo_no_existente(self, mock_exists):
        """Test resource_path con archivo no existente"""
        mock_exists.return_value = False
        
        path = resource_path("archivo_inexistente.txt")
        # Debe devolver la ruta relativa aunque no exista
        assert "archivo_inexistente.txt" in path

    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_get_ui_file_path_archivo_ui(self, mock_isfile, mock_exists):
        """Test búsqueda de archivo UI"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        path = get_ui_file_path("test.ui")
        assert path is not None
        assert path.endswith(".ui")

    @pytest.mark.unit
    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_crear_copia_respaldo_proyecto(self, mock_exists, mock_copy):
        """Test creación de copia de respaldo"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            resultado = crear_copia_respaldo_proyecto(temp_file.name)
            assert resultado is True

    @pytest.mark.unit
    @patch('os.path.exists')
    def test_crear_copia_respaldo_archivo_no_existente(self, mock_exists):
        """Test respaldo de archivo no existente"""
        mock_exists.return_value = False
        
        resultado = crear_copia_respaldo_proyecto("archivo_inexistente.json")
        assert resultado is False

    @pytest.mark.unit
    @patch('webbrowser.open')
    @patch('os.path.exists')
    def test_abrir_archivo_existente(self, mock_exists, mock_browser):
        """Test abrir archivo existente"""
        mock_exists.return_value = True
        mock_browser.return_value = None
        
        # Debe ejecutarse sin errores
        abrir_archivo("test.pdf")
        mock_browser.assert_called_once()

    @pytest.mark.unit
    @patch('os.path.exists')
    def test_abrir_archivo_no_existente(self, mock_exists):
        """Test abrir archivo no existente"""
        mock_exists.return_value = False
        
        # No debe lanzar excepción
        resultado = abrir_archivo("archivo_inexistente.pdf")
        # La función puede devolver False o None dependiendo de la implementación


class TestSetupUI:
    """Tests para configuración de UI"""

    @pytest.mark.unit
    @patch('PyQt5.uic.loadUi')
    def test_setup_ui_with_new_structure_carga_correcta(self, mock_load_ui):
        """Test carga correcta de estructura UI"""
        mock_widget = Mock()
        mock_load_ui.return_value = mock_widget
        
        with patch('helpers_py.get_ui_file_path', return_value="test.ui"):
            resultado = setup_ui_with_new_structure("test.ui", Mock())
            assert resultado is not None

    @pytest.mark.unit
    @patch('PyQt5.uic.loadUi')
    def test_setup_ui_with_new_structure_error_carga(self, mock_load_ui):
        """Test error en carga de UI"""
        mock_load_ui.side_effect = Exception("Error de carga")
        
        with patch('helpers_py.get_ui_file_path', return_value="test.ui"):
            # No debe lanzar excepción, debe manejarla internamente
            resultado = setup_ui_with_new_structure("test.ui", Mock())


class TestIntegracionHelpers:
    """Tests de integración para múltiples funciones"""

    @pytest.mark.integration
    def test_flujo_validacion_completa_empresa(self):
        """Test flujo completo de validación de empresa"""
        # 1. Datos de entrada
        datos_empresa = {
            "nombre": "CONSTRUCTORA INTEGRAL S.L.",
            "nif": "12345678A",
            "email": "info@constructora.com",
            "contacto": "Ana García Martínez"
        }
        
        # 2. Validaciones individuales
        assert validar_nif_basico(datos_empresa["nif"]) is True
        assert validar_email_basico(datos_empresa["email"]) is True
        
        # 3. Validación completa
        es_valido, errores = validar_datos_empresa(datos_empresa)
        assert es_valido is True
        assert len(errores) == 0

    @pytest.mark.integration
    def test_procesamiento_oferta_completo(self):
        """Test procesamiento completo de oferta económica"""
        # 1. Validar formato de número
        oferta_str = "45.678,50"  # Formato español
        assert es_numero_valido(oferta_str.replace(',', '.')) is True
        
        # 2. Validar oferta económica
        es_valido, valor, mensaje = validar_oferta_economica(oferta_str.replace(',', '.'))
        assert es_valido is True
        assert valor == 45678.50
        
        # 3. Formatear para mostrar
        formato_espanol = formatear_numero_espanol(valor)
        assert "45.678,50" in formato_espanol

    @pytest.mark.integration
    @patch('os.path.exists')
    @patch('shutil.copy2')
    def test_flujo_completo_gestion_archivos(self, mock_copy, mock_exists):
        """Test flujo completo de gestión de archivos"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        
        # 1. Limpiar nombre de archivo
        nombre_sucio = "Proyecto: <Test> | Versión #1.json"
        nombre_limpio = limpiar_nombre_archivo(nombre_sucio)
        assert "<" not in nombre_limpio
        assert "|" not in nombre_limpio
        
        # 2. Crear respaldo
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            resultado = crear_copia_respaldo_proyecto(temp_path)
            # El mock simula éxito
            assert resultado is True
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# Marks para diferentes tipos de test
pytestmark = pytest.mark.unit