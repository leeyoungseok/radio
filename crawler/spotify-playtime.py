import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
import sys

# Spotify API credentials (replace with your own client ID and secret)
CLIENT_ID = '1205859b155d48eebf81b3e5483ea23d'
CLIENT_SECRET = '219f94cc6e7e4785bfdb4630b27d175c'

# Spotify API setup
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to search for song and artist on Spotify and retrieve the playtime
def get_song_playtime(song_title, artist_name):
    try:
        results = sp.search(q=f'track:{song_title} artist:{artist_name}', type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            playtime_ms = track['duration_ms']  # Playtime in milliseconds
            playtime_seconds = playtime_ms / 1000  # Convert to seconds
            return playtime_seconds
        else:
            return None  # Return None if the song is not found
    except Exception as e:
        print(f"Error retrieving playtime for {song_title} by {artist_name}: {e}")
        return None

def get_song_playtime_with_title(song_title):
    try:
        results = sp.search(q=f'track:{song_title}', type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            playtime_ms = track['duration_ms']  # Playtime in milliseconds
            playtime_seconds = playtime_ms / 1000  # Convert to seconds
            return playtime_seconds
        else:
            return None  # Return None if the song is not found
    except Exception as e:
        print(f"Error retrieving playtime for {song_title} : {e}")
        return None

def remove_parentheses(text):
    # Remove parentheses and their contents only at the beginning and end of the string
    text = re.sub(r'^\([^()]*\)', '', text)  # Remove parentheses at the start
    text = re.sub(r'\([^()]*\)$', '', text)  # Remove parentheses at the end
    text = remove_parentheses2(text)
    return text.strip()


def remove_parentheses2(text):
    text = text.replace('\"','')
    text = text.split('(')[0]
    text = text.split(';')[0]
    while '(' in text and ')' in text:
        text = re.sub(r'\(.*?\)', '', text)  # Remove innermost parentheses
    return text.strip()

# Function to process CSV and add playtime column
def add_playtime_to_csv(input_csv, output_csv):
    # Read the CSV file with proper handling of quotes and spaces
    df = pd.read_csv(input_csv, quotechar='"', skipinitialspace=True)
    
    # Ensure columns exist
    if 'Title' not in df.columns or 'Artist' not in df.columns:
        print("Error: Input CSV must contain 'Title' and 'Artist' columns.")
        return
    
    # Add a new column for playtime
    df['Playtime (seconds)'] = None

    # Iterate over rows to fetch playtime from Spotify
    for index, row in df.iterrows():
        # Extract the first title and artist, and remove parentheses content
        song_title = remove_parentheses(row['Title'].split(',')[0])
        artist_name = remove_parentheses(row['Artist'].split(',')[0])

        # Get playtime from Spotify
        playtime = get_song_playtime(song_title, artist_name)
        if playtime == None:
            playtime = get_song_playtime_with_title(song_title)

        print(song_title, ',', artist_name, ',', playtime)
        
        # Update the DataFrame with the playtime
        df.at[index, 'Playtime (seconds)'] = playtime
    
    # Save the updated DataFrame to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV saved to {output_csv}")

# Main script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)
    
    input_csv = sys.argv[1]  # Get the input file name from command-line arguments
    output_csv = input_csv.replace(".csv", "_playtime.csv")  # Append '_playtime' to the input file name
    add_playtime_to_csv(input_csv, output_csv)

#    input_csv = "cbs_playlist_2024-12-02.csv"  # Replace with your input file
#    output_csv = "cbs_playlist_with_playtime.csv"  # Replace with your desired output file
#    add_playtime_to_csv(input_csv, output_csv)
