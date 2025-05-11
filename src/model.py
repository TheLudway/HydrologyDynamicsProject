#!./.venv/bin/python3 
import numpy as np

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
h = np.zeros((N, nt))    # h(x,t)
Q = np.zeros((N, nt))    # Q(x,t)

# Initial conditions (t=0)
# Assume linear profile from h(0,0) to h(L,0)=h(0,0) (or other assumption)
h[:, 0] = np.linspace(h_at_x0[0], h_at_x0[0], N)  # Constant initial profile
# Or use Manning's to estimate Q(x,0):
Q[:, 0] = np.linspace(Q_at_x0[0], Q_at_x0[0]*0.9, N)  # Example linear profile

# Boundary conditions (x=0)
h[0, :] = h_at_x0        # h(0,t) for all t
Q[0, :] = Q_at_x0        # Q(0,t) for all t     

# Time loop
# for n in range(nt):
#     # Update A from h (using channel geometry, e.g., rectangular)
#     A = W * h[n, :]  # Assuming width W is constant
    
#     # Continuity equation (solve for A^{n+1})
#     Q[n+1, 0] = 
