import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- HTML Template ---
# We embed the HTML directly here for simplicity
# In a larger app, you'd use template files (e.g., using render_template)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meta Tag Extractor</title>
    <style>
        body {
            font-family: sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: auto;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        #url-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        #urlInput {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        #submitButton {
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        #submitButton:hover {
            background-color: #0056b3;
        }
        #results {
            background-color: #fff;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-height: 100px;
            white-space: pre-wrap; /* Allows line breaks */
            word-wrap: break-word; /* Breaks long words */
        }
        .loading {
            color: #555;
            font-style: italic;
        }
        .error {
            color: #d9534f;
            font-weight: bold;
        }
        .meta-item {
            border-bottom: 1px dashed #eee;
            padding-bottom: 5px;
            margin-bottom: 5px;
        }
        .meta-item:last-child {
            border-bottom: none;
        }
        .attr-name {
            font-weight: bold;
            color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Website Meta Tag Extractor</h1>

    <div id="url-form">
        <input type="url" id="urlInput" placeholder="Enter website URL (e.g., https://www.example.com)" required>
        <button id="submitButton">Extract Meta Tags</button>
    </div>

    <h2>Results:</h2>
    <div id="results">
        Enter a URL above and click "Extract Meta Tags".
    </div>

    <script>
        const urlInput = document.getElementById('urlInput');
        const submitButton = document.getElementById('submitButton');
        const resultsDiv = document.getElementById('results');

        submitButton.addEventListener('click', async () => {
            const url = urlInput.value.trim();
            if (!url) {
                resultsDiv.innerHTML = '<p class="error">Please enter a URL.</p>';
                return;
            }

            resultsDiv.innerHTML = '<p class="loading">Fetching and extracting...</p>';
            submitButton.disabled = true; // Prevent multiple clicks

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url }),
                });

                const data = await response.json();

                if (!response.ok) {
                    // Use error message from backend if available
                    throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                }

                if (data.metadata && data.metadata.length > 0) {
                    resultsDiv.innerHTML = ''; // Clear loading message
                    data.metadata.forEach(meta => {
                        const itemDiv = document.createElement('div');
                        itemDiv.classList.add('meta-item');
                        let attributesHTML = '';
                        for (const [key, value] of Object.entries(meta.attributes)) {
                            // Basic escaping to prevent HTML injection from attribute values
                            const safeKey = key.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                            const safeValue = value.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                            attributesHTML += `<span class="attr-name">${safeKey}</span>: "${safeValue}"<br>`;
                        }
                        itemDiv.innerHTML = attributesHTML || '<i>(Empty meta tag)</i>';
                        resultsDiv.appendChild(itemDiv);
                    });
                } else if (data.metadata) {
                     resultsDiv.innerHTML = '<p>No meta tags found on the page.</p>';
                } else {
                    // Should have been caught by !response.ok, but just in case
                     resultsDiv.innerHTML = '<p class="error">Received unexpected data from server.</p>';
                }

            } catch (error) {
                console.error('Error:', error);
                resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            } finally {
                 submitButton.disabled = false; // Re-enable button
            }
        });

        // Optional: Allow pressing Enter in the input field
        urlInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent default form submission if it were in a form
                submitButton.click(); // Trigger the button click
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract_meta():
    """API endpoint to extract metadata from a given URL."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL parameter is missing'}), 400

    url = data['url']
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url # Basic attempt to fix missing protocol

    app.logger.info(f"Attempting to fetch URL: {url}")

    try:
        # Send a GET request with a User-Agent and timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MetaExtractorBot/1.0'
        }
        # Allow redirects, set a timeout
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Check if content type is HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
             app.logger.warning(f"URL {url} returned non-HTML content-type: {content_type}")
             # Allow processing anyway, BeautifulSoup might handle it, or return specific error:
             # return jsonify({'error': f'URL did not return HTML content (Content-Type: {content_type})'}), 400


        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <meta> tags
        meta_tags = soup.find_all('meta')

        # Extract attributes from each meta tag
        extracted_data = []
        for tag in meta_tags:
            # tag.attrs is a dictionary of the tag's attributes
            if tag.attrs: # Only add if it has attributes
                extracted_data.append({'attributes': tag.attrs})

        app.logger.info(f"Successfully extracted {len(extracted_data)} meta tags from {url}")
        return jsonify({'metadata': extracted_data})

    except requests.exceptions.Timeout:
        app.logger.error(f"Timeout occurred while fetching {url}")
        return jsonify({'error': f'Request timed out for URL: {url}'}), 504 # Gateway Timeout
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching URL {url}: {e}")
        # Provide a more specific error if possible
        error_message = f'Could not fetch or process URL: {url}. Error: {e}'
        status_code = 500 # Internal Server Error by default
        if isinstance(e, requests.exceptions.ConnectionError):
            error_message = f'Could not connect to URL: {url}. Check the address and network connection.'
            status_code = 400 # Bad Request (likely bad URL)
        elif isinstance(e, requests.exceptions.HTTPError):
            error_message = f'HTTP Error {e.response.status_code} for URL: {url}.'
            status_code = 400 # Bad Request (or map specific codes)

        return jsonify({'error': error_message}), status_code
    except Exception as e:
        # Catch potential BeautifulSoup errors or other unexpected issues
        app.logger.error(f"An unexpected error occurred processing {url}: {e}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible on your network
    # debug=True is useful for development (auto-reloads), but disable for production
    app.run(host='0.0.0.0', port=5000, debug=True)
