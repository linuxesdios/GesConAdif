#!/usr/bin/env python3
"""
Script mejorado para compilar Generador de Actas ADIF con mejor manejo de paths
MEJORAS:
- Mejor manejo de BaseDatos.json y su ubicación
- Inclusión de todos los controladores necesarios
- Verificación de integridad post-compilación
- Manejo mejorado de rutas para PyInstaller
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import time

def activar_entorno_virtual():
    """Detecta y activa entorno virtual automáticamente"""
    posibles_entornos = [
        "venv/Scripts/python.exe",
        "env/Scripts/python.exe", 
        "adif_env/Scripts/python.exe",
        "entorno_adif/Scripts/python.exe",
        "C:/Users/2839876/EntornoPythonAdif/EntornoPython/Scripts/python.exe"  # Ruta actual del entorno
    ]
    
    for entorno in posibles_entornos:
        if os.path.exists(entorno):
            print(f"✅ Entorno virtual detectado: {entorno}")
            return entorno
    
    print("⚠️ No se detectó entorno virtual, usando Python global")
    return sys.executable

def verificar_basedatos_json():
    """Verifica y corrige BaseDatos.json antes de compilar"""
    print("\n🔍 Verificando BaseDatos.json...")
    
    if not os.path.exists("BaseDatos.json"):
        print("⚠️ BaseDatos.json no encontrado, creando uno básico...")
        estructura_basica = {
            "firmantes": {
                "jefe_proyecto": {
                    "nombre": "Nombre del Jefe de Proyecto",
                    "cargo": "Jefe de Proyecto"
                }
            },
            "obras": [
                {
                    "nombre": "OBRAS DE REPARACIÓN EN LAS INSTALACIONES INTERIORES",
                    "expediente": "EXP-2024-001",
                    "tipo": "obras",
                    "datos_contrato": {
                        "basePresupuesto": 26029.89,
                        "precioAdjudicacion": 100.0,
                        "plazoEjecucion": 30,
                        "fechaContrato": "2024-01-01"
                    },
                    "empresas": [],
                    "liquidacion": {}
                },
                {
                    "nombre": "2332",
                    "expediente": "EXP-2024-002", 
                    "tipo": "mantenimiento",
                    "datos_contrato": {},
                    "empresas": [],
                    "liquidacion": {}
                }
            ]
        }
        
        with open("BaseDatos.json", 'w', encoding='utf-8') as f:
            json.dump(estructura_basica, f, ensure_ascii=False, indent=2)
        print("✅ BaseDatos.json creado con datos de ejemplo")
    else:
        # Verificar y corregir estructura existente
        try:
            with open("BaseDatos.json", 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            # Verificar estructura básica
            if "obras" not in datos:
                datos["obras"] = []
            if "firmantes" not in datos:
                datos["firmantes"] = {}
                
            # Asegurar que las obras tienen estructura correcta
            for obra in datos["obras"]:
                if "datos_contrato" not in obra:
                    obra["datos_contrato"] = {}
                if "empresas" not in obra:
                    obra["empresas"] = []
                if "liquidacion" not in obra:
                    obra["liquidacion"] = {}
                if "expediente" not in obra:
                    obra["expediente"] = f"EXP-{obra.get('nombre', 'SIN_NOMBRE')[:10]}"
                    
            # Guardar cambios
            with open("BaseDatos.json", 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
                
            print(f"✅ BaseDatos.json verificado - {len(datos['obras'])} obras encontradas")
            
        except Exception as e:
            print(f"❌ Error verificando BaseDatos.json: {e}")
            return False
    
    return True

def preservar_archivos_criticos():
    """Respalda archivos críticos esenciales"""
    print("\n🛡️ Preservando archivos críticos...")
    
    archivos_preservar = ["BaseDatos.json"]
    carpetas_preservar = ["obras", "plantillas"]
    
    backups = {"archivos": {}, "carpetas": {}}
    
    # Respaldar archivos
    for archivo in archivos_preservar:
        if os.path.exists(archivo):
            backup_path = f"{archivo}.backup_compilacion"
            try:
                shutil.copy2(archivo, backup_path)
                backups["archivos"][archivo] = backup_path
                print(f"✅ Respaldado: {archivo}")
            except Exception as e:
                print(f"⚠️ Error respaldando {archivo}: {e}")
    
    # Respaldar carpetas
    for carpeta in carpetas_preservar:
        if os.path.exists(carpeta):
            backup_path = f"{carpeta}_backup_temp"
            try:
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.copytree(carpeta, backup_path)
                backups["carpetas"][carpeta] = backup_path
                print(f"✅ Respaldado: {carpeta}/")
            except Exception as e:
                print(f"⚠️ Error respaldando {carpeta}: {e}")
    
    return backups

def compilar_con_mejoras(python_exe):
    """Compila con configuración mejorada"""
    print(f"\n🚀 Compilando con mejoras usando: {python_exe}")
    
    main_file = "main_py_optimized.py" if os.path.exists("main_py_optimized.py") else "main_py.py"
    
    # Buscar icono
    icono_encontrado = None
    for icono in ["images/icono.ico", "icono.ico", "ui/icono.ico"]:
        if os.path.exists(icono):
            icono_encontrado = icono
            break
    
    comando = [
        python_exe, "-m", "PyInstaller",
        "--onedir",
        "--windowed",  # Sin consola para ejecutable principal
        "--optimize=2",
        "--noupx",
        "--noconfirm",
        "--name=generador_actas",
        "--distpath=dist",
        "--workpath=build",
        
        # ARCHIVOS DE DATOS CRÍTICOS
        "--add-data=BaseDatos.json;.",
        "--add-data=controladores;controladores",
        "--add-data=ui;ui", 
        "--add-data=plantillas;plantillas",
        "--add-data=images;images",
        "--add-data=firmas.py;.",
        
        # LIBRERÍAS ESENCIALES + CONTROLADORES FALTANTES
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.uic",
        "--hidden-import=PyQt5.QtGraphicsView",
        "--hidden-import=openpyxl",
        "--hidden-import=lxml",
        "--hidden-import=docx2pdf",
        "--hidden-import=PyPDF2",
        "--hidden-import=platform",
        "--hidden-import=subprocess",
        "--hidden-import=controladores.controlador_grafica",
        "--hidden-import=controladores.controlador_json",
        "--hidden-import=controladores.controlador_documentos", 
        "--hidden-import=controladores.controlador_pdf_unificado",
        "--hidden-import=controladores.controlador_backup",
        "--hidden-import=controladores.controlador_routes",
        "--hidden-import=controladores.Controlador_selector",
        "--hidden-import=controladores.controlador_actuaciones_facturas",
        "--hidden-import=controladores.controlador_facturas_directas",
        "--hidden-import=controladores.controlador_resumen",
        "--hidden-import=controladores.controlador_contratos",
        "--hidden-import=controladores.controlador_tablas",
        "--hidden-import=controladores.controlador_calculos",
        "--hidden-import=controladores.controlador_eventos_ui",
        "--hidden-import=controladores.controlador_autosave",
        "--hidden-import=controladores.controlador_fases_documentos",
        "--hidden-import=controladores.controlador_archivos_unificado",
        "--hidden-import=controladores.ventana_doble_tabla",
        "--hidden-import=controladores.dialogo_actuaciones_especiales",
        "--hidden-import=controladores.dialogo_gestionar_contratos",
        "--hidden-import=modelos_py",
        "--hidden-import=helpers_py",
        "--hidden-import=firmas",
        
        # EXCLUIR INNECESARIOS
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
        "--exclude-module=notebook",
        "--exclude-module=PySide6",
        "--exclude-module=PySide2",
        "--exclude-module=PyQt6",
        
        main_file
    ]
    
    # Añadir icono si existe
    if icono_encontrado:
        comando.insert(-1, f"--icon={icono_encontrado}")
        print(f"✅ Icono incluido: {icono_encontrado}")
    
    try:
        print("⏳ Ejecutando PyInstaller...")
        resultado = subprocess.run(comando, check=True)
        print("✅ Compilación exitosa")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR en compilación: {e}")
        return False

def reorganizar_estructura_mejorada(backups):
    """Reorganiza estructura con mejoras en manejo de BaseDatos"""
    print("\n🏗️ Reorganizando estructura mejorada...")
    
    dist_dir = "dist/generador_actas"
    internal_dir = f"{dist_dir}/_internal"
    
    if not os.path.exists(dist_dir):
        print(f"❌ No se encontró directorio compilado: {dist_dir}")
        return False
    
    # 1. MOVER TODOS LOS JSON A _internal (NO en subdirectorios)
    print("📁 Moviendo todos los JSON a _internal...")
    
    archivos_json = {
        "BaseDatos.json": [
            "BaseDatos.json.backup_compilacion", # Desde backup (primera prioridad)
            "BaseDatos.json",                     # Desde directorio actual
            f"{dist_dir}/BaseDatos.json",         # Por si quedó en raíz dist
            f"{internal_dir}/BaseDatos.json"      # Desde add-data (última prioridad)
        ],
        "facturas_directas.json": [
            "facturas_directas.json",            # Desde directorio actual
            f"{dist_dir}/facturas_directas.json",
            f"{internal_dir}/facturas_directas.json"
        ],
        "historial_documentos.json": [
            "historial_documentos.json",         # Desde directorio actual
            f"{dist_dir}/historial_documentos.json",
            f"{internal_dir}/historial_documentos.json"
        ]
    }
    
    # 2. PROCESAR CADA ARCHIVO JSON
    for nombre_archivo, sources in archivos_json.items():
        destino = f"{internal_dir}/{nombre_archivo}"
        archivo_copiado = False
        
        for source in sources:
            if os.path.exists(source):
                try:
                    if os.path.exists(destino):
                        os.remove(destino)
                    shutil.copy2(source, destino)
                    print(f"✅ {nombre_archivo} copiado desde: {source}")
                    archivo_copiado = True
                    
                    # Limpiar archivo original si no es el backup y está en la raíz del dist
                    if source.startswith(dist_dir) and not source.endswith(".backup_compilacion"):
                        try:
                            os.remove(source)
                        except:
                            pass
                    break
                except Exception as e:
                    print(f"⚠️ Error copiando {nombre_archivo} desde {source}: {e}")
                    continue
        
        # Si no se pudo copiar desde ninguna fuente, crear archivo básico si es crítico
        if not archivo_copiado:
            if nombre_archivo == "BaseDatos.json":
                print(f"⚠️ {nombre_archivo} no encontrado en ninguna fuente, creando básico...")
                try:
                    estructura_basica = {
                        "firmantes": {},
                        "obras": []
                    }
                    with open(destino, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(estructura_basica, f, ensure_ascii=False, indent=2)
                    print(f"✅ {nombre_archivo} básico creado")
                except Exception as e:
                    print(f"❌ Error creando {nombre_archivo} básico: {e}")
            else:
                print(f"⚠️ {nombre_archivo} no encontrado (archivo opcional)")
    
    # 3. RESTAURAR CARPETAS CRÍTICAS
    for carpeta_original, backup_path in backups["carpetas"].items():
        if backup_path and os.path.exists(backup_path):
            if carpeta_original == "obras":
                destino = f"{dist_dir}/obras"
            elif carpeta_original == "plantillas":
                # Plantillas ya deberían estar en _internal por add-data
                continue
            else:
                continue
                
            try:
                if os.path.exists(destino):
                    shutil.rmtree(destino)
                shutil.move(backup_path, destino)
                print(f"✅ Restaurado: {carpeta_original}/ → {destino}")
            except Exception as e:
                print(f"⚠️ Error restaurando {carpeta_original}: {e}")
    
    # 4. CREAR SCRIPT DE VALIDACIÓN
    crear_script_validacion(dist_dir)
    
    # 5. COMPILAR TAMBIÉN VERSIÓN CON CONSOLA
    print("\n🖥️ Compilando versión con consola...")
    crear_version_consola()
    
    return True

def crear_script_validacion(dist_dir):
    """Crea script de validación para el ejecutable distribuido"""
    try:
        script_content = '''#!/usr/bin/env python3
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
    
    print("\\n--- Archivos críticos (OBLIGATORIOS) ---")
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
    
    print("\\n--- Archivos opcionales (pueden faltar) ---")
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
    print("\\n--- Capacidades del sistema ---")
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
    print("\\n--- Librerías (verificación suave) ---")
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
    
    print("\\n" + "="*50)
    if todos_ok:
        print("✅ VALIDACIÓN EXITOSA - Aplicación lista para ejecutar")
        return True
    else:
        print("❌ ERRORES CRÍTICOS ENCONTRADOS")
        print("La aplicación puede no funcionar correctamente")
        return False

if __name__ == "__main__":
    exito = validar_entorno()
    print(f"\\n{'✅ RESULTADO: OK' if exito else '❌ RESULTADO: ERRORES'}")
    input("\\nPresiona Enter para continuar...")
'''
        
        # Crear el script en _internal
        internal_dir = f"{dist_dir}/_internal"
        script_path = f"{internal_dir}/validar_entorno.py"
        
        if not os.path.exists(internal_dir):
            os.makedirs(internal_dir)
            
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Script de validación creado en: {script_path}")
        
        # Crear también versión .exe del script de validación
        crear_validador_exe(script_path, internal_dir)
        
    except Exception as e:
        print(f"⚠️ Error creando script de validación: {e}")

def crear_validador_exe(script_path, internal_dir):
    """Crea versión .exe del validador"""
    try:
        python_exe = activar_entorno_virtual()
        
        comando = [
            python_exe, "-m", "PyInstaller",
            "--onefile",                    # Un solo archivo .exe
            "--console",                    # Con consola
            "--optimize=2",
            "--noupx",
            "--noconfirm",
            "--name=validar_entorno",
            "--distpath=temp_validator",    # Directorio temporal
            "--workpath=temp_validator_build",
            script_path
        ]
        
        print("🔨 Compilando validador a .exe...")
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        
        # Mover el .exe a _internal
        exe_source = "temp_validator/validar_entorno.exe"
        exe_dest = f"{internal_dir}/validar_entorno.exe"
        
        if os.path.exists(exe_source):
            shutil.copy2(exe_source, exe_dest)
            print(f"✅ Validador .exe creado: {exe_dest}")
            
            # Limpiar temporales
            shutil.rmtree("temp_validator", ignore_errors=True)
            shutil.rmtree("temp_validator_build", ignore_errors=True)
            
        else:
            print("⚠️ No se pudo crear validar_entorno.exe")
            
    except Exception as e:
        print(f"⚠️ Error creando validador .exe: {e}")
        # Limpiar temporales en caso de error
        shutil.rmtree("temp_validator", ignore_errors=True)
        shutil.rmtree("temp_validator_build", ignore_errors=True)

def crear_version_consola():
    """Crea versión con consola para debug"""
    python_exe = activar_entorno_virtual()
    main_file = "main_py_optimized.py" if os.path.exists("main_py_optimized.py") else "main_py.py"
    
    comando = [
        python_exe, "-m", "PyInstaller",
        "--onedir",
        "--console",  # CON consola para debug
        "--optimize=2",
        "--noupx",
        "--noconfirm", 
        "--name=generador_actas_console",
        "--distpath=dist_console",
        "--workpath=build_console",
        main_file
    ]
    
    try:
        subprocess.run(comando, check=True, capture_output=True)
        
        # Copiar ejecutable a ubicación final
        exe_source = "dist_console/generador_actas_console/generador_actas_console.exe"
        exe_dest = "dist/generador_actas/generador_actas_console.exe"
        
        if os.path.exists(exe_source):
            shutil.copy2(exe_source, exe_dest)
            print("✅ Versión con consola creada")
            
            # Limpiar temporal
            shutil.rmtree("dist_console", ignore_errors=True)
            shutil.rmtree("build_console", ignore_errors=True)
            
    except Exception as e:
        print(f"⚠️ Error creando versión consola: {e}")

def verificar_estructura_final_mejorada():
    """Verificación mejorada de la estructura final"""
    print("\n🔍 Verificando estructura final mejorada...")
    
    dist_dir = "dist/generador_actas"
    checks = {
        "generador_actas.exe": f"{dist_dir}/generador_actas.exe",
        "generador_actas_console.exe": f"{dist_dir}/generador_actas_console.exe", 
        "_internal/": f"{dist_dir}/_internal",
        "BaseDatos.json": f"{dist_dir}/_internal/BaseDatos.json",
        "facturas_directas.json": f"{dist_dir}/_internal/facturas_directas.json",
        "historial_documentos.json": f"{dist_dir}/_internal/historial_documentos.json",
        "obras/": f"{dist_dir}/obras",
        "firmas.py": f"{dist_dir}/_internal/firmas.py",
        "controladores/controlador_resumen.py": f"{dist_dir}/_internal/controladores/controlador_resumen.py",
        "validar_entorno.py": f"{dist_dir}/_internal/validar_entorno.py",
        "validar_entorno.exe": f"{dist_dir}/_internal/validar_entorno.exe"
    }
    
    todos_ok = True
    for nombre, ruta in checks.items():
        if os.path.exists(ruta):
            if os.path.isfile(ruta):
                size = os.path.getsize(ruta) / (1024*1024)
                print(f"✅ {nombre} ({size:.1f} MB)")
            else:
                items = len(os.listdir(ruta)) if os.path.isdir(ruta) else 0
                print(f"✅ {nombre} ({items} elementos)")
        else:
            print(f"❌ {nombre} - NO ENCONTRADO")
            todos_ok = False
    
    # Verificar que BaseDatos.json tiene contenido válido
    basedatos_path = f"{dist_dir}/_internal/BaseDatos.json"
    if os.path.exists(basedatos_path):
        try:
            with open(basedatos_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            obras_count = len(datos.get('obras', []))
            print(f"✅ BaseDatos.json válido ({obras_count} obras)")
        except Exception as e:
            print(f"❌ BaseDatos.json corrupto: {e}")
            todos_ok = False
    
    return todos_ok

def limpiar_temporales():
    """Limpia archivos temporales"""
    print("\n🧹 Limpiando temporales...")
    
    temporales = [
        "build", "build_console", "dist_console",
        "*.backup_compilacion", "*_backup_temp"
    ]
    
    for temp in temporales:
        if '*' in temp:
            import glob
            for archivo in glob.glob(temp):
                try:
                    if os.path.isfile(archivo):
                        os.remove(archivo)
                    else:
                        shutil.rmtree(archivo)
                    print(f"✅ Eliminado: {archivo}")
                except:
                    pass
        else:
            if os.path.exists(temp):
                try:
                    if os.path.isfile(temp):
                        os.remove(temp)
                    else:
                        shutil.rmtree(temp)
                    print(f"✅ Eliminado: {temp}")
                except:
                    pass

def main():
    """Función principal de compilación mejorada"""
    print("=" * 70)
    print("   COMPILADOR MEJORADO GENERADOR ACTAS ADIF")
    print("   ✨ Con mejoras de paths y BaseDatos.json")
    print("=" * 70)
    
    try:
        # 1. Verificar y corregir BaseDatos.json
        if not verificar_basedatos_json():
            print("❌ Error en BaseDatos.json")
            return False
        
        # 2. Preservar archivos críticos  
        backups = preservar_archivos_criticos()
        
        # 3. Detectar Python
        python_exe = activar_entorno_virtual()
        
        # 4. Compilar aplicación
        if not compilar_con_mejoras(python_exe):
            print("❌ Error en compilación")
            return False
        
        # 5. Reorganizar estructura
        if not reorganizar_estructura_mejorada(backups):
            print("❌ Error reorganizando estructura")
            return False
        
        # 6. Verificar resultado
        if not verificar_estructura_final_mejorada():
            print("❌ Error en verificación final")
            return False
        
        # 7. Limpiar temporales
        limpiar_temporales()
        
        print("\n🎉 ¡COMPILACIÓN EXITOSA CON MEJORAS!")
        print("\n📁 ESTRUCTURA FINAL:")
        print("dist/generador_actas/")
        print("├── generador_actas.exe (🚀 Principal)")
        print("├── generador_actas_console.exe (🖥️ Debug)")
        print("├── _internal/")
        print("│   ├── BaseDatos.json (✅ DATOS PRINCIPALES)")
        print("│   ├── facturas_directas.json (✅ FACTURAS)")  
        print("│   ├── historial_documentos.json (✅ HISTORIAL)")
        print("│   ├── firmas.py (📋 Escaneado de firmas PDF)")
        print("│   ├── validar_entorno.py (🔧 Validación Python)")
        print("│   ├── validar_entorno.exe (🔧 Validación EXE)")
        print("│   ├── controladores/")
        print("│   │   └── controlador_resumen.py (📊 Tabla seguimiento + PDF)")
        print("│   └── [otros archivos internos]")
        print("└── obras/ (🛡️ Preservado)")
        print("\n✨ NUEVAS FUNCIONALIDADES INCLUIDAS:")
        print("   📋 Tabla de seguimiento con firmas digitales")
        print("   📂 Clic en tabla para abrir PDFs automáticamente") 
        print("   🔍 Escaneo automático de firmas en documentos")
        print("   📊 Timeline visual de fases del proyecto")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Compilador Mejorado - Generador Actas ADIF")
    print("🔧 Correcciones: BaseDatos paths, controladores faltantes")
    
    success = main()
    
    if success:
        print("\n✅ COMPILACIÓN COMPLETADA CON MEJORAS")
        print("🎯 Ejecuta: dist/generador_actas/generador_actas.exe")
        print("🐛 Debug: dist/generador_actas/generador_actas_console.exe")
    else:
        print("\n❌ ERROR EN COMPILACIÓN")
    
    input("\n⏸️ Presiona Enter para salir...")