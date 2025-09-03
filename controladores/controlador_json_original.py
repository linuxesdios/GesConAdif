#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador JSON especializado SOLO para lectura/escritura de datos JSON
Sin lógica de UI, solo operaciones puras de datos
"""
import json
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import QMessageBox

class GestorContratosJSON:
    """Gestor especializado SOLO para operaciones JSON de contratos"""
    
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.datos = self._cargar_datos_iniciales()
        logger.info(f"[GestorContratosJSON] 📁 Inicializado con archivo: {ruta_archivo}")

    def _cargar_datos_iniciales(self) -> Dict[str, Any]:
        """Cargar datos con verificación mejorada de archivos"""
        try:
            logger.debug(f"[GestorContratosJSON] Intentando cargar: {self.ruta_archivo}")
            logger.debug(f"[GestorContratosJSON] Archivo existe: {os.path.exists(self.ruta_archivo)}")
            
            if os.path.exists(self.ruta_archivo):
                # Verificar que el archivo no esté vacío
                tamaño = os.path.getsize(self.ruta_archivo)
                logger.debug(f"[GestorContratosJSON] Tamaño del archivo: {tamaño} bytes")
                
                if tamaño == 0:
                    logger.warning(f"[GestorContratosJSON] Archivo vacío, creando estructura inicial")
                    return self._crear_estructura_inicial()
                
                with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                    obras_count = len(datos.get('obras', []))
                    logger.info(f"[GestorContratosJSON] Datos cargados: {obras_count} obras")
                    
                    if obras_count == 0:
                        logger.warning(f"[GestorContratosJSON] No hay obras en el archivo")
                    else:
                        # Mostrar nombres de las primeras 3 obras para debug
                        obras = datos.get('obras', [])
                        for i, obra in enumerate(obras[:3]):
                            nombre = obra.get('nombreObra', 'Sin nombre')
                            logger.debug(f"[GestorContratosJSON] Obra {i+1}: {nombre}")
                    
                    return datos
            else:
                logger.info(f"[GestorContratosJSON] Archivo no existe, creando nuevo...")
                return self._crear_estructura_inicial()
                    
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"[GestorContratosJSON] Error cargando/creando JSON: {e}")
            return {"firmantes": {}, "obras": []}

    def _crear_estructura_inicial(self) -> Dict[str, Any]:
        """Crear estructura inicial del JSON"""
        estructura_inicial = {
            "firmantes": {
                "firmanteConforme": "PABLO MARTÍN FERNÁNDEZ",
                "cargoConforme": "Cuadro Técnico de Mantenimiento",
                "firmantePropone": "",
                "cargoPropone": "",
                "firmanteAprueba": "MARÍA CRUZ NIETO TORTUERO",
                "cargoAprueba": "Gerente del Área de Patrimonio y Urbanismo Centro",
                "cargoResponsable": "",
                "representanteFirma": "",
                "directorFacultativo": "",
                "representanteAdif": "",
                "nombreAsistenteAdif": ""
            },
            "obras": []
        }
        
        # Crear directorio si no existe
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            logger.info(f"[GestorContratosJSON] Directorio creado: {directorio}")
        
        # Guardar archivo inicial
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(estructura_inicial, archivo, ensure_ascii=False, indent=2)
            logger.info(f"[GestorContratosJSON] BaseDatos.json creado: {self.ruta_archivo}")
        except Exception as e:
            logger.error(f"[GestorContratosJSON] Error creando archivo inicial: {e}")
        
        return estructura_inicial
    def recargar_datos(self) -> bool:
        """Recargar datos desde el archivo"""
        try:
            self.datos = self._cargar_datos_iniciales()
            return True
        except Exception as e:
            logger.error(f"[GestorContratosJSON] ❌ Error recargando datos: {e}")
            return False

    def guardar_datos(self) -> bool:
        """Guardar datos actuales en el archivo JSON"""
        try:
            # Crear directorio si no existe
            directorio = os.path.dirname(self.ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            
            # Escribir archivo con formato legible
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(self.datos, archivo, ensure_ascii=False, indent=2)
            
            logger.info(f"[GestorContratosJSON] 💾 Datos guardados exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"[GestorContratosJSON] ❌ Error guardando datos: {e}")
            return False

    def buscar_contrato_por_nombre(self, nombre_contrato: str) -> Optional[Dict[str, Any]]:
        """🔧 BÚSQUEDA MEJORADA: Buscar contrato por nombre exacto o parcial"""
        if not nombre_contrato:
            return None
            
        obras = self.datos.get("obras", [])
        logger.debug(f"[GestorContratosJSON] 🔍 Buscando contrato por nombre: '{nombre_contrato}' en {len(obras)} obras")
        
        # 🆕 DEBUG: Mostrar nombres disponibles
        for i, obra in enumerate(obras):
            nombre_obra = obra.get("nombreObra", "N/A")
            print(f"[GestorContratosJSON] 📋 Obra[{i}]: '{nombre_obra}'")
        
        # 1. Búsqueda exacta
        for obra in obras:
            if obra.get("nombreObra") == nombre_contrato:
                print(f"[GestorContratosJSON] ✅ Coincidencia exacta encontrada: '{nombre_contrato}'")
                return obra
        
        # 2. Búsqueda parcial para nombres truncados
        if nombre_contrato.endswith("..."):
            nombre_parcial = nombre_contrato[:-3]
            for obra in obras:
                nombre_obra = obra.get("nombreObra", "")
                if nombre_obra.startswith(nombre_parcial):
                    return obra
        
        # 3. Búsqueda por similitud
        for obra in obras:
            nombre_obra = obra.get("nombreObra", "")
            if len(nombre_contrato) > 10:  # Solo para nombres suficientemente largos
                if nombre_contrato in nombre_obra or nombre_obra in nombre_contrato:
                    return obra
        
        print(f"[GestorContratosJSON] ❌ Contrato no encontrado: '{nombre_contrato}'")
        return None

    def buscar_contrato_por_expediente(self, numero_expediente: str) -> Optional[Dict[str, Any]]:
        """Buscar contrato por número de expediente"""
        if not numero_expediente:
            return None
            
        obras = self.datos.get("obras", [])
        
        for obra in obras:
            if obra.get("numeroExpediente") == numero_expediente:
                return obra
        
        print(f"[GestorContratosJSON] ❌ Expediente no encontrado: '{numero_expediente}'")
        return None

    def buscar_contrato_inteligente(self, identificador: str) -> Optional[Dict[str, Any]]:
        """🔧 BÚSQUEDA CORREGIDA: Primero por nombre, después por expediente"""
        if not identificador:
            return None
        
        identificador = identificador.strip()
        
        # 🆕 PASO 1: Buscar SIEMPRE por nombre primero
        resultado_nombre = self.buscar_contrato_por_nombre(identificador)
        if resultado_nombre:
            print(f"[GestorContratosJSON] ✅ Contrato encontrado por nombre: '{identificador}'")
            return resultado_nombre
        
        # 🆕 PASO 2: Solo si no se encuentra por nombre, buscar por expediente
        # Detectar si es un número de expediente (contiene números y separadores)
        patron_expediente = re.compile(r'^\d{1,5}[\/\.\-\d]+$')
        
        if patron_expediente.match(identificador):
            print(f"[GestorContratosJSON] 🔍 Buscando por expediente: '{identificador}'")
            resultado_expediente = self.buscar_contrato_por_expediente(identificador)
            if resultado_expediente:
                print(f"[GestorContratosJSON] ✅ Contrato encontrado por expediente: '{identificador}'")
                return resultado_expediente
        
        print(f"[GestorContratosJSON] ❌ No encontrado ni por nombre ni por expediente: '{identificador}'")
        return None
    
    
    def crear_contrato(self, datos_contrato: Dict[str, Any]) -> bool:
        """Crear nuevo contrato en el JSON"""
        try:
            nombre_obra = datos_contrato.get("nombreObra", "").strip()
            if not nombre_obra:
                print("[GestorContratosJSON] ❌ Nombre de obra requerido")
                return False
            
            # Verificar que no existe
            if self.buscar_contrato_por_nombre(nombre_obra):
                print(f"[GestorContratosJSON] ❌ Ya existe contrato: {nombre_obra}")
                return False
            
            # Preparar datos con estructura básica
            nuevo_contrato = {
                "nombreObra": nombre_obra,
                "fechaCreacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **datos_contrato  # Agregar datos adicionales
            }
            
            # Agregar a la lista de obras
            obras = self.datos.setdefault("obras", [])
            obras.append(nuevo_contrato)
            
            # Guardar
            if self.guardar_datos():
                print(f"[GestorContratosJSON] ✅ Contrato creado: {nombre_obra}")
                return True
            else:
                # Revertir si falla el guardado
                obras.remove(nuevo_contrato)
                return False
                
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error creando contrato: {e}")
            return False

    def actualizar_contrato(self, nombre_contrato: str, datos_actualizados: Dict[str, Any]) -> bool:
        """Actualizar contrato existente"""
        try:
            if not nombre_contrato:
                return False
            
            obras = self.datos.get("obras", [])
            
            # Buscar el contrato
            for i, obra in enumerate(obras):
                if obra.get("nombreObra") == nombre_contrato:
                    # Actualizar datos manteniendo la estructura
                    obras[i].update(datos_actualizados)
                    obras[i]["fechaModificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Guardar
                    if self.guardar_datos():
                        print(f"[GestorContratosJSON] ✅ Contrato actualizado: {nombre_contrato}")
                        return True
                    else:
                        return False
            
            print(f"[GestorContratosJSON] ❌ No se encontró contrato para actualizar: {nombre_contrato}")
            return False
            
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error actualizando contrato: {e}")
            return False

    
    def listar_contratos(self) -> List[Dict[str, str]]:
        """Listar todos los contratos con información básica"""
        try:
            obras = self.datos.get("obras", [])
            resultado = []
            
            for obra in obras:
                info_basica = {
                    "nombreObra": obra.get("nombreObra", "Sin nombre"),
                    "numeroExpediente": obra.get("numeroExpediente", "Sin expediente"),
                    "fechaCreacion": obra.get("fechaCreacion", "Desconocida"),
                    "tipoActuacion": obra.get("tipoActuacion", "Sin especificar")
                }
                resultado.append(info_basica)
            
            return resultado
            
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error listando contratos: {e}")
            return []

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas básicas del JSON"""
        try:
            obras = self.datos.get("obras", [])
            
            tipos = {}
            for obra in obras:
                tipo = obra.get("tipoActuacion", "Sin especificar")
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            estadisticas = {
                "total_contratos": len(obras),
                "tipos_actuacion": tipos,
                "archivo": self.ruta_archivo,
                "tamaño_archivo_mb": round(os.path.getsize(self.ruta_archivo) / 1024 / 1024, 2) if os.path.exists(self.ruta_archivo) else 0
            }
            
            return estadisticas
            
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error obteniendo estadísticas: {e}")
            return {}

    def obtener_todos_nombres_obras(self) -> List[str]:
        """Método de compatibilidad - obtener todos los nombres de obras"""
        try:
            obras = self.datos.get("obras", [])
            nombres = []
            for obra in obras:
                nombre = obra.get("nombreObra")
                if nombre:
                    nombres.append(nombre)
            return nombres
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error obteniendo nombres: {e}")
            return []

    def obtener_contrato_por_nombre(self, nombre_contrato: str) -> Dict[str, Any]:
        """Método de compatibilidad - obtener contrato por nombre"""
        resultado = self.buscar_contrato_por_nombre(nombre_contrato)
        return resultado if resultado else {}

    def cargar_datos_obra(self, identificador: str) -> Dict[str, Any]:
        """Método de compatibilidad - cargar datos de obra"""
        resultado = self.buscar_contrato_inteligente(identificador)
        return resultado if resultado else {}

    def get_contract_type_for_contract(self, nombre_contrato: str) -> str:
        """Método de compatibilidad - obtener tipo de contrato"""
        try:
            contrato = self.buscar_contrato_por_nombre(nombre_contrato)
            if not contrato:
                return "servicios"
            
            tipo_actuacion = contrato.get("tipoActuacion", "").lower()
            
            if "obra" in tipo_actuacion:
                return "obras_puntual"
            elif "mantenimiento" in tipo_actuacion:
                return "mantenimiento"
            elif "servicio" in tipo_actuacion:
                return "servicios"
            else:
                # Fallback basado en nombre
                nombre_lower = nombre_contrato.lower()
                if any(word in nombre_lower for word in ["construcción", "obras", "puente", "edificio"]):
                    return "obras_puntual"
                elif any(word in nombre_lower for word in ["mantenimiento", "conservación"]):
                    return "mantenimiento"
                else:
                    return "servicios"
        except Exception:
            return "servicios"
    def eliminar_contrato(self, nombre_contrato: str) -> bool:
        """Eliminar contrato del JSON - MÉTODO CORRECTO PARA GestorContratosJSON"""
        try:
            if not nombre_contrato:
                print(f"[GestorContratosJSON] ❌ Nombre de contrato requerido")
                return False
            
            obras = self.datos.get("obras", [])
            
            # Buscar y eliminar el contrato
            for i, obra in enumerate(obras):
                if obra.get("nombreObra") == nombre_contrato:
                    # Eliminar de la lista
                    del obras[i]
                    
                    # Guardar cambios
                    if self.guardar_datos():
                        print(f"[GestorContratosJSON] ✅ Contrato eliminado: {nombre_contrato}")
                        return True
                    else:
                        # Revertir si falla el guardado
                        obras.insert(i, obra)
                        print(f"[GestorContratosJSON] ❌ Error guardando después de eliminar")
                        return False
            
            print(f"[GestorContratosJSON] ❌ No se encontró contrato para eliminar: {nombre_contrato}")
            return False
            
        except Exception as e:
            print(f"[GestorContratosJSON] ❌ Error eliminando contrato: {e}")
            return False

class ControladorJson:
    """Controlador especializado SOLO para operaciones JSON"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.gestor = self._inicializar_gestor()

    def _inicializar_gestor(self) -> Optional[GestorContratosJSON]:
        """🔧 INICIALIZACIÓN UNIFICADA con ControladorRutas"""
        try:
            # 🆕 INTENTAR USAR CONTROLADOR DE RUTAS CENTRALIZADO PRIMERO
            try:
                from .controlador_routes import ControladorRutas
                rutas = ControladorRutas()
                ruta_bd = rutas.get_ruta_base_datos()
                
                print(f"[ControladorJson] ✅ Usando ruta centralizada: {ruta_bd}")
                return GestorContratosJSON(ruta_bd)
                
            except ImportError:
                print(f"[ControladorJson] ⚠️ ControladorRutas no disponible, usando búsqueda manual")
            
            # 🔧 FALLBACK: Búsqueda manual en ubicaciones conocidas
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Buscar BaseDatos.json en diferentes ubicaciones (incluyendo _internal)
            posibles_rutas = [
                os.path.join(current_dir, "BaseDatos.json"),
                os.path.join(os.path.dirname(current_dir), "BaseDatos.json"),
                os.path.join(current_dir, "..", "BaseDatos.json"),
                os.path.join(os.path.dirname(current_dir), "_internal", "BaseDatos", "BaseDatos.json"),  # 🆕
                "BaseDatos.json"  # Directorio actual
            ]
            
            for ruta in posibles_rutas:
                ruta_absoluta = os.path.abspath(ruta)
                if os.path.exists(ruta_absoluta):
                    print(f"[ControladorJson] ✅ BaseDatos.json encontrado: {ruta_absoluta}")
                    return GestorContratosJSON(ruta_absoluta)
            
            # Si no existe, usar la ubicación _internal para crear
            ruta_crear = os.path.abspath(posibles_rutas[3])  # _internal/BaseDatos/BaseDatos.json
            print(f"[ControladorJson] 📁 Creando BaseDatos.json en: {ruta_crear}")
            return GestorContratosJSON(ruta_crear)
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error inicializando gestor: {e}")
            return None

    def esta_disponible(self) -> bool:
        """Verificar si el controlador JSON está disponible"""
        return self.gestor is not None

    def recargar_datos(self) -> bool:
        """Recargar datos desde el archivo"""
        if not self.gestor:
            return False
        return self.gestor.recargar_datos()

    # =================== OPERACIONES DE LECTURA ===================
    
    def leer_contrato_completo(self, nombre_contrato: str) -> Optional[Dict[str, Any]]:
        """Leer datos completos de un contrato"""
        if not self.gestor or not nombre_contrato:
            return None
        return self.gestor.buscar_contrato_inteligente(nombre_contrato)

    def leer_campo_contrato(self, nombre_contrato: str, nombre_campo: str) -> Any:
        """Leer un campo específico de un contrato"""
        try:
            contrato = self.leer_contrato_completo(nombre_contrato)
            if contrato:
                return contrato.get(nombre_campo)
            return None
        except Exception as e:
            print(f"[ControladorJson] ❌ Error leyendo campo '{nombre_campo}': {e}")
            return None

    def leer_lista_contratos(self) -> List[Dict[str, str]]:
        """Leer lista básica de todos los contratos"""
        if not self.gestor:
            return []
        return self.gestor.listar_contratos()

    def leer_nombres_contratos(self) -> List[str]:
        """Leer solo los nombres de todos los contratos"""
        try:
            lista = self.leer_lista_contratos()
            return [item.get("nombreObra", "") for item in lista if item.get("nombreObra")]
        except Exception:
            return []

    def obtener_todos_nombres_obras(self) -> List[str]:
        """Método de compatibilidad - obtener todos los nombres de obras"""
        return self.leer_nombres_contratos()

    def obtener_contrato_por_nombre(self, nombre_contrato: str) -> Dict[str, Any]:
        """Método de compatibilidad - buscar contrato por nombre"""
        resultado = self.leer_contrato_completo(nombre_contrato)
        return resultado if resultado else {}

    def cargar_datos_obra(self, identificador: str) -> Dict[str, Any]:
        """Método de compatibilidad - cargar datos de obra"""
        resultado = self.leer_contrato_completo(identificador)
        return resultado if resultado else {}

    # =================== OPERACIONES DE ESCRITURA ===================
    
    def guardar_campo_en_json(self, nombre_contrato: str, nombre_campo: str, valor: str) -> bool:
        """Guardar un campo específico en el JSON"""
        if not self.gestor or not nombre_contrato or not nombre_campo:
            return False
        
        try:
            # Buscar contrato actual
            contrato_actual = self.gestor.buscar_contrato_inteligente(nombre_contrato)
            if not contrato_actual:
                print(f"[ControladorJson] ❌ No se encontró contrato: {nombre_contrato}")
                return False
            
            # Actualizar campo
            datos_actualizados = {nombre_campo: valor}
            return self.gestor.actualizar_contrato(nombre_contrato, datos_actualizados)
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error guardando campo '{nombre_campo}': {e}")
            return False

    def guardar_texto_largo_en_json(self, nombre_contrato: str, nombre_campo: str, texto: str) -> bool:
        """Guardar texto largo (mismo comportamiento que campo normal)"""
        return self.guardar_campo_en_json(nombre_contrato, nombre_campo, texto)

    def guardar_fecha_en_json(self, nombre_contrato: str, nombre_campo: str, fecha: str) -> bool:
        """Guardar fecha en formato específico"""
        return self.guardar_campo_en_json(nombre_contrato, nombre_campo, fecha)

    
    def guardar_empresas_unificadas_en_json(self, nombre_contrato: str, empresas_data: List[Dict[str, str]]) -> bool:
        """NUEVA: Guardar empresas en estructura unificada"""
        if not self.gestor or not nombre_contrato:
            return False
        
        try:
            # ✅ ESTRUCTURA UNIFICADA SIMPLE
            datos_empresas = {
                "empresas": empresas_data  # Array directo, no nested
            }
            
            return self.gestor.actualizar_contrato(nombre_contrato, datos_empresas)
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error guardando empresas unificadas: {e}")
            return False

    def guardar_empresas_en_json(self, nombre_contrato: str, empresas_data: List[Dict[str, str]]) -> bool:
        """MODIFICADA: Redirigir a método unificado"""
        return self.guardar_empresas_unificadas_en_json(nombre_contrato, empresas_data)

    def guardar_ofertas_en_json(self, nombre_contrato: str, ofertas_data: List[Dict[str, str]]) -> bool:
        """MODIFICADA: Las ofertas se guardan junto con empresas"""
        print("[ControladorJson] ℹ️ Las ofertas se guardan automáticamente con empresas unificadas")
        return True  # No hacer nada, ya se guardan unificadas
    
    def guardar_contrato_completo(self, nombre_contrato: str, datos_completos: Dict[str, Any]) -> bool:
        """Guardar/actualizar contrato completo"""
        if not self.gestor or not nombre_contrato:
            return False
        
        return self.gestor.actualizar_contrato(nombre_contrato, datos_completos)

    # =================== OPERACIONES DE GESTIÓN ===================
    
    def crear_contrato_nuevo(self, datos_contrato: Dict[str, Any]) -> bool:
        """Crear nuevo contrato"""
        
        if not self.gestor:
            print(f"[ControladorJson] ❌ Gestor no disponible")
            return False
        
        try:
            resultado = self.gestor.crear_contrato(datos_contrato)
            return resultado
        except Exception as e:
            print(f"[ControladorJson] ❌ Error en crear_contrato_nuevo: {e}")
            import traceback
            traceback.print_exc()
            return False

    

    # =================== UTILIDADES ===================
    
    def obtener_tipo_contrato(self, nombre_contrato: str) -> str:
        """Obtener tipo de contrato basado en tipoActuacion"""
        try:
            contrato = self.leer_contrato_completo(nombre_contrato)
            if not contrato:
                return "servicios"  # Default
            
            tipo_actuacion = contrato.get("tipoActuacion", "").lower()
            
            if "obra" in tipo_actuacion:
                return "obras_puntual"
            elif "mantenimiento" in tipo_actuacion:
                return "mantenimiento"
            elif "servicio" in tipo_actuacion:
                return "servicios"
            else:
                # Fallback basado en nombre
                nombre_lower = nombre_contrato.lower()
                if any(word in nombre_lower for word in ["construcción", "obras", "puente", "edificio"]):
                    return "obras_puntual"
                elif any(word in nombre_lower for word in ["mantenimiento", "conservación"]):
                    return "mantenimiento"
                else:
                    return "servicios"
                    
        except Exception:
            return "servicios"

    def get_contract_type_for_contract(self, nombre_contrato: str) -> str:
        """Método de compatibilidad - obtener tipo de contrato"""
        return self.obtener_tipo_contrato(nombre_contrato)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del JSON"""
        if not self.gestor:
            return {}
        
        return self.gestor.obtener_estadisticas()

    def validar_integridad_json(self) -> Dict[str, Any]:
        """Validar integridad de los datos JSON"""
        if not self.gestor:
            return {"valido": False, "errores": ["Gestor no disponible"]}
        
        try:
            errores = []
            warnings = []
            
            obras = self.gestor.datos.get("obras", [])
            
            # Validar estructura básica
            if not isinstance(obras, list):
                errores.append("'obras' no es una lista")
                return {"valido": False, "errores": errores, "warnings": warnings}
            
            # Validar contratos individuales
            nombres_duplicados = []
            nombres_vistos = set()
            
            for i, obra in enumerate(obras):
                if not isinstance(obra, dict):
                    errores.append(f"Obra {i} no es un diccionario")
                    continue
                
                nombre = obra.get("nombreObra")
                if not nombre:
                    warnings.append(f"Obra {i} sin nombreObra")
                elif nombre in nombres_vistos:
                    nombres_duplicados.append(nombre)
                else:
                    nombres_vistos.add(nombre)
            
            if nombres_duplicados:
                errores.append(f"Nombres duplicados: {nombres_duplicados}")
            
            return {
                "valido": len(errores) == 0,
                "errores": errores,
                "warnings": warnings,
                "total_contratos": len(obras),
                "nombres_unicos": len(nombres_vistos)
            }
            
        except Exception as e:
            return {"valido": False, "errores": [f"Error validando: {e}"]}
    def hacer_backup(self, sufijo: str = None) -> bool:
        """Crear backup del archivo JSON"""
        if not self.gestor or not os.path.exists(self.gestor.ruta_archivo):
            return False
        
        try:
            import shutil
            
            # Generar nombre de backup
            archivo_original = self.gestor.ruta_archivo
            directorio = os.path.dirname(archivo_original)
            nombre_base = os.path.splitext(os.path.basename(archivo_original))[0]
            
            if not sufijo:
                sufijo = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            archivo_backup = os.path.join(directorio, f"{nombre_base}_backup_{sufijo}.json")
            
            # Crear backup
            shutil.copy2(archivo_original, archivo_backup)
            
            return True
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error creando backup: {e}")
            return False

    def clonar_contrato(self, nombre_origen, nuevo_nombre, opciones=None):
        """Clonar un contrato existente con nuevo nombre y opciones selectivas"""
        try:
            # Verificar que el contrato origen existe
            contrato_origen = self.leer_contrato_completo(nombre_origen)
            if not contrato_origen:
                QMessageBox.critical(None, "Error", f"No se encontró el contrato: {nombre_origen}")
                return False
            
            # Verificar que el nuevo nombre no existe
            if self.leer_contrato_completo(nuevo_nombre):
                QMessageBox.warning(None, "Error", f"Ya existe un contrato con el nombre: {nuevo_nombre}")
                return False
            
            # Si no se especifican opciones, clonar todo (comportamiento legacy)
            if opciones is None:
                datos_clonados = contrato_origen.copy()
                datos_clonados["nombreObra"] = nuevo_nombre
            else:
                # Clonación selectiva según opciones
                datos_clonados = self._clonar_selectivo(contrato_origen, nuevo_nombre, opciones)
            
            # Crear nuevo contrato
            resultado = self.crear_contrato_nuevo(datos_clonados)
            
            if resultado:
                # 🆕 RECARGAR Y SELECCIONAR AUTOMÁTICAMENTE
                if self.main_window:
                    try:
                        # Recargar ContractManager
                        if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                            self.main_window.contract_manager.reload_contracts()
                            self.main_window.contract_manager._update_combo_box()
                            
                            # Seleccionar el contrato clonado
                            if hasattr(self.main_window, 'comboBox'):
                                index = self.main_window.comboBox.findText(nuevo_nombre)
                                if index >= 0:
                                    self.main_window.comboBox.setCurrentIndex(index)
                                    
                            # Limpiar campos no clonados
                            self._limpiar_campos_no_clonados(opciones)
                    
                    except Exception as e:
                        print(f"[ControladorJson] ⚠️ Error recargando después de clonar: {e}")
                
                # Mostrar resumen de lo que se clonó
                if opciones:
                    seleccionadas = sum(1 for v in opciones.values() if v)
                    QMessageBox.information(None, "Éxito", 
                        f"Contrato clonado: '{nuevo_nombre}'\n"
                        f"Se copiaron {seleccionadas} secciones seleccionadas.")
                else:
                    QMessageBox.information(None, "Éxito", f"Contrato clonado: '{nuevo_nombre}'")
                return True
            else:
                QMessageBox.critical(None, "Error", "Error creando el contrato clonado")
                return False
                
        except Exception as e:
            print(f"[ControladorJson] ❌ Error clonando contrato: {e}")
            QMessageBox.critical(None, "Error", f"Error clonando contrato: {e}")
            return False
    
    def _clonar_selectivo(self, contrato_origen, nuevo_nombre, opciones):
        """Realizar clonación selectiva según opciones especificadas"""
        # Crear estructura básica del contrato
        datos_clonados = {
            "nombreObra": nuevo_nombre,
            "tipoActuacion": contrato_origen.get("tipoActuacion", ""),
            "fechaCreacion": contrato_origen.get("fechaCreacion", ""),
            "version": contrato_origen.get("version", "1.0")
        }
        
        # Clonar secciones según opciones seleccionadas
        
        # 📋 DATOS DEL CONTRATO (sin número de expediente)
        if opciones.get("objeto_contrato", False):
            datos_clonados["objetoContrato"] = contrato_origen.get("objetoContrato", "")
            datos_clonados["objeto"] = contrato_origen.get("objeto", "")  # Campo alternativo
        
        if opciones.get("tipo_contrato", False):
            datos_clonados["tipoContrato"] = contrato_origen.get("tipoContrato", "")
            datos_clonados["tipoActuacion"] = contrato_origen.get("tipoActuacion", "")  # Campo alternativo
        
        if opciones.get("organo_contratacion", False):
            datos_clonados["organoContratacion"] = contrato_origen.get("organoContratacion", "")
            datos_clonados["organoContratacion2"] = contrato_origen.get("organoContratacion2", "")  # Campo alternativo
        
        if opciones.get("importes", False):
            # Campos estándar
            datos_clonados["importeLicitacion"] = contrato_origen.get("importeLicitacion", 0.0)
            datos_clonados["importeIVA"] = contrato_origen.get("importeIVA", 0.0)
            datos_clonados["importeTotal"] = contrato_origen.get("importeTotal", 0.0)
            # Campos alternativos de la estructura real
            datos_clonados["basePresupuesto"] = contrato_origen.get("basePresupuesto", "")
            datos_clonados["ivaPresupuestoBase"] = contrato_origen.get("ivaPresupuestoBase", "")
            datos_clonados["totalPresupuestoBase"] = contrato_origen.get("totalPresupuestoBase", "")
        
        if opciones.get("plazos", False):
            datos_clonados["duracion"] = contrato_origen.get("duracion", "")
            datos_clonados["plazoEjecucion"] = contrato_origen.get("plazoEjecucion", "")
        
        # 🏢 EMPRESAS
        if opciones.get("empresas_datos", False) or opciones.get("empresas_invitadas", False):
            empresas_origen = contrato_origen.get("empresas", [])
            if empresas_origen:
                datos_clonados["empresas"] = []
                for empresa in empresas_origen:
                    empresa_clonada = {}
                    
                    if opciones.get("empresas_datos", False):
                        # Copiar datos básicos de empresa
                        empresa_clonada.update({
                            "nombre": empresa.get("nombre", ""),
                            "nif": empresa.get("nif", ""),
                            "email": empresa.get("email", ""),
                            "contacto": empresa.get("contacto", "")
                        })
                    
                    if opciones.get("empresas_invitadas", False):
                        # Mantener estado de invitación
                        empresa_clonada["invitada"] = empresa.get("invitada", False)
                    
                    datos_clonados["empresas"].append(empresa_clonada)
        
        # 💰 OFERTAS
        if any([opciones.get("ofertas_importes", False), 
                opciones.get("ofertas_clasificacion", False), 
                opciones.get("empresa_adjudicataria", False)]):
            
            ofertas_origen = contrato_origen.get("ofertas", [])
            if ofertas_origen:
                datos_clonados["ofertas"] = []
                for oferta in ofertas_origen:
                    oferta_clonada = {
                        "empresa": oferta.get("empresa", "")
                    }
                    
                    if opciones.get("ofertas_importes", False):
                        oferta_clonada["importe"] = oferta.get("importe", 0.0)
                    
                    if opciones.get("ofertas_clasificacion", False):
                        oferta_clonada["orden_clasificatorio"] = oferta.get("orden_clasificatorio", 0)
                        oferta_clonada["presenta_oferta"] = oferta.get("presenta_oferta", True)
                    
                    datos_clonados["ofertas"].append(oferta_clonada)
            
            if opciones.get("empresa_adjudicataria", False):
                datos_clonados["empresaAdjudicataria"] = contrato_origen.get("empresaAdjudicataria", "")
        
        # 📋 DOCUMENTOS ESPECÍFICOS (solo datos mínimos, resto en blanco)
        if opciones.get("acta_inicio_datos", False):
            # Solo campos básicos para acta inicio (SIN nombreObra)
            campos_acta_inicio = [
                "objeto", "objetoContrato", "organoContratacion", 
                "organoContratacion2", "basePresupuesto", "ivaPresupuestoBase", 
                "totalPresupuestoBase", "plazoEjecucion"
            ]
            for campo in campos_acta_inicio:
                if campo in contrato_origen:
                    datos_clonados[campo] = contrato_origen[campo]
            # Resto de campos específicos de acta inicio se dejan en blanco
            
        if opciones.get("contrato_datos", False):
            # Solo campos básicos para contrato (SIN nombreObra)
            campos_contrato = [
                "objeto", "objetoContrato", "tipoContrato",
                "organoContratacion", "basePresupuesto", "ivaPresupuestoBase",
                "totalPresupuestoBase", "plazoEjecucion", "regimenPagos"
            ]
            for campo in campos_contrato:
                if campo in contrato_origen:
                    datos_clonados[campo] = contrato_origen[campo]
            # Resto de campos se dejan en blanco
            
        if opciones.get("cartas_invitacion_datos", False):
            # Solo campos básicos para cartas invitación (SIN nombreObra)
            campos_cartas = [
                "objeto", "objetoContrato", "organoContratacion",
                "OrganoSolicitaOfertas", "basePresupuesto", "plazoEjecucion"
            ]
            for campo in campos_cartas:
                if campo in contrato_origen:
                    datos_clonados[campo] = contrato_origen[campo]
            # Empresas básicas para invitación
            if "empresas" in contrato_origen:
                datos_clonados["empresas"] = []
                for empresa in contrato_origen["empresas"]:
                    datos_clonados["empresas"].append({
                        "nombre": empresa.get("nombre", ""),
                        "nif": empresa.get("nif", ""),
                        "email": empresa.get("email", ""),
                        "contacto": empresa.get("contacto", "")
                    })
        
        # 📅 FECHAS
        if opciones.get("fechas_proceso", False):
            fechas_proceso = [
                "fechaInvitacion", "fechaPresentacionOfertas", "fechaAdjudicacion",
                "fechaEnvioContrato", "fechaDevolucionContrato"
            ]
            for fecha in fechas_proceso:
                if fecha in contrato_origen:
                    datos_clonados[fecha] = contrato_origen[fecha]
        
        if opciones.get("fechas_ejecucion", False):
            fechas_ejecucion = [
                "fechaInicio", "fechaReplanteo", "fechaRecepcion", "fechaFinalizacion"
            ]
            for fecha in fechas_ejecucion:
                if fecha in contrato_origen:
                    datos_clonados[fecha] = contrato_origen[fecha]
        
        # 💰 LIQUIDACIÓN
        if opciones.get("liquidacion_importes", False) or opciones.get("liquidacion_saldos", False):
            liquidacion = contrato_origen.get("liquidacion", {})
            if liquidacion:
                datos_clonados["liquidacion"] = {}
                
                if opciones.get("liquidacion_importes", False):
                    datos_clonados["liquidacion"].update({
                        "importeLicitado": liquidacion.get("importeLicitado", 0.0),
                        "importeFacturado": liquidacion.get("importeFacturado", 0.0),
                        "importePenalizaciones": liquidacion.get("importePenalizaciones", 0.0),
                        "diferencia": liquidacion.get("diferencia", 0.0),
                        "porcentajeEjecutado": liquidacion.get("porcentajeEjecutado", 0.0)
                    })
                
                if opciones.get("liquidacion_saldos", False):
                    datos_clonados["liquidacion"].update({
                        "saldoFavorADIF": liquidacion.get("saldoFavorADIF", 0.0),
                        "saldoFavorEmpresa": liquidacion.get("saldoFavorEmpresa", 0.0),
                        "empresaEjecutora": liquidacion.get("empresaEjecutora", "")
                    })
        
        # 📄 CONFIGURACIÓN Y FIRMANTES
        if opciones.get("firmantes", False):
            firmantes = contrato_origen.get("firmantes", {})
            if firmantes:
                datos_clonados["firmantes"] = firmantes.copy()
        
        if opciones.get("plantillas_config", False):
            config_plantillas = contrato_origen.get("configuracionPlantillas", {})
            if config_plantillas:
                datos_clonados["configuracionPlantillas"] = config_plantillas.copy()
        
        # IMPORTANTE: Asegurar que el nuevo nombre se preserve
        datos_clonados["nombreObra"] = nuevo_nombre
        
        return datos_clonados
    
    def _limpiar_campos_no_clonados(self, opciones):
        """Limpiar campos específicos que no se clonaron"""
        try:
            if not self.main_window:
                return
                
            print(f"[ControladorJson] 🧹 Limpiando campos no clonados...")
            
            # Campos que siempre deben limpiarse si no se seleccionaron específicamente
            campos_a_limpiar = {}
            
            # Si no se seleccionó objeto_contrato, limpiar campos relacionados
            if not opciones.get("objeto_contrato", False):
                campos_a_limpiar.update({
                    "textEdit_objeto": "",
                    "textEdit_objetoContrato": "",
                    "textEdit_justificacion": "",
                    "textEdit_insuficiencia": "",
                    "textEdit_justificacionLimites": "",
                    "textEdit_noAlteracion": ""
                })
            
            # Si no se seleccionó importes, limpiar campos de presupuesto
            if not opciones.get("importes", False):
                campos_a_limpiar.update({
                    "doubleSpinBox_basePresupuesto": 0.0,
                    "doubleSpinBox_ivaPresupuestoBase": 0.0,
                    "doubleSpinBox_totalPresupuestoBase": 0.0
                })
            
            # Si no se seleccionó plazos, limpiar
            if not opciones.get("plazos", False):
                campos_a_limpiar.update({
                    "lineEdit_plazoEjecucion": "",
                    "textEdit_regimenPagos": ""
                })
            
            # Si no se seleccionó organo_contratacion, limpiar
            if not opciones.get("organo_contratacion", False):
                campos_a_limpiar.update({
                    "lineEdit_organoContratacion": "",
                    "lineEdit_organoContratacion2": "",
                    "lineEdit_OrganoSolicitaOfertas": ""
                })
            
            # Aplicar limpieza
            for widget_name, valor_vacio in campos_a_limpiar.items():
                widget = getattr(self.main_window, widget_name, None)
                if widget:
                    try:
                        if hasattr(widget, 'setText'):
                            widget.setText(str(valor_vacio))
                        elif hasattr(widget, 'setPlainText'):
                            widget.setPlainText(str(valor_vacio))
                        elif hasattr(widget, 'setValue'):
                            widget.setValue(valor_vacio)
                        print(f"[ControladorJson] ✅ Limpiado: {widget_name}")
                    except Exception as e:
                        print(f"[ControladorJson] ⚠️ Error limpiando {widget_name}: {e}")
            
            print(f"[ControladorJson] 🧹 Limpieza completada: {len(campos_a_limpiar)} campos")
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error limpiando campos: {e}")
    
    def restaurar_backup(self, archivo_backup: str) -> bool:
        """Restaurar desde archivo de backup"""
        if not self.gestor or not os.path.exists(archivo_backup):
            return False
        
        try:
            import shutil
            
            # Crear backup del actual antes de restaurar
            self.hacer_backup("pre_restore")
            
            # Restaurar
            shutil.copy2(archivo_backup, self.gestor.ruta_archivo)
            
            # Recargar datos
            self.recargar_datos()
            
            return True
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error restaurando backup: {e}")
            return False

    def exportar_contrato(self, nombre_contrato: str, archivo_destino: str) -> bool:
        """Exportar un contrato específico a archivo JSON independiente"""
        try:
            contrato = self.leer_contrato_completo(nombre_contrato)
            if not contrato:
                return False
            
            datos_exportacion = {
                "contrato_exportado": contrato,
                "fecha_exportacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "origen": self.gestor.ruta_archivo if self.gestor else "Desconocido"
            }
            
            with open(archivo_destino, "w", encoding="utf-8") as f:
                json.dump(datos_exportacion, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error exportando contrato: {e}")
            return False

    def importar_contrato(self, archivo_origen: str) -> bool:
        """Importar contrato desde archivo JSON"""
        try:
            if not os.path.exists(archivo_origen):
                return False
            
            with open(archivo_origen, "r", encoding="utf-8") as f:
                datos_importacion = json.load(f)
            
            # Extraer datos del contrato
            contrato = datos_importacion.get("contrato_exportado")
            if not contrato:
                # Intentar como contrato directo
                contrato = datos_importacion
            
            nombre_contrato = contrato.get("nombreObra")
            if not nombre_contrato:
                print("[ControladorJson] ❌ Contrato sin nombreObra")
                return False
            
            # Verificar si ya existe
            if self.leer_contrato_completo(nombre_contrato):
                print(f"[ControladorJson] ❌ Ya existe contrato: {nombre_contrato}")
                return False
            
            # Crear contrato
            if self.crear_contrato_nuevo(contrato):
                return True
            else:
                return False
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error importando contrato: {e}")
            return False

    def limpiar_datos_vacios(self) -> int:
        """Limpiar campos vacíos de todos los contratos"""
        if not self.gestor:
            return 0
        
        try:
            obras = self.gestor.datos.get("obras", [])
            campos_limpiados = 0
            
            for obra in obras:
                campos_a_eliminar = []
                
                for campo, valor in obra.items():
                    # Identificar campos vacíos
                    if valor is None or valor == "" or valor == [] or valor == {}:
                        campos_a_eliminar.append(campo)
                
                # Eliminar campos vacíos (excepto campos importantes)
                campos_importantes = ["nombreObra", "numeroExpediente", "fechaCreacion"]
                
                for campo in campos_a_eliminar:
                    if campo not in campos_importantes:
                        del obra[campo]
                        campos_limpiados += 1
            
            if campos_limpiados > 0:
                self.gestor.guardar_datos()
                print(f"[ControladorJson] 🧹 Limpiados {campos_limpiados} campos vacíos")
            
            return campos_limpiados
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error limpiando datos: {e}")
            return 0

    def optimizar_json(self) -> bool:  
        """Optimizar estructura del JSON eliminando redundancias"""
        if not self.gestor:
            return False
        
        try:
            # Hacer backup antes de optimizar
            self.hacer_backup("pre_optimize")
            
            obras = self.gestor.datos.get("obras", [])
            optimizaciones = 0
            
            for obra in obras:
                # Normalizar fechas
                for campo in obra:
                    if "fecha" in campo.lower() and isinstance(obra[campo], str):
                        # Intentar normalizar formato de fecha
                        try:
                            fecha_obj = datetime.strptime(obra[campo], "%Y-%m-%d %H:%M:%S")
                            obra[campo] = fecha_obj.strftime("%Y-%m-%d")
                            optimizaciones += 1
                        except:
                            pass
                
                # Normalizar campos numéricos
                campos_numericos = ["basePresupuesto", "precioAdjudicacion", "certBase"]
                for campo in campos_numericos:
                    if campo in obra and isinstance(obra[campo], str):
                        try:
                            # Convertir strings numéricos a números
                            valor_float = float(obra[campo])
                            obra[campo] = str(valor_float)
                            optimizaciones += 1
                        except:
                            pass
            
            if optimizaciones > 0:
                resultado = self.gestor.guardar_datos()
                if resultado:
                    print(f"[ControladorJson] ⚡ JSON optimizado: {optimizaciones} campos")
                return resultado
            
            return True
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error optimizando JSON: {e}")
            return False

    def obtener_ruta_archivo(self) -> str:
        """Obtener ruta del archivo JSON actual"""
        if self.gestor:
            return self.gestor.ruta_archivo
        return ""

    def cambiar_archivo_json(self, nueva_ruta: str) -> bool:
        """Cambiar a un archivo JSON diferente"""
        try:
            nuevo_gestor = GestorContratosJSON(nueva_ruta)
            if nuevo_gestor:
                self.gestor = nuevo_gestor
                return True
            return False
            
        except Exception as e:
            print(f"[ControladorJson] ❌ Error cambiando archivo JSON: {e}")
            return False

    # Método debug eliminado - innecesario en producción

    # =================== MÉTODOS DE COMPATIBILIDAD ===================
    
    def cargar_json_simple(self, archivo_path: str) -> Dict[str, Any]:
        """Cargar cualquier archivo JSON (método de compatibilidad)"""
        try:
            with open(archivo_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ControladorJson] ❌ Error cargando JSON simple: {e}")
            return {}

    def guardar_json_simple(self, datos: Dict[str, Any], archivo_path: str) -> bool:
        """Guardar cualquier diccionario como JSON (método de compatibilidad)"""
        try:
            with open(archivo_path, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[ControladorJson] ❌ Error guardando JSON simple: {e}")
            return False

    def borrar_contrato_con_carpetas(self, nombre_contrato: Optional[str]) -> tuple[bool, str]:
        """Eliminar contrato y sus carpetas asociadas"""
        try:
            if not self.gestor or not nombre_contrato:
                return False, "Gestor o nombre no disponible"
            
            # Primero eliminar las carpetas del contrato si existen
            try:
                import os
                import shutil
                carpeta_obras = os.path.join(os.getcwd(), "obras", nombre_contrato)
                
                if os.path.exists(carpeta_obras):
                    shutil.rmtree(carpeta_obras)
                    print(f"[ControladorJson] 🗂️ Carpeta eliminada: {carpeta_obras}")
                else:
                    print(f"[ControladorJson] ℹ️ No existe carpeta para: {nombre_contrato}")
                    
            except Exception as e:
                print(f"[ControladorJson] ⚠️ Error eliminando carpeta: {e}")
                # Continuar con la eliminación del JSON aunque falle la carpeta
            
            # Eliminar del JSON
            resultado = self.gestor.eliminar_contrato(nombre_contrato)
            
            if not resultado:
                return False, "Error eliminando del JSON"
            
            # RECARGAR AUTOMÁTICAMENTE DESPUÉS DE ELIMINAR
            if self.main_window:
                try:
                    # Recargar ContractManager
                    if hasattr(self.main_window, 'contract_manager') and self.main_window.contract_manager:
                        self.main_window.contract_manager.reload_contracts()
                        self.main_window.contract_manager.update_combo_box()
                        
                        # Seleccionar el primer contrato disponible o mensaje por defecto
                        if hasattr(self.main_window, 'comboBox'):
                            if self.main_window.comboBox.count() > 1:  # Hay contratos además del "Seleccionar..."
                                self.main_window.comboBox.setCurrentIndex(1)  # Primer contrato real
                            else:
                                self.main_window.comboBox.setCurrentIndex(0)  # "Seleccionar contrato..."
                    else:
                        print(f"[ControladorJson] ⚠️ ContractManager no disponible para recargar")
                
                except Exception as e:
                    print(f"[ControladorJson] ⚠️ Error recargando después de eliminar: {e}")
                    # No falla la eliminación por esto
            else:
                print(f"[ControladorJson] ⚠️ main_window no disponible para recargar")
            
            return True, f"Contrato '{nombre_contrato}' eliminado correctamente"
        
        except Exception as e:
            mensaje_error = f"Error eliminando contrato: {e}"
            print(f"[ControladorJson] ❌ {mensaje_error}")
            import traceback
            traceback.print_exc()
            return False, mensaje_error