#!/usr/bin/env python3
import os
import sys
import json
import random

from to_save_fileformat import to_safe_filename

def load_meta(meta_filename):
    """
    Reads the meta file (movie.metadata.tsv).
    Columns (tab-separated), at least:
      - Col 0: movie ID
      - Col 2: title
      - Col 3: date or year (e.g. '2001-08-24')

    Returns a dict mapping:
      {
        <movie_id>: {
          "title": <str>,
          "year": <str>
        },
        ...
      }
    """
    meta_dict = {}
    with open(meta_filename, "r", encoding="utf-8") as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            # Need at least 4 columns for ID, something, title, and year/date
            if len(parts) < 4:
                continue

            movie_id = parts[0].strip()
            title = parts[2].strip()
            date_str = parts[3].strip()

            # Extract year from something like "2001-08-24" -> "2001"
            year = ""
            if date_str:
                if "-" in date_str:
                    year = date_str.split("-", 1)[0]  # take first part
                else:
                    year = date_str

            meta_dict[movie_id] = {
                "title": title,
                "year": year
            }

    return meta_dict

def load_plots(plot_filename):
    """
    Reads *all* lines from plot_summaries.txt into a list (so we can shuffle).
    Each line has format:
      <movie_id>\\t<plot_text>

    Returns a list of strings (each is one raw line).
    """
    lines = []
    with open(plot_filename, "r", encoding="utf-8") as plot_file:
        for line in plot_file:
            line = line.strip()
            if line:
                lines.append(line)
    return lines

def main():
    """
    Usage:
      python generate_movie_dataset.py <meta_file> <plot_file> <output_dir> [max_movies] [seed]

    Example:
      python generate_movie_dataset.py \
         /path/to/movie.metadata.tsv \
         /path/to/plot_summaries.txt \
         /path/to/output_dir \
         100 \
         123
    This would shuffle with seed=123 and limit output to 100 movies (with >=200 words in the plot).
    """
    if len(sys.argv) < 4:
        print("Error: Not enough arguments.")
        print("Usage: python generate_movie_dataset.py <meta_file> <plot_file> <output_dir> [max_movies] [seed]")
        sys.exit(1)

    meta_filename = sys.argv[1]
    plot_filename = sys.argv[2]
    output_dir = sys.argv[3]

    # Optional arguments
    max_movies = None
    if len(sys.argv) > 4:
        max_movies = int(sys.argv[4])

    seed = 42  # default seed
    if len(sys.argv) > 5:
        seed = int(sys.argv[5])

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load metadata into a dict
    meta_dict = load_meta(meta_filename)

    # Load *all* plot lines
    plot_lines = load_plots(plot_filename)

    # Shuffle them using the given seed
    random.seed(seed)
    random.shuffle(plot_lines)

    count = 0
    for line in plot_lines:
        # Each line is "<movie_id>\t<plot_text>"
        parts = line.split("\t", 1)
        if len(parts) < 2:
            continue

        movie_id = parts[0].strip()
        plot_text = parts[1].strip()

        # Check if we have meta info for this movie
        meta_info = meta_dict.get(movie_id)
        if meta_info is None:
            title = f"Title not found for ID {movie_id}"
            year = ""
        else:
            title = meta_info["title"]
            year = meta_info["year"]

        # Check if plot has >= 200 words
        word_count = len(plot_text.split())
        if word_count < 200:
            continue

        # prepend title and year to plottext
        plot_text = f"Title: {title} ({year})\n\n{plot_text}"

        # If we have a max limit, stop once reached
        if max_movies is not None and count >= max_movies:
            break

        # Construct the JSON record
        json_record = {
            "item_type": "movie",
            "title": title,
            "year": year,
            "descriptions": [plot_text],
            "origin": "Human"
        }

        # Create a safe JSON filename from the movie title
        filename = to_safe_filename(
            title_text=title,
            prompt_key="movie",
            max_title_characters=32
        )
        out_path = os.path.join(output_dir, filename)

        # Write the JSON file
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(json_record, f, indent=2, ensure_ascii=False)

        print(f"Saved: {out_path}")
        count += 1

if __name__ == "__main__":
    main()
