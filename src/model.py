#!./.venv/bin/python3 
import numpy as np
import random
import matplotlib.pyplot as plt 

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

def area_from_initial(Q0, Q1, h0, q_l, s_c=(1, 1), W=300, dt=1, L=472.74, N=100):
    """
    Estimate area A(x) using only initial discharge and height.

    Parameters:
        Q0: scalar, initial discharge at x=0
        h0: scalar, initial height at x=0
        q_l: vector, lateral flow at time t q_l[t]
        s_c: tuple (real_length, study_length) to compute sinuosity
        W: river width (m)
        dx: spatial step (m)
        N: number of spatial points

    Returns:
        A: 1D numpy array of shape (N,) with area at each x
    """
    dx = L/N
    A = np.zeros(N)
    A[0] = h0 * W

    sinuosity = sc(s_c[0], s_c[1])     # path correction factor

    for j in range(1, N):
        dQ_dx = (Q1-Q0)/dx
        A[j] = (( (q_l[j-1] - dQ_dx) * dt + sinuosity * (A[0]+A[j - 1])) / sinuosity) - A[j-1] 

    return A

def momentumEffect(Q, qL, A, B, v, seein=0, overin=0):
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

def frictionSlope(u, n, R, c=1.0):
    """
        Args:
        u: escalar - velocidad del agua.
        n: escalar - Coeficiente de mannings.
        c: escalar - Unidad dependiente constante. 1 en el SI 1.486 en el sistema británico.
        R: Radio hidráulico (area dividio por el perímetro mojado).
    """
    return (u**2 * n**2) / (c * R**(2/3))

def headLossSlope(Ke, g, Q, A, dx):
    """
        Args:
        Ke: escalar - Coeficiente de head loss.
        Q: escalar - cambio en el flujo.
        A: escalar - area.
        g: escalar - gravedad.
        dx: escalar - paso en x.
    """
    return Ke * (Q/A)**2
