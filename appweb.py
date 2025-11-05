# ======================================================
# APP WEB - Análisis de Mortalidad en Colombia (2019)
# Desarrollado en Python con Dash y Plotly
# ======================================================

import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table

# ============================================
# CARGA DE DATOS (rutas automáticas para Render)
# ============================================
ruta = os.path.dirname(os.path.abspath(__file__))

df_mortalidad = pd.read_excel(os.path.join(ruta, "Anexo1.NoFetal2019_CE_15-03-23.xlsx"))
df_codigos = pd.read_excel(os.path.join(ruta, "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"))
df_divipola = pd.read_excel(os.path.join(ruta, "Divipola_CE_.xlsx"))

# ============================================
# LIMPIEZA DE COLUMNAS
# ============================================
for df in [df_mortalidad, df_codigos, df_divipola]:
    df.columns = (
        df.columns.str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("Ó", "O")
        .str.replace("Í", "I")
        .str.replace("É", "E")
        .str.replace("Á", "A")
        .str.replace("Ú", "U")
    )

# ============================================
# NORMALIZACIÓN DE CÓDIGOS Y LIMPIEZA DIVIPOLA
# ============================================
# Convertir a texto sin espacios
for col in ["COD_DEPARTAMENTO", "COD_MUNICIPIO"]:
    if col in df_mortalidad.columns:
        df_mortalidad[col] = df_mortalidad[col].astype(str).str.strip()
    if col in df_divipola.columns:
        df_divipola[col] = df_divipola[col].astype(str).str.strip()

# Dejar un solo registro por municipio (evita duplicados)
df_divipola = df_divipola.drop_duplicates(subset=["COD_MUNICIPIO"], keep="first")

print("Tamaño Divipola limpio:", df_divipola.shape)
print("Tamaño Mortalidad:", df_mortalidad.shape)

# ============================================
# MERGE SEGURO POR MUNICIPIO Y DEPARTAMENTO
# ============================================
if "COD_MUNICIPIO" in df_mortalidad.columns and "COD_MUNICIPIO" in df_divipola.columns:
    df_mortalidad = df_mortalidad.merge(
        df_divipola[["COD_MUNICIPIO", "MUNICIPIO"]],
        on="COD_MUNICIPIO",
        how="left"
    )

if "COD_DEPARTAMENTO" in df_mortalidad.columns and "COD_DEPARTAMENTO" in df_divipola.columns:
    df_mortalidad = df_mortalidad.merge(
        df_divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates(),
        on="COD_DEPARTAMENTO",
        how="left"
    )

print("Filas después del merge:", len(df_mortalidad))

# ============================================
# USO DE MANERA_MUERTE COMO COLUMNA DE CAUSA
# ============================================
col_causa = "MANERA_MUERTE"
if col_causa not in df_mortalidad.columns:
    raise KeyError("No se encontró la columna 'MANERA_MUERTE' en el archivo de mortalidad.")

# ============================================
# MAPA: MUERTES POR DEPARTAMENTO
# ============================================
import json
import requests

# ===============================
# MAPA DE COLOMBIA POR DEPARTAMENTO
# ===============================
import json
import requests

# ===============================
# MAPA DE COLOMBIA POR DEPARTAMENTO
# ===============================
import os
import json
import requests
import plotly.express as px

# ===============================
# MAPA DE COLOMBIA POR DEPARTAMENTO
# ===============================

muertes_departamento = df_mortalidad.groupby("DEPARTAMENTO").size().reset_index(name="TOTAL_MUERTES")
fig_mapa = px.choropleth(
    muertes_departamento,
    locations="DEPARTAMENTO",
    color="TOTAL_MUERTES",
    title="Distribución total de muertes por departamento (2019)",
    color_continuous_scale="Reds"
)



# ============================================
# GRÁFICO DE LÍNEAS: MUERTES POR MES
# ============================================
mes_col = next((col for col in df_mortalidad.columns if "MES" in col), None)
if mes_col:
    muertes_mes = df_mortalidad.groupby(mes_col).size().reset_index(name="TOTAL_MUERTES")
    fig_lineas = px.line(
        muertes_mes,
        x=mes_col,
        y="TOTAL_MUERTES",
        markers=True,
        title="Total de muertes por mes en Colombia (2019)"
    )
else:
    fig_lineas = px.line(title="No se encontró la columna de mes en los datos")

# ============================================
# GRÁFICO DE BARRAS: 5 MANERAS DE MUERTE MÁS FRECUENTES
# ============================================
top_causas = df_mortalidad[col_causa].value_counts().head(5).reset_index()
top_causas.columns = ["MANERA_MUERTE", "TOTAL_CASOS"]
fig_barras_violentas = px.bar(
    top_causas,
    x="MANERA_MUERTE",
    y="TOTAL_CASOS",
    title="5 maneras de muerte más frecuentes en Colombia (2019)",
    color="MANERA_MUERTE"
)

# ============================================
# GRÁFICO CIRCULAR: 10 MUNICIPIOS CON MENOR MORTALIDAD
# ============================================
muertes_ciudad = df_mortalidad.groupby("MUNICIPIO").size().reset_index(name="TOTAL_MUERTES")
ciudades_menor = muertes_ciudad.nsmallest(10, "TOTAL_MUERTES")
fig_circular = px.pie(
    ciudades_menor,
    values="TOTAL_MUERTES",
    names="MUNICIPIO",
    title="10 municipios con menor mortalidad (2019)"
)

# ============================================
# TABLA: 10 PRINCIPALES MANERAS DE MUERTE
# ============================================
causas_top10 = (
    df_mortalidad[col_causa]
    .value_counts()
    .head(10)
    .reset_index()
    .rename(columns={"index": "MANERA_MUERTE", col_causa: "TOTAL_CASOS"})
)

# ============================================
# BARRAS APILADAS: MUERTES POR SEXO Y DEPARTAMENTO
# ============================================
if "SEXO" in df_mortalidad.columns:
    muertes_sexo_dep = df_mortalidad.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="TOTAL_MUERTES")
    fig_barras_apiladas = px.bar(
        muertes_sexo_dep,
        x="DEPARTAMENTO",
        y="TOTAL_MUERTES",
        color="SEXO",
        title="Muertes por sexo y departamento (2019)",
        barmode="stack"
    )
else:
    fig_barras_apiladas = px.bar(title="No se encontró la columna 'SEXO' en los datos")

# ============================================
# HISTOGRAMA: DISTRIBUCIÓN POR GRUPO DE EDAD
# ============================================
df_mortalidad["GRUPO_EDAD1"] = pd.to_numeric(df_mortalidad.get("GRUPO_EDAD1", pd.Series()), errors="coerce")

rangos = {
    "Mortalidad neonatal": range(0, 5),
    "Mortalidad infantil": range(5, 7),
    "Primera infancia": range(7, 9),
    "Niñez": range(9, 11),
    "Adolescencia": [11],
    "Juventud": range(12, 14),
    "Adultez temprana": range(14, 17),
    "Adultez intermedia": range(17, 20),
    "Vejez": range(20, 25),
    "Longevidad / Centenarios": range(25, 29),
    "Edad desconocida": [29]
}

def asignar_rango(codigo):
    for k, v in rangos.items():
        if codigo in v:
            return k
    return "Desconocido"

if "GRUPO_EDAD1" in df_mortalidad.columns:
    df_mortalidad["RANGO_EDAD"] = df_mortalidad["GRUPO_EDAD1"].apply(asignar_rango)
    fig_histograma = px.histogram(
        df_mortalidad,
        x="RANGO_EDAD",
        title="Distribución de muertes por rango de edad (2019)"
    )
else:
    fig_histograma = px.histogram(title="No se encontró la columna 'GRUPO_EDAD1' en los datos")

# ============================================
# APLICACIÓN DASH
# ============================================
app = Dash(__name__)
app.title = "Mortalidad en Colombia 2019"

app.layout = html.Div([
    html.H1("Análisis de Mortalidad en Colombia - 2019", style={"textAlign": "center"}),

    dcc.Graph(figure=fig_mapa),
    dcc.Graph(figure=fig_lineas),
    dcc.Graph(figure=fig_barras_violentas),
    dcc.Graph(figure=fig_circular),

    html.H3("10 principales maneras de muerte en Colombia (2019)"),
    dash_table.DataTable(
        data=causas_top10.to_dict("records"),
        columns=[{"name": i, "id": i} for i in causas_top10.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'}
    ),

    dcc.Graph(figure=fig_barras_apiladas),
    dcc.Graph(figure=fig_histograma)
])

if __name__ == '__main__':
    app.run(debug=True)
