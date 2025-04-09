# NASA Battery Data Loader - Fixed version
import os
import numpy as np
import pandas as pd
from scipy.io import loadmat

def load_nasa_battery_data(data_dir, verbose=True):
    """
    Load NASA battery dataset according to the described structure
    
    Parameters:
    -----------
    data_dir : str
        Path to directory containing battery data files
    verbose : bool
        Whether to print detailed loading information
        
    Returns:
    --------
    dict
        Dictionary containing battery data with structure:
        {
            'B0005': {
                'summary': DataFrame with cycle summary data,
                'cycles': {
                    1: {
                        'charge': DataFrame with charge data,
                        'discharge': DataFrame with discharge data
                    },
                    ...
                }
            },
            ...
        }
    """
    batteries = {}
    
    # Make sure the directory exists
    if not os.path.exists(data_dir):
        if verbose:
            print(f"Error: Data directory '{data_dir}' does not exist.")
        return batteries
    
    # Find battery mat files
    try:
        all_files = os.listdir(data_dir)
        if verbose:
            print(f"Found {len(all_files)} total files in directory")
            
        battery_files = [f for f in all_files if f.endswith('.mat') and f.startswith('B')]
        
        if verbose:
            print(f"Found {len(battery_files)} battery files: {battery_files}")
        
        if len(battery_files) == 0:
            if verbose:
                print(f"No battery files found in '{data_dir}'. Make sure the path is correct and files are named like 'B0005.mat'.")
            return batteries
            
    except Exception as e:
        if verbose:
            print(f"Error listing directory: {str(e)}")
        return batteries
    
    for battery_file in battery_files:
        try:
            battery_id = battery_file.split('.')[0]
            mat_file = os.path.join(data_dir, battery_file)
            
            if verbose:
                print(f"Processing file {mat_file}...")
            
            # Load mat file
            mat_data = loadmat(mat_file, simplify_cells=True)  # Use simplify_cells for easier navigation
            
            # Check if battery_id is in keys
            if battery_id not in mat_data:
                possible_keys = [k for k in mat_data.keys() if not k.startswith('__')]
                if possible_keys:
                    if verbose:
                        print(f"  Battery ID '{battery_id}' not found. Using '{possible_keys[0]}' instead.")
                    battery_id = possible_keys[0]
                else:
                    if verbose:
                        print(f"  No valid data found in {battery_file}. Skipping.")
                    continue
            
            # Initialize battery data structures
            summary_data = []
            cycles_data = {}
            
            try:
                # Extract battery data with simplified cell structure
                battery_data = mat_data[battery_id]
                
                # Check if the expected cycle structure exists
                if 'cycle' not in battery_data:
                    if verbose:
                        print(f"  Error: 'cycle' not found in battery data. Keys: {battery_data.keys()}")
                    continue
                
                # Get all cycles
                cycles = battery_data['cycle']
                
                # Process each cycle
                for cycle_idx, cycle in enumerate(cycles):
                    cycle_num = cycle_idx + 1
                    
                    # Extract cycle type as string
                    if 'type' in cycle:
                        cycle_type = cycle['type']
                        # Convert bytes or arrays to string if needed
                        if isinstance(cycle_type, (bytes, np.ndarray)):
                            if isinstance(cycle_type, bytes):
                                cycle_type = cycle_type.decode('utf-8')
                            elif isinstance(cycle_type, np.ndarray):
                                if cycle_type.dtype.kind in ['S', 'U']:  # String or Unicode
                                    cycle_type = ''.join(c.decode('utf-8') if isinstance(c, bytes) else c for c in cycle_type)
                                else:  # Numeric array representing ASCII
                                    cycle_type = ''.join(chr(x) for x in cycle_type)
                    else:
                        cycle_type = 'unknown'
                    
                    # Get temperature
                    ambient_temp = cycle.get('ambient_temperature', np.nan)
                    
                    if cycle_type in ['charge', 'discharge']:
                        # Access data for specific cycle
                        if 'data' not in cycle:
                            if verbose:
                                print(f"  Cycle {cycle_num}: No data found for {cycle_type}")
                            continue
                        
                        cycle_data = cycle['data']
                        
                        # Calculate capacity for discharge cycles
                        capacity = np.nan
                        if cycle_type == 'discharge' and 'Capacity' in cycle_data:
                            capacity = cycle_data['Capacity']
                        
                        # Add to summary
                        summary_data.append({
                            'Cycle': cycle_num,
                            'Capacity (Ah)': capacity,
                            'Ambient Temperature (C)': ambient_temp,
                            'Type': cycle_type
                        })
                        
                        # Process measurements
                        if 'Voltage_measured' in cycle_data and 'Current_measured' in cycle_data and 'Time' in cycle_data:
                            # Extract arrays
                            voltage = cycle_data['Voltage_measured']
                            current = cycle_data['Current_measured']
                            time = cycle_data['Time']
                            
                            # Ensure arrays are flat (handle potential nested structures)
                            voltage = np.array(voltage).flatten() if isinstance(voltage, (list, np.ndarray)) else np.array([voltage])
                            current = np.array(current).flatten() if isinstance(current, (list, np.ndarray)) else np.array([current])
                            time = np.array(time).flatten() if isinstance(time, (list, np.ndarray)) else np.array([time])
                            
                            # Create DataFrame with measurements
                            measurements = {
                                'Time (s)': time,
                                'Voltage (V)': voltage,
                                'Current (A)': current
                            }
                            
                            # Add temperature if available
                            if 'Temperature_measured' in cycle_data:
                                temp = cycle_data['Temperature_measured']
                                temp = np.array(temp).flatten() if isinstance(temp, (list, np.ndarray)) else np.array([temp])
                                measurements['Temperature (C)'] = temp
                            
                            # Create cycle entry if it doesn't exist
                            if cycle_num not in cycles_data:
                                cycles_data[cycle_num] = {}
                            
                            # Store measurements
                            cycles_data[cycle_num][cycle_type] = pd.DataFrame(measurements)
                            
                            if verbose and (cycle_num <= 3 or cycle_num % 20 == 0):  # Log only some cycles
                                print(f"  Processed {cycle_type} data for cycle {cycle_num}")
                    
                    elif cycle_type == 'impedance':
                        # We can also process impedance data if needed
                        # This is not required for the current project
                        pass
                    
                    else:
                        if verbose and cycle_num <= 3:  # Only log for first few cycles
                            print(f"  Skipping cycle {cycle_num} with type '{cycle_type}'")
                
                # Create summary DataFrame
                summary_df = pd.DataFrame(summary_data)
                
                if len(summary_df) > 0:
                    # Filter to include only discharge cycles for capacity analysis
                    discharge_summary = summary_df[summary_df['Type'] == 'discharge'].copy()
                    
                    # Clean capacity data (remove zeros and NaNs)
                    discharge_summary = discharge_summary[discharge_summary['Capacity (Ah)'] > 0]
                    
                    if len(discharge_summary) > 0:
                        # Calculate SOH based on initial capacity
                        initial_capacity = discharge_summary['Capacity (Ah)'].iloc[0]
                        discharge_summary['SOH'] = discharge_summary['Capacity (Ah)'] / initial_capacity
                        
                        # Merge SOH back to main summary
                        summary_df = pd.merge(
                            summary_df, 
                            discharge_summary[['Cycle', 'SOH']], 
                            on='Cycle', 
                            how='left'
                        )
                    
                    # Store battery data
                    batteries[battery_id] = {
                        'summary': summary_df,
                        'cycles': cycles_data
                    }
                    
                    if verbose:
                        print(f"Successfully loaded battery {battery_id} with {len(summary_df)} cycles")
                        print(f"  - {len(discharge_summary)} discharge cycles")
                        print(f"  - {len(cycles_data)} detailed cycle measurements")
                else:
                    if verbose:
                        print(f"  No valid cycles found for battery {battery_id}")
                
            except Exception as e:
                if verbose:
                    print(f"  Error processing cycles for {battery_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            if verbose:
                print(f"Error loading battery {battery_file}: {str(e)}")
    
    return batteries
