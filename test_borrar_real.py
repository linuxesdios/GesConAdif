import os
import shutil

# Función real de borrado (la misma que está en controlador_grafica.py)
def borrar_carpeta_obra(nombre_contrato, datos_contrato=None):
    """Borrar carpeta física de la obra buscando por nombre de obra o expediente"""
    try:
        print(f"[DEBUG] Intentando borrar carpeta para: {nombre_contrato}")
        print(f"[DEBUG] Datos contrato: {datos_contrato}")
        
        carpetas_a_buscar = [nombre_contrato]
        
        if datos_contrato and 'numeroExpediente' in datos_contrato:
            expediente = datos_contrato['numeroExpediente']
            if expediente and expediente.strip():
                carpetas_a_buscar.append(expediente.strip())
        
        print(f"[DEBUG] Carpetas a buscar: {carpetas_a_buscar}")
        
        carpeta_obras = os.path.join(os.getcwd(), "obras")
        print(f"[DEBUG] Buscando en: {carpeta_obras}")
        
        if not os.path.exists(carpeta_obras):
            print(f"[DEBUG] No existe la carpeta obras: {carpeta_obras}")
            return
        
        # Listar todas las carpetas disponibles
        carpetas_disponibles = [d for d in os.listdir(carpeta_obras) if os.path.isdir(os.path.join(carpeta_obras, d))]
        print(f"[DEBUG] Carpetas disponibles: {carpetas_disponibles}")
        
        for nombre_carpeta in carpetas_a_buscar:
            ruta_carpeta = os.path.join(carpeta_obras, nombre_carpeta)
            print(f"[DEBUG] Verificando: {ruta_carpeta}")
            if os.path.exists(ruta_carpeta):
                shutil.rmtree(ruta_carpeta)
                print(f"[DEBUG] OK - Carpeta borrada: {ruta_carpeta}")
                return
        
        print(f"[DEBUG] ERROR - No se encontró carpeta para: {carpetas_a_buscar}")
        
    except Exception as e:
        print(f"[DEBUG] Error borrando carpeta: {e}")

# Test real de borrado
print("=== TEST REAL: Borrar carpeta 'test_borrar' ===")
borrar_carpeta_obra("test_borrar")

print("\n=== Verificar que se borró ===")
carpeta_obras = os.path.join(os.getcwd(), "obras")
carpetas_disponibles = [d for d in os.listdir(carpeta_obras) if os.path.isdir(os.path.join(carpeta_obras, d))]
if "test_borrar" in carpetas_disponibles:
    print("ERROR: La carpeta NO se borró")
else:
    print("OK: La carpeta se borró correctamente")