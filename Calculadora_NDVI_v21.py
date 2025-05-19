# Importar módulos necesarios de Tkinter para la GUI
import tkinter as tk
# Importar PhotoImage para mostrar imágenes
from tkinter import filedialog, messagebox, ttk, scrolledtext, PhotoImage

# Importar módulos para el cálculo del NDVI
import rasterio
import numpy as np
import os

# Importar Pillow para manejar imágenes
from PIL import Image, ImageTk  # Importar Image y ImageTk

# --- Función para realizar el cálculo del NDVI ---
# Esta función es la misma lógica que usamos en los scripts anteriores


def calcular_ndvi(ruta_rojo, ruta_nir, ruta_salida, label_estado):
    """
    Calcula el NDVI a partir de las rutas de las bandas Roja y NIR,
    y guarda el resultado en la ruta de salida especificada.
    Actualiza una etiqueta de estado en la GUI.
    Retorna el array NDVI calculado si es exitoso, de lo contrario None.
    """
    # Validar que las rutas no estén vacías
    if not ruta_rojo or not ruta_nir or not ruta_salida:
        messagebox.showwarning(
            "Advertencia", "Por favor, especifica las rutas de los archivos de entrada y salida.")
        label_estado.config(text="Estado: Faltan rutas", foreground="red")
        return None  # Indicar que hubo un problema

    # Actualizar el estado en la GUI
    label_estado.config(text="Estado: Calculando...", foreground="orange")
    # Forzar la actualización de la GUI para que se actualice el texto cambie inmediatamente
    label_estado.update_idletasks()

    try:
        # --- Lógica del cálculo del NDVI ---
        # Imprimir en consola para depuración
        print(
            f"Iniciando cálculo para:\n Rojo: {ruta_rojo}\n NIR: {ruta_nir}\n Salida: {ruta_salida}")

        # Verificar si los archivos de entrada existen
        if not os.path.exists(ruta_rojo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_rojo}")
        if not os.path.exists(ruta_nir):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_nir}")

        # Abrir las bandas usando rasterio
        with rasterio.open(ruta_rojo) as src_rojo:
            banda_rojo = src_rojo.read(1)
            perfil_salida = src_rojo.profile

        with rasterio.open(ruta_nir) as src_nir:
            banda_nir = src_nir.read(1)

        # Convertir a tipo float32 para el cálculo
        banda_rojo_float = banda_rojo.astype('float32')
        banda_nir_float = banda_nir.astype('float32')

        # Calcular NDVI, manejando la división por cero y valores sin datos
        denominador = banda_nir_float + banda_rojo_float
        # Inicializar con NaN. Esto también maneja los nodata originales si rasterio los lee como tal.
        ndvi = np.full(banda_rojo_float.shape, np.nan, dtype='float32')

        # Máscara para píxeles donde el cálculo es válido (denominador no es cero y no son NaN originales si los hubiera)
        # Consideramos válido si el denominador no es cero Y si las bandas de entrada no eran NaN (aunque rasterio read(1) suele manejar esto)
        mascara_valida = (denominador != 0) & (
            ~np.isnan(banda_rojo_float)) & (~np.isnan(banda_nir_float))

        # Realizar el cálculo del NDVI solo para los píxeles válidos
        # Suprimir advertencias de NaN en la división
        with np.errstate(invalid='ignore'):
            ndvi[mascara_valida] = (banda_nir_float[mascara_valida] -
                                    banda_rojo_float[mascara_valida]) / denominador[mascara_valida]

        print("Cálculo de NDVI completado.")

        # --- Guardar el resultado ---
        perfil_salida.update(
            dtype=rasterio.float32,
            count=1,
            nodata=np.nan  # Asegurarse de que el archivo de salida tenga NaN como nodata
        )

        # Crear directorio de salida si no existe
        directorio_salida = os.path.dirname(ruta_salida)
        if directorio_salida and not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)

        with rasterio.open(ruta_salida, 'w', **perfil_salida) as dst:
            dst.write(ndvi, 1)

        # --- Fin de la lógica del cálculo ---

        # Mostrar mensaje de éxito y actualizar estado
        label_estado.config(
            text="Estado: ¡Cálculo completado!", foreground="green")
        # El messagebox ya bloquea la ejecución hasta que se cierra, por lo que la GUI se actualiza después.
        messagebox.showinfo(
            "Éxito", f"El archivo NDVI se ha guardado en:\n{ruta_salida}")
        # Imprimir en consola para depuración
        print("Cálculo y guardado exitoso.")
        return ndvi  # Retornar el array NDVI calculado para la visualización

    except FileNotFoundError as e:
        # Manejar error si los archivos de entrada no existen
        error_msg = f"Error de Archivo: {e}"
        label_estado.config(text="Estado: Error de Archivo", foreground="red")
        messagebox.showerror("Error de Archivo", error_msg)
        print(error_msg)  # Imprimir en consola para depuración
        return None

    except rasterio.errors.RasterioIOError as e:
        # Manejar errores de lectura/escritura de archivos raster
        error_msg = f"Error de E/S de Rasterio: {e}"
        label_estado.config(text="Estado: Error de Rasterio", foreground="red")
        messagebox.showerror("Error de Rasterio", error_msg)
        print(error_msg)  # Imprimir en consola para depuración
        return None

    except Exception as e:
        # Manejar cualquier otro error inesperado
        error_msg = f"Ocurrió un error inesperado: {e}"
        label_estado.config(text="Estado: Error General", foreground="red")
        messagebox.showerror("Error", error_msg)
        print(error_msg)  # Imprimir en consola para depuración
        return None

# --- Función para aplicar paleta de colores y mostrar imagen ---


def mostrar_ndvi_en_gui(ndvi_array, image_label):
    """
    Aplica una paleta de colores al array NDVI y lo muestra en un widget Label de Tkinter.
    Asegura que los valores NaN se muestren en negro.
    """
    print("Entrando a mostrar_ndvi_en_gui...")  # Debug print

    if ndvi_array is None:
        print("NDVI array is None, clearing image.")  # Debug print
        image_label.config(image='')  # Limpiar imagen si no hay datos
        image_label.image = None
        root.update_idletasks()  # Try updating GUI
        return

    # Debug print
    print(f"NDVI array shape: {ndvi_array.shape}, dtype: {ndvi_array.dtype}")

    # Definir la paleta de colores (mapeo lineal de NDVI a RGB)
    # NDVI va de -1 a +1
    # Queremos mapear:
    # -1 (agua/nubes) -> Café oscuro [165, 42, 42]
    # 0 (suelo) -> Amarillo/Marrón claro [255, 215, 0]
    # +1 (vegetación) -> Verde intenso [34, 139, 34]

    # Definir colores clave (RGB 0-255) con tonalidades ajustadas
    # Brown - Un café más rojizo
    color_bajo = np.array([165, 42, 42], dtype=np.uint8)
    # Gold - Un amarillo más dorado
    color_medio = np.array([255, 215, 0], dtype=np.uint8)
    # ForestGreen - Un verde bosque
    color_alto = np.array([34, 139, 34], dtype=np.uint8)
    # Negro para valores sin datos (NaN)
    color_nodata = np.array([0, 0, 0], dtype=np.uint8)

    # Crear una imagen RGB completamente negra con las mismas dimensiones que el array NDVI
    height, width = ndvi_array.shape  # Usar las dimensiones originales
    rgb_image_array = np.full((height, width, 3), color_nodata, dtype=np.uint8)

    print("RGB image array initialized with nodata color (black).")  # Debug print

    # Crear una máscara para identificar los píxeles que NO son NaN
    mascara_no_nan = ~np.isnan(ndvi_array)
    print(f"Shape of mascara_no_nan: {mascara_no_nan.shape}")  # Debug print
    print(f"Number of non-NaN pixels: {np.sum(mascara_no_nan)}")  # Debug print

    # Aplicar la lógica de color solo a los píxeles que NO son NaN
    ndvi_validos = ndvi_array[mascara_no_nan]
    print(f"Shape of ndvi_validos: {ndvi_validos.shape}")  # Debug print
    print(f"Size of ndvi_validos: {ndvi_validos.size}")  # Debug print
    # --- Nueva línea de depuración para imprimir el dtype ---
    print(f"Dtype of ndvi_validos: {ndvi_validos.dtype}")  # Debug print
    # --- Fin de la nueva línea de depuración ---

    if ndvi_validos.size > 0:  # Asegurarse de que haya píxeles válidos
        print("Processing valid NDVI values...")  # Debug print
        # Imprimir estadísticas de los valores NDVI válidos
        # Corregido el formato de impresión para mostrar los valores
        print(f"Min NDVI valid: {np.min(ndvi_validos)}")  # Debug print
        print(f"Max NDVI valid: {np.max(ndvi_validos)}")  # Debug print
        print(f"Mean NDVI valid: {np.mean(ndvi_validos)}")  # Debug print

        # Asegurar que los valores válidos estén dentro del rango [-1, 1]
        ndvi_validos_clipped = np.clip(ndvi_validos, -1, 1)
        # Normalizar al rango [0, 1]
        ndvi_normalized = (ndvi_validos_clipped + 1) / 2.0

        # Crear un array para almacenar los colores interpolados para los píxeles válidos
        colores_interpolados = np.empty((ndvi_validos.size, 3), dtype=np.uint8)

        # Interpolar colores basándose en el valor normalizado
        # Mapeo lineal: 0 a 0.5 -> color_bajo a color_medio
        #              0.5 a 1.0 -> color_medio a color_alto
        mascara_bajo_medio = ndvi_normalized < 0.5
        mascara_medio_alto = ndvi_normalized >= 0.5

        # Interpolar para el rango bajo-medio
        factores_bajo_medio = ndvi_normalized[mascara_bajo_medio] / 0.5
        colores_interpolados[mascara_bajo_medio] = (
            (1 - factores_bajo_medio[:, np.newaxis]) * color_bajo + factores_bajo_medio[:, np.newaxis] * color_medio).astype(np.uint8)
        # Debug print
        print(
            f"Assigned colors to {np.sum(mascara_bajo_medio)} pixels (bajo-medio range).")

        # Interpolar para el rango medio-alto
        factores_medio_alto = (ndvi_normalized[mascara_medio_alto] - 0.5) / 0.5
        colores_interpolados[mascara_medio_alto] = (
            (1 - factores_medio_alto[:, np.newaxis]) * color_medio + factores_medio_alto[:, np.newaxis] * color_alto).astype(np.uint8)
        # Debug print
        print(
            f"Assigned colors to {np.sum(mascara_medio_alto)} pixels (medio-alto range).")

        # Asignar los colores interpolados de vuelta al array de imagen RGB principal
        # ¡Importante! Solo asignamos a los píxeles que originalmente no eran NaN
        rgb_image_array[mascara_no_nan] = colores_interpolados

    else:
        print("No valid NDVI pixels found (ndvi_validos.size is 0).")  # Debug print

    print("Color assignment finished.")  # Debug print

    # Convertir el array RGB a una imagen de Pillow
    img_pil = Image.fromarray(rgb_image_array, 'RGB')

    print(f"Pillow image created with size: {img_pil.size}")  # Debug print

    # Redimensionar la imagen para que quepa en la GUI sin ser demasiado grande
    max_gui_width = 500  # Aumentar un poco el tamaño máximo para la visualización
    max_gui_height = 400  # Aumentar un poco el tamaño máximo para la visualización

    original_width, original_height = img_pil.size

    if original_width > max_gui_width or original_height > max_gui_height:
        print("Resizing image for GUI display.")  # Debug print
        # Calcular la nueva proporción manteniendo el aspecto
        ratio = min(max_gui_width / original_width,
                    max_gui_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        # Usar un buen filtro de redimensionamiento
        img_pil = img_pil.resize(
            (new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Resized image size: {img_pil.size}")  # Debug print

    # Convertir la imagen de Pillow a un formato que Tkinter pueda usar
    try:
        img_tk = ImageTk.PhotoImage(img_pil)
        print("Pillow image converted to ImageTk.PhotoImage.")  # Debug print
    except Exception as e:
        # Debug print
        print(f"Error converting Pillow image to ImageTk.PhotoImage: {e}")
        messagebox.showerror("Error de Visualización",
                             f"No se pudo convertir la imagen para mostrar: {e}")
        image_label.config(image='')
        image_label.image = None
        root.update_idletasks()
        return

    # Mostrar la imagen en el widget Label
    try:
        image_label.config(image=img_tk)
        # Guardar una referencia a la imagen para evitar que sea eliminada por el recolector de basura
        image_label.image = img_tk
        print("Image set on label.")  # Debug print
        root.update_idletasks()  # Try updating GUI after setting image
        print("GUI updated after setting image.")  # Debug print
    except Exception as e:
        print(f"Error setting image on label: {e}")  # Debug print
        messagebox.showerror("Error de Visualización",
                             f"No se pudo mostrar la imagen en la ventana: {e}")
        image_label.config(image='')
        image_label.image = None
        root.update_idletasks()


# --- Configuración de la GUI con Tkinter ---

# Crear la ventana principal
root = tk.Tk()
root.title("Calculadora de NDVI Simple (Tkinter)")

# Configurar el tamaño inicial de la ventana
# root.geometry("600x350") # Eliminamos el tamaño fijo inicial
# Permitir que la ventana se pueda redimensionar (True, True para ancho y alto)
root.resizable(True, True)

# Crear un Notebook (widget de pestañas)
notebook = ttk.Notebook(root)
# Usar fill=tk.BOTH y expand=True para que el notebook se expanda con la ventana
notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# --- Pestaña de Calculadora ---
frame_calculadora = ttk.Frame(notebook, padding="10")
# Añadir el frame al notebook con el texto de la pestaña
notebook.add(frame_calculadora, text='Calculadora')

# Configurar la expansión de columnas y filas dentro del frame de la calculadora
# Hacer que la columna de los Entry se expanda
frame_calculadora.columnconfigure(1, weight=1)
# Permitir que la fila que contiene la imagen se expanda
frame_calculadora.rowconfigure(5, weight=1)  # La fila 5 contendrá la imagen

# Widgets para la Banda Roja (B4)
label_rojo = ttk.Label(frame_calculadora, text="Ruta Banda Roja (B4):")
label_rojo.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)

# El width es solo un tamaño inicial, se expandirá con la columna
entry_rojo = ttk.Entry(frame_calculadora, width=50)
entry_rojo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Función para el botón de búsqueda de Banda Roja


def browse_rojo():
    filename = filedialog.askopenfilename(
        title="Seleccionar archivo Banda Roja (B4)",
        filetypes=(("GeoTIFF Files", "*.tif *.tiff *.jp2"),
                   ("All Files", "*.*"))
    )
    if filename:
        entry_rojo.delete(0, tk.END)
        entry_rojo.insert(0, filename)


boton_rojo = ttk.Button(
    frame_calculadora, text="Buscar...", command=browse_rojo)
boton_rojo.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)

# Widgets para la Banda NIR (B8)
label_nir = ttk.Label(frame_calculadora, text="Ruta Banda NIR (B8):")
label_nir.grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)

# El width es solo un tamaño inicial
entry_nir = ttk.Entry(frame_calculadora, width=50)
entry_nir.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Función para el botón de búsqueda de Banda NIR


def browse_nir():
    filename = filedialog.askopenfilename(
        title="Seleccionar archivo Banda NIR (B8)",
        filetypes=(("GeoTIFF Files", "*.tif *.tiff *.jp2"),
                   ("All Files", "*.*"))
    )
    if filename:
        entry_nir.delete(0, tk.END)
        entry_nir.insert(0, filename)


boton_nir = ttk.Button(frame_calculadora, text="Buscar...", command=browse_nir)
boton_nir.grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)

# Widgets para el Archivo de Salida NDVI
label_salida = ttk.Label(frame_calculadora, text="Ruta Archivo Salida NDVI:")
label_salida.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)

# El width es solo un tamaño inicial
entry_salida = ttk.Entry(frame_calculadora, width=50)
entry_salida.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

# Función para el botón de guardar archivo de salida


def save_as_ndvi():
    filename = filedialog.asksaveasfilename(
        title="Guardar archivo NDVI como...",
        defaultextension=".tif",
        filetypes=(("GeoTIFF Files", "*.tif"), ("All Files", "*.*"))
    )
    if filename:
        entry_salida.delete(0, tk.END)
        entry_salida.insert(0, filename)


boton_salida = ttk.Button(
    frame_calculadora, text="Guardar como...", command=save_as_ndvi)
boton_salida.grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)

# Botón para Calcular NDVI


def on_calcular_click():
    boton_calcular.config(state=tk.DISABLED)
    ruta_rojo = entry_rojo.get()
    ruta_nir = entry_nir.get()
    ruta_salida = entry_salida.get()

    # Llamar a la función de cálculo
    ndvi_resultado_array = calcular_ndvi(
        ruta_rojo, ruta_nir, ruta_salida, label_estado_calculadora)

    # Si el cálculo fue exitoso, mostrar la imagen
    if ndvi_resultado_array is not None:
        mostrar_ndvi_en_gui(ndvi_resultado_array, label_imagen_ndvi)

    boton_calcular.config(state=tk.NORMAL)


boton_calcular = ttk.Button(
    frame_calculadora, text="Calcular NDVI", command=on_calcular_click)
boton_calcular.grid(row=3, column=0, columnspan=3, pady=15)

# Etiqueta para mostrar el Estado en la pestaña Calculadora
label_estado_calculadora = ttk.Label(
    frame_calculadora, text="Estado: Listo", foreground="blue")
label_estado_calculadora.grid(
    row=4, column=0, columnspan=3, sticky=tk.W + tk.E, padx=5, pady=5)

# Widget Label para mostrar la imagen del NDVI
# Usamos sticky para que se expanda en todas direcciones dentro de su celda
label_imagen_ndvi = ttk.Label(frame_calculadora)
label_imagen_ndvi.grid(row=5, column=0, columnspan=3,
                       sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)


# --- Pestaña de Información ---
frame_info = ttk.Frame(notebook, padding="10")
# Añadir el frame al notebook con el texto de la pestaña
notebook.add(frame_info, text='Información')

# Configurar la expansión dentro del frame de información
# Permitir que la columna del texto se expanda
frame_info.columnconfigure(0, weight=1)
# Permitir que la fila del texto se expanda
frame_info.rowconfigure(0, weight=1)

# Texto de instrucciones y leyenda de colores
instrucciones_texto = """
Instrucciones de uso:

1.  **Seleccionar Banda Roja (B4):** Haz clic en "Buscar..." junto a "Ruta Banda Roja (B4)" y selecciona el archivo GeoTIFF o JP2 correspondiente a la banda Roja (B4) de tu imagen Sentinel-2.
2.  **Seleccionar Banda NIR (B8):** Haz clic en "Buscar..." junto a "Ruta Banda NIR (B8)" y selecciona el archivo GeoTIFF o JP2 correspondiente a la banda Infrarrojo Cercano (B8) de tu imagen Sentinel-2.
    * La aplicación funciona con imágenes de Sentinel-2 que ya estén recortadas a tu área de interés. Asegúrate de usar las bandas correctas (B4 y B8).
3.  **Especificar Archivo de Salida:** Haz clic en "Guardar como..." junto a "Ruta Archivo Salida NDVI" y elige la ubicación y el nombre para guardar el archivo GeoTIFF resultante con el cálculo del NDVI.
4.  **Calcular NDVI:** Una vez que hayas especificado las tres rutas, haz clic en el botón "Calcular NDVI".
5.  **Ver Resultado:** La aplicación calculará el NDVI, guardará el archivo GeoTIFF de salida y **mostrará una visualización del mapa de NDVI con una paleta de colores en la parte inferior de esta pestaña "Calculadora"**. Las áreas fuera de tu estudio (sin datos) se mostrarán en color negro para distinguirlas. Puedes abrir el archivo GeoTIFF de salida en un software GIS (como QGIS o ArcGIS) para un análisis más detallado.

El estado del proceso se mostrará en la parte inferior de la pestaña "Calculadora". Si ocurre algún error, se mostrará un mensaje.

---

Leyenda de Colores NDVI (Interpretación General):

Esta paleta de colores representa los valores de NDVI de la siguiente manera:

* **Negro:** Áreas sin datos (fuera del área de estudio, nubes densas, etc.).
* **Café Oscuro:** Valores de NDVI bajos (típicamente entre -1.0 y 0.1). Representa áreas sin vegetación, como cuerpos de agua, nieve, rocas o suelo desnudo.
* **Amarillo/Marrón Claro:** Valores de NDVI medios-bajos (típicamente entre 0.1 y 0.3). Puede indicar áreas con vegetación escasa, pastos secos, cultivos jóvenes o en etapas tempranas de desarrollo.
* **Verde:** Valores de NDVI altos (típicamente entre 0.3 y 1.0). Representa áreas con vegetación densa y saludable, como bosques, cultivos maduros o vegetación vigorosa.

Ten en cuenta que la interpretación exacta puede variar ligeramente dependiendo del tipo de vegetación y las condiciones específicas del área de estudio.

"""

# Usar scrolledtext para tener una barra de desplazamiento automática
# Usar sticky para que el widget se expanda dentro de su celda/frame
text_area_instrucciones = scrolledtext.ScrolledText(
    frame_info, wrap=tk.WORD)  # Eliminamos width/height fijos aquí
text_area_instrucciones.insert(tk.INSERT, instrucciones_texto)
# Hacer el texto de solo lectura
text_area_instrucciones.config(state='disabled')
text_area_instrucciones.grid(row=0, column=0, sticky=(
    tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)  # Usar grid y sticky

# Etiqueta de "creado por"
label_creado_por = ttk.Label(
    frame_info, text="Creado por LuisFarming", foreground="gray")
# Usar grid y sticky para alinear abajo a la derecha
label_creado_por.grid(row=1, column=0, sticky=tk.S + tk.E, padx=10, pady=5)


# --- Iniciar el bucle principal de la GUI ---
# Esto mantiene la ventana abierta y responde a las interacciones del usuario
if __name__ == "__main__":
    root.mainloop()
