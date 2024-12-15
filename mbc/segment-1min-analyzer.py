import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

def plot_speech_music_intervals(df, output_file='speech_music_intervals.jpg'):
    # Create the plot
    plt.figure(figsize=(12, 6))

    # Plot each row based on 'labels'
    for _, row in df.iterrows():
        label = row['labels']
        start = row['start']
        stop = row['stop']

        # Assign colors based on the label
        color = 'blue' if label == 'speech' else 'orange'
        plt.barh(label, stop - start, left=start, color=color, alpha=0.7, label=label)

    # Remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # Add labels and title
    plt.xlabel('Time (seconds)')
    plt.ylabel('Labels')
    plt.title('Speech and Music Intervals')

    # Save the plot as a .jpg file
    plt.savefig(output_file, format='jpg', dpi=300)
    print(f"Plot saved as {output_file}")

    # Show the plot (optional)
    plt.show()

def plot_speech_music_distribution(time_data, output_file='speech_music_distribution.jpg'):
    # Prepare data for plotting
    minutes = sorted(time_data.keys())
    speech_durations = [time_data[minute]['speech'] for minute in minutes]
    music_durations = [time_data[minute]['music'] for minute in minutes]

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.bar(minutes, speech_durations, label='Speech', color='blue', alpha=0.7)
    plt.bar(minutes, music_durations, label='Music', color='orange', bottom=speech_durations, alpha=0.7)
    plt.xlabel('Minutes')
    plt.ylabel('Duration (seconds)')
    plt.title('Speech and Music Distribution Per Minute')
    plt.legend()

    # Save the plot as a .jpg file
    plt.savefig(output_file, format='jpg', dpi=300)
    print(f"Plot saved as {output_file}")

    # Show the plot (optional)
    #plt.show()


# Function to calculate speech and music duration per minute and save results to a file
def calculate_speech_music_per_minute(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    df['Duration'] = df['stop'] - df['start']
    df['Candidate'] = ''  # Add Candidate column with empty values

    # Prepare a dictionary to store speech and music durations per minute
    time_data = {}

    # Iterate through each row of the DataFrame
    for _, row in df.iterrows():
        label = row['labels']
        start = row['start']
        stop = row['stop']
        
        if label == 'noEnergy':
            label = row['labels'] = 'music'
        
        # Iterate from start to stop in minute intervals
        current_time = start
        while current_time < stop:
            current_minute = int(current_time // 60)
            next_minute_start = (current_minute + 1) * 60
            
            # Calculate duration in current minute
            duration_in_current_minute = min(stop, next_minute_start) - current_time
            
            # Update dictionary
            if current_minute not in time_data:
                time_data[current_minute] = {'speech': 0, 'music': 0, 'speech_count': 0, 'music_count': 0}
            
            time_data[current_minute][label] += duration_in_current_minute
            time_data[current_minute][f'{label}_count'] += 1
            
            # Move to next time segment
            current_time = next_minute_start

    # Prepare output file name based on input file name
    input_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_file_name = f"{input_filename}-1min-result.txt"

    # Open the output file for writing results
    with open(output_file_name, 'w') as output_file:
        # Collect music detected segments
        music_detected_segments = []
        for minute in sorted(time_data.keys()):
            speech_duration = time_data[minute]['speech']
            music_duration = time_data[minute]['music']
            speech_count = time_data[minute]['speech_count']
            music_count = time_data[minute]['music_count']
            total_duration = speech_duration + music_duration
            speech_percentage = (speech_duration / total_duration) * 100 if total_duration > 0 else 0
            music_percentage = (music_duration / total_duration) * 100 if total_duration > 0 else 0

            # Write minute results to the output file
            output_file.write(
                f"Minute {minute}: Speech = {speech_duration:.2f} seconds ({speech_count} segments, {speech_percentage:.2f}%), "
                f"Music = {music_duration:.2f} seconds ({music_count} segments, {music_percentage:.2f}%)\n"
            )
            
            # Check if music percentage is 70% or more
            if music_percentage >= 70:
                if music_detected_segments and music_detected_segments[-1][1] == minute - 1:
                    music_detected_segments[-1][1] = minute
                else:
                    music_detected_segments.append([minute, minute])
                
        # Update the DataFrame with 'song' in the Candidate column for rows corresponding to detected segments
        for segment in music_detected_segments:
            for minute in range(segment[0], segment[1] + 1):
                df.loc[
                    (df['start'] // 60 <= minute) & (df['stop'] // 60 > minute), 
                    'Candidate'
                ] = 'song'

        # Print rows with 'song' in Candidate column
        output_file.write("Rows with 'song' in Candidate column:")
        #print("Rows with 'song' in Candidate column:")
        rows_with_song = df[df['Candidate'] == 'song']  # Filter rows where Candidate is 'song'
        output_file.write(rows_with_song.to_string(index=True) + "\n")
        #print(df[df['Candidate'] == 'song'])

        # Save the modified DataFrame to a new CSV
        modified_file_name = file_path.replace('.csv', '_modified.csv')
        #df['Duration'] = df['stop'] - df['start']
        df = df.round(2)
        df.to_csv(modified_file_name, index=False)
        print(f"Modified data saved to {modified_file_name}")


        # Write the music detected segments with 70% or more music
        music_detected_count = 0
        output_file.write("\nMusic Detected Segments (70% or more music):\n")
        for segment in music_detected_segments:
            if segment[1] > segment[0]:
                start_minute = segment[0]
                end_minute = segment[1]
                total_music_duration = sum(time_data[minute]['music'] for minute in range(start_minute, end_minute + 1))
                total_music_count = sum(time_data[minute]['music_count'] for minute in range(start_minute, end_minute + 1))
                output_file.write(
                    f"Music detected: {start_minute} - {end_minute} ({total_music_duration:.2f} seconds, {total_music_count} segments)\n"
                )
                music_detected_count += 1

        # Write the number of music detected segments
        output_file.write(f"\nNumber of music detected segments with 70% or more music: {music_detected_count}\n")

    print(f"Results saved to {output_file_name}")
    plot_speech_music_distribution(time_data, output_file='speech_music_distribution.jpg')
    plot_speech_music_intervals(df)

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    calculate_speech_music_per_minute(file_path)
