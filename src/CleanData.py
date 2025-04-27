

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
def _(pd):
    df = pd.DataFrame(pd.read_csv("../Data/Levels/niveles.csv"))
    return (df,)


@app.cell
def _(df):
    df_no_duplicates = df.drop_duplicates(subset=["Date"], ignore_index=True)
    df_no_duplicates
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
