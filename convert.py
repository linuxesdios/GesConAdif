import subprocess
import os

# Ruta al jar de PlantUML (ajústala a donde lo tengas descargado)
PLANTUML_JAR = r"C:\Users\pablo\plantuml-1.2025.4.jar"

# Archivo PUML de entrada
PUML_FILE = r"C:\Users\pablo\Desktop\generador_actas\architecture_compact.puml"

# Carpeta de salida (misma que el .puml)
OUTPUT_DIR = os.path.dirname(PUML_FILE)

# Ejecutar PlantUML para generar PNG
subprocess.run([
    "java", "-jar", PLANTUML_JAR,
    "-tpng",  # puedes usar -tpng o -tjpg
    "-o", OUTPUT_DIR,
    PUML_FILE
], check=True)

print("✅ Conversión terminada, revisa la carpeta:", OUTPUT_DIR)
