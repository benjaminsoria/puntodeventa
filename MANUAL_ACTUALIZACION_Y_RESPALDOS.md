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

## 📦 Parte 1: Cómo instalar la actualización (Exportación de Etiquetas en .doc) sin afectar tus datos

Los únicos archivos de código modificados/agregados en esta actualización son:
1. `inventario.py` (Nuevo botón "Exportar Etiquetas (.doc)" y ventana de opciones en la pestaña de Inventario).
2. `etiquetas.py` (Módulo autónomo para formatear etiquetas de 1.5 cm x 5.0 cm a 68 por página y guardarlas en el Escritorio).
3. `MANUAL_DE_USUARIO.md` *(Documentación actualizada)*.

> **GARANTÍA DE SEGURIDAD PARA TU BASE DE DATOS:**  
> La estructura de la base de datos **`dulceria.db` no sufre ninguna modificación ni requiere migraciones**. Tus productos, precios, historial de ventas, cortes de caja y turnos se mantienen 100% intactos.

---

### Procedimiento Recomendado de Actualización (Paso a Paso):

#### Paso 1: Cerrar el programa en la computadora de la dulcería
Asegúrate de que el Punto de Venta esté completamente cerrado antes de copiar o reemplazar archivos.

#### Paso 2: Respaldo preventivo (Recomendado)
Antes de copiar archivos, haz una copia de seguridad rápida de tu base de datos `dulceria.db` en tu memoria USB (ver Parte 2).

#### Paso 3: Preparar la memoria USB con los archivos actualizados
En la memoria USB (Pendrive), copia **únicamente los siguientes archivos**:
- `inventario.py`
- `etiquetas.py`
- `MANUAL_DE_USUARIO.md` *(opcional)*
- `MANUAL_ACTUALIZACION_Y_RESPALDOS.md` *(opcional)*

*(⚠️ NUNCA copies ni lleves el archivo `dulceria.db` desde tu máquina personal hacia la tienda, para no sobreescribir las ventas reales de la dulcería).*

#### Paso 4: Pegar en la computadora de la dulcería
1. Conecta la memoria USB en la computadora de la dulcería.
2. Abre la memoria USB y copia los archivos `inventario.py` y `etiquetas.py`.
3. Ve a la carpeta donde está instalado el sistema (usualmente `C:\puntodeventa\` o en el Escritorio).
4. Pega los archivos (`Ctrl + V`). Cuando Windows te pregunte si deseas **Reemplazar / Sobreescribir**, selecciona **"Sí a todo"**.

#### Paso 5: Abrir el sistema y generar tus etiquetas
1. Inicia el sistema con el acceso directo habitual (`iniciar_pos.bat`).
2. Presiona la tecla **F2** o haz clic en la pestaña **[F2] INVENTARIO**.
3. En la barra de botones inferior verás el nuevo botón morado:  
   **`Exportar Etiquetas (.doc)`**.
4. Haz clic en él. Aparecerá la ventana de opciones:
   - Puedes exportar todos los dulces, o solo los que tengas filtrados.
   - Puedes indicar cuántas copias por dulce deseas (por defecto 1 copia para mostrador).
5. Presiona **Enter** o haz clic en **`Generar Etiquetas en Escritorio`**.
6. En tu **Escritorio** aparecerá el archivo generado con la fecha del día:  
   ```text
   etiquetas_AAAA-MM-DD.doc
   ```
7. Ábrelo con Microsoft Word, WordPad o LibreOffice y verás la cuadrícula lista con 68 etiquetas por página para mandar a imprimir.

---

## 🖨️ Historial de Actualizaciones Previas (Impresora 70 mm)
*(Para consultar cómo configurar impresoras de 70 mm en Ajustes F5, consulte la sección anterior en este mismo manual).*

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
