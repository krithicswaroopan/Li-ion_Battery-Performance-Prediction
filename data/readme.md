# Battery Dataset

This directory contains the NASA battery dataset used for the Battery Performance Prediction project.

## Dataset Description

The dataset consists of lithium-ion battery cycling data collected by NASA Ames Research Center. The batteries were run through charge/discharge cycles until failure under different operational conditions.

## Download Instructions

1. Download the NASA Prognostics Center Battery Dataset from the following URL:
   https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/#battery

2. Specifically, download "Battery Data Set" which contains data from Li-ion batteries cycling from full charge to full discharge.

3. Extract the downloaded zip file and place the contents in this directory with the following structure:
   ```
   data/
   └── NASA_batteries/
       ├── B0005/
       ├── B0006/
       ├── B0007/
       └── B0018/
   ```

## Dataset Structure

Each battery directory contains:
- Discharge voltage, current, temperature, and capacity measurements
- Charge voltage, current, and temperature measurements
- Impedance measurements

## Data Format

Data is stored in MATLAB .mat files, which will be loaded using the utility functions in the `utils/data_loader.py` script.

## Citation

If using this data for research, please cite:
B. Saha and K. Goebel (2007). "Battery Data Set", NASA Ames Prognostics Data Repository, NASA Ames Research Center, Moffett Field, CA.