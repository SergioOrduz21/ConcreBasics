import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

st.title("Diseño de Mezclas de Concreto de Peso Normal")

st.write("Datos iniciales para el cálculo de la mezcla de concreto según el Método ACI")

sand_Mf = st.number_input("MF (Modulo de Finura de la arena)", min_value=0.0, step=1.0)

gravel_MUC = st.number_input("MUC (Masa Unitaria Compacta) de la grava", min_value=0.0, step=1.0)

gravel_dg = st.number_input("Densidad aparente (dg) de la grava", min_value=0.0, step=1.0)

sand_df = st.number_input("Densidad aparente (dg) del agregado fino", min_value=0.0, step=1.0)

#------Establishing Databases------
# ASENTAMIENTO - SETTLEMENT
settlement_Table = pd.DataFrame({

    "Asentamiento (cm)": [
        pd.Interval(0.0, 2.0,   closed="left"),
        pd.Interval(2.0, 3.5,   closed="left"),
        pd.Interval(3.5, 5.0,   closed="left"),
        pd.Interval(5.0, 10.0,  closed="left"),
        pd.Interval(10.0, 15.0, closed="both"),
    ],

    "Consistencia (tipo de concreto)": [
        "Muy seca", 
        "Seca", 
        "Semi-seca", 
        "Media", 
        "Húmeda"
    ],

    "Grado de trabajabilidad": [
        "Muy pequeño", 
        "Pequeño", 
        "Pequeño", 
        "Medio", 
        "Alto"
    ],

    "Tipo de estructura y condiciones de colocación": [
        [
            "Vigas alta resistencia c/ vibrador formaleta",
            "Pilotes alta resistencia c/ vibrador formaleta"
        ], 
        [
            "Pavimentos vibrados con máquina"
        ], 
        [
            "Construcciones masas voluminosas", 
            "Losas medianamente reforzadas vibradas", 
            "Fundaciones en concreto simple", 
            "Pavimentos vibrados normales"
        ], 
        [
            "Losas medianamente reforzadas compactadas a mano", 
            "Pavimentos compactados a mano", 
            "Columnas vibradas", 
            "Vigas vibradas", 
            "Fundaciones vibradas", 
            "Muros vibrados"], 
        [
            "Secciones con mucho refuerzo",
            "Intervenciones de dificil colocación",
            "Revestimiento de túneles",
            "No se recomienda con mucha vibración"
        ]],
})

def range_format(r):
    return f"{r.left:g} - {r.right:g}"          # 0.0 -> "0", 3.5 -> "3.5"

def list_format(list):
    return "; ".join(list)

settlement_Table_View = settlement_Table.copy()
settlement_Table_View["Asentamiento (cm)"] = settlement_Table_View["Asentamiento (cm)"].apply(range_format)
settlement_Table_View["Tipo de estructura y condiciones de colocación"] = (
    settlement_Table_View["Tipo de estructura y condiciones de colocación"].apply(list_format)
)

st.header("Cálculo del Asentamiento")
st.table(settlement_Table_View)

selected_Settlement = st.number_input("Asentamiento elegido (cm)", min_value=0.0, max_value=15.0, step=0.1)

selected_Settlement_In = selected_Settlement * 2.54

st.info(f"Asentamiento seleccionado en {selected_Settlement} cm / {selected_Settlement_In} in.")

# --------------- TMN (tamaño máximo nominal del agregado) - NMAS (Nominal Maximum Aggregate Size) ---------------


tmn_Selected = 0
st.title("Cálculo TMN (tamaño máximo nominal del agregado)")


tmn_Mode = st.radio(    # Elegir el modo de cálculo del TMN
    "¿Cómo desea calcular el TMN?",
    [
        "Ingresar pesos retenidos y calcular granulometría",
        "Seleccionar un tamaño según el tipo de construcción"
    ],
    horizontal=True
)

if tmn_Mode == "Ingresar pesos retenidos y calcular granulometría" :
    
    st.header("Granulometría Agregado Grueso")

    gravel_Sieves = [   # Database Agregado Grueso / Gravel 

        ('5"', 127.0),    
        ('4"', 101.6),    
        ('3 1/2"', 88.9),    
        ('3"', 76.2),    
        ('2 1/2"', 63.5),    
        ('2"', 50.8),    
        ('1 1/2"', 38.1),    
        ('1"', 25.4),    
        ('3/4"', 19.1),    
        ('1/2"', 12.7),    
        ('3/8"', 9.53),    
        ("No. 4", 4.76),    
        ("Fondo", None)
    ]

    gravel_Base = pd.DataFrame({
        "Tamiz": [t for t, _ in gravel_Sieves],
        "Abertura (mm)": [a for _, a in gravel_Sieves],
        "Retenido (g)": [0.0] * len(gravel_Sieves),
    })

    initial_Gravel_Mass = st.number_input("Masa inicial seca gravas (g)", min_value=0.0, step=1.0)

    # Tabla editable
    # Solo la columna de peso se puede modificar
    gravel_Table_Edited = st.data_editor(
        gravel_Base,
        disabled=["Tamiz", "Abertura (mm)"],
        column_config={"Retenido (g)": st.column_config.NumberColumn(min_value=0.0, format="%.2f")},
        hide_index=True,
    )

    gravel_Total = gravel_Table_Edited["Retenido (g)"].sum()

    if gravel_Total > 0:
        gravel_Percentages_Table = gravel_Table_Edited.copy()
        gravel_Percentages_Table["% Retenido"] = gravel_Percentages_Table["Retenido (g)"] / gravel_Total * 100
        gravel_Percentages_Table["% Ret. acum."] = gravel_Percentages_Table["% Retenido"].cumsum()
        gravel_Percentages_Table["% Pasa"] = (100 - gravel_Percentages_Table["% Ret. acum."]).clip(lower=0)

        st.dataframe(gravel_Percentages_Table.round(1), hide_index=True)

        if initial_Gravel_Mass > 0:
            gravel_Difference = (initial_Gravel_Mass - gravel_Total) / initial_Gravel_Mass * 100
            st.caption(f"Total retenido: {gravel_Total:.1f} g | Diferencia vs. masa inicial: {gravel_Difference:.2f} %")

        # Curva granulométrica
        gravel_Curve_Data = gravel_Percentages_Table[gravel_Percentages_Table["Abertura (mm)"].notna()]
        fig, ax = plt.subplots(figsize=(8,5))
        ax.semilogx(gravel_Curve_Data["Abertura (mm)"], gravel_Curve_Data["% Pasa"], marker="o")
        ax.invert_xaxis()
        ax.set_xticks(gravel_Curve_Data["Abertura (mm)"])
        ax.set_xticklabels(gravel_Curve_Data["Tamiz"], rotation=90)
        ax.minorticks_off()
        ax.set_xlabel("Denominación Tamiz")
        ax.set_ylabel("% que pasa")
        ax.grid(True, which="both")
        st.pyplot(fig)
    else:
            st.info("Ingresa los pesos retenidos para ver los resultados.")

# ---------- Agregado Fino / Sand ------------

    st.title("Granulometría Agregado Fino")

    sand_Sieves = [    

        ('3/8"', 9.53),    
        ("No. 4", 4.76),    
        ("No. 8", 2.36),    
        ("No. 16", 1.18),    
        ("No. 30", 0.60),    
        ("No. 50", 0.30),    
        ("No. 100", 0.15),    
        ("No. 200", 0.075),    
        ("Fondo", None)
    ]

    sand_Base = pd.DataFrame({
        "Tamiz": [t for t, _ in sand_Sieves],
        "Abertura (mm)": [a for _, a in sand_Sieves],
        "Retenido (g)": [0.0] * len(sand_Sieves),
    })

    initial_Sand_Mass = st.number_input("Masa inicial seca finos (g)", min_value=0.0, step=1.0)

    # Tabla editable: solo la columna de peso se puede modificar

    sand_Table_Edited = st.data_editor(
        sand_Base,
        disabled=["Tamiz", "Abertura (mm)"],
        column_config={"Retenido (g)": st.column_config.NumberColumn(min_value=0.0, format="%.2f")},
        hide_index=True,
    )

    sand_Total = sand_Table_Edited["Retenido (g)"].sum()

    if sand_Total > 0:
        sand_Percentages_Table = sand_Table_Edited.copy()
        sand_Percentages_Table["% Retenido"] = sand_Percentages_Table["Retenido (g)"] / sand_Total * 100
        sand_Percentages_Table["% Ret. acum."] = sand_Percentages_Table["% Retenido"].cumsum()
        sand_Percentages_Table["% Pasa"] = (100 - sand_Percentages_Table["% Ret. acum."]).clip(lower=0)

        st.dataframe(sand_Percentages_Table.round(1), hide_index=True)

        if initial_Sand_Mass > 0:
            sand_Difference = (initial_Sand_Mass - sand_Total) / initial_Sand_Mass * 100
            st.caption(f"Total retenido: {sand_Total:.1f} g | Diferencia vs. masa inicial: {sand_Difference:.2f} %")

        # Curva granulométrica
        sand_Curve_Data = sand_Percentages_Table[sand_Percentages_Table["Abertura (mm)"].notna()]
        fig, ax = plt.subplots(figsize=(8,5))
        ax.semilogx(sand_Curve_Data["Abertura (mm)"], sand_Curve_Data["% Pasa"], marker="o")
        ax.invert_xaxis()
        ax.set_xticks(sand_Curve_Data["Abertura (mm)"])
        ax.set_xticklabels(sand_Curve_Data["Tamiz"], rotation=90)
        ax.minorticks_off()
        ax.set_xlabel("Denominación Tamiz")
        ax.set_ylabel("% que pasa")
        ax.grid(True, which="both")
        st.pyplot(fig)
    else:
        st.info("Ingresa los pesos retenidos para ver los resultados.")


    st.subheader("TMN - Tamaño Máximo Nominal")

    def find_TMN(percentages_Table):
        # Sin el fondo (no tiene abertura)
        sieves = percentages_Table[percentages_Table["Abertura (mm)"].notna()].reset_index(drop=True)

        # 1. Último tamiz por el que pasa el 100 % (retenido acumulado = 0)
        passes_All = sieves["% Ret. acum."] == 0
        last_100 = sieves.index[passes_All].max() if passes_All.any() else -1

        # 2. De los tamices siguientes, el primero con % retenido entre 5 y 10
        next_Sieves = sieves.iloc[last_100 + 1:]
        candidates = next_Sieves[(next_Sieves["% Retenido"] >= 5) & (next_Sieves["% Retenido"] <= 10)]

        return candidates.head(1)   # DataFrame de 1 fila, o vacío si ninguno cumple


    if gravel_Total > 0:
        tmn_Selected = find_TMN(gravel_Percentages_Table)

        if tmn_Selected.empty:
            st.warning("Ningún tamiz cumple: % retenido entre 5 y 10 % después del último con 100 % pasante.")
        else:
            tmn_Sieve = tmn_Selected["Tamiz"].iloc[0]
            tmn_mm = tmn_Selected["Abertura (mm)"].iloc[0]

            st.success(f"Tamaño máximo nominal: {tmn_Sieve} ({tmn_mm} mm)")
            st.dataframe(tmn_Selected.round(1), hide_index=True)
    else:
        st.info("Ingresa la granulometría del agregado grueso para calcular el TMN.")
else:

    tmn_Const_Type_Table = pd.DataFrame({

    "Dimensión Mínima del Elemento (cm)": [
        pd.Interval(6, 15,   closed="left"),
        pd.Interval(16, 29,   closed="left"),
        pd.Interval(30, 75,   closed="left"),
        pd.Interval(75, np.inf, closed="left"),
    ],
    "Muros reforzados, vigas y columnas": [
        "12(1/2\") - 19(3/4\")",
        "19(3/4\") - 38(1 1/2\")",
        "38(1 1/2\") - 76(3\")",
        "38(1 1/2\") - 76(3\")"
    ],
    "Muros sin refuerzo": [
        "19(3/4\")",
        "38(1 1/2\")",
        "76(3\")",
        "152(6\")"
    ],
    "Losas muy reforzadas": [
        "19(3/4\") - 25(1\")",
        "38(1 1/2\")",
        "38(1/2\") - 76(3\")",
        "38(1 1/2\") - 76(3\")"
    ],
    "Losas sin refuerzo o poco reforzadas": [
        "19(3/4\") - 38(1 1/2\")",
        "38(1 1/2\") - 76(3\")",
        "76(3\")",
        "76(3\") - 152(6\")"
    ]

    })
    def format_range(interval):
        if np.isinf(interval.right):
            return f"≥ {interval.left:g}"
        return f"{interval.left:g} - {interval.right:g}"

    tmn_table_view = tmn_Const_Type_Table.copy()
    tmn_table_view["Dimensión Mínima del Elemento (cm)"] = (
        tmn_table_view["Dimensión Mínima del Elemento (cm)"].apply(format_range)
    )

    st.header("Valores Recomendados de TMN según el tipo de construcción")
    st.table(tmn_table_view)

    standard_sieves = { # Standard sieve sizes (mm: inches)
        12.5: '1/2"', 19.0: '3/4"', 25.0: '1"', 37.5: '1 1/2"',
        75.0: '3"', 150.0: '6"',
    }

    tmn_Selected = st.selectbox(
        "TMN Elegido",
        list(standard_sieves),
        format_func=lambda mm: f'{mm:g} mm ({standard_sieves[mm]})',
    )


# ------------------CONTENIDO DE AIRE------------------

air_Content_Table = {
    "Agregado grueso (pulg.)": [
        '3/8"', '1/2"', '3/4"', '1"', '1 1/2"', '2"', '3"', '6"'
    ],
    "Tamaño (mm)": [
        9.51, 12.50, 19.10, 25.40, 38.10, 50.8, 76.1, 152.4
    ],
    "Porcentaje Promedio aproximado de aire atrapado (%)": [
        2.7, 2.5, 2.0, 1.7, 1.5, 1.0, 0.3, 0.2
    ]
}

air_Percentage = 0

# Crear DataFrame
air_Content_Table_Copy = pd.DataFrame(air_Content_Table)

# Mostrar tabla
st.title("Porcentaje de aire atrapado en el concreto")

concrete_Air_Mode = st.radio(
    "El concreto tiene aire adicionado?",
    ["Si", "No"],
    horizontal=True
)

st.dataframe(
    air_Content_Table_Copy,
    use_container_width=True,
    hide_index=True
)

# Sección de interpolación
st.subheader("Cálculo del porcentaje de aire atrapado")

interpol_Table = air_Content_Table_Copy.sort_values(
    "Tamaño (mm)"
).reset_index(drop=True)

percentage_Column = (
    "Porcentaje Promedio aproximado de aire atrapado (%)"
)

# Elegir el modo de cálculo
tmn_Air_Mode = st.radio(
    "¿Cómo deseas ingresar el TMN?",
    [
        "Seleccionar un tamaño de la tabla",
        "Ingresar un tamaño personalizado"
    ],
    horizontal=True
)

if tmn_Air_Mode == "Seleccionar un tamaño de la tabla":

    # Crear opciones con tamaño en mm y pulgadas
    tmn_Options = {
        f"{tmn_Row['Agregado grueso (pulg.)']} "
        f"({tmn_Row['Tamaño (mm)']:.2f} mm)": tmn_Row["Tamaño (mm)"]
        for _, tmn_Row in interpol_Table.iterrows()
    }

    tmn_Selection = st.selectbox(
        "Selecciona el tamaño del agregado:",
        options=list(tmn_Options.keys())
    )

    gravel_Selected_Size = tmn_Options[tmn_Selection]

else:

    gravel_Selected_Size = st.number_input(
        "Ingresa el tamaño del agregado (mm):",
        min_value=float(interpol_Table["Tamaño (mm)"].min()),
        max_value=float(interpol_Table["Tamaño (mm)"].max()),
        value=20.00,
        step=0.01,
        format="%.2f"
    )

# Botón de cálculo
if st.button("Calcular porcentaje de aire atrapado"):

    table_Sizes = interpol_Table["Tamaño (mm)"].to_numpy()
    table_Percentages = interpol_Table[percentage_Column].to_numpy()

    # Verificar si el tamaño está en la tabla
    exact_Match = interpol_Table[
        np.isclose(
            interpol_Table["Tamaño (mm)"],
            gravel_Selected_Size,
            atol=1e-8,
            rtol=0
        )
    ]

    if not exact_Match.empty:

        # Valor exacto de la tabla
        air_Percentage = float(
            exact_Match.iloc[0][percentage_Column]
        )

        st.success(f"Porcentaje de aire atrapado: {air_Percentage:.2f} %")
        st.info(f"Valor decimal: {air_Percentage / 100:.4f} m3 aire/m3 ccto")

        st.caption("Resultado exacto de la tabla original.")

    else:

        # Interpolación lineal
        air_Percentage = float(
            np.interp(
                gravel_Selected_Size,
                table_Sizes,
                table_Percentages
            )
        )

        st.success(f"Porcentaje estimado de aire atrapado: {air_Percentage:.3f} %")
        st.info(f"Valor decimal: {air_Percentage / 100:.5f} m3 aire/m3 ccto")

        st.caption("Resultado calculado mediante interpolación lineal.")

air_Percentage_Vol = air_Percentage/100 
# ---------------CANTIDAD DE AGUA---------------

st.header("Cálculo Cantidad de agua")

water_No_Air_Table = {

    "Asentamiento (cm)":[
        pd.Interval(0, 3, closed="left"),   #No incluye al limite superior
        pd.Interval(3, 5, closed="left"),
        pd.Interval(5, 8, closed="left"),
        pd.Interval(8, 10, closed="left"),
        pd.Interval(10, 15, closed="left"),
        pd.Interval(15, 18, closed="both"),
    ],

    10:[
        195, 205, 215, 225, 232, 240
    ],

    12.5:[
        192.5, 200, 207.5, 215, 222, 230
    ],
    
    20:[
        177.5, 185, 192.5, 200, 214.7, 210
    ],
    
    25:[
        172.5, 180, 187.5, 195, 209.7, 205
    ],
    
    40:[
        152.5, 160, 167.5, 175, 189.7, 185
    ],
    
    50:[
        147.5, 155, 162.5, 170, 184.7, 180
    ],
    
    70:[
        137.5, 145, 152.5, 160, 174.7, 170
    ],
    
    150:[
        117.5, 125, 132.5, 140, None, None
    ]
}

# Tabla para CÁLCULOS (columnas numéricas, no se modifica)
water_No_Air_Table_Copy = pd.DataFrame(water_No_Air_Table.copy())


def get_water_no_air(slump_cm, tmn_mm, table=water_No_Air_Table_Copy):
    """Devuelve el agua de mezcla (kg/m3) para un asentamiento y un TMN,
    interpolando linealmente entre tamices. Retorna None si está fuera de rango."""

    # 1. Fila según el intervalo de asentamiento
    row_mask = table["Asentamiento (cm)"].apply(lambda interval: slump_cm in interval)
    if not row_mask.any():
        return None
    row = table.loc[row_mask].iloc[0]

    # 2. Solo los tamices que tienen valor (descarta los None)
    water_values = row[table.columns[1:]].astype(float).dropna()
    sieve_sizes = water_values.index.astype(float)

    # 3. Si el TMN queda fuera del rango disponible, no se puede interpolar
    if tmn_mm < sieve_sizes.min() or tmn_mm > sieve_sizes.max():
        return None

    # 4. Interpolación lineal (si el TMN coincide con un tamiz, da el valor exacto)
    return float(np.interp(tmn_mm, sieve_sizes, water_values.values))


# Tabla para MOSTRAR (copia con encabezados de dos niveles)
water_No_Air_Table_Display = water_No_Air_Table_Copy.copy()
water_No_Air_Table_Display.columns = pd.MultiIndex.from_tuples(
    [("Concreto sin aire", "Asentamiento (cm)")]
    + [
        ("Tamaño Máximo Nominal", f"{sieve} mm")
        for sieve in water_No_Air_Table_Copy.columns[1:]
    ]
)

st.dataframe(
    water_No_Air_Table_Display,
    use_container_width=True,
    hide_index=True
)

# Agua calculada automáticamente con los datos seleccionados antes
water_Interpolated = get_water_no_air(selected_Settlement, tmn_Selected)

water_Mode = st.radio(
    "Cantidad de agua de mezcla",
    ["Automática (interpolada de la tabla)", "Manual"],
    horizontal=True
)

if water_Mode == "Automática (interpolada de la tabla)":
    water_Content = water_Interpolated

    if water_Content is None:
        st.warning(
            "No hay dato de agua para ese asentamiento y TMN (fuera del rango de la tabla). "
            "Puedes cambiar a modo Manual para ingresarla."
        )
        st.stop()
    else:
        st.write(f"Agua de mezcla: **{water_Content:.1f} kg/m³**")

else:
    # El valor inicial es el interpolado (si existe) para que puedas ajustarlo
    water_Content = st.number_input(
        "Agua de mezcla (kg/m³)",
        min_value=0.0,
        value=round(water_Interpolated, 1) if water_Interpolated is not None else 180.0,
        step=1.0
    )
    st.write(f"Agua de mezcla (manual): **{water_Content:.1f} kg/m³**")

water_Content_Vol = water_Content / 1000

# water_Content es la variable que usas en el resto de tus cálculos

# -----------------RELACION AGUA CEMENTO-----------------
st.header("Cálculo Relación Agua/Cemento a/c")

concrete_Strength_Mode = st.radio(
    "Resistencia del concreto",
    ["MPa", "PSI"],
    horizontal=True
)

fc_Concrete_Strength = 0

if concrete_Strength_Mode == "MPa": 

    fc_Concrete_Strength = st.number_input("Resistencia del Concreto", min_value=0.0, step=10.0)

    concrete_Strength_Table = {
    "Resistencia a la compresión a los 28 dias": [
        175, 210, 245, 280, 315, 350
    ],

    "Concreto sin aire": [
        0.65, 0.58, 0.52, 0.47, 0.43, 0.40
    ],

    "Concreto con aire": [
        0.56, 0.50, 0.46, 0.42, 0.38, 0.35
    ]
    }
else: 
    fc_Concrete_Strength = st.number_input("Resistencia del Concreto", min_value=0.0, step=100.0)
    
    concrete_Strength_Table = {
    "Resistencia a la compresión a los 28 dias": [
        2500, 3000, 3500, 4000, 4500, 5000
    ],
    
    "Concreto sin aire": [
        0.65, 0.58, 0.52, 0.47, 0.43, 0.40
    ],
    
    "Concreto con aire": [
        0.56, 0.50, 0.46, 0.42, 0.38, 0.35
    ]
    }

def get_water_cement_ratio(strength, air_mode, table):
    """Devuelve la relación a/c para una resistencia dada, interpolando
    linealmente en la columna con aire o sin aire. Retorna None si está fuera de rango."""

    # 1. Columna según el tipo de concreto
    column_Name = "Concreto con aire" if air_mode == "Si" else "Concreto sin aire"

    strength_Column = table.columns[0]
    strength_Values = table[strength_Column].astype(float).values
    ratio_Values = table[column_Name].astype(float).values

    # 2. Fuera del rango de la tabla no se puede interpolar
    if strength < strength_Values.min() or strength > strength_Values.max():
        return None

    # 3. Interpolación lineal (si coincide con un valor de la tabla, da el valor exacto)
    return float(np.interp(strength, strength_Values, ratio_Values))


concrete_Strength_DataFrame = pd.DataFrame(concrete_Strength_Table)

st.dataframe(
    concrete_Strength_DataFrame,
    use_container_width=True,
    hide_index=True
)

water_Cement_Ratio = get_water_cement_ratio(
    fc_Concrete_Strength,
    concrete_Air_Mode,
    concrete_Strength_DataFrame
)

if water_Cement_Ratio is None:
    st.warning("La resistencia está fuera del rango de la tabla, no se puede obtener la relación a/c.")
    st.stop()
else:
    air_Label = "con aire" if concrete_Air_Mode == "Si" else "sin aire"
    st.write(f"Relación a/c ({air_Label}): **{water_Cement_Ratio:.3f}**")

# -----------------CONTENIDO DE CEMENTO-----------------

st.header("Cálculo cantidad de cemento")

cement_Density = st.number_input("Ingrese la densidad del concreto en kg/m3: ", min_value=0.0, step=100.0)

cement_Weight = water_Content/water_Cement_Ratio
cement_Vol = cement_Weight / cement_Density

st.write(f"Con la cantidad de agua determinada: **{water_Content:.1f} kg/m3** y con la relacion **agua/cemento de: {water_Cement_Ratio:.3f},** la cantidad de **cemento necesaria es de {cement_Weight:.0f} kg/m3**")

st.write(f"El volumen de cemento es de: {cement_Vol:.4f} m3/m3 de concreto")

# -----------------ESTIMAR CANTIDAD DE GRAVA-----------------

st.header("Cálculo cantidad de grava")

mf_Table = {
    "Tamaño Maximo Nominal (mm)": [
        9.5, 12.5, 19.0, 25.0, 38.0, 50.0, 75.0, 150.0
    ],

    2.0: [
        0.50, 0.59, 0.69, 0.74, 0.80, 0.83, 0.88, 0.94
    ],

    2.1: [
        0.49, 0.58, 0.68, 0.73, 0.79, 0.82, 0.87, 0.93
    ],

    2.2: [
        0.48, 0.57, 0.67, 0.72, 0.78, 0.81, 0.86, 0.92
    ],

    2.3: [
        0.47, 0.56, 0.66, 0.71, 0.77, 0.80, 0.85, 0.91
    ],

    2.4: [
        0.46, 0.55, 0.65, 0.70, 0.76, 0.79, 0.84, 0.90
    ],

    2.5: [
        0.45, 0.54, 0.64, 0.69, 0.75, 0.78, 0.83, 0.89
    ],

    2.6: [
        0.44, 0.53, 0.63, 0.68, 0.74, 0.77, 0.82, 0.88
    ],

    2.7: [
        0.43, 0.52, 0.62, 0.67, 0.73, 0.76, 0.81, 0.87
    ],

    2.8: [
        0.42, 0.51, 0.61, 0.66, 0.72, 0.75, 0.80, 0.86
    ],

    2.9: [
        0.41, 0.50, 0.60, 0.65, 0.71, 0.74, 0.79, 0.85
    ],

    3.0: [
        0.40, 0.49, 0.59, 0.64, 0.70, 0.73, 0.78, 0.84
    ],

    3.1: [
        0.39, 0.48, 0.58, 0.63, 0.69, 0.72, 0.77, 0.83
    ]
}

mf_DataFrame = pd.DataFrame(mf_Table)

st.subheader("Relación b/b0 para diferentes modulos de finura MF de la arena")

st.table(mf_DataFrame)

def get_coarse_aggregate_factor(tmn_mm, fineness_modulus, table=mf_DataFrame):
    """Devuelve el valor de la tabla para un TMN y un módulo de finura,
    interpolando linealmente en ambas direcciones (bilineal).
    Retorna None si alguno de los dos está fuera del rango de la tabla."""

    tmn_Column = table.columns[0]
    tmn_Values = table[tmn_Column].astype(float).values
    mf_Values = np.array(table.columns[1:], dtype=float)

    # 1. Fuera de rango no se puede interpolar
    if tmn_mm < tmn_Values.min() or tmn_mm > tmn_Values.max():
        return None
    if fineness_modulus < mf_Values.min() or fineness_modulus > mf_Values.max():
        return None

    # 2. Interpolar en TMN para cada columna de módulo de finura
    values_At_Tmn = [
        np.interp(tmn_mm, tmn_Values, table[mf].astype(float).values)
        for mf in table.columns[1:]
    ]

    # 3. Interpolar en módulo de finura con los valores obtenidos
    return float(np.interp(fineness_modulus, mf_Values, values_At_Tmn))

coarse_Factor = get_coarse_aggregate_factor(tmn_Selected, sand_Mf)

if coarse_Factor is None:
    st.warning("El TMN o el módulo de finura están fuera del rango de la tabla.")
else:
    st.write(f"Relación b/b0: **{coarse_Factor:.3f}**")

b0_Value = gravel_MUC/gravel_dg

st.write(f"EL valor de b0 es igual al **MUC/dg**. Por lo tanto, el valor de b0 en este análisis es de: **{b0_Value:.4f}**")

b_Value = coarse_Factor*b0_Value 

st.write(f"Luego, el valor del volumen de agregado grueso por cada m3 de concreto se calcula de la siguiente manera: b = (b/b0)*b0. Por lo mismo, el valor de b es igual a: {b_Value:.4f} m3/m3")

gravel_Weight = b_Value * gravel_dg

st.write(f"Finalmente, el peso de agregado grueso por cada m3 de concreto se calcula de la siguiente manera: W = b*dg Por lo mismo, el valor del peso de agregado grueso es de: {gravel_Weight:.0f} kg/m3 de concreto")

# -----------------ESTIMAR CANTIDAD DE ARENA-----------------

st.header("Cálculo cantidad de agregado fino")

sand_Vol = 1 - (cement_Vol + water_Content_Vol + b_Value + air_Percentage_Vol)

st.write(f"La cantidad de agregado fino se define hallando la diferencia entre 1 m3 y la sumatoria de todos los demás volumenes hallados durante el diseño. Luego, el **volumen de agregado fino es de {sand_Vol:.4f} m3/m3 de concreto**")

sand_Weight = sand_Vol * sand_df

st.write(f"El peso del agregado fino es de {sand_Weight:.0f} kg/m3 de concreto")
# -----------------AJUSTAR CANTIDAD DE AGUA POR HUMEDAD-----------------



# -----------------AJUSTAR MEZCLAS DE PRUEBA-----------------


