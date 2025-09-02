#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador JSON Unificado y Optimizado
Combina GestorContratosJSON + ControladorJson en una sola clase eficiente
"""
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

# IMPORTAR EL CONTROLADOR DE RUTAS CENTRALIZADO
try:
    from .controlador_routes import rutas
except (ImportError, ValueError):
    from controlador_routes import rutas

class GestorJsonUnificado:
    """Controlador JSON unificado y optimizado para operaciones de contratos"""
    
    def __init__(self, ruta_archivo: str = None, main_window=None):
        self.main_window = main_window
        # USAR CONTROLADOR DE RUTAS CENTRALIZADO - UNA SOLA FUENTE DE VERDAD
        self.ruta_archivo = ruta_archivo or rutas.get_ruta_base_datos()
        self.datos = self._cargar_datos_iniciales()
        print(f"[GestorJsonUnificado] Inicializado con archivo: {self.ruta_archivo}")

    def _buscar_archivo_base_datos(self) -> str:
        """DEPRECATED: Usar rutas.get_ruta_base_datos() en su lugar"""
        # ⚠️ ESTA FUNCIÓN ES OBSOLETA - USAR ControladorRutas
        return rutas.get_ruta_base_datos()

    def _cargar_datos_iniciales(self) -> Dict[str, Any]:
        """Cargar datos con verificación mejorada de archivos"""
        try:
            if os.path.exists(self.ruta_archivo) and os.path.getsize(self.ruta_archivo) > 0:
                with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                    pass
                    return datos
            else:
                return self._crear_estructura_inicial()
        except (json.JSONDecodeError, Exception) as e:
            print(f"[GestorJsonUnificado] Error cargando JSON: {e}")
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
        
        # Crear directorio y archivo
        directorio = os.path.dirname(self.ruta_archivo)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(estructura_inicial, archivo, ensure_ascii=False, indent=2)
            print(f"[GestorJsonUnificado] BaseDatos.json creado: {self.ruta_archivo}")
        except Exception as e:
            print(f"[GestorJsonUnificado] Error creando archivo inicial: {e}")
        
        return estructura_inicial

    # =================== OPERACIONES BÁSICAS ===================
    
    def guardar_datos(self) -> bool:
        """Guardar datos actuales en el archivo JSON"""
        try:

            

            
            directorio = os.path.dirname(self.ruta_archivo)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(self.datos, archivo, ensure_ascii=False, indent=2)
            
            pass
            return True
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR guardando datos: {e}")
            return False

    def recargar_datos(self) -> bool:
        """Recargar datos desde el archivo"""
        try:

            
            self.datos = self._cargar_datos_iniciales()
            

            
            return True
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR recargando datos: {e}")
            return False

    # =================== OPERACIONES DE BÚSQUEDA ===================
    
    def buscar_contrato_por_nombre(self, nombre_contrato: str) -> Optional[Dict[str, Any]]:
        """Buscar contrato por nombre exacto o parcial - Compatible con ambos formatos"""
        if not nombre_contrato:
            return None
            
        obras = self.datos.get("obras", [])
        
        # Búsqueda exacta - compatibilidad con ambos campos
        for obra in obras:
            nombre_obra = obra.get("nombreObra") or obra.get("nombre", "")
            if nombre_obra == nombre_contrato:
                return obra
        
        # Búsqueda parcial para nombres truncados
        if nombre_contrato.endswith("..."):
            nombre_parcial = nombre_contrato[:-3]
            for obra in obras:
                if obra.get("nombreObra", "").startswith(nombre_parcial):
                    return obra
        
        # Búsqueda por similitud MÁS ESTRICTA
        # Solo buscar por similitud si los nombres son muy parecidos (>80% match)
        for obra in obras:
            nombre_obra = obra.get("nombreObra") or obra.get("nombre", "")
            if nombre_obra and len(nombre_contrato) > 10:
                # Calcular similitud más precisa
                if len(nombre_contrato) == len(nombre_obra):
                    # Misma longitud - verificar diferencia mínima
                    diferencias = sum(c1 != c2 for c1, c2 in zip(nombre_contrato, nombre_obra))
                    if diferencias <= 2:  # Máximo 2 caracteres diferentes
                        return obra
                elif abs(len(nombre_contrato) - len(nombre_obra)) <= 3:
                    # Diferencia de longitud mínima - usar substring más estricto
                    if len(nombre_contrato) > len(nombre_obra):
                        # nombre_contrato es más largo
                        if nombre_obra in nombre_contrato and len(nombre_obra) > 15:
                            return obra
                    else:
                        # nombre_obra es más largo
                        if nombre_contrato in nombre_obra and len(nombre_contrato) > 15:
                            return obra
        
        return None

    def buscar_contrato_por_expediente(self, numero_expediente: str) -> Optional[Dict[str, Any]]:
        """Buscar contrato por número de expediente"""
        if not numero_expediente:
            return None
            
        obras = self.datos.get("obras", [])
        for obra in obras:
            if obra.get("numeroExpediente") == numero_expediente:
                return obra
        return None

    def buscar_contrato_inteligente(self, identificador: str) -> Optional[Dict[str, Any]]:
        """Búsqueda inteligente: primero por nombre, después por expediente"""
        if not identificador:
            return None
        
        identificador = identificador.strip()
        
        # Buscar por nombre primero
        resultado = self.buscar_contrato_por_nombre(identificador)
        if resultado:
            return resultado
        
        # Si parece un expediente, buscar por expediente
        patron_expediente = re.compile(r'^\d{1,5}[\/\.\-\d]+$')
        if patron_expediente.match(identificador):
            return self.buscar_contrato_por_expediente(identificador)
        
        return None

    # =================== OPERACIONES DE LISTADO ===================
    
    def listar_contratos(self) -> List[Dict[str, str]]:
        """Listar todos los contratos con información básica"""
        obras = self.datos.get("obras", [])
        return [
            {
                "nombreObra": obra.get("nombreObra", ""),
                "numeroExpediente": obra.get("numeroExpediente", ""),
                "tipoContrato": obra.get("tipoContrato", "")
            }
            for obra in obras if obra.get("nombreObra")
        ]

    def obtener_nombres_obras(self) -> List[str]:
        """Obtener solo los nombres de todas las obras - Compatible con ambos formatos"""
        nombres = []
        for obra in self.datos.get("obras", []):
            # Buscar en ambos campos para compatibilidad
            nombre = obra.get("nombreObra") or obra.get("nombre", "")
            if nombre and nombre.strip():
                nombres.append(nombre.strip())
        
        return nombres
    
    def obtener_todos_nombres_obras(self) -> List[str]:
        """Alias de compatibilidad para obtener_nombres_obras"""
        return self.obtener_nombres_obras()
    
    def cargar_datos_obra(self, identificador: str) -> Dict[str, Any]:
        """Método de compatibilidad - cargar datos de obra"""
        resultado = self.buscar_contrato_inteligente(identificador)
        return resultado if resultado else {}
    
    def guardar_campo_en_json(self, nombre_contrato: str, nombre_campo: str, valor: str) -> bool:
        """Guardar un campo específico en el JSON"""
        if not nombre_contrato or not nombre_campo:
            return False
        
        try:
            # Buscar contrato actual
            contrato_actual = self.buscar_contrato_inteligente(nombre_contrato)
            if not contrato_actual:
                print(f"[GestorJsonUnificado] ERROR: No se encontró contrato: {nombre_contrato}")
                return False
            
            # Actualizar campo
            datos_actualizados = {nombre_campo: valor}
            return self.actualizar_contrato(nombre_contrato, datos_actualizados)
            
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR guardando campo: {e}")
            return False
    
    def guardar_empresas_unificadas_en_json(self, nombre_contrato: str, empresas_data: List[Dict[str, str]]) -> bool:
        """Guardar empresas en estructura unificada"""
        if not nombre_contrato:
            return False
        
        try:
            # Estructura unificada simple
            datos_empresas = {
                "empresas": empresas_data  # Array directo, no nested
            }
            
            return self.actualizar_contrato(nombre_contrato, datos_empresas)
            
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR guardando empresas unificadas: {e}")
            return False
    
    def guardar_empresas_en_json(self, nombre_contrato: str, empresas_data: List[Dict[str, str]]) -> bool:
        """Método de compatibilidad - redirigir a método unificado"""
        return self.guardar_empresas_unificadas_en_json(nombre_contrato, empresas_data)
    
    def actualizar_contrato(self, nombre_contrato: str, datos_actualizados: Dict[str, Any], guardar_inmediato: bool = True) -> bool:
        """Actualizar contrato existente - OPTIMIZADO con guardado opcional"""
        try:
            if not nombre_contrato:
                return False
            
            obras = self.datos.get("obras", [])
            
            # Buscar y actualizar el contrato directamente
            for obra in obras:
                if obra.get("nombreObra") == nombre_contrato:
                    obra.update(datos_actualizados)
                    obra["fechaModificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Guardar solo si se solicita
                    if guardar_inmediato:
                        return self.guardar_datos()
                    else:
                        return True
            
            return False
            
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR actualizando contrato: {e}")
            return False

    # =================== OPERACIONES DE LECTURA ===================
    
    def leer_contrato_completo(self, nombre_contrato: str) -> Optional[Dict[str, Any]]:
        """Leer datos completos de un contrato"""
        return self.buscar_contrato_inteligente(nombre_contrato)

    def leer_campo_contrato(self, nombre_contrato: str, nombre_campo: str) -> Any:
        """Leer un campo específico de un contrato"""
        try:
            contrato = self.leer_contrato_completo(nombre_contrato)
            return contrato.get(nombre_campo) if contrato else None
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR leyendo campo '{nombre_campo}': {e}")
            return None

    # =================== OPERACIONES DE ESCRITURA ===================
    
    def guardar_contrato(self, datos_contrato: Dict[str, Any]) -> bool:
        """Guardar o actualizar un contrato"""
        try:
            if not datos_contrato.get("nombreObra"):
                print("[GestorJsonUnificado] ERROR: nombreObra es obligatorio")
                return False

            obras = self.datos.get("obras", [])
            nombre_obra = datos_contrato["nombreObra"]
            
            # Buscar si existe para actualizar
            for i, obra in enumerate(obras):
                if obra.get("nombreObra") == nombre_obra:
                    obras[i] = datos_contrato
                    print(f"[GestorJsonUnificado] OK: Contrato actualizado: {nombre_obra}")
                    return self.guardar_datos()
            
            # Si no existe, agregar nuevo
            obras.append(datos_contrato)
            print(f"[GestorJsonUnificado] OK: Nuevo contrato agregado: {nombre_obra}")
            return self.guardar_datos()
            
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR guardando contrato: {e}")
            return False

    def eliminar_contrato(self, nombre_contrato: str) -> bool:
        """Eliminar un contrato"""
        try:
            obras = self.datos.get("obras", [])
            obras_filtradas = [obra for obra in obras 
                             if obra.get("nombreObra") != nombre_contrato]
            
            if len(obras_filtradas) < len(obras):
                self.datos["obras"] = obras_filtradas
                print(f"[GestorJsonUnificado] OK: Contrato eliminado: {nombre_contrato}")
                return self.guardar_datos()
            else:
                print(f"[GestorJsonUnificado] ERROR: Contrato no encontrado para eliminar: {nombre_contrato}")
                return False
                
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR eliminando contrato: {e}")
            return False

    # =================== OPERACIONES DE FIRMANTES ===================
    
    def obtener_firmantes(self) -> Dict[str, str]:
        """Obtener datos de firmantes"""
        return self.datos.get("firmantes", {})

    def actualizar_firmantes(self, firmantes: Dict[str, str]) -> bool:
        """Actualizar datos de firmantes"""
        try:
            self.datos["firmantes"] = firmantes
            return self.guardar_datos()
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR actualizando firmantes: {e}")
            return False

    # =================== UTILIDADES ===================
    
    def esta_disponible(self) -> bool:
        """Verificar si el controlador está disponible"""
        return self.datos is not None

    def obtener_estadisticas(self) -> Dict[str, int]:
        """Obtener estadísticas básicas"""
        obras = self.datos.get("obras", [])
        estadisticas = {
            "total_obras": len(obras),
            "obras_servicio": len([o for o in obras if o.get("tipoContrato") == "servicio"]),
            "obras_construccion": len([o for o in obras if o.get("tipoContrato") == "obra"])
        }
        return estadisticas


    # =================== MÉTODOS DE CREACIÓN DE CONTRATOS ===================
    
    def crear_contrato_nuevo(self, datos_contrato: dict) -> bool:
        """Crear nuevo contrato - método requerido por controlador_grafica"""
        try:
            print(f"[GestorJsonUnificado] Creando nuevo contrato: {datos_contrato.get('nombreObra', 'sin_nombre')}")
            
            # Validar datos mínimos
            nombre_obra = datos_contrato.get("nombreObra", "").strip()
            if not nombre_obra:
                print("[GestorJsonUnificado] ERROR: Nombre de obra requerido")
                return False
            
            # Verificar que no existe ya
            contrato_existente = self.buscar_contrato_inteligente(nombre_obra)
            if contrato_existente:
                print(f"[GestorJsonUnificado] ERROR: Ya existe contrato con nombre: {nombre_obra}")
                print(f"[GestorJsonUnificado] DEBUG: Contrato encontrado: {contrato_existente.get('nombreObra')} / {contrato_existente.get('nombre')}")
                return False
            else:
                print(f"[GestorJsonUnificado] OK: Nombre '{nombre_obra}' disponible para crear")
            
            # Crear estructura del contrato SIGUIENDO EL FORMATO ORIGINAL
            nuevo_contrato = {
                "nombreObra": nombre_obra,
                "fechaCreacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipoActuacion": datos_contrato.get("tipoActuacion", "Servicios"),  # Estructura original
                "plazoEjecucion": str(datos_contrato.get("plazoEjecucion", "30")),  # String como en original
                "basePresupuesto": str(datos_contrato.get("basePresupuesto", "0")),  # String como en original
                
                # Campos adicionales del formato original
                "organoContratacion": datos_contrato.get("organoContratacion", ""),
                "organoContratacion2": datos_contrato.get("organoContratacion2", ""),
                "OrganoSolicitaOfertas": datos_contrato.get("OrganoSolicitaOfertas", ""),
                "ivaPresupuestoBase": str(float(datos_contrato.get("basePresupuesto", 0)) * 0.21),
                "totalPresupuestoBase": str(float(datos_contrato.get("basePresupuesto", 0)) * 1.21),
                "justificacionLimites": f"El contrato de la obra es por importe de {datos_contrato.get('basePresupuesto', 0)} euros.",
                
                # Campos de responsables (vacíos inicialmente)
                "cargoConforme": "--------------------------",
                "cargoAprueba": "--------------------------",
                "cargoResponsable1": "--------------------------",
                
                # Listas para actuaciones y facturas
                "actuaciones": [],
                "facturas": [],
                
                # Empresas vacías
                "empresas": [],
                
                # Liquidación vacía
                "liquidacion": {}
            }
            
            # Agregar a la lista de obras
            if "obras" not in self.datos:
                self.datos["obras"] = []
            
            self.datos["obras"].append(nuevo_contrato)
            
            # Guardar los cambios
            if self.guardar_datos():
                print(f"[GestorJsonUnificado] OK: Contrato creado exitosamente: {nombre_obra}")
                return True
            else:
                # Revertir si falla el guardado
                self.datos["obras"].remove(nuevo_contrato)
                print(f"[GestorJsonUnificado] ERROR: Error guardando contrato nuevo")
                return False
                
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR en crear_contrato_nuevo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def crear_contrato_con_carpetas(self, datos_contrato: dict) -> tuple:
        """Crear contrato con carpetas - método avanzado"""
        try:
            print(f"[GestorJsonUnificado] Creando contrato con carpetas...")
            
            # Primero crear el contrato básico
            exito_contrato = self.crear_contrato_nuevo(datos_contrato)
            
            if not exito_contrato:
                return False, "Error creando contrato básico"
            
            # Intentar crear carpetas (opcional - si falla, el contrato ya está creado)
            nombre_obra = datos_contrato.get("nombreObra", "").strip()
            mensaje_carpetas = ""
            
            try:
                from .controlador_routes import rutas
                carpeta_obras = rutas.get_ruta_carpeta_obras()
                
                # Crear carpeta del proyecto
                import os, re
                nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre_obra)
                nombre_limpio = re.sub(r'\s+', '_', nombre_limpio)[:50]
                
                ruta_proyecto = os.path.join(carpeta_obras, nombre_limpio)
                os.makedirs(ruta_proyecto, exist_ok=True)
                
                # Crear subcarpetas estándar - ESTRUCTURA COMPLETA
                subcarpetas = [
                    "01-proyecto",
                    "02-documentacion-finales",
                    "03-cartas-finales",
                    "04-documentos-sin-firmar",
                    "05-cartas-sin-firmar",
                    "06-ofertas",
                    "07-seguridad-y-salud",
                    "08-actuaciones",
                    "09-facturas",
                    "10-otros",
                    "11-fotos",
                    "12-comunicaciones"
                ]
                
                for subcarpeta in subcarpetas:
                    os.makedirs(os.path.join(ruta_proyecto, subcarpeta), exist_ok=True)
                
                mensaje_carpetas = f"Carpetas creadas en: {ruta_proyecto}"
                print(f"[GestorJsonUnificado] {mensaje_carpetas}")
                
            except Exception as e:
                mensaje_carpetas = f"Advertencia: Error creando carpetas - {e}"
                print(f"[GestorJsonUnificado] WARNING: {mensaje_carpetas}")
            
            return True, f"Contrato '{nombre_obra}' creado exitosamente. {mensaje_carpetas}"
            
        except Exception as e:
            print(f"[GestorJsonUnificado] ERROR en crear_contrato_con_carpetas: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error creando contrato: {e}"
    
    def clonar_contrato(self, nombre_origen, nuevo_nombre, opciones=None):
        """Clonar un contrato existente con nuevo nombre y opciones selectivas"""
        from PyQt5.QtWidgets import QMessageBox
        
        print(f"[GestorJsonUnificado] 🔧 DEBUG CLONAR - Origen: '{nombre_origen}', Nuevo: '{nuevo_nombre}'")
        
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
                
            print(f"[GestorJsonUnificado] 🔧 DEBUG DATOS CLONADOS - nombreObra: '{datos_clonados.get('nombreObra', 'NO_ENCONTRADO')}'")
            
            # Crear nuevo contrato usando el método unificado
            resultado_tupla = self.crear_contrato_con_carpetas(datos_clonados)
            resultado = resultado_tupla[0] if isinstance(resultado_tupla, tuple) else resultado_tupla
            
            if resultado:
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
            print(f"[GestorJsonUnificado] ❌ Error clonando contrato: {e}")
            QMessageBox.critical(None, "Error", f"Error clonando contrato: {e}")
            return False
    
    def _clonar_selectivo(self, contrato_origen, nuevo_nombre, opciones):
        """Realizar clonación selectiva según opciones especificadas con los nuevos nombres de campos"""
        print(f"[GestorJsonUnificado] 🔧 DEBUG _clonar_selectivo - nuevo_nombre: '{nuevo_nombre}'")
        print(f"[GestorJsonUnificado] 🔧 DEBUG opciones seleccionadas: {len([k for k,v in opciones.items() if v])}")
        
        # Crear estructura básica del contrato
        datos_clonados = {
            "nombreObra": nuevo_nombre,
            "tipoActuacion": contrato_origen.get("tipoActuacion", ""),
            "fechaCreacion": contrato_origen.get("fechaCreacion", ""),
            "version": contrato_origen.get("version", "1.0")
        }
        
        campos_copiados = 0
        
        # Clonar campos según la nueva estructura basada en GroupBox_Campo
        for campo_key, valor in opciones.items():
            if valor and not campo_key.startswith('groupbox_'):  # Ignorar checkboxes de grupo
                print(f"[GestorJsonUnificado] 🔧 Procesando campo: {campo_key}")
                
                # Extraer el nombre del campo real
                if campo_key.startswith(('groupBox_2_', 'groupBox_3_', 'groupBox_', 
                                       'groupBox_9_', 'groupBox_10_', 'groupBox_11_',
                                       'groupBox_5_', 'groupBox_6_')):
                    # Extraer el nombre del campo real eliminando el prefijo del GroupBox
                    partes = campo_key.split('_')
                    if len(partes) >= 3:
                        campo_real = '_'.join(partes[2:])  # Tomar todo después de groupBox_X_
                    else:
                        campo_real = campo_key
                        
                    print(f"[GestorJsonUnificado] 🔧 Campo extraído: '{campo_real}'")
                    
                    # Copiar el campo si existe en el contrato origen, EXCEPTO nombreObra
                    if campo_real == 'nombreObra':
                        print(f"[GestorJsonUnificado] ⚠️ Saltando campo 'nombreObra' para preservar nuevo nombre")
                    elif campo_real in contrato_origen:
                        datos_clonados[campo_real] = contrato_origen[campo_real]
                        campos_copiados += 1
                        print(f"[GestorJsonUnificado] ✅ Campo copiado: '{campo_real}' = '{contrato_origen[campo_real]}'")
                    else:
                        print(f"[GestorJsonUnificado] ⚠️ Campo '{campo_real}' no encontrado en contrato origen")
        
        print(f"[GestorJsonUnificado] 🔧 Total campos copiados: {campos_copiados}")
        return datos_clonados


# =================== COMPATIBILIDAD CON CÓDIGO EXISTENTE ===================

# Alias para mantener compatibilidad
GestorContratosJSON = GestorJsonUnificado
ControladorJson = GestorJsonUnificado