

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


@app.cell
def _(mo):
    mo.md(
        r"""
        # Limpieza de Datos

        Después de hacer web scrapping, los datos de las fechas quedan muy desordenados.
        """
    )
    return


@app.cell
def _(pd):
    df = pd.DataFrame(pd.read_csv("../Data/Levels/niveles.csv"))
    return (df,)


@app.cell
def _(df, pd):
    df_no_duplicates = df.drop_duplicates(subset=["Date"], ignore_index=True)
    df_no_duplicates.rename(columns={"Value":"Value (m)"}, inplace=True)
    df_no_duplicates["Date"] = pd.to_datetime(df_no_duplicates["Date"], format="%b/%d/%y")
    df_no_duplicates.sort_values(by="Date", ascending=True)
    return


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
