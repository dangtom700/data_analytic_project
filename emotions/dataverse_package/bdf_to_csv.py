# Code for converting BDF to CSV files
## Converting all files to CSV files

import mne
import pandas as pd
import os

SOURCE_DIR = "raw\\dataverse_files"
for file in os.listdir(SOURCE_DIR):
    bdf_file = os.path.join(SOURCE_DIR, file)
    raw = mne.io.read_raw_bdf(bdf_file)

    # Extract data and channel names
    data, times = raw.get_data(return_times=True)
    channel_names = raw.ch_names

    # Create a DataFrame: channels as columns, rows as time samples
    df = pd.DataFrame(data.T, columns=channel_names)
    df['Time'] = times  # Add time column

    # Optional: reorder so Time is first column
    df = df[['Time'] + channel_names]

    # Save to CSV
    dataverse_csv = os.path.join("dataverse_csv", file.replace(".bdf", ".csv"))
    df.to_csv(f'{dataverse_csv}', index=False)
    print(f"EEG data saved to {file.replace('.bdf', '.csv')}")

print("EEG data saved to eeg_data.csv")

# ## Convert a single file to a CSV file
# bdf_file = "" # Change the name of .bdf files
# raw = mne.io.read_raw_bdf(bdf_file)

# # Extract data and channel names
# data, times = raw.get_data(return_times=True)
# channel_names = raw.ch_names

# # Create a DataFrame: channels as columns, rows as time samples
# df = pd.DataFrame(data.T, columns=channel_names)
# df['Time'] = times  # Add time column

# # Optional: reorder so Time is first column
# df = df[['Time'] + channel_names]

# # Save to CSV
# dataverse_csv = file.replace(".bdf", ".csv")
# df.to_csv(f'{dataverse_csv}', index=False)
# print(f"EEG data saved to {file.replace('.bdf', '.csv')}")

# print("EEG data saved to eeg_data.csv")
