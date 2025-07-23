# Nearlink RSSI and Ground Truth Dataset for Indoor Positioning

This repository contains a sample of a time-series dataset designed for research in indoor localization, presence detection, and device tracking. The dataset consists of two main components:
1.  **Nearlink RSSI Data**: Received Signal Strength Indicator (RSSI) values from multiple wireless devices, collected by a stationary sensor,stored in data/Nearlink, divided into two folders: fingerprint and validation.
2.  **Ground Truth Data**: Corresponding 3D coordinate data representing the true position of the sensor at given times,stored in data/True_value

We also provide a Python script to parse, synchronize, and process these raw data files into a clean, machine-learning-ready format.

## Repository Contents

This repository includes:
*   `2025_04_17_*_deal.txt`:  Files containing raw Nearlink RSSI measurements.
*   `2025-04-17-*_deal.txt`:  Files containing ground truth position data.
*   `data_preprocessing.py`: A Python script to process and align the RSSI and ground truth data.

## Data Format

### 1. Nearlink RSSI Data

The RSSI data is logged in text files. Each file contains multiple measurement blocks, where each block is preceded by a human-readable timestamp.

*   **Block Header**: `Timestamp: YYYY-MM-DD HH:MM:SS.ffffff`
*   **Data Line**: `MAC: [MAC_Address], Average RSSI: [Value] dBm`

**Note**: RSSI is a measurement of signal power. A higher value (closer to 0, e.g., -50 dBm) indicates a stronger signal.

### 2. Ground Truth Data

The ground truth data provides the real-world coordinates corresponding to the collected RSSI data.

*   **Format**: Each line is space-separated.
*   **Columns**: `[Unix_Timestamp] [X_coordinate] [Y_coordinate] [Z_coordinate]`

The timestamp is a high-precision Unix timestamp (seconds since the epoch). The coordinates represent the position in a 3D space.

## Data Samples

### RSSI Data Sample (`*_deal.txt`)
```text
Timestamp: 2025-04-17 15:07:17.172248
MAC: 33:22:33:44:55:66, Average RSSI: -67.32 dBm
MAC: 88:22:33:44:55:66, Average RSSI: -68.37 dBm
MAC: aa:22:33:44:55:66, Average RSSI: -86.21 dBm
...

Timestamp: 2025-04-17 15:07:17.672667
MAC: 77:22:33:44:55:66, Average RSSI: -78.48 dBm
MAC: 88:22:33:44:55:66, Average RSSI: -67.86 dBm
...
Ground Truth Data Sample (*_deal.txt)
1744873639.907392025 -3.8744663811606147293e-05 -1.8033074025547371629e-05 -0.00028841727590487908949
1744873640.0073640347 0.058686411545691437308 1.6568109604734313489 0.57783354523031749128
1744873640.1073660851 0.05339662322949255413 1.6245769774070439873 0.30551083759380143201
1744873640.207449913 0.050636965830479656325 1.6165466005117756776 0.39427341854927988596
...
Data Processing Script
We have included data_preprocessing.py to help you get started. This script performs the following key steps:
Parses all raw RSSI and ground truth text files from specified directories.
Identifies a consistent set of MAC addresses that appear frequently, which will serve as the features.
Synchronizes the RSSI measurements with the ground truth coordinates by matching the closest timestamps within a defined tolerance.
Handles missing data: If a MAC address is not detected at a specific timestamp, it is assigned a default low RSSI value (-80 dBm).
Outputs the final, aligned data into two CSV files: processed_training_data_original.csv and processed_validation_data_original.csv, which are ready for use in machine learning models.

How to Use the Script
Place your RSSI data files and ground truth files in their respective directories.
Update the directory paths at the top of the data_preprocessing.py script.
Run the script from your terminal:
python data_preprocessing.py
Use code with caution.

Dataset Availability
The data files provided in this repository are only samples of the full dataset. They are intended to provide a clear example of the data structure and content for evaluation purposes.
Getting the Full Dataset
To obtain access to the complete dataset for your research, please contact us via email.
Contact Email: 2023302121062@whu.edu.cn
When you email us, please briefly introduce yourself, your institution, and the intended purpose of your research. We will be happy to assist you.
License
Please consider this data to be available for academic and research purposes. If you plan to use it for commercial purposes, please contact us first.
Citation
If you use this dataset in your work, we would appreciate a citation to this repository.
