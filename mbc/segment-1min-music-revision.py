import pandas as pd
import sys

# Function to process the CSV file
def process_csv_file(filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)
    
    # Initialize the 'Revision' column
    df['Revision'] = ''
    
    # Identify continuous segments of 'song' in Candidate
    i = 0
    while i < len(df):
        if df.at[i, 'Candidate'] == 'song':
            # Start of a continuous 'song' segment
            start_index = i
            while i < len(df) and df.at[i, 'Candidate'] == 'song':
                i += 1
            end_index = i - 1
            
            # First Job: Iterate from the start until 'music' is encountered
            j = start_index
            while j <= end_index and df.at[j, 'labels'] != 'music':
                if df.at[j, 'labels'] == 'speech':
                    df.at[j, 'Revision'] = 'speech'
                j += 1
            
            # Iterate from the end until 'music' is encountered
            j = end_index
            while j >= start_index and df.at[j, 'labels'] != 'music':
                if df.at[j, 'labels'] == 'speech':
                    df.at[j, 'Revision'] = 'speech'
                j -= 1
            
            # Second Job: Check for continuous 'music' before and after the song segment
            # Before the segment
            j = start_index - 1
            while j >= 0 and df.at[j, 'labels'] == 'music' and df.at[j+1, 'Revision'] != 'speech':
                df.at[j, 'Revision'] = 'song'
                j -= 1
            
            # After the segment
            j = end_index + 1
            while j < len(df) and df.at[j, 'labels'] == 'music' and df.at[j-1, 'Revision'] != 'speech' :
                df.at[j, 'Revision'] = 'song'
                j += 1

        else:
            i += 1
    
    # Save the processed DataFrame to a new CSV file
    modified_file_name = filename.replace('.csv', '_revisied.csv')
    #output_filename = 'revised_' + filename
    df.to_csv(modified_file_name, index=False)
    
    # Print the result for verification
    print(f"Processed data saved to {modified_file_name}")
    print(df[['labels', 'start', 'stop', 'Duration', 'Candidate', 'Revision']])


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    filename = sys.argv[1]
    #filename = 'segment-song-candidate.csv'  # Replace with your actual CSV file path
    process_csv_file(filename)