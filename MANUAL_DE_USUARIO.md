# 📖 Manual de Uso - Punto de Venta para Dulcería

¡Bienvenidos! Este programa está diseñado para ser muy fácil de usar, rápido y sin complicaciones. No necesita internet y guarda todas sus ventas de manera segura.

---

## 📌 Pestañas Principales (Presione las teclas F1 a F5)
En la parte superior de la pantalla encontrará las 5 secciones del sistema:
- **[F1] VENTA:** Para registrar lo que compran los clientes y cobrar.
- **[F2] INVENTARIO:** Para ver sus productos, agregar dulces nuevos y reponer piezas.
- **[F3] CORTE DE CAJA:** Para abrir la caja, registrar pagos de gastos y hacer el corte del día.
- **[F4] HISTORIAL:** Para ver las ventas del día o reimprimir/cancelar una venta.
- **[F5] AJUSTES / USB:** Para cambiar el nombre de la tienda y hacer respaldos a la memoria USB.

---

## 1. Cómo Realizar una Venta

### Forma Rápida 1: Con Lector de Código de Barras (Pistola)
1. Apunte el lector al código de barras del dulce.
2. Al escanear, el producto se agrega automáticamente a la lista.

### Forma Rápida 2: Botonera de "Dulces Rápidos" (Sin teclear nada)
- En la parte superior hay botones de colores con los dulces más vendidos (ej. *Mazapán, Paleta Payaso, Bubbaloo, Pelón Pelo Rico*).
- Solo haga **un clic en el botón** y se sumará 1 pieza al carrito de inmediato.

### Forma Rápida 3: Escribiendo el Nombre
1. En el recuadro blanco escriba una parte del nombre (por ejemplo: `paleta` o `mazapan`).
2. Presione la tecla **Enter** (o clic en "+ Agregar").
3. Si hay varios dulces parecidos, aparecerá una ventanita para que elija el correcto con un doble clic o con la tecla Enter.

### Modificar Cantidades en el Carrito:
- **Para vender varias piezas:** En el campo `Cant:` escriba la cantidad antes de escanear (ej. `5`) y luego escanee o seleccione el dulce.
- **Botones rápidos:** Debajo de la tabla puede usar los botones `[ +1 Pieza ]` o `[ -1 Pieza ]` sobre el dulce seleccionado.
- **Eliminar un producto del carrito:** Seleccione el renglón y dé clic en `Quitar Renglón`.

---

## 2. Cómo Cobrar y Calcular el Cambio

1. Cuando termine de agregar los dulces, presione la tecla **F12** o dé clic en el botón verde grande **COBRAR**.
2. Aparecerá una ventana grande:
   - Verá el **TOTAL A COBRAR** en números gigantes.
   - Haga clic en el botón del billete con el que le pagan (`$20`, `$50`, `$100`, `$200`, `$500`) o escriba la cantidad en el recuadro "Paga con:".
   - **El sistema calculará automáticamente el CAMBIO A ENTREGAR en letras grandes y color verde.**
   - Opciones activadas por defecto:
     - `[✓] Imprimir Ticket`
     - `[✓] Abrir Cajón`
3. Presione la tecla **Enter** o clic en **CONFIRMAR COBRO**.
4. ¡Listo! La venta se guardará, **el cajón de dinero se abrirá al instante** para entregar el cambio y **se imprimirá el ticket de compra**.
5. Para abrir el cajón en cualquier momento (por ejemplo para dar cambio o ingresar billetes), presione la tecla **F8** o haga clic en el botón **Abrir Cajón (F8)**.

---

## 3. Cómo Administrar el Inventario y Dulces

Haga clic en la pestaña **[F2] INVENTARIO**.

### Ver dulces que están por agotarse:
- Los productos con pocas piezas aparecen marcados en color **rojo o rosado**.
- Puede marcar la casilla `[✓] Ver solo dulces por agotarse` para hacer su lista de compras antes de ir a la dulcería mayorista.

### Cuando llegan cajas nuevas (Entrada Rápida):
1. Seleccione el dulce en la lista.
2. Haga clic en el botón naranja **`+ Agregar Mercancía (Stock)`**.
3. Escriba cuántas piezas llegaron (por ejemplo: `24` o `50`) y presione **Enter**.
4. ¡El stock se sumará al instante sin tener que editar precios ni códigos!

### Registrar un dulce nuevo:
1. Haga clic en **`+ Nuevo Dulce`**.
2. Escanee o escriba su código, escriba el nombre, el precio que le costó a usted y el precio al que lo vende al público.
3. Si es un dulce que se vende mucho, marque la casilla **"Marcar como Dulce Favorito"** para que aparezca en los botones rápidos de venta.
4. Haga clic en **Guardar**.

---

## 4. Corte de Caja y Cierre del Día

Haga clic en la pestaña **[F3] CORTE DE CAJA**.

### Al abrir la tienda en la mañana:
- Si la caja está cerrada, dé clic en **`ABRIR NUEVO TURNO DE CAJA`**.
- Ingrese su dinero inicial para dar cambio (ej. `$200.00`) y presione **Enter**.

### Registrar pagos o gastos menores durante el día:
- **Si le paga a un repartidor o compra bolsas:** Dé clic en **`(-) Salida de Dinero (Gasto)`**, ingrese el monto (ej. `$85.00`) y el motivo (ej. *Pago repartidor Sabritas*).
- **Si mete morralla extra:** Dé clic en **`(+) Entrada de Dinero`**.

### En la noche al cerrar la dulcería:
1. Haga clic en **`REALIZAR CORTE Y CERRAR TURNO`**.
2. La pantalla le mostrará el resumen exacto:
   - Fondo con el que empezó
   - (+) Total de ventas en efectivo
   - (+) Entradas extras
   - (-) Gastos o pagos realizados
   - **TOTAL QUE DEBE HABER EN EL CAJÓN**
   - **Su Ganancia estimada del día**
3. Cuente su dinero en efectivo e ingréselo para confirmar que no falte ni sobre dinero.
4. Haga clic en **Finalizar Corte**. Se guardará un archivo de texto con el comprobante en la carpeta `cortes` y podrá imprimir el comprobante térmico directamente a su impresora.

---

## 5. Respaldo a Memoria USB (¡Muy Importante!)

Al ser una computadora sin internet, hacer una copia de seguridad a su memoria USB evita que pierda su información si la computadora se llega a descomponer o apagar por un corte de luz.

1. Conecte su memoria USB a la computadora.
2. Vaya a la pestaña **[F5] AJUSTES / USB**.
3. Haga clic en el botón azul: **`COPIAR RESPALDO A MEMORIA USB`**.
4. Seleccione su memoria USB (ejemplo: Disco `E:\` o `F:\`) y dé clic en **Aceptar**.
5. ¡Listo! En 2 segundos tendrá una copia de todos sus productos y ventas segura en su memoria.
   *(Se recomienda hacerlo una vez por semana o al final de cada quincena).*

---

## 6. Configuración de Impresora y Cajón de Dinero

En la pestaña **[F5] AJUSTES / USB** encontrará la sección central **Impresora y Cajón de Dinero**:

### 1. Conexión del Equipo:
- **Impresora:** Conéctela por USB a la computadora. Windows XP la detectará (ej. `POS-58`, `POS-80` o `Generic / Text Only`).
- **Cajón de Dinero:** Conecte el cable RJ11 (parecido al cable telefónico) en el conector marcado como **DK** o **Drawer** en la parte trasera de la impresora térmica.

### 2. Probar y Configurar en el Sistema:
1. En **Impresora de Tickets**, seleccione su impresora o deje `(Predeterminada de Windows)`.
2. Haga clic en **`🖨 Probar Impresión de Ticket`** para confirmar que la impresora saca papel.
3. Haga clic en **`💵 Probar Abrir Cajón`** para verificar que el cajón se abra de inmediato.
4. Elija el ancho de su papel:
   - `58 mm (32 car.)`: Para impresoras térmicas pequeñas estándar de 58 milímetros.
   - `80 mm (40 car.)`: Para impresoras térmicas grandes de 80 milímetros.
5. Deje marcadas las casillas automáticas si desea que imprima y abra el cajón en cada venta.
6. Haga clic en **`💾 Guardar Cambios de Impresora`**.

### 3. Apertura Manual y Reimpresión:
- **Abrir Cajón sin Venta:** Presione la tecla **F8** en cualquier momento o haga clic en el botón **`Abrir Cajón (F8)`**.
- **Reimprimir un Ticket Pasado:** Vaya a **[F4] HISTORIAL**, seleccione la venta deseada en la lista y haga clic en **`🖨 Reimprimir Ticket`**.

---

## ⌨️ Resumen de Teclas Rápidas
| Tecla | Acción |
|---|---|
| **F1** | Ir a la pantalla de Ventas |
| **F2** | Ir al Inventario |
| **F3** | Ir al Corte de Caja |
| **F4** | Ir al Historial de Ventas |
| **F5** | Ir a Ajustes y Respaldos |
| **F8** | **Abrir Cajón de Dinero (Manual)** |
| **F12** | Cobrar venta actual |
| **Enter** | Aceptar / Agregar producto / Confirmar cobro |
| **Esc** | Cancelar o cerrar ventanitas emergentes |
