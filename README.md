# Meta Tag Verifier Web App

`This app was entirely built using Gemini 2.5 pro`

A simple web application built with Python (Flask) and vanilla JavaScript that allows users to enter a website URL and view its extracted metadata. The application fetches the target URL's HTML, parses it, and displays the `<title>` tag and various `<meta>` tags in an organized and user-friendly format.

This tool is designed to help developers, SEO specialists, and content creators quickly verify the presence and correctness of important metadata used for search engine optimization (SEO) and social media sharing (like Open Graph and Twitter Cards).

## Features

- **Title Tag Extraction:** Displays the content of the main `<title>` tag.
- **Meta Tag Extraction:** Extracts all `<meta>` tags found in the page's `<head>`.
- **Categorized Display:** Organizes metadata into logical sections:
  - General (Title, Description, Keywords, Viewport, Charset)
  - Open Graph (for Facebook, LinkedIn, etc.)
  - Twitter Card
- **Highlighting Key Tags:** Emphasizes common and important tags within each category.
- **Image Previews:** Renders image previews for `og:image` and `twitter:image` tags.
- **Copy Functionality:** Provides convenient "Copy to Clipboard" buttons for the values of important tags.
- **Raw Tag View:** Includes a collapsible section displaying all extracted meta tags with their raw attributes.
- **User Feedback:** Shows loading indicators and clear success or error messages.
- **Simple Interface:** Clean and straightforward UI for ease of use.
- **Canonical Link Check:** Detects and displays the page's `<link rel="canonical" href="...">` value (or shows a clear message when none is present), so you can verify canonicalization quickly.
- **Character Counts:** Shows character counts for `title` and `description` values (general, Open Graph and Twitter), helping you gauge length against SEO best-practices.

## Technologies Used- **Backend:**

- Python 3
- Flask (Micro web framework)
- Requests (HTTP library for fetching URLs)
- Beautiful Soup 4 (HTML parsing library)
- **Frontend:**
  - HTML5
  - CSS3 (including CSS Variables for styling)
  - Vanilla JavaScript (no frameworks, uses Fetch API, DOM manipulation)
- **Icons:**
  - Font Awesome (loaded via CDN)

## Setup and Installation

1. **Clone the Repository (or Download):**

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

   Or, simply download the `app.py` file into a directory.

2. **Install Dependencies:**
   Make sure you are in the directory containing `app.py` and run:

   ```bash
   pip install Flask requests beautifulsoup4
   ```

3. **Run the Application:**

   ```bash
   python app.py
   ```

4. **Access the App:**
   By default, the application will be running at `http://127.0.0.1:5000/`. Open this URL in your web browser. If you see `Running on http://0.0.0.0:5000/`, it means it's accessible from other devices on your network using your machine's local IP address.

## Usage

1. Navigate to the application's URL in your web browser (e.g., `http://127.0.0.1:5000/`).
2. Enter the full URL (including `http://` or `https://`) of the website you want to inspect into the input field.
3. Click the "Verify" button or press the Enter key.
4. The application will fetch the URL and display a loading indicator.
5. Once processed, the results will appear below, categorized into sections.
6. Review the General, Open Graph, and Twitter Card sections for key metadata.
7. Use the <i class="far fa-copy"></i> icon next to important tags to copy their values.
8. View image previews directly in the interface.
9. If needed, expand the "All Raw Meta Tags" section at the bottom to see a complete list of every meta tag found and its attributes.
10. If an error occurs (e.g., invalid URL, site unreachable), an error message will be displayed.

## Screenshots

_(Add screenshots of the application interface here)_

- _Screenshot of the initial input screen._
- _Screenshot of the results display with categorized sections._
- _Screenshot showing an image preview._
- _Screenshot showing the raw tags section expanded._

## Future Improvements / TODO

- More robust URL validation (handle edge cases, international domains/Punycode).
- Add visual warnings for missing _required_ tags (e.g., missing `og:title` if `og:type` is present).
- Option to simulate different User-Agents.
