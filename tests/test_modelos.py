"""
Tests comprehensivos para modelos_py.py
Cobertura objetivo: >90%
"""
import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, Mock

# Importar clases del modelo
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelos_py import (
    TipoContrato, EstadoOferta, Empresa, DatosContrato, 
    Oferta, DatosLiquidacion, Proyecto, Constantes
)


class TestTipoContrato:
    """Tests para enum TipoContrato"""
    
    @pytest.mark.unit
    def test_tipo_contrato_valores_correctos(self):
        """Test que verifica los valores correctos del enum"""
        assert TipoContrato.SERVICIO.value == "servicio"
        assert TipoContrato.OBRA.value == "obra"
    
    @pytest.mark.unit
    def test_tipo_contrato_miembros(self):
        """Test que verifica que el enum tiene los miembros esperados"""
        assert len(TipoContrato) == 2
        assert TipoContrato.SERVICIO in TipoContrato
        assert TipoContrato.OBRA in TipoContrato


class TestEstadoOferta:
    """Tests para enum EstadoOferta"""
    
    @pytest.mark.unit
    def test_estado_oferta_valores_correctos(self):
        """Test que verifica los valores correctos del enum"""
        assert EstadoOferta.NO_PRESENTADA.value == "no_presentada"
        assert EstadoOferta.PRESENTADA.value == "presentada"
        assert EstadoOferta.ADJUDICADA.value == "adjudicada"
        assert EstadoOferta.RECHAZADA.value == "rechazada"
    
    @pytest.mark.unit
    def test_estado_oferta_todos_los_miembros(self):
        """Test que verifica todos los estados posibles"""
        assert len(EstadoOferta) == 4


class TestEmpresa:
    """Tests comprehensivos para la clase Empresa"""
    
    @pytest.mark.unit
    def test_empresa_inicializacion_vacia(self):
        """Test inicialización por defecto"""
        empresa = Empresa()
        assert empresa.nombre == ""
        assert empresa.nif == ""
        assert empresa.email == ""
        assert empresa.contacto == ""
        assert empresa.oferta is None
    
    @pytest.mark.unit
    def test_empresa_inicializacion_con_datos(self):
        """Test inicialización con datos completos"""
        empresa = Empresa(
            nombre="CONSTRUCTORA TEST S.L.",
            nif="B12345678",
            email="test@constructora.com",
            contacto="Juan Pérez",
            oferta=50000.0
        )
        assert empresa.nombre == "CONSTRUCTORA TEST S.L."
        assert empresa.nif == "B12345678"
        assert empresa.email == "test@constructora.com"
        assert empresa.contacto == "Juan Pérez"
        assert empresa.oferta == 50000.0
    
    @pytest.mark.unit
    def test_validar_correo_basico_correo_valido(self):
        """Test validación de correo válido"""
        emails_validos = [
            "test@example.com",
            "user.name@domain.co.uk",
            "contact+info@empresa.es",
            "admin@subdomain.domain.org"
        ]
        for email in emails_validos:
            assert Empresa.validar_correo_basico(email) is True
    
    @pytest.mark.unit
    def test_validar_correo_basico_correo_invalido(self):
        """Test validación de correo inválido"""
        emails_invalidos = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user.domain.com",
            "user@domain.",
            "",
            "   ",
            "user@domain..com",
            "user@@domain.com"
        ]
        for email in emails_invalidos:
            assert Empresa.validar_correo_basico(email) is False
    
    @pytest.mark.unit
    def test_validar_correo_basico_con_espacios(self):
        """Test validación de correo con espacios"""
        assert Empresa.validar_correo_basico("  test@example.com  ") is True
    
    @pytest.mark.unit
    def test_tiene_oferta_con_oferta_valida(self):
        """Test tiene_oferta con oferta válida"""
        empresa = Empresa(oferta=1000.0)
        assert empresa.tiene_oferta() is True
        
        empresa = Empresa(oferta=0.01)
        assert empresa.tiene_oferta() is True
    
    @pytest.mark.unit
    def test_tiene_oferta_sin_oferta(self):
        """Test tiene_oferta sin oferta"""
        empresa = Empresa(oferta=None)
        assert empresa.tiene_oferta() is False
        
        empresa = Empresa(oferta=0)
        assert empresa.tiene_oferta() is False
        
        empresa = Empresa(oferta=-100)
        assert empresa.tiene_oferta() is False
    
    @pytest.mark.unit
    def test_es_valida_empresa_valida(self):
        """Test es_valida con empresa válida"""
        empresa = Empresa(nombre="EMPRESA VALIDA")
        assert empresa.es_valida() is True
        
        empresa = Empresa(nombre="   EMPRESA CON ESPACIOS   ")
        assert empresa.es_valida() is True
    
    @pytest.mark.unit
    def test_es_valida_empresa_invalida(self):
        """Test es_valida con empresa inválida"""
        empresa = Empresa(nombre="")
        assert empresa.es_valida() is False
        
        empresa = Empresa(nombre="   ")
        assert empresa.es_valida() is False
        
        empresa = Empresa()
        assert empresa.es_valida() is False


class TestDatosContrato:
    """Tests para la clase DatosContrato"""
    
    @pytest.fixture
    def datos_contrato_completos(self):
        """Fixture con datos de contrato completos"""
        return {
            'tipo': TipoContrato.OBRA,
            'objeto': 'Reparación de edificios',
            'presupuesto_base': Decimal('50000.00'),
            'plazo_ejecucion': 90,
            'fecha_adjudicacion': date(2024, 1, 15),
            'precio_adjudicacion': Decimal('45000.00'),
            'empresa_adjudicataria': 'CONSTRUCTORA TEST S.L.'
        }
    
    @pytest.mark.unit
    def test_datos_contrato_inicializacion(self, datos_contrato_completos):
        """Test inicialización de DatosContrato"""
        contrato = DatosContrato(**datos_contrato_completos)
        assert contrato.tipo == TipoContrato.OBRA
        assert contrato.objeto == 'Reparación de edificios'
        assert contrato.presupuesto_base == Decimal('50000.00')
        assert contrato.plazo_ejecucion == 90
    
    @pytest.mark.unit
    def test_datos_contrato_calculo_iva(self):
        """Test cálculo de IVA en contrato"""
        contrato = DatosContrato(presupuesto_base=Decimal('1000.00'))
        iva_esperado = Decimal('1000.00') * Decimal('0.21')
        assert contrato.calcular_iva_base() == iva_esperado
    
    @pytest.mark.unit
    def test_datos_contrato_validacion_tipo(self):
        """Test validación de tipo de contrato"""
        # Tipo válido
        contrato = DatosContrato(tipo=TipoContrato.SERVICIO)
        assert contrato.validar_tipo() is True
        
        # Tipo inválido
        contrato = DatosContrato(tipo="tipo_invalido")
        assert contrato.validar_tipo() is False
    
    @pytest.mark.unit
    def test_datos_contrato_limites_presupuestarios(self):
        """Test verificación de límites presupuestarios según tipo"""
        # Obra dentro del límite
        contrato = DatosContrato(
            tipo=TipoContrato.OBRA, 
            presupuesto_base=Decimal('10000.00')
        )
        assert contrato.dentro_limite_presupuestario() is True
        
        # Obra fuera del límite
        contrato = DatosContrato(
            tipo=TipoContrato.OBRA,
            presupuesto_base=Decimal('20000.00')
        )
        assert contrato.dentro_limite_presupuestario() is False
        
        # Servicio dentro del límite
        contrato = DatosContrato(
            tipo=TipoContrato.SERVICIO,
            presupuesto_base=Decimal('30000.00')
        )
        assert contrato.dentro_limite_presupuestario() is True
        
        # Servicio fuera del límite
        contrato = DatosContrato(
            tipo=TipoContrato.SERVICIO,
            presupuesto_base=Decimal('50000.00')
        )
        assert contrato.dentro_limite_presupuestario() is False


class TestOferta:
    """Tests para la clase Oferta"""
    
    @pytest.mark.unit
    def test_oferta_inicializacion_basica(self):
        """Test inicialización básica de oferta"""
        oferta = Oferta(
            empresa="CONSTRUCTORA TEST",
            importe=45000.0,
            estado=EstadoOferta.PRESENTADA
        )
        assert oferta.empresa == "CONSTRUCTORA TEST"
        assert oferta.importe == 45000.0
        assert oferta.estado == EstadoOferta.PRESENTADA
    
    @pytest.mark.unit
    def test_oferta_calculo_total_con_iva(self):
        """Test cálculo del total con IVA"""
        oferta = Oferta(importe=1000.0)
        total_esperado = 1000.0 * 1.21
        assert oferta.calcular_total_con_iva() == total_esperado
    
    @pytest.mark.unit
    def test_oferta_es_ganadora(self):
        """Test verificación de oferta ganadora"""
        oferta = Oferta(estado=EstadoOferta.ADJUDICADA)
        assert oferta.es_ganadora() is True
        
        oferta = Oferta(estado=EstadoOferta.PRESENTADA)
        assert oferta.es_ganadora() is False
    
    @pytest.mark.unit
    def test_oferta_validacion(self):
        """Test validación de oferta"""
        # Oferta válida
        oferta = Oferta(
            empresa="EMPRESA VALID A",
            importe=1000.0,
            estado=EstadoOferta.PRESENTADA
        )
        assert oferta.es_valida() is True
        
        # Oferta sin empresa
        oferta = Oferta(empresa="", importe=1000.0)
        assert oferta.es_valida() is False
        
        # Oferta con importe negativo
        oferta = Oferta(empresa="EMPRESA", importe=-100.0)
        assert oferta.es_valida() is False


class TestDatosLiquidacion:
    """Tests para la clase DatosLiquidacion"""
    
    @pytest.fixture
    def datos_liquidacion_base(self):
        """Datos básicos de liquidación"""
        return {
            'importe_adjudicado': Decimal('45000.00'),
            'importe_ejecutado': Decimal('44000.00'),
            'penalizaciones': Decimal('500.00'),
            'adicionales': Decimal('1000.00')
        }
    
    @pytest.mark.unit
    def test_liquidacion_calculo_diferencia(self, datos_liquidacion_base):
        """Test cálculo de diferencia en liquidación"""
        liquidacion = DatosLiquidacion(**datos_liquidacion_base)
        diferencia_esperada = Decimal('44000.00') - Decimal('45000.00')
        assert liquidacion.calcular_diferencia() == diferencia_esperada
    
    @pytest.mark.unit
    def test_liquidacion_calculo_saldo_final(self, datos_liquidacion_base):
        """Test cálculo del saldo final"""
        liquidacion = DatosLiquidacion(**datos_liquidacion_base)
        # importe_ejecutado + adicionales - penalizaciones - importe_adjudicado
        saldo_esperado = Decimal('44000.00') + Decimal('1000.00') - Decimal('500.00') - Decimal('45000.00')
        assert liquidacion.calcular_saldo_final() == saldo_esperado
    
    @pytest.mark.unit
    def test_liquidacion_a_favor_empresa(self):
        """Test liquidación a favor de la empresa"""
        liquidacion = DatosLiquidacion(
            importe_adjudicado=Decimal('40000.00'),
            importe_ejecutado=Decimal('42000.00')
        )
        assert liquidacion.es_a_favor_empresa() is True
        assert liquidacion.es_a_favor_adif() is False
    
    @pytest.mark.unit
    def test_liquidacion_a_favor_adif(self):
        """Test liquidación a favor de ADIF"""
        liquidacion = DatosLiquidacion(
            importe_adjudicado=Decimal('45000.00'),
            importe_ejecutado=Decimal('42000.00')
        )
        assert liquidacion.es_a_favor_adif() is True
        assert liquidacion.es_a_favor_empresa() is False


class TestProyecto:
    """Tests para la clase Proyecto (contenedor principal)"""
    
    @pytest.mark.unit
    def test_proyecto_inicializacion_vacia(self):
        """Test inicialización de proyecto vacío"""
        proyecto = Proyecto()
        assert proyecto.nombre == ""
        assert proyecto.datos_contrato is None
        assert proyecto.empresas == []
        assert proyecto.ofertas == []
    
    @pytest.mark.unit
    def test_proyecto_agregar_empresa(self, sample_empresa_data):
        """Test agregar empresa al proyecto"""
        proyecto = Proyecto()
        empresa = Empresa(**sample_empresa_data)
        
        proyecto.agregar_empresa(empresa)
        assert len(proyecto.empresas) == 1
        assert proyecto.empresas[0] == empresa
    
    @pytest.mark.unit
    def test_proyecto_agregar_empresa_duplicada(self, sample_empresa_data):
        """Test agregar empresa duplicada"""
        proyecto = Proyecto()
        empresa = Empresa(**sample_empresa_data)
        
        proyecto.agregar_empresa(empresa)
        proyecto.agregar_empresa(empresa)  # Duplicada
        
        # Debe seguir habiendo solo una empresa
        assert len(proyecto.empresas) == 1
    
    @pytest.mark.unit
    def test_proyecto_obtener_oferta_ganadora(self):
        """Test obtención de oferta ganadora"""
        proyecto = Proyecto()
        
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000, estado=EstadoOferta.PRESENTADA)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000, estado=EstadoOferta.ADJUDICADA)
        oferta3 = Oferta(empresa="EMPRESA C", importe=48000, estado=EstadoOferta.PRESENTADA)
        
        proyecto.ofertas = [oferta1, oferta2, oferta3]
        
        ganadora = proyecto.obtener_oferta_ganadora()
        assert ganadora == oferta2
        assert ganadora.es_ganadora() is True
    
    @pytest.mark.unit
    def test_proyecto_sin_oferta_ganadora(self):
        """Test proyecto sin oferta ganadora"""
        proyecto = Proyecto()
        
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000, estado=EstadoOferta.PRESENTADA)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000, estado=EstadoOferta.PRESENTADA)
        
        proyecto.ofertas = [oferta1, oferta2]
        
        ganadora = proyecto.obtener_oferta_ganadora()
        assert ganadora is None
    
    @pytest.mark.unit
    def test_proyecto_exportar_json(self, sample_contrato_data):
        """Test exportación a JSON"""
        proyecto = Proyecto(nombre="Proyecto Test")
        proyecto.datos_contrato = DatosContrato(**{
            'tipo': TipoContrato.OBRA,
            'objeto': 'Test objeto',
            'presupuesto_base': Decimal('50000.00')
        })
        
        json_data = proyecto.exportar_json()
        assert json_data['nombre'] == "Proyecto Test"
        assert 'datos_contrato' in json_data
        assert 'empresas' in json_data
        assert 'ofertas' in json_data
    
    @pytest.mark.unit
    def test_proyecto_importar_json(self):
        """Test importación desde JSON"""
        json_data = {
            'nombre': 'Proyecto Importado',
            'datos_contrato': {
                'tipo': 'obra',
                'objeto': 'Objeto importado',
                'presupuesto_base': '30000.00'
            },
            'empresas': [],
            'ofertas': []
        }
        
        proyecto = Proyecto.importar_json(json_data)
        assert proyecto.nombre == 'Proyecto Importado'
        assert proyecto.datos_contrato is not None


class TestConstantes:
    """Tests para la clase Constantes"""
    
    @pytest.mark.unit
    def test_constantes_limites_presupuestarios(self):
        """Test constantes de límites presupuestarios"""
        assert Constantes.LIMITE_OBRA == 15000
        assert Constantes.LIMITE_SERVICIO == 40000
    
    @pytest.mark.unit
    def test_constantes_iva(self):
        """Test constante de IVA"""
        assert Constantes.IVA_GENERAL == 0.21
    
    @pytest.mark.unit 
    def test_constantes_formatos_fecha(self):
        """Test formatos de fecha"""
        assert Constantes.FORMATO_FECHA_CORTA == "%d/%m/%Y"
        assert Constantes.FORMATO_FECHA_LARGA == "%d de %B de %Y"
        assert Constantes.FORMATO_FECHA_ISO == "%Y-%m-%d"


class TestIntegracionModelos:
    """Tests de integración entre modelos"""
    
    @pytest.mark.integration
    def test_flujo_completo_contrato(self, sample_empresa_data, sample_contrato_data):
        """Test del flujo completo de un contrato"""
        # 1. Crear proyecto
        proyecto = Proyecto(nombre="Proyecto Integración")
        
        # 2. Configurar datos del contrato
        proyecto.datos_contrato = DatosContrato(
            tipo=TipoContrato.OBRA,
            objeto="Reparación integral",
            presupuesto_base=Decimal('50000.00'),
            plazo_ejecucion=60
        )
        
        # 3. Agregar empresas
        empresa1 = Empresa(
            nombre="CONSTRUCTORA UNO S.L.",
            nif="B11111111", 
            email="uno@constructora.com",
            oferta=45000.0
        )
        empresa2 = Empresa(
            nombre="CONSTRUCTORA DOS S.A.",
            nif="B22222222",
            email="dos@constructora.com", 
            oferta=47000.0
        )
        
        proyecto.agregar_empresa(empresa1)
        proyecto.agregar_empresa(empresa2)
        
        # 4. Crear ofertas
        oferta1 = Oferta(
            empresa=empresa1.nombre,
            importe=empresa1.oferta,
            estado=EstadoOferta.ADJUDICADA
        )
        oferta2 = Oferta(
            empresa=empresa2.nombre,
            importe=empresa2.oferta,
            estado=EstadoOferta.PRESENTADA
        )
        
        proyecto.ofertas = [oferta1, oferta2]
        
        # 5. Verificar estado final
        assert len(proyecto.empresas) == 2
        assert len(proyecto.ofertas) == 2
        
        ganadora = proyecto.obtener_oferta_ganadora()
        assert ganadora.empresa == empresa1.nombre
        assert ganadora.importe == 45000.0
        
        # 6. Verificar que el contrato está dentro de límites
        assert proyecto.datos_contrato.dentro_limite_presupuestario() is False  # 50000 > 15000
        
        # 7. Exportar e importar JSON
        json_data = proyecto.exportar_json()
        proyecto_importado = Proyecto.importar_json(json_data)
        assert proyecto_importado.nombre == proyecto.nombre


# Marks para diferentes tipos de test
pytestmark = pytest.mark.unit