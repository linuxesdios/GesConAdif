"""
Controlador especializado SOLO para cálculos matemáticos
VERSIÓN MEJORADA: Guarda automáticamente los valores calculados en JSON
"""
from typing import Optional
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import logging

logger = logging.getLogger(__name__)


class ControladorCalculos:
    """Controlador especializado SOLO para cálculos matemáticos - CON AUTO-GUARDADO"""
    
    def __init__(self):
        self._calculando = False
        self._campos_pendientes = {}  # Cache de campos para guardado por lotes


    # =================== CÁLCULOS DE IVA CON AUTO-GUARDADO ===================
    
    def calcular_iva_base_presupuesto(self, window):
        """Calcular IVA para base presupuesto - CON AUTO-GUARDADO EN JSON"""
        try:
            
            if self._calculando:

                return False
            
            self._calculando = True
            
            # Verificar que existe basePresupuesto
            if not hasattr(window, 'basePresupuesto'):
                logger.error("No existe basePresupuesto en window")
                return False
            
            widget_base = window.basePresupuesto
            
            base = self._obtener_valor_widget(widget_base)
            
            if base <= 0:

                return False
            
            # Calcular IVA (base × 0.21)
            iva = base * 0.21

            
            # Calcular total (base × 1.21)
            total = base * 1.21

            
            # 🆕 NUEVO: Establecer Y GUARDAR en JSON
            iva_guardado = False
            total_guardado = False
            
            # Establecer IVA en UI y guardar en JSON
            if hasattr(window, 'ivaPresupuestoBase'):

                self._establecer_valor_widget(window.ivaPresupuestoBase, iva)
                
                # 🆕 GUARDAR EN JSON
                iva_guardado = self._guardar_campo_calculado_en_json(window, 'ivaPresupuestoBase', f"{iva:.2f}")
                
            else:
                logger.error("No existe ivaPresupuestoBase en window")
            
            # Establecer total en UI y guardar en JSON
            if hasattr(window, 'totalPresupuestoBase'):

                self._establecer_valor_widget(window.totalPresupuestoBase, total)
                
                # 🆕 GUARDAR EN JSON
                total_guardado = self._guardar_campo_calculado_en_json(window, 'totalPresupuestoBase', f"{total:.2f}")
                
            else:
                logger.error("No existe totalPresupuestoBase en window")
            
            # Resumen de guardado
            if iva_guardado:
                pass  # Guardado exitoso
            if total_guardado:
                pass  # Guardado exitoso
            
            # 🆕 GUARDAR LOTE AL FINAL
            self._guardar_lote_completo(window)
            
            return True
            
        except Exception as e:
            logger.error(f"Error IVA base: {e}")
            import traceback
            logger.exception("Error completo:")
            return False
        finally:
            self._calculando = False

    def calcular_iva_adjudicacion(self, window):
        """Calcular IVA para precio adjudicación - CON AUTO-GUARDADO + LICITACIONES"""
        try:
            if self._calculando:
                return False
            
            self._calculando = True
            
            if not hasattr(window, 'precioAdjudicacion'):
                logger.error("No existe precioAdjudicacion")
                return False
            
            base = self._obtener_valor_widget(window.precioAdjudicacion)
            if base <= 0:

                return False
            

            
            # Calcular IVA y total
            iva = base * 0.21
            total = base * 1.21
            
            # 🆕 NUEVO: Calcular licitaciones
            licitacion15_valor = base * 1.5  # precioAdjudicacion * 1.5
            licitacion07_valor = base * 0.7  # precioAdjudicacion * 0.7
            

            
            # Establecer en campos principales Y GUARDAR
            if hasattr(window, 'ivaAdjudicacion'):
                self._establecer_valor_widget(window.ivaAdjudicacion, iva)
                self._guardar_campo_calculado_en_json(window, 'ivaAdjudicacion', f"{iva:.2f}")
            
            if hasattr(window, 'totalAdjudicacion'):
                self._establecer_valor_widget(window.totalAdjudicacion, total)
                self._guardar_campo_calculado_en_json(window, 'totalAdjudicacion', f"{total:.2f}")
            
            # También establecer en campos alternativos si existen Y GUARDAR
            if hasattr(window, 'precioAdjudicacionIva'):
                self._establecer_valor_widget(window.precioAdjudicacionIva, iva)
                self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionIva', f"{iva:.2f}")
            
            if hasattr(window, 'precioAdjudicacionTotal'):
                self._establecer_valor_widget(window.precioAdjudicacionTotal, total)
                self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionTotal', f"{total:.2f}")
            
            # 🆕 NUEVO: Establecer y guardar licitaciones
            if hasattr(window, 'licitacion15'):

                self._establecer_valor_widget(window.licitacion15, licitacion15_valor)
                self._guardar_campo_calculado_en_json(window, 'licitacion15', f"{licitacion15_valor:.2f}")

            else:

                pass
            if hasattr(window, 'licitacion07'):

                self._establecer_valor_widget(window.licitacion07, licitacion07_valor)
                self._guardar_campo_calculado_en_json(window, 'licitacion07', f"{licitacion07_valor:.2f}")

            else:
                pass
            
            # 🆕 GUARDAR LOTE AL FINAL
            self._guardar_lote_completo(window)
            

            return True
            
        except Exception as e:
            logger.error(f"Error IVA adjudicación: {e}")
            import traceback
            logger.exception("Error completo:")
            return False
        finally:
            self._calculando = False
    def calcular_certificacion_completa(self, window):
        """Calcular IVA certificación + liquidación - CON AUTO-GUARDADO"""
        try:
            if self._calculando:
                return False
            
            self._calculando = True
            
            # Usar la función mejorada de liquidación
            liquidacion_ok = self.calcular_liquidacion(window)
            
            return liquidacion_ok
            
        except Exception as e:
            logger.error(f"Error certificación: {e}")
            return False
        finally:
            self._calculando = False

    def calcular_liquidacion(self, window):
        """Calcular liquidación completa - CON AUTO-GUARDADO DE TODOS LOS CAMPOS"""
        try:
            logger.info("Iniciando cálculo de liquidación completa...")

            # Verificar campos mínimos necesarios
            if not hasattr(window, 'certBase'):
                logger.error("No existe certBase")
                return False

            cert_base = self._obtener_valor_widget(window.certBase)

            # 1. Calcular IVA y total de certificación Y GUARDAR
            cert_iva = cert_base * 0.21
            cert_total = cert_base * 1.21
            
            if hasattr(window, 'certIva'):
                self._establecer_valor_widget(window.certIva, cert_iva)
                self._guardar_campo_calculado_en_json(window, 'certIva', f"{cert_iva:.2f}")
            
            if hasattr(window, 'certTotal'):
                self._establecer_valor_widget(window.certTotal, cert_total)
                self._guardar_campo_calculado_en_json(window, 'certTotal', f"{cert_total:.2f}")

            # 2. Obtener precio de ejecución
            ejecucion = 0
            if hasattr(window, 'precioEjecucionContrata'):
                ejecucion = self._obtener_valor_widget(window.precioEjecucionContrata)
            elif hasattr(window, 'precioAdjudicacion'):
                ejecucion = self._obtener_valor_widget(window.precioAdjudicacion)
            

            # 3. CALCULAR saldoBaseLiquidacion Y GUARDAR
            saldo_base = ejecucion - cert_base
            logger.debug(f"Calculando saldoBaseLiquidacion: {ejecucion} - {cert_base} = {saldo_base}")
            
            if hasattr(window, 'saldoBaseLiquidacion'):
                self._establecer_valor_widget(window.saldoBaseLiquidacion, saldo_base)
                self._guardar_campo_calculado_en_json(window, 'saldoBaseLiquidacion', f"{saldo_base:.2f}")

            # 4. CALCULAR saldoIvaLiquidacion Y GUARDAR
            saldo_iva = saldo_base * 0.21
            if hasattr(window, 'saldoIvaLiquidacion'):
                self._establecer_valor_widget(window.saldoIvaLiquidacion, saldo_iva)
                self._guardar_campo_calculado_en_json(window, 'saldoIvaLiquidacion', f"{saldo_iva:.2f}")

            # 5. Calcular diferencia para liquidación
            diferencia_base = saldo_base
            logger.debug(f"Diferencia base = {diferencia_base}")

            # 6. Calcular adicional Y GUARDAR
            adicional_base = abs(diferencia_base)
            adicional_iva = adicional_base * 0.21
            adicional_total = adicional_base * 1.21

            if hasattr(window, 'adicionalBaseLiquidacion'):
                self._establecer_valor_widget(window.adicionalBaseLiquidacion, adicional_base)
                self._guardar_campo_calculado_en_json(window, 'adicionalBaseLiquidacion', f"{adicional_base:.2f}")
            
            if hasattr(window, 'adicionalIvaLiquidacion'):
                self._establecer_valor_widget(window.adicionalIvaLiquidacion, adicional_iva)
                self._guardar_campo_calculado_en_json(window, 'adicionalIvaLiquidacion', f"{adicional_iva:.2f}")
            
            if hasattr(window, 'adicionalTotalLiquidacion'):
                self._establecer_valor_widget(window.adicionalTotalLiquidacion, adicional_total)
                self._guardar_campo_calculado_en_json(window, 'adicionalTotalLiquidacion', f"{adicional_total:.2f}")

            # 7. Limpiar TODOS los campos de liquidación Y GUARDAR
            campos_liquidacion = [
                'liquidacionAFavorAdifBase', 'adifIvaAFavor', 'adifTotalAFavor',
                'empresaBaseAFavor', 'empresaIvaAFavor', 'empresaTotalAFavor'
            ]
            
            for campo in campos_liquidacion:
                if hasattr(window, campo):
                    self._establecer_valor_widget(getattr(window, campo), 0)
                    self._guardar_campo_calculado_en_json(window, campo, "0.00")

            # 8. Asignar según la diferencia Y GUARDAR
            if diferencia_base > 0:
                
                empresa_iva = diferencia_base * 0.21
                empresa_total = diferencia_base * 1.21
                
                if hasattr(window, 'empresaBaseAFavor'):
                    self._establecer_valor_widget(window.empresaBaseAFavor, diferencia_base)
                    self._guardar_campo_calculado_en_json(window, 'empresaBaseAFavor', f"{diferencia_base:.2f}")
                
                if hasattr(window, 'empresaIvaAFavor'):
                    self._establecer_valor_widget(window.empresaIvaAFavor, empresa_iva)
                    self._guardar_campo_calculado_en_json(window, 'empresaIvaAFavor', f"{empresa_iva:.2f}")
                
                if hasattr(window, 'empresaTotalAFavor'):
                    self._establecer_valor_widget(window.empresaTotalAFavor, empresa_total)
                    self._guardar_campo_calculado_en_json(window, 'empresaTotalAFavor', f"{empresa_total:.2f}")

            elif diferencia_base < 0:
                
                diferencia_abs = abs(diferencia_base)
                adif_iva = diferencia_abs * 0.21
                adif_total = diferencia_abs * 1.21
                
                if hasattr(window, 'liquidacionAFavorAdifBase'):
                    self._establecer_valor_widget(window.liquidacionAFavorAdifBase, diferencia_abs)
                    self._guardar_campo_calculado_en_json(window, 'liquidacionAFavorAdifBase', f"{diferencia_abs:.2f}")
                
                if hasattr(window, 'adifIvaAFavor'):
                    self._establecer_valor_widget(window.adifIvaAFavor, adif_iva)
                    self._guardar_campo_calculado_en_json(window, 'adifIvaAFavor', f"{adif_iva:.2f}")
                
                if hasattr(window, 'adifTotalAFavor'):
                    self._establecer_valor_widget(window.adifTotalAFavor, adif_total)
                    self._guardar_campo_calculado_en_json(window, 'adifTotalAFavor', f"{adif_total:.2f}")

            # 🆕 GUARDAR LOTE AL FINAL
            self._guardar_lote_completo(window)
            
            return True

        except Exception as e:
            logger.error(f"Error liquidación: {e}")
            import traceback
            logger.exception("Error completo:")
            return False

    # =================== SISTEMA DE GUARDADO OPTIMIZADO POR LOTES ===================
    # __init__ duplicado eliminado - ya está definido al inicio de la clase

    def _agregar_campo_pendiente(self, nombre_campo: str, valor: str):
        """Agregar campo al lote de guardado pendiente"""
        self._campos_pendientes[nombre_campo] = valor
        
    def _guardar_lote_completo(self, window) -> bool:
        """Guardar todos los campos pendientes - DELEGADO al sistema de eventos"""
        if not self._campos_pendientes:
            return True
            
        try:
            # Usar el sistema de eventos para guardado diferido
            if (hasattr(window, 'controlador_eventos_ui') and 
                window.controlador_eventos_ui):
                
                # Transferir todos los campos pendientes al sistema de eventos
                for nombre_campo, valor in self._campos_pendientes.items():
                    window.controlador_eventos_ui._guardar_campo_en_json(nombre_campo, valor)
                
                # Limpiar cache local
                self._campos_pendientes.clear()
                return True
            else:
                logger.warning("No hay controlador_eventos_ui para lote")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando lote: {e}")
            self._campos_pendientes.clear()
            return False

    def _guardar_campo_calculado_en_json(self, window, nombre_campo: str, valor: str) -> bool:
        """Guardar campo - DELEGADO al sistema de eventos"""
        try:
            # Usar el sistema de eventos para guardado diferido
            if (hasattr(window, 'controlador_eventos_ui') and 
                window.controlador_eventos_ui and
                hasattr(window.controlador_eventos_ui, '_guardar_campo_en_json')):
                window.controlador_eventos_ui._guardar_campo_en_json(nombre_campo, valor)
                return True
            else:
                # Fallback al sistema anterior
                self._agregar_campo_pendiente(nombre_campo, valor)
                return True
        except Exception as e:
            logger.error(f"Error guardando campo {nombre_campo}: {e}")
            return False

    # =================== CÁLCULOS DE OFERTAS CON AUTO-GUARDADO ===================
    
    def calcular_ofertas_completo(self, window):
        """Calcular todos los valores relacionados con ofertas - CON AUTO-GUARDADO + LICITACIONES"""
        try:
            if self._calculando:
                return False
            
            self._calculando = True
            
            if not hasattr(window, 'TwOfertas'):
                logger.error("No existe TwOfertas")
                return False
            
            tabla = window.TwOfertas
            
            # 1. Contar ofertas válidas Y GUARDAR
            num_ofertas = self._contar_ofertas_validas(tabla)
            if hasattr(window, 'numEmpresasPresentadas'):
                window.numEmpresasPresentadas.setText(str(num_ofertas))
                self._guardar_campo_calculado_en_json(window, 'numEmpresasPresentadas', str(num_ofertas))
            
            # 2. Obtener precio más bajo
            precio_min = self._obtener_precio_mas_bajo(tabla)
            
            # 3-4. Procesar valores dependientes del precio (solo si hay precio válido)
            if precio_min > 0:
                # 3. FORZAR establecimiento del precio adjudicación Y GUARDAR
                if hasattr(window, 'precioAdjudicacion'):
                    self._establecer_valor_widget(window.precioAdjudicacion, precio_min)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacion', f"{precio_min:.2f}")
                
                # 4. FORZAR cálculo de IVA y total adjudicación Y GUARDAR
                iva_adj = precio_min * 0.21
                total_adj = precio_min * 1.21
                
                # 🆕 NUEVO: Calcular licitaciones automáticamente
                licitacion15_valor = precio_min * 1.5
                licitacion07_valor = precio_min * 0.7
                
                logger.info(f"Auto-calculando licitaciones desde ofertas: precio mínimo {precio_min:.2f}, licitacion15 {licitacion15_valor:.2f}, licitacion07 {licitacion07_valor:.2f}")
                
                if hasattr(window, 'ivaAdjudicacion'):
                    self._establecer_valor_widget(window.ivaAdjudicacion, iva_adj)
                    self._guardar_campo_calculado_en_json(window, 'ivaAdjudicacion', f"{iva_adj:.2f}")
                
                if hasattr(window, 'totalAdjudicacion'):
                    self._establecer_valor_widget(window.totalAdjudicacion, total_adj)
                    self._guardar_campo_calculado_en_json(window, 'totalAdjudicacion', f"{total_adj:.2f}")

                # También campos alternativos Y GUARDAR
                if hasattr(window, 'precioAdjudicacionIva'):
                    self._establecer_valor_widget(window.precioAdjudicacionIva, iva_adj)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionIva', f"{iva_adj:.2f}")
                
                if hasattr(window, 'precioAdjudicacionTotal'):
                    self._establecer_valor_widget(window.precioAdjudicacionTotal, total_adj)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionTotal', f"{total_adj:.2f}")

                # 🆕 NUEVO: Establecer y guardar licitaciones
                if hasattr(window, 'licitacion15'):
                    self._establecer_valor_widget(window.licitacion15, licitacion15_valor)
                    self._guardar_campo_calculado_en_json(window, 'licitacion15', f"{licitacion15_valor:.2f}")
                    logger.info(f"licitacion15 auto-establecido: {licitacion15_valor:.2f}")
                
                if hasattr(window, 'licitacion07'):
                    self._establecer_valor_widget(window.licitacion07, licitacion07_valor)
                    self._guardar_campo_calculado_en_json(window, 'licitacion07', f"{licitacion07_valor:.2f}")
                    logger.info(f"licitacion07 auto-establecido: {licitacion07_valor:.2f}")
            else:
                # Limpiar campos dependientes del precio cuando no hay ofertas válidas
                logger.info("Limpiando campos por falta de ofertas válidas")
                
                if hasattr(window, 'precioAdjudicacion'):
                    self._establecer_valor_widget(window.precioAdjudicacion, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacion', "0.00")
                
                if hasattr(window, 'ivaAdjudicacion'):
                    self._establecer_valor_widget(window.ivaAdjudicacion, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'ivaAdjudicacion', "0.00")
                
                if hasattr(window, 'totalAdjudicacion'):
                    self._establecer_valor_widget(window.totalAdjudicacion, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'totalAdjudicacion', "0.00")

                # También limpiar campos alternativos
                if hasattr(window, 'precioAdjudicacionIva'):
                    self._establecer_valor_widget(window.precioAdjudicacionIva, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionIva', "0.00")
                
                if hasattr(window, 'precioAdjudicacionTotal'):
                    self._establecer_valor_widget(window.precioAdjudicacionTotal, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'precioAdjudicacionTotal', "0.00")

                # Limpiar también licitaciones
                if hasattr(window, 'licitacion15'):
                    self._establecer_valor_widget(window.licitacion15, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'licitacion15', "0.00")
                
                if hasattr(window, 'licitacion07'):
                    self._establecer_valor_widget(window.licitacion07, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'licitacion07', "0.00")

            # 5-8. Procesar empresa y campos relacionados (SIEMPRE, independientemente del precio)
            
            # 5. FORZAR cálculo de precio ejecución contrata Y GUARDAR
            if hasattr(window, 'precioEjecucionContrata'):
                if precio_min > 0:  # Solo si hay un precio válido
                    self._establecer_valor_widget(window.precioEjecucionContrata, precio_min)
                    self._guardar_campo_calculado_en_json(window, 'precioEjecucionContrata', f"{precio_min:.2f}")
                else:
                    # Si no hay precio mínimo válido, limpiar el campo
                    self._establecer_valor_widget(window.precioEjecucionContrata, 0.0)
                    self._guardar_campo_calculado_en_json(window, 'precioEjecucionContrata', "0.00")
            
            # 6. Obtener nombre empresa con menor oferta Y GUARDAR
            empresa = self._obtener_nombre_empresa_menor_oferta(tabla)
            logger.info(f"Empresa adjudicada recalculada: '{empresa}'")
            
            # SIEMPRE actualizar el campo empresaAdjudicada (incluso si está vacía)
            if hasattr(window, 'empresaAdjudicada'):
                window.empresaAdjudicada.blockSignals(True)
                window.empresaAdjudicada.setText(empresa)  # Puede ser "" si no hay ofertas
                window.empresaAdjudicada.blockSignals(False)
                self._guardar_campo_calculado_en_json(window, 'empresaAdjudicada', empresa)
            
            # 7. Buscar CIF Y GUARDAR (solo si hay empresa)
            if hasattr(window, 'TwEmpresas') and hasattr(window, 'contratistaCIF'):
                if empresa:  # Solo si hay empresa adjudicada
                    cif = self._obtener_valor_en_otra_columna(
                        window.TwEmpresas, empresa, 0, 1
                    )
                    
                    if cif:
                        window.contratistaCIF.blockSignals(True)
                        window.contratistaCIF.setText(cif)
                        window.contratistaCIF.blockSignals(False)
                        self._guardar_campo_calculado_en_json(window, 'contratistaCIF', cif)
                    else:
                        # Si no se encuentra CIF, limpiar el campo
                        window.contratistaCIF.blockSignals(True)
                        window.contratistaCIF.setText("")
                        window.contratistaCIF.blockSignals(False)
                        self._guardar_campo_calculado_en_json(window, 'contratistaCIF', "")
                else:
                    # Si no hay empresa, limpiar el CIF
                    window.contratistaCIF.blockSignals(True)
                    window.contratistaCIF.setText("")
                    window.contratistaCIF.blockSignals(False)
                    self._guardar_campo_calculado_en_json(window, 'contratistaCIF', "")
                
                # 8. Calcular números de empresas Y GUARDAR
                total_empresas = tabla.rowCount()
                if hasattr(window, 'numEmpresasSolicitadas'):
                    window.numEmpresasSolicitadas.setText(str(total_empresas))
                    self._guardar_campo_calculado_en_json(window, 'numEmpresasSolicitadas', str(total_empresas))
            
            # 🆕 GUARDAR LOTE AL FINAL
            self._guardar_lote_completo(window)
            return True
            
        except Exception as e:
            logger.error(f"Error ofertas: {e}")
            import traceback
            logger.exception("Error completo:")
            return False
        finally:
            self._calculando = False
    def actualizar_justificacion_limites(self, window):
        """Actualizar texto de justificación según tipo de contrato y presupuesto - CON AUTO-GUARDADO"""
        try:
            if not hasattr(window, 'justificacionLimites'):
                return False
            
            # Obtener valor del presupuesto
            base_presupuesto = 0.0
            if hasattr(window, 'basePresupuesto'):
                base_presupuesto = self._obtener_valor_widget(window.basePresupuesto)
            
            # Determinar tipo de contrato usando el nuevo sistema
            es_obras = False
            es_servicios = False
            
            if (hasattr(window, 'contract_manager') and 
                window.contract_manager):
                
                contract_data = window.contract_manager.get_current_contract_data()
                if contract_data:
                    tipo_actuacion = contract_data.get('tipoActuacion', '')
                    es_obras = tipo_actuacion in ['obras', 'obra_mantenimiento']
                    es_servicios = tipo_actuacion in ['servicios', 'serv_mantenimiento']
            
            # Generar texto según el tipo
            if es_obras:
                texto = f"El contrato de la obra es por importe de {base_presupuesto:,.2f} euros, no superando por tanto el límite de 40.000 € establecido."
            elif es_servicios:
                texto = f"El contrato de servicios es por importe de {base_presupuesto:,.2f} euros, no superando por tanto el límite de 15.000 € establecido."
            else:
                texto = f"El contrato es por importe de {base_presupuesto:,.2f} euros."
            
            # Establecer texto en UI
            window.justificacionLimites.blockSignals(True)
            if hasattr(window.justificacionLimites, 'setPlainText'):
                window.justificacionLimites.setPlainText(texto)
            elif hasattr(window.justificacionLimites, 'setText'):
                window.justificacionLimites.setText(texto)
            window.justificacionLimites.blockSignals(False)
            
            # 🆕 GUARDAR EN JSON
            self._guardar_campo_calculado_en_json(window, 'justificacionLimites', texto)
            
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando justificación: {e}")
            return False

    # =================== SINCRONIZACIÓN EMPRESAS ===================
    
    def sincronizar_empresas_ofertas(self, main_window):
        """MODIFICADA: Sincronizar con estructura unificada - LEYENDO DIRECTAMENTE DE TABLA"""
        try:
            # 🔄 LEER DIRECTAMENTE DE LA TABLA DE EMPRESAS PARA SINCRONIZAR EN TIEMPO REAL
            if not hasattr(main_window, 'TwEmpresas') or not hasattr(main_window, 'TwOfertas'):
                return

            tabla_empresas = main_window.TwEmpresas
            tabla_ofertas = main_window.TwOfertas

            # Obtener empresas actuales de la tabla (sin depender del JSON)
            empresas_nombres = []
            for fila in range(tabla_empresas.rowCount()):
                nombre_item = tabla_empresas.item(fila, 0)
                if nombre_item and nombre_item.text().strip():
                    empresas_nombres.append(nombre_item.text().strip())

            # Sincronizar tabla ofertas directamente
            self._sincronizar_tabla_ofertas_directo(tabla_ofertas, empresas_nombres)

        except Exception as e:
            logger.error(f"Error sincronizando empresas unificadas: {e}")

    def _sincronizar_tabla_ofertas_directo(self, tabla_ofertas, empresas_nombres):
        """NUEVA: Sincronizar tabla ofertas directamente desde nombres de empresas"""
        try:
            # Bloquear señales para evitar eventos recursivos
            tabla_ofertas.blockSignals(True)
            
            # Obtener ofertas existentes antes de cambiar
            ofertas_existentes = {}
            for fila in range(tabla_ofertas.rowCount()):
                oferta_item = tabla_ofertas.item(fila, 1)
                if oferta_item and oferta_item.text().strip():
                    ofertas_existentes[fila] = oferta_item.text().strip()
            
            # Ajustar número de filas
            tabla_ofertas.setRowCount(len(empresas_nombres))

            # Llenar tabla de ofertas
            for i, nombre_empresa in enumerate(empresas_nombres):
                # Columna 0: Nombre empresa (solo lectura, fondo gris)
                item_nombre = QTableWidgetItem(nombre_empresa)
                item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)
                item_nombre.setBackground(QColor('lightgray'))
                tabla_ofertas.setItem(i, 0, item_nombre)
                
                # Columna 1: Oferta (mantener valor existente si existe)
                oferta_existente = ofertas_existentes.get(i, "")
                item_oferta = QTableWidgetItem(oferta_existente)
                tabla_ofertas.setItem(i, 1, item_oferta)

            # Reactivar señales
            tabla_ofertas.blockSignals(False)
            
            logger.info(f"Tabla ofertas sincronizada: {len(empresas_nombres)} empresas")

        except Exception as e:
            logger.error(f"Error sincronizando tabla ofertas directo: {e}")
            if tabla_ofertas:
                tabla_ofertas.blockSignals(False)

    def _sincronizar_tabla_ofertas_unificada(self, tabla_ofertas, empresas_lista):
        """NUEVA: Sincronizar tabla ofertas con estructura unificada"""
        try:
            tabla_ofertas.blockSignals(True)
            tabla_ofertas.setRowCount(len(empresas_lista))

            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtCore import Qt

            for i, empresa in enumerate(empresas_lista):
                if isinstance(empresa, dict):
                    nombre = empresa.get('nombre', '')
                    ofertas = empresa.get('ofertas', '')
                    
                    # Nombre empresa (solo lectura)
                    item_nombre = QTableWidgetItem(nombre)
                    item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable)
                    tabla_ofertas.setItem(i, 0, item_nombre)
                    
                    # Ofertas (editable)
                    item_ofertas = QTableWidgetItem(str(ofertas))
                    tabla_ofertas.setItem(i, 1, item_ofertas)

            tabla_ofertas.blockSignals(False)

        except Exception as e:
            logger.error(f"Error sincronizando tabla ofertas: {e}")
            if tabla_ofertas:
                tabla_ofertas.blockSignals(False)
    def validar_datos_empresas(self, window, fila, valor):
        """Validar datos en segunda columna de TwEmpresas - USANDO HELPERS CONSOLIDADOS"""
        try:
            
            from helpers_py import es_numero_valido
            es_valido = es_numero_valido(valor)
            logger.debug(f"Valor válido: {es_valido}")
            
            return es_valido
            
        except Exception as e:
            logger.error(f"Error validación: {e}")
            return False

    # =================== UTILIDADES =================== 
    # Función _es_numero_valido eliminada - ahora en helpers_py.es_numero_valido

    def _obtener_valor_en_otra_columna(self, tabla, valor_buscado, col_buscar=0, col_devolver=3):
        """Buscar valor en tabla y devolver valor de otra columna"""
        try:
            for fila in range(tabla.rowCount()):
                item = tabla.item(fila, col_buscar)
                if item and item.text().strip() == valor_buscado.strip():
                    item_devuelto = tabla.item(fila, col_devolver)
                    return item_devuelto.text() if item_devuelto else ""
            return ""
        except Exception:
            return ""

    def _contar_ofertas_validas(self, tabla):
        """Contar ofertas válidas en tabla"""
        contador = 0
        try:
            for fila in range(tabla.rowCount()):
                item = tabla.item(fila, 1)  # Segunda columna
                if item and item.text().strip():
                    valor_str = item.text().replace(',', '.')
                    try:
                        valor = float(valor_str)
                        if valor > 0:
                            contador += 1
                    except ValueError:
                        pass
        except Exception:
            pass
        
        return contador

    def _obtener_precio_mas_bajo(self, tabla):
        """Obtener precio más bajo de ofertas válidas - MEJORADO para manejar formatos"""
        precios = []
        try:
            
            for fila in range(tabla.rowCount()):
                item = tabla.item(fila, 1)  # Segunda columna
                if item and item.text().strip():
                    texto_original = item.text().strip()
                    
                    try:
                        # Usar el método unificado de conversión
                        valor = self._convertir_texto_a_numero(texto_original)
                        if valor > 0:
                            precios.append(valor)
                        else:
                            logger.warning(f"Valor <= 0: {valor}")
                    except ValueError as e:
                        logger.error(f"No se pudo convertir: '{texto_original}' - {e}")
        except Exception as e:
            logger.error(f"Error procesando tabla: {e}")
        
        if precios:
            precio_minimo = min(precios)
            logger.info(f"Precio mínimo encontrado: {precio_minimo} (de {len(precios)} ofertas válidas)")
            return precio_minimo
        else:
            logger.warning("No se encontraron ofertas válidas")
            return 0.0

    def _obtener_nombre_empresa_menor_oferta(self, tabla):
        """Obtener nombre de empresa con menor oferta"""
        try:
            logger.debug("Analizando tabla de ofertas...")
            logger.debug(f"Número de filas en tabla: {tabla.rowCount()}")
            
            # Si la tabla está vacía, devolver cadena vacía
            if tabla.rowCount() == 0:
                logger.info("Tabla de ofertas vacía - devolviendo empresa vacía")
                return ""
            
            menor_valor = float('inf')
            nombre_empresa = ""
            ofertas_validas = 0
            
            for fila in range(tabla.rowCount()):
                item_oferta = tabla.item(fila, 1)  # Segunda columna
                item_nombre = tabla.item(fila, 0)   # Primera columna
                
                logger.debug(f"Fila {fila}:")
                logger.debug(f"  - item_nombre existe: {item_nombre is not None}")
                logger.debug(f"  - item_oferta existe: {item_oferta is not None}")
                
                if item_nombre:
                    nombre_texto = item_nombre.text()
                    logger.debug(f"  - Nombre: '{nombre_texto}'")
                
                if item_oferta:
                    oferta_texto = item_oferta.text()
                    logger.debug(f"  - Oferta texto: '{oferta_texto}'")
                
                if item_oferta and item_nombre:
                    valor_texto = item_oferta.text().strip()
                    
                    # Saltar celdas vacías
                    if not valor_texto:
                        logger.debug("  - Oferta vacía, saltando...")
                        continue
                    
                    # Convertir formato español a float
                    try:
                        valor = self._convertir_texto_a_numero(valor_texto)
                        logger.debug(f"  - Valor convertido: {valor}")
                        if valor > 0 and valor < menor_valor:
                            menor_valor = valor
                            nombre_empresa = item_nombre.text()
                            ofertas_validas += 1
                            logger.debug(f"  - Nueva menor oferta: {nombre_empresa} con {valor}")
                    except ValueError as e:
                        logger.error(f"  - Error convirtiendo '{valor_texto}': {e}")
            
            logger.info(f"Resumen: {ofertas_validas} ofertas válidas encontradas")
            logger.info(f"Menor valor: {menor_valor}")
            logger.info(f"Empresa ganadora: '{nombre_empresa}'")
            
            # Si no hay ofertas válidas, devolver cadena vacía
            if ofertas_validas == 0:
                logger.info("No se encontraron ofertas válidas - devolviendo empresa vacía")
                return ""
            
            return nombre_empresa
            
        except Exception as e:
            logger.error(f"Error en _obtener_nombre_empresa_menor_oferta: {e}")
            import traceback
            logger.exception("Error completo:")
            return ""

    def _convertir_texto_a_numero(self, texto):
        """Convertir texto en formato español (33.000,00) a float"""
        if not texto or not isinstance(texto, str):
            raise ValueError("Texto vacío o no válido")
        
        # Limpiar espacios
        texto = texto.strip()
        
        # Detectar formato: si hay punto Y coma, es formato español
        if '.' in texto and ',' in texto:
            # Formato español: 33.000,00 -> punto = miles, coma = decimales
            texto_limpio = texto.replace('.', '').replace(',', '.')
            logger.debug(f"Formato español detectado: '{texto}' -> '{texto_limpio}'")
            return float(texto_limpio)
        elif ',' in texto and texto.count(',') == 1:
            # Solo coma: podría ser decimal español (33000,00)
            texto_limpio = texto.replace(',', '.')
            logger.debug(f"Decimal español detectado: '{texto}' -> '{texto_limpio}'")
            return float(texto_limpio)
        elif '.' in texto:
            # Solo punto: podría ser decimal inglés (33000.00) o miles español (33.000)
            partes = texto.split('.')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Probablemente decimal inglés
                logger.debug(f"Decimal inglés detectado: '{texto}'")
                return float(texto)
            else:
                # Probablemente miles español (quitar puntos)
                texto_limpio = texto.replace('.', '')
                logger.debug(f"Miles español detectado: '{texto}' -> '{texto_limpio}'")
                return float(texto_limpio)
        else:
            # Solo números sin separadores
            logger.debug(f"Número simple detectado: '{texto}'")
            return float(texto)

    def _verificar_ofertas_duplicadas(self, tabla):
        """Verificar si hay ofertas con el mismo precio mínimo (detectar empates)"""
        try:
            precio_min = self._obtener_precio_mas_bajo(tabla)
            if precio_min <= 0:
                return False
            
            contador_minimo = 0
            
            for fila in range(tabla.rowCount()):
                item = tabla.item(fila, 1)  # Segunda columna
                if item and item.text().strip():
                    valor_str = item.text().replace(',', '.')
                    try:
                        valor = float(valor_str)
                        if abs(valor - precio_min) < 0.01:  # Considerar iguales con 2 decimales
                            contador_minimo += 1
                    except ValueError:
                        pass
            
            return contador_minimo > 1
            
        except Exception:
            return False

    def _establecer_valor_widget(self, widget, valor):
        """Establecer valor en widget según su tipo"""
        try:
            if hasattr(widget, 'setValue'):  # QDoubleSpinBox, QSpinBox
                widget.blockSignals(True)
                widget.setValue(float(valor))
                widget.blockSignals(False)
                
            elif hasattr(widget, 'setText'):  # QLineEdit
                widget.blockSignals(True)
                widget.setText(str(valor))
                widget.blockSignals(False)
                
            elif hasattr(widget, 'setPlainText'):  # QTextEdit
                widget.blockSignals(True)
                widget.setPlainText(str(valor))
                widget.blockSignals(False)
                
            elif hasattr(widget, 'setCurrentText'):  # QComboBox
                widget.blockSignals(True)
                widget.setCurrentText(str(valor))
                widget.blockSignals(False)
                
            elif hasattr(widget, 'setChecked'):  # QCheckBox, QRadioButton
                widget.blockSignals(True)
                widget.setChecked(bool(valor))
                widget.blockSignals(False)
                
            else:
                logger.warning(f"No se puede establecer valor en widget tipo: {type(widget)}")
                
        except Exception as e:
            logger.error(f"Error estableciendo valor en widget: {e}")    

    def _obtener_valor_widget(self, widget):
        """Obtener valor del widget según su tipo - SOLO PARA CÁLCULOS NUMÉRICOS"""
        try:
            # Esta función está diseñada SOLO para cálculos matemáticos
            # Por eso siempre devuelve float
            
            if hasattr(widget, 'value'):  # QDoubleSpinBox, QSpinBox
                return float(widget.value())
                
            elif hasattr(widget, 'text'):  # QLineEdit
                valor = widget.text().strip()
                if not valor:
                    return 0.0
                try:
                    return float(valor.replace(',', '.'))
                except ValueError:
                    return 0.0
                
            elif hasattr(widget, 'toPlainText'):  # QTextEdit
                valor = widget.toPlainText().strip()
                if not valor:
                    return 0.0
                try:
                    return float(valor.replace(',', '.'))
                except ValueError:
                    return 0.0
                
            elif hasattr(widget, 'currentText'):  # QComboBox
                valor = widget.currentText().strip()
                try:
                    return float(valor.replace(',', '.'))
                except ValueError:
                    return 0.0
                    
            elif hasattr(widget, 'isChecked'):  # QCheckBox, QRadioButton
                return 1.0 if widget.isChecked() else 0.0
                
            # Para widgets no numéricos (fechas, tiempo), devolver 0
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error obteniendo valor de widget: {e}")
            return 0.0
    
    # =================== MÉTODOS BÁSICOS REQUERIDOS POR LOS TESTS ===================
    
    def calcular_iva(self, importe: float, porcentaje: float = 21.0) -> float:
        """Calcular IVA de un importe"""
        try:
            return importe * (porcentaje / 100)
        except Exception:
            return 0.0
    
    def calcular_total_con_iva(self, importe: float, porcentaje: float = 21.0) -> float:
        """Calcular total con IVA"""
        try:
            return importe * (1 + porcentaje / 100)
        except Exception:
            return 0.0
    
    def validar_importe(self, importe) -> bool:
        """Validar que un importe es válido"""
        try:
            if isinstance(importe, str):
                importe = float(importe.replace(',', '.'))
            return isinstance(importe, (int, float)) and importe >= 0
        except (ValueError, TypeError):
            return False
    
    def formatear_moneda(self, importe: float, simbolo: str = '€') -> str:
        """Formatear importe como moneda"""
        try:
            return f"{importe:,.2f} {simbolo}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except Exception:
            return f"0,00 {simbolo}"
    
    # =================== MÉTODOS DE CONTROL ===================
    
    def pausar_calculos(self):
        """Pausar cálculos temporalmente"""
        self._calculando = True
        logger.info("Cálculos pausados")

    def reanudar_calculos(self):
        """Reanudar cálculos"""
        self._calculando = False
        logger.info("Cálculos reanudados")

    def esta_calculando(self):
        """Verificar si está calculando"""
        return self._calculando

    # =================== CÁLCULOS DE ANUALIDADES ===================
    
    def calcular_anualidades(self, window):
        """Calcular anualidades basado en precio adjudicación, plazoEjecucion y fechaContrato"""
        try:
            if self._calculando:
                return False
            
            self._calculando = True
            
            # Obtener valores necesarios
            precio_adjudicacion = 0
            if hasattr(window, 'precioAdjudicacion'):
                precio_adjudicacion = self._obtener_valor_widget(window.precioAdjudicacion)
            
            if precio_adjudicacion <= 0:
                logger.info("Precio adjudicación <= 0, no calculando anualidades")
                return False
            
            # Obtener plazo de ejecución
            plazo_meses = 0
            if hasattr(window, 'plazoEjecucion'):
                plazo_meses = self._obtener_valor_widget(window.plazoEjecucion)
            
            if plazo_meses <= 0:
                logger.info("Plazo ejecución <= 0, no calculando anualidades")
                return False
            
            # Obtener mes de fecha contrato
            mes_inicio = 1  # Por defecto enero
            if hasattr(window, 'fechaContrato'):
                try:
                    fecha = window.fechaContrato.date()
                    mes_inicio = fecha.month()
                except:
                    mes_inicio = 1
            
            logger.info("Calculando anualidades:")
            logger.info(f"  - Precio adjudicación: {precio_adjudicacion:.2f}")
            logger.info(f"  - Plazo ejecución: {plazo_meses} meses")
            logger.info(f"  - Mes inicio: {mes_inicio}")
            
            # Calcular valor mensual
            valor_mensual = precio_adjudicacion / plazo_meses
            
            # Calcular meses del primer año (desde mes_inicio hasta diciembre)
            meses_anualidad1 = 13 - mes_inicio  # 13 porque queremos desde mes_inicio hasta 12 (diciembre)
            if meses_anualidad1 > plazo_meses:
                meses_anualidad1 = plazo_meses
            
            # Calcular meses del segundo año
            meses_anualidad2 = plazo_meses - meses_anualidad1
            
            # Calcular valores de anualidades
            base_anualidad1 = valor_mensual * meses_anualidad1
            base_anualidad2 = valor_mensual * meses_anualidad2
            
            # Calcular IVA (21%)
            iva_anualidad1 = base_anualidad1 * 0.21
            iva_anualidad2 = base_anualidad2 * 0.21
            
            # Calcular totales
            total_anualidad1 = base_anualidad1 * 1.21
            total_anualidad2 = base_anualidad2 * 1.21
            
            logger.info("Resultado anualidades:")
            logger.info(f"  - Meses Anualidad 1: {meses_anualidad1}")
            logger.info(f"  - Meses Anualidad 2: {meses_anualidad2}")
            logger.info(f"  - Base Anualidad 1: {base_anualidad1:.2f}")
            logger.info(f"  - Base Anualidad 2: {base_anualidad2:.2f}")
            logger.info(f"  - Total verificación: {base_anualidad1 + base_anualidad2:.2f}")
            
            # Establecer valores en los widgets y guardar
            if hasattr(window, 'BaseAnualidad1'):
                self._establecer_valor_widget(window.BaseAnualidad1, base_anualidad1)
                self._guardar_campo_calculado_en_json(window, 'BaseAnualidad1', f"{base_anualidad1:.2f}")
            
            if hasattr(window, 'IvaAnualidad1'):
                self._establecer_valor_widget(window.IvaAnualidad1, iva_anualidad1)
                self._guardar_campo_calculado_en_json(window, 'IvaAnualidad1', f"{iva_anualidad1:.2f}")
            
            if hasattr(window, 'TotalAnualidad1'):
                self._establecer_valor_widget(window.TotalAnualidad1, total_anualidad1)
                self._guardar_campo_calculado_en_json(window, 'TotalAnualidad1', f"{total_anualidad1:.2f}")
            
            if hasattr(window, 'BaseAnualidad2'):
                self._establecer_valor_widget(window.BaseAnualidad2, base_anualidad2)
                self._guardar_campo_calculado_en_json(window, 'BaseAnualidad2', f"{base_anualidad2:.2f}")
            
            if hasattr(window, 'IvaAnualidad2'):
                self._establecer_valor_widget(window.IvaAnualidad2, iva_anualidad2)
                self._guardar_campo_calculado_en_json(window, 'IvaAnualidad2', f"{iva_anualidad2:.2f}")
            
            if hasattr(window, 'TotalAnualidad2'):
                self._establecer_valor_widget(window.TotalAnualidad2, total_anualidad2)
                self._guardar_campo_calculado_en_json(window, 'TotalAnualidad2', f"{total_anualidad2:.2f}")
            
            # Guardar lote completo
            self._guardar_lote_completo(window)
            
            logger.info("Cálculo de anualidades completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error calculando anualidades: {e}")
            import traceback
            logger.exception("Error completo:")
            return False
        finally:
            self._calculando = False