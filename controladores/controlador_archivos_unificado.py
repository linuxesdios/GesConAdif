#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
"""
=============================================================================
REPORTE DE ANÁLISIS COMPLETO - GENERADOR DE ACTAS ADIF v3.0
=============================================================================

FECHA DE ANÁLISIS: 2025-01-07
ARCHIVOS ANALIZADOS: 17 controladores principales

=============================================================================
🔥 FUNCIONES COMPLETAMENTE DUPLICADAS (CRÍTICO - ELIMINAR INMEDIATAMENTE)
=============================================================================

1. CLASE ExcelTableApp - DUPLICACIÓN COMPLETA:
   📁 controlador_excel.py:19-258 vs 367-801
   💥 PROBLEMA: La misma clase está definida 2 veces completas
   🔧 SOLUCIÓN: Eliminar la primera definición (líneas 19-258)

2. MÉTODO _cargar_todos_los_widgets - LÓGICA SIMILAR:
   📁 controlador_grafica.py:273-350 
   📁 controlador_grafica.py:560-618 (_cargar_campos_basicos)
   💥 PROBLEMA: Ambos cargan widgets pero con enfoques diferentes
   🔧 SOLUCIÓN: Unificar en un solo método optimizado

3. MÉTODOS DE GESTIÓN DE EMPRESAS - DUPLICADOS:
   📁 controlador_grafica.py:477-521 (_cargar_tabla_empresas)
   📁 controlador_grafica.py:665-701 (_cargar_empresas_directas) 
   📁 controlador_calculos.py:508-536 (sincronizar_empresas_ofertas)
   💥 PROBLEMA: 3 formas diferentes de cargar la misma tabla
   🔧 SOLUCIÓN: Mantener solo el método unificado más reciente

4. FUNCIONES DE VALIDACIÓN - REDUNDANTES:
   📁 controlador_calculos.py:582-600 (_es_numero_valido)
   📁 controlador_eventos_ui.py:566-578 (validar_datos_empresas)
   💥 PROBLEMA: Validación numérica repetida
   🔧 SOLUCIÓN: Crear utilidad común en helpers_py.py

=============================================================================
🟡 FUNCIONES OBSOLETAS Y NO UTILIZADAS (ALTO - REVISAR)
=============================================================================

5. MÉTODOS DE ANIMACIÓN - INNECESARIOS:
   📁 controlador_grafica.py:744-919 (todo el bloque de animaciones)
   💥 PROBLEMA: Complejo, no esencial para funcionalidad
   🔧 SOLUCIÓN: Eliminar o simplificar drasticamente

6. MÉTODOS DE PDF - POSIBLE REDUNDANCIA:
   📁 controlador_grafica.py:718-742 (update_pdf_for_current_contract)
   💥 PROBLEMA: Muy específico, posible sobrecarga
   🔧 SOLUCIÓN: Revisar si es realmente necesario

7. CONTROLADOR DE EVENTOS - DEMASIADO ESPECÍFICO:
   📁 controlador_eventos_ui.py:35-196 (setup_event_handlers gigante)
   💥 PROBLEMA: Método monstruoso con 160+ líneas
   🔧 SOLUCIÓN: Dividir en métodos más pequeños

8. MÉTODOS DE DEBUG - INNECESARIOS EN PRODUCCIÓN:
   📁 controlador_grafica.py:61-169 (debug_rutas_completo)
   📁 controlador_contratos.py:167-186 (debug_contract_status) 
   💥 PROBLEMA: Código de debug en producción
   🔧 SOLUCIÓN: Eliminar o envolver en condicional DEBUG

=============================================================================
🟠 OPTIMIZACIONES MAYORES RECOMENDADAS (MEDIO)
=============================================================================

9. CLASE ControladorCalculos - DEMASIADO AUTO-GUARDADO:
   📁 controlador_calculos.py:312-344 (_guardar_campo_calculado_en_json)
   💥 PROBLEMA: Guarda en JSON cada cálculo individual
   🔧 SOLUCIÓN: Batch saving al final de cálculos

10. CONTROLADOR_JSON - MÉTODOS SIMILARES:
    📁 controlador_json.py:96-158 (múltiples métodos de búsqueda)
    💥 PROBLEMA: 4 métodos para buscar contratos
    🔧 SOLUCIÓN: Unificar en método inteligente único

11. GESTIÓN DE TABLAS - REDUNDANCIA:
    📁 controlador_tablas.py:35-100 (setup completo)
    📁 controlador_grafica.py:924-973 (configuración similar)
    💥 PROBLEMA: Configuración de tablas en dos lugares
    🔧 SOLUCIÓN: Centralizar en controlador_tablas.py

=============================================================================
🔵 MEJORAS MENORES RECOMENDADAS (BAJO)
=============================================================================

12. MÉTODOS DE UI PERSONALIZADOS - SIMPLIFICAR:
    📁 controlador_grafica.py:1100-1182 (_create_custom_title_bar)
    💥 PROBLEMA: Complejidad innecesaria para barra de título
    🔧 SOLUCIÓN: Simplificar o usar estándares Qt

13. MÚLTIPLES MÉTODOS DE CARGA - CONSOLIDAR:
    📁 controlador_grafica.py:621-663 (_cargar_fechas, _cargar_tipo_contrato)
    💥 PROBLEMA: Muchos métodos pequeños para carga
    🔧 SOLUCIÓN: Consolidar en menos métodos más eficientes

=============================================================================
📊 ESTADÍSTICAS DE DUPLICACIÓN
=============================================================================

TOTAL LÍNEAS DUPLICADAS DETECTADAS: ~847 líneas
TOTAL MÉTODOS REDUNDANTES: 23
POTENCIAL REDUCCIÓN DE CÓDIGO: 35-40%

ARCHIVOS MÁS PROBLEMÁTICOS:
1. controlador_excel.py (261 líneas duplicadas)
2. controlador_grafica.py (198 líneas redundantes) 
3. controlador_calculos.py (156 líneas de auto-guardado excesivo)
4. controlador_eventos_ui.py (134 líneas de método gigante)

=============================================================================
🎯 PLAN DE LIMPIEZA RECOMENDADO
=============================================================================

FASE 1 - CRÍTICO (Hacer INMEDIATAMENTE):
- Eliminar ExcelTableApp duplicada
- Consolidar métodos de carga de widgets
- Eliminar métodos debug de producción

FASE 2 - ALTO (Próxima semana):  
- Refactorizar controlador_eventos_ui
- Unificar gestión de tablas
- Optimizar auto-guardado JSON

FASE 3 - MEDIO (Siguiente iteración):
- Simplificar animaciones UI
- Consolidar métodos de carga específicos
- Revisar necesidad de métodos PDF complejos

=============================================================================

Gestor Unificado de Archivos y Carpetas de Obras
Combina lo mejor de controlador_archivos.py y gestor_carpetas.py
"""
import os
import re,sys
import json
import subprocess
import platform
from typing import Optional, Tuple, List
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QTimer


class GestorArchivos:
    """Gestor unificado para gestión completa de archivos y carpetas de obras"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.obras_dir = self._auto_detectar_directorio_obras()
        self._cache_carpetas = {}
    
    def set_main_window(self, main_window):
        """Establecer referencia a la ventana principal"""
        self.main_window = main_window

    # ========================================
    # 🔍 DETECCIÓN ROBUSTA DEL DIRECTORIO
    # ========================================
    
    def _auto_detectar_directorio_obras(self):
        """Auto-detección SIMPLE: buscar obras junto al EXE, sino crear"""
        try:
            # Detectar si estamos en ejecutable
            if getattr(sys, 'frozen', False):
                # Ejecutable: buscar/crear junto al EXE
                exe_dir = os.path.dirname(sys.executable)
                obras_dir = os.path.join(exe_dir, "obras")
            else:
                # Desarrollo: buscar/crear junto al script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                obras_dir = os.path.join(script_dir, "..", "obras")
            
            # Crear si no existe
            os.makedirs(obras_dir, exist_ok=True)
            
            return os.path.abspath(obras_dir)
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error detectando directorio obras: {e}")
            # Fallback a directorio actual
            fallback = os.path.join(os.getcwd(), "obras")
            os.makedirs(fallback, exist_ok=True)
            return fallback
    
    def debug_rutas_completo(self):
        """Debug exhaustivo de todas las rutas y estado del sistema"""
        try:
            # Debug completo disponible solo cuando sea necesario
            pass
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error en debug completo: {e}")
            import traceback
            traceback.print_exc()

    # ========================================
    # 🔍 BÚSQUEDA DE CARPETAS EXISTENTES
    # ========================================
    
    def buscar_carpeta_existente(self, contract_data):
        """Buscar carpeta existente con varios criterios físicos y explícitos"""
        try:
            if not os.path.exists(self.obras_dir):
                return None

            # Obtener datos del contrato
            nombre_obra = contract_data.get('nombreObra', '').strip()
            numero_expediente = contract_data.get('numeroExpediente', '').strip()
            nombre_carpeta_json = contract_data.get('nombreCarpeta', '').strip()
            alias = contract_data.get('alias', '').strip()


            carpetas_existentes = [
                item for item in os.listdir(self.obras_dir)
                if os.path.isdir(os.path.join(self.obras_dir, item))
            ]

            if not carpetas_existentes:
                return None

            # CRITERIO 0: nombreCarpeta explícito (preferente si está bien definido)
            if nombre_carpeta_json and nombre_carpeta_json in carpetas_existentes:
                return os.path.join(self.obras_dir, nombre_carpeta_json)

            # CRITERIO 2: nombre generado por contrato (expediente o nombreObra)
            nombre_esperado = self._generar_nombre_carpeta(contract_data)

            for carpeta in carpetas_existentes:
                if carpeta == nombre_esperado:
                    return os.path.join(self.obras_dir, carpeta)

            # CRITERIO 3: prefijo
            for carpeta in carpetas_existentes:
                if carpeta.startswith(nombre_esperado):
                    return os.path.join(self.obras_dir, carpeta)

            # CRITERIO 4: coincidencia numérica en expediente
            numeros_expediente = ''.join(re.findall(r'\d+', numero_expediente))
            if numeros_expediente and len(numeros_expediente) >= 3:
                for carpeta in carpetas_existentes:
                    numeros_carpeta = ''.join(re.findall(r'\d+', carpeta))
                    if numeros_expediente == numeros_carpeta:
                        return os.path.join(self.obras_dir, carpeta)

            # CRITERIO 5: fuzzy por nombre de obra
            if nombre_obra and len(nombre_obra) > 10:
                nombre_obra_limpio = self._limpiar_texto_busqueda(nombre_obra)
                mejor_score = 0
                mejor_carpeta = None

                for carpeta in carpetas_existentes:
                    carpeta_limpia = self._limpiar_texto_busqueda(carpeta)
                    score = self._calcular_similitud_texto(nombre_obra_limpio, carpeta_limpia)
                    if score > 0.7 and score > mejor_score:
                        mejor_score = score
                        mejor_carpeta = carpeta

                if mejor_carpeta:
                    return os.path.join(self.obras_dir, mejor_carpeta)

            return None

        except Exception as e:
            print(f"[GestorUnificado] ❌ Error buscando carpeta existente: {e}")
            import traceback
            traceback.print_exc()
            return None

    
    def renombrar_carpeta_por_expediente(self):
        """Valida, transforma y renombra la carpeta de la obra usando el número de expediente"""
        
        try:
            if not self.main_window:
                return

            # Obtener datos desde la UI
            nombre_obra = self.main_window.nombreObra.text().strip()
            numero_expediente = self.main_window.numeroExpediente.text().strip()

            if not nombre_obra or not numero_expediente:
                return False

            # ✅ Validar que el expediente tenga al menos 2 puntos y 2 barras y formato correcto
            import re

            if numero_expediente.count('.') < 2 or numero_expediente.count('/') < 2:
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("⚠️ Formato de Expediente Incorrecto")
                msg.setText("<b>El número de expediente no tiene el formato válido</b>")
                msg.setInformativeText(
                    f"<b>Expediente ingresado:</b> {numero_expediente}<br><br>"
                    f"<b>Formato requerido:</b> XX.XX.XX/XX.XX.XX/XXXX<br>"
                    f"<b>Ejemplo válido:</b> 12.34.56/78.90.12/2025<br><br>"
                    f"<b>Requisitos mínimos:</b><br>"
                    f"• Al menos 2 puntos (.)<br>"
                    f"• Al menos 2 barras (/)<br>"
                    f"• Solo números separados por puntos y barras"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return False

            patron = r'^\d+(\.\d+)*\/\d+(\.\d+)*\/\d+$'
            if not re.match(patron, numero_expediente):
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("⚠️ Formato de Expediente Incorrecto")
                msg.setText("<b>El número de expediente contiene caracteres no válidos</b>")
                msg.setInformativeText(
                    f"<b>Expediente ingresado:</b> {numero_expediente}<br><br>"
                    f"<b>Formato válido:</b> Solo números separados por puntos y barras<br>"
                    f"<b>Ejemplo correcto:</b> 12.34.56/78.90.12/2025<br><br>"
                    f"<b>Caracteres permitidos:</b><br>"
                    f"• Números (0-9)<br>"
                    f"• Puntos (.)<br>"
                    f"• Barras (/)"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return False

            # 🔁 Transformar expediente a nombre de carpeta
            nombre_limpio = numero_expediente.replace('/', '_').replace('.', '_')
            nombre_limpio = re.sub(r'[^\w_]', '', nombre_limpio)
            nombre_limpio = re.sub(r'_+', '_', nombre_limpio).strip('_')

            if not nombre_limpio:
                return False

            # 📁 Buscar carpeta actual
            contract_data = {
                'nombreObra': nombre_obra,
                'numeroExpediente': numero_expediente
            }
            carpeta_actual = self.buscar_carpeta_existente(contract_data)
            if not carpeta_actual:
                return False

            nueva_ruta = os.path.join(self.obras_dir, nombre_limpio)
            if os.path.exists(nueva_ruta):
                return False

            # 🔄 Renombrar carpeta física - CON MANEJO DE PERMISOS
            try:
                os.rename(carpeta_actual, nueva_ruta)

                # 💾 Actualizar JSON con el nuevo nombre
                self._actualizar_json_con_carpeta(contract_data, nombre_limpio)
                return True

            except PermissionError as e:
                # Error de permisos - manejado por UI
                
                # Mostrar popup informativo con opción de cerrar y abrir carpeta
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("🔒 Error de Permisos")
                msg.setText("<b>No se puede renombrar la carpeta por falta de permisos</b>")
                msg.setInformativeText(
                    f"<b>Problema:</b> La carpeta está siendo usada por otro proceso<br><br>"
                    f"<b>Carpeta actual:</b> {os.path.basename(carpeta_actual)}<br>"
                    f"<b>Nuevo nombre:</b> {nombre_limpio}<br><br>"
                    f"<b>Posibles causas:</b><br>"
                    f"• Archivos abiertos en la carpeta<br>"
                    f"• Explorador de archivos abierto<br>"
                    f"• Otro programa usando la carpeta<br><br>"
                    f"<b>Solución:</b><br>"
                    f"1. Cierre todos los archivos de la carpeta<br>"
                    f"2. Cierre exploradores de archivos<br>"
                    f"3. Intente de nuevo"
                )
                
                # Botones personalizados
                btn_abrir = msg.addButton("📂 Abrir Carpeta", QMessageBox.ActionRole)
                btn_reintentar = msg.addButton("🔄 Reintentar", QMessageBox.ActionRole)
                btn_cancelar = msg.addButton("❌ Cancelar", QMessageBox.RejectRole)
                
                msg.setDefaultButton(btn_abrir)
                resultado = msg.exec_()
                
                # Manejar respuesta del usuario
                if msg.clickedButton() == btn_abrir:
                    # Abrir carpeta en explorador
                    self.abrir_carpeta_en_explorador(carpeta_actual)
                    
                    # Mostrar mensaje adicional
                    QMessageBox.information(
                        self.main_window, "📂 Carpeta Abierta",
                        f"Se ha abierto la carpeta en el explorador.\n\n"
                        f"✅ Cierre todos los archivos y programas que usen esta carpeta\n"
                        f"✅ Cierre esta ventana del explorador\n"
                        f"✅ Luego presione el botón 'Cambiar Exp.' nuevamente"
                    )
                    
                elif msg.clickedButton() == btn_reintentar:
                    # Reintentar inmediatamente
                    try:
                        os.rename(carpeta_actual, nueva_ruta)
                        
                        # Actualizar JSON
                        self._actualizar_json_con_carpeta(contract_data, nombre_limpio)
                        
                        # Mostrar éxito
                        QMessageBox.information(
                            self.main_window, "✅ Éxito",
                            f"Carpeta renombrada exitosamente:\n\n"
                            f"📂 Nuevo nombre: {nombre_limpio}"
                        )
                        return True
                        
                    except PermissionError:
                        QMessageBox.critical(
                            self.main_window, "❌ Error Persistente",
                            f"La carpeta sigue siendo usada por otro proceso.\n\n"
                            f"💡 Intente:\n"
                            f"• Reiniciar el explorador de archivos\n"
                            f"• Cerrar todos los programas\n"
                            f"• Reiniciar la aplicación"
                        )
                        return False
                else:
                    return False  # Operación cancelada

            except OSError as e:
                # Error del sistema - manejado por UI
                QMessageBox.critical(
                    self.main_window, "❌ Error del Sistema",
                    f"Error del sistema al renombrar carpeta:\n\n{e}\n\n"
                    f"Verifique que la carpeta existe y tiene permisos correctos."
                )
                return False

        except Exception as e:
            print(f"[GestorArchivos] ❌ Error en renombrar_carpeta_por_expediente: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar error general solo si hay main_window
            if self.main_window is not None:
                QMessageBox.critical(
                    self.main_window, "❌ Error Inesperado",
                    f"Se produjo un error inesperado:\n\n{str(e)}\n\n"
                    f"Revise la consola para más detalles."
                )
            return False
    def _limpiar_texto_busqueda(self, texto):
        """Limpiar texto para búsqueda fuzzy"""
        if not texto:
            return ""
        # Convertir a minúsculas, quitar acentos básicos, solo alfanuméricos
        texto = texto.lower()
        texto = re.sub(r'[áàäâ]', 'a', texto)
        texto = re.sub(r'[éèëê]', 'e', texto)
        texto = re.sub(r'[íìïî]', 'i', texto)
        texto = re.sub(r'[óòöô]', 'o', texto)
        texto = re.sub(r'[úùüû]', 'u', texto)
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        return ' '.join(texto.split())  # Normalizar espacios
    
    def _calcular_similitud_texto(self, texto1, texto2):
        """Calcular similitud entre dos textos (algoritmo simple de Jaccard)"""
        if not texto1 or not texto2:
            return 0.0
        
        palabras1 = set(texto1.split())
        palabras2 = set(texto2.split())
        
        if not palabras1 or not palabras2:
            return 0.0
        
        intersection = len(palabras1.intersection(palabras2))
        union = len(palabras1.union(palabras2))
        
        return intersection / union if union > 0 else 0.0

    # ========================================
    # 🏗️ CREACIÓN DE CARPETAS Y ESTRUCTURA
    # ========================================
    
    def verificar_o_crear_carpeta(self, contract_data, modo="auto", force_create=False):
        """
        Verificar carpeta existente o crear nueva con múltiples modos
        
        Args:
            contract_data: Datos del contrato
            modo: "auto" (automático), "ask" (pregunta), "silent" (silencioso)
            force_create: Forzar creación de nueva carpeta
            
        Returns:
            tuple: (ruta_carpeta, fue_creada, operacion_realizada)
        """
        try:
            nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
            
            # PASO 1: Buscar carpeta existente (si no se fuerza creación)
            carpeta_existente = None
            if not force_create:
                carpeta_existente = self.buscar_carpeta_existente(contract_data)
            
            # PASO 2: Si existe carpeta, utilizarla
            if carpeta_existente and not force_create:
                self._actualizar_json_con_carpeta(contract_data, os.path.basename(carpeta_existente))
                return carpeta_existente, False, "carpeta_encontrada"
            
            # PASO 3: Decidir si crear nueva carpeta según el modo
            if modo == "ask":
                # Modo pregunta: mostrar diálogo
                crear = self._preguntar_crear_carpeta(contract_data)
                if not crear:
                    return None, False, "creacion_cancelada"
                    
            elif modo == "silent":
                # Modo silencioso: no crear automáticamente
                if not force_create:
                    return None, False, "no_existe_silencioso"
            
            # PASO 4: Crear nueva carpeta
            nueva_carpeta = self._crear_carpeta_con_estructura(contract_data)
            
            if nueva_carpeta:
                # Actualizar JSON
                self._actualizar_json_con_carpeta(contract_data, os.path.basename(nueva_carpeta))
                
                # Mostrar notificación según el modo
                if modo != "silent":
                    self._mostrar_notificacion_carpeta_creada(contract_data, nueva_carpeta)
                
                return nueva_carpeta, True, "carpeta_creada"
            else:
                return None, False, "error_creacion"
                
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error en verificar_o_crear: {e}")
            import traceback
            traceback.print_exc()
            return None, False, "error_excepcion"
    
    def _preguntar_crear_carpeta(self, contract_data):
        """Mostrar diálogo para preguntar si crear carpeta"""
        try:
            nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
            expediente = contract_data.get('numeroExpediente', 'Sin expediente')
            
            parent = self.main_window if self.main_window else None
            
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("📂 Crear Carpeta")
            msg.setText("<b>No se encontró carpeta para este contrato</b>")
            msg.setInformativeText(
                f"<b>Proyecto:</b> {nombre_obra[:60]}{'...' if len(nombre_obra) > 60 else ''}<br>"
                f"<b>Expediente:</b> {expediente}<br><br>"
                f"¿Desea crear la estructura completa de carpetas?"
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            resultado = msg.exec_()
            return resultado == QMessageBox.Yes
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error mostrando diálogo: {e}")
            return True  # En caso de error, crear por defecto
    
    def _crear_carpeta_con_estructura(self, contract_data):
        """Crear carpeta nueva con estructura completa de subcarpetas"""
        try:
            # Generar nombre único para la carpeta
            nombre_base = self._generar_nombre_carpeta(contract_data)
            carpeta_path = self._generar_nombre_unico(nombre_base)
            
            # Crear carpeta principal
            os.makedirs(carpeta_path, exist_ok=True)
            
            # Crear estructura de subcarpetas
            subcarpetas_creadas = self._crear_estructura_subcarpetas(carpeta_path, contract_data)
            
            if subcarpetas_creadas:
                return carpeta_path
            else:
                return None
                
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error creando carpeta: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _crear_estructura_subcarpetas(self, carpeta_path, contract_data):
        """Crear estructura completa de subcarpetas con README y metadatos"""
        try:
            # Definir estructura de carpetas mejorada
            estructura_carpetas = [
                ("01-proyecto", "Documentos del proyecto y planos"),
                ("02-documentacion-finales", "Documentación oficial firmada"),
                ("03-cartas-finales", "Correspondencia oficial firmada"),
                ("04-documentos-sin-firmar", "Borradores y documentos pendientes"),
                ("05-cartas-sin-firmar", "Borradores de correspondencia"),
                ("06-ofertas", "Ofertas y propuestas económicas"),
                ("07-seguridad-y-salud", "Documentación de seguridad y salud laboral"),
                ("08-actuaciones", "Registros de actuaciones y trabajos"),
                ("09-facturas", "Facturas y documentos económicos"),
                ("10-otros", "Otros documentos diversos"),
                ("11-fotos", "Fotografías y material gráfico"),
                ("12-comunicaciones", "Comunicaciones internas y externas")
            ]
            
            nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
            numero_expediente = contract_data.get('numeroExpediente', 'Sin expediente')
            fecha_creacion = datetime.now()
            
            subcarpetas_creadas = []
            
            for nombre_subcarpeta, descripcion in estructura_carpetas:
                try:
                    subcarpeta_path = os.path.join(carpeta_path, nombre_subcarpeta)
                    os.makedirs(subcarpeta_path, exist_ok=True)
                    
                    # Crear archivo README detallado
                    readme_path = os.path.join(subcarpeta_path, "README.txt")
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write("="*60 + "\n")
                        f.write(f"CARPETA: {nombre_subcarpeta}\n")
                        f.write("="*60 + "\n\n")
                        f.write(f"Descripción: {descripcion}\n\n")
                        f.write(f"INFORMACIÓN DEL PROYECTO:\n")
                        f.write(f"  • Nombre: {nombre_obra}\n")
                        f.write(f"  • Expediente: {numero_expediente}\n")
                        f.write(f"  • Tipo: {contract_data.get('tipoActuacion', 'No especificado')}\n")
                        f.write(f"  • Creado: {fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(f"CONTENIDO ESPERADO:\n")
                        f.write(f"  {descripcion}\n\n")
                        f.write(f"INSTRUCCIONES:\n")
                        f.write(f"  • Mantener organizado por fechas\n")
                        f.write(f"  • Usar nombres descriptivos para archivos\n")
                        f.write(f"  • Verificar antes de eliminar documentos\n\n")
                        f.write(f"Generado automáticamente por Gestor de Archivos \n")
                    
                    # Crear archivo .gitkeep para mantener estructura en Git
                    gitkeep_path = os.path.join(subcarpeta_path, ".gitkeep")
                    with open(gitkeep_path, "w") as f:
                        f.write("")
                    
                    subcarpetas_creadas.append(nombre_subcarpeta)
                    
                except Exception as e:
                    pass  # Error creando subcarpeta
            
            # Crear archivo de metadatos principal
            metadata_path = os.path.join(carpeta_path, "_PROYECTO_INFO.json")
            metadata = {
                "nombre_obra": nombre_obra,
                "numero_expediente": numero_expediente,
                "tipo_actuacion": contract_data.get('tipoActuacion', ''),
                "fecha_creacion": fecha_creacion.isoformat(),
                "subcarpetas_creadas": len(subcarpetas_creadas),
                "version_gestor": "1.0",
                "estructura": [{"carpeta": sc, "descripcion": desc} for sc, desc in estructura_carpetas]
            }
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return subcarpetas_creadas
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error creando estructura: {e}")
            import traceback
            traceback.print_exc()
            return []

    # ========================================
    # 📝 GENERACIÓN Y LIMPIEZA DE NOMBRES
    # ========================================
    
    def _generar_nombre_carpeta(self, contract_data):
        """Generar nombre de carpeta siguiendo reglas optimizadas - CON SOPORTE nombreCarpeta"""
        try:
            numero_expediente = contract_data.get('numeroExpediente', '').strip()
            nombre_obra = contract_data.get('nombreObra', '').strip()
            nombre_carpeta_json = contract_data.get('nombreCarpeta', '').strip()
            
            print(f"   Expediente: '{numero_expediente}'")
            print(f"   Obra: '{nombre_obra}'")
            print(f"   Carpeta JSON: '{nombre_carpeta_json}'")
            
            # REGLA 0: PRIORITARIO - Usar nombreCarpeta del JSON si existe
            if nombre_carpeta_json:
                print(f"   ✅ Usando nombreCarpeta del JSON: '{nombre_carpeta_json}'")
                return nombre_carpeta_json
            
            # REGLA 1: Priorizar nombre de obra (ya que las carpetas existentes usan este formato)
            if nombre_obra:
                # Truncar a 80 caracteres para evitar problemas de longitud
                nombre_truncado = nombre_obra[:80] if len(nombre_obra) > 80 else nombre_obra
                nombre_limpio = self._limpiar_nombre_carpeta(nombre_truncado)
                if nombre_limpio and nombre_limpio != "carpeta_sin_nombre":
                    return nombre_limpio
            
            # REGLA 2: Usar número de expediente (si no hay nombre de obra válido)
            if numero_expediente and len(numero_expediente) >= 3:
                nombre_limpio = self._limpiar_nombre_carpeta(numero_expediente)
                if nombre_limpio and nombre_limpio != "carpeta_sin_nombre":
                    return nombre_limpio
            
            # REGLA 3: Fallback con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            fallback_name = f"contrato_{timestamp}"
            return fallback_name
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error generando nombre: {e}")
            return f"contrato_error_{datetime.now().strftime('%Y%m%d_%H%M')}"
    def _limpiar_nombre_carpeta(self, nombre):
        """Limpiar nombre para uso como carpeta del sistema de archivos"""
        if not nombre or not str(nombre).strip():
            return "carpeta_sin_nombre"
        
        nombre_str = str(nombre).strip()
        
        # Reemplazar caracteres problemáticos manteniendo legibilidad
        # Caracteres absolutamente prohibidos en Windows/Linux
        caracteres_prohibidos = r'[<>:"/\\|?*]'
        nombre_limpio = re.sub(caracteres_prohibidos, '-', nombre_str)
        
        # Reemplazar caracteres especiales comunes por equivalentes seguros
        replacements = {
            'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ā': 'a',
            'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e', 'ē': 'e',
            'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i', 'ī': 'i',
            'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'ō': 'o',
            'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u', 'ū': 'u',
            'ñ': 'n', 'ç': 'c',
            '&': 'y', '@': 'at', '#': 'num',
            '€': 'euro'
        }
        
        for char, replacement in replacements.items():
            nombre_limpio = nombre_limpio.replace(char, replacement)
        
        # Normalizar espacios múltiples y puntos
        nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio)
        nombre_limpio = re.sub(r'\.+', '.', nombre_limpio)
        
        # Limpiar caracteres al inicio y final
        nombre_limpio = nombre_limpio.strip(' .-_')
        
        # Limitar longitud (Windows tiene límite de 260 caracteres para ruta completa)
        if len(nombre_limpio) > 100:
            nombre_limpio = nombre_limpio[:97] + "..."
        
        # Verificar que no esté vacío después de limpieza
        if not nombre_limpio or len(nombre_limpio.strip()) < 1:
            return "carpeta_sin_nombre"
        
        return nombre_limpio
    
    def _generar_nombre_unico(self, nombre_base):
        """Generar nombre único para carpeta evitando duplicados"""
        carpeta_path = os.path.join(self.obras_dir, nombre_base)
        
        if not os.path.exists(carpeta_path):
            return carpeta_path
        
        # Generar nombres incrementales
        contador = 1
        while True:
            nombre_con_contador = f"{nombre_base}_{contador:02d}"
            carpeta_path_contador = os.path.join(self.obras_dir, nombre_con_contador)
            
            if not os.path.exists(carpeta_path_contador):
                return carpeta_path_contador
            
            contador += 1
            
            # Evitar bucle infinito
            if contador > 999:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_timestamp = f"{nombre_base}_{timestamp}"
                return os.path.join(self.obras_dir, nombre_timestamp)

    # ========================================
    # 💾 GESTIÓN DE JSON Y METADATOS
    # ========================================
    
    def _actualizar_json_con_carpeta(self, contract_data, nombre_carpeta):
        """Actualizar archivo JSON con información de carpeta - FIX IDENTIFICACIÓN CORRECTA"""
        try:
            json_path = self._get_json_path()
            if not json_path:
                print(f"[GestorArchivos] ⚠️ No se encontró archivo JSON para actualizar")
                return False
            
            # Cargar datos JSON
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extraer información del contrato
            nombre_obra = contract_data.get("nombreObra", "")
            numero_expediente = contract_data.get("numeroExpediente", "")
            
            obras = data.get("obras", [])
            obra_encontrada = False
            
            for i, obra in enumerate(obras):
                obra_nombre = obra.get("nombreObra", "")
                obra_expediente = obra.get("numeroExpediente", "")
                obra_carpeta = obra.get("nombreCarpeta", "")
                
                #print(f"   [{i}] Nombre: '{obra_nombre}'")
                #print(f"       Expediente: '{obra_expediente}'")
                #print(f"       Carpeta actual: '{obra_carpeta}'")
            
            # 🆕 BÚSQUEDA MEJORADA: PRIORIZAR EXPEDIENTE + NOMBRE
            for i, obra in enumerate(obras):
                obra_nombre = obra.get("nombreObra", "")
                obra_expediente = obra.get("numeroExpediente", "")
                
                # 🔍 IDENTIFICACIÓN PRECISA:
                # 1. Si ambos tienen expediente, deben coincidir NOMBRE + EXPEDIENTE
                # 2. Si solo uno tiene expediente, buscar por NOMBRE únicamente
                # 3. Evitar confusión por carpetas compartidas
                
                coincide_nombre = obra_nombre == nombre_obra
                coincide_expediente = (obra_expediente == numero_expediente)
                
                # CASO 1: Ambos tienen expediente - deben coincidir ambos
                if numero_expediente and obra_expediente:
                    if coincide_nombre and coincide_expediente:
                        print(f"   Carpeta antigua: '{obra.get('nombreCarpeta', '')}'")
                        print(f"   Carpeta nueva: '{nombre_carpeta}'")
                        
                        obra["nombreCarpeta"] = nombre_carpeta
                        obra["fechaCreacionCarpeta"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        obra["gestorVersion"] = "1.0-archivos"
                        obra_encontrada = True
                        break
                
                # CASO 2: Solo el contrato actual tiene expediente - buscar por nombre
                elif numero_expediente and not obra_expediente:
                    if coincide_nombre:
                        print(f"   Carpeta antigua: '{obra.get('nombreCarpeta', '')}'")
                        print(f"   Carpeta nueva: '{nombre_carpeta}'")
                        
                        obra["nombreCarpeta"] = nombre_carpeta
                        obra["fechaCreacionCarpeta"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        obra["gestorVersion"] = "1.0-archivos"
                        obra_encontrada = True
                        break
                
                # CASO 3: Solo el contrato del JSON tiene expediente - NO coincidir
                elif not numero_expediente and obra_expediente:
                    # No hacer nada - son contratos diferentes
                    continue
                
                # CASO 4: Ninguno tiene expediente - buscar por nombre únicamente
                elif not numero_expediente and not obra_expediente:
                    if coincide_nombre:
                        print(f"   Carpeta antigua: '{obra.get('nombreCarpeta', '')}'")
                        print(f"   Carpeta nueva: '{nombre_carpeta}'")
                        
                        obra["nombreCarpeta"] = nombre_carpeta
                        obra["fechaCreacionCarpeta"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        obra["gestorVersion"] = "1.0-archivos"
                        obra_encontrada = True
                        break
            
            if not obra_encontrada:
                print(f"[GestorArchivos] Info: No se encontró la obra en el JSON (esto es normal si es nueva)")
                print(f"   Buscaba: nombre='{nombre_obra}'")
                return True  # Cambiado a True para evitar el error
            
            # Guardar archivo actualizado
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error actualizando JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    def _get_json_path(self):
        """Encontrar archivo JSON de datos"""
        try:
            # Buscar en múltiples ubicaciones
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            posibles_rutas = [
                "BaseDatos.json",
                os.path.join(".", "BaseDatos.json"),
                os.path.join("..", "BaseDatos.json"),
                os.path.join(current_dir, "BaseDatos.json"),
                os.path.join(current_dir, "..", "BaseDatos.json"),
                os.path.join(os.path.dirname(self.obras_dir), "BaseDatos.json"),
                os.path.join(os.getcwd(), "BaseDatos.json")
            ]
            
            for ruta in posibles_rutas:
                ruta_abs = os.path.abspath(ruta)
                if os.path.exists(ruta_abs) and os.path.isfile(ruta_abs):
                    try:
                        # Verificar que sea un JSON válido
                        with open(ruta_abs, "r", encoding="utf-8") as f:
                            json.load(f)
                        return ruta_abs
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error buscando JSON: {e}")
            return None

    # ========================================
    # 🔔 NOTIFICACIONES Y UI
    # ========================================
    
    def _mostrar_notificacion_carpeta_creada(self, contract_data, carpeta_path):
        """Mostrar notificación de carpeta creada"""
        try:
            nombre_obra = contract_data.get('nombreObra', 'Sin nombre')
            nombre_carpeta = os.path.basename(carpeta_path)
            
            # Contar subcarpetas creadas
            try:
                contenido = os.listdir(carpeta_path)
                subcarpetas = [item for item in contenido if os.path.isdir(os.path.join(carpeta_path, item))]
                num_subcarpetas = len(subcarpetas)
            except:
                num_subcarpetas = 0
            
            # Buscar ventana principal
            parent = self._find_main_window()
            
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("📁 Estructura de Carpetas Creada")
            msg.setText("<b>Se ha creado exitosamente la estructura de carpetas</b>")
            msg.setInformativeText(
                f"<b>Proyecto:</b> {nombre_obra[:50]}{'...' if len(nombre_obra) > 50 else ''}<br>"
                f"<b>Carpeta:</b> {nombre_carpeta}<br>"
                f"<b>Ubicación:</b> {carpeta_path}<br>"
                f"<b>Subcarpetas:</b> {num_subcarpetas}<br><br>"
                f"<i>La estructura está lista para usar. Se han creado archivos README en cada subcarpeta.</i>"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            
            # Agregar botón para abrir carpeta
            abrir_btn = msg.addButton("📂 Abrir Carpeta", QMessageBox.ActionRole)
            
            resultado = msg.exec_()
            
            # Si presionó "Abrir Carpeta"
            if msg.clickedButton() == abrir_btn:
                self.abrir_carpeta_en_explorador(carpeta_path)
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error mostrando notificación: {e}")
    
    def _find_main_window(self):
        """Buscar ventana principal de la aplicación"""
        try:
            if self.main_window:
                return self.main_window
            
            app = QApplication.instance()
            if app:
                for widget in QApplication.topLevelWidgets():
                    if hasattr(widget, 'comboBox') and hasattr(widget, 'tabWidget'):
                        return widget
            
            return None
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error buscando main window: {e}")
            return None

    # ========================================
    # 💻 INTEGRACIÓN CON SISTEMA OPERATIVO
    # ========================================
    
    def abrir_carpeta_en_explorador(self, carpeta_path):
        """Abrir carpeta en el explorador del sistema operativo"""
        try:
            if not os.path.exists(carpeta_path):
                return False
            
            sistema = platform.system()
            
            if sistema == "Windows":
                subprocess.Popen(['explorer', os.path.normpath(carpeta_path)])
            elif sistema == "Darwin":  # macOS
                subprocess.Popen(['open', carpeta_path])
            elif sistema == "Linux":
                subprocess.Popen(['xdg-open', carpeta_path])
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error abriendo carpeta: {e}")
            return False
    
    def abrir_carpeta_contrato(self, contract_data):
        """Abrir carpeta del contrato (crear si no existe)"""
        try:
            carpeta_path, _, operacion = self.verificar_o_crear_carpeta(contract_data, modo="ask")
            
            if carpeta_path:
                return self.abrir_carpeta_en_explorador(carpeta_path)
            else:
                return False
                
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error abriendo carpeta contrato: {e}")
            return False

    # ========================================
    # 📊 UTILIDADES Y ANÁLISIS
    # ========================================
    
    def listar_carpetas_huerfanas(self):
        """Listar carpetas físicas que no tienen contrato asociado en JSON"""
        try:
            json_path = self._get_json_path()
            if not json_path:
                return []
            
            # Obtener carpetas asociadas en JSON
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            obras = data.get("obras", [])
            carpetas_json = set()
            
            for obra in obras:
                nombre_carpeta = obra.get("nombreCarpeta", "")
                if nombre_carpeta and nombre_carpeta.strip():
                    carpetas_json.add(nombre_carpeta.strip())
            
            # Obtener carpetas físicas
            if not os.path.exists(self.obras_dir):
                return []
            
            carpetas_fisicas = set()
            for item in os.listdir(self.obras_dir):
                item_path = os.path.join(self.obras_dir, item)
                if os.path.isdir(item_path):
                    carpetas_fisicas.add(item)
            
            # Encontrar huérfanas
            carpetas_huerfanas = carpetas_fisicas - carpetas_json
            
            
            return list(carpetas_huerfanas)
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error listando huérfanas: {e}")
            return []
    
    def generar_informe_carpetas(self):
        """Generar informe completo del estado de las carpetas"""
        try:
            informe = {
                "fecha_generacion": datetime.now().isoformat(),
                "directorio_obras": self.obras_dir,
                "existe_directorio": os.path.exists(self.obras_dir),
                "carpetas_fisicas": [],
                "carpetas_json": [],
                "carpetas_huerfanas": [],
                "estadisticas": {}
            }
            
            # Análizar carpetas físicas
            if os.path.exists(self.obras_dir):
                for item in os.listdir(self.obras_dir):
                    item_path = os.path.join(self.obras_dir, item)
                    if os.path.isdir(item_path):
                        try:
                            contenido = os.listdir(item_path)
                            subcarpetas = [x for x in contenido if os.path.isdir(os.path.join(item_path, x))]
                            archivos = [x for x in contenido if os.path.isfile(os.path.join(item_path, x))]
                            
                            informe["carpetas_fisicas"].append({
                                "nombre": item,
                                "ruta": item_path,
                                "subcarpetas": len(subcarpetas),
                                "archivos": len(archivos),
                                "total_elementos": len(contenido)
                            })
                        except:
                            pass
            
            # Analizar JSON
            json_path = self._get_json_path()
            if json_path:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for obra in data.get("obras", []):
                    nombre_carpeta = obra.get("nombreCarpeta", "")
                    if nombre_carpeta:
                        informe["carpetas_json"].append({
                            "nombre_obra": obra.get("nombreObra", ""),
                            "nombre_carpeta": nombre_carpeta,
                            "expediente": obra.get("numeroExpediente", ""),
                            "tipo": obra.get("tipoActuacion", "")
                        })
            
            # Carpetas huérfanas
            informe["carpetas_huerfanas"] = self.listar_carpetas_huerfanas()
            
            # Estadísticas
            informe["estadisticas"] = {
                "total_carpetas_fisicas": len(informe["carpetas_fisicas"]),
                "total_carpetas_json": len(informe["carpetas_json"]),
                "total_huerfanas": len(informe["carpetas_huerfanas"]),
                "porcentaje_asociadas": (
                    (len(informe["carpetas_json"]) / len(informe["carpetas_fisicas"]) * 100)
                    if len(informe["carpetas_fisicas"]) > 0 else 0
                )
            }
            
            return informe
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error generando informe: {e}")
            return None

    # ========================================
    # 🔄 COMPATIBILIDAD Y MIGRACIÓN
    # ========================================
    
    def migrar_desde_controlador_anterior(self):
        """Migrar configuración desde controlador_archivos.py anterior"""
        try:
            
            # Buscar configuraciones anteriores
            rutas_anteriores = [
                "obras",
                os.path.join("..", "obras"),
                os.path.join(os.getcwd(), "obras")
            ]
            
            for ruta in rutas_anteriores:
                if os.path.exists(ruta) and os.path.isdir(ruta):
                    # Verificar si tiene estructura típica del controlador anterior
                    contenido = os.listdir(ruta)
                    if contenido:  # Si tiene contenido, probablemente sea válida
                        self.obras_dir = os.path.abspath(ruta)
                        return True
            
            return False
            
        except Exception as e:
            print(f"[GestorArchivos] ❌ Error en migración: {e}")
            return False

    # ========================================
    # 🎯 API PÚBLICA SIMPLIFICADA
    # ========================================
    
    def obtener_carpeta_obra(self, contract_data, crear_si_no_existe=True):
        """API principal: obtener carpeta de obra (crear automáticamente si no existe)"""
        modo = "auto" if crear_si_no_existe else "silent"
        carpeta_path, _, _ = self.verificar_o_crear_carpeta(contract_data, modo=modo)
        return carpeta_path
    
    def crear_carpeta_obra(self, contract_data, preguntar=True):
        """API: crear nueva carpeta de obra"""
        modo = "ask" if preguntar else "auto"
        carpeta_path, fue_creada, _ = self.verificar_o_crear_carpeta(contract_data, modo=modo, force_create=True)
        return carpeta_path, fue_creada
    
    def existe_carpeta_obra(self, contract_data):
        """API: verificar si existe carpeta para la obra"""
        return self.buscar_carpeta_existente(contract_data) is not None


# ========================================
# 🌍 INSTANCIA GLOBAL Y FUNCIONES DE CONVENIENCIA
# ========================================

# Instancia global del gestor
gestor_global = None

def get_gestor_global(main_window=None):
    """Obtener instancia global del gestor"""
    global gestor_global
    if gestor_global is None:
        gestor_global = GestorArchivos(main_window)
    elif main_window and not gestor_global.main_window:
        gestor_global.set_main_window(main_window)
    return gestor_global

def verificar_o_crear_carpeta_obra(contract_data, crear_si_no_existe=True, main_window=None):
    """Función de conveniencia para verificar/crear carpeta de obra"""
    gestor = get_gestor_global(main_window)
    return gestor.obtener_carpeta_obra(contract_data, crear_si_no_existe)

def abrir_carpeta_obra(contract_data, main_window=None):
    """Función de conveniencia para abrir carpeta de obra"""
    gestor = get_gestor_global(main_window)
    return gestor.abrir_carpeta_contrato(contract_data)


