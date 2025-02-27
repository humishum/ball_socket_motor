import numpy as np
import magpylib as magpy
from time import time
import matplotlib.pyplot as plt
from magnet_designer import CoilCylinder, SimpleCoil


def create_hemisphere_magnetic_system(magnet_class, params, system_params):
    """
    Create a hemisphere system with the specified magnet class and parameters.
    
    Args:
        magnet_class: Class of magnet to use (SimpleCoil or CoilCylinder)
        params: Dictionary with parameters for the magnet class
        system_params: Dictionary with parameters for the hemisphere system
        
    Returns:
        collection: magpylib Collection containing the entire system
        sensor_positions: List of sensor positions
    """
    # Extract system parameters
    r_m = system_params['r_m']
    n_phi_rad = system_params['n_phi_rad']
    n_theta_rad = system_params['n_theta_rad']
    include_ferro_center = system_params.get('include_ferro_center', False)
    ferro_polarization = system_params.get('ferro_polarization', (.1, .2, .3))
    ferro_dimension = system_params.get('ferro_dimension', (.01, .01))
    
    # Generate coils on hemisphere
    coils = []
    sensor_positions = []
    phi_values = np.linspace(0, np.pi/2, n_phi_rad)  # 0 to π/2 for a hemisphere
    theta_values = np.linspace(0, 2*np.pi, n_theta_rad, endpoint=False)
    
    # Sensor Offsets
    range_offsets = [0, 0.005]
    angle_offsets = [0]
    angle_offsets.extend([a*-1 for a in angle_offsets])
    phi_offsets = [0]
    
    for phi in phi_values:  # elevation
        for theta in theta_values:  # azimuth
            for r_offset in range_offsets:  # range for sensor
                for theta_offset in angle_offsets:  # az for sensor
                    for phi_offset in phi_offsets:  # el for sensor
                        # Calculate sensor position in cartesian
                        x = (r_m + r_offset) * np.sin(phi+phi_offset) * np.cos(theta + theta_offset)
                        y = (r_m + r_offset) * np.sin(phi+phi_offset) * np.sin(theta + theta_offset)
                        z = (r_m + r_offset) * np.cos(phi+phi_offset)
                        pos = np.array([x, y, z])
                        sensor_positions.append(pos)
                        
                        # Add coil only for the 0 offset case
                        if r_offset == 0 and theta_offset == 0 and phi_offset == 0:
                            # Create magnet based on the provided class and parameters
                            if magnet_class == SimpleCoil:
                                magnet_instance = SimpleCoil(**params)
                            elif magnet_class == CoilCylinder:
                                magnet_instance = CoilCylinder(**params)
                            else:
                                raise ValueError(f"Unsupported magnet class: {magnet_class}")
                                
                            coil = magnet_instance.get_magnet()
                            
                            # Rotate coil from +z-axis to the local radial direction
                            radial_dir = pos / np.linalg.norm(pos)  # Unit Vector for radial direction
                            z_axis = np.array([0, 0, 1])
                            z_cross_radial = np.cross(z_axis, radial_dir)  # Orthogonal vector to z_axis and radial_dir
                            norm_cross = np.linalg.norm(z_cross_radial)  # Magnitude
                            
                            if norm_cross > 1e-9:
                                z_cross_radial /= norm_cross
                                angle = np.arccos(np.dot(z_axis, radial_dir))
                                coil.rotate_from_angax(angle=angle, axis=z_cross_radial, degrees=False)
                            
                            # Add ferro center if enabled
                            if include_ferro_center:
                                ferro = magpy.magnet.Cylinder(position=pos, polarization=ferro_polarization, dimension=ferro_dimension)
                                if norm_cross > 1e-9:
                                    ferro.rotate_from_angax(angle=angle, axis=z_cross_radial, degrees=False)
                                coils.append(ferro)
                                
                            # Move coil out to the hemisphere surface
                            coil.move(pos)
                            coils.append(coil)
    
    # Combine all coils into a single Collection
    collection = magpy.Collection(coils)
    sensors = [magpy.Sensor(i) for i in sensor_positions]
    collection.add(sensors)
    
    return collection, sensor_positions


def compute_energy_and_force(collection, grid_length_m):
    """
    Compute magnetic energy and force fields for top and side views.
    
    Args:
        collection: magpylib Collection containing the entire system
        grid_length_m: Length of the grid for visualization
        
    Returns:
        Dictionary containing grids, energies, and forces for both views
    """
    # Define grid for the top-down (x-y) view
    nx_top, ny_top = 60, 60
    xs_top = np.linspace(-grid_length_m, grid_length_m, nx_top)
    ys_top = np.linspace(-grid_length_m, grid_length_m, ny_top)
    X_top, Y_top = np.meshgrid(xs_top, ys_top)
    # Create a grid of points in the z=0 plane
    grid_top = np.stack((X_top, Y_top, np.zeros_like(X_top)), axis=2)
    
    # Compute the B-field on the top view grid and scale it
    t0 = time()
    B_top = magpy.getB(collection, grid_top) * 1E-3
    print(f"Time to compute B_top: {time()-t0:.3f}")
    
    # Calculate the magnetic energy density: Energy = 0.5 * |B|^2
    Energy_top = 0.5 * np.sum(np.square(B_top), axis=2)
    
    # Compute the force field (i.e. the gradient of the energy)
    force_top = np.gradient(Energy_top, ys_top, xs_top)
    
    # Define grid for the side view: here we take an x-z slice at y=0
    nx_side, nz_side = 60, 60
    xs_side = np.linspace(-grid_length_m, grid_length_m, nx_side)
    zs_side = np.linspace(-grid_length_m, grid_length_m, nz_side)
    X_side, Z_side = np.meshgrid(xs_side, zs_side)
    # Create a grid of points in the y=0 plane (side view)
    grid_side = np.stack((X_side, np.zeros_like(X_side), Z_side), axis=2)
    
    t0 = time()
    B_side = magpy.getB(collection, grid_side) * 1E-3
    print(f"Time to compute B_side: {time()-t0:.3f}")
    
    Energy_side = 0.5 * np.sum(np.square(B_side), axis=2)
    # For the side view, the first axis corresponds to z and the second to x
    force_side = np.gradient(Energy_side, zs_side, xs_side)
    
    return {
        'X_top': X_top, 'Y_top': Y_top, 'Energy_top': Energy_top, 'force_top': force_top,
        'X_side': X_side, 'Z_side': Z_side, 'Energy_side': Energy_side, 'force_side': force_side
    }


def calculate_metrics(energy_data):
    """
    Calculate metrics to evaluate magnet performance.
    
    Args:
        energy_data: Dictionary with energy and force data
        
    Returns:
        Dictionary of performance metrics
    """
    # Calculate average energy gradient (force) magnitude
    top_force_magnitude = np.sqrt(energy_data['force_top'][0]**2 + energy_data['force_top'][1]**2)
    side_force_magnitude = np.sqrt(energy_data['force_side'][0]**2 + energy_data['force_side'][1]**2)
    
    # Calculate energy peak
    energy_peak_top = np.max(energy_data['Energy_top'])
    energy_peak_side = np.max(energy_data['Energy_side'])
    
    # Calculate energy contrast (max/min ratio)
    energy_contrast_top = np.max(energy_data['Energy_top']) / (np.min(energy_data['Energy_top']) + 1e-10)
    energy_contrast_side = np.max(energy_data['Energy_side']) / (np.min(energy_data['Energy_side']) + 1e-10)
    
    # Calculate average gradient direction uniformity
    # (How well aligned are the force vectors with the center?)
    center_x_idx_top = len(energy_data['X_top']) // 2
    center_y_idx_top = len(energy_data['Y_top']) // 2
    
    return {
        'avg_force_top': np.mean(top_force_magnitude),
        'avg_force_side': np.mean(side_force_magnitude),
        'energy_peak_top': energy_peak_top,
        'energy_peak_side': energy_peak_side,
        'energy_contrast_top': energy_contrast_top,
        'energy_contrast_side': energy_contrast_side,
        'force_strength': (np.mean(top_force_magnitude) + np.mean(side_force_magnitude)) / 2,
        'energy_peak': (energy_peak_top + energy_peak_side) / 2,
        'energy_contrast': (energy_contrast_top + energy_contrast_side) / 2
    }


def plot_energy_field(energy_data, title):
    """
    Plot energy and force fields.
    
    Args:
        energy_data: Dictionary with energy and force data
        title: Title for the plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Top-down contour plot (x-y view)
    contour1 = axes[0].contourf(energy_data['X_top'], energy_data['Y_top'], 
                               energy_data['Energy_top'], levels=25, cmap='viridis')
    # Overlay quiver: note that force_top[1] is dE/dx and force_top[0] is dE/dy
    axes[0].quiver(energy_data['X_top'], energy_data['Y_top'], 
                  energy_data['force_top'][1], energy_data['force_top'][0], 
                  color='white', scale=50)
    axes[0].set_title(f"{title} - Top Down (x-y)")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    fig.colorbar(contour1, ax=axes[0], label="Energy")
    
    # Side view contour plot (x-z view)
    contour2 = axes[1].contourf(energy_data['X_side'], energy_data['Z_side'], 
                               energy_data['Energy_side'], levels=25, cmap='viridis')
    # Here force_side[1] is dE/dx and force_side[0] is dE/dz
    axes[1].quiver(energy_data['X_side'], energy_data['Z_side'], 
                  energy_data['force_side'][1], energy_data['force_side'][0], 
                  color='white', scale=50)
    axes[1].set_title(f"{title} - Side View (x-z)")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("z")
    fig.colorbar(contour2, ax=axes[1], label="Energy")
    
    plt.tight_layout()
    return fig


def sweep_magnet_designs():
    """
    Sweep through different magnet designs and parameters, evaluating performance.
    """
    # Base system parameters
    system_params = {
        'r_m': 0.1,       # hemisphere radius
        'n_phi_rad': 4,   # steps in elevation
        'n_theta_rad': 8, # steps in azimuth
        'include_ferro_center': False,
        'ferro_polarization': (.1, .2, .3),
        'ferro_dimension': (.01, .01)
    }
    
    # Define parameter ranges for sweep
    magnet_classes = [SimpleCoil, CoilCylinder]
    coil_diameters = [0.03, 0.05, 0.07]
    current_values = [0.3, 0.5, 0.7]
    turn_values = [150, 250, 350]
    
    # For CoilCylinder specific parameters
    coil_heights = [0.01, 0.02]
    magnetization_values = [(0, 0, 1), (0, 0, 1.5)]
    
    results = []
    
    # Iterate through all parameter combinations
    for magnet_class in magnet_classes:
        for coil_diameter in coil_diameters:
            for current in current_values:
                for n_turns in turn_values:
                    
                    # Set up parameters based on magnet class
                    if magnet_class == SimpleCoil:
                        params = {
                            'n_turns': n_turns,
                            'current_a_base': current,
                            'diameter_m': coil_diameter
                        }
                        config_name = f"SimpleCoil_d{coil_diameter}_c{current}_t{n_turns}"
                    
                    elif magnet_class == CoilCylinder:
                        # For CoilCylinder, we'll also sweep through heights and magnetization
                        for height in coil_heights:
                            for magnetization in magnetization_values:
                                params = {
                                    'n_turns': n_turns,
                                    'current_a': current * n_turns,  # Effective current
                                    'coil_diameter': coil_diameter,
                                    'coil_height': height,
                                    'magnetization': magnetization
                                }
                                mag_str = f"m{magnetization[2]}"
                                config_name = f"CoilCyl_d{coil_diameter}_c{current}_t{n_turns}_h{height}_{mag_str}"
                                
                                # Create system and compute metrics
                                print(f"Testing configuration: {config_name}")
                                
                                # Create the hemisphere system with current parameters
                                collection, sensor_positions = create_hemisphere_magnetic_system(
                                    magnet_class, params, system_params
                                )
                                
                                # Compute energy and force fields
                                grid_length_m = system_params['r_m'] * 1.25
                                energy_data = compute_energy_and_force(collection, grid_length_m)
                                
                                # Calculate performance metrics
                                metrics = calculate_metrics(energy_data)
                                
                                # Generate plot
                                fig = plot_energy_field(energy_data, config_name)
                                plt.savefig(f"magnet_sweep_{config_name}.png")
                                plt.close(fig)
                                
                                # Store results
                                result = {
                                    'config_name': config_name,
                                    'magnet_class': magnet_class.__name__,
                                    'params': params,
                                    'metrics': metrics
                                }
                                results.append(result)
                        
                        # Skip the CoilCylinder loop for SimpleCoil class
                        if magnet_class == SimpleCoil:
                            # Create system and compute metrics
                            print(f"Testing configuration: {config_name}")
                            
                            # Create the hemisphere system with current parameters
                            collection, sensor_positions = create_hemisphere_magnetic_system(
                                magnet_class, params, system_params
                            )
                            
                            # Compute energy and force fields
                            grid_length_m = system_params['r_m'] * 1.25
                            energy_data = compute_energy_and_force(collection, grid_length_m)
                            
                            # Calculate performance metrics
                            metrics = calculate_metrics(energy_data)
                            
                            # Generate plot
                            fig = plot_energy_field(energy_data, config_name)
                            plt.savefig(f"magnet_sweep_{config_name}.png")
                            plt.close(fig)
                            
                            # Store results
                            result = {
                                'config_name': config_name,
                                'magnet_class': magnet_class.__name__,
                                'params': params,
                                'metrics': metrics
                            }
                            results.append(result)
    
    # Sort results by a composite score and display the best configurations
    for result in results:
        metrics = result['metrics']
        # Create a composite score prioritizing force strength and energy contrast
        result['score'] = metrics['force_strength'] * 0.5 + metrics['energy_contrast'] * 0.5
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print top results
    print("\n===== Top Performing Configurations =====")
    for i, result in enumerate(results[:10]):
        print(f"{i+1}. {result['config_name']} - Score: {result['score']:.4f}")
        print(f"   Force Strength: {result['metrics']['force_strength']:.4f}")
        print(f"   Energy Contrast: {result['metrics']['energy_contrast']:.4f}")
        print(f"   Energy Peak: {result['metrics']['energy_peak']:.4f}")
        print()
    
    # Create comparison plot of top configurations
    plt.figure(figsize=(12, 8))
    top_configs = [result['config_name'] for result in results[:10]]
    scores = [result['score'] for result in results[:10]]
    force_strengths = [result['metrics']['force_strength'] for result in results[:10]]
    energy_contrasts = [result['metrics']['energy_contrast'] for result in results[:10]]
    
    plt.barh(top_configs, scores, alpha=0.7, label='Overall Score')
    plt.barh(top_configs, force_strengths, alpha=0.5, label='Force Strength')
    plt.barh(top_configs, energy_contrasts, alpha=0.3, label='Energy Contrast')
    
    plt.xlabel('Score / Metric Value')
    plt.ylabel('Configuration')
    plt.title('Top Performing Magnet Configurations')
    plt.legend()
    plt.tight_layout()
    plt.savefig("magnet_sweep_comparison.png")
    plt.show()
    
    return results


if __name__ == "__main__":
    results = sweep_magnet_designs()
    
    # Optionally save results to a file
    import json
    with open('magnet_sweep_results.json', 'w') as f:
        # Convert to serializable format
        serializable_results = []
        for result in results:
            serializable_result = {
                'config_name': result['config_name'],
                'magnet_class': result['magnet_class'],
                'params': {k: (v if not isinstance(v, tuple) else list(v)) 
                          for k, v in result['params'].items()},
                'metrics': result['metrics'],
                'score': result['score']
            }
            serializable_results.append(serializable_result)
        
        json.dump(serializable_results, f, indent=4)