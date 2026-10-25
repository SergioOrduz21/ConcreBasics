import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

st.set_page_config(page_title="Diseño de Mezclas de Concreto")

# ---------- ESTILO - STYLE ----------

# Centers headings, captions, radios, metrics and static tables
st.markdown("""
<style>
h1, h2, h3, h4 { text-align: center; }
[data-testid="stHeadingWithActionElements"] { display: flex; justify-content: center; }
[data-testid="stCaptionContainer"] { text-align: center; }
[data-testid="stRadio"] { display: flex; flex-direction: column; align-items: center; }
[data-testid="stMetric"] { text-align: center; align-items: center; }
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { justify-content: center; }
[data-testid="stTable"] th, [data-testid="stTable"] td { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

st.title("Diseño de Mezclas de Concreto de Peso Normal")
st.caption("Cálculo de la mezcla de concreto según el Método ACI")

# ---------- DATOS INICIALES - INITIAL DATA ----------

st.header("Datos Iniciales")

gravel_Dry_Weight = st.number_input("Peso seco del agregado grueso (Ensayo INV-E-223) en g.", min_value=0.0, step=1.0)

sand_Dry_Weight = st.number_input("Peso seco del agregado fino (Ensayo INV-E-222) en g.", min_value=0.0, step=1.0)

gravel_Wet_Weight = st.number_input("Peso húmedo del agregado grueso (Ensayo INV-E-223) en g.", min_value=0.0, step=1.0)

sand_Wet_Weight = st.number_input("Peso húmedo del agregado fino (Ensayo INV-E-222) en g.", min_value=0.0, step=1.0)

gravel_Sss_Weight = st.number_input("Peso Saturado y Superficialmente Seco SSS del agregado grueso (Ensayo INV-E-223) en g.", min_value=0.0, step=1.0)

sand_Sss_Weight = st.number_input("Peso Saturado y Superficialmente Seco del agregado fino (Ensayo INV-E-222) en g.", min_value=0.0, step=1.0)

sand_Mf = st.number_input("MF (Modulo de Finura de la arena)", min_value=0.0, step=1.0)

gravel_Muc = st.number_input("MUC (Masa Unitaria Compacta) de la grava", min_value=0.0, step=1.0)

gravel_Dg = st.number_input("Densidad aparente (dg) de la grava", min_value=0.0, step=1.0)

sand_Df = st.number_input("Densidad aparente (dg) del agregado fino", min_value=0.0, step=1.0)

# ---------- ASENTAMIENTO - SETTLEMENT ----------

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

def format_interval(r):
    return f"{r.left:g} - {r.right:g}"          # 0.0 -> "0", 3.5 -> "3.5"

def format_list(items):
    return "; ".join(items)

settlement_Table_View = settlement_Table.copy()
settlement_Table_View["Asentamiento (cm)"] = settlement_Table_View["Asentamiento (cm)"].apply(format_interval)
settlement_Table_View["Tipo de estructura y condiciones de colocación"] = (
    settlement_Table_View["Tipo de estructura y condiciones de colocación"].apply(format_list)
)

st.header("Cálculo del Asentamiento")
st.table(settlement_Table_View)

selected_Settlement = st.number_input("Asentamiento elegido (cm)", min_value=0.0, max_value=15.0, step=0.1)

selected_Settlement_In = selected_Settlement * 2.54

st.info(f"Asentamiento seleccionado en {selected_Settlement} cm / {selected_Settlement_In} in.")

# ---------- TMN - NMAS (NOMINAL MAXIMUM AGGREGATE SIZE) ----------

tmn_Selected = 0
st.header("Cálculo del TMN (Tamaño Máximo Nominal del Agregado)")

tmn_Mode = st.radio(
    "¿Cómo desea calcular el TMN?",
    [
        "Ingresar pesos retenidos y calcular granulometría",
        "Seleccionar un tamaño según el tipo de construcción"
    ],
    horizontal=True
)

if tmn_Mode == "Ingresar pesos retenidos y calcular granulometría" :
    
    # ---------- AGREGADO GRUESO - GRAVEL ----------

    st.subheader("Granulometría Agregado Grueso")

    gravel_Sieves = [

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

    # Only the weight column is editable
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

        # Grading curve
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

    # ---------- AGREGADO FINO - SAND ----------

    st.subheader("Granulometría Agregado Fino")

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

    # Only the weight column is editable
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

        # Grading curve
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

    # ---------- RESULTADO TMN - TMN RESULT ----------

    st.subheader("TMN - Tamaño Máximo Nominal")

    def find_tmn(percentages_Table):
        """First sieve with 5-10 % retained after the last sieve passing 100 %."""
        # Drop "Fondo" (no opening)
        sieves = percentages_Table[percentages_Table["Abertura (mm)"].notna()].reset_index(drop=True)

        # Last sieve with 100 % passing (cumulative retained = 0)
        passes_All = sieves["% Ret. acum."] == 0
        last_100 = sieves.index[passes_All].max() if passes_All.any() else -1

        # First following sieve with 5-10 % retained
        next_Sieves = sieves.iloc[last_100 + 1:]
        candidates = next_Sieves[(next_Sieves["% Retenido"] >= 5) & (next_Sieves["% Retenido"] <= 10)]

        return candidates.head(1)   # 1-row DataFrame, empty if none


    if gravel_Total > 0:
        tmn_Selected = find_tmn(gravel_Percentages_Table)

        if tmn_Selected.empty:
            st.warning("Ningún tamiz cumple: % retenido entre 5 y 10 % después del último con 100 % pasante.")
        else:
            tmn_Sieve = tmn_Selected["Tamiz"].iloc[0]
            tmn_Mm = tmn_Selected["Abertura (mm)"].iloc[0]

            st.success(f"Tamaño máximo nominal: {tmn_Sieve} ({tmn_Mm} mm)")
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

    tmn_Table_View = tmn_Const_Type_Table.copy()
    tmn_Table_View["Dimensión Mínima del Elemento (cm)"] = (
        tmn_Table_View["Dimensión Mínima del Elemento (cm)"].apply(format_range)
    )

    st.subheader("Valores Recomendados de TMN según el tipo de construcción")
    st.table(tmn_Table_View)

    standard_Sieves = {     # mm: inches
        12.5: '1/2"', 19.0: '3/4"', 25.0: '1"', 37.5: '1 1/2"',
        75.0: '3"', 150.0: '6"',
    }

    tmn_Selected = st.selectbox(
        "TMN Elegido",
        list(standard_Sieves),
        format_func=lambda mm: f'{mm:g} mm ({standard_Sieves[mm]})',
    )


# ---------- CONTENIDO DE AIRE - AIR CONTENT ----------

st.header("Contenido de Aire en el Concreto")

air_Content_Table = {
    "Agregado grueso (pulg.)": [
        '3/8"', '1/2"', '3/4"', '1"', '1 1/2"', '2"', '3"', '6"'
    ],
    "Tamaño (mm)": [
        9.51, 12.50, 19.10, 25.40, 38.10, 50.8, 76.1, 152.4
    ],
    "Porcentaje Promedio aproximado de aire atrapado (%)": [
        2.7, 2.5, 2.0, 1.7, 1.5, 1.0, 0.3, 0.2
    ],
    "Aire total - Suave (%)": [
        4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0
    ],
    "Aire total - Moderado (%)": [
        6.0, 5.5, 5.0, 4.5, 4.5, 4.0, 3.5, 3.0
    ],
    "Aire total - Severo (%)": [
        7.5, 7.0, 6.0, 6.0, 5.5, 4.0, 4.5, 4.0
    ]
}

air_Percentage = 0

air_Content_Table_Copy = pd.DataFrame(air_Content_Table)

# Display copy with two-level headers
air_Content_Table_Display = air_Content_Table_Copy.copy()
air_Content_Table_Display.columns = pd.MultiIndex.from_tuples([
    ("Agregado grueso", "Pulg."),
    ("Agregado grueso", "mm"),
    ("Aire atrapado", "Promedio aprox. (%)"),
    ("Aire total recomendado (%) según grado de exposición", "Suave"),
    ("Aire total recomendado (%) según grado de exposición", "Moderado"),
    ("Aire total recomendado (%) según grado de exposición", "Severo"),
])

concrete_Air_Mode = st.radio(
    "El concreto tiene aire adicionado?",
    ["Si", "No"],
    horizontal=True
)

# With added air: total air by exposure. Without: trapped air.
if concrete_Air_Mode == "Si":
    exposure_Level = st.radio(
        "Grado de exposición",
        ["Suave", "Moderado", "Severo"],
        horizontal=True
    )
    percentage_Column = f"Aire total - {exposure_Level} (%)"
    air_Result_Label = "aire total"
else:
    percentage_Column = "Porcentaje Promedio aproximado de aire atrapado (%)"
    air_Result_Label = "aire atrapado"

st.subheader("Contenido aproximado de aire en el concreto para varios grados de exposición")

st.dataframe(
    air_Content_Table_Display,
    use_container_width=True,
    hide_index=True
)

st.subheader("Cálculo del porcentaje de aire")

interpol_Table = air_Content_Table_Copy.sort_values(
    "Tamaño (mm)"
).reset_index(drop=True)

tmn_Air_Mode = st.radio(
    "¿Cómo deseas ingresar el TMN?",
    [
        "Seleccionar un tamaño de la tabla",
        "Ingresar un tamaño personalizado"
    ],
    horizontal=True
)

if tmn_Air_Mode == "Seleccionar un tamaño de la tabla":

    # Options labeled in inches and mm
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

if st.button(f"Calcular porcentaje de {air_Result_Label}"):

    table_Sizes = interpol_Table["Tamaño (mm)"].to_numpy()
    table_Percentages = interpol_Table[percentage_Column].to_numpy()

    # Size already in the table?
    exact_Match = interpol_Table[
        np.isclose(
            interpol_Table["Tamaño (mm)"],
            gravel_Selected_Size,
            atol=1e-8,
            rtol=0
        )
    ]

    if not exact_Match.empty:

        air_Percentage = float(
            exact_Match.iloc[0][percentage_Column]
        )

        st.success(f"Porcentaje de {air_Result_Label}: {air_Percentage:.2f} %")
        st.info(f"Valor decimal: {air_Percentage / 100:.4f} m3 aire/m3 ccto")

        st.caption("Resultado exacto de la tabla original.")

    else:

        # Linear interpolation
        air_Percentage = float(
            np.interp(
                gravel_Selected_Size,
                table_Sizes,
                table_Percentages
            )
        )

        st.success(f"Porcentaje estimado de {air_Result_Label}: {air_Percentage:.3f} %")
        st.info(f"Valor decimal: {air_Percentage / 100:.5f} m3 aire/m3 ccto")

        st.caption("Resultado calculado mediante interpolación lineal.")

air_Percentage_Vol = air_Percentage/100 

# ---------- CANTIDAD DE AGUA - WATER CONTENT ----------

st.header("Cálculo Cantidad de Agua")

water_No_Air_Table = {

    "Asentamiento (cm)":[
        pd.Interval(0, 3, closed="left"),   # Upper limit excluded
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

water_With_Air_Table = {

    "Asentamiento (cm)":[
        pd.Interval(0, 3, closed="left"),   # Upper limit excluded
        pd.Interval(3, 5, closed="left"),
        pd.Interval(5, 8, closed="left"),
        pd.Interval(8, 10, closed="left"),
        pd.Interval(10, 15, closed="left"),
        pd.Interval(15, 18, closed="both"),
    ],

    10:[
        172.5, 180, 190, 200, 207.5, 215
    ],

    12.5:[
        167.5, 175, 182.5, 190, 197.5, 205
    ],
    
    20:[
        157.5, 165, 172.5, 180, 185, 190
    ],
    
    25:[
        152.5, 160, 167.5, 175, 180, 185
    ],
    
    40:[
        137.5, 145, 152.5, 160, 165, 170
    ],
    
    50:[
        132.5, 140, 147.5, 155, 160, 165
    ],
    
    70:[
        127.5, 135, 142.5, 150, 155, 160
    ],
    
    150:[
        112.5, 120, 127.5, 135, None, None
    ]
}

# Numeric tables for calculations (not modified)
water_No_Air_Table_Copy = pd.DataFrame(water_No_Air_Table.copy())
water_With_Air_Table_Copy = pd.DataFrame(water_With_Air_Table.copy())


def get_water_content(slump_Cm, tmn_Mm, table):
    """Mix water (kg/m3) for a slump and TMN, interpolating between sieves. None if out of range."""

    # Row by slump interval
    row_mask = table["Asentamiento (cm)"].apply(lambda interval: slump_Cm in interval)
    if not row_mask.any():
        return None
    row = table.loc[row_mask].iloc[0]

    # Keep only sieves with data (drop None)
    water_values = row[table.columns[1:]].astype(float).dropna()
    sieve_sizes = water_values.index.astype(float)

    # TMN outside the available range cannot be interpolated
    if tmn_Mm < sieve_sizes.min() or tmn_Mm > sieve_sizes.max():
        return None

    # Linear interpolation (exact value if TMN matches a sieve)
    return float(np.interp(tmn_Mm, sieve_sizes, water_values.values))


def format_water_table(table, label):
    """Copy of a water table with two-level headers for display."""
    table_View = table.copy()
    table_View.columns = pd.MultiIndex.from_tuples(
        [(label, "Asentamiento (cm)")]
        + [
            ("Tamaño Máximo Nominal", f"{sieve} mm")
            for sieve in table.columns[1:]
        ]
    )
    return table_View


# Table by air mode
if concrete_Air_Mode == "Si":
    water_Table_Selected = water_With_Air_Table_Copy
    water_Table_View = format_water_table(water_With_Air_Table_Copy, "Concreto con aire")
else:
    water_Table_Selected = water_No_Air_Table_Copy
    water_Table_View = format_water_table(water_No_Air_Table_Copy, "Concreto sin aire")

st.subheader("Agua de mezcla (kg/m³) según asentamiento y TMN")

st.dataframe(
    water_Table_View,
    use_container_width=True,
    hide_index=True
)

# Water from the previously selected settlement and TMN
water_Interpolated = get_water_content(selected_Settlement, tmn_Selected, water_Table_Selected)

water_Mode = st.radio(
    "Cantidad de agua de mezcla",
    ["Automática (interpolada de la tabla)", "Manual"],
    horizontal=True
)

water_Content = 0

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
    # Default is the interpolated value (if any), adjustable
    water_Content = st.number_input(
        "Agua de mezcla (kg/m³)",
        min_value=0.0,
        value=round(water_Interpolated, 1) if water_Interpolated is not None else 180.0,
        step=1.0
    )
    st.write(f"Agua de mezcla (manual): **{water_Content:.1f} kg/m³**")

water_Content_Vol = water_Content / 1000

# ---------- RELACION AGUA CEMENTO - WATER/CEMENT RATIO ----------

st.header("Cálculo Relación Agua/Cemento (a/c)")

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

def get_water_cement_ratio(strength, air_Mode, table):
    """a/c ratio for a strength, interpolating in the with/without air column. None if out of range."""

    # Column by concrete type
    column_Name = "Concreto con aire" if air_Mode == "Si" else "Concreto sin aire"

    strength_Column = table.columns[0]
    strength_Values = table[strength_Column].astype(float).values
    ratio_Values = table[column_Name].astype(float).values

    # Outside the table range cannot be interpolated
    if strength < strength_Values.min() or strength > strength_Values.max():
        return None

    # Linear interpolation (exact value if strength matches the table)
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

# ---------- CONTENIDO DE CEMENTO - CEMENT CONTENT ----------

st.header("Cálculo Cantidad de Cemento")

cement_Density = st.number_input("Ingrese la densidad del concreto en kg/m3: ", min_value=0.0, step=100.0)

cement_Weight = water_Content/water_Cement_Ratio
cement_Vol = cement_Weight / cement_Density

st.write(f"Con la cantidad de agua determinada: **{water_Content:.1f} kg/m3** y con la relacion **agua/cemento de: {water_Cement_Ratio:.3f},** la cantidad de **cemento necesaria es de {cement_Weight:.0f} kg/m3**")

st.write(f"El volumen de cemento es de: {cement_Vol:.4f} m3/m3 de concreto")

# ---------- CANTIDAD DE GRAVA - GRAVEL CONTENT ----------

st.header("Cálculo Cantidad de Grava")

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

def get_coarse_aggregate_factor(tmn_Mm, fineness_Modulus, table=mf_DataFrame):
    """b/b0 for a TMN and fineness modulus (bilinear interpolation). None if out of range."""

    tmn_Column = table.columns[0]
    tmn_Values = table[tmn_Column].astype(float).values
    mf_Values = np.array(table.columns[1:], dtype=float)

    # Outside the table range cannot be interpolated
    if tmn_Mm < tmn_Values.min() or tmn_Mm > tmn_Values.max():
        return None
    if fineness_Modulus < mf_Values.min() or fineness_Modulus > mf_Values.max():
        return None

    # Interpolate on TMN for each fineness modulus column
    values_At_Tmn = [
        np.interp(tmn_Mm, tmn_Values, table[mf].astype(float).values)
        for mf in table.columns[1:]
    ]

    # Interpolate on fineness modulus
    return float(np.interp(fineness_Modulus, mf_Values, values_At_Tmn))

coarse_Factor = get_coarse_aggregate_factor(tmn_Selected, sand_Mf)

if coarse_Factor is None:
    st.warning("El TMN o el módulo de finura están fuera del rango de la tabla.")
else:
    st.write(f"Relación b/b0: **{coarse_Factor:.3f}**")

b0_Value = gravel_Muc/gravel_Dg

st.write(f"EL valor de b0 es igual al **MUC/dg**. Por lo tanto, el valor de b0 en este análisis es de: **{b0_Value:.4f}**")

b_Value = coarse_Factor*b0_Value 

st.write(f"Luego, el valor del volumen de agregado grueso por cada m3 de concreto se calcula de la siguiente manera: b = (b/b0)*b0. Por lo mismo, el valor de b es igual a: {b_Value:.4f} m3/m3")

gravel_Weight = b_Value * gravel_Dg

st.write(f"Finalmente, el peso de agregado grueso por cada m3 de concreto se calcula de la siguiente manera: W = b*dg Por lo mismo, el valor del peso de agregado grueso es de: {gravel_Weight:.0f} kg/m3 de concreto")

# ---------- CANTIDAD DE ARENA - SAND CONTENT ----------

st.header("Cálculo Cantidad de Agregado Fino")

sand_Vol = 1 - (cement_Vol + water_Content_Vol + b_Value + air_Percentage_Vol)

st.write(f"La cantidad de agregado fino se define hallando la diferencia entre 1 m3 y la sumatoria de todos los demás volumenes hallados durante el diseño. Luego, el **volumen de agregado fino es de {sand_Vol:.4f} m3/m3 de concreto**")

sand_Weight = sand_Vol * sand_Df

st.write(f"El peso del agregado fino es de {sand_Weight:.0f} kg/m3 de concreto")

# ---------- CORRECCION POR HUMEDAD - MOISTURE ADJUSTMENT ----------

st.header("Corrección por Humedad y Dosificación Final")

def calculate_moisture(wet_Weight, dry_Weight):
    """Moisture content (fraction of dry weight)."""
    return (wet_Weight - dry_Weight) / dry_Weight


def calculate_absorption(sss_Weight, dry_Weight):
    """Absorption (fraction of dry weight)."""
    return (sss_Weight - dry_Weight) / dry_Weight


def calculate_water_excess_deficit(weight, moisture, absorption):
    """Water correction vs SSS: positive = add water, negative = remove water."""
    return weight * (absorption - moisture)


def calculate_wet_weight(weight, moisture):
    """Dry weight to wet weight."""
    return weight * (1 + moisture)


# Base: 1 m3 of concrete
if gravel_Dry_Weight <= 0 or sand_Dry_Weight <= 0:
    st.error("Ingresa pesos secos mayores que cero para ambos agregados y verifica los pesos húmedos y SSS.")

elif gravel_Weight < 0 or sand_Weight < 0 or water_Content < 0:
    st.error("Las cantidades de diseño no pueden ser negativas.")

else:
    if (
        gravel_Wet_Weight < gravel_Dry_Weight
        or sand_Wet_Weight < sand_Dry_Weight
        or gravel_Sss_Weight < gravel_Dry_Weight
        or sand_Sss_Weight < sand_Dry_Weight
    ):
        st.warning("Hay pesos húmedos o SSS menores que el peso seco. Revisa los datos de laboratorio.")

    # Moisture and absorption (fractions)
    gravel_H = calculate_moisture(gravel_Wet_Weight, gravel_Dry_Weight)
    gravel_Abs = calculate_absorption(gravel_Sss_Weight, gravel_Dry_Weight)
    sand_H = calculate_moisture(sand_Wet_Weight, sand_Dry_Weight)
    sand_Abs = calculate_absorption(sand_Sss_Weight, sand_Dry_Weight)

    # Wet weights to batch
    gravel_Wet_Weight_Mix = calculate_wet_weight(gravel_Weight, gravel_H)
    sand_Wet_Weight_Mix = calculate_wet_weight(sand_Weight, sand_H)

    # Water correction: positive = add, negative = remove
    gravel_Water_Correction = calculate_water_excess_deficit(gravel_Weight, gravel_H, gravel_Abs)
    sand_Water_Correction = calculate_water_excess_deficit(sand_Weight, sand_H, sand_Abs)
    total_Water_Correction = gravel_Water_Correction + sand_Water_Correction

    # Water to add in the mixer
    corrected_Water = water_Content + total_Water_Correction

    # ---------- CORRECCION POR AGREGADO - CORRECTION PER AGGREGATE ----------

    st.subheader("Corrección por humedad de los agregados")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Agregado grueso")
        st.write(f"Humedad: {gravel_H * 100:.2f} %")
        st.write(f"Absorción: {gravel_Abs * 100:.2f} %")
        st.write(f"Peso húmedo de diseño: {gravel_Wet_Weight_Mix:.2f} kg/m³")
        st.write(f"Corrección de agua: {gravel_Water_Correction:+.2f} kg/m³")

    with col2:
        st.markdown("#### Agregado fino")
        st.write(f"Humedad: {sand_H * 100:.2f} %")
        st.write(f"Absorción: {sand_Abs * 100:.2f} %")
        st.write(f"Peso húmedo de diseño: {sand_Wet_Weight_Mix:.2f} kg/m³")
        st.write(f"Corrección de agua: {sand_Water_Correction:+.2f} kg/m³")

    st.divider()

    st.metric("Corrección total de agua", f"{total_Water_Correction:+.2f} kg/m³")

    if corrected_Water < 0:
        st.error("El agua corregida es negativa. Revisa los datos de diseño, humedad y absorción.")
    else:
        # ---------- DOSIFICACION FINAL - FINAL BATCHING ----------

        st.subheader("Dosificación final corregida")

        col1, col2, col3 = st.columns(3)

        col1.metric("Grava húmeda", f"{gravel_Wet_Weight_Mix:.2f} kg/m³")
        col2.metric("Arena húmeda", f"{sand_Wet_Weight_Mix:.2f} kg/m³")
        col3.metric("Agua corregida", f"{corrected_Water:.2f} kg/m³")

        st.caption(
            "Las masas húmedas son las cantidades de agregado que "
            "se deben dosificar. El agua corregida es la cantidad "
            "que se añade, considerando el agua aportada o absorbida "
            "por los agregados."
        )

        # ---------- TABLA RESUMEN - SUMMARY TABLE ----------

        # Volumes are design volumes (unchanged by moisture), they add up to 1 m3/m3
        materials = [
            {
                "Material": "Cemento",
                "Peso de diseño (kg/m³)": cement_Weight,
                "Corrección de peso (kg/m³)": 0.0,
                "Peso final (kg/m³)": cement_Weight,
                "Volumen (m³/m³)": cement_Vol,
            },
            {
                "Material": "Agregado grueso",
                "Peso de diseño (kg/m³)": gravel_Weight,
                "Corrección de peso (kg/m³)": gravel_Wet_Weight_Mix - gravel_Weight,
                "Peso final (kg/m³)": gravel_Wet_Weight_Mix,
                "Volumen (m³/m³)": b_Value,
            },
            {
                "Material": "Agregado fino",
                "Peso de diseño (kg/m³)": sand_Weight,
                "Corrección de peso (kg/m³)": sand_Wet_Weight_Mix - sand_Weight,
                "Peso final (kg/m³)": sand_Wet_Weight_Mix,
                "Volumen (m³/m³)": sand_Vol,
            },
            {
                "Material": "Agua",
                "Peso de diseño (kg/m³)": water_Content,
                "Corrección de peso (kg/m³)": total_Water_Correction,
                "Peso final (kg/m³)": corrected_Water,
                "Volumen (m³/m³)": water_Content_Vol,
            },
            {
                "Material": "Aire",
                "Peso de diseño (kg/m³)": 0.0,
                "Corrección de peso (kg/m³)": 0.0,
                "Peso final (kg/m³)": 0.0,
                "Volumen (m³/m³)": air_Percentage_Vol,
            },
        ]

        mix_Table = pd.DataFrame(materials)

        st.subheader("Tabla resumen de dosificación por 1 m³")

        st.dataframe(
            mix_Table,
            use_container_width=True,
            hide_index=True
        )

        csv = mix_Table.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Descargar tabla de dosificación (CSV)",
            data=csv,
            file_name="dosificacion_concreto_corregida.csv",
            mime="text/csv"
        )

# ---------- AJUSTE DE MEZCLAS DE PRUEBA - TRIAL BATCH ADJUSTMENT ----------
