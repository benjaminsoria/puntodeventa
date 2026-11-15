# 💾 Guía de Actualización Segura y Respaldos en Memoria USB
## Punto de Venta - Dulcería

Esta guía explica paso a paso cómo actualizar el sistema en la computadora de la dulcería **sin perder ni alterar ningún dato existente** (productos, inventario, precios, ventas y cortes de caja), y cómo realizar respaldos periódicos en una memoria USB (Pendrive).

---

## 🔒 Regla de Oro: ¿Dónde está guardada tu información?

Toda la información del negocio vive en un **único archivo**:
```text
C:\puntodeventa\dulceria.db
```
En este archivo SQLite se almacenan:
- Catálogo de dulces, códigos de barras y precios de compra/venta.
- Existencias de inventario.
- Historial completo de ventas, cobros y folios de tickets.
- Turnos y cortes de caja diarios.
- Nombre de la tienda, teléfono y configuración de periféricos.

> **IMPORTANTE:**  
> Mientras **NUNCA sobreescribas ni borres el archivo `dulceria.db`** de tu computadora de trabajo, tus datos estarán 100% a salvo en cualquier actualización de código.

---

## 📦 Parte 1: Cómo instalar esta actualización (Impresora 70 mm) sin afectar tus datos

Los únicos archivos de código modificados en esta actualización son:
1. `ticket.py` (Lógica de formateo a 70 mm, 58 mm y 80 mm).
2. `configuracion.py` (Nueva opción visual de 70 mm en Ajustes).

La estructura de la base de datos **no requiere migraciones**, ya que el campo de ancho de ticket ya estaba preparado para almacenar valores enteros (como `36` columnas).

### Procedimiento Recomendado (Paso a Paso):

#### Paso 1: Cerrar el programa en la computadora de la dulcería
Asegúrate de que el Punto de Venta esté completamente cerrado antes de copiar archivos.

#### Paso 2: Copiar el respaldo preventivo
Antes de cualquier cambio, haz una copia de seguridad de tu base de datos actual (ver Parte 2).

#### Paso 3: Preparar la memoria USB con los archivos actualizados
En la memoria USB, copia **únicamente los archivos de código actualizados**:
- `ticket.py`
- `configuracion.py`
- `MANUAL_DE_USUARIO.md` *(opcional, documentación)*
- `MANUAL_ACTUALIZACION_Y_RESPALDOS.md` *(opcional)*

*(Evita llevar o sobreescribir el archivo `dulceria.db` desde la máquina de desarrollo a la tienda).*

#### Paso 4: Pegar en la computadora de la tienda
1. Conecta la memoria USB en la computadora de la dulcería.
2. Abre la memoria y copia los archivos `ticket.py` y `configuracion.py`.
3. Ve a la carpeta del sistema (por ejemplo `C:\puntodeventa\` o donde lo tengas instalado).
4. Pega los archivos. Cuando Windows pregunte si deseas **Reemplazar / Sobreescribir**, haz clic en **Sí a todo**.

#### Paso 5: Abrir el sistema y configurar los 70 mm
1. Inicia el sistema con el acceso directo habitual (`iniciar_pos.bat`).
2. Presiona la tecla **F5** o haz clic en **[F5] AJUSTES / USB**.
3. En la sección central **"2. Impresora Térmica y Cajón de Dinero"**:
   - En **Ancho de Papel**, verás la nueva opción:  
     🔘 **70 mm (36 car.)**
   - Selecciónala.
4. Haz clic en **`🖨 Probar Impresión de Ticket`** para comprobar que el ticket de prueba imprima en los 36 caracteres exactos.
5. Haz clic en **`💾 Guardar Cambios de Impresora`**.

---

## 🛡️ Parte 2: Manual de Respaldos en Memoria USB

Hacer respaldos periódicos en una memoria USB garantiza que, ante cualquier fallo eléctrico, virus o avería del disco duro, toda la información de la dulcería se recupere en minutos.

---

### Método 1: Respaldo directo desde el sistema (El más fácil y rápido)

El sistema incluye una función automatizada para exportar una copia fechada a tu memoria USB.

1. **Conecta tu memoria USB** en cualquier puerto de la computadora.
2. Abre el Punto de Venta y ve a la pestaña **[F5] AJUSTES / USB**.
3. En la columna derecha (3. Respaldos), haz clic en el botón azul:  
   **`COPIAR A MEMORIA USB`**.
4. Se abrirá una ventana del explorador de Windows:
   - Selecciona la unidad de tu memoria USB (por ejemplo `Disco extraíble (E:)` o `(F:)`).
   - Puedes crear una carpeta llamada `Respaldos_Dulceria` si deseas tenerlos ordenados.
   - Haz clic en **Aceptar**.
5. Aparecerá un mensaje de éxito:
   > *"¡Respaldo Exitoso! Se ha guardado una copia completa de la base de datos en su memoria USB: respaldo_dulceria_AAAAMMDD_HHMMSS.db"*
6. ¡Listo! El archivo contendrá la fecha y hora exacta del respaldo.

---

### Método 2: Respaldo manual desde el Explorador de Windows (Sin abrir el programa)

Si la computadora está apagada o prefieres hacerlo directamente desde Windows:

1. Conecta tu memoria USB.
2. Abre **Mi PC** (o *Equipo*) y entra a la carpeta donde está instalado el sistema:
   ```text
   C:\puntodeventa\
   ```
3. Busca el archivo llamado:
   ```text
   dulceria.db
   ```
4. Haz clic derecho sobre él y selecciona **Copiar** (o presiona `Ctrl + C`).
5. Abre tu memoria USB.
6. Haz clic derecho en un espacio en blanco y selecciona **Pegar** (o presiona `Ctrl + V`).
7. *(Recomendado)* Cambia el nombre del archivo en la memoria para identificarlo, por ejemplo:
   ```text
   dulceria_respaldo_2026_11_15.db
   ```

---

### Método 3: Respaldo Local Rápido (En la misma computadora)

Si no tienes una memoria USB a la mano en ese momento:
1. En **[F5] AJUSTES / USB**, haz clic en **`Guardar Respaldo Local Rápido`**.
2. El sistema guardará una copia en la carpeta `C:\puntodeventa\respaldos\`.
3. Verás la lista de las últimas copias generadas en la tabla inferior de esa misma pantalla.

---

## 🔄 Parte 3: ¿Cómo restaurar un respaldo si ocurre una emergencia?

Si en algún momento necesitas recuperar la información de una fecha anterior:

### Opción A: Desde la interfaz del sistema
1. Conecta la memoria USB con tu respaldo.
2. Ve a **[F5] AJUSTES / USB**.
3. En la columna derecha, haz clic en el botón rojo: **`Restaurar Base de Datos`**.
4. Selecciona el archivo `.db` que tienes guardado en tu memoria USB.
5. El sistema te pedirá confirmación:
   - *Nota de seguridad:* Antes de restaurar, el sistema crea automáticamente un respaldo de lo que tienes actualmente.
6. Al confirmar, los datos se cargarán de inmediato. Cierra y vuelve a abrir el programa.

### Opción B: Restauración manual
1. Cierra el Punto de Venta.
2. Ve a la carpeta `C:\puntodeventa\`.
3. Renombra el archivo dañado como `dulceria_vieja.db`.
4. Copia el archivo de respaldo desde tu USB a `C:\puntodeventa\`.
5. Renómbralo exactamente como:
   ```text
   dulceria.db
   ```
6. Vuelve a abrir el Punto de Venta con `iniciar_pos.bat`.

---

## 📅 Buenas Prácticas de Respaldo

- **Antes de cualquier actualización:** Siempre realiza un respaldo en tu USB antes de reemplazar archivos de código.
- **Frecuencia recomendada:** Al menos una vez por semana o cada fin de quincena tras realizar el corte de caja de la noche.
- **Mantener varias copias:** No borres los respaldos anteriores de la USB; como cada archivo pesa menos de 1 MB, puedes guardar cientos de respaldos sin llenar tu memoria.
- **Cuidado del pendrive:** Guarda la memoria USB en un lugar seguro y protegido del calor o humedad de la tienda.
