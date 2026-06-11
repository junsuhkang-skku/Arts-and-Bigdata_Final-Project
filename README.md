# Movie Poster Color Palette Analysis Dashboard

## Project Overview

**Movie Poster Color Palette Analysis Dashboard** is a Streamlit-based interactive web application that analyzes movie poster colors using real-time data from the TMDB API.

The project collects movie metadata and poster images, then analyzes visual features such as dominant color, color palette, brightness, saturation, color diversity, and color mood. It combines Film Studies, visual design, and big data visualization by transforming movie posters into measurable image data.

## Live Demo

Add your deployed Streamlit link here:

```text
https://arts-and-bigdatafinal-project-mkmonsquvpypomj99merex.streamlit.app
```

## Main Concept

Movie posters are one of the first visual materials that audiences encounter before watching a film. They communicate mood, genre, and identity through color, brightness, contrast, and composition.

Instead of analyzing only numerical movie data such as ratings or popularity, this project focuses on movie posters as visual data. The dashboard helps users explore how different films and genres use color to create audience expectations.

## Key Features

### 1. Real-Time TMDB API Data

The dashboard uses the TMDB API to collect real-time movie information.

Collected data includes:

- Movie title
- Genre
- Release year
- Rating
- Popularity
- Overview
- Poster image URL

### 2. Dashboard Search Modes

The dashboard supports two main search modes:

- Popular Movies
- Year Range Search

Popular Movies loads currently popular movies from TMDB.

Year Range Search allows users to search movies within a selected release year range. The year condition is applied directly during the TMDB API request stage, which improves search accuracy for older films.

### 3. Safe Search Filtering

The project includes a safe search filtering system.

The TMDB API requests use adult-content exclusion, and the app also removes movies marked as adult or containing explicit keywords in the title, overview, or genre fields.

This helps keep the dashboard appropriate for general users.

### 4. Poster Color Analysis

For each poster, the app analyzes:

- Dominant color
- Full color palette
- Average brightness
- Average saturation
- Color diversity score
- Color mood classification

The poster image is loaded from its URL and processed as RGB image data.

### 5. Analysis Result Table

The result table displays analyzed poster information, including:

- Movie title
- Genre
- Year
- Rating
- Dominant color
- Color palette
- Brightness
- Saturation
- Color diversity
- Color mood

Color values are visualized as color squares so users can understand the results more easily than reading HEX codes only.

### 6. Poster Gallery with Palette

The poster gallery displays each analyzed movie as a visual card.

Each card includes:

- Poster image
- Movie title
- Year
- Rating
- Color mood
- Dominant color
- Color palette
- Brightness
- Saturation
- Color diversity
- Add to Cart button

### 7. Movie Title Search

Users can search for a movie by title using the TMDB Search API.

The app displays similar or matching movie results. When a user selects one movie, the dashboard shows an individual movie detail page with poster analysis.

The detail page includes:

- Poster image
- Movie title
- Release year
- Genre
- Rating
- Popularity
- Overview
- Dominant color
- Color palette
- Brightness
- Saturation
- Color diversity
- Color mood
- Poster image download button
- Add to Cart button

### 8. Poster Cart

Users can add posters to a personal cart.

The cart stores poster information such as:

- Movie title
- Poster image
- Dominant color
- Color palette
- Brightness
- Saturation
- Color diversity
- Color mood

The cart page is separated from the dashboard and loads cart items only when the user enters the Cart page. This reduces unnecessary dashboard reloading.

The cart supports:

- Gallery-style cart view
- Cart information CSV download
- All poster images ZIP download
- Remove selected item
- Clear cart

### 9. Dominant Color Challenge Game

The dashboard includes an interactive game called **Dominant Color Challenge**.

After poster analysis is completed, the game randomly selects one analyzed poster. The user guesses the dominant color using a color picker.

The app calculates similarity between the user's selected color and the actual dominant color. If the similarity is 80% or higher, the answer is counted as successful.

Game features include:

- Random analyzed poster selection
- Color picker input
- RGB distance-based similarity calculation
- 80% success threshold
- Score tracking
- Duplicate poster prevention
- Next question disabled until an answer is submitted

### 10. Advanced Analysis

The dashboard provides advanced analysis features:

- Genre-based average color analysis
- Decade trend analysis
- Color mood distribution
- Poster ranking analysis
- CSV download

Decade Trend Analysis groups movies by decade and compares average brightness, saturation, color diversity, and rating.

Poster Ranking Analysis includes:

- Darkest posters
- Brightest posters
- Most saturated posters
- Least saturated posters
- Most color-diverse posters
- Highest-rated posters

## Tech Stack

This project uses:

- Python
- Streamlit
- Pandas
- NumPy
- Requests
- Pillow
- scikit-learn
- Plotly
- python-dotenv
- TMDB API

## File Structure

```text
final_artsbigdata/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── src/
    ├── tmdb_api.py
    ├── poster_fetcher.py
    ├── color_analysis.py
    ├── analysis_pipeline.py
    ├── ui_components.py
    ├── advanced_analysis.py
    ├── download_utils.py
    ├── cart_utils.py
    └── game_utils.py
```

## File Description

### app.py

Main Streamlit application file.

It controls:

- Page configuration
- Sidebar navigation
- Dashboard page
- Movie Search page
- Cart page
- Game Zone page
- Advanced Analysis page

### src/tmdb_api.py

Handles TMDB API requests.

Main functions include:

- Loading the TMDB API key
- Fetching popular movies
- Fetching movies by year range
- Searching movies by title
- Getting movie detail data
- Creating poster image URLs
- Filtering adult or explicit results
- Converting API responses into Pandas DataFrames

### src/poster_fetcher.py

Handles poster image loading and download preparation.

Main functions include:

- Loading poster images from URL
- Converting poster images into Pillow image objects
- Getting image bytes for download
- Creating safe poster file names

### src/color_analysis.py

Analyzes poster image colors.

Main functions include:

- Dominant color extraction
- Color palette extraction
- Brightness calculation
- Saturation calculation
- Color diversity score calculation
- Color mood classification
- HEX and RGB conversion

### src/analysis_pipeline.py

Connects movie metadata with poster image analysis.

Main functions include:

- Analyzing a movie DataFrame
- Analyzing a single movie
- Cleaning analysis results
- Creating dataset summary values

### src/ui_components.py

Contains reusable Streamlit UI components.

Main functions include:

- Dominant color display
- Color palette display
- Result table rendering
- Poster gallery rendering
- Single movie detail page rendering

### src/advanced_analysis.py

Creates advanced analysis outputs.

Main functions include:

- Genre-based average analysis
- Decade trend analysis
- Poster ranking analysis
- Color mood summary

### src/download_utils.py

Handles download features.

Main functions include:

- Analysis CSV export
- Cart information CSV download
- Poster image ZIP download

### src/cart_utils.py

Manages the poster cart using Streamlit session state.

Main functions include:

- Cart initialization
- Add to cart flag
- Remove from cart
- Clear cart
- Cart count
- Cart DataFrame creation

### src/game_utils.py

Handles the Dominant Color Challenge game logic.

Main functions include:

- Random poster selection
- Color similarity calculation
- Answer evaluation
- Score tracking
- Duplicate poster prevention

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. Create a Virtual Environment

For Mac OS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

## API Key Setup

This project requires a TMDB API key.

Create a `.env` file in the project root folder:

```bash
touch .env
```

Inside `.env`, add:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

Do not upload `.env` to GitHub.

For GitHub, only upload `.env.example`:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

## Streamlit Cloud Secrets

When deploying to Streamlit Cloud, add the API key in the app's Secrets settings:

```toml
TMDB_API_KEY = "your_tmdb_api_key_here"
```

This allows the deployed app to use the TMDB API without exposing the API key in GitHub.

## How to Run

Run the Streamlit app locally:

```bash
streamlit run app.py
```

Default local URL:

```text
http://localhost:8501
```

## Main Data Columns

| Column Name | Description |
|---|---|
| tmdb_id | TMDB movie ID |
| title | Movie title |
| genres | Movie genres |
| year | Release year |
| release_date | Full release date |
| rating | TMDB average rating |
| vote_count | Number of votes |
| popularity | TMDB popularity score |
| overview | Movie overview |
| poster_url | Poster image URL |
| dominant_color | Main extracted color |
| dominant_colors | Extracted color palette |
| brightness | Average poster brightness |
| saturation | Average poster saturation |
| color_diversity | Color diversity score |
| color_mood | Classified color mood |

## Color Analysis Method

### Dominant Color

The dominant color is extracted using KMeans clustering. Poster pixels are grouped into several color clusters, and the most frequent cluster is selected as the dominant color.

### Color Palette

The color palette is created from the representative cluster colors extracted from the poster image.

### Brightness

Brightness is calculated from RGB pixel values using a weighted RGB formula:

```text
brightness = 0.299R + 0.587G + 0.114B
```

### Saturation

Saturation is calculated by converting RGB values into HSV color space and averaging the saturation values.

### Color Diversity

Color diversity is calculated by measuring the average RGB distance between extracted palette colors.

### Color Mood

Color mood is classified using brightness, saturation, and dominant color hue.

Examples include:

- Dark / Moody
- Vivid / Energetic
- Warm
- Cold / Mysterious
- Neutral / Minimal
- Balanced

## Dashboard Pages

### Dashboard

The main analysis page.

It supports:

- Popular Movies search
- Year Range Search
- Poster color analysis
- Dataset overview
- Result table
- Brightness and saturation charts
- Genre-based analysis
- Poster gallery

### Movie Search

Searches for a specific movie title and provides individual poster analysis.

### Cart

Displays saved posters and supports CSV and ZIP download.

### Game Zone

Provides the Dominant Color Challenge game.

### Advanced Analysis

Provides decade trend, ranking, and color mood analysis.

## Download Features

The app supports:

- Individual poster image download
- Full analysis CSV download
- Cart information CSV download
- All cart poster images ZIP download

## Development Notes

During development, several changes were made to improve stability and usability.

- IMDb HTML parsing was first considered, but the project changed to TMDB API because API-based data collection is safer and more stable.
- Python 3.9 did not support the `str | None` syntax, so the code was changed to use `Optional[str]`.
- Streamlit Cloud had issues with Pandas Styler, so the result table was rebuilt using HTML components.
- Cart logic was redesigned as flag-based lazy loading to reduce unnecessary dashboard reloading.
- Game logic was improved to prevent duplicate posters and to require answer submission before moving to the next question.

## Future Improvements

Possible future improvements include:

- User login system
- Persistent cart database using SQLite or Firebase
- More advanced color similarity using HSV or LAB color space
- Genre signature palette generation
- Similar poster recommendation
- Poster design trend comparison by decade
- Streamlit fragment optimization for partial reruns

## One-Sentence Summary

This project analyzes movie poster color palettes to explore how films use color, brightness, saturation, and visual mood to communicate genre and identity.
