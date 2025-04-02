import numpy as np
import matplotlib.pyplot as plt

# Constants
g = 9.81  # Gravity (m/s^2)
L = 1000  # River length (m)
nx = 100  # Number of spatial points
dx = L / (nx - 1)  # Spatial step
dt = 0.5  # Time step (s)
T = 200  # Total simulation time (s)
n_steps = int(T / dt)  # Number of time steps

# Initial conditions
A = np.ones(nx) * 10  # Initial cross-sectional area (m^2)
Q = np.ones(nx) * 20  # Initial discharge (m^3/s)

# Boundary condition: A flood wave enters at the left boundary
Q[0] += 10  # Increase inflow

# Numerical solution using Lax-Friedrichs scheme
def compute_next_step(A, Q):
    A_new, Q_new = A.copy(), Q.copy()
    
    for i in range(1, nx - 1):
        # Ensure no division by zero
        if A[i] <= 0:
            A[i] = 1e-6  # Small positive value to prevent instability

        # Compute velocity
        u = Q[i] / A[i]
        h = A[i] / 5  # Assuming a rectangular channel with width = 5 m
        Sf = (u * abs(u)) / (25 ** (4/3))  # Manning's equation (n=0.03)

        # Lax-Friedrichs update
        A_new[i] = max(0, 0.5 * (A[i-1] + A[i+1]) - (dt / (2 * dx)) * (Q[i+1] - Q[i-1]))
        Q_new[i] = max(0, 0.5 * (Q[i-1] + Q[i+1]) - (dt / (2 * dx)) * (
            (Q[i+1]**2 / max(A[i+1], 1e-6) + g * A[i+1] * h) - (Q[i-1]**2 / max(A[i-1], 1e-6) + g * A[i-1] * h)
        ) - dt * g * A[i] * Sf)
    
    return A_new, Q_new

# Time stepping
for _ in range(n_steps):
    A, Q = compute_next_step(A, Q)

# Plot results
plt.figure(figsize=(10, 4))
plt.plot(np.linspace(0, L, nx), A, label='Water Cross-Sectional Area (A)')
plt.plot(np.linspace(0, L, nx), Q, label='Discharge (Q)')
plt.xlabel("Distance along river (m)")
plt.ylabel("Values")
plt.legend()
plt.title("Flood Wave Propagation using Saint-Venant Equations")
plt.show()
