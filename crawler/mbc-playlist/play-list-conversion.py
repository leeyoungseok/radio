import pandas as pd

# Function to process the playlist text and save CSV files by date, handling artists with commas
def process_playlist_to_csv(file_path):
    # Read the text file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Prepare lists for data
    dates = []
    numbers = []
    music_titles = []
    singers = []
    durations = []

    # Initialize track number
    track_number = 1

    # Extract relevant data
    for line in lines:
        if "not found on Spotify" in line:
            # Handle the case when a song is not found on Spotify
            parts = line.strip().split(", Song: ")
            date = parts[0].replace("Date: ", "")
            song_artist = parts[1].split(", Artist: ")
            song = song_artist[0]
            artist = song_artist[1].replace(" not found on Spotify", "")
            playtime = 0
        else:
            try:
                parts = line.strip().split(", Playtime: ")
                playtime = float(parts[1].replace(" seconds", ""))
                meta_data = parts[0].split(", Artist: ")
                artist = meta_data[1]
                date_song = meta_data[0].split(", Song: ")
                date = date_song[0].replace("Date: ", "")
                song = date_song[1]
            except IndexError:
                continue
        
        # Append data to lists
        dates.append(date)
        numbers.append(track_number)
        music_titles.append(song)
        singers.append(artist)
        durations.append(playtime)
        track_number += 1

    # Create a DataFrame
    df = pd.DataFrame({
        'date': dates,
        'number': numbers,
        'music_title': music_titles,
        'singer': singers,
        'duration': durations
    })

    # Save to CSV files by date
    for date in df['date'].unique():
        date_df = df[df['date'] == date]
        date_df['number'] = range(1, len(date_df) + 1)
        filename = f"{date}.csv"
        date_df[['number', 'music_title', 'singer', 'duration']].to_csv(filename, index=False)
        print(f"Saved {filename}")

# Example usage
process_playlist_to_csv('mbc-playlist-1015-spotify.csv')
