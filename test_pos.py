# -*- coding: utf-8 -*-
"""
Pruebas automáticas para verificar la lógica de negocio, base de datos y corte de caja.
"""

import os
import unittest
import database

class TestPuntoDeVenta(unittest.TestCase):

    def setUp(self):
        # Usar una base de datos de prueba
        self.db_path = database.obtener_ruta_db()
        database.inicializar_db()

    def test_catalogo_inicial(self):
        productos = database.obtener_todos_los_productos()
        self.assertGreaterEqual(len(productos), 10, "Deben existir productos precargados.")

        # Verificar búsqueda por código
        p = database.buscar_producto_por_codigo("101")
        self.assertIsNotNone(p)
        self.assertIn("Mazapán", p['nombre'])

    def test_abrir_turno_y_venta(self):
        # Asegurar que hay turno abierto
        turno = database.obtener_turno_actual()
        if not turno:
            exito, id_turno = database.abrir_turno(200.0, "Fondo de prueba")
            self.assertTrue(exito)
        else:
            id_turno = turno['id']

        # Producto para vender
        p = database.buscar_producto_por_codigo("101") # Mazapan 7.00, stock inicial
        stock_original = p['stock']

        carrito = [{
            'id': p['id'],
            'codigo': p['codigo'],
            'nombre': p['nombre'],
            'precio': p['precio_venta'],
            'costo': p['precio_costo'],
            'cantidad': 2
        }]

        # Total venta = 14.00, Pago con 20.00, Cambio = 6.00
        exito, msg, ticket = database.registrar_venta(id_turno, carrito, 20.0, "Efectivo")
        self.assertTrue(exito)
        self.assertEqual(ticket['total'], 14.00)
        self.assertEqual(ticket['cambio'], 6.00)

        # Verificar que el stock se descontó
        p_actualizado = database.buscar_producto_por_codigo("101")
        self.assertEqual(p_actualizado['stock'], stock_original - 2)

        # Verificar resumen de caja
        resumen = database.calcular_resumen_caja(id_turno)
        self.assertGreaterEqual(resumen['total_ventas'], 14.00)

        # Probar cancelación de venta
        exito_cancel, msg_cancel = database.cancelar_venta(ticket['id_venta'], "Prueba de error")
        self.assertTrue(exito_cancel)

        # Verificar que el stock se restableció
        p_restablecido = database.buscar_producto_por_codigo("101")
        self.assertEqual(p_restablecido['stock'], stock_original)

    def test_tickets_y_cortes(self):
        import ticket
        cfg = database.obtener_configuracion()
        datos_venta = {
            'folio': 'T-99999',
            'fecha_hora': '2026-11-05 10:00:00',
            'total': 25.50,
            'pago_con': 50.00,
            'cambio': 24.50,
            'articulos': [
                {'nombre': 'Mazapán de la Rosa', 'cantidad': 2, 'precio': 7.00, 'subtotal': 14.00},
                {'nombre': 'Pelón Pelo Rico', 'cantidad': 1, 'precio': 11.50, 'subtotal': 11.50}
            ]
        }
        texto_t = ticket.generar_texto_ticket(datos_venta, cfg)
        self.assertIn("T-99999", texto_t)
        self.assertIn("TOTAL A PAGAR", texto_t)

        ruta_t = ticket.guardar_ticket_en_archivo(datos_venta, cfg)
        self.assertIsNotNone(ruta_t)
        self.assertTrue(os.path.exists(ruta_t))

        # Probar corte de caja
        resumen = {
            'id_turno': 99,
            'fecha_inicio': '2026-11-05 08:00:00',
            'fecha_fin': '2026-11-05 20:00:00',
            'monto_inicial': 200.0,
            'num_ventas': 15,
            'total_ventas': 850.0,
            'total_costo': 500.0,
            'ganancia_estimada': 350.0,
            'total_entradas': 50.0,
            'total_salidas': 100.0,
            'dinero_esperado': 1000.0
        }
        movs = [{'tipo': 'SALIDA', 'motivo': 'Pago a repartidor', 'monto': 100.0}]
        texto_c = ticket.generar_texto_corte(resumen, movs, cfg)
        self.assertIn("CORTE DE CAJA", texto_c)
        self.assertIn("TOTAL ESPERADO EN CAJA", texto_c)

        ruta_c = ticket.guardar_corte_en_archivo(resumen, movs, cfg)
        self.assertIsNotNone(ruta_c)
        self.assertTrue(os.path.exists(ruta_c))

    def test_respaldo(self):
        exito, ruta = database.crear_respaldo()
        self.assertTrue(exito)
        self.assertTrue(os.path.exists(ruta))

if __name__ == '__main__':
    unittest.main()
