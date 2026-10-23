# ConcreBasics
Aplicación en Python para el diseño, cálculo y dosificación de mezclas de concreto siguiendo los lineamientos del método ACI (American Concrete Institute).
# Diseño de Mezclas de Concreto - Método ACI

Una herramienta desarrollada en Python para automatizar y facilitar el diseño de mezclas de concreto normal (peso normal) utilizando el método basado en la práctica estándar del comité 211 del ACI (ACI 211.1). Esta aplicación permite a ingenieros civiles, estudiantes y profesionales de la construcción calcular rápidamente las proporciones óptimas de cemento, agua y agregados (fino y grueso) requeridas para una resistencia de diseño específica.

## Características Principales

*   **Cálculo Automatizado:** Determina las cantidades de material (kg/m³) basándose en la resistencia a la compresión deseada ($f'_c$), el tamaño máximo del agregado y el revenimiento (asentamiento).
*   **Ajuste por Humedad:** Permite ingresar los porcentajes de humedad natural y absorción de los agregados para corregir la cantidad de agua de mezclado.
*   **Fácil de Usar:** Interfaz clara para la entrada de parámetros de los materiales (módulo de finura, peso específico, masa unitaria compactada).
*   **Resultados Detallados:** Presenta un resumen claro con las proporciones finales de dosificación (en peso y/o volumen).

## Requisitos Previos

*   Python 3.8 o superior.
*   Dependencias adicionales *(modificar según las librerías que uses, ej. numpy, pandas, tkinter o PyQt si tiene interfaz gráfica)*.

## Instalación

1.  Clona este repositorio en tu máquina local:
    ```bash
    git clone https://github.com/tu-usuario/nombre-del-repo.git
    ```
2.  Navega al directorio del proyecto:
    ```bash
    cd nombre-del-repo
    ```
3.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Ejecuta el archivo principal para iniciar la aplicación. Sigue las instrucciones en pantalla para ingresar las propiedades de los materiales y obtener el diseño de mezcla.

```bash
python main.py
```

## Contribución

Las contribuciones son bienvenidas. Si deseas mejorar la precisión de los cálculos, agregar soporte para aditivos, o mejorar la interfaz, por favor haz un *fork* del repositorio, crea una rama con tu nueva función y envía un *Pull Request*.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
