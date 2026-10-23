import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


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

def formato_rango(r):
    return f"{r.left:g} - {r.right:g}"          # 0.0 -> "0", 3.5 -> "3.5"

def formato_lista(lista):
    return "; ".join(lista)

tabla_vista = settlement_Table.copy()
tabla_vista["Asentamiento (cm)"] = tabla_vista["Asentamiento (cm)"].apply(formato_rango)
tabla_vista["Tipo de estructura y condiciones de colocación"] = (
    tabla_vista["Tipo de estructura y condiciones de colocación"].apply(formato_lista)
)

st.title("Asentamiento")
st.table(tabla_vista)

selected_Settlement = st.number_input("Asentamiento elegido (cm)", min_value=1.0, step=1.0)

selected_Settlement_In = selected_Settlement * 2.54

# --------------- TMN (tamaño máximo nominal del agregado) - NMAS (Nominal Maximum Aggregate Size) ---------------

# ---------- Agregado Grueso / Gravel ------------
st.title("Granulometría Agregado Grueso")

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

# Tabla editable: solo la columna de peso se puede modificar

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

# Crear DataFrame
air_Content_Table_Copy = pd.DataFrame(air_Content_Table)

# Mostrar tabla
st.title("Porcentaje de aire atrapado en el concreto")

st.dataframe(
    air_Content_Table_Copy,
    use_container_width=True,
    hide_index=True
)

# Sección de interpolación
st.subheader("Cálculo del porcentaje de aire atrapado")

df = air_Content_Table_Copy.sort_values(
    "Tamaño (mm)"
).reset_index(drop=True)

columna_porcentaje = (
    "Porcentaje Promedio aproximado de aire atrapado (%)"
)

# Elegir el modo de cálculo
modo = st.radio(
    "¿Cómo deseas ingresar el tamaño del agregado?",
    [
        "Seleccionar un tamaño de la tabla",
        "Ingresar un tamaño personalizado"
    ],
    horizontal=True
)

if modo == "Seleccionar un tamaño de la tabla":

    # Crear opciones con tamaño en mm y pulgadas
    opciones = {
        f"{fila['Agregado grueso (pulg.)']} "
        f"({fila['Tamaño (mm)']:.2f} mm)": fila["Tamaño (mm)"]
        for _, fila in df.iterrows()
    }

    seleccion = st.selectbox(
        "Selecciona el tamaño del agregado:",
        options=list(opciones.keys())
    )

    tamano_agregado = opciones[seleccion]

else:

    tamano_agregado = st.number_input(
        "Ingresa el tamaño del agregado (mm):",
        min_value=float(df["Tamaño (mm)"].min()),
        max_value=float(df["Tamaño (mm)"].max()),
        value=20.00,
        step=0.01,
        format="%.2f"
    )

# Botón de cálculo
if st.button("Calcular porcentaje de aire atrapado"):

    tamanos = df["Tamaño (mm)"].to_numpy()
    porcentajes = df[columna_porcentaje].to_numpy()

    # Verificar si el tamaño está en la tabla
    coincidencia = df[
        np.isclose(
            df["Tamaño (mm)"],
            tamano_agregado,
            atol=1e-8,
            rtol=0
        )
    ]

    if not coincidencia.empty:

        # Valor exacto de la tabla
        porcentaje = float(
            coincidencia.iloc[0][columna_porcentaje]
        )

        st.success(f"Porcentaje de aire atrapado: {porcentaje:.2f} %")
        st.info(f"Valor decimal: {porcentaje / 100:.4f}")

        st.caption("Resultado exacto de la tabla original.")

    else:

        # Interpolación lineal
        porcentaje = float(
            np.interp(
                tamano_agregado,
                tamanos,
                porcentajes
            )
        )

        st.success(f"Porcentaje estimado de aire atrapado: {porcentaje:.3f} %")
        st.info(f"Valor decimal: {porcentaje / 100:.5f}")

        st.caption("Resultado calculado mediante interpolación lineal.")


# CANTIDAD DE AGUA



# RELACION AGUA CEMENTO



# CONTENIDO DE CEMENTO



# ESTIMAR CANTIDAD DE GRAVA



# ESTIMAR CANTIDAD DE ARENA



# AJUSTAR CANTIDAD DE AGUA POR HUMEDAD



# AJUSTAR MEZCLAS DE PRUEBA


