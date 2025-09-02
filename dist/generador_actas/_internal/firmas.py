#!/usr/bin/env python3
import PyPDF2
from datetime import datetime

def obtener_firmas_pdf(pdf_path):
    """
    Extrae todas las firmas digitales de un PDF
    
    Args:
        pdf_path (str): Ruta al archivo PDF
    
    Returns:
        list: Lista de diccionarios con formato:
              [{"firmante": "nombre", "fecha": "dd/mm/yyyy hh:mm:ss"}, ...]
    """
    
    def parse_pdf_date(pdf_date):
        """Convierte fecha PDF a formato legible"""
        try:
            if pdf_date.startswith('D:'):
                date_part = pdf_date[2:16]
                year = int(date_part[0:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                hour = int(date_part[8:10])
                minute = int(date_part[10:12])
                second = int(date_part[12:14])
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            pass
        return pdf_date

    def extract_name_from_cert(contents):
        """Extrae nombre del certificado"""
        try:
            from cryptography.hazmat.primitives.serialization import pkcs7
            from cryptography import x509
            import warnings
            import binascii
            
            if isinstance(contents, str):
                cert_data = binascii.unhexlify(contents)
            else:
                cert_data = contents
            
            # Extraer nombre del certificado
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    p7 = pkcs7.load_der_pkcs7_certificates(cert_data)
                
                if p7:
                    cert = p7[0]
                    for attribute in cert.subject:
                        if attribute.oid == x509.oid.NameOID.COMMON_NAME:
                            name = attribute.value
                            if len(name) > 5 and any(c.isspace() for c in name):
                                return name
            except:
                pass
            
            # Buscar DNI si no hay nombre
            try:
                texts = []
                for encoding in ['utf-8', 'latin1', 'cp1252']:
                    try:
                        text = cert_data.decode(encoding, errors='ignore')
                        texts.append(text.upper())
                    except:
                        continue
                
                full_text = ' '.join(texts)
                
                import re
                dni_pattern = r'\b(\d{8}[A-Z])\b'
                dni_matches = re.findall(dni_pattern, full_text)
                
                if dni_matches:
                    return dni_matches[0]
                
            except:
                pass
            
            return "Sin identificar"
            
        except Exception as e:
            return f"Error: {str(e)[:20]}"

    # Función principal
    firmas = []
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            if '/AcroForm' not in reader.trailer['/Root']:
                return firmas
                
            acroform = reader.trailer['/Root']['/AcroForm']
            
            if '/Fields' not in acroform:
                return firmas
                
            fields = acroform['/Fields']
            
            for field_ref in fields:
                field = field_ref.get_object()
                
                if '/FT' in field and field['/FT'] == '/Sig':
                    if '/V' in field:
                        sig_dict = field['/V'].get_object()
                        
                        # Extraer fecha
                        date = sig_dict.get('/M', 'Fecha no disponible')
                        fecha_formateada = parse_pdf_date(date)
                        
                        # Extraer firmante
                        firmante = "Sin identificar"
                        if '/Contents' in sig_dict:
                            contents = sig_dict['/Contents']
                            firmante = extract_name_from_cert(contents)
                        
                        # Añadir a la lista
                        firmas.append({
                            "firmante": firmante,
                            "fecha": fecha_formateada
                        })
                        
    except Exception as e:
        print(f"Error leyendo PDF: {e}")
        
    return firmas

# Ejemplo de uso
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python script.py archivo.pdf")
        sys.exit(1)
    
    # Test de la función
    firmas = obtener_firmas_pdf(sys.argv[1])
    
    if firmas:
        print("Firmas encontradas:")
        for i, firma in enumerate(firmas, 1):
            print(f"  {i}. {firma['firmante']} - {firma['fecha']}")
    else:
        print("No se encontraron firmas")