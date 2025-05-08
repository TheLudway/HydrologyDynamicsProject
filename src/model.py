#!./.venv/bin/python3 

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

# Parameters from the problem specification
# Physical parameters
g = 9.81  # Acceleration due to gravity (m/s^2)
s_c = 1.0  # Sinuosity coefficient (assuming straight channel)
s_m = 1.0  # Sinuosity factor for momentum (assuming straight channel)
beta = 1.0  # Momentum coefficient (assuming uniform velocity distribution)

# Channel geometry
L = 10000  # Length of the river (m) - 10 km
base_width = 20.0  # Base width of trapezoidal channel (m)
side_slope = 2.0  # Horizontal:Vertical side slope ratio (2:1)
S0 = 0.001  # Bed slope (m/m)
n = 0.020  # Manning's roughness coefficient

# Simulation parameters
dx = 100  # Spatial step (m) as given
nx = 101  # Number of nodes as given
T = 7 * 24 * 3600  # Simulation time (s) - 1 week
# Calculate time step using Courant condition (for stability)
initial_depth = 1.44  # Initial guess for depth
initial_velocity = (1.0/n) * initial_depth**(2/3) * np.sqrt(S0)  # Manning's equation
courant_number = 0.8  # Safety factor
dt_calculated = courant_number * dx / (initial_velocity + np.sqrt(g * initial_depth))
dt = int(dt_calculated)  # Round to nearest second for simplicity
print(f"Time step: {dt} seconds")
nt = int(T / dt) + 1  # Temporal grid points

# Initialize arrays
A = np.zeros((nx, nt))  # Cross-sectional area
A0 = np.zeros((nx, nt))  # Base cross-sectional area (not used in this case, set to 0)
Q = np.zeros((nx, nt))  # Discharge (m^3/s)
h_r = np.zeros((nx, nt))  # River height/depth (m)
W = np.zeros((nx, nt))  # Top width of water surface

# Function to calculate trapezoidal channel properties
def calculate_channel_properties(depth):
    """Calculate cross-sectional area and top width for a trapezoidal channel."""
    area = base_width * depth + side_slope * depth**2
    top_width = base_width + 2 * side_slope * depth
    return area, top_width

# Set downstream boundary condition - constant depth of 1.44 m
downstream_depth = 1.44  # m
downstream_area, downstream_width = calculate_channel_properties(downstream_depth)
h_r[-1, :] = downstream_depth
A[-1, :] = downstream_area
W[-1, :] = downstream_width

# Initial conditions - assume uniform flow with downstream depth
for i in range(nx):
    h_r[i, 0] = downstream_depth
    A[i, 0], W[i, 0] = calculate_channel_properties(h_r[i, 0])
    
    # Calculate initial discharge using Manning's equation
    hydraulic_radius = A[i, 0] / (base_width + 2 * h_r[i, 0] * np.sqrt(1 + side_slope**2))
    Q[i, 0] = (1.0/n) * A[i, 0] * hydraulic_radius**(2/3) * np.sqrt(S0)

# Print initial discharge for reference
print(f"Initial discharge: {Q[0, 0]:.2f} m³/s")

# Upstream boundary condition - triangular hydrograph
# Define peak parameters - we'll assume peak at 1 day with 3x the base flow
base_flow = Q[0, 0] 
peak_flow = 3 * base_flow
peak_time_hours = 24  # Peak at 1 day
peak_time_index = int(peak_time_hours * 3600 / dt)
total_hydrograph_duration_hours = 48  # Total duration of the hydrograph event (2 days)
total_hydrograph_duration_index = int(total_hydrograph_duration_hours * 3600 / dt)

# Create triangular hydrograph
for j in range(nt):
    if j <= peak_time_index:
        # Rising limb
        Q[0, j] = base_flow + (peak_flow - base_flow) * (j / peak_time_index)
    elif j <= total_hydrograph_duration_index:
        # Falling limb
        Q[0, j] = peak_flow - (peak_flow - base_flow) * ((j - peak_time_index) / (total_hydrograph_duration_index - peak_time_index))
    else:
        # Return to base flow
        Q[0, j] = base_flow

# Define functions for the terms in the Saint-Venant equations
def calculate_q_L(i, j):
    """Calculate lateral flow."""
    # No lateral flow in this problem
    return 0

def calculate_M_L(i, j):
    """Calculate lateral momentum flux."""
    # No lateral momentum flux in this problem
    return 0

def calculate_friction_slope(i, j):
    """Calculate friction slope using Manning's equation."""
    if A[i, j] <= 0 or abs(Q[i, j]) <= 1e-6:
        return 0
    
    wetted_perimeter = base_width + 2 * h_r[i, j] * np.sqrt(1 + side_slope**2)
    hydraulic_radius = A[i, j] / wetted_perimeter
    
    return (n**2 * abs(Q[i, j]) * Q[i, j]) / (A[i, j]**2 * hydraulic_radius**(4/3))

def calculate_energy_loss(i, j):
    """Calculate energy loss due to expansion/contraction."""
    # For simplicity, use a small constant value
    return 0.0001

# Main simulation loop
print("Starting simulation...")
for j in range(nt - 1):
    if j % 1000 == 0:
        print(f"Time step {j}/{nt-1} ({j*dt/3600:.1f} hours)")
    
    for i in range(1, nx-1):  # Skip boundaries which are handled separately
        # Calculate terms for the current time step
        q_L = calculate_q_L(i, j)
        S_f = calculate_friction_slope(i, j)
        S_ec = calculate_energy_loss(i, j)
        M_L = calculate_M_L(i, j)
        
        # Update area using continuity equation (eq. 3)
        A[i, j+1] = ((q_L - (Q[i, j] - Q[i-1, j]) / dx) * dt + s_c * (A[i, j] + A0[i, j])) / s_c - A0[i, j+1]
        
        # Ensure non-negative area
        A[i, j+1] = max(0.01, A[i, j+1])
        
        # Calculate corresponding depth and width using numerical method
        def find_depth(area):
            """Find depth for given area using Newton-Raphson method."""
            depth = h_r[i, j]  # Initial guess - previous depth
            for _ in range(10):  # Max iterations
                current_area = base_width * depth + side_slope * depth**2
                derivative = base_width + 2 * side_slope * depth
                if abs(derivative) < 1e-6:
                    break
                depth = depth - (current_area - area) / derivative
                if depth < 0.01:
                    depth = 0.01
            return depth
        
        h_r[i, j+1] = find_depth(A[i, j+1])
        W[i, j+1] = base_width + 2 * side_slope * h_r[i, j+1]
        
        # Update discharge using momentum equation (eq. 5)
        # Calculate depth gradient term
        depth_gradient = (h_r[i, j] - h_r[i-1, j]) / dx
        
        # Calculate momentum flux term
        momentum_flux = ((beta * Q[i, j]**2 / A[i, j]) - (beta * Q[i-1, j]**2 / A[i-1, j])) / dx if A[i, j] > 0 and A[i-1, j] > 0 else 0
        
        # Apply momentum equation (eq. 5)
        Q[i, j+1] = ((-M_L - g * A[i, j] * (depth_gradient + S_f + S_ec - S0) - momentum_flux) * dt + s_m * Q[i, j]) / s_m
        
        # For stability, limit discharge changes
        max_change = 0.2 * abs(Q[i, j])
        if abs(Q[i, j+1] - Q[i, j]) > max_change:
            Q[i, j+1] = Q[i, j] + np.sign(Q[i, j+1] - Q[i, j]) * max_change

    # Apply downstream boundary condition (constant depth)
    h_r[-1, j+1] = downstream_depth
    A[-1, j+1], W[-1, j+1] = calculate_channel_properties(downstream_depth)
    
    # Calculate discharge at downstream boundary using continuity
    Q[-1, j+1] = Q[-2, j+1]

print("Simulation completed.")

# Convert time steps to hours and days for plotting
time_hours = np.arange(nt) * dt / 3600
time_days = time_hours / 24

# Create plots
plt.figure(figsize=(15, 10))

# Plot 1: Discharge vs time at different locations
# plt.subplot(2, 2, 1)
locations = [0]
labels = ['Upstream']
colors = ['b']

for i, loc in enumerate(locations):
    plt.plot(time_days, Q[loc, :], label=f'{labels[i]} (x = {loc*dx/1000:.1f} km)', color=colors[i])

plt.xlabel('Time (days)')
plt.ylabel('Discharge (m³/s)')
plt.title('Discharge vs Time at Different River Locations')
plt.grid(True)
plt.legend()
plt.savefig('river_simulation_results.png', dpi=300)

# # Plot 2: Water depth vs time at different locations
# plt.subplot(2, 2, 2)
# for i, loc in enumerate(locations):
#     plt.plot(time_days, h_r[loc, :], label=f'{labels[i]} (x = {loc*dx/1000:.1f} km)', color=colors[i])

# plt.xlabel('Time (days)')
# plt.ylabel('Water Depth (m)')
# plt.title('Water Depth vs Time at Different River Locations')
# plt.grid(True)
# plt.legend()

# Plot 3: Water depth along the river at different times
# plt.subplot(2, 2, 3)
# x_values = np.arange(nx) * dx / 1000  # km

# # Select times to plot
# time_indices = [0, nt//14, nt//7, nt//3, 2*nt//3, nt-1]
# time_labels = ['0 days', '0.5 days', '1 day', '2.33 days', '4.67 days', '7 days']
# line_styles = ['-', '--', '-.', ':', '-', '--']

# for i, t_idx in enumerate(time_indices):
#     plt.plot(x_values, h_r[:, t_idx], label=f'{time_labels[i]}', linestyle=line_styles[i])

# plt.xlabel('Distance along river (km)')
# plt.ylabel('Water Depth (m)')
# plt.title('Water Depth Profile at Different Times')
# plt.grid(True)
# plt.legend()

# # Plot 4: Discharge along the river at different times
# plt.subplot(2, 2, 4)
# for i, t_idx in enumerate(time_indices):
#     plt.plot(x_values, Q[:, t_idx], label=f'{time_labels[i]}', linestyle=line_styles[i])

# plt.xlabel('Distance along river (km)')
# plt.ylabel('Discharge (m³/s)')
# plt.title('Discharge Profile at Different Times')
# plt.grid(True)
# plt.legend()

# plt.tight_layout()
# plt.savefig('river_simulation_results.png', dpi=300)

# Create a visualization of the trapezoidal channel cross-section
# def plot_channel_cross_section():
#     fig, ax = plt.subplots(figsize=(8, 6))
    
#     # Set up the plot
#     ax.set_xlim(-10, 30)
#     ax.set_ylim(0, 5)
#     ax.set_xlabel('Width (m)')
#     ax.set_ylabel('Height (m)')
#     ax.set_title('Trapezoidal Channel Cross-Section')
#     ax.grid(True)
    
#     # Plot the channel cross-section
#     bottom_points = [(-side_slope*h_r[-1, 0], 0), (base_width + side_slope*h_r[-1, 0], 0)]
#     water_points = [(0, h_r[-1, 0]), (base_width, h_r[-1, 0])]
    
#     # Draw channel banks
#     ax.plot([-side_slope*5, 0, base_width, base_width+side_slope*5], [5, 0, 0, 5], 'k-', linewidth=2)
    
#     # Draw water level
#     ax.plot([-side_slope*h_r[-1, 0], 0, base_width, base_width+side_slope*h_r[-1, 0]], 
#             [h_r[-1, 0], 0, 0, h_r[-1, 0]], 'b-', linewidth=2)
    
#     # Fill water area
#     water_polygon = patches.Polygon([(-side_slope*h_r[-1, 0], h_r[-1, 0]), (0, 0), 
#                                       (base_width, 0), (base_width+side_slope*h_r[-1, 0], h_r[-1, 0])], 
#                                      color='skyblue', alpha=0.7)
#     ax.add_patch(water_polygon)
    
#     # Add labels
#     ax.text(base_width/2, -0.3, f'{base_width} m', ha='center')
#     ax.text(base_width+2, h_r[-1, 0]/2, f'{h_r[-1, 0]:.2f} m', va='center')
#     ax.text(base_width+side_slope*h_r[-1, 0]/2, h_r[-1, 0]/2, '2:1 slope', rotation=-np.arctan(1/side_slope)*180/np.pi, va='center')
    
#     plt.savefig('channel_cross_section.png', dpi=300)
#     plt.close()

# Create a visualization of the upstream hydrograph
# def plot_upstream_hydrograph():
#     plt.figure(figsize=(8, 6))
#     plt.plot(time_days[:total_hydrograph_duration_index+1000], Q[0, :total_hydrograph_duration_index+1000], 'r-', linewidth=2)
#     plt.xlabel('Time (days)')
#     plt.ylabel('Discharge (m³/s)')
#     plt.title('Upstream Boundary Condition: Triangular Hydrograph')
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig('upstream_hydrograph.png', dpi=300)
#     plt.close()

# # Create a longitudinal profile plot
# def plot_longitudinal_profile():
#     plt.figure(figsize=(12, 6))
    
#     # Plot the river bed profile
#     bed_elevation = np.linspace(L*S0, 0, nx)
#     plt.plot(x_values, bed_elevation, 'k-', label='River Bed')
    
#     # Plot the water surface at different times
#     for i, t_idx in enumerate(time_indices):
#         water_surface = bed_elevation + h_r[:, t_idx]
#         plt.plot(x_values, water_surface, label=f'Water Surface at {time_labels[i]}', linestyle=line_styles[i])
    
#     plt.xlabel('Distance along river (km)')
#     plt.ylabel('Elevation (m)')
#     plt.title('Longitudinal Profile of River Bed and Water Surface')
#     plt.grid(True)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig('longitudinal_profile.png', dpi=300)
#     plt.close()

# Execute the additional plots
# plot_channel_cross_section()
# plot_upstream_hydrograph()
# plot_longitudinal_profile()

print("Plotting completed. All figures saved.")
