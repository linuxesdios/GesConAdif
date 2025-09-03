"""
Tests mejorados y ampliados para modelos_py.py
Cobertura objetivo: >95%
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
    Oferta, DatosLiquidacion, Proyecto, Constantes,
    crear_proyecto_vacio
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
            "",
            "   "
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

    @pytest.mark.unit
    def test_limpiar_datos(self):
        """Test limpieza de datos de empresa"""
        empresa = Empresa(
            nombre="  EMPRESA TEST  ",
            nif="  b12345678  ",
            email="  TEST@EXAMPLE.COM  ",
            contacto="  Juan Pérez  "
        )
        empresa.limpiar_datos()
        
        assert empresa.nombre == "EMPRESA TEST"
        assert empresa.nif == "B12345678"
        assert empresa.email == "test@example.com"
        assert empresa.contacto == "Juan Pérez"

    @pytest.mark.unit
    def test_a_diccionario(self):
        """Test conversión a diccionario"""
        empresa = Empresa(
            nombre="TEST",
            nif="B12345678",
            email="test@test.com",
            contacto="Juan",
            oferta=1000.0
        )
        
        dict_empresa = empresa.a_diccionario()
        assert dict_empresa['nombre'] == "TEST"
        assert dict_empresa['nif'] == "B12345678"
        assert dict_empresa['email'] == "test@test.com"
        assert dict_empresa['contacto'] == "Juan"
        assert dict_empresa['oferta'] == 1000.0

    @pytest.mark.unit
    def test_desde_diccionario(self):
        """Test creación desde diccionario"""
        datos = {
            'nombre': 'EMPRESA DICT',
            'nif': 'B87654321',
            'email': 'dict@test.com',
            'contacto': 'María',
            'oferta': 2000.0
        }
        
        empresa = Empresa.desde_diccionario(datos)
        assert empresa.nombre == 'EMPRESA DICT'
        assert empresa.nif == 'B87654321'
        assert empresa.email == 'dict@test.com'
        assert empresa.contacto == 'María'
        assert empresa.oferta == 2000.0


class TestOferta:
    """Tests ampliados para la clase Oferta"""
    
    @pytest.mark.unit
    def test_oferta_inicializacion_basica(self):
        """Test inicialización básica de oferta"""
        oferta = Oferta(
            empresa="CONSTRUCTORA TEST",
            importe=45000.0
        )
        assert oferta.empresa == "CONSTRUCTORA TEST"
        assert oferta.importe == 45000.0
        assert oferta.orden_clasificatorio == 0
        assert oferta.presenta_oferta is True
        assert oferta.estado == EstadoOferta.PRESENTADA
    
    @pytest.mark.unit
    def test_oferta_post_init_validaciones(self):
        """Test validaciones en __post_init__"""
        # Importe negativo debe fallar
        with pytest.raises(ValueError, match="El importe no puede ser negativo"):
            Oferta(empresa="TEST", importe=-100.0)
        
        # Empresa vacía debe fallar
        with pytest.raises(ValueError, match="El nombre de la empresa es obligatorio"):
            Oferta(empresa="", importe=1000.0)
        
        with pytest.raises(ValueError, match="El nombre de la empresa es obligatorio"):
            Oferta(empresa="   ", importe=1000.0)
    
    @pytest.mark.unit
    def test_oferta_es_valida(self):
        """Test validación de oferta"""
        # Oferta válida
        oferta = Oferta(empresa="EMPRESA VALIDA", importe=1000.0)
        assert oferta.es_valida() is True
        
        # Oferta no presentada
        oferta = Oferta(empresa="EMPRESA", importe=1000.0, presenta_oferta=False)
        assert oferta.es_valida() is False
        
        # Importe cero
        oferta = Oferta(empresa="EMPRESA", importe=0.0)
        assert oferta.es_valida() is False
    
    @pytest.mark.unit
    def test_oferta_calcular_iva(self):
        """Test cálculo de IVA"""
        oferta = Oferta(empresa="TEST", importe=1000.0)
        
        # IVA por defecto (21%)
        assert oferta.calcular_iva() == 210.0
        
        # IVA personalizado
        assert oferta.calcular_iva(0.10) == 100.0
    
    @pytest.mark.unit
    def test_oferta_calcular_total_con_iva(self):
        """Test cálculo del total con IVA"""
        oferta = Oferta(empresa="TEST", importe=1000.0)
        
        # Total con IVA por defecto
        assert oferta.calcular_total_con_iva() == 1210.0
        
        # Total con IVA personalizado
        assert oferta.calcular_total_con_iva(0.10) == 1100.0
    
    @pytest.mark.unit
    def test_oferta_a_diccionario(self):
        """Test conversión a diccionario"""
        fecha_test = date(2024, 1, 15)
        oferta = Oferta(
            empresa="TEST",
            importe=1000.0,
            orden_clasificatorio=1,
            presenta_oferta=True,
            estado=EstadoOferta.ADJUDICADA,
            fecha_presentacion=fecha_test,
            observaciones="Test observación"
        )
        
        dict_oferta = oferta.a_diccionario()
        assert dict_oferta['empresa'] == "TEST"
        assert dict_oferta['importe'] == 1000.0
        assert dict_oferta['orden_clasificatorio'] == 1
        assert dict_oferta['presenta_oferta'] is True
        assert dict_oferta['estado'] == "adjudicada"
        assert dict_oferta['fecha_presentacion'] == "2024-01-15"
        assert dict_oferta['observaciones'] == "Test observación"
    
    @pytest.mark.unit
    def test_oferta_desde_diccionario(self):
        """Test creación desde diccionario"""
        datos = {
            'empresa': 'EMPRESA DICT',
            'importe': 2000.0,
            'orden_clasificatorio': 2,
            'presenta_oferta': False,
            'estado': 'rechazada',
            'fecha_presentacion': '2024-02-01',
            'observaciones': 'Rechazada por precio'
        }
        
        oferta = Oferta.desde_diccionario(datos)
        assert oferta.empresa == 'EMPRESA DICT'
        assert oferta.importe == 2000.0
        assert oferta.orden_clasificatorio == 2
        assert oferta.presenta_oferta is False
        assert oferta.estado == EstadoOferta.RECHAZADA
        assert oferta.fecha_presentacion == date(2024, 2, 1)
        assert oferta.observaciones == 'Rechazada por precio'


class TestDatosContrato:
    """Tests ampliados para la clase DatosContrato"""
    
    @pytest.mark.unit
    def test_datos_contrato_inicializacion_defecto(self):
        """Test inicialización con valores por defecto"""
        contrato = DatosContrato()
        assert contrato.numero_expediente == ""
        assert contrato.objeto_contrato == ""
        assert contrato.tipo_contrato == TipoContrato.SERVICIO
        assert contrato.importe_licitacion == 0.0
        assert contrato.importe_iva == 0.0
        assert contrato.importe_total == 0.0
        assert contrato.duracion == ""
        assert contrato.plazo_ejecucion == ""
    
    @pytest.mark.unit
    def test_datos_contrato_calcular_iva(self):
        """Test cálculo de IVA"""
        contrato = DatosContrato(importe_licitacion=1000.0)
        
        # IVA por defecto (21%)
        iva = contrato.calcular_iva()
        assert iva == 210.0
        assert contrato.importe_iva == 210.0
        
        # IVA personalizado
        iva_custom = contrato.calcular_iva(0.10)
        assert iva_custom == 100.0
        assert contrato.importe_iva == 100.0
    
    @pytest.mark.unit
    def test_datos_contrato_calcular_total(self):
        """Test cálculo del total con IVA"""
        contrato = DatosContrato(importe_licitacion=1000.0)
        
        # Total por defecto
        total = contrato.calcular_total()
        assert total == 1210.0
        assert contrato.importe_total == 1210.0
        
        # Total personalizado
        total_custom = contrato.calcular_total(0.10)
        assert total_custom == 1100.0
        assert contrato.importe_total == 1100.0
    
    @pytest.mark.unit
    def test_datos_contrato_es_obra(self):
        """Test verificación de tipo obra"""
        contrato = DatosContrato(tipo_contrato=TipoContrato.OBRA)
        assert contrato.es_obra() is True
        assert contrato.es_servicio() is False
    
    @pytest.mark.unit
    def test_datos_contrato_es_servicio(self):
        """Test verificación de tipo servicio"""
        contrato = DatosContrato(tipo_contrato=TipoContrato.SERVICIO)
        assert contrato.es_servicio() is True
        assert contrato.es_obra() is False
    
    @pytest.mark.unit
    def test_datos_contrato_obtener_limite_contratacion(self):
        """Test obtención de límites de contratación"""
        # Obra
        contrato_obra = DatosContrato(tipo_contrato=TipoContrato.OBRA)
        assert contrato_obra.obtener_limite_contratacion() == 15000.0
        
        # Servicio
        contrato_servicio = DatosContrato(tipo_contrato=TipoContrato.SERVICIO)
        assert contrato_servicio.obtener_limite_contratacion() == 40000.0
    
    @pytest.mark.unit
    def test_datos_contrato_cumple_limite_contratacion(self):
        """Test verificación de cumplimiento de límites"""
        # Obra dentro del límite
        contrato = DatosContrato(
            tipo_contrato=TipoContrato.OBRA,
            importe_licitacion=10000.0
        )
        assert contrato.cumple_limite_contratacion() is True
        
        # Obra fuera del límite
        contrato = DatosContrato(
            tipo_contrato=TipoContrato.OBRA,
            importe_licitacion=20000.0
        )
        assert contrato.cumple_limite_contratacion() is False
        
        # Servicio dentro del límite
        contrato = DatosContrato(
            tipo_contrato=TipoContrato.SERVICIO,
            importe_licitacion=30000.0
        )
        assert contrato.cumple_limite_contratacion() is True
        
        # Servicio fuera del límite
        contrato = DatosContrato(
            tipo_contrato=TipoContrato.SERVICIO,
            importe_licitacion=50000.0
        )
        assert contrato.cumple_limite_contratacion() is False
    
    @pytest.mark.unit
    def test_datos_contrato_to_dict(self):
        """Test conversión a diccionario"""
        fecha_test = date(2024, 1, 15)
        contrato = DatosContrato(
            numero_expediente="EXP-2024-001",
            objeto_contrato="Reparación edificio",
            tipo_contrato=TipoContrato.OBRA,
            importe_licitacion=25000.0,
            fecha_adjudicacion=fecha_test
        )
        
        dict_contrato = contrato.to_dict()
        assert dict_contrato['numero_expediente'] == "EXP-2024-001"
        assert dict_contrato['objeto_contrato'] == "Reparación edificio"
        assert dict_contrato['tipo_contrato'] == "obra"
        assert dict_contrato['importe_licitacion'] == 25000.0
        assert dict_contrato['fecha_adjudicacion'] == "2024-01-15"
    
    @pytest.mark.unit
    def test_datos_contrato_from_dict(self):
        """Test creación desde diccionario"""
        datos = {
            'numero_expediente': 'EXP-2024-002',
            'objeto_contrato': 'Mantenimiento sistemas',
            'tipo_contrato': 'servicio',
            'importe_licitacion': 35000.0,
            'fecha_inicio': '2024-03-01'
        }
        
        contrato = DatosContrato.from_dict(datos)
        assert contrato.numero_expediente == 'EXP-2024-002'
        assert contrato.objeto_contrato == 'Mantenimiento sistemas'
        assert contrato.tipo_contrato == TipoContrato.SERVICIO
        assert contrato.importe_licitacion == 35000.0
        assert contrato.fecha_inicio == date(2024, 3, 1)


class TestDatosLiquidacion:
    """Tests ampliados para la clase DatosLiquidacion"""
    
    @pytest.mark.unit
    def test_liquidacion_inicializacion_defecto(self):
        """Test inicialización con valores por defecto"""
        liquidacion = DatosLiquidacion()
        assert liquidacion.importe_licitado == 0.0
        assert liquidacion.importe_facturado == 0.0
        assert liquidacion.importe_penalizaciones == 0.0
        assert liquidacion.diferencia == 0.0
        assert liquidacion.porcentaje_ejecutado == 0.0
        assert liquidacion.empresa_ejecutora == ""
        assert liquidacion.saldo_favor_adif == 0.0
        assert liquidacion.saldo_favor_empresa == 0.0
    
    @pytest.mark.unit
    def test_liquidacion_calcular_diferencia(self):
        """Test cálculo de diferencia"""
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=48000.0,
            importe_penalizaciones=500.0
        )
        
        diferencia = liquidacion.calcular_diferencia()
        # |50000 - 48000 - 500| = 1500
        assert diferencia == 1500.0
        assert liquidacion.diferencia == 1500.0
    
    @pytest.mark.unit
    def test_liquidacion_calcular_porcentaje_ejecutado(self):
        """Test cálculo de porcentaje ejecutado"""
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=45000.0
        )
        
        porcentaje = liquidacion.calcular_porcentaje_ejecutado()
        assert porcentaje == 90.0  # 45000/50000 * 100
        assert liquidacion.porcentaje_ejecutado == 90.0
        
        # Caso con importe licitado cero
        liquidacion_cero = DatosLiquidacion(importe_licitado=0.0, importe_facturado=1000.0)
        porcentaje_cero = liquidacion_cero.calcular_porcentaje_ejecutado()
        assert porcentaje_cero == 0.0
    
    @pytest.mark.unit
    def test_liquidacion_calcular_saldos_favor_adif(self):
        """Test cálculo de saldos a favor de ADIF"""
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=45000.0,
            importe_penalizaciones=1000.0
        )
        
        saldo_adif, saldo_empresa = liquidacion.calcular_saldos()
        # 50000 - 45000 + 1000 = 6000 (favor ADIF)
        assert saldo_adif == 6000.0
        assert saldo_empresa == 0.0
        assert liquidacion.saldo_favor_adif == 6000.0
        assert liquidacion.saldo_favor_empresa == 0.0
    
    @pytest.mark.unit
    def test_liquidacion_calcular_saldos_favor_empresa(self):
        """Test cálculo de saldos a favor de empresa"""
        liquidacion = DatosLiquidacion(
            importe_licitado=45000.0,
            importe_facturado=50000.0,
            importe_penalizaciones=0.0
        )
        
        saldo_adif, saldo_empresa = liquidacion.calcular_saldos()
        # 45000 - 50000 + 0 = -5000 (favor empresa)
        assert saldo_adif == 0.0
        assert saldo_empresa == 5000.0
        assert liquidacion.saldo_favor_adif == 0.0
        assert liquidacion.saldo_favor_empresa == 5000.0
    
    @pytest.mark.unit
    def test_liquidacion_calcular_saldos_equilibrado(self):
        """Test cálculo de saldos equilibrados"""
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=50000.0,
            importe_penalizaciones=0.0
        )
        
        saldo_adif, saldo_empresa = liquidacion.calcular_saldos()
        assert saldo_adif == 0.0
        assert saldo_empresa == 0.0
    
    @pytest.mark.unit
    def test_liquidacion_actualizar_calculos(self):
        """Test actualización de todos los cálculos"""
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=48000.0,
            importe_penalizaciones=500.0
        )
        
        liquidacion.actualizar_calculos()
        
        assert liquidacion.diferencia == 1500.0
        assert liquidacion.porcentaje_ejecutado == 96.0  # 48000/50000 * 100
        assert liquidacion.saldo_favor_adif == 1500.0
        assert liquidacion.saldo_favor_empresa == 0.0
    
    @pytest.mark.unit
    def test_liquidacion_to_dict(self):
        """Test conversión a diccionario"""
        fecha_test = date(2024, 1, 15)
        liquidacion = DatosLiquidacion(
            importe_licitado=50000.0,
            importe_facturado=48000.0,
            empresa_ejecutora="CONSTRUCTORA TEST",
            fecha_liquidacion=fecha_test,
            observaciones_liquidacion="Liquidación completa"
        )
        
        dict_liquidacion = liquidacion.to_dict()
        assert dict_liquidacion['importe_licitado'] == 50000.0
        assert dict_liquidacion['importe_facturado'] == 48000.0
        assert dict_liquidacion['empresa_ejecutora'] == "CONSTRUCTORA TEST"
        assert dict_liquidacion['fecha_liquidacion'] == "2024-01-15"
        assert dict_liquidacion['observaciones_liquidacion'] == "Liquidación completa"
    
    @pytest.mark.unit
    def test_liquidacion_from_dict(self):
        """Test creación desde diccionario"""
        datos = {
            'importe_licitado': 60000.0,
            'importe_facturado': 58000.0,
            'importe_penalizaciones': 1000.0,
            'empresa_ejecutora': 'EMPRESA DICT',
            'fecha_liquidacion': '2024-02-15',
            'observaciones_liquidacion': 'Liquidación desde dict'
        }
        
        liquidacion = DatosLiquidacion.from_dict(datos)
        assert liquidacion.importe_licitado == 60000.0
        assert liquidacion.importe_facturado == 58000.0
        assert liquidacion.importe_penalizaciones == 1000.0
        assert liquidacion.empresa_ejecutora == 'EMPRESA DICT'
        assert liquidacion.fecha_liquidacion == date(2024, 2, 15)
        assert liquidacion.observaciones_liquidacion == 'Liquidación desde dict'


class TestProyecto:
    """Tests ampliados para la clase Proyecto"""
    
    @pytest.mark.unit
    def test_proyecto_inicializacion_defecto(self):
        """Test inicialización con valores por defecto"""
        proyecto = Proyecto()
        assert proyecto.nombre == ""
        assert proyecto.ruta == ""
        assert proyecto.archivo_json == ""
        assert isinstance(proyecto.contrato, DatosContrato)
        assert proyecto.empresas == []
        assert proyecto.ofertas == []
        assert isinstance(proyecto.liquidacion, DatosLiquidacion)
        assert isinstance(proyecto.fecha_creacion, datetime)
        assert isinstance(proyecto.ultima_modificacion, datetime)
        assert proyecto.version == "3.0"
    
    @pytest.mark.unit
    def test_proyecto_obtener_empresa_adjudicataria(self):
        """Test obtención de empresa adjudicataria"""
        proyecto = Proyecto()
        
        # Agregar empresas
        empresa1 = Empresa(nombre="EMPRESA A", oferta=50000.0)
        empresa2 = Empresa(nombre="EMPRESA B", oferta=45000.0)
        proyecto.empresas = [empresa1, empresa2]
        
        # Agregar ofertas
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000.0, presenta_oferta=True)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000.0, presenta_oferta=True)
        proyecto.ofertas = [oferta1, oferta2]
        
        adjudicataria = proyecto.obtener_empresa_adjudicataria()
        assert adjudicataria.nombre == "EMPRESA B"  # Menor oferta
    
    @pytest.mark.unit
    def test_proyecto_obtener_empresa_adjudicataria_sin_ofertas(self):
        """Test obtención de adjudicataria sin ofertas"""
        proyecto = Proyecto()
        adjudicataria = proyecto.obtener_empresa_adjudicataria()
        assert adjudicataria is None
    
    @pytest.mark.unit
    def test_proyecto_obtener_oferta_minima(self):
        """Test obtención de oferta mínima"""
        proyecto = Proyecto()
        
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000.0, presenta_oferta=True)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000.0, presenta_oferta=True)
        oferta3 = Oferta(empresa="EMPRESA C", importe=48000.0, presenta_oferta=False)
        proyecto.ofertas = [oferta1, oferta2, oferta3]
        
        minima = proyecto.obtener_oferta_minima()
        assert minima.empresa == "EMPRESA B"
        assert minima.importe == 45000.0
    
    @pytest.mark.unit
    def test_proyecto_contar_ofertas_validas(self):
        """Test conteo de ofertas válidas"""
        proyecto = Proyecto()
        
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000.0, presenta_oferta=True)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000.0, presenta_oferta=True)
        oferta3 = Oferta(empresa="EMPRESA C", importe=0.0, presenta_oferta=True)  # Inválida
        oferta4 = Oferta(empresa="EMPRESA D", importe=48000.0, presenta_oferta=False)  # Inválida
        proyecto.ofertas = [oferta1, oferta2, oferta3, oferta4]
        
        count = proyecto.contar_ofertas_validas()
        assert count == 2
    
    @pytest.mark.unit
    def test_proyecto_hay_ofertas_duplicadas(self):
        """Test detección de ofertas duplicadas"""
        proyecto = Proyecto()
        
        # Ofertas con mismo importe mínimo
        oferta1 = Oferta(empresa="EMPRESA A", importe=45000.0, presenta_oferta=True)
        oferta2 = Oferta(empresa="EMPRESA B", importe=45000.0, presenta_oferta=True)
        oferta3 = Oferta(empresa="EMPRESA C", importe=50000.0, presenta_oferta=True)
        proyecto.ofertas = [oferta1, oferta2, oferta3]
        
        assert proyecto.hay_ofertas_duplicadas() is True
        
        # Sin duplicadas
        oferta2.importe = 46000.0
        assert proyecto.hay_ofertas_duplicadas() is False
    
    @pytest.mark.unit
    def test_proyecto_sincronizar_ofertas_con_empresas(self):
        """Test sincronización de ofertas con empresas"""
        proyecto = Proyecto()
        
        # Agregar empresas
        empresa1 = Empresa(nombre="EMPRESA A", oferta=50000.0)
        empresa2 = Empresa(nombre="EMPRESA B", oferta=45000.0)
        proyecto.empresas = [empresa1, empresa2]
        
        # Solo una oferta inicial
        oferta1 = Oferta(empresa="EMPRESA A", importe=50000.0)
        proyecto.ofertas = [oferta1]
        
        proyecto.sincronizar_ofertas_con_empresas()
        
        # Debe haber creado oferta para EMPRESA B
        assert len(proyecto.ofertas) == 2
        ofertas_empresas = [o.empresa for o in proyecto.ofertas]
        assert "EMPRESA A" in ofertas_empresas
        assert "EMPRESA B" in ofertas_empresas
    
    @pytest.mark.unit
    def test_proyecto_actualizar_metadatos(self):
        """Test actualización de metadatos"""
        proyecto = Proyecto()
        fecha_inicial = proyecto.ultima_modificacion
        
        # Esperar un poco para que cambie la fecha
        import time
        time.sleep(0.01)
        
        proyecto.actualizar_metadatos()
        assert proyecto.ultima_modificacion > fecha_inicial
    
    @pytest.mark.unit
    def test_proyecto_es_valido(self):
        """Test validación de proyecto"""
        proyecto = Proyecto()
        
        # Proyecto inválido inicialmente
        assert proyecto.es_valido() is False
        
        # Completar datos mínimos
        proyecto.nombre = "Proyecto Test"
        proyecto.contrato.numero_expediente = "EXP-2024-001"
        proyecto.contrato.objeto_contrato = "Objeto test"
        proyecto.empresas = [Empresa(nombre="EMPRESA TEST")]
        
        assert proyecto.es_valido() is True
    
    @pytest.mark.unit
    def test_proyecto_to_dict(self):
        """Test conversión completa a diccionario"""
        proyecto = Proyecto(
            nombre="Proyecto Dict",
            ruta="/test/path",
            archivo_json="/test/path/proyecto.json"
        )
        
        dict_proyecto = proyecto.to_dict()
        assert dict_proyecto['nombre'] == "Proyecto Dict"
        assert dict_proyecto['ruta'] == "/test/path"
        assert dict_proyecto['archivo_json'] == "/test/path/proyecto.json"
        assert 'contrato' in dict_proyecto
        assert 'empresas' in dict_proyecto
        assert 'ofertas' in dict_proyecto
        assert 'liquidacion' in dict_proyecto
        assert 'fecha_creacion' in dict_proyecto
        assert 'ultima_modificacion' in dict_proyecto
        assert dict_proyecto['version'] == "3.0"
    
    @pytest.mark.unit
    def test_proyecto_from_dict(self):
        """Test creación desde diccionario completo"""
        datos = {
            'nombre': 'Proyecto From Dict',
            'ruta': '/dict/path',
            'archivo_json': '/dict/path/proyecto.json',
            'version': '3.1',
            'fecha_creacion': '2024-01-01T10:00:00',
            'ultima_modificacion': '2024-01-15T15:30:00',
            'contrato': {
                'numero_expediente': 'EXP-DICT-001',
                'objeto_contrato': 'Objeto desde dict',
                'tipo_contrato': 'obra'
            },
            'empresas': [
                {
                    'nombre': 'EMPRESA DICT',
                    'nif': 'B12345678',
                    'email': 'dict@test.com',
                    'oferta': 30000.0
                }
            ],
            'ofertas': [
                {
                    'empresa': 'EMPRESA DICT',
                    'importe': 30000.0,
                    'estado': 'presentada'
                }
            ],
            'liquidacion': {
                'importe_licitado': 30000.0,
                'importe_facturado': 29000.0
            }
        }
        
        proyecto = Proyecto.from_dict(datos)
        assert proyecto.nombre == 'Proyecto From Dict'
        assert proyecto.ruta == '/dict/path'
        assert proyecto.version == '3.1'
        assert proyecto.fecha_creacion == datetime.fromisoformat('2024-01-01T10:00:00')
        assert proyecto.ultima_modificacion == datetime.fromisoformat('2024-01-15T15:30:00')
        assert proyecto.contrato.numero_expediente == 'EXP-DICT-001'
        assert len(proyecto.empresas) == 1
        assert len(proyecto.ofertas) == 1
        assert proyecto.liquidacion.importe_licitado == 30000.0


class TestConstantes:
    """Tests ampliados para la clase Constantes"""
    
    @pytest.mark.unit
    def test_constantes_limites_presupuestarios(self):
        """Test constantes de límites presupuestarios"""
        assert Constantes.LIMITE_OBRA == 15000.0
        assert Constantes.LIMITE_SERVICIO == 40000.0
    
    @pytest.mark.unit
    def test_constantes_porcentajes(self):
        """Test constantes de porcentajes"""
        assert Constantes.IVA_GENERAL == 0.21
        assert Constantes.PORCENTAJE_VEZ_Y_MEDIA == 1.5
        assert Constantes.PORCENTAJE_SETENTA == 0.7
    
    @pytest.mark.unit 
    def test_constantes_formatos_fecha(self):
        """Test formatos de fecha"""
        assert Constantes.FORMATO_FECHA_CORTA == "%d/%m/%Y"
        assert Constantes.FORMATO_FECHA_LARGA == "%d de %B de %Y"
        assert Constantes.FORMATO_FECHA_ISO == "%Y-%m-%d"
    
    @pytest.mark.unit
    def test_constantes_extensiones(self):
        """Test constantes de extensiones de archivo"""
        assert Constantes.EXTENSION_PROYECTO == ".PROJPMF"
        assert Constantes.EXTENSION_WORD == ".docx"
        assert Constantes.EXTENSION_PDF == ".pdf"
        assert ".xlsx" in Constantes.EXTENSION_EXCEL
        assert ".xls" in Constantes.EXTENSION_EXCEL
    
    @pytest.mark.unit
    def test_constantes_carpetas_proyecto(self):
        """Test constantes de carpetas del proyecto"""
        carpetas_esperadas = [
            "0_Modelos",
            "1_Actas_generadas", 
            "2_proyecto",
            "3_cartas_invitaciones",
            "4_ofertas",
            "5_cartas_adjudicacion",
            "7_seguridad_y_salud",
            "8_otros",
            "9_Guardado_seguridad"
        ]
        
        for carpeta in carpetas_esperadas:
            assert carpeta in Constantes.CARPETAS_PROYECTO
    
    @pytest.mark.unit
    def test_constantes_plantillas(self):
        """Test constantes de plantillas"""
        assert 'acta_inicio_obra' in Constantes.PLANTILLAS
        assert 'acta_inicio_servicio' in Constantes.PLANTILLAS
        assert 'carta_invitacion' in Constantes.PLANTILLAS
        assert 'acta_adjudicacion' in Constantes.PLANTILLAS
        
        # Verificar que las plantillas tienen extensión .docx
        for plantilla in Constantes.PLANTILLAS.values():
            assert plantilla.endswith('.docx')
    
    @pytest.mark.unit
    def test_constantes_mensajes_error(self):
        """Test constantes de mensajes de error"""
        mensajes_esperados = [
            'proyecto_no_encontrado',
            'datos_invalidos',
            'campos_vacios',
            'ofertas_duplicadas',
            'sin_ofertas',
            'error_guardado',
            'error_generacion'
        ]
        
        for mensaje in mensajes_esperados:
            assert mensaje in Constantes.MENSAJES_ERROR
            assert isinstance(Constantes.MENSAJES_ERROR[mensaje], str)
    
    @pytest.mark.unit
    def test_constantes_urls(self):
        """Test constantes de URLs"""
        assert 'portafirmas' in Constantes.URLS
        assert 'boe_contratos' in Constantes.URLS
        
        # Verificar que son URLs válidas
        assert Constantes.URLS['portafirmas'].startswith('https://')
        assert Constantes.URLS['boe_contratos'].startswith('https://')


class TestFuncionesAuxiliares:
    """Tests para funciones auxiliares"""
    
    @pytest.mark.unit
    def test_crear_proyecto_vacio(self):
        """Test creación de proyecto vacío"""
        nombre = "Proyecto Test"
        ruta = "/test/path"
        
        proyecto = crear_proyecto_vacio(nombre, ruta)
        
        assert proyecto.nombre == nombre
        assert proyecto.ruta == ruta
        assert proyecto.archivo_json == f"{ruta}/{nombre}{Constantes.EXTENSION_PROYECTO}"
        assert len(proyecto.empresas) == 1  # Empresa vacía por defecto
        assert proyecto.empresas[0].nombre == ""


class TestIntegracionModelos:
    """Tests de integración entre modelos"""
    
    @pytest.mark.integration
    def test_flujo_completo_contrato(self):
        """Test del flujo completo de un contrato"""
        # 1. Crear proyecto
        proyecto = Proyecto(nombre="Proyecto Integración Completo")
        
        # 2. Configurar datos del contrato
        proyecto.contrato = DatosContrato(
            numero_expediente="EXP-INT-2024-001",
            objeto_contrato="Reparación integral de edificio",
            tipo_contrato=TipoContrato.OBRA,
            importe_licitacion=45000.0,
            duracion="6 meses",
            plazo_ejecucion="180 días"
        )
        
        # 3. Calcular IVA y total
        proyecto.contrato.calcular_iva()
        proyecto.contrato.calcular_total()
        
        # 4. Agregar empresas
        empresa1 = Empresa(
            nombre="CONSTRUCTORA ALPHA S.L.",
            nif="B11111111", 
            email="alpha@constructora.com",
            contacto="Juan Pérez",
            oferta=42000.0
        )
        empresa2 = Empresa(
            nombre="CONSTRUCTORA BETA S.A.",
            nif="B22222222",
            email="beta@constructora.com",
            contacto="María García",
            oferta=44000.0
        )
        empresa3 = Empresa(
            nombre="CONSTRUCTORA GAMMA S.L.",
            nif="B33333333",
            email="gamma@constructora.com",
            contacto="Carlos López",
            oferta=43500.0
        )
        
        proyecto.empresas = [empresa1, empresa2, empresa3]
        
        # 5. Crear ofertas
        oferta1 = Oferta(
            empresa=empresa1.nombre,
            importe=empresa1.oferta,
            orden_clasificatorio=1,
            estado=EstadoOferta.ADJUDICADA,
            fecha_presentacion=date(2024, 1, 15),
            observaciones="Oferta más económica"
        )
        oferta2 = Oferta(
            empresa=empresa2.nombre,
            importe=empresa2.oferta,
            orden_clasificatorio=3,
            estado=EstadoOferta.PRESENTADA,
            fecha_presentacion=date(2024, 1, 15)
        )
        oferta3 = Oferta(
            empresa=empresa3.nombre,
            importe=empresa3.oferta,
            orden_clasificatorio=2,
            estado=EstadoOferta.PRESENTADA,
            fecha_presentacion=date(2024, 1, 15)
        )
        
        proyecto.ofertas = [oferta1, oferta2, oferta3]
        
        # 6. Configurar liquidación
        proyecto.liquidacion = DatosLiquidacion(
            importe_licitado=42000.0,
            importe_facturado=41500.0,
            importe_penalizaciones=200.0,
            empresa_ejecutora=empresa1.nombre,
            fecha_liquidacion=date(2024, 7, 15),
            observaciones_liquidacion="Liquidación con penalización menor"
        )
        
        # Calcular todos los valores de liquidación
        proyecto.liquidacion.actualizar_calculos()
        
        # 7. Verificaciones del estado final
        assert len(proyecto.empresas) == 3
        assert len(proyecto.ofertas) == 3
        assert proyecto.contar_ofertas_validas() == 3
        
        # Verificar empresa adjudicataria
        adjudicataria = proyecto.obtener_empresa_adjudicataria()
        assert adjudicataria.nombre == empresa1.nombre
        
        # Verificar oferta mínima
        oferta_minima = proyecto.obtener_oferta_minima()
        assert oferta_minima.empresa == empresa1.nombre
        assert oferta_minima.importe == 42000.0
        
        # Verificar que no hay ofertas duplicadas
        assert proyecto.hay_ofertas_duplicadas() is False
        
        # Verificar límites de contratación
        assert proyecto.contrato.cumple_limite_contratacion() is False  # 45000 > 15000
        
        # Verificar cálculos de liquidación
        assert proyecto.liquidacion.porcentaje_ejecutado > 98.0  # ~98.8%
        assert proyecto.liquidacion.saldo_favor_adif > 0  # Hay saldo a favor de ADIF
        
        # 8. Verificar validez del proyecto
        assert proyecto.es_valido() is True
        
        # 9. Test de serialización completa
        dict_proyecto = proyecto.to_dict()
        proyecto_restaurado = Proyecto.from_dict(dict_proyecto)
        
        # Verificar que la restauración es correcta
        assert proyecto_restaurado.nombre == proyecto.nombre
        assert proyecto_restaurado.contrato.numero_expediente == proyecto.contrato.numero_expediente
        assert len(proyecto_restaurado.empresas) == len(proyecto.empresas)
        assert len(proyecto_restaurado.ofertas) == len(proyecto.ofertas)
        assert proyecto_restaurado.liquidacion.importe_licitado == proyecto.liquidacion.importe_licitado
        
        # 10. Verificar sincronización
        proyecto_restaurado.sincronizar_ofertas_con_empresas()
        assert len(proyecto_restaurado.ofertas) == 3  # No debe cambiar
        
        # 11. Actualizar metadatos
        fecha_anterior = proyecto_restaurado.ultima_modificacion
        proyecto_restaurado.actualizar_metadatos()
        assert proyecto_restaurado.ultima_modificacion >= fecha_anterior


# Marks para diferentes tipos de test
pytestmark = pytest.mark.unit