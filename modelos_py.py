"""
Modelos de datos para la aplicación Generador de Actas ADIF
Contiene todas las clases de datos del dominio empresarial
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from enum import Enum


class TipoContrato(Enum):
    """Tipos de contrato disponibles"""
    SERVICIO = "servicio"
    OBRA = "obra"


class EstadoOferta(Enum):
    """Estados posibles de una oferta"""
    NO_PRESENTADA = "no_presentada"
    PRESENTADA = "presentada"
    ADJUDICADA = "adjudicada"
    RECHAZADA = "rechazada"


@dataclass
class Empresa:
    """Modelo para representar una empresa licitadora"""
    nombre: str = ""
    nif: str = ""
    email: str = ""
    contacto: str = ""
    oferta: Optional[float] = None
    
    def __init__(self, nombre="", nif="", email="", contacto="", oferta=None, ofertas=None, **kwargs):
        """Constructor con compatibilidad para parámetros legacy"""
        self.nombre = nombre
        self.nif = nif
        self.email = email
        self.contacto = contacto
        
        # Compatibilidad con 'ofertas' parameter
        if ofertas is not None:
            try:
                self.oferta = float(ofertas)
            except (ValueError, TypeError):
                self.oferta = None
        elif oferta is not None:
            self.oferta = float(oferta)
        else:
            self.oferta = None
    
    @staticmethod
    def validar_correo_basico(correo: str) -> bool:
        """Validación básica de formato email"""
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, correo.strip()))


    def tiene_oferta(self) -> bool:
        """Verifica si la empresa tiene una oferta válida"""
        return self.oferta is not None and self.oferta > 0
        
    def es_valida(self) -> bool:
        """Verifica si los datos de la empresa son válidos"""
        return bool(self.nombre.strip())
    
    def limpiar_datos(self):
        """Limpia y normaliza los datos de la empresa"""
        self.nombre = self.nombre.strip()
        self.nif = self.nif.strip().upper()
        self.email = self.email.strip().lower()
        self.contacto = self.contacto.strip()
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la empresa a diccionario"""
        return {
            'nombre': self.nombre,
            'nif': self.nif,
            'email': self.email,
            'contacto': self.contacto,
            'oferta': self.oferta
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Alias para a_diccionario para compatibilidad"""
        return self.a_diccionario()
    
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> 'Empresa':
        """Crea una empresa desde diccionario"""
        return cls(
            nombre=datos.get('nombre', ''),
            nif=datos.get('nif', ''),
            email=datos.get('email', ''),
            contacto=datos.get('contacto', ''),
            oferta=datos.get('oferta')
        )
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'Empresa':
        """Alias para desde_diccionario para compatibilidad"""
        return cls.desde_diccionario(datos)



@dataclass
class Oferta:
    """Modelo para representar una oferta económica"""
    empresa: str
    importe: float
    orden_clasificatorio: int = 0
    presenta_oferta: bool = True
    estado: EstadoOferta = EstadoOferta.PRESENTADA
    fecha_presentacion: Optional[date] = None
    observaciones: str = ""
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.importe < 0:
            raise ValueError("El importe no puede ser negativo")
        
        if not self.empresa.strip():
            raise ValueError("El nombre de la empresa es obligatorio")
    
    def es_valida(self) -> bool:
        """Verifica si la oferta es válida"""
        return (
            self.presenta_oferta and 
            self.importe > 0 and 
            bool(self.empresa.strip())
        )
    
    def calcular_iva(self, porcentaje: float = 0.21) -> float:
        """Calcula el IVA de la oferta"""
        return self.importe * porcentaje
    
    def calcular_total_con_iva(self, porcentaje: float = 0.21) -> float:
        """Calcula el total con IVA"""
        return self.importe * (1 + porcentaje)
    
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la oferta a diccionario"""
        return {
            'empresa': self.empresa,
            'importe': self.importe,
            'orden_clasificatorio': self.orden_clasificatorio,
            'presenta_oferta': self.presenta_oferta,
            'estado': self.estado.value,
            'fecha_presentacion': self.fecha_presentacion.isoformat() if self.fecha_presentacion else None,
            'observaciones': self.observaciones
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Alias para a_diccionario para compatibilidad"""
        return self.a_diccionario()
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'Oferta':
        """Alias para desde_diccionario para compatibilidad"""
        return cls.desde_diccionario(datos)
    
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> 'Oferta':
        """Crea una oferta desde diccionario"""
        fecha_str = datos.get('fecha_presentacion')
        fecha_presentacion = None
        if fecha_str:
            fecha_presentacion = date.fromisoformat(fecha_str)
        
        return cls(
            empresa=datos.get('empresa', ''),
            importe=datos.get('importe', 0.0),
            orden_clasificatorio=datos.get('orden_clasificatorio', 0),
            presenta_oferta=datos.get('presenta_oferta', True),
            estado=EstadoOferta(datos.get('estado', 'presentada')),
            fecha_presentacion=fecha_presentacion,
            observaciones=datos.get('observaciones', '')
        )


@dataclass
class DatosContrato:
    """Datos principales del contrato"""
    numero_expediente: str = ""
    objeto_contrato: str = ""
    tipo_contrato: TipoContrato = TipoContrato.SERVICIO
    importe_licitacion: float = 0.0
    importe_iva: float = 0.0
    importe_total: float = 0.0
    duracion: str = ""
    plazo_ejecucion: str = ""
    
    def __init__(self, numero_expediente="", objeto_contrato="", tipo_contrato=None, 
                 tipo=None, presupuesto_base=None, importe_licitacion=None, 
                 importe_iva=0.0, importe_total=0.0, duracion="", plazo_ejecucion="", **kwargs):
        """Constructor con compatibilidad para parámetros legacy"""
        self.numero_expediente = numero_expediente
        self.objeto_contrato = objeto_contrato
        
        # Compatibilidad con 'tipo' parameter
        if tipo is not None:
            if isinstance(tipo, str):
                self.tipo_contrato = TipoContrato.OBRA if tipo.lower() == 'obra' else TipoContrato.SERVICIO
            else:
                self.tipo_contrato = tipo
        else:
            self.tipo_contrato = tipo_contrato or TipoContrato.SERVICIO
        
        # Compatibilidad con 'presupuesto_base'
        if presupuesto_base is not None:
            self.importe_licitacion = float(presupuesto_base)
        elif importe_licitacion is not None:
            self.importe_licitacion = float(importe_licitacion)
        else:
            self.importe_licitacion = 0.0
            
        self.importe_iva = float(importe_iva)
        self.importe_total = float(importe_total)
        self.duracion = duracion
        self.plazo_ejecucion = plazo_ejecucion
        
        # Inicializar fechas y campos adicionales con valores por defecto
        for field_name in ['fecha_limite_presentacion', 'fecha_apertura', 'fecha_adjudicacion',
                          'fecha_inicio', 'fecha_fin_prevista', 'fecha_recepcion']:
            setattr(self, field_name, kwargs.get(field_name, None))
        
        for field_name in ['responsable_contrato', 'director_obra', 'justificacion', 'criterios_adjudicacion']:
            setattr(self, field_name, kwargs.get(field_name, ""))
    
    # Fechas importantes
    fecha_limite_presentacion: Optional[date] = None
    fecha_apertura: Optional[date] = None
    fecha_adjudicacion: Optional[date] = None
    fecha_inicio: Optional[date] = None
    fecha_fin_prevista: Optional[date] = None
    fecha_recepcion: Optional[date] = None
    
    # Responsables
    responsable_contrato: str = ""
    director_obra: str = ""
    
    # Datos adicionales
    justificacion: str = ""
    criterios_adjudicacion: str = ""
    
    def calcular_iva(self, porcentaje: float = 0.21) -> float:
        """Calcula el IVA del importe de licitación"""
        iva = self.importe_licitacion * porcentaje
        self.importe_iva = iva
        return iva
    
    def calcular_total(self, porcentaje: float = 0.21) -> float:
        """Calcula el total con IVA"""
        total = self.importe_licitacion * (1 + porcentaje)
        self.importe_total = total
        return total
    
    def es_obra(self) -> bool:
        """Verifica si es un contrato de obra"""
        return self.tipo_contrato == TipoContrato.OBRA
    
    def es_servicio(self) -> bool:
        """Verifica si es un contrato de servicio"""
        return self.tipo_contrato == TipoContrato.SERVICIO
    
    def obtener_limite_contratacion(self) -> float:
        """Obtiene el límite de contratación según el tipo"""
        if self.es_obra():
            return 15000.0  # Límite para obras
        else:
            return 40000.0  # Límite para servicios
    
    def cumple_limite_contratacion(self) -> bool:
        """Verifica si cumple los límites de contratación"""
        return self.importe_licitacion <= self.obtener_limite_contratacion()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el contrato a diccionario"""
        return {
            'numero_expediente': self.numero_expediente,
            'objeto_contrato': self.objeto_contrato,
            'tipo_contrato': self.tipo_contrato.value,
            'importe_licitacion': self.importe_licitacion,
            'importe_iva': self.importe_iva,
            'importe_total': self.importe_total,
            'duracion': self.duracion,
            'plazo_ejecucion': self.plazo_ejecucion,
            'fecha_limite_presentacion': self.fecha_limite_presentacion.isoformat() if self.fecha_limite_presentacion else None,
            'fecha_apertura': self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            'fecha_adjudicacion': self.fecha_adjudicacion.isoformat() if self.fecha_adjudicacion else None,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin_prevista': self.fecha_fin_prevista.isoformat() if self.fecha_fin_prevista else None,
            'fecha_recepcion': self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            'responsable_contrato': self.responsable_contrato,
            'director_obra': self.director_obra,
            'justificacion': self.justificacion,
            'criterios_adjudicacion': self.criterios_adjudicacion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatosContrato':
        """Crea datos de contrato desde diccionario"""
        # Convertir fechas
        fechas = {}
        for campo in ['fecha_limite_presentacion', 'fecha_apertura', 'fecha_adjudicacion', 
                      'fecha_inicio', 'fecha_fin_prevista', 'fecha_recepcion']:
            fecha_str = data.get(campo)
            fechas[campo] = date.fromisoformat(fecha_str) if fecha_str else None
        
        return cls(
            numero_expediente=data.get('numero_expediente', ''),
            objeto_contrato=data.get('objeto_contrato', ''),
            tipo_contrato=TipoContrato(data.get('tipo_contrato', 'servicio')),
            importe_licitacion=data.get('importe_licitacion', 0.0),
            importe_iva=data.get('importe_iva', 0.0),
            importe_total=data.get('importe_total', 0.0),
            duracion=data.get('duracion', ''),
            plazo_ejecucion=data.get('plazo_ejecucion', ''),
            responsable_contrato=data.get('responsable_contrato', ''),
            director_obra=data.get('director_obra', ''),
            justificacion=data.get('justificacion', ''),
            criterios_adjudicacion=data.get('criterios_adjudicacion', ''),
            **fechas
        )


@dataclass
class DatosLiquidacion:
    """Datos específicos para liquidación económica"""
    importe_licitado: float = 0.0
    importe_facturado: float = 0.0
    importe_penalizaciones: float = 0.0
    diferencia: float = 0.0
    porcentaje_ejecutado: float = 0.0
    empresa_ejecutora: str = ""
    saldo_favor_adif: float = 0.0
    saldo_favor_empresa: float = 0.0
    fecha_liquidacion: Optional[date] = None
    observaciones_liquidacion: str = ""
    
    def __init__(self, importe_licitado=None, importe_adjudicado=None, importe_facturado=0.0, 
                 importe_penalizaciones=0.0, diferencia=0.0, porcentaje_ejecutado=0.0,
                 empresa_ejecutora="", saldo_favor_adif=0.0, saldo_favor_empresa=0.0,
                 fecha_liquidacion=None, observaciones_liquidacion="", **kwargs):
        """Constructor con compatibilidad para parámetros legacy"""
        # Compatibilidad con 'importe_adjudicado'
        if importe_adjudicado is not None:
            self.importe_licitado = float(importe_adjudicado)
        elif importe_licitado is not None:
            self.importe_licitado = float(importe_licitado)
        else:
            self.importe_licitado = 0.0
            
        self.importe_facturado = float(importe_facturado)
        self.importe_penalizaciones = float(importe_penalizaciones)
        self.diferencia = float(diferencia)
        self.porcentaje_ejecutado = float(porcentaje_ejecutado)
        self.empresa_ejecutora = empresa_ejecutora
        self.saldo_favor_adif = float(saldo_favor_adif)
        self.saldo_favor_empresa = float(saldo_favor_empresa)
        self.fecha_liquidacion = fecha_liquidacion
        self.observaciones_liquidacion = observaciones_liquidacion
    
    def calcular_diferencia(self) -> float:
        """Calcula la diferencia entre licitado y facturado"""
        self.diferencia = abs(self.importe_licitado - self.importe_facturado - self.importe_penalizaciones)
        return self.diferencia
    
    def calcular_porcentaje_ejecutado(self) -> float:
        """Calcula el porcentaje de ejecución"""
        if self.importe_licitado > 0:
            self.porcentaje_ejecutado = (self.importe_facturado / self.importe_licitado) * 100
        else:
            self.porcentaje_ejecutado = 0.0
        return self.porcentaje_ejecutado
    
    def calcular_saldos(self) -> tuple[float, float]:
        """Calcula saldos a favor de ADIF y empresa"""
        diferencia = self.importe_licitado - self.importe_facturado + self.importe_penalizaciones
        
        if diferencia > 0:
            self.saldo_favor_adif = diferencia
            self.saldo_favor_empresa = 0.0
        elif diferencia < 0:
            self.saldo_favor_adif = 0.0
            self.saldo_favor_empresa = abs(diferencia)
        else:
            self.saldo_favor_adif = 0.0
            self.saldo_favor_empresa = 0.0
        
        return self.saldo_favor_adif, self.saldo_favor_empresa
    
    def actualizar_calculos(self):
        """Actualiza todos los cálculos de liquidación"""
        self.calcular_diferencia()
        self.calcular_porcentaje_ejecutado()
        self.calcular_saldos()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte liquidación a diccionario"""
        return {
            'importe_licitado': self.importe_licitado,
            'importe_facturado': self.importe_facturado,
            'importe_penalizaciones': self.importe_penalizaciones,
            'diferencia': self.diferencia,
            'porcentaje_ejecutado': self.porcentaje_ejecutado,
            'empresa_ejecutora': self.empresa_ejecutora,
            'saldo_favor_adif': self.saldo_favor_adif,
            'saldo_favor_empresa': self.saldo_favor_empresa,
            'fecha_liquidacion': self.fecha_liquidacion.isoformat() if self.fecha_liquidacion else None,
            'observaciones_liquidacion': self.observaciones_liquidacion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatosLiquidacion':
        """Crea liquidación desde diccionario"""
        fecha_str = data.get('fecha_liquidacion')
        fecha_liquidacion = date.fromisoformat(fecha_str) if fecha_str else None
        
        return cls(
            importe_licitado=data.get('importe_licitado', 0.0),
            importe_facturado=data.get('importe_facturado', 0.0),
            importe_penalizaciones=data.get('importe_penalizaciones', 0.0),
            diferencia=data.get('diferencia', 0.0),
            porcentaje_ejecutado=data.get('porcentaje_ejecutado', 0.0),
            empresa_ejecutora=data.get('empresa_ejecutora', ''),
            saldo_favor_adif=data.get('saldo_favor_adif', 0.0),
            saldo_favor_empresa=data.get('saldo_favor_empresa', 0.0),
            fecha_liquidacion=fecha_liquidacion,
            observaciones_liquidacion=data.get('observaciones_liquidacion', '')
        )


@dataclass
class Proyecto:
    """Modelo principal del proyecto de contratación"""
    nombre: str = ""
    ruta: str = ""
    archivo_json: str = ""
    
    # Datos del contrato
    contrato: DatosContrato = field(default_factory=DatosContrato)
    
    # Empresas y ofertas
    empresas: List[Empresa] = field(default_factory=list)
    ofertas: List[Oferta] = field(default_factory=list)
    
    # Datos de liquidación
    liquidacion: DatosLiquidacion = field(default_factory=DatosLiquidacion)
    
    # Metadatos
    fecha_creacion: datetime = field(default_factory=datetime.now)
    ultima_modificacion: datetime = field(default_factory=datetime.now)
    version: str = "3.0"
    
    @property 
    def datos_contrato(self) -> DatosContrato:
        """Alias para compatibilidad con tests"""
        return self.contrato
    
    def obtener_oferta_ganadora(self) -> Optional[Oferta]:
        """Alias para obtener_oferta_minima"""
        return self.obtener_oferta_minima()
    
    def agregar_empresa(self, empresa: Empresa):
        """Agregar empresa al proyecto"""
        if empresa not in self.empresas:
            self.empresas.append(empresa)
    
    def exportar_json(self) -> Dict[str, Any]:
        """Exportar proyecto a diccionario"""
        return {
            'nombre': self.nombre,
            'ruta': self.ruta,
            'archivo_json': self.archivo_json,
            'contrato': self.contrato.to_dict(),
            'empresas': [empresa.to_dict() for empresa in self.empresas],
            'ofertas': [oferta.a_diccionario() for oferta in self.ofertas],
            'liquidacion': self.liquidacion.to_dict(),
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'ultima_modificacion': self.ultima_modificacion.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def importar_json(cls, data: Dict[str, Any]) -> 'Proyecto':
        """Importar proyecto desde diccionario"""
        proyecto = cls(
            nombre=data.get('nombre', ''),
            ruta=data.get('ruta', ''),
            archivo_json=data.get('archivo_json', '')
        )
        
        # Cargar contrato
        if 'contrato' in data:
            proyecto.contrato = DatosContrato.from_dict(data['contrato'])
        
        # Cargar empresas
        if 'empresas' in data:
            proyecto.empresas = [Empresa.from_dict(emp) for emp in data['empresas']]
        
        # Cargar ofertas
        if 'ofertas' in data:
            proyecto.ofertas = [Oferta.desde_diccionario(oferta) for oferta in data['ofertas']]
        
        # Cargar liquidación
        if 'liquidacion' in data:
            proyecto.liquidacion = DatosLiquidacion.from_dict(data['liquidacion'])
            
        return proyecto
    
    def obtener_empresa_adjudicataria(self) -> Optional[Empresa]:
        """Obtiene la empresa con la oferta más baja"""
        if not self.ofertas:
            return None
        
        ofertas_validas = [o for o in self.ofertas if o.es_valida()]
        if not ofertas_validas:
            return None
        
        oferta_minima = min(ofertas_validas, key=lambda x: x.importe)
        
        for empresa in self.empresas:
            if empresa.nombre == oferta_minima.empresa:
                return empresa
        return None
    
    def obtener_oferta_minima(self) -> Optional[Oferta]:
        """Obtiene la oferta con menor importe"""
        ofertas_validas = [o for o in self.ofertas if o.es_valida()]
        if not ofertas_validas:
            return None
        return min(ofertas_validas, key=lambda x: x.importe)
    
    def contar_ofertas_validas(self) -> int:
        """Cuenta las ofertas válidas presentadas"""
        return len([o for o in self.ofertas if o.es_valida()])
    
    def hay_ofertas_duplicadas(self) -> bool:
        """Verifica si hay múltiples ofertas con el mismo importe mínimo"""
        oferta_minima = self.obtener_oferta_minima()
        if not oferta_minima:
            return False
        
        ofertas_minimas = [
            o for o in self.ofertas 
            if o.es_valida() and abs(o.importe - oferta_minima.importe) < 0.01
        ]
        
        return len(ofertas_minimas) > 1
    
    def sincronizar_ofertas_con_empresas(self):
        """Sincroniza la lista de ofertas con las empresas"""
        # Crear ofertas faltantes
        empresas_con_oferta = {o.empresa for o in self.ofertas}
        
        for empresa in self.empresas:
            if empresa.nombre not in empresas_con_oferta:
                oferta = Oferta(
                    empresa=empresa.nombre,
                    importe=empresa.oferta or 0.0,
                    presenta_oferta=empresa.tiene_oferta()
                )
                self.ofertas.append(oferta)
        
        # Eliminar ofertas de empresas que ya no existen
        nombres_empresas = {e.nombre for e in self.empresas}
        self.ofertas = [o for o in self.ofertas if o.empresa in nombres_empresas]
        
        # Actualizar importes en empresas
        for oferta in self.ofertas:
            for empresa in self.empresas:
                if empresa.nombre == oferta.empresa and oferta.es_valida():
                    empresa.oferta = oferta.importe
    
    def actualizar_metadatos(self):
        """Actualiza metadatos del proyecto"""
        self.ultima_modificacion = datetime.now()
    
    def es_valido(self) -> bool:
        """Verifica si el proyecto tiene datos mínimos válidos"""
        return (
            bool(self.nombre.strip()) and
            bool(self.contrato.numero_expediente.strip()) and
            bool(self.contrato.objeto_contrato.strip()) and
            len(self.empresas) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el proyecto completo a diccionario"""
        return {
            'nombre': self.nombre,
            'ruta': self.ruta,
            'archivo_json': self.archivo_json,
            'contrato': self.contrato.to_dict(),
            'empresas': [e.to_dict() for e in self.empresas],
            'ofertas': [o.to_dict() for o in self.ofertas],
            'liquidacion': self.liquidacion.to_dict(),
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'ultima_modificacion': self.ultima_modificacion.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proyecto':
        """Crea un proyecto desde diccionario"""
        proyecto = cls(
            nombre=data.get('nombre', ''),
            ruta=data.get('ruta', ''),
            archivo_json=data.get('archivo_json', ''),
            version=data.get('version', '3.0')
        )
        
        # Cargar fechas
        fecha_creacion_str = data.get('fecha_creacion')
        if fecha_creacion_str:
            proyecto.fecha_creacion = datetime.fromisoformat(fecha_creacion_str)
        
        fecha_modificacion_str = data.get('ultima_modificacion')
        if fecha_modificacion_str:
            proyecto.ultima_modificacion = datetime.fromisoformat(fecha_modificacion_str)
        
        # Cargar contrato
        contrato_data = data.get('contrato', {})
        proyecto.contrato = DatosContrato.from_dict(contrato_data)
        
        # Cargar empresas
        empresas_data = data.get('empresas', [])
        proyecto.empresas = [Empresa.from_dict(e) for e in empresas_data]
        
        # Cargar ofertas
        ofertas_data = data.get('ofertas', [])
        proyecto.ofertas = [Oferta.from_dict(o) for o in ofertas_data]
        
        # Cargar liquidación
        liquidacion_data = data.get('liquidacion', {})
        proyecto.liquidacion = DatosLiquidacion.from_dict(liquidacion_data)
        
        return proyecto


@dataclass
class ConfiguracionUI:
    """Configuración de la interfaz de usuario"""
    ventana_ancho: int = 1200
    ventana_alto: int = 800
    mostrar_tooltips: bool = True
    validacion_tiempo_real: bool = True
    autoguardar_intervalo: int = 300  # segundos
    tema: str = "claro"  # "claro" o "oscuro"
    idioma: str = "es"  # "es" o "en"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario"""
        return {
            'ventana_ancho': self.ventana_ancho,
            'ventana_alto': self.ventana_alto,
            'mostrar_tooltips': self.mostrar_tooltips,
            'validacion_tiempo_real': self.validacion_tiempo_real,
            'autoguardar_intervalo': self.autoguardar_intervalo,
            'tema': self.tema,
            'idioma': self.idioma
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfiguracionUI':
        """Crea configuración desde diccionario"""
        return cls(
            ventana_ancho=data.get('ventana_ancho', 1200),
            ventana_alto=data.get('ventana_alto', 800),
            mostrar_tooltips=data.get('mostrar_tooltips', True),
            validacion_tiempo_real=data.get('validacion_tiempo_real', True),
            autoguardar_intervalo=data.get('autoguardar_intervalo', 300),
            tema=data.get('tema', 'claro'),
            idioma=data.get('idioma', 'es')
        )


@dataclass


# Constantes del dominio
class Constantes:
    """Constantes utilizadas en toda la aplicación"""
    
    # Límites de contratación (en euros)
    LIMITE_OBRA = 15000.0
    LIMITE_SERVICIO = 40000.0
    
    # Porcentajes
    IVA_GENERAL = 0.21
    PORCENTAJE_VEZ_Y_MEDIA = 1.5
    PORCENTAJE_SETENTA = 0.7
    
    # Formatos de fecha
    FORMATO_FECHA_CORTA = "%d/%m/%Y"
    FORMATO_FECHA_LARGA = "%d de %B de %Y"
    FORMATO_FECHA_ISO = "%Y-%m-%d"
    
    # Extensiones de archivo
    EXTENSION_PROYECTO = ".PROJPMF"
    EXTENSION_WORD = ".docx"
    EXTENSION_PDF = ".pdf"
    EXTENSION_EXCEL = [".xlsx", ".xls"]
    
    # Nombres de carpetas del proyecto
    CARPETAS_PROYECTO = [
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
    
    # Plantillas de documentos
    PLANTILLAS = {
        'acta_inicio_obra': 'Modelo_Inicio_Contrato_obr.docx',
        'acta_inicio_servicio': 'Modelo_Inicio_Contrato_serv.docx',
        'carta_invitacion': 'ModeloCartaInvitacion.docx',
        'acta_adjudicacion': 'Modelo_Acta_Resolucion_Adjudicacion.docx',
        'carta_adjudicatario': 'Modelo_carta_adjudicatario.docx',
        'carta_no_adjudicatario': 'Modelo_carta_no_adjudicatario.docx',
        'acta_liquidacion_obra': 'Modelo_Acta_Liquidacion_obra.docx',
        'acta_liquidacion_servicio': 'Modelo_Acta_Liquidacion_serv.docx',
        'acta_replanteo': 'Modelo_Acta_Replanteo.docx',
        'acta_recepcion': 'Modelo_Acta_Recepcion.docx',
        'director_obra': 'Modelo_director_obra.docx'
    }
    
    # Mensajes de error comunes
    MENSAJES_ERROR = {
        'proyecto_no_encontrado': 'Archivo de proyecto no encontrado',
        'datos_invalidos': 'Los datos ingresados no son válidos',
        'campos_vacios': 'Hay campos obligatorios vacíos',
        'ofertas_duplicadas': 'Hay múltiples ofertas con el mismo importe mínimo',
        'sin_ofertas': 'No hay ofertas válidas para evaluar',
        'error_guardado': 'Error al guardar el proyecto',
        'error_generacion': 'Error al generar el documento',
        'fechas_incorrectas': 'Las fechas ingresadas no son correctas',
        'limite_excedido': 'El importe excede el límite de contratación'
    }
    
    # URLs útiles
    URLS = {
        'portafirmas': 'https://portafirmas.adif.es/ePortafirmas/Inicio.do?cr=',
        'boe_contratos': 'https://www.boe.es/buscar/act.php?id=BOE-A-2017-12902'
    }


# Funciones auxiliares para modelos
def crear_proyecto_vacio(nombre: str, ruta: str) -> Proyecto:
    """Crea un proyecto vacío con valores por defecto"""
    proyecto = Proyecto(
        nombre=nombre,
        ruta=ruta,
        archivo_json=os.path.join(ruta, f"{nombre}{Constantes.EXTENSION_PROYECTO}")
    )
    
    # Agregar una empresa vacía por defecto
    proyecto.empresas.append(Empresa())
    
    return proyecto



