import numpy as np
from collections import defaultdict
import datetime
import os
import csv  # For saving CSV files

# Directory paths
data_directory = r"D:\data\Nearlink"
truth_directory = r"D:\data\True_value"
output_processed_data_directory = r"D:\data\Processed_Data"

# Parse fingerprint database file
def parse_fingerprint_file(file_path):
    fingerprint_db = {}
    all_macs_in_file = defaultdict(int)
    with open(file_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if "Timestamp" in lines[i]:
                timestamp = lines[i].strip().split(": ")[1]
                rssi_data = {}
                i += 1
                while i < len(lines) and "MAC" in lines[i]:
                    line = lines[i].strip()
                    try:
                        mac_part, rssi_part = line.split(", ")
                        mac = mac_part.split(": ")[1]
                        rssi_str = rssi_part.split(": ")[1].strip()
                        rssi = float(rssi_str.replace("dBm", "").strip())
                        rssi_data[mac] = rssi
                        all_macs_in_file[mac] += 1
                    except Exception as e:
                        print(f"Error parsing line {line}: {e}, skipping this line")
                    i += 1
                fingerprint_db[timestamp] = rssi_data
            else:
                i += 1
    # Select MACs that appear frequently enough in this specific file
    selected_macs_for_file = {mac: count for mac, count in all_macs_in_file.items() if count > 5}
    return fingerprint_db, selected_macs_for_file

# Parse validation file
def parse_validation_file(file_path, all_macs_list):
    validation_data = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if "Timestamp" in lines[i]:
                timestamp = lines[i].strip().split(": ")[1]
                rssi_data = {mac: -80 for mac in all_macs_list}  # Initialize with default for all known MACs
                i += 1
                while i < len(lines) and "MAC" in lines[i]:
                    line = lines[i].strip()
                    try:
                        mac_part, rssi_part = line.split(", ")
                        mac = mac_part.split(": ")[1]
                        rssi_str = rssi_part.split(": ")[1].strip()
                        rssi = float(rssi_str.replace("dBm", "").strip())
                        if mac in rssi_data:  # Only store MACs present in the global all_macs_list
                            rssi_data[mac] = rssi
                    except Exception as e:
                        print(f"Error parsing line {line}: {e}, skipping this line")
                    i += 1
                validation_data[timestamp] = rssi_data
            else:
                i += 1
    return validation_data

# Parse ground truth file
def parse_ground_truth_file(file_path):
    ground_truth = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                timestamp = float(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                ground_truth[timestamp] = (x, y)
    return ground_truth

# Find the closest timestamp
def find_closest_timestamp(target_timestamp, ground_truth, max_diff=0.5):
    valid_timestamps = [t for t in ground_truth if abs(t - target_timestamp) < max_diff]
    if not valid_timestamps:
        return None
    return min(valid_timestamps, key=lambda t: abs(t - target_timestamp))

# Load all files in a directory
def load_files(directory, suffix):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(suffix):
            files.append(os.path.join(directory, filename))
    return files

# Save processed data to a CSV file
def save_processed_to_csv(filepath, timestamps_str_list, positions_np, fingerprints_np, mac_order_list):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['timestamp_str', 'pos_x', 'pos_y'] + mac_order_list
        writer.writerow(header)
        for i in range(len(fingerprints_np)):
            row = [
                timestamps_str_list[i],
                positions_np[i, 0],
                positions_np[i, 1]
            ] + fingerprints_np[i].tolist()
            writer.writerow(row)
    print(f"Processed data saved to: {filepath}")

# Main process
def main():
    os.makedirs(output_processed_data_directory, exist_ok=True)

    # Load file paths
    fingerprint_dir = os.path.join(data_directory, 'fingerprint')
    validation_dir = os.path.join(data_directory, 'validation')
    fingerprint_files = load_files(fingerprint_dir, '_1_deal.txt')
    validation_files = load_files(validation_dir, '_1_deal.txt')
    truth_files = load_files(truth_directory, '_deal.txt')

    # 1. Merge all fingerprint database files and determine the global MAC list
    raw_fingerprint_db = {}
    global_mac_counts = defaultdict(int)
    for file_path in fingerprint_files:
        db_part, macs_in_file = parse_fingerprint_file(file_path)
        raw_fingerprint_db.update(db_part)
        for mac, count in macs_in_file.items():
            global_mac_counts[mac] += count

    final_mac_list = sorted(list(global_mac_counts.keys()))
    if not final_mac_list:
        print("Warning: No eligible MAC addresses found, cannot continue processing. Please check the fingerprint files and MAC filtering conditions.")
        return
    print(f"Number of MAC addresses used (feature dimension): {len(final_mac_list)}")

    # 2. Merge all ground truth files
    ground_truth = {}
    for file_path in truth_files:
        gt_part = parse_ground_truth_file(file_path)
        ground_truth.update(gt_part)
    if not ground_truth:
        print("Warning: No ground truth data loaded.")

    # 3. Process training data (from the fingerprint database)
    training_fingerprints_list = []
    training_positions_list = []
    training_timestamps_str_list = []

    for ts_str, rssi_data_map in raw_fingerprint_db.items():
        dt = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S.%f')
        unix_ts = dt.timestamp()
        closest_gt_ts = find_closest_timestamp(unix_ts, ground_truth)

        if closest_gt_ts is not None:
            true_pos = ground_truth[closest_gt_ts]
            current_rssi_values = []
            for mac in final_mac_list:
                current_rssi_values.append(rssi_data_map.get(mac, -80))

            training_fingerprints_list.append(current_rssi_values)
            training_positions_list.append(true_pos)
            training_timestamps_str_list.append(ts_str)

    training_fingerprints_np = np.array(training_fingerprints_list)
    training_positions_np = np.array(training_positions_list)

    print(f"Number of original fingerprint database samples (after processing): {len(training_fingerprints_np)}")

    if len(training_fingerprints_np) > 0:
        # Save the original processed training data
        path_orig_train = os.path.join(output_processed_data_directory, "processed_training_data_original.csv")
        save_processed_to_csv(path_orig_train, training_timestamps_str_list, training_positions_np, training_fingerprints_np, final_mac_list)
    else:
        print("No training data to process.")

    # 4. Merge all validation set files
    raw_validation_data = {}
    for file_path in validation_files:
        data_part = parse_validation_file(file_path, final_mac_list)
        raw_validation_data.update(data_part)

    # 5. Process validation data (validation data is usually not noisy or augmented)
    validation_fingerprints_list = []
    validation_positions_list = []
    validation_timestamps_str_list = []

    for ts_str, rssi_data_map in raw_validation_data.items():
        dt = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S.%f')
        unix_ts = dt.timestamp()
        closest_gt_ts = find_closest_timestamp(unix_ts, ground_truth)

        if closest_gt_ts is not None:
            true_pos = ground_truth[closest_gt_ts]
            current_rssi_values = []
            for mac in final_mac_list:
                current_rssi_values.append(rssi_data_map.get(mac, -80))

            validation_fingerprints_list.append(current_rssi_values)
            validation_positions_list.append(true_pos)
            validation_timestamps_str_list.append(ts_str)

    validation_fingerprints_np = np.array(validation_fingerprints_list)
    validation_positions_np = np.array(validation_positions_list)

    if len(validation_timestamps_str_list) > 0:
        try:
            datetime_objects = [datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f') for ts in validation_timestamps_str_list]
            sorted_indices = np.argsort(datetime_objects)

            validation_fingerprints_np = validation_fingerprints_np[sorted_indices]
            validation_positions_np = validation_positions_np[sorted_indices]
            validation_timestamps_str_list = [validation_timestamps_str_list[i] for i in sorted_indices]
        except ValueError as e:
            print(f"Error sorting validation set timestamps: {e}. Using the original order.")

    print(f"Number of original validation set samples (after processing): {len(validation_fingerprints_np)}")

    if len(validation_fingerprints_np) > 0:
        path_orig_val = os.path.join(output_processed_data_directory, "processed_validation_data_original.csv")
        save_processed_to_csv(path_orig_val, validation_timestamps_str_list, validation_positions_np, validation_fingerprints_np, final_mac_list)
    else:
        print("No validation data to process.")

    print("\nData preprocessing completed.")

if __name__ == "__main__":
    main()