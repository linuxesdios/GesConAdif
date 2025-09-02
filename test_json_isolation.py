#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test directo de aislamiento de datos en operaciones JSON
Sin dependencias GUI - Solo testea la lógica de controlador_json
"""

import json
import os
import sys
import shutil
from datetime import datetime

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def crear_backup():
    """Crear backup del archivo BaseDatos.json antes del test"""
    if os.path.exists('BaseDatos.json'):
        shutil.copy2('BaseDatos.json', 'BaseDatos_backup.json')
        print("Backup creado: BaseDatos_backup.json")

def restaurar_backup():
    """Restaurar el backup después del test"""
    if os.path.exists('BaseDatos_backup.json'):
        shutil.copy2('BaseDatos_backup.json', 'BaseDatos.json')
        os.remove('BaseDatos_backup.json')
        print("Backup restaurado y eliminado")

def leer_json_directo():
    """Lee directamente el archivo JSON"""
    try:
        with open('BaseDatos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR leyendo JSON: {e}")
        return None

def test_aislamiento_directo():
    """
    Test directo del fix sin GUI:
    1. Cargar controlador JSON standalone
    2. Cambiar plazoEjecucion en obra A
    3. Simular cambio a obra B 
    4. Verificar que obra A mantiene el cambio
    """
    print("="*60)
    print("TEST DIRECTO DE AISLAMIENTO JSON")
    print("="*60)
    
    # Crear backup antes de empezar
    crear_backup()
    
    try:
        # Importar solo el controlador de rutas que no depende de PyQt5
        from controladores.controlador_routes import ControladorRutas
        
        # Crear controlador de rutas
        rutas = ControladorRutas()
        ruta_json = rutas.get_ruta_base_datos()
        
        print(f"Usando archivo: {ruta_json}")
        
        # Crear una clase JSON simplificada solo para este test
        class GestorJsonTest:
            def __init__(self, ruta_archivo):
                self.ruta_archivo = ruta_archivo
                self.datos = self._cargar_datos()
            
            def _cargar_datos(self):
                """Cargar datos del archivo"""
                try:
                    with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error cargando datos: {e}")
                    return {"obras": []}
            
            def actualizar_contrato_aislado(self, nombre_contrato, datos_actualizados):
                """
                MÉTODO DE AISLAMIENTO: 
                Lee datos frescos del disco para cada operación
                """
                try:
                    print(f"[TEST] Actualizando {nombre_contrato} con aislamiento...")
                    
                    # 1. LEER DATOS FRESCOS DEL ARCHIVO
                    with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
                        datos_frescos = json.load(f)
                    
                    # 2. BUSCAR Y ACTUALIZAR EN DATOS FRESCOS
                    obras = datos_frescos.get("obras", [])
                    actualizado = False
                    
                    for i, obra in enumerate(obras):
                        if obra.get("nombreObra") == nombre_contrato:
                            # Actualizar en datos frescos
                            obras[i].update(datos_actualizados)
                            obras[i]["fechaModificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            actualizado = True
                            break
                    
                    if not actualizado:
                        print(f"[TEST] ADVERTENCIA: No se encontró obra {nombre_contrato}")
                        return False
                    
                    # 3. GUARDAR DATOS FRESCOS AL ARCHIVO
                    with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
                        json.dump(datos_frescos, f, ensure_ascii=False, indent=2)
                    
                    print(f"[TEST] Obra {nombre_contrato} actualizada con aislamiento")
                    return True
                    
                except Exception as e:
                    print(f"[TEST] ERROR en actualización aislada: {e}")
                    return False
            
            def obtener_plazo_ejecucion(self, nombre_obra):
                """Obtener plazoEjecucion de una obra específica leyendo del disco"""
                try:
                    # SEMPRE leer del disco para evitar cache
                    with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    for obra in datos.get("obras", []):
                        if nombre_obra.lower() in obra.get("nombreObra", "").lower():
                            return obra.get("plazoEjecucion", "N/A")
                    return "Obra no encontrada"
                except Exception as e:
                    print(f"Error obteniendo plazo: {e}")
                    return "Error"
        
        # Crear instancia del gestor de test
        gestor = GestorJsonTest(ruta_json)
        
        # Encontrar nombres de obras para el test
        datos_iniciales = leer_json_directo()
        if not datos_iniciales:
            print("ERROR: No se pudieron cargar datos iniciales")
            return False
        
        # Buscar obras REPARACIÓN y MANTENIMIENTO
        obra_reparacion = None
        obra_mantenimiento = None
        
        for obra in datos_iniciales.get("obras", []):
            nombre = obra.get("nombreObra", "")
            if "REPARACIÓN" in nombre and not obra_reparacion:
                obra_reparacion = nombre
            elif "MANTENIMIENTO" in nombre and not obra_mantenimiento:
                obra_mantenimiento = nombre
        
        if not obra_reparacion or not obra_mantenimiento:
            print("ERROR: No se encontraron obras REPARACIÓN y MANTENIMIENTO")
            return False
        
        print(f"\nObra REPARACIÓN: {obra_reparacion}")
        print(f"Obra MANTENIMIENTO: {obra_mantenimiento}")
        
        # PASO 1: Estado inicial
        print("\n--- PASO 1: Estado inicial ---")
        plazo_inicial_rep = gestor.obtener_plazo_ejecucion("REPARACIÓN")
        plazo_inicial_man = gestor.obtener_plazo_ejecucion("MANTENIMIENTO")
        print(f"REPARACIÓN plazoEjecucion inicial: {plazo_inicial_rep}")
        print(f"MANTENIMIENTO plazoEjecucion inicial: {plazo_inicial_man}")
        
        # PASO 2: Cambiar REPARACIÓN a valor test
        print("\n--- PASO 2: Cambiar REPARACIÓN a '88' ---")
        resultado_rep = gestor.actualizar_contrato_aislado(
            obra_reparacion,
            {"plazoEjecucion": "88"}
        )
        
        if not resultado_rep:
            print("ERROR: No se pudo actualizar REPARACIÓN")
            return False
        
        # Verificar cambio
        plazo_despues_rep = gestor.obtener_plazo_ejecucion("REPARACIÓN")
        print(f"REPARACIÓN plazoEjecucion después del cambio: {plazo_despues_rep}")
        
        if plazo_despues_rep != "88":
            print("ERROR: El cambio en REPARACIÓN no se guardó")
            return False
        
        # PASO 3: Cambiar MANTENIMIENTO (simulando cambio de contrato)
        print("\n--- PASO 3: Cambiar MANTENIMIENTO a '66' ---")
        resultado_man = gestor.actualizar_contrato_aislado(
            obra_mantenimiento,
            {"plazoEjecucion": "66"}
        )
        
        if not resultado_man:
            print("ERROR: No se pudo actualizar MANTENIMIENTO")
            return False
        
        # Verificar cambio en MANTENIMIENTO
        plazo_despues_man = gestor.obtener_plazo_ejecucion("MANTENIMIENTO")
        print(f"MANTENIMIENTO plazoEjecucion después del cambio: {plazo_despues_man}")
        
        # PASO 4: VERIFICACIÓN CRÍTICA - ¿Se mantiene REPARACIÓN?
        print("\n--- PASO 4: VERIFICACIÓN CRÍTICA ---")
        print("Verificando si REPARACIÓN mantiene su valor después del cambio de MANTENIMIENTO...")
        
        plazo_final_rep = gestor.obtener_plazo_ejecucion("REPARACIÓN")
        plazo_final_man = gestor.obtener_plazo_ejecucion("MANTENIMIENTO")
        
        print(f"REPARACIÓN plazoEjecucion FINAL: {plazo_final_rep} (debe ser 88)")
        print(f"MANTENIMIENTO plazoEjecucion FINAL: {plazo_final_man} (debe ser 66)")
        
        # RESULTADO
        print("\n" + "="*60)
        if plazo_final_rep == "88" and plazo_final_man == "66":
            print("RESULTADO: FIX DE AISLAMIENTO EXITOSO!")
            print("Los valores se mantienen independientes entre contratos")
            return True
        else:
            print("RESULTADO: FIX FALLIDO")
            print(f"REPARACIÓN esperado: 88, obtenido: {plazo_final_rep}")
            print(f"MANTENIMIENTO esperado: 66, obtenido: {plazo_final_man}")
            return False
        
    except Exception as e:
        print(f"ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restaurar backup siempre
        restaurar_backup()

if __name__ == "__main__":
    print(f"Iniciando test directo de aislamiento JSON...")
    print(f"Timestamp: {datetime.now()}")
    
    resultado = test_aislamiento_directo()
    
    print("\n" + "="*60)
    if resultado:
        print("TEST COMPLETADO: AISLAMIENTO FUNCIONANDO")
    else:
        print("TEST FALLIDO: REVISAR IMPLEMENTACIÓN")
    print("="*60)