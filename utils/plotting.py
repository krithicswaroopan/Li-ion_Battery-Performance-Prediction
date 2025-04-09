"""
Utility functions for plotting battery data and model results.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.signal import savgol_filter

def plot_capacity_degradation(batteries, fig_size=(12, 6), savefig=None):
    """
    Plot capacity degradation for multiple batteries
    
    Parameters:
    -----------
    batteries : dict
        Dictionary containing battery data
    fig_size : tuple
        Figure size (width, height)
    savefig : str, optional
        If specified, save figure to this path
    """
    plt.figure(figsize=fig_size)
    
    for battery_id, battery_data in batteries.items():
        summary = battery_data['summary']
        
        # Plot capacity vs cycle
        plt.plot(summary['Cycle'], summary['Capacity (Ah)'], 'o-', label=battery_id, alpha=0.7)
    
    plt.xlabel('Cycle Number')
    plt.ylabel('Capacity (Ah)')
    plt.title('Battery Capacity Degradation')
    plt.grid(True)
    plt.legend()
    
    if savefig:
        plt.savefig(savefig, dpi=300, bbox_inches='tight')
    
    plt.show()

def plot_voltage_current_profiles(battery_data, cycle_num, fig_size=(12, 10), savefig=None):
    """
    Plot voltage and current profiles for a specific battery cycle
    
    Parameters:
    -----------
    battery_data : dict
        Dictionary containing data for a single battery
    cycle_num : int
        Cycle number to plot
    fig_size : tuple
        Figure size (width, height)
    savefig : str, optional
        If specified, save figure to this path
    """
    if cycle_num not in battery_data['cycles']:
        print(f"Cycle {cycle_num} not found in data")
        return
    
    cycle_data = battery_data['cycles'][cycle_num]
    
    fig, axs = plt.subplots(2, 2, figsize=fig_size)
    
    # Charge voltage and current
    if 'charge' in cycle_data:
        charge = cycle_data['charge']
        
        # Voltage
        axs[0, 0].plot(charge['Time (s)'], charge['Voltage (V)'])
        axs[0, 0].set_xlabel('Time (s)')
        axs[0, 0].set_ylabel('Voltage (V)')
        axs[0, 0].set_title('Charge Voltage Profile')
        axs[0, 0].grid(True)
        
        # Current
        axs[0, 1].plot(charge['Time (s)'], charge['Current (A)'])
        axs[0, 1].set_xlabel('Time (s)')
        axs[0, 1].set_ylabel('Current (A)')
        axs[0, 1].set_title('Charge Current Profile')
        axs[0, 1].grid(True)
    
    # Discharge voltage and current
    if 'discharge' in cycle_data:
        discharge = cycle_data['discharge']
        
        # Voltage
        axs[1, 0].plot(discharge['Time (s)'], discharge['Voltage (V)'])
        axs[1, 0].set_xlabel('Time (s)')
        axs[1, 0].set_ylabel('Voltage (V)')
        axs[1, 0].set_title('Discharge Voltage Profile')
        axs[1, 0].grid(True)
        
        # Current
        axs[1, 1].plot(discharge['Time (s)'], discharge['Current (A)'])
        axs[1, 1].set_xlabel('Time (s)')
        axs[1, 1].set_ylabel('Current (A)')
        axs[1, 1].set_title('Discharge Current Profile')
        axs[1, 1].grid(True)
    
    plt.tight_layout()
    
    if savefig:
        plt.savefig(savefig, dpi=300, bbox_inches='tight')
    
    plt.show()

def plot_model_predictions(y_true, y_pred, model_name, fig_size=(10, 6), savefig=None):
    """
    Plot actual vs predicted values for model evaluation
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
    model_name : str
        Name of the model for the plot title
    fig_size : tuple
        Figure size (width, height)
    savefig : str, optional
        If specified, save figure to this path
    """
    plt.figure(figsize=fig_size)
    
    # Sort by true values for better visualization
    sorted_indices = np.argsort(y_true)
    y_true_sorted = np.array(y_true)[sorted_indices]
    y_pred_sorted = np.array(y_pred)[sorted_indices]
    
    # Plot true vs predicted
    plt.scatter(y_true_sorted, y_pred_sorted, alpha=0.6)
    
    # Plot identity line
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--')
    
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title(f'{model_name} Predictions')
    plt.grid(True)
    
    if savefig:
        plt.savefig(savefig, dpi=300, bbox_inches='tight')
    
    plt.show()

def plot_feature_importance(model, feature_names, top_n=10, fig_size=(12, 6), savefig=None):
    """
    Plot feature importance for tree-based models
    
    Parameters:
    -----------
    model : model object
        Trained model with feature_importances_ attribute (e.g., XGBoost)
    feature_names : list
        List of feature names
    top_n : int
        Number of top features to plot
    fig_size : tuple
        Figure size (width, height)
    savefig : str, optional
        If specified, save figure to this path
    """
    # Get feature importance
    importances = model.feature_importances_
    
    # Sort by importance
    indices = np.argsort(importances)[-top_n:]
    
    plt.figure(figsize=fig_size)
    plt.barh(range(top_n), importances[indices])
    plt.yticks(range(top_n), [feature_names[i] for i in indices])
    plt.xlabel('Feature Importance')
    plt.title('Top Features')
    plt.tight_layout()
    
    if savefig:
        plt.savefig(savefig, dpi=300, bbox_inches='tight')
    
    plt.show()