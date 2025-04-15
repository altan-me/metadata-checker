import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- HTML Template (Updated) ---
# See section 2 below for the new HTML/CSS/JS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meta Tag Verifier</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --border-color: #dee2e6;
            --text-color: #212529;
            --light-text: #6c757d;
            --error-color: #dc3545;
            --success-color: #28a745;
            --font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
        }
        body {
            font-family: var(--font-family);
            line-height: 1.6;
            padding: 20px;
            background-color: var(--background-color);
            color: var(--text-color);
            margin: 0;
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            background-color: var(--card-background);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 30px;
            font-weight: 600;
        }
        #url-form {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        #urlInput {
            flex-grow: 1;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 1rem;
        }
        #submitButton {
            padding: 12px 20px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.2s ease-in-out;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #submitButton:hover:not(:disabled) {
            background-color: #0056b3;
        }
        #submitButton:disabled {
            background-color: var(--secondary-color);
            cursor: not-allowed;
        }
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        #results-container {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }
        #results-status {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 4px;
            font-weight: 500;
        }
        #results-status.loading {
            background-color: #e9ecef;
            color: var(--light-text);
            text-align: center;
        }
        #results-status.error {
            background-color: #f8d7da;
            color: var(--error-color);
            border: 1px solid #f5c6cb;
        }
        #results-status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        #results-status a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: bold;
        }
        #results-status a:hover {
            text-decoration: underline;
        }
        .meta-section {
            margin-bottom: 25px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            overflow: hidden; /* Contain borders */
        }
        .meta-section h3 {
            background-color: #e9ecef;
            padding: 10px 15px;
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .meta-section h3 i {
            color: var(--primary-color);
        }
        .meta-content {
            padding: 15px;
        }
        .meta-item {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 5px 15px; /* row-gap column-gap */
            padding: 8px 0;
            border-bottom: 1px dashed #eee;
            align-items: start; /* Align items to the top */
        }
        .meta-item:last-child {
            border-bottom: none;
        }
        .meta-key {
            font-weight: bold;
            color: var(--primary-color);
            text-align: right;
            white-space: nowrap;
        }
        .meta-value {
            word-wrap: break-word;
            white-space: pre-wrap; /* Preserve whitespace formatting */
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 3px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .meta-value.missing {
            color: var(--error-color);
            font-style: italic;
            background-color: transparent;
            padding: 0;
        }
        .meta-value img {
            max-width: 100%;
            height: auto;
            max-height: 150px; /* Limit preview height */
            display: block;
            margin-top: 5px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }
        .copy-button {
            background: none;
            border: none;
            color: var(--secondary-color);
            cursor: pointer;
            font-size: 0.9em;
            padding: 5px;
            line-height: 1; /* Ensure icon aligns well */
            transition: color 0.2s;
        }
        .copy-button:hover {
            color: var(--primary-color);
        }
        .raw-attributes {
            font-size: 0.85em;
            color: var(--light-text);
            margin-top: 5px;
            white-space: pre-wrap;
            word-break: break-all;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
        }
        details { /* Style the collapsible raw section */
            border: 1px solid var(--border-color);
            border-radius: 5px;
            margin-top: 15px;
        }
        details summary {
            background-color: #e9ecef;
            padding: 10px 15px;
            cursor: pointer;
            font-weight: 600;
            outline: none; /* Remove focus outline */
        }
        details summary:hover {
            background-color: #d8dde2;
        }
        .raw-tag-list {
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
            line-height: 1.5;
        }
        .raw-tag {
            border-bottom: 1px dashed #eee;
            padding-bottom: 8px;
            margin-bottom: 8px;
        }
        .raw-tag:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        .attr-name {
            font-weight: bold;
            color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-tags"></i> Meta Tag Verifier</h1>

        <div id="url-form">
            <input type="url" id="urlInput" placeholder="Enter website URL (e.g., https://www.example.com)" required>
            <button id="submitButton">
                <span id="button-text">Verify</span>
                <div id="spinner" class="spinner" style="display: none;"></div>
            </button>
        </div>

        <div id="results-container" style="display: none;">
            <div id="results-status"></div>
            <div id="results-content">
                <!-- Results will be populated here -->
            </div>
        </div>
         <div id="initial-message">
             Enter a URL above and click "Verify" to see its metadata.
         </div>
    </div>

    <script>
        const urlInput = document.getElementById('urlInput');
        const submitButton = document.getElementById('submitButton');
        const buttonText = document.getElementById('button-text');
        const spinner = document.getElementById('spinner');
        const resultsContainer = document.getElementById('results-container');
        const resultsStatus = document.getElementById('results-status');
        const resultsContent = document.getElementById('results-content');
        const initialMessage = document.getElementById('initial-message');

        // --- Helper Functions ---
        function escapeHtml(unsafe) {
            if (unsafe === null || unsafe === undefined) return '';
            return unsafe
                 .toString()
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        function createCopyButton(textToCopy) {
            const button = document.createElement('button');
            button.className = 'copy-button';
            button.innerHTML = '<i class="far fa-copy"></i>';
            button.title = 'Copy value';
            button.onclick = () => {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    button.innerHTML = '<i class="fas fa-check" style="color: var(--success-color);"></i>';
                    setTimeout(() => { button.innerHTML = '<i class="far fa-copy"></i>'; }, 1500);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy text.');
                });
            };
            return button;
        }

        function createMetaItem(key, value, container, isImportant = false, isImage = false) {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'meta-item';

            const keySpan = document.createElement('span');
            keySpan.className = 'meta-key';
            keySpan.textContent = key + ':';
            itemDiv.appendChild(keySpan);

            const valueSpan = document.createElement('span');
            valueSpan.className = 'meta-value';
            if (value) {
                valueSpan.textContent = value;
                if (isImage) {
                    const img = document.createElement('img');
                    img.src = value;
                    img.alt = `${key} preview`;
                    img.onerror = () => { img.style.display = 'none'; }; // Hide if image fails to load
                    valueSpan.appendChild(img);
                }
            } else {
                valueSpan.textContent = '(Not set or empty)';
                valueSpan.classList.add('missing');
            }
            itemDiv.appendChild(valueSpan);

            if (value && isImportant) {
                itemDiv.appendChild(createCopyButton(value));
            } else {
                 itemDiv.appendChild(document.createElement('span')); // Placeholder for grid alignment
            }

            container.appendChild(itemDiv);
        }

        function displayResults(data, url) {
            resultsContent.innerHTML = ''; // Clear previous results
            initialMessage.style.display = 'none';
            resultsContainer.style.display = 'block';

            const { title, metadata } = data;

            // --- Status Message ---
            const safeUrl = escapeHtml(url);
            resultsStatus.className = 'success';
            resultsStatus.innerHTML = `Successfully fetched metadata for: <a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${safeUrl}</a>`;

            // --- Prepare Data Structures ---
            const generalMeta = {};
            const ogMeta = {};
            const twitterMeta = {};
            const otherMeta = []; // Keep raw structure for 'other'

            // --- Extract Title ---
            generalMeta['page_title'] = title || null; // Use a distinct key

            // --- Process Meta Tags ---
            const metaMap = new Map(); // Use map to easily find tags by name/property
            metadata.forEach(tag => {
                const attrs = tag.attributes;
                if (attrs.name) metaMap.set(attrs.name.toLowerCase(), attrs.content);
                if (attrs.property) metaMap.set(attrs.property.toLowerCase(), attrs.content);
                if (attrs.charset) metaMap.set('charset', attrs.charset); // Handle charset separately
                if (attrs.hasOwnProperty('http-equiv')) metaMap.set(`http-equiv-${attrs['http-equiv'].toLowerCase()}`, attrs.content);

                // Categorize for display
                if (attrs.property?.startsWith('og:')) {
                    ogMeta[attrs.property] = attrs.content;
                } else if (attrs.name?.startsWith('twitter:')) {
                    twitterMeta[attrs.name] = attrs.content;
                } else if (attrs.name && ['description', 'keywords', 'author', 'viewport'].includes(attrs.name.toLowerCase())) {
                    generalMeta[attrs.name.toLowerCase()] = attrs.content;
                } else if (attrs.charset) {
                     generalMeta['charset'] = attrs.charset;
                } else {
                    otherMeta.push(tag); // Keep the original structure for the raw list
                }
            });

             // Ensure common general tags are present, even if null
            ['description', 'keywords', 'author', 'viewport', 'charset'].forEach(key => {
                if (!generalMeta.hasOwnProperty(key)) {
                    generalMeta[key] = null;
                }
            });
             // Ensure common OG tags are present
            ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name'].forEach(key => {
                 if (!ogMeta.hasOwnProperty(key)) {
                    ogMeta[key] = null;
                 }
            });
             // Ensure common Twitter tags are present
            ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image', 'twitter:site'].forEach(key => {
                 if (!twitterMeta.hasOwnProperty(key)) {
                    twitterMeta[key] = null;
                 }
            });


            // --- Build HTML Sections ---

            // 1. General Section
            const generalSection = document.createElement('div');
            generalSection.className = 'meta-section';
            generalSection.innerHTML = '<h3><i class="fas fa-info-circle"></i> General</h3>';
            const generalContent = document.createElement('div');
            generalContent.className = 'meta-content';
            createMetaItem('Page Title', generalMeta.page_title, generalContent, true);
            createMetaItem('Description', generalMeta.description, generalContent, true);
            createMetaItem('Keywords', generalMeta.keywords, generalContent, false); // Less important now
            createMetaItem('Author', generalMeta.author, generalContent, false);
            createMetaItem('Viewport', generalMeta.viewport, generalContent, false);
            createMetaItem('Charset', generalMeta.charset, generalContent, false);
            generalSection.appendChild(generalContent);
            resultsContent.appendChild(generalSection);

            // 2. Open Graph Section
            const ogSection = document.createElement('div');
            ogSection.className = 'meta-section';
            ogSection.innerHTML = '<h3><i class="fab fa-facebook-square"></i> Open Graph (Facebook, LinkedIn, etc.)</h3>';
            const ogContent = document.createElement('div');
            ogContent.className = 'meta-content';
            createMetaItem('og:title', ogMeta['og:title'], ogContent, true);
            createMetaItem('og:description', ogMeta['og:description'], ogContent, true);
            createMetaItem('og:image', ogMeta['og:image'], ogContent, true, true); // Mark as image
            createMetaItem('og:url', ogMeta['og:url'], ogContent, true);
            createMetaItem('og:type', ogMeta['og:type'], ogContent, false);
            createMetaItem('og:site_name', ogMeta['og:site_name'], ogContent, false);
            // Add any other found OG tags
            for (const [key, value] of Object.entries(ogMeta)) {
                if (!['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name'].includes(key)) {
                     createMetaItem(key, value, ogContent, false, key.endsWith(':image'));
                }
            }
            ogSection.appendChild(ogContent);
            resultsContent.appendChild(ogSection);

            // 3. Twitter Card Section
            const twitterSection = document.createElement('div');
            twitterSection.className = 'meta-section';
            twitterSection.innerHTML = '<h3><i class="fab fa-twitter-square"></i> Twitter Card</h3>';
            const twitterContent = document.createElement('div');
            twitterContent.className = 'meta-content';
            createMetaItem('twitter:card', twitterMeta['twitter:card'], twitterContent, true);
            createMetaItem('twitter:title', twitterMeta['twitter:title'], twitterContent, true);
            createMetaItem('twitter:description', twitterMeta['twitter:description'], twitterContent, true);
            createMetaItem('twitter:image', twitterMeta['twitter:image'], twitterContent, true, true); // Mark as image
            createMetaItem('twitter:site', twitterMeta['twitter:site'], twitterContent, false);
             // Add any other found Twitter tags
            for (const [key, value] of Object.entries(twitterMeta)) {
                if (!['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image', 'twitter:site'].includes(key)) {
                     createMetaItem(key, value, twitterContent, false, key.endsWith(':image'));
                }
            }
            twitterSection.appendChild(twitterContent);
            resultsContent.appendChild(twitterSection);

            // 4. All Raw Meta Tags Section (Collapsible)
            if (metadata.length > 0) {
                const details = document.createElement('details');
                const summary = document.createElement('summary');
                summary.textContent = `All Raw Meta Tags (${metadata.length})`;
                details.appendChild(summary);

                const rawListDiv = document.createElement('div');
                rawListDiv.className = 'raw-tag-list';
                metadata.forEach(tag => {
                    const tagDiv = document.createElement('div');
                    tagDiv.className = 'raw-tag';
                    let attributesHTML = '';
                    for (const [key, value] of Object.entries(tag.attributes)) {
                        attributesHTML += `<span class="attr-name">${escapeHtml(key)}</span>: "${escapeHtml(value)}"<br>`;
                    }
                    tagDiv.innerHTML = attributesHTML || '<i>(Empty meta tag)</i>';
                    rawListDiv.appendChild(tagDiv);
                });
                details.appendChild(rawListDiv);
                resultsContent.appendChild(details);
            }
        }

        // --- Event Listener ---
        submitButton.addEventListener('click', async () => {
            const url = urlInput.value.trim();
            if (!url) {
                resultsContainer.style.display = 'block';
                initialMessage.style.display = 'none';
                resultsStatus.className = 'error';
                resultsStatus.textContent = 'Please enter a URL.';
                resultsContent.innerHTML = '';
                return;
            }

            // --- Update UI for Loading State ---
            resultsContainer.style.display = 'block';
            initialMessage.style.display = 'none';
            resultsStatus.className = 'loading';
            resultsStatus.textContent = 'Fetching and extracting metadata...';
            resultsContent.innerHTML = ''; // Clear previous results
            submitButton.disabled = true;
            spinner.style.display = 'inline-block';
            buttonText.textContent = 'Verifying...';

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
                    throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                }

                displayResults(data, url); // Pass URL for display

            } catch (error) {
                console.error('Error:', error);
                resultsStatus.className = 'error';
                resultsStatus.textContent = `Error: ${error.message}`;
                resultsContent.innerHTML = ''; // Clear content area on error
            } finally {
                 // --- Restore UI from Loading State ---
                 submitButton.disabled = false;
                 spinner.style.display = 'none';
                 buttonText.textContent = 'Verify';
            }
        });

        // Optional: Allow pressing Enter in the input field
        urlInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                submitButton.click();
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
    """API endpoint to extract metadata and title from a given URL."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL parameter is missing'}), 400

    url = data['url']
    # Basic validation/fixing for URL
    if not url.startswith(('http://', 'https://')):
        # Check if it looks like a domain before prepending https://
        if '.' in url and not url.startswith('/'):
             url = 'https://' + url
        else:
             return jsonify({'error': f'Invalid URL format: {url}'}), 400


    app.logger.info(f"Attempting to fetch URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MetaVerifierBot/1.1'
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True) # Increased timeout slightly
        response.raise_for_status()

        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
             app.logger.warning(f"URL {url} returned non-HTML content-type: {content_type}")
             # Proceeding anyway, but could return an error here if strict HTML is required

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract <title> tag
        title_tag = soup.find('title')
        page_title = title_tag.string.strip() if title_tag else None

        # Find all <meta> tags
        meta_tags = soup.find_all('meta')
        extracted_data = []
        for tag in meta_tags:
            if tag.attrs:
                extracted_data.append({'attributes': tag.attrs})

        app.logger.info(f"Successfully extracted title and {len(extracted_data)} meta tags from {url}")
        # Return both title and metadata
        return jsonify({'title': page_title, 'metadata': extracted_data})

    except requests.exceptions.Timeout:
        app.logger.error(f"Timeout occurred while fetching {url}")
        return jsonify({'error': f'Request timed out fetching URL: {url}'}), 504
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching URL {url}: {e}")
        error_message = f'Could not fetch or process URL: {url}. Error: {str(e)}'
        status_code = 500
        if isinstance(e, requests.exceptions.ConnectionError):
            error_message = f'Could not connect to URL: {url}. Check the address and network.'
            status_code = 400
        elif isinstance(e, requests.exceptions.HTTPError):
            error_message = f'Server returned error {e.response.status_code} for URL: {url}.'
            status_code = 400 # Treat client/server errors from target as bad request for our service
        elif isinstance(e, requests.exceptions.InvalidURL):
             error_message = f'Invalid URL format provided: {url}'
             status_code = 400

        return jsonify({'error': error_message}), status_code
    except Exception as e:
        app.logger.error(f"An unexpected error occurred processing {url}: {e}", exc_info=True) # Log traceback
        return jsonify({'error': f'An unexpected server error occurred while processing the URL.'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # Remember to set debug=False for production
