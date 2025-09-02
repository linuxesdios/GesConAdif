#!/usr/bin/env python3
"""
Generador de diagramas UML a partir del archivo PlantUML
Genera una imagen PNG del diagrama de arquitectura
"""

import os
import sys
import subprocess
import requests
import base64
from pathlib import Path

def parse_plantuml_and_generate():
    """Leer architecture_compact.puml y generar usando matplotlib"""
    print("🔄 Analizando architecture_compact.puml y generando con matplotlib...")
    
    puml_file = "architecture_compact.puml"
    if not os.path.exists(puml_file):
        print(f"❌ No se encuentra {puml_file}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
        import re
        
        # Leer archivo PlantUML
        with open(puml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer clases del archivo PlantUML
        classes = []
        
        # Patrón para encontrar definiciones de clase
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{([^}]*)\}', re.DOTALL | re.MULTILINE)
        
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            class_content = match.group(2)
            
            # Extraer métodos y atributos
            methods = []
            lines = class_content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('--') and not line.startswith("'"):
                    # Limpiar la línea
                    if ':' in line:
                        methods.append(line)
                    elif '(' in line:  # Es un método
                        methods.append(line)
                    elif line.startswith(('+', '-', '#')):  # Es un atributo o método
                        methods.append(line)
            
            classes.append({
                'name': class_name,
                'methods': methods[:10]  # Límite de 10 items por clase
            })
        
        print(f"📊 Encontradas {len(classes)} clases en el archivo PlantUML")
        
        # Determinar categorías automáticamente
        def get_category(class_name):
            name_lower = class_name.lower()
            if any(word in name_lower for word in ['main', 'splash']):
                return 'main'
            elif any(word in name_lower for word in ['proyecto', 'datos', 'empresa', 'oferta', 'liquidacion', 'configuracion', 'constantes', 'tipo', 'estado']):
                return 'models'
            elif any(word in name_lower for word in ['controlador', 'gestor', 'manager']):
                return 'controllers'
            elif any(word in name_lower for word in ['utils', 'helpers', 'imports', 'dialogo']):
                return 'utils'
            else:
                return 'other'
        
        # Crear figura más grande para acomodar todas las clases
        fig_width = max(25, len(classes) // 3 * 8)
        fig_height = max(20, len(classes) // 4 * 6)
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        ax.set_xlim(0, 120)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Título
        ax.text(60, 95, 'ADIF Document Generator - Complete Architecture', 
               fontsize=20, fontweight='bold', ha='center')
        ax.text(60, 92, f'Extracted from PlantUML - {len(classes)} Classes', 
               fontsize=14, ha='center', style='italic')
        
        # Colores por categoría
        colors = {
            'main': '#FFE6CC',
            'models': '#E6F2FF', 
            'controllers': '#E6FFE6',
            'utils': '#FFE6F2',
            'other': '#F0F0F0'
        }
        
        # Función para crear caja de clase mejorada
        def create_class_box(x, y, width, height, class_info, color):
            # Caja principal
            box = FancyBboxPatch((x, y), width, height,
                               boxstyle="round,pad=0.2",
                               facecolor=color, edgecolor='black', linewidth=1.2)
            ax.add_patch(box)
            
            # Título de clase
            ax.text(x + width/2, y + height - 1.5, class_info['name'],
                   fontsize=11, fontweight='bold', ha='center')
            
            # Línea separadora
            ax.plot([x + 0.5, x + width - 0.5], [y + height - 3, y + height - 3], 
                   'k-', linewidth=1)
            
            # Métodos y atributos
            for i, method in enumerate(class_info['methods'][:8]):  # Max 8
                # Limpiar el texto del método
                clean_method = method.replace('{static}', '').strip()
                if len(clean_method) > 35:  # Truncar si es muy largo
                    clean_method = clean_method[:32] + '...'
                
                ax.text(x + 0.8, y + height - 4.5 - i*1.2, clean_method,
                       fontsize=9, ha='left', family='monospace')
        
        # Organizar clases por categorías
        categories = {}
        for class_info in classes:
            category = get_category(class_info['name'])
            if category not in categories:
                categories[category] = []
            categories[category].append(class_info)
        
        # Posiciones base para cada categoría
        positions = {
            'main': (5, 80),
            'models': (5, 55),
            'controllers': (5, 20),
            'utils': (70, 55),
            'other': (70, 20)
        }
        
        # Dibujar clases por categoría
        for category, class_list in categories.items():
            if not class_list:
                continue
                
            base_x, base_y = positions.get(category, (5, 5))
            
            # Título de categoría
            category_titles = {
                'main': 'Main Application',
                'models': 'Data Models', 
                'controllers': 'Controllers',
                'utils': 'Utilities',
                'other': 'Other Components'
            }
            
            ax.text(base_x, base_y + 20, category_titles.get(category, category.title()),
                   fontsize=14, fontweight='bold', color='darkblue')
            
            # Dibujar clases en grid
            cols = 3 if len(class_list) > 6 else 2
            for i, class_info in enumerate(class_list):
                col = i % cols
                row = i // cols
                
                x = base_x + col * 20
                y = base_y - row * 18
                
                # Ajustar tamaño según contenido
                width = 18
                height = min(15, 4 + len(class_info['methods']) * 1.2)
                
                create_class_box(x, y, width, height, class_info, colors[category])
        
        # Leyenda mejorada
        legend_x, legend_y = 5, 8
        ax.text(legend_x, legend_y, 'Legend:', fontsize=12, fontweight='bold')
        
        for i, (category, color) in enumerate(colors.items()):
            if category in categories and categories[category]:
                y_pos = legend_y - 2 - i * 1.5
                # Cuadrado de color
                box = FancyBboxPatch((legend_x, y_pos-0.3), 1.5, 1,
                                   facecolor=color, edgecolor='black')
                ax.add_patch(box)
                # Texto
                category_names = {
                    'main': 'Main Application',
                    'models': 'Data Models',
                    'controllers': 'Controllers', 
                    'utils': 'Utilities',
                    'other': 'Other'
                }
                ax.text(legend_x + 2.5, y_pos, f'{category_names.get(category, category)} ({len(categories[category])})',
                       fontsize=10)
        
        # Estadísticas
        stats_x = 90
        ax.text(stats_x, 8, f'Statistics:', fontsize=12, fontweight='bold')
        ax.text(stats_x, 6, f'Total Classes: {len(classes)}', fontsize=10)
        ax.text(stats_x, 4.5, f'Categories: {len([c for c in categories.values() if c])}', fontsize=10)
        
        # Guardar
        output_file = "architecture_complete_parsed.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"✅ Diagrama completo generado: {output_file}")
        print(f"📊 Clases procesadas: {len(classes)}")
        print(f"📁 Categorías: {list(categories.keys())}")
        
        # Abrir imagen
        if sys.platform == "win32":
            os.startfile(output_file)
        
        return True
        
    except ImportError:
        print("❌ matplotlib no está instalado")
        print("💡 Instala con: pip install matplotlib")
        return False
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_with_local_plantuml():
    """Generar usando PlantUML local (si está instalado)"""
    print("🔄 Intentando usar PlantUML local...")
    
    puml_file = "architecture_compact.puml"
    
    try:
        # Intentar ejecutar plantuml
        result = subprocess.run([
            "java", "-jar", "plantuml.jar", 
            "-tpng", puml_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            png_file = puml_file.replace('.puml', '.png')
            print(f"✅ Diagrama generado: {png_file}")
            return True
        else:
            print("❌ Error ejecutando PlantUML local")
            return False
            
    except FileNotFoundError:
        print("⚠️ PlantUML no está instalado localmente")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout ejecutando PlantUML")
        return False
    except Exception as e:
        print(f"❌ Error con PlantUML local: {e}")
        return False

def generate_with_python_plantuml():
    """Generar usando la librería plantuml de Python"""
    print("🔄 Intentando usar librería plantuml de Python...")
    
    try:
        import plantuml
        
        # Leer el archivo
        puml_file = "architecture_compact.puml"
        with open(puml_file, 'r', encoding='utf-8') as f:
            plantuml_code = f.read()
        
        # Crear servidor PlantUML
        server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
        
        # Generar imagen
        output_file = "architecture_diagram.png"
        server.processes_file(puml_file, outfile=output_file)
        
        print(f"✅ Diagrama generado: {output_file}")
        return True
        
    except ImportError:
        print("⚠️ Librería 'plantuml' no está instalada")
        print("💡 Instala con: pip install plantuml")
        return False
    except Exception as e:
        print(f"❌ Error con librería plantuml: {e}")
        return False

def check_puml_file():
    """Verificar que existe el archivo PlantUML"""
    puml_file = "architecture_compact.puml"
    
    if not os.path.exists(puml_file):
        print(f"❌ Error: No se encuentra el archivo {puml_file}")
        print(f"📂 Directorio actual: {os.getcwd()}")
        print("📋 Archivos disponibles:")
        for file in os.listdir('.'):
            if file.endswith('.puml'):
                print(f"   🔹 {file}")
        return False
    
    # Verificar contenido
    with open(puml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print(f"❌ Error: El archivo {puml_file} está vacío")
        return False
    
    if '@startuml' not in content:
        print(f"❌ Error: El archivo {puml_file} no parece ser válido")
        return False
    
    print(f"✅ Archivo {puml_file} encontrado y válido")
    print(f"📊 Tamaño: {len(content)} caracteres")
    return True

def main():
    """Función principal"""
    print("🎨 Generador de Diagramas UML para ADIF")
    print("=" * 50)
    
    # Verificar archivo
    if not check_puml_file():
        return 1
    
    # Intentar diferentes métodos (LOCAL PRIMERO)
    methods = [
        ("Parse PlantUML + Matplotlib", parse_plantuml_and_generate),
        ("PlantUML Local", generate_with_local_plantuml),
        ("Librería Python plantuml", generate_with_python_plantuml)
    ]
    
    for method_name, method_func in methods:
        print(f"\n📌 Método: {method_name}")
        print("-" * 30)
        
        if method_func():
            print(f"\n🎉 ¡Éxito! Diagrama generado usando {method_name}")
            return 0
        
        print(f"⚠️ {method_name} no funcionó, probando siguiente método...")
    
    # Si nada funcionó
    print("\n❌ No se pudo generar el diagrama con ningún método")
    print("\n💡 Soluciones alternativas:")
    print("1. Ve a https://www.plantuml.com/plantuml/uml/")
    print("2. Copia el contenido de architecture_compact.puml")
    print("3. Pégalo en la web y descarga la imagen")
    print("\n📂 O instala dependencias:")
    print("   pip install plantuml requests")
    
    return 1

if __name__ == "__main__":
    exit_code = main()
    
    # Pausa para ver el resultado
    if sys.platform == "win32":
        input("\n⏸️ Presiona Enter para salir...")
    
    sys.exit(exit_code)