# 🚀 Guía de Instalación para Windows XP (100% Sin Internet)

Este punto de venta fue programado especialmente para funcionar en **Windows XP (Service Pack 3)** de forma local, rápida y sin necesidad de conexión a internet ni librerías pesadas.

---

## 📋 ¿Qué necesitas? (Solo por única vez)
En cualquier computadora con internet (o cibercafé), descarga y guarda en una memoria USB (Pendrive):
1. El instalador oficial de **Python 3.4.4 (32-bit)** para Windows XP:
   - Nombre del archivo: `python-3.4.4.msi`
   - Enlace oficial: [https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi](https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi)
2. La carpeta completa de este proyecto: `puntodeventa`.

---

## 🛠️ Pasos de Instalación en la computadora con Windows XP

### Paso 1: Conectar la Memoria USB
Conecta la memoria USB en cualquier puerto de la computadora de la dulcería.

### Paso 2: Instalar Python 3.4.4
1. Abre la memoria USB y haz doble clic sobre el archivo `python-3.4.4.msi`.
2. Selecciona **"Install for all users"** y haz clic en **Next**.
3. Deja la ruta por defecto (`C:\Python34\`) y haz clic en **Next**.
4. **IMPORTANTE:** En la lista de opciones que aparece:
   - Busca al final la opción **"Add python.exe to Path"**.
   - Haz clic sobre la pequeña "X" roja y selecciona **"Will be installed on local hard drive"** (para que se agregue al sistema).
   - Verifica que **"Tcl/Tk"** esté seleccionado (viene activado por defecto).
5. Haz clic en **Next** y luego en **Finish**. ¡Toma menos de 1 minuto!

### Paso 3: Copiar la carpeta del Punto de Venta
1. Copia la carpeta `puntodeventa` desde tu memoria USB y pégala en el disco local:
   - Ruta recomendada: `C:\puntodeventa` (o directamente en el Escritorio).

### Paso 4: Crear el acceso directo en el Escritorio
1. Abre la carpeta `puntodeventa`.
2. Haz clic derecho sobre el archivo `iniciar_pos.bat`.
3. Selecciona **Enviar a** ➔ **Escritorio (crear acceso directo)**.
4. *(Opcional)* En el escritorio, haz clic derecho al nuevo acceso directo, selecciona **Cambiar nombre** y nómbralo: **"Punto de Venta - Dulcería"**.

---

## ▶️ ¿Cómo iniciar el programa?
Simplemente haz **doble clic en el icono del Punto de Venta en el Escritorio**.

- Se abrirá la ventana limpia del sistema sin ventanas negras de fondo.
- No requiere contraseñas complicadas ni configuraciones adicionales.
- Ya incluye 20 dulces populares precargados con precios para que tus papás puedan probarlo de inmediato.

---

## 🔌 Requisitos y Conexión de Periféricos
- **Sistema Operativo:** Windows XP SP3 (también compatible con Windows 7, 8, 10 y 11).
- **Procesador:** Pentium III / Pentium 4 / Celeron o superior.
- **Memoria RAM:** 256 MB o más.
- **Espacio en Disco:** Menos de 50 MB en total.
- **Lector de Código de Barras (Opcional):** Cualquier lector USB tipo pistola (Plug & Play, no requiere drivers especiales).
- **Impresora de Tickets:** Compatible con cualquier impresora térmica (58mm u 80mm por USB, LPT o COM). Se comunica mediante el Spooler nativo de Windows XP sin requerir controladores especiales ni paquetes externos.
- **Cajón de Dinero:** Se conecta mediante cable RJ11 (tipo telefónico) directamente a la parte trasera de la impresora de tickets. El sistema envía el pulso ESC/POS para abrirlo de forma automática o con la tecla **F8**.
