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


def chargeFromInitial(g, A, W, dx, dt, n, L, beta, Q_upstream, qL, u, sm=(1,1), N=100):
    """
    Calculate initial discharge (Q) along the river using finite differences
    
    Parameters:
        g: gravitational acceleration (m/s²)
        A: array of cross-sectional areas (m²) at t=0 [size N]
        W: array of river widths (m) [size N]
        dx: spatial step (m)
        dt: time step (s)
        n: Manning's roughness coefficient
        L: river length (m)
        beta: momentum coefficient
        Q_upstream: upstream boundary condition (m³/s)
        qL: array of lateral inflows (m²/s) [size N-1]
        u: characteristic velocity (m/s)
        sm: tuple of sinuosity coefficients (default (1,1))
        N: number of spatial points
        
    Returns:
        Q: array of discharge values along the river (m³/s) [size N]
    """
    Q = np.zeros(N)
    Q[0] = Q_upstream  # Upstream boundary condition
    
    Sm = sm[0]  # Sinuosity coefficient for momentum equation
    
    for i in range(1, N):
        # Calculate terms for momentum equation
        A_i = A[i]
        A_im1 = A[i-1]
        W_i = W[i]
        W_im1 = W[i-1]
        
        # Momentum effect from lateral flow
        ML = qL[i-1] * u if i < len(qL) else 0  # Simplified momentum effect
        
        # Friction slope (Manning's equation)
        R = A_i / (W_i + 2*A_i/W_i)  # Hydraulic radius
        Sf = (n**2 * Q[i-1] * abs(Q[i-1])) / (A_i**2 * R**(4/3))
        
        # Expansion/contraction loss (simplified)
        Sec = 0.1 * (A_i - A_im1)/dx if i > 1 else 0
        
        # Calculate the discharge at point i
        term1 = -ML - g*A_i*(( (A_i/W_i - A_im1/W_im1)/dx + Sf + Sec ))
        term2 = - (beta*Q[i-1]**2/A_i - beta*Q[i-1]**2/A_im1)/dx
        Q[i] = ( (term1 + term2)*dt + Sm*Q[i-1] ) / Sm
        
        # Ensure physical realism
        Q[i] = max(Q[i], 0)  # Discharge can't be negative
        
    return Q


create_height(h, std=0.05)
q_L = calculate_lateral_flow(dx, h)
A = area_from_initial(Q[0, 0], Q[1, 0], h[0, 0], q_l = q_L[0])
Q_extra = chargeFromInitial(g, A, np.full(len(A), 300), dx, dt, n_m, L, 1.05, Q[0, 0], q_L[0], 1.1)
