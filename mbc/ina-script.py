import os
import subprocess
import argparse
import re

# Set up argument parser
parser = argparse.ArgumentParser(description='Process multiple MP3 files using ina_speech_segmenter.py.')
parser.add_argument('--input_mp3_dir', required=True, help='Directory containing the MP3 files to process.')
parser.add_argument('--output_dir', required=True, help='Base directory where output CSV files will be stored.')

args = parser.parse_args()

# Function to run the ina_speech_segmenter script with options
def process_mp3_file(input_file, output_dir, csv_file):
    # Run the ina_speech_segmenter script with -d sm and -g false options
    command = [
        '/home/yslee/.local/bin/ina_speech_segmenter.py',
        '-i', input_file,
        '-o', output_dir,
        '-d', 'sm',  # Option for segmenter model
        '-g', 'false'  # Option to disable GPU
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Processed {input_file}, saved results to {csv_file}")

# Get the list of MP3 files in the input directory
mp3_files = [f for f in os.listdir(args.input_mp3_dir) if f.endswith('.mp3')]

# Process each MP3 file in the directory
for mp3_file in mp3_files:
    # Extract date from the mp3 file name (assuming format: YYYYMMDD.mp3)
    date_match = re.search(r'(\d{8})', mp3_file)
    if date_match:
        date_str = date_match.group(1)
        year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
        
        # Define output directory and CSV file based on the extracted date
        output_subdir = os.path.join(args.output_dir, f"output-{year}{month}{day}")
        os.makedirs(output_subdir, exist_ok=True)
        
        csv_file = os.path.join(output_subdir, f"{year}{month}{day}.csv")
        
        # Full path to the input MP3 file
        input_mp3_path = os.path.join(args.input_mp3_dir, mp3_file)
        
        # Process the MP3 file with the segmenter and the additional options
        process_mp3_file(input_mp3_path, output_subdir, csv_file)

    else:
        print(f"Skipping {mp3_file}, no valid date found in the filename.")
