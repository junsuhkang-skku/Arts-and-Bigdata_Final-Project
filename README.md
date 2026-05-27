# Movie Poster Color Palette Analysis Dashboard

## 1. Project Overview

**Movie Poster Color Palette Analysis Dashboard** is a Streamlit-based web dashboard that analyzes movie poster images using real-time movie data from the TMDB API.

The project focuses on how movie posters use color to communicate genre, mood, and visual identity. Since movie posters are important visual materials in film marketing, this dashboard treats poster images as visual data and extracts measurable features such as dominant colors, brightness, and saturation.

This project connects **Film Studies**, **visual design**, and **big data analysis** by transforming visual impressions into data-based insights.

---

## 2. Project Goal

The goal of this project is to build an interactive dashboard that allows users to explore movie poster color patterns.

The dashboard helps users understand:

- What colors are commonly used in movie posters
- How poster color palettes differ by movie genre
- Which posters are darker, brighter, or more saturated
- How color can support genre identity and audience expectations
- How visual elements in film marketing can be analyzed as data

---

## 3. Key Features

### 1. Real-time Movie Data Collection

The dashboard uses the **TMDB API** to collect movie data in real time.

Collected data includes:

- Movie title
- Genre
- Release year
- Rating
- Popularity
- Poster URL

### 2. Search Mode Selection

Users can choose between two search modes:

#### Popular Movies

This mode collects currently popular movies from TMDB.

#### Year Range Search

This mode allows users to search movies within a selected release year range.

This improves search accuracy because the year condition is applied directly during the API request stage.

### 3. Search Filters

The dashboard includes interactive filters:

- TMDB page count
- Release year range
- Minimum rating

These filters allow users to control the size and type of movie data used for analysis.

### 4. Poster Color Analysis

For each movie poster, the dashboard analyzes:

- Dominant color
- Color palette
- Average brightness
- Average saturation

The poster image is processed using Python image analysis libraries.

### 5. Color Palette Visualization

The extracted color palette is displayed visually as color blocks.

This allows users to understand poster color composition more easily than reading HEX color codes only.

### 6. Brightness and Saturation Charts

The dashboard provides visual charts such as:

- Poster brightness by movie
- Poster saturation by movie
- Average brightness by genre
- Average saturation by genre

These charts help compare visual characteristics across movies and genres.

### 7. Poster Gallery

The dashboard displays a poster gallery with:

- Poster image
- Movie title
- Release year
- Rating
- Dominant color
- Color palette
- Brightness
- Saturation

---

## 4. Target Users

This dashboard is designed for:

- Film studies students
- Visual design students
- Movie fans
- Film marketers
- Researchers interested in visual trends
- People interested in movie poster design

---

## 5. Tech Stack

The project uses the following technologies:

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Pillow
- scikit-learn
- Requests
- python-dotenv
- TMDB API

---

## 6. File Structure

```text
movie-poster-color-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── src/
    ├── tmdb_api.py
    ├── poster_fetcher.py
    └── color_analysis.py
```

---

## 7. File Description

### `app.py`

Main Streamlit application file.

It controls:

- Dashboard layout
- Sidebar filters
- Movie data loading
- Poster analysis execution
- Charts
- Result table
- Poster gallery

### `src/tmdb_api.py`

Handles TMDB API requests.

Main functions include:

- Fetching popular movies
- Searching movies by year range
- Getting genre information
- Creating poster image URLs
- Converting API results into a DataFrame

### `src/poster_fetcher.py`

Loads poster images from URL.

It downloads poster images and converts them into Pillow image objects for analysis.

### `src/color_analysis.py`

Analyzes poster images.

Main features include:

- Dominant color extraction
- Color palette extraction
- Brightness calculation
- Saturation calculation

### `requirements.txt`

Contains the Python libraries required to run the project.

### `.env.example`

Example file for setting up the TMDB API key.

The actual `.env` file should not be uploaded to GitHub.

---

## 8. Installation

### Step 1. Clone the repository

```bash
git clone https://github.com/your-username/movie-poster-color-dashboard.git
cd movie-poster-color-dashboard
```

### Step 2. Create a virtual environment

For Mac OS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3. Install required packages

```bash
pip install -r requirements.txt
```

---

## 9. API Key Setup

This project requires a TMDB API key.

Create a `.env` file in the project root folder.

```bash
touch .env
```

Inside `.env`, add your TMDB API key:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

Do not upload `.env` to GitHub.

The `.gitignore` file should include:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.DS_Store
.ipynb_checkpoints/
```

---

## 10. How to Run

Run the Streamlit app with:

```bash
streamlit run app.py
```

The dashboard will open in your browser.

Default local URL:

```text
http://localhost:8501
```

---

## 11. Main Data Columns

The dashboard uses the following main data columns:

| Column Name | Description |
|---|---|
| `title` | Movie title |
| `genres` | Movie genres |
| `year` | Release year |
| `rating` | Movie rating |
| `popularity` | TMDB popularity score |
| `poster_url` | Movie poster image URL |
| `dominant_color` | Main extracted color |
| `dominant_colors` | Extracted color palette |
| `brightness` | Average poster brightness |
| `saturation` | Average poster saturation |

---

## 12. Color Analysis Method

The project analyzes each movie poster as image data.

### Dominant Color

The dominant color is extracted using clustering.

The image pixels are grouped into several color clusters, and the most common cluster is selected as the dominant color.

### Color Palette

A palette of multiple representative colors is extracted from each poster.

### Brightness

Brightness is calculated using RGB values.

### Saturation

Saturation is calculated by converting RGB values into HSV color space and measuring the average saturation level.

---

## 13. Dashboard Preview

Add a dashboard screenshot here after running the app.

```markdown
![Dashboard Preview](assets/dashboard_preview.png)
```

---

## 14. Project Meaning

This project shows that movie posters can be analyzed not only as visual artworks but also as data.

By extracting dominant colors, brightness, and saturation from posters, the dashboard makes it possible to compare visual styles across movies and genres. This helps explain how film marketing uses color to create mood, genre identity, and audience expectations.

---

## 15. Future Improvements

Possible future improvements include:

- Add genre selection filter
- Add movie title search
- Add CSV download feature
- Add poster ranking by brightness and saturation
- Add more advanced color emotion analysis
- Compare poster color trends by decade
- Deploy the dashboard using Streamlit Cloud

---

## 16. One-Sentence Summary

This project analyzes movie poster color palettes to discover how films use color, brightness, and saturation to communicate mood, genre, and visual identity.
