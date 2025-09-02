# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is **Generador de Actas ADIF** (ADIF Document Generator), a PyQt5 desktop application for managing construction contracts and generating legal documents for ADIF (Spanish railway infrastructure company). The application follows an MVC architecture and manages the complete lifecycle of contracts from invitation to liquidation.

## Running the Application

### Main Entry Points
- `python main_py.py` - Main application entry point, launches the PyQt5 GUI
- `python test.py` - Testing/debugging script (XML to SpinBox conversion utility)
- `python.bat` - Windows batch script for extracting Python code structure

### Dependencies (Check main_py.py:118-123)
Required modules that must be installed:
- PyQt5 (GUI framework)
- openpyxl (Excel file handling)
- lxml (XML processing)
- docx2pdf (Word to PDF conversion)

The application will check for these dependencies on startup and show installation instructions if missing.

## Architecture and Structure

### Core MVC Components
- **Models** (`modelos_py.py`): Data models including `Proyecto`, `DatosContrato`, `Empresa`, `Oferta`, `DatosLiquidacion`
- **Views** (`ui/*.ui` files): PyQt5 UI forms (actas.ui, actas_mod.ui, actas_modificado.ui)
- **Controllers** (`controladores/`): Business logic controllers for different aspects:
  - `controlador_grafica.py` - Main GUI controller
  - `controlador_json.py` - Project data persistence
  - `controlador_excel.py` - Excel integration
  - `controlador_documentos.py` - Word document generation
  - `controlador_pdf.py` - PDF operations
  - And others for specific functionality

### Key Data Models
- **Proyecto**: Main project container with contract data, companies, offers, and liquidation
- **DatosContrato**: Contract details (type, amounts, dates, participants)
- **Empresa**: Company information (name, CIF, email, contact, offer amount)  
- **Oferta**: Economic offer details with validation states
- **DatosLiquidacion**: Financial liquidation calculations

### Project Structure
- **obras/**: Contains project folders with standardized subfolder structure (01-proyecto, 02-documentacion-finales, etc.)
- **plantillas/**: Word document templates for generating contracts and official documents
- **BaseDatos.json**: Configuration file with signatories and project data
- **controladores/**: MVC controllers for business logic
- **ui/**: PyQt5 UI definition files

## Document Generation System

The application generates official ADIF documents using Word templates from `plantillas/`:
- Contract documents (obras/servicios)
- Invitation letters
- Award letters  
- Official acts (inicio, adjudicación, replanteo, recepción, finalización)
- Liquidation documents

Templates use variable substitution with `@variableName@` syntax for dynamic content.

## Business Logic

### Contract Types and Limits (modelos_py.py:590-592)
- **OBRA** (Construction): €15,000 limit  
- **SERVICIO** (Service): €40,000 limit

### Financial Calculations
- IVA (VAT): 21% standard rate
- Automatic calculation of totals, differences, and settlements
- Support for penalties and adjustments in liquidations

### Validation System
The app includes comprehensive validation for:
- Required contract fields
- Company data (NIF format, email validation)
- Financial limits and calculations
- Date consistency across contract lifecycle

## File Management

### Project Storage
- Projects saved as `.PROJPMF` files (JSON format)
- Each project creates standardized folder structure in `obras/`
- Automatic backup system for data safety

### Logging
- Application logs to `adif_actas.log`
- Error tracking and debugging information
- UTF-8 encoding support

## Development Notes

### UI Development
- UI files are in Qt Designer format (.ui)
- `test.py` contains utility for converting QLineEdit widgets to QDoubleSpinBox for numeric fields
- The application supports dynamic UI loading and configuration

### Error Handling
- Comprehensive error handling with user-friendly messages
- Fallback mechanisms for PyInstaller deployment
- Critical error dialogs for startup issues

### Windows Compatibility
- Designed for Windows deployment
- Batch scripts for development utilities
- Path handling compatible with Windows file systems

## Testing

No formal test framework is configured. Testing appears to be done manually through the GUI and utility scripts like `test.py`.