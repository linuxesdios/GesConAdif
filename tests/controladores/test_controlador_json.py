"""
Tests comprehensivos para controlador_json.py
Cobertura actual: 36% - Objetivo: >85%
"""
import pytest
import os
import sys
import json
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock

# Agregar el directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from controladores.controlador_json import GestorJsonUnificado


class TestGestorJsonUnificadoInicializacion:
    """Tests para inicialización del GestorJsonUnificado"""
    
    @pytest.mark.unit
    def test_inicializacion_sin_parametros(self):
        """Test inicialización por defecto"""
        with patch('controladores.controlador_json.rutas') as mock_rutas:
            mock_rutas.get_ruta_base_datos.return_value = "BaseDatos.json"
            
            with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value={}):
                gestor = GestorJsonUnificado()
                
                assert gestor.main_window is None
                assert gestor.ruta_archivo == "BaseDatos.json"
                assert gestor.datos == {}
    
    @pytest.mark.unit
    def test_inicializacion_con_parametros(self):
        """Test inicialización con parámetros"""
        mock_window = Mock()
        ruta_personalizada = "/ruta/custom.json"
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value={"test": "data"}):
            gestor = GestorJsonUnificado(ruta_personalizada, mock_window)
            
            assert gestor.main_window == mock_window
            assert gestor.ruta_archivo == ruta_personalizada
            assert gestor.datos == {"test": "data"}
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open)
    def test_cargar_datos_iniciales_archivo_existente(self, mock_file, mock_getsize, mock_exists):
        """Test carga de datos desde archivo existente"""
        mock_exists.return_value = True
        mock_getsize.return_value = 100
        
        datos_test = {"firmantes": {}, "obras": [{"nombreObra": "TEST"}]}
        mock_file.return_value.read.return_value = json.dumps(datos_test)
        
        with patch('json.load', return_value=datos_test):
            gestor = GestorJsonUnificado()
            
            assert gestor.datos == datos_test
    
    @pytest.mark.unit
    @patch('os.path.exists')
    def test_cargar_datos_iniciales_archivo_no_existente(self, mock_exists):
        """Test creación de estructura inicial cuando archivo no existe"""
        mock_exists.return_value = False
        
        gestor = GestorJsonUnificado()
        
        # Debe crear estructura inicial
        assert "firmantes" in gestor.datos
        assert "obras" in gestor.datos
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.path.getsize') 
    @patch('builtins.open', side_effect=OSError("Error de archivo"))
    def test_cargar_datos_iniciales_error_lectura(self, mock_file, mock_getsize, mock_exists):
        """Test manejo de error en lectura de archivo"""
        mock_exists.return_value = True
        mock_getsize.return_value = 100
        
        gestor = GestorJsonUnificado()
        
        # Debe crear estructura por defecto en caso de error
        assert gestor.datos == {"firmantes": {}, "obras": []}


class TestOperacionesGuardado:
    """Tests para operaciones de guardado"""
    
    @pytest.fixture
    def gestor_mock(self):
        """Fixture con gestor básico"""
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value={"obras": []}):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_guardar_datos_exitoso(self, mock_json_dump, mock_file, mock_makedirs, gestor_mock):
        """Test guardado exitoso de datos"""
        gestor_mock.datos = {"test": "data"}
        
        resultado = gestor_mock.guardar_datos()
        
        assert resultado is True
        mock_json_dump.assert_called_once_with(
            {"test": "data"}, mock_file.return_value, ensure_ascii=False, indent=2
        )
    
    @pytest.mark.unit
    @patch('os.makedirs', side_effect=OSError("Error directorio"))
    def test_guardar_datos_error_directorio(self, mock_makedirs, gestor_mock):
        """Test error creando directorio"""
        resultado = gestor_mock.guardar_datos()
        
        assert resultado is False
    
    @pytest.mark.unit
    @patch('os.makedirs')
    @patch('builtins.open', side_effect=OSError("Error archivo"))
    def test_guardar_datos_error_archivo(self, mock_file, mock_makedirs, gestor_mock):
        """Test error escribiendo archivo"""
        resultado = gestor_mock.guardar_datos()
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_recargar_datos_exitoso(self, gestor_mock):
        """Test recarga exitosa de datos"""
        nuevos_datos = {"nuevos": "datos"}
        
        with patch.object(gestor_mock, '_cargar_datos_iniciales', return_value=nuevos_datos):
            resultado = gestor_mock.recargar_datos()
            
            assert resultado is True
            assert gestor_mock.datos == nuevos_datos
    
    @pytest.mark.unit
    def test_recargar_datos_error(self, gestor_mock):
        """Test error en recarga de datos"""
        with patch.object(gestor_mock, '_cargar_datos_iniciales', side_effect=Exception("Error")):
            resultado = gestor_mock.recargar_datos()
            
            assert resultado is False


class TestOperacionesBusqueda:
    """Tests para operaciones de búsqueda"""
    
    @pytest.fixture
    def gestor_con_datos(self):
        """Fixture con gestor con datos de prueba"""
        datos_test = {
            "obras": [
                {
                    "nombreObra": "REPARACIÓN EDIFICIO A",
                    "numeroExpediente": "EXP-2024-001",
                    "tipoContrato": "obra"
                },
                {
                    "nombreObra": "MANTENIMIENTO EDIFICIO B",
                    "numeroExpediente": "EXP-2024-002", 
                    "tipoContrato": "servicio"
                },
                {
                    "nombreObra": "OBRAS DE REFORMA...",  # Nombre truncado
                    "numeroExpediente": "EXP-2024-003",
                    "tipoContrato": "obra"
                }
            ]
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_buscar_contrato_por_nombre_exacto(self, gestor_con_datos):
        """Test búsqueda por nombre exacto"""
        resultado = gestor_con_datos.buscar_contrato_por_nombre("REPARACIÓN EDIFICIO A")
        
        assert resultado is not None
        assert resultado["nombreObra"] == "REPARACIÓN EDIFICIO A"
        assert resultado["numeroExpediente"] == "EXP-2024-001"
    
    @pytest.mark.unit
    def test_buscar_contrato_por_nombre_no_encontrado(self, gestor_con_datos):
        """Test búsqueda de contrato inexistente"""
        resultado = gestor_con_datos.buscar_contrato_por_nombre("CONTRATO_INEXISTENTE")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_buscar_contrato_por_nombre_truncado(self, gestor_con_datos):
        """Test búsqueda por nombre truncado con '...'"""
        resultado = gestor_con_datos.buscar_contrato_por_nombre("OBRAS DE REFORMA...")
        
        assert resultado is not None
        assert resultado["numeroExpediente"] == "EXP-2024-003"
    
    @pytest.mark.unit
    def test_buscar_contrato_por_expediente_existente(self, gestor_con_datos):
        """Test búsqueda por expediente existente"""
        resultado = gestor_con_datos.buscar_contrato_por_expediente("EXP-2024-002")
        
        assert resultado is not None
        assert resultado["nombreObra"] == "MANTENIMIENTO EDIFICIO B"
    
    @pytest.mark.unit
    def test_buscar_contrato_por_expediente_no_existente(self, gestor_con_datos):
        """Test búsqueda por expediente inexistente"""
        resultado = gestor_con_datos.buscar_contrato_por_expediente("EXP-9999-999")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_buscar_contrato_inteligente_por_nombre(self, gestor_con_datos):
        """Test búsqueda inteligente por nombre"""
        resultado = gestor_con_datos.buscar_contrato_inteligente("REPARACIÓN EDIFICIO A")
        
        assert resultado is not None
        assert resultado["nombreObra"] == "REPARACIÓN EDIFICIO A"
    
    @pytest.mark.unit
    def test_buscar_contrato_inteligente_por_expediente(self, gestor_con_datos):
        """Test búsqueda inteligente por expediente"""
        resultado = gestor_con_datos.buscar_contrato_inteligente("EXP-2024-001")
        
        assert resultado is not None
        assert resultado["numeroExpediente"] == "EXP-2024-001"
    
    @pytest.mark.unit
    def test_buscar_contrato_inteligente_entrada_vacia(self, gestor_con_datos):
        """Test búsqueda inteligente con entrada vacía"""
        assert gestor_con_datos.buscar_contrato_inteligente("") is None
        assert gestor_con_datos.buscar_contrato_inteligente("   ") is None
        assert gestor_con_datos.buscar_contrato_inteligente(None) is None


class TestOperacionesListado:
    """Tests para operaciones de listado"""
    
    @pytest.fixture
    def gestor_con_obras(self):
        """Fixture con obras de prueba"""
        datos_test = {
            "obras": [
                {"nombreObra": "OBRA A", "numeroExpediente": "001", "tipoContrato": "obra"},
                {"nombreObra": "OBRA B", "numeroExpediente": "002", "tipoContrato": "servicio"},
                {"nombreObra": "", "numeroExpediente": "003", "tipoContrato": "obra"},  # Sin nombre
            ]
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_listar_contratos(self, gestor_con_obras):
        """Test listado de contratos"""
        resultado = gestor_con_obras.listar_contratos()
        
        # Debe filtrar obras sin nombre
        assert len(resultado) == 2
        assert resultado[0]["nombreObra"] == "OBRA A"
        assert resultado[1]["nombreObra"] == "OBRA B"
    
    @pytest.mark.unit
    def test_obtener_nombres_obras(self, gestor_con_obras):
        """Test obtener nombres de obras"""
        resultado = gestor_con_obras.obtener_nombres_obras()
        
        assert len(resultado) == 2
        assert "OBRA A" in resultado
        assert "OBRA B" in resultado
        assert "" not in resultado  # Sin nombres vacíos
    
    @pytest.mark.unit
    def test_obtener_nombres_obras_vacio(self):
        """Test obtener nombres cuando no hay obras"""
        datos_vacios = {"obras": []}
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_vacios):
            gestor = GestorJsonUnificado()
            resultado = gestor.obtener_nombres_obras()
            
            assert resultado == []
    
    @pytest.mark.unit
    def test_cargar_datos_obra_existente(self, gestor_con_obras):
        """Test cargar datos de obra existente"""
        resultado = gestor_con_obras.cargar_datos_obra("OBRA A")
        
        assert resultado is not None
        assert resultado["nombreObra"] == "OBRA A"
        assert resultado["numeroExpediente"] == "001"
    
    @pytest.mark.unit
    def test_cargar_datos_obra_no_existente(self, gestor_con_obras):
        """Test cargar datos de obra inexistente"""
        resultado = gestor_con_obras.cargar_datos_obra("OBRA_INEXISTENTE")
        
        assert resultado == {}


class TestOperacionesActualizacion:
    """Tests para operaciones de actualización"""
    
    @pytest.fixture
    def gestor_actualizable(self):
        """Fixture con gestor para actualización"""
        datos_test = {
            "obras": [
                {
                    "nombreObra": "OBRA_ACTUALIZABLE",
                    "basePresupuesto": "50000",
                    "fechaModificacion": "2024-01-01 12:00:00"
                }
            ]
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_actualizar_contrato_exitoso(self, gestor_actualizable):
        """Test actualización exitosa de contrato"""
        with patch.object(gestor_actualizable, 'guardar_datos', return_value=True):
            datos_actualizados = {"basePresupuesto": "75000", "nuevoCampo": "valor"}
            
            resultado = gestor_actualizable.actualizar_contrato("OBRA_ACTUALIZABLE", datos_actualizados)
            
            assert resultado is True
            
            # Verificar que los datos se actualizaron
            obra = gestor_actualizable.datos["obras"][0]
            assert obra["basePresupuesto"] == "75000"
            assert obra["nuevoCampo"] == "valor"
            
            # Debe actualizar fecha de modificación
            assert obra["fechaModificacion"] != "2024-01-01 12:00:00"
    
    @pytest.mark.unit
    def test_actualizar_contrato_no_existente(self, gestor_actualizable):
        """Test actualización de contrato inexistente"""
        with patch.object(gestor_actualizable, 'guardar_datos', return_value=True):
            resultado = gestor_actualizable.actualizar_contrato("OBRA_INEXISTENTE", {"campo": "valor"})
            
            assert resultado is False
    
    @pytest.mark.unit
    def test_actualizar_contrato_error_guardado(self, gestor_actualizable):
        """Test error en guardado durante actualización"""
        with patch.object(gestor_actualizable, 'guardar_datos', return_value=False):
            resultado = gestor_actualizable.actualizar_contrato("OBRA_ACTUALIZABLE", {"campo": "valor"})
            
            assert resultado is False
    
    @pytest.mark.unit
    def test_actualizar_contrato_sin_nombre(self, gestor_actualizable):
        """Test actualización sin nombre de contrato"""
        resultado = gestor_actualizable.actualizar_contrato("", {"campo": "valor"})
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_actualizar_contrato_sin_guardado_inmediato(self, gestor_actualizable):
        """Test actualización sin guardado inmediato"""
        resultado = gestor_actualizable.actualizar_contrato(
            "OBRA_ACTUALIZABLE", 
            {"basePresupuesto": "60000"}, 
            guardar_inmediato=False
        )
        
        assert resultado is True
        
        # Debe actualizar datos pero no guardar
        obra = gestor_actualizable.datos["obras"][0]
        assert obra["basePresupuesto"] == "60000"
    
    @pytest.mark.unit
    def test_guardar_campo_en_json_exitoso(self, gestor_actualizable):
        """Test guardado de campo específico"""
        with patch.object(gestor_actualizable, 'actualizar_contrato', return_value=True):
            resultado = gestor_actualizable.guardar_campo_en_json(
                "OBRA_ACTUALIZABLE", 
                "plazoEjecucion", 
                "90"
            )
            
            assert resultado is True
    
    @pytest.mark.unit
    def test_guardar_campo_en_json_contrato_no_encontrado(self, gestor_actualizable):
        """Test guardado de campo en contrato inexistente"""
        resultado = gestor_actualizable.guardar_campo_en_json("OBRA_INEXISTENTE", "campo", "valor")
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_guardar_campo_en_json_parametros_vacios(self, gestor_actualizable):
        """Test guardado con parámetros vacíos"""
        assert gestor_actualizable.guardar_campo_en_json("", "campo", "valor") is False
        assert gestor_actualizable.guardar_campo_en_json("OBRA", "", "valor") is False


class TestOperacionesEmpresas:
    """Tests para operaciones con empresas"""
    
    @pytest.fixture
    def gestor_con_empresas(self):
        """Fixture con gestor que maneja empresas"""
        datos_test = {"obras": [{"nombreObra": "OBRA_CON_EMPRESAS", "empresas": []}]}
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_guardar_empresas_unificadas_exitoso(self, gestor_con_empresas):
        """Test guardado de empresas en formato unificado"""
        empresas_data = [
            {"nombre": "EMPRESA A", "nif": "A12345678"},
            {"nombre": "EMPRESA B", "nif": "B87654321"}
        ]
        
        with patch.object(gestor_con_empresas, 'actualizar_contrato', return_value=True):
            resultado = gestor_con_empresas.guardar_empresas_unificadas_en_json(
                "OBRA_CON_EMPRESAS", empresas_data
            )
            
            assert resultado is True
    
    @pytest.mark.unit
    def test_guardar_empresas_unificadas_sin_nombre_contrato(self, gestor_con_empresas):
        """Test guardado sin nombre de contrato"""
        empresas_data = [{"nombre": "EMPRESA A"}]
        
        resultado = gestor_con_empresas.guardar_empresas_unificadas_en_json("", empresas_data)
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_guardar_empresas_en_json_compatibilidad(self, gestor_con_empresas):
        """Test método de compatibilidad para empresas"""
        empresas_data = [{"nombre": "EMPRESA TEST"}]
        
        with patch.object(gestor_con_empresas, 'guardar_empresas_unificadas_en_json', return_value=True) as mock_unificado:
            resultado = gestor_con_empresas.guardar_empresas_en_json("OBRA_CON_EMPRESAS", empresas_data)
            
            assert resultado is True
            mock_unificado.assert_called_once_with("OBRA_CON_EMPRESAS", empresas_data)


class TestOperacionesLectura:
    """Tests para operaciones de lectura"""
    
    @pytest.fixture
    def gestor_lectura(self):
        """Fixture para tests de lectura"""
        datos_test = {
            "obras": [
                {
                    "nombreObra": "OBRA_LECTURA",
                    "basePresupuesto": "40000",
                    "plazoEjecucion": "45",
                    "empresas": [{"nombre": "EMPRESA X"}]
                }
            ]
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_leer_contrato_completo_existente(self, gestor_lectura):
        """Test lectura completa de contrato existente"""
        resultado = gestor_lectura.leer_contrato_completo("OBRA_LECTURA")
        
        assert resultado is not None
        assert resultado["nombreObra"] == "OBRA_LECTURA"
        assert resultado["basePresupuesto"] == "40000"
        assert len(resultado["empresas"]) == 1
    
    @pytest.mark.unit
    def test_leer_contrato_completo_no_existente(self, gestor_lectura):
        """Test lectura de contrato inexistente"""
        resultado = gestor_lectura.leer_contrato_completo("OBRA_INEXISTENTE")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_leer_campo_contrato_existente(self, gestor_lectura):
        """Test lectura de campo específico"""
        resultado = gestor_lectura.leer_campo_contrato("OBRA_LECTURA", "basePresupuesto")
        
        assert resultado == "40000"
    
    @pytest.mark.unit
    def test_leer_campo_contrato_campo_no_existente(self, gestor_lectura):
        """Test lectura de campo inexistente"""
        resultado = gestor_lectura.leer_campo_contrato("OBRA_LECTURA", "campoInexistente")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_leer_campo_contrato_no_existente(self, gestor_lectura):
        """Test lectura de campo de contrato inexistente"""
        resultado = gestor_lectura.leer_campo_contrato("OBRA_INEXISTENTE", "basePresupuesto")
        
        assert resultado is None


class TestOperacionesEscritura:
    """Tests para operaciones de escritura de contratos"""
    
    @pytest.fixture
    def gestor_escritura(self):
        """Fixture para tests de escritura"""
        datos_test = {"obras": []}
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_guardar_contrato_nuevo(self, gestor_escritura):
        """Test guardado de nuevo contrato"""
        nuevo_contrato = {
            "nombreObra": "NUEVO_CONTRATO",
            "basePresupuesto": "30000",
            "tipoContrato": "servicio"
        }
        
        with patch.object(gestor_escritura, 'guardar_datos', return_value=True):
            resultado = gestor_escritura.guardar_contrato(nuevo_contrato)
            
            assert resultado is True
            assert len(gestor_escritura.datos["obras"]) == 1
            assert gestor_escritura.datos["obras"][0]["nombreObra"] == "NUEVO_CONTRATO"
    
    @pytest.mark.unit
    def test_guardar_contrato_actualizar_existente(self, gestor_escritura):
        """Test actualización de contrato existente"""
        # Crear contrato inicial
        contrato_inicial = {"nombreObra": "CONTRATO_EXISTENTE", "basePresupuesto": "20000"}
        gestor_escritura.datos["obras"] = [contrato_inicial]
        
        # Actualizar contrato
        contrato_actualizado = {
            "nombreObra": "CONTRATO_EXISTENTE", 
            "basePresupuesto": "25000",
            "nuevoCampo": "nuevo_valor"
        }
        
        with patch.object(gestor_escritura, 'guardar_datos', return_value=True):
            resultado = gestor_escritura.guardar_contrato(contrato_actualizado)
            
            assert resultado is True
            assert len(gestor_escritura.datos["obras"]) == 1  # No debe duplicarse
            assert gestor_escritura.datos["obras"][0]["basePresupuesto"] == "25000"
            assert gestor_escritura.datos["obras"][0]["nuevoCampo"] == "nuevo_valor"
    
    @pytest.mark.unit
    def test_guardar_contrato_sin_nombre_obra(self, gestor_escritura):
        """Test error guardando contrato sin nombreObra"""
        contrato_sin_nombre = {"basePresupuesto": "30000"}
        
        resultado = gestor_escritura.guardar_contrato(contrato_sin_nombre)
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_eliminar_contrato_existente(self, gestor_escritura):
        """Test eliminación de contrato existente"""
        # Agregar contratos de prueba
        gestor_escritura.datos["obras"] = [
            {"nombreObra": "CONTRATO_A"},
            {"nombreObra": "CONTRATO_B"},
            {"nombreObra": "CONTRATO_C"}
        ]
        
        with patch.object(gestor_escritura, 'guardar_datos', return_value=True):
            resultado = gestor_escritura.eliminar_contrato("CONTRATO_B")
            
            assert resultado is True
            assert len(gestor_escritura.datos["obras"]) == 2
            nombres = [obra["nombreObra"] for obra in gestor_escritura.datos["obras"]]
            assert "CONTRATO_B" not in nombres
            assert "CONTRATO_A" in nombres
            assert "CONTRATO_C" in nombres
    
    @pytest.mark.unit
    def test_eliminar_contrato_no_existente(self, gestor_escritura):
        """Test eliminación de contrato inexistente"""
        gestor_escritura.datos["obras"] = [{"nombreObra": "CONTRATO_A"}]
        
        resultado = gestor_escritura.eliminar_contrato("CONTRATO_INEXISTENTE")
        
        assert resultado is False
        assert len(gestor_escritura.datos["obras"]) == 1  # No debe cambiar


class TestOperacionesFirmantes:
    """Tests para operaciones con firmantes"""
    
    @pytest.fixture
    def gestor_firmantes(self):
        """Fixture con firmantes de prueba"""
        datos_test = {
            "firmantes": {
                "firmanteConforme": "Juan Pérez",
                "cargoConforme": "Técnico",
                "firmanteAprueba": "María García",
                "cargoAprueba": "Director"
            },
            "obras": []
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_obtener_firmantes(self, gestor_firmantes):
        """Test obtener datos de firmantes"""
        resultado = gestor_firmantes.obtener_firmantes()
        
        assert resultado["firmanteConforme"] == "Juan Pérez"
        assert resultado["cargoConforme"] == "Técnico"
        assert resultado["firmanteAprueba"] == "María García"
        assert resultado["cargoAprueba"] == "Director"
    
    @pytest.mark.unit
    def test_actualizar_firmantes_exitoso(self, gestor_firmantes):
        """Test actualización exitosa de firmantes"""
        nuevos_firmantes = {
            "firmanteConforme": "Carlos López",
            "cargoConforme": "Ingeniero",
            "firmanteAprueba": "Ana Martín",
            "cargoAprueba": "Gerente"
        }
        
        with patch.object(gestor_firmantes, 'guardar_datos', return_value=True):
            resultado = gestor_firmantes.actualizar_firmantes(nuevos_firmantes)
            
            assert resultado is True
            assert gestor_firmantes.datos["firmantes"]["firmanteConforme"] == "Carlos López"
            assert gestor_firmantes.datos["firmantes"]["cargoConforme"] == "Ingeniero"
    
    @pytest.mark.unit
    def test_actualizar_firmantes_error_guardado(self, gestor_firmantes):
        """Test error en guardado de firmantes"""
        nuevos_firmantes = {"firmanteConforme": "Nuevo Firmante"}
        
        with patch.object(gestor_firmantes, 'guardar_datos', return_value=False):
            resultado = gestor_firmantes.actualizar_firmantes(nuevos_firmantes)
            
            assert resultado is False


class TestUtilidades:
    """Tests para métodos utilitarios"""
    
    @pytest.fixture
    def gestor_utilidades(self):
        """Fixture para tests de utilidades"""
        datos_test = {
            "obras": [
                {"nombreObra": "OBRA A", "tipoContrato": "servicio"},
                {"nombreObra": "OBRA B", "tipoContrato": "obra"},
                {"nombreObra": "OBRA C", "tipoContrato": "servicio"},
                {"nombreObra": "OBRA D", "tipoContrato": "obra"}
            ]
        }
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_test):
            return GestorJsonUnificado()
    
    @pytest.mark.unit
    def test_esta_disponible_con_datos(self, gestor_utilidades):
        """Test verificación de disponibilidad con datos"""
        assert gestor_utilidades.esta_disponible() is True
    
    @pytest.mark.unit
    def test_esta_disponible_sin_datos(self):
        """Test verificación de disponibilidad sin datos"""
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=None):
            gestor = GestorJsonUnificado()
            assert gestor.esta_disponible() is False
    
    @pytest.mark.unit
    def test_obtener_estadisticas(self, gestor_utilidades):
        """Test obtener estadísticas de obras"""
        resultado = gestor_utilidades.obtener_estadisticas()
        
        assert resultado["total_obras"] == 4
        assert resultado["obras_servicio"] == 2
        assert resultado["obras_construccion"] == 2


class TestIntegracionGestorJson:
    """Tests de integración para flujos completos"""
    
    @pytest.mark.integration
    def test_flujo_completo_crear_actualizar_eliminar_contrato(self):
        """Test flujo completo CRUD de contrato"""
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value={"obras": []}):
            gestor = GestorJsonUnificado()
        
        # 1. Crear contrato
        nuevo_contrato = {
            "nombreObra": "CONTRATO_INTEGRACIÓN",
            "basePresupuesto": "45000",
            "tipoContrato": "obra"
        }
        
        with patch.object(gestor, 'guardar_datos', return_value=True):
            # Crear
            assert gestor.guardar_contrato(nuevo_contrato) is True
            assert len(gestor.datos["obras"]) == 1
            
            # Leer
            contrato_leido = gestor.leer_contrato_completo("CONTRATO_INTEGRACIÓN")
            assert contrato_leido["basePresupuesto"] == "45000"
            
            # Actualizar
            assert gestor.actualizar_contrato("CONTRATO_INTEGRACIÓN", {"basePresupuesto": "50000"}) is True
            contrato_actualizado = gestor.leer_contrato_completo("CONTRATO_INTEGRACIÓN")
            assert contrato_actualizado["basePresupuesto"] == "50000"
            
            # Eliminar
            assert gestor.eliminar_contrato("CONTRATO_INTEGRACIÓN") is True
            assert len(gestor.datos["obras"]) == 0
    
    @pytest.mark.integration
    def test_flujo_completo_gestion_empresas(self):
        """Test flujo completo de gestión de empresas"""
        datos_iniciales = {"obras": [{"nombreObra": "OBRA_EMPRESAS", "empresas": []}]}
        
        with patch.object(GestorJsonUnificado, '_cargar_datos_iniciales', return_value=datos_iniciales):
            gestor = GestorJsonUnificado()
        
        empresas_test = [
            {"nombre": "EMPRESA A", "nif": "A11111111", "oferta": "40000"},
            {"nombre": "EMPRESA B", "nif": "B22222222", "oferta": "42000"}
        ]
        
        with patch.object(gestor, 'actualizar_contrato', return_value=True):
            # Guardar empresas
            resultado = gestor.guardar_empresas_unificadas_en_json("OBRA_EMPRESAS", empresas_test)
            assert resultado is True
            
            # Verificar que se puede leer el contrato completo
            contrato = gestor.leer_contrato_completo("OBRA_EMPRESAS")
            assert contrato is not None


# Marks para organizar tests  
pytestmark = [pytest.mark.critical, pytest.mark.unit]