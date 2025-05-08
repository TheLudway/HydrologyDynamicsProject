#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# Parámetros para la simulación
nx = 100 # Número de pasos en el espacio.
nt = 500  # Número de pasos en el tiempo.
dx = 10.0 # Proporción del espacio (m).
dt = 0.1  # Paso del tiempo (s).
W = 5.0 # Ancho del río.
g = 9.81 # Gravedad.
beta = 1.0
Sf = 0.001
Sec = 0.001
nu = 0.01  # Diffusion coefficient

# Initialize arrays
A = np.zeros((nx, nt))
Q = np.zeros((nx, nt))
A0 = np.zeros((nx, nt))
qL = np.zeros((nx, nt))
ML = np.zeros((nx, nt))

# Smoother initial condition
x = np.linspace(0, nx*dx, nx)
A[:, 0] = 10.0
Q[:, 0] = 50

# Simulation loop
for j in range(nt - 1):
    # Boundary conditions
    Q[0, j+1] = Q[0, j]  # Upstream
    A[-1, j+1] = A[-1, j]  # Downstream
    
    for i in range(1, nx-1):
        # Continuity equation
        A[i, j+1] = ((qL[i, j] - (Q[i, j] - Q[i-1, j]) / dx) * dt +
                     (A[i, j] + A0[i, j])) - A0[i, j+1]
        
        # Momentum equation
        h_i = A[i, j] / W
        h_im1 = A[i-1, j] / W
        slope_term = (h_i - h_im1) / dx + Sf + Sec

        betaQ2A_i = Q[i, j]**2 / (A[i, j] + 1e-10)
        betaQ2A_im1 = Q[i-1, j]**2 / (A[i-1, j] + 1e-10)
        momentum_flux = (betaQ2A_i - betaQ2A_im1) / dx

        diffusion = nu * (Q[i+1, j] - 2*Q[i, j] + Q[i-1, j])/dx**2
        
        Q[i, j+1] = ((-ML[i, j] - g * A[i, j] * slope_term - momentum_flux) * dt 
                    + Q[i, j] + diffusion)
        
        # Limit extreme values
        Q[i, j+1] = np.clip(Q[i, j+1], -100, 100)

# Plotting
time_steps = [0, 100, 200, 300, 400]
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

for t in time_steps:
    axs[0].plot(range(nx), A[:, t], label=f'Time {t*dt:.0f}s')
    axs[1].plot(range(nx), Q[:, t], label=f'Time {t*dt:.0f}s')

axs[0].set_ylabel("Area (A)")
axs[1].set_ylabel("Discharge (Q)")
axs[1].set_xlabel("Spatial Position")
axs[0].legend()
axs[1].legend()
plt.tight_layout()
plt.show()
