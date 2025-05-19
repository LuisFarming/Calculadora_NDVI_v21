# Proyecto de Procesamiento de Imágenes para Agricultura

Este proyecto es una herramienta en desarrollo para el procesamiento de imágenes aéreas o satelitales, enfocada en la aplicación de índice de vegetación NDVI para la agricultura de precisión.

## ¿Qué hace actualmente?

La aplicación permite cargar y procesar imágenes (especificar formatos si aplica, ej. GeoTIFF) para calcular y visualizar resultados como índices de vegetación (ej. NDVI, NDRE) u otros mapas temáticos.

## Estado Actual y Problemas Conocidos

Este proyecto se encuentra activamente en desarrollo y mejora.

**Problema Conocido:** Actualmente, al visualizar los resultados del procesamiento, se ha detectado un problema donde los píxeles con valores "No Data" (áreas fuera de la zona de interés, bordes, etc.) están siendo representados con un color amarillo. Este color parece estar confundiéndose con la paleta de colores utilizada para los valores medios del índice, creando un rectángulo amarillo que **oculta parcialmente o completamente el mapa de resultados**, dificultando la visualización del análisis.

Estamos investigando la causa de esta asignación incorrecta de color a los valores "No Data" y trabajando para solucionarlo en futuras actualizaciones.

## Próximos Pasos

* Corregir el problema de visualización de los valores "No Data".

* Mejorar la interfaz de usuario.

* Añadir opciones de procesamiento adicionales (si aplica).

* Optimizar el rendimiento.

## Cómo Usar (Funcionalidad Actual)

1. (Instrucciones básicas sobre cómo cargar una imagen y ejecutar el procesamiento, si la interfaz lo permite).

2. (Describir dónde se muestra el resultado).

## Requisitos

* (Listar cualquier librería o dependencia necesaria, ej. GDAL, NumPy, etc.)

* Python 3.x

## Instalación (desde código fuente)

1. Clona o descarga este repositorio.

2. (Instrucciones para instalar dependencias, ej. `pip install -r requirements.txt` si tienes un archivo requirements.txt).

3. (Instrucciones para ejecutar el script principal).

## Desarrollado por

LuisFarming

Agradecemos tu comprensión mientras trabajamos en mejorar esta herramienta. ¡Tus comentarios y sugerencias son bienvenidos!
