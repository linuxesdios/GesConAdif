import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_json_basico():
    import tempfile
    import json
    from datetime import datetime
    
    try:
        factura_data = {
            "id": 1, 
            "empresa": "Test Corp",
            "importe": 1500.50,
            "estado": "Emitida"
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"facturas": [factura_data]}, f)
            json_file = f.name
        
        with open(json_file, "r") as f:
            data = json.load(f)
        
        os.unlink(json_file)
        assert "facturas" in data
        assert len(data["facturas"]) == 1
        print("PASSED: JSON test")
        assert True  # Test passed
    except Exception as e:
        print(f"FAILED: JSON test - {e}")
        assert False, f"JSON test failed: {e}"

if __name__ == "__main__":
    result = test_json_basico()
    print("Test completed:", result)
