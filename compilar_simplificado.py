#!/usr/bin/env python3
"""
Script para compilar Generador de Actas ADIF con estructura SIMPLIFICADA
ESTRUCTURA FINAL:
- generador_actas.exe (ejecutable principal SIN consola)
- generador_actas_console.exe (ejecutable CON consola)
- _internal/ (archivos internos del programa)
  - BaseDeDatos/ (movido DENTRO de _internal)
- obras/ (PRESERVADO - carpeta de trabajos)

ARCHIVOS ELIMINADOS AUTOMÁTICAMENTE:
- ejecutar.bat
- README.txt
- historial_documentos.json
- generador_actas.exe.old
- obras_backup_compilacion/
- reportes/
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def activar_entorno_virtual():
    """Detecta y activa entorno virtual automáticamente"""
    posibles_entornos = [
        "venv/Scripts/python.exe",
        "env/Scripts/python.exe",
        "adif_env/Scripts/python.exe",
        "entorno_adif/Scripts/python.exe"
    ]
    
    for entorno in posibles_entornos:
        if os.path.exists(entorno):
            print(f"✅ Entorno virtual detectado: {entorno}")
            return entorno
    
    print("⚠️ No se detectó entorno virtual, usando Python global")
    return sys.executable

def preservar_archivos_criticos():
    """Respalda SOLO archivos críticos esenciales"""
    print("\n🛡️ Preservando archivos críticos...")
    
    # Solo preservar BaseDatos.json y carpeta obras
    archivos_preservar = {
        "BaseDatos.json": None,
        "_internal/BaseDatos.json": None,
        "dist/generador_actas/_internal/BaseDatos.json": None,
        "_internal/BaseDatos/BaseDatos.json": None,
        "dist/generador_actas/_internal/BaseDatos/BaseDatos.json": None,
    }
    
    carpetas_preservar = {
        "obras": None,
        "dist/generador_actas/obras": None,
        "BaseDatos": None,
        "_internal/BaseDatos": None,
        "dist/generador_actas/_internal/BaseDatos": None,
    }
    
    backups = {
        "archivos": {},
        "carpetas": {}
    }
    
    # Respaldar archivos
    for archivo in archivos_preservar.keys():
        if os.path.exists(archivo):
            backup_path = f"{archivo}.backup_compilacion"
            try:
                shutil.copy2(archivo, backup_path)
                backups["archivos"][archivo] = backup_path
                print(f"✅ Respaldado: {archivo} → {backup_path}")
            except Exception as e:
                print(f"⚠️ Error respaldando {archivo}: {e}")
    
    # Respaldar carpetas
    for carpeta in carpetas_preservar.keys():
        if os.path.exists(carpeta) and os.path.isdir(carpeta):
            backup_path = f"{carpeta.replace('/', '_').replace('\\', '_')}_backup_temp"
            try:
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.copytree(carpeta, backup_path)
                backups["carpetas"][carpeta] = backup_path
                print(f"✅ Respaldado: {carpeta}/ → {backup_path}/")
            except Exception as e:
                print(f"⚠️ Error respaldando {carpeta}: {e}")
    
    return backups

def limpiar_archivos_no_deseados():
    """Elimina archivos específicos que NO queremos en la estructura final"""
    print("\n🧹 Eliminando archivos no deseados...")
    
    archivos_eliminar = [
        "dist/generador_actas/ejecutar.bat",
        "dist/generador_actas/README.txt", 
        "dist/generador_actas/historial_documentos.json",
        "dist/generador_actas/generador_actas.exe.old",
        "dist/generador_actas/validar_entorno.py",    # Eliminar validar_entorno si existe
        "ejecutar.bat",
        "README.txt",
        "historial_documentos.json",
        "validar_entorno.py"                          # También en raíz
    ]
    
    carpetas_eliminar = [
        "dist/generador_actas/obras_backup_compilacion",
        "dist/generador_actas/reportes",
        "obras_backup_compilacion",
        "reportes"
    ]
    
    # Eliminar archivos
    for archivo in archivos_eliminar:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"🗑️ Eliminado: {os.path.basename(archivo)}")
            except Exception as e:
                print(f"⚠️ Error eliminando {archivo}: {e}")
    
    # Eliminar carpetas
    for carpeta in carpetas_eliminar:
        if os.path.exists(carpeta):
            try:
                shutil.rmtree(carpeta)
                print(f"🗑️ Carpeta eliminada: {os.path.basename(carpeta)}/")
            except Exception as e:
                print(f"⚠️ Error eliminando {carpeta}: {e}")

def verificar_dependencias(python_exe):
    """Verifica que las dependencias estén disponibles"""
    dependencias = ['PyQt5', 'openpyxl', 'lxml', 'docx2pdf', 'PyInstaller']
    
    print("\n🔍 Verificando dependencias...")
    for dep in dependencias:
        try:
            resultado = subprocess.run([
                python_exe, "-c", f"import {dep.replace('-', '_').replace('python_', '')}"
            ], capture_output=True, check=True)
            print(f"✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ {dep} - NO ENCONTRADO")
            return False
    
    return True

def verificar_archivos_necesarios():
    """Verifica que todos los archivos necesarios existan"""
    print("\n🔍 Verificando archivos necesarios...")
    
    # Preferir archivos optimizados si existen
    main_file = "main_py_optimized.py" if os.path.exists("main_py_optimized.py") else "main_py.py"
    controlador_file = "controladores/controlador_grafica.py"
    
    archivos_criticos = [
        main_file,
        "modelos_py.py", 
        "helpers_py.py",
        controlador_file
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            return False
    
    return True

def compilar_aplicacion_doble(python_exe):
    """Compila AMBOS ejecutables: normal y con consola"""
    print(f"\n🚀 Compilando AMBOS ejecutables con: {python_exe}")
    
    # Preferir archivo optimizado si existe
    main_file = "main_py_optimized.py" if os.path.exists("main_py_optimized.py") else "main_py.py"
    
    # Buscar icono
    posibles_iconos = ["images/icono.ico", "icono.ico", "resources/icono.ico", "ui/icono.ico"]
    icono_encontrado = None
    for icono in posibles_iconos:
        if os.path.exists(icono):
            icono_encontrado = icono
            break
    
    # CONFIGURACIÓN BASE COMÚN
    comando_base = [
        python_exe, "-m", "PyInstaller",
        "--onedir",
        "--optimize=2",
        "--noupx", 
        "--noconfirm",
        "--distpath=dist_temp",
        "--workpath=build",
        
        # ARCHIVOS DE DATOS
        "--add-data=controladores;controladores",
        "--add-data=ui;ui",
        "--add-data=plantillas;plantillas",
        "--add-data=images;images",
        "--add-data=BaseDatos.json;.",
        "--add-data=obras;obras",  # Incluir carpeta obras en compilación
        
        # LIBRERÍAS ESENCIALES
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets", 
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.uic",
        "--hidden-import=openpyxl",
        "--hidden-import=lxml",
        "--hidden-import=docx2pdf",
        "--hidden-import=controladores.controlador_grafica",
        "--hidden-import=controladores.controlador_json",
        "--hidden-import=controladores.controlador_documentos",
        "--hidden-import=controladores.controlador_pdf",
        "--hidden-import=controladores.controlador_backup",
        "--hidden-import=controladores.controlador_routes",
        "--hidden-import=controladores.Controlador_selector",
        "--hidden-import=modelos_py",
        "--hidden-import=helpers_py",
        
        # EXCLUIR INNECESARIOS
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
        "--exclude-module=notebook",
        "--exclude-module=PySide6",
        "--exclude-module=PySide2", 
        "--exclude-module=PyQt6"
    ]
    
    # Añadir icono si se encontró
    if icono_encontrado:
        comando_base.extend([f"--icon={icono_encontrado}"])
        print(f"✅ Icono incluido: {icono_encontrado}")
    
    # 1. COMPILAR EJECUTABLE SIN CONSOLA (normal)
    print("\n⚙️ Compilando generador_actas.exe (SIN consola)...")
    comando_sin_consola = comando_base.copy()
    comando_sin_consola.extend([
        "--windowed",  # SIN consola
        "--name=generador_actas",
        main_file
    ])
    
    try:
        resultado = subprocess.run(comando_sin_consola, check=True, cwd=os.getcwd())
        print("✅ Compilación SIN consola exitosa")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR compilando SIN consola: {e}")
        return False
    
    # Renombrar el resultado para evitar conflictos
    dist_sin_consola = "dist_temp/generador_actas"
    dist_backup = "dist_temp/generador_actas_windowed"
    if os.path.exists(dist_sin_consola):
        if os.path.exists(dist_backup):
            shutil.rmtree(dist_backup)
        shutil.move(dist_sin_consola, dist_backup)
        print("📦 Ejecutable SIN consola guardado temporalmente")
    
    # 2. COMPILAR EJECUTABLE CON CONSOLA
    print("\n⚙️ Compilando generador_actas_console.exe (CON consola)...")
    comando_con_consola = comando_base.copy()
    comando_con_consola.extend([
        "--console",  # CON consola
        "--name=generador_actas_console", 
        main_file
    ])
    
    try:
        resultado = subprocess.run(comando_con_consola, check=True, cwd=os.getcwd())
        print("✅ Compilación CON consola exitosa")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR compilando CON consola: {e}")
        return False
    
    # Renombrar el resultado
    dist_con_consola = "dist_temp/generador_actas_console"
    dist_console_backup = "dist_temp/generador_actas_console_final"
    if os.path.exists(dist_con_consola):
        if os.path.exists(dist_console_backup):
            shutil.rmtree(dist_console_backup)
        shutil.move(dist_con_consola, dist_console_backup)
        print("📦 Ejecutable CON consola guardado temporalmente")
    
    return True

def crear_estructura_simplificada(backups):
    """Crea la estructura SIMPLIFICADA requerida"""
    print("\n🏗️ Creando estructura SIMPLIFICADA...")
    
    # Definir rutas
    dist_backup_windowed = "dist_temp/generador_actas_windowed"
    dist_backup_console = "dist_temp/generador_actas_console_final"
    dist_final = "dist/generador_actas"
    
    # Limpiar destino si no hay archivos críticos
    if os.path.exists("dist"):
        critical_files = [
            f"{dist_final}/_internal/BaseDatos/BaseDatos.json",
            f"{dist_final}/obras"
        ]
        has_critical = any(os.path.exists(f) for f in critical_files)
        
        if not has_critical:
            print("🧹 Limpiando destino (no hay archivos críticos)...")
            shutil.rmtree("dist")
        else:
            print("🛡️ Preservando archivos críticos en destino...")
    
    # Crear estructura base
    try:
        Path(dist_final).mkdir(parents=True, exist_ok=True)
        Path(f"{dist_final}/_internal").mkdir(exist_ok=True)
        print("✅ Estructura base creada")
    except Exception as e:
        print(f"❌ Error creando estructura: {e}")
        return False
    
    # 1. COPIAR EJECUTABLE SIN CONSOLA
    print("\n🚀 Copiando generador_actas.exe (SIN consola)...")
    exe_windowed_origen = f"{dist_backup_windowed}/generador_actas.exe"
    exe_windowed_destino = f"{dist_final}/generador_actas.exe"
    
    if os.path.exists(exe_windowed_origen):
        try:
            if os.path.exists(exe_windowed_destino):
                os.remove(exe_windowed_destino)
            shutil.copy2(exe_windowed_origen, exe_windowed_destino)
            size_mb = os.path.getsize(exe_windowed_destino) / (1024 * 1024)
            print(f"✅ generador_actas.exe copiado ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"❌ Error copiando ejecutable sin consola: {e}")
            return False
    else:
        print(f"❌ No se encontró: {exe_windowed_origen}")
        return False
    
    # 2. COPIAR EJECUTABLE CON CONSOLA
    print("\n🖥️ Copiando generador_actas_console.exe (CON consola)...")
    exe_console_origen = f"{dist_backup_console}/generador_actas_console.exe"
    exe_console_destino = f"{dist_final}/generador_actas_console.exe"
    
    if os.path.exists(exe_console_origen):
        try:
            if os.path.exists(exe_console_destino):
                os.remove(exe_console_destino)
            shutil.copy2(exe_console_origen, exe_console_destino)
            size_mb = os.path.getsize(exe_console_destino) / (1024 * 1024)
            print(f"✅ generador_actas_console.exe copiado ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"❌ Error copiando ejecutable con consola: {e}")
            return False
    else:
        print(f"❌ No se encontró: {exe_console_origen}")
        return False
    
    # 3. COPIAR ARCHIVOS _INTERNAL
    print("\n📦 Copiando archivos _internal...")
    
    # Usar el _internal de cualquiera de los dos (son iguales)
    internal_origen = f"{dist_backup_windowed}/_internal"
    internal_destino = f"{dist_final}/_internal"
    
    if os.path.exists(internal_origen):
        try:
            # Copiar todos los archivos de _internal
            for item in os.listdir(internal_origen):
                item_origen = os.path.join(internal_origen, item)
                item_destino = os.path.join(internal_destino, item)
                
                if os.path.isdir(item_origen):
                    if os.path.exists(item_destino):
                        shutil.rmtree(item_destino)
                    shutil.copytree(item_origen, item_destino)
                    print(f"   📁 {item}/")
                else:
                    if os.path.exists(item_destino):
                        os.remove(item_destino)
                    shutil.copy2(item_origen, item_destino)
                    print(f"   📄 {item}")
            
            print("✅ Archivos _internal copiados")
        except Exception as e:
            print(f"❌ Error copiando _internal: {e}")
            return False
    else:
        print(f"❌ No se encontró _internal en: {internal_origen}")
        return False
    
    # 4. MOVER BaseDatos DENTRO DE _internal
    print("\n🗄️ Configurando BaseDatos dentro de _internal...")
    
    # Crear carpeta BaseDatos dentro de _internal
    basedatos_destino = f"{dist_final}/_internal/BaseDatos"
    try:
        Path(basedatos_destino).mkdir(exist_ok=True)
        print(f"✅ Carpeta {basedatos_destino}/ creada")
    except Exception as e:
        print(f"❌ Error creando carpeta BaseDatos: {e}")
    
    # 5. RESTAURAR CARPETA OBRAS Y BaseDatos desde backups
    print("\n🛡️ Restaurando archivos críticos...")
    print(f"📋 Backups disponibles: {list(backups['carpetas'].keys())}")
    
    # Restaurar BaseDatos
    for carpeta_original, backup_path in backups["carpetas"].items():
        if backup_path and os.path.exists(backup_path):
            carpeta_nombre = os.path.basename(carpeta_original)
            
            if carpeta_nombre == "BaseDatos" or "BaseDatos" in carpeta_original:
                # BaseDatos va DENTRO de _internal
                destino = f"{dist_final}/_internal/BaseDatos"
                print(f"   📂 Restaurando BaseDatos → _internal/BaseDatos/")
            elif carpeta_nombre == "obras":
                # obras va en la raíz
                destino = f"{dist_final}/obras"
                print(f"   📂 Restaurando obras → obras/")
            else:
                continue
            
            try:
                if os.path.exists(destino):
                    shutil.rmtree(destino)
                
                shutil.move(backup_path, destino)
                print(f"✅ Restaurado: {carpeta_nombre}/ → {os.path.relpath(destino, dist_final)}/")
            except Exception as e:
                print(f"⚠️ Error restaurando {carpeta_nombre}: {e}")
                try:
                    shutil.copytree(backup_path, destino)
                    shutil.rmtree(backup_path)
                    print(f"✅ Copiado (alternativo): {carpeta_nombre}/")
                except:
                    print(f"❌ No se pudo restaurar {carpeta_nombre}")
    
    # Restaurar archivos BaseDatos.json
    print(f"📋 Archivos de backup: {list(backups['archivos'].keys())}")
    for archivo_original, backup_path in backups["archivos"].items():
        if backup_path and os.path.exists(backup_path) and "BaseDatos.json" in archivo_original:
            # Copiar a _internal/BaseDatos/ (para funcionamiento interno)
            destino_internal = f"{dist_final}/_internal/BaseDatos/BaseDatos.json"
            # También copiar a la raíz (para compatibilidad)
            destino_raiz = f"{dist_final}/BaseDatos.json"
            
            try:
                # Crear carpeta _internal/BaseDatos
                os.makedirs(os.path.dirname(destino_internal), exist_ok=True)
                shutil.copy2(backup_path, destino_internal)
                print(f"✅ BaseDatos.json → _internal/BaseDatos/")
                
                # También copiar a raíz
                shutil.copy2(backup_path, destino_raiz)
                print(f"✅ BaseDatos.json → raíz del ejecutable")
                
                os.remove(backup_path)
                break
            except Exception as e:
                print(f"⚠️ Error restaurando BaseDatos.json: {e}")
    
    # 6. ELIMINAR ARCHIVOS NO DESEADOS (por si acaso)
    limpiar_archivos_no_deseados()
    
    return True

def verificar_estructura_final_simplificada():
    """Verifica la estructura final SIMPLIFICADA"""
    print("\n🔍 Verificando estructura final SIMPLIFICADA...")
    
    dist_final = "dist/generador_actas"
    
    # Verificar ejecutables
    ejecutables = [
        ("generador_actas.exe", "🚀 PRINCIPAL (sin consola)"),
        ("generador_actas_console.exe", "🖥️ CON CONSOLA")
    ]
    
    for ejecutable, descripcion in ejecutables:
        exe_path = f"{dist_final}/{ejecutable}"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ {ejecutable} ({size_mb:.1f} MB) - {descripcion}")
        else:
            print(f"❌ {ejecutable} - NO ENCONTRADO")
            return False
    
    # Verificar _internal
    internal_path = f"{dist_final}/_internal"
    if os.path.exists(internal_path):
        archivos_internal = os.listdir(internal_path)
        print(f"✅ _internal/ ({len(archivos_internal)} elementos)")
        
        # Verificar BaseDatos dentro de _internal
        basedatos_path = f"{internal_path}/BaseDatos"
        if os.path.exists(basedatos_path):
            basedatos_archivos = os.listdir(basedatos_path)
            json_files = [f for f in basedatos_archivos if f.endswith('.json')]
            print(f"✅ _internal/BaseDatos/ ({len(json_files)} archivos JSON)")
            
            # Mostrar archivos JSON
            for json_file in json_files[:3]:  # Máximo 3
                print(f"     📄 {json_file}")
            if len(json_files) > 3:
                print(f"     ... y {len(json_files)-3} archivos más")
        else:
            print("❌ _internal/BaseDatos/ - NO ENCONTRADO")
    else:
        print("❌ _internal/ - NO ENCONTRADO")
        return False
    
    # Verificar obras (opcional pero recomendado)
    obras_path = f"{dist_final}/obras"
    if os.path.exists(obras_path):
        obras_archivos = os.listdir(obras_path)
        print(f"✅ obras/ ({len(obras_archivos)} elementos) 🛡️ PRESERVADO")
    else:
        print("⚠️ obras/ - No encontrado (puede ser normal)")
    
    # Calcular tamaño total
    try:
        tamano_total = 0
        archivo_count = 0
        for root, dirs, files in os.walk(dist_final):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    tamano_total += os.path.getsize(filepath)
                    archivo_count += 1
        
        tamano_mb = tamano_total / (1024 * 1024)
        print(f"\n📊 Estadísticas:")
        print(f"   📦 Tamaño total: {tamano_mb:.1f} MB")
        print(f"   📄 Archivos totales: {archivo_count}")
    except Exception as e:
        print(f"⚠️ Error calculando estadísticas: {e}")
    
    # Verificar que NO existen archivos no deseados
    print(f"\n🗑️ Verificando que archivos no deseados fueron eliminados:")
    archivos_no_deseados = [
        "ejecutar.bat", "README.txt", "historial_documentos.json", 
        "generador_actas.exe.old"
    ]
    
    carpetas_no_deseadas = ["obras_backup_compilacion", "reportes"]
    
    todos_limpio = True
    for archivo in archivos_no_deseados:
        archivo_path = f"{dist_final}/{archivo}"
        if os.path.exists(archivo_path):
            print(f"⚠️ {archivo} - AÚN EXISTE (se eliminará)")
            try:
                os.remove(archivo_path)
                print(f"✅ {archivo} - ELIMINADO")
            except:
                todos_limpio = False
        else:
            print(f"✅ {archivo} - No existe (correcto)")
    
    for carpeta in carpetas_no_deseadas:
        carpeta_path = f"{dist_final}/{carpeta}"
        if os.path.exists(carpeta_path):
            print(f"⚠️ {carpeta}/ - AÚN EXISTE (se eliminará)")
            try:
                shutil.rmtree(carpeta_path)
                print(f"✅ {carpeta}/ - ELIMINADO")
            except:
                todos_limpio = False
        else:
            print(f"✅ {carpeta}/ - No existe (correcto)")
    
    if todos_limpio:
        print("✅ Estructura limpia correctamente")
    
    return True

def limpiar_temporales():
    """Limpia archivos temporales de compilación"""
    print("\n🧹 Limpiando archivos temporales...")
    
    archivos_temporales = [
        "dist_temp", 
        "build",
        "__pycache__",
        "generador_actas.spec",        # Eliminar spec files para forzar regeneración limpia
        "generador_actas_console.spec",
        "validar_entorno.py"           # Eliminar si existe
    ]
    
    for archivo in archivos_temporales:
        if os.path.exists(archivo):
            try:
                if os.path.isdir(archivo):
                    shutil.rmtree(archivo)
                    print(f"✅ {archivo}/ eliminado")
                else:
                    os.remove(archivo)
                    print(f"✅ {archivo} eliminado")
            except Exception as e:
                print(f"⚠️ Error eliminando {archivo}: {e}")

def main():
    """Función principal de compilación SIMPLIFICADA"""
    print("=" * 70)
    print("   COMPILADOR GENERADOR ACTAS ADIF - v5.0 (SIMPLIFICADO)")
    print("=" * 70)
    
    # PASO 0: Preservar archivos críticos
    backups = preservar_archivos_criticos()
    
    # Detectar entorno virtual
    python_exe = activar_entorno_virtual()
    
    # Verificar dependencias
    if not verificar_dependencias(python_exe):
        print("\n❌ FALTAN DEPENDENCIAS")
        return False
    
    # Verificar archivos necesarios
    if not verificar_archivos_necesarios():
        print("\n❌ FALTAN ARCHIVOS NECESARIOS")
        return False
    
    # Verificar PyInstaller
    try:
        subprocess.run([python_exe, "-c", "import PyInstaller"], check=True, capture_output=True)
        print("✅ PyInstaller disponible")
    except subprocess.CalledProcessError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([python_exe, "-m", "pip", "install", "pyinstaller"])
    
    # Limpiar compilaciones anteriores
    limpiar_temporales()
    
    # PASO 1: Compilar AMBOS ejecutables
    if not compilar_aplicacion_doble(python_exe):
        print("❌ Error en compilación")
        return False
    
    # PASO 2: Crear estructura simplificada
    if not crear_estructura_simplificada(backups):
        print("❌ Error creando estructura simplificada")
        return False
    
    # PASO 3: Verificar resultado final
    if not verificar_estructura_final_simplificada():
        print("❌ Error en verificación final")
        return False
    
    # PASO 4: Limpiar temporales
    limpiar_temporales()
    
    # ÉXITO
    print("\n" + "=" * 70)
    print("🎉 ¡COMPILACIÓN EXITOSA - ESTRUCTURA SIMPLIFICADA!")
    print("=" * 70)
    
    print("\n📁 ESTRUCTURA FINAL:")
    print("dist/generador_actas/")
    print("├── generador_actas.exe         (🚀 EJECUTABLE PRINCIPAL - SIN consola)")
    print("├── generador_actas_console.exe (🖥️ EJECUTABLE CON consola)")
    print("├── _internal/                  (📦 Archivos internos)")
    print("│   ├── BaseDatos/              (🗄️ Base de datos DENTRO de _internal)")
    print("│   │   ├── BaseDatos.json")
    print("│   │   └── backups automáticos")
    print("│   ├── plantillas/             (📄 Archivos .docx)")
    print("│   ├── otros/                  (🎨 UI y recursos)")
    print("│   └── [librerías PyInstaller]")
    print("└── obras/                      (🛡️ CARPETA PRESERVADA)")
    
    print(f"\n🚀 PARA EJECUTAR:")
    print("- MODO NORMAL: generador_actas.exe")
    print("- MODO DEBUG:  generador_actas_console.exe")
    
    print(f"\n✅ ARCHIVOS ELIMINADOS:")
    print("- ejecutar.bat")
    print("- README.txt") 
    print("- historial_documentos.json")
    print("- generador_actas.exe.old")
    print("- obras_backup_compilacion/")
    print("- reportes/")
    
    return True

if __name__ == "__main__":
    print("🚀 Generador de Actas ADIF - Compilador v5.0 (SIMPLIFICADO)")
    print("📦 Estructura: Solo ejecutables + _internal + obras")
    print("🛡️ Preserva: BaseDatos y obras")
    print("🗑️ Elimina: ejecutar.bat, README.txt, historial, reportes, backups")
    
    # Permitir compilación sin entorno virtual
    print("\n🔍 Iniciando compilación...")
    print("💡 Modo: Estructura simplificada con doble ejecutable")
    
    try:
        success = main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Compilación interrumpida por el usuario")
        success = False
    except Exception as e:
        print(f"\n\n💥 Error inesperado durante la compilación: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print(f"\n{'='*70}")
    if success:
        print("🎊 ¡COMPILACIÓN COMPLETADA - ESTRUCTURA SIMPLIFICADA!")
        print("📁 Ubicación: dist/generador_actas/")
        
        print("\n📋 ESTRUCTURA FINAL GENERADA:")
        print("🚀 generador_actas.exe         (ejecutable principal - SIN consola)")
        print("🖥️ generador_actas_console.exe (ejecutable con consola - DEBUG)")
        print("📦 _internal/                  (archivos internos del programa)")
        print("🗄️ _internal/BaseDatos/        (base de datos MOVIDA aquí)")
        print("🛡️ obras/                     (carpeta de proyectos PRESERVADA)")
        
        print("\n🗑️ ARCHIVOS/CARPETAS ELIMINADOS:")
        print("❌ ejecutar.bat")
        print("❌ README.txt")
        print("❌ historial_documentos.json")
        print("❌ generador_actas.exe.old")
        print("❌ obras_backup_compilacion/")
        print("❌ reportes/")
        
        print("\n🎯 INSTRUCCIONES DE USO:")
        print("1. Ve a: dist/generador_actas/")
        print("2. Ejecuta: generador_actas.exe (modo normal)")
        print("3. O ejecuta: generador_actas_console.exe (si necesitas debug)")
        
        print("\n💡 NOTAS IMPORTANTES:")
        print("• BaseDatos ahora está en: _internal/BaseDatos/")
        print("• Carpeta obras se mantiene en la raíz")
        print("• Archivos innecesarios han sido eliminados")
        print("• Dos ejecutables disponibles: normal y con consola")
        
    else:
        print("💥 ERROR EN COMPILACIÓN")
        print("🔍 Revisa los mensajes de error anteriores")
        print("💡 Sugerencias:")
        print("   - Verifica que tienes todas las dependencias")
        print("   - Comprueba que main_py.py existe")
        print("   - Asegúrate de tener permisos de escritura")
    
    print(f"\n{'='*70}")
    input("⏸️ Presiona Enter para salir...")
    sys.exit(0 if success else 1)