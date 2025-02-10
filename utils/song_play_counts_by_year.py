import os
import re
from collections import defaultdict

# Path to the 'setlist' directory
SETLIST_DIR = "../setlist/"
OUTPUT_DIR = "../statistics/song_count_by_year"  # Directory to store the yearly output files

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Dictionary to store song play counts by year
# For each year, we will store a dictionary of "Artist - Song" and their counts.
year_song_counts = defaultdict(lambda: defaultdict(int))
year_artist_counts = defaultdict(lambda: defaultdict(int))

# Updated regular expression to extract the year from filenames
year_pattern = re.compile(r"setlist_(\d{4})-\d{2}-\d{2}")

# Iterate over files in the 'setlist' directory
for filename in os.listdir(SETLIST_DIR):
    filepath = os.path.join(SETLIST_DIR, filename)
    if os.path.isfile(filepath):
        # Extract the year from the filename
        match = year_pattern.search(filename)
        if match:
            year = match.group(1)  # Extract the year (first capture group)

            # Open the file and read its content
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    # Clean up the song line (remove extra spaces, newlines, etc.)
                    song = line.strip()

                    # Skip unwanted lines
                    if not song or song.startswith("---------") or song.startswith("Setlist of"):
                        continue

                    # Avoid empty lines
                    if song:
                        # Assuming the song format is artist and song combined, e.g., "Artist - Song"
                        try:
                            artist, song_title = map(str.strip, song.split(" - ", 1))
                        except ValueError:
                            # If the format is not "Artist - Song", treat the entire line as the song title
                            artist, song_title = "Unknown Artist", song

                        # Increment the count for "Artist - Song" pair
                        year_song_counts[year][f"{artist} - {song_title}"] += 1

                        # Increment the count for the artist
                        year_artist_counts[year][artist] += 1

# Write summarized data to separate files for each year
for year in year_song_counts.keys():
    # Set the output file name for the current year
    output_file = os.path.join(OUTPUT_DIR, f"song_count_{year}.txt")

    # Calculate the total number of songs played and distinct songs played in the year
    total_songs_played = sum(year_song_counts[year].values())
    distinct_songs_count = len(year_song_counts[year])

    # Calculate the total number of songs played (from artist counts) and distinct artists
    artist_total_songs = sum(year_artist_counts[year].values())
    distinct_artist_count = len(year_artist_counts[year])

    # Write artist and song play counts for the current year
    with open(output_file, "w", encoding="utf-8") as f:
        # Write artist stats first
        f.write(f"Year: {year}\n")
        f.write(f"Total songs played: {artist_total_songs}\n")  # Renamed to "Total songs played"
        f.write(f"Distinct artists appeared: {distinct_artist_count}\n")  # Retains distinct artists count
        f.write("Count | Artist\n")
        f.write("------------------------\n")
        for artist, count in sorted(year_artist_counts[year].items(), key=lambda x: x[1],
                                    reverse=True):  # Sort artists by count
            f.write(f"{count:2} | {artist}\n")  # Add leading space for numbers < 10
        f.write("\n")  # Add a newline at the end

        # Write song stats second
        f.write(f"Total songs played: {total_songs_played}\n")  # Add the total played songs
        f.write(f"Distinct songs played: {distinct_songs_count}\n")  # Add the distinct song count
        f.write("Count | Artist - Song\n")
        f.write("------------------------\n")
        for song, count in sorted(year_song_counts[year].items(), key=lambda x: x[1],
                                  reverse=True):  # Sort songs by count
            f.write(f"{count:2} | {song}\n")  # Include artist and song in the same line
        f.write("\n")  # Add a newline at the end

print(f"Song and artist play counts by year have been saved in the folder: {OUTPUT_DIR}")
