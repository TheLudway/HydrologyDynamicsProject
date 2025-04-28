

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import pandas as pd 
    return (pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Limpieza de Datos""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Elevación del río""")
    return


@app.cell(hide_code=True)
def _(pd):
    df = pd.DataFrame(pd.read_csv("../Data/Levels/niveles.csv"))
    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Se tienen en total 1800 filas de datos, sin embargo, no se repiten 223, por lo tanto, en la siguiente celda se eliminan los duplicados y se renombra la columna "Value" a "Value (m)".""")
    return


@app.cell(hide_code=True)
def _(df, pd):
    # Create a copy of the DataFrame to avoid modifying the original DataFrame
    df_no_duplicates = df.drop_duplicates(subset=["Date"], ignore_index=True).copy()

    # Rename the 'Value' column to 'Value (m)'
    df_no_duplicates.rename(columns={"Value": "Value (m)"}, inplace=True)

    # Convert the 'Date' column to datetime
    df_no_duplicates["Date"] = pd.to_datetime(df_no_duplicates["Date"], format="%b/%d/%y")

    # Sort the DataFrame by 'Date'
    df_no_duplicates = df_no_duplicates.sort_values(by="Date", ascending=True)
    df_no_duplicates
    return (df_no_duplicates,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Caudal del río

        Después de realizar la limpieza de la meta-data utilizando comandos de UNIX, ahora se va a pasar a un formato de tablas para que pueda ser mejor procesador por Python y Pandas. Por último, se limpia de los valores nulos el dataset, y se renombra la columna a Value (m³/s).
        """
    )
    return


@app.cell(hide_code=True)
def _(pd):
    df_caudal = pd.read_csv("../Data/Discharge/Caudal.txt", delimiter=";")
    df_caudal["YYYY-MM-DD"] = pd.to_datetime(df_caudal["YYYY-MM-DD"], format="%Y-%m-%d")
    df_caudal.rename(columns={"YYYY-MM-DD":"Date", " Value": "Value (m³/s)"}, inplace=True)
    df_caudal_clean = df_caudal[df_caudal["Value (m³/s)"] != -999.000]
    return (df_caudal_clean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Filtrar datos

        Debido a que los datos del caudal y de la elevación del río son diferentes en las fechas. Se va a filtrar un período que tenga una variabilidad climática similar. Se fija entonces un intervalo desde octubre de 2017 a mayo de 2018 para los datos del caudal y un intervalo desde septiembre de 2024 a abril de 2025. 
        """
    )
    return


@app.cell
def _(df_caudal_clean):
    df_caudal_clean.set_index("Date", inplace=True)
    return


@app.cell
def _(df_caudal_clean):
    df_caudal_filter = df_caudal_clean.rename(columns={"Value (m³/s)":"Caudal (m³/s)"}).loc["2017-10-01":"2018-05-11"]
    df_caudal_filter
    return


@app.cell
def _(df_no_duplicates):
    df_elevation = df_no_duplicates.set_index("Date")
    df_elevation.rename(columns={"Value (m)":"Elevation (m)"}, inplace=True)
    df_elevation
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
