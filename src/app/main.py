
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io
import csv 
import uvicorn 
import numpy as np
import matplotlib.pyplot as plt
import zipfile


app = FastAPI()

np.random.seed(42)
# Load data
data = np.genfromtxt('descarga-altura.csv', delimiter=',', skip_header=1)
h_at_x0 = data[:, 1]  # h(0,t) for all t (shape: (nt,))
Q_at_x0 = data[:, 0]  # Q(0,t) for all t (shape: (nt,))

# Parameters
N = 100                  # Number of spatial points
L = 472.74               # River length (m)
dx = L / N               # Spatial step
dt = 0.1                 # Time step
nt = len(Q_at_x0)        # Number of time steps
g = 9.81                 # Gravity (m/s²)
W = 300                  # River width (m)
n_m = 0.018              # Manning's roughness coefficient
s_c = 1                  # Factor de sinuosidad de la ecuación de continuidad.
s_m = 1                  # Factor de sinuosidad de la ecuación de momentum.

# Arrays (N x nt)
h = np.zeros((nt, N))    # h(x,t)
Q = np.zeros((nt, N))    # Q(x,t)


# Condiciones iniciales en la posición inicial para todo t
h[:, 0] = h_at_x0  
Q[:, 0] = Q_at_x0  

# Condición de downstream
Q[:, -1] = np.random.normal(Q[:, 0].mean(), Q[:, 0].std(), Q[:, 0].size)


def create_height(h, mean=h[:,0].mean(), std=h[:, 0].std()):
    """
    Args:
        h: matrix-integer
    """
    for i in range(h.shape[0]):
        for j in range(1, h.shape[1]):
            h[i, j] = np.random.normal(h[i, 0], std)

def calculate_lateral_flow(L, h, Cw=1.84):
    """
    Args:
        Cw: scalar-weir coefficient. Typically 1.84 for sharp-crested; 3.367 1.83 for Cipolletti;
            3.09 1.7 for Broad-crested.
        L:  scalar-Length of the weir crest.
        H:  matrix-surface distance.
    Returns:
        q_L: matrix-lateral flow.
    """
    q_L = np.zeros((nt, N))
    for i in range(nt):
        for j in range(N):
            q_L[i, j] = Cw * L * h[i, j]**1.5
    return q_L


def ql(L1, L2):
    return L1+L2

def sc(real_length, study_length):
    return real_length/study_length

def area_from_initial(Q, h, q_l, s_c=(1, 1), W=300, dt=1, L=472.74, N=100):
    """
    Parameters:
        Q: 2D array (nt x N) of discharge values [m³/s]
        h: 2D array (nt x N) of water heights [m]
        q_l: 2D array (nt x N) of lateral flows [m²/s]
        s_c: tuple (real_length, study_length) for sinuosity calculation
        W: river width (m) [constant or array of size N]
        dt: time step (s)
        L: river length (m)
        N: number of spatial points

    Returns:
        A: 2D numpy array (nt x N) of cross-sectional areas [m²]
    """
    nt = Q.shape[0]
    dx = L / N
    A = np.zeros((nt, N))
    sinuosity = sc(s_c[0], s_c[1])  # path correction factor

    # Initialize first time step
    A[0, :] = h[0, :] * (W if isinstance(W, (int, float)) else W[:N])
    
    for k in range(1, nt):  # Time loop
        A[k, 0] = h[k, 0] * (W if isinstance(W, (int, float)) else W[0])  # Boundary condition
        
        for i in range(1, N):  # Space loop
            dQ_dx = (Q[k-1, i] - Q[k-1, i-1]) / dx if i < N-1 else 0
            A[k, i] = (( (q_l[k, i] - dQ_dx) * dt + sinuosity * (A[k-1, i] + A[k-1, i-1])) / sinuosity ) - A[k-1, i]
            A[k, i] = max(A[k, i], 0)  # Ensure non-negative area

    return A

def momentumEffect(Q, qL, A, B, v=1, seein=0, overin=0):
    """
        Args:
            Todo es escalar.
    """
    if (seein == 1):
        ML1 = 0
    else:
        ML1 = - (Q - qL)/2*A

    if (overin == 1):
        ML2 = -B*v*qL
    else:
        ML2 = - (Q - qL)/A

    return ML1 + ML2

def frictionSlope(u, n, A, L, W, c=1.0):
    """
        Args:
        u: escalar - velocidad del agua.
        n: escalar - Coeficiente de mannings.
        c: escalar - Unidad dependiente constante. 1 en el SI 1.486 en el sistema británico.
        R=L*W: Radio hidráulico (area dividio por el perímetro mojado).
    """
    return (u**2 * n**2) / (c * (A/(L * W))**(2/3))

def headLossSlope(g, Q, A, dx, Ke=0.2):
    """
        Args:
        Ke: escalar - Coeficiente de head loss.
        Q: escalar - cambio en el flujo.
        A: escalar - area.
        g: escalar - gravedad.
        dx: escalar - paso en x.
    """
    return (Ke * (Q/A)**2)/(2*g*dx)


def calculateDischarge(g, A, W, dx, dt, n, L, beta, Q_upstream, qL, u, sm=(1,1), N=100):
    """
    Calculate discharge (Q) along the river for all time steps using finite differences
    
    Parameters:
        g: gravitational acceleration (m/s²)
        A: 2D array of cross-sectional areas (m²) [size nt x N]
        W: array of river widths (m) [size N]
        dx: spatial step (m)
        dt: time step (s)
        n: Manning's roughness coefficient
        L: river length (m)
        beta: momentum coefficient
        Q_upstream: array of upstream boundary conditions (m³/s) [size nt]
        qL: 2D array of lateral inflows (m²/s) [size nt x N]
        u: characteristic velocity (m/s)
        sm: tuple of sinuosity coefficients (default (1,1))
        N: number of spatial points
        
    Returns:
        Q_extra: 2D array of discharge values [size nt x N]
    """
    nt = len(Q_upstream)
    Q_extra = np.zeros((nt, N))
    Sm = sm[0]  # Sinuosity coefficient for momentum equation
    Q_extra[:, 0] = Q_upstream
    for k in range(nt):  # Time loop
        # Q_extra[k, 0] = Q_upstream[k]  # Upstream boundary condition
        
        for i in range(1, N):  # Space loop
            # Current and previous cross-sectional areas
            A_i = max(A[k, i], 1e-3)
            A_im1 = max(A[k, i-1], 1e-3)
            
            # Momentum effect from lateral flow
            ML = min(qL[k, i-1] * u, 0.1 * Q_extra[k, i-1]) #if i < N else 0
            
            # Friction slope (Manning's equation)
            R = A_i / (W[i] + 2*A_i/W[i])  # Hydraulic radius
            Sf = (n**2 * Q_extra[k, i-1] * abs(Q_extra[k, i-1])) / (A_i**2 * R**(4/3))
            
            # Expansion/contraction loss (simplified)
            Sec = 0.1 * (A_i - A_im1)/dx #if i > 1 else 0
            
            # Calculate the discharge at point i
            term1 = -ML - g*A_i*(( (A_i/W[i] - A_im1/W[i-1])/dx + Sf + Sec ))
            term2 = - (beta*Q_extra[k, i-1]**2/A_i - beta*Q_extra[k, i-1]**2/A_im1)/dx
            Q_extra[k, i] = ( (term1 + term2)*dt + Sm*Q_extra[k, i-1] ) / Sm
            
            # Ensure physical realism
            Q_extra[k, i] = max(min(Q_extra[k, i], 2*Q_upstream[k]), 0)
    
    return Q_extra


def create_plot(data, title, ylabel, label):
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(data)), data, color="blue", marker="o", label=label)
    ax.set_xlabel("Tiempo (días)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf



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
        "area_upstream.png": create_area_plot(A[:, 0], "Área por cada día en la posición inicial"),
        "area_midstream.png": create_area_plot(A[:, A.shape[1] // 2], "Área por cada día en la mitad del camino"),
        "area_downstream.png": create_area_plot(A[:, -1], "Área por cada día en la posición final"),
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

