import os
import shutil

def test_borrar_carpeta_obra(nombre_contrato, datos_contrato=None):
    """Test de borrar carpeta física de la obra buscando por nombre de obra o expediente"""
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
                print(f"[DEBUG] OK - Se encontró carpeta: {ruta_carpeta}")
                # En lugar de borrar, solo mostramos que se encontró
                print(f"[DEBUG] SE BORRARIA: {nombre_carpeta}")
                return True
        
        print(f"[DEBUG] ERROR - No se encontró carpeta para: {carpetas_a_buscar}")
        return False
        
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return False

# Pruebas
print("=== TEST 1: Buscar carpeta 'teste' ===")
result1 = test_borrar_carpeta_obra("teste")

print("\n=== TEST 2: Buscar con datos de expediente ===")  
datos_fake = {"numeroExpediente": "2332"}
result2 = test_borrar_carpeta_obra("no_existe", datos_fake)

print("\n=== TEST 3: Buscar 'averia' ===")
result3 = test_borrar_carpeta_obra("averia")