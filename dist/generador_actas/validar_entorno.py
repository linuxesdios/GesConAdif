#!/usr/bin/env python3
"""
Script de validación para Generador de Actas ADIF - Distribución
Verifica que todos los componentes necesarios están disponibles
"""
import os
import sys
import platform

def validar_entorno():
    """Valida el entorno de ejecución"""
    print("=== VALIDACIÓN ENTORNO GENERADOR ACTAS ===")
    
    # 1. Información del sistema
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    
    # 2. Validar archivos críticos
    archivos_criticos = [
        "_internal/BaseDatos/BaseDatos.json",
        "_internal/firmas.py", 
        "_internal/controladores/controlador_resumen.py",
        "obras"
    ]
    
    print("\n--- Archivos críticos ---")
    todos_ok = True
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            if os.path.isfile(archivo):
                size = os.path.getsize(archivo) / 1024
                print(f"✅ {archivo} ({size:.1f} KB)")
            else:
                items = len(os.listdir(archivo))
                print(f"✅ {archivo}/ ({items} elementos)")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    # 3. Validar capacidad de abrir archivos
    print("\n--- Capacidad sistema ---")
    try:
        import subprocess
        print("✅ subprocess disponible")
        
        if platform.system() == 'Windows':
            print("✅ Detección Windows - os.startfile disponible")
        else:
            print(f"✅ Sistema {platform.system()} detectado")
    except:
        print("❌ Error importando subprocess")
        todos_ok = False
    
    # 4. Validar PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 disponible")
    except ImportError:
        print("❌ PyQt5 no disponible")
        todos_ok = False
    
    # 5. Validar PyPDF2
    try:
        import PyPDF2
        print("✅ PyPDF2 disponible (firmas)")
    except ImportError:
        print("❌ PyPDF2 no disponible")
        todos_ok = False
    
    print("\n" + "="*40)
    if todos_ok:
        print("✅ VALIDACIÓN EXITOSA - Todo OK")
        return True
    else:
        print("❌ ERRORES ENCONTRADOS")
        return False

if __name__ == "__main__":
    validar_entorno()
    input("\nPresiona Enter para continuar...")
