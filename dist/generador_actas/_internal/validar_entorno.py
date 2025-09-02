#!/usr/bin/env python3
"""
Script de validación para Generador de Actas ADIF - Distribución
Verifica que todos los componentes necesarios están disponibles
Se ejecuta desde _internal y valida la estructura de la aplicación
"""
import os
import sys
import platform

def validar_entorno():
    """Valida el entorno de ejecución"""
    print("=== VALIDACIÓN ENTORNO GENERADOR ACTAS ===")
    
    # Determinar si estamos en _internal o en el directorio raíz
    current_dir = os.getcwd()
    if current_dir.endswith('_internal'):
        # Estamos en _internal, subir un nivel para validar
        root_dir = os.path.dirname(current_dir)
    else:
        # Estamos en el directorio raíz, usar como base
        root_dir = current_dir
    
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Directorio actual: {current_dir}")
    print(f"Directorio de validación: {root_dir}")
    
    # Cambiar al directorio raíz para las validaciones
    os.chdir(root_dir)
    
    # 2. Validar archivos REALMENTE críticos
    archivos_criticos = [
        "generador_actas.exe",           # Ejecutable principal
        "_internal/BaseDatos.json",      # Base de datos principal
        "_internal/ui",                  # Carpeta UI (crítica)
        "_internal/plantillas",          # Plantillas de documentos
        "_internal/controladores"        # Controladores
    ]
    
    archivos_opcionales = [
        "obras",                         # Puede no existir en primera ejecución
        "_internal/firmas.py",          # Puede no estar si no se usa firmas
        "_internal/facturas_directas.json",
        "_internal/historial_documentos.json"
    ]
    
    print("\n--- Archivos críticos (OBLIGATORIOS) ---")
    todos_ok = True
    for archivo in archivos_criticos:
        ruta_completa = os.path.join(root_dir, archivo)
        if os.path.exists(ruta_completa):
            if os.path.isfile(ruta_completa):
                size = os.path.getsize(ruta_completa) / 1024
                print(f"✅ {archivo} ({size:.1f} KB)")
            else:
                try:
                    items = len(os.listdir(ruta_completa))
                    print(f"✅ {archivo}/ ({items} elementos)")
                except:
                    print(f"✅ {archivo}/ (carpeta)")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO en {ruta_completa}")
            todos_ok = False
    
    print("\n--- Archivos opcionales (pueden faltar) ---")
    for archivo in archivos_opcionales:
        ruta_completa = os.path.join(root_dir, archivo)
        if os.path.exists(ruta_completa):
            if os.path.isfile(ruta_completa):
                size = os.path.getsize(ruta_completa) / 1024
                print(f"✅ {archivo} ({size:.1f} KB)")
            else:
                try:
                    items = len(os.listdir(ruta_completa))
                    print(f"✅ {archivo}/ ({items} elementos)")
                except:
                    print(f"✅ {archivo}/ (carpeta)")
        else:
            print(f"⚠️ {archivo} - No encontrado (OK, se creará automáticamente)")
    
    # 3. Validar capacidad del sistema
    print("\n--- Capacidades del sistema ---")
    try:
        import subprocess
        print("✅ subprocess disponible")
        
        if platform.system() == 'Windows':
            print("✅ Sistema Windows - os.startfile disponible")
        else:
            print(f"✅ Sistema {platform.system()} detectado")
    except Exception as e:
        print(f"⚠️ subprocess: {e}")
    
    # 4. Validar librerías (modo suave - no crítico)
    print("\n--- Librerías (verificación suave) ---")
    librerias = [
        ("PyQt5.QtWidgets", "PyQt5 GUI"),
        ("openpyxl", "Excel"),
        ("lxml", "XML processing"),
        ("json", "JSON processing")
    ]
    
    for lib, desc in librerias:
        try:
            __import__(lib)
            print(f"✅ {lib} ({desc})")
        except ImportError:
            print(f"⚠️ {lib} ({desc}) - No disponible, pero puede funcionar")
            # NO marcar como error crítico
        except Exception as e:
            print(f"⚠️ {lib} ({desc}) - Error: {e}")
    
    # 5. Verificar que BaseDatos.json tiene estructura válida
    try:
        basedatos_path = os.path.join(root_dir, "_internal", "BaseDatos.json")
        if os.path.exists(basedatos_path):
            import json
            with open(basedatos_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            obras_count = len(datos.get('obras', []))
            firmantes_count = len(datos.get('firmantes', {}))
            print(f"✅ BaseDatos.json válido ({obras_count} obras, {firmantes_count} firmantes)")
        else:
            print(f"⚠️ BaseDatos.json no encontrado en {basedatos_path}")
    except Exception as e:
        print(f"⚠️ Error validando BaseDatos.json: {e}")
        todos_ok = False
    
    print("\n" + "="*50)
    if todos_ok:
        print("✅ VALIDACIÓN EXITOSA - Aplicación lista para ejecutar")
        return True
    else:
        print("❌ ERRORES CRÍTICOS ENCONTRADOS")
        print("La aplicación puede no funcionar correctamente")
        return False

if __name__ == "__main__":
    exito = validar_entorno()
    print(f"\n{'✅ RESULTADO: OK' if exito else '❌ RESULTADO: ERRORES'}")
    input("\nPresiona Enter para continuar...")
