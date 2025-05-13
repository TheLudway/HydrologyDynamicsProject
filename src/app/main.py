
from fastapi import UploadFile, File, FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from demo import *
from plot import *
import io
import csv 
import uvicorn 
import numpy as np
import matplotlib.pyplot as plt
import zipfile
import json


description = """

La API que permite determinar cosas de hidrodinámica y cosas del caudal y del área transversal.

# TODO

Muchas cosas, falta la documentación


"""



app = FastAPI(
    title="Saint-Venant-Finite-Differences",
    description=description,
    summary="Permite resolver las ecuaciones de Saint-Venant utilizando diferencias finitas.",
    version="0.0.1",
    contact={
        "name": "Ludwig Alvarado Becerra",
        "url": "https://www.github.com/theludway",
        "email": "ludwig.alvaradob@utadeo.edu.co"
    },
    license_info={
        "name": "GPL V3",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    },
)



@app.post("/simulate")
async def simulate_from_json(json_file: UploadFile = File(...)):
    # === Read and parse JSON ===
    content = await json_file.read()
    params = json.loads(content)

    # === Extract values ===
    Q = np.array(params["Caudal"])                      # shape (nt, N)
    h = np.array(params["Height"])                      # shape (nt, N)
    nt, N = Q.shape                                     # aseguramos dimensiones

    W = float(params["RiverWidth"])
    n_m = float(params["Mannings_Roughness"])
    dt = float(params["TimeStep"])
    L = float(params["Length"])
    v = float(params["Velocity"])
    L_real = float(params["RiverRealLength"])
    L_euclid = float(params["RiverEucledianDistance"])
    g = float(params["Gravity"])
    beta = float(params["BetaCoefficient"])
    K = float(params["CoefcicienteHeadLoss"])

    dx = L / N

    # === Run Simulation ===
    create_height(h, std=0.05)
    q_L = calculate_lateral_flow(dx, h, N=N, nt=nt)  # ✅ flujo lateral dinámico
    A = area_from_initial(Q, h, q_L, s_c=[L_real, L_euclid], W=W, dt=dt, L=L, N=N)

    Q_f = calculateDischarge(g, A, np.full(N, W), dx, dt, n_m, L, beta, Q[:, 0], q_L, v, sm=[L_real, L_euclid], N=N)

    # === Save CSVs ===
    qf_csv = io.StringIO()
    a_csv = io.StringIO()
    np.savetxt(qf_csv, Q_f, delimiter=",")
    np.savetxt(a_csv, A, delimiter=",")

    # === Generate plots ===
    plots = {
        "area_upstream.png": create_plot(A[:, 0], "Área por cada día en la posición inicial", "Área de la Sección Transversal", "Área Sección Transversal"),
        "area_midstream.png": create_plot(A[:, A.shape[1] // 2], "Área por cada día en la mitad del camino", "Área de la Sección Transversal", "Área Sección Transversal"),
        "area_downstream.png": create_plot(A[:, -1], "Área por cada día en la posición final", "Área de la Sección Transversal", "Área Sección Transversal"),
        "discharge_upstream.png": create_plot(Q_f[:, 0], "Caudal por día en la posición inicial", "Caudal (m³/s)", "Caudal"),
        "discharge_midstream.png": create_plot(Q_f[:, Q_f.shape[1] // 2], "Caudal por día en la mitad del camino", "Caudal (m³/s)", "Caudal"),
        "discharge_downstream.png": create_plot(Q_f[:, -1], "Caudal por día en la posición final", "Caudal (m³/s)", "Caudal"),
    }

    # === Build ZIP ===
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.writestr("Q_f.csv", qf_csv.getvalue())
        z.writestr("A.csv", a_csv.getvalue())
        for filename, plot_buf in plots.items():
            z.writestr(filename, plot_buf.getvalue())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=simulation.zip"}
    )

@app.get("/demo")
async def calculate_matrices():
    # === Compute matrices ===
    create_height(h, std=0.05)
    q_L = calculate_lateral_flow(dx, h)
    A = area_from_initial(Q, h, q_L)
    Q_f = calculateDischarge(g, A, np.full(N, W), dx, dt, n_m, L, 1.05, Q[:, 0], q_L, 2)

    # === CSVs ===
    qf_csv = io.StringIO()
    a_csv = io.StringIO()
    csv.writer(qf_csv).writerows(Q_f.tolist())
    csv.writer(a_csv).writerows(A.tolist())

    # === Plots ===
    plots = {
        "area_upstream.png": create_plot(A[:, 0], "Área por cada día en la posición inicial", "Área de la Sección Transversal", "Área Sección Transversal"),
        "area_midstream.png": create_plot(A[:, A.shape[1] // 2], "Área por cada día en la mitad del camino", "Área de la Sección Transversal", "Área Seccion Transversal"),
        "area_downstream.png": create_plot(A[:, -1], "Área por cada día en la posición final", "Área de la Sección Transversal", "Área Seccion Transversal"),
        "discharge_upstream.png": create_plot(Q_f[:, 0], "Caudal por día en la posición inicial", "Caudal (m³/s)", "Caudal"),
        "discharge_midstream.png": create_plot(Q_f[:, Q_f.shape[1] // 2], "Caudal por día en la mitad del camino", "Caudal (m³/s)", "Caudal"),
        "discharge_downstream.png": create_plot(Q_f[:, -1], "Caudal por día en la posición final", "Caudal (m³/s)", "Caudal"),
    }

    # === Create ZIP ===
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("Q_f.csv", qf_csv.getvalue())
        zip_file.writestr("A.csv", a_csv.getvalue())
        for name, buf in plots.items():
            zip_file.writestr(name, buf.getvalue())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=demo_outputs.zip"}
    )

