# Online Scraper - Setup and Usage Guide

The **Online Scraper** is a tool designed to automatically gather information from the web on a given topic and summarize it using Google AI's Gemini model. It works in conjunction with the **Debate AI** program, providing real-time information to enhance the AI's arguments with up-to-date data and perspectives.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Running the Scraper](#running-the-scraper)
- [Code Overview](#code-overview)
- [Advanced Usage and Customization](#advanced-usage-and-customization)
- [Final Notes](#final-notes)

---

## Overview

### Key Features

- **Automated Information Gathering:** Fetches relevant web pages based on a user-provided topic.
- **Content Extraction:** Extracts and cleans text content from web pages.
- **Summarization:** Uses Google AI's Gemini model to generate concise summaries of the gathered information.
- **Integration with Debate AI:** Provides real-time summaries that can be accessed by the Debate AI program without interruptions.
- **User-Friendly Interface:** Simple GUI built with Tkinter for easy topic input and output visualization.

---

## How It Works

1. **Topic Input:**

   - The user provides a topic through a simple graphical user interface (GUI).

2. **Search:**

   - Utilizes the **Google Custom Search API** to find relevant web pages.
   - **Configuration Required:** Users must set up their own Google Custom Search Engine ID and API Key.

3. **Extract:**

   - Extracts the main textual content from the fetched web pages.
   - Cleans unnecessary elements like scripts, styles, and noscript tags using **BeautifulSoup**.

4. **Summarize:**

   - Sends the aggregated text to **Google AI's Gemini** model for summarization.
   - Gemini analyzes the information, identifies key themes, different perspectives, and generates a concise summary.
   - **Configuration Required:** Users need a Gemini API key and must enable the Gemini API in their Google Cloud project.

5. **Save:**

   - The generated summary is saved to:
     - A text file (`online_scrape_info.txt`)
     - A JSON file (`online_scrape_info.json`)

6. **Live Integration:**

   - The **Debate AI** program can access this summarized information in real-time.
   - This allows the AI debaters to dynamically adapt their arguments based on newly acquired knowledge without needing to pause or restart.

---

## Running the Scraper

### Prerequisites

- **Python 3.x:** Ensure you have Python 3.7 or higher installed.
- **pip:** Python package installer to install dependencies.
- **Virtual Environment (Optional but Recommended):** To isolate dependencies.
- **Google Cloud Account:**
  - Access to Google Custom Search API.
  - Access to Google AI Gemini API.

### Installation Steps

1. **Clone or Download the Main Repository:**

   ```bash
   git clone https://github.com/JoshuaAIHAHA/Debate-AI
   cd /home/your_username/Desktop/Debate Github 
   ```

2. **Activate Your Already Made Virtual Environment (Refer to Debate Setup If Not Made):**

   #### On Unix or MacOS:

   ```bash
   source venv/bin/activate
   ```

   #### On Windows:

   ```bash
   venv\Scripts\activate
   ```

3. **Install Dependencies (Should Already Be Done):**

   ```bash
   pip install -r requirements.txt
   ```

   **Requirements include:**

   - `requests`
   - `beautifulsoup4`
   - `tkinter` (usually included with Python)
   - `google-generativeai` (for Gemini integration)

4. **Obtain and Configure API Keys:**

   - **Google Custom Search API:**
     - Create a Custom Search Engine and obtain the **Search Engine ID**.
     - Get an API key from the [Google Developers Console](https://console.developers.google.com/).
   - **Google AI Gemini API:**
     - Sign up and enable access to the Gemini API.
     - Obtain your Gemini API key.

5. **Configure API Keys in the Script:**

   Open the `Online_Scraper.py` file and replace the placeholder strings with your actual API keys:

   ```python
   # Google Custom Search API credentials
   GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
   SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"  # Replace with your actual Search Engine ID

   # Gemini API Configuration
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual Gemini API key
   genai.configure(api_key=GEMINI_API_KEY)
   ```

   **Important:** Keep your API keys secure and do not share them publicly.

### Running the Scraper

Run the scraper script using the command line:

```bash
python Online_Scraper.py
```

### Using the GUI

1. **Launch the Application:**

   - Upon running the script, a GUI window will appear titled "Web Scrape App."

2. **Enter a Topic:**

   - In the input field labeled "Enter Topic to Scrape," type the topic you want to gather information about.

3. **Start Scraping:**

   - Click the "Scrape and Summarize" button.
   - The output window will display the progress:
     - Fetching URLs
     - Extracting content from each URL
     - Generating the summary

4. **View the Summary:**

   - Once completed, the summary will be displayed in the output window.
   - The summary is also saved to `online_scrape_info.txt` and `online_scrape_info.json` in the script's directory.
   - AI debaters will use it automatically without pausing or restart.

5. **Clear Output (Optional):**

   - Delete the text inside of online_scrape_info.txt.

---

## Code Overview

The script is organized into several key functions:

### 1. `fetch_search_results(topic, num_results=10)`

- **Purpose:** Fetches URLs related to the provided topic using the Google Custom Search API.
- **Parameters:**
  - `topic`: The topic to search for.
  - `num_results`: Number of search results to fetch (default is 10).
- **Returns:** A list of URLs.

### 2. `extract_content(url)`

- **Purpose:** Extracts and cleans textual content from a given webpage.
- **Parameters:**
  - `url`: The URL of the webpage to extract content from.
- **Returns:** A string containing the extracted text.

### 3. `generate_summary_with_gemini(text, max_context_length=1000000)`

- **Purpose:** Sends the extracted text to Google AI's Gemini model to generate a summary.
- **Parameters:**
  - `text`: The combined text content from all scraped webpages.
  - `max_context_length`: The maximum allowed length of the text chunk sent to Gemini (adjust if necessary).
- **Logic:**
  - If the text exceeds a certain length, it divides it into chunks to fit within Gemini's context window.
  - Sends each chunk to Gemini and combines the summaries.

### 4. `save_summary(topic, summary)`

- **Purpose:** Saves the generated summary to `online_scrape_info.txt` and `online_scrape_info.json`.
- **Parameters:**
  - `topic`: The topic that was processed.
  - `summary`: The summary text to save.

### 5. `process_topic(topic, output_text_widget)`

- **Purpose:** Orchestrates the entire scraping and summarization process.
- **Parameters:**
  - `topic`: The topic to process.
  - `output_text_widget`: The Tkinter Text widget to display output messages.

### 6. GUI Components

- **`create_gui()`**: Sets up the Tkinter GUI, including input fields, buttons, and the output text area.
- **Event Handlers:** Linked to buttons for starting the process and clearing output.

---

## Advanced Usage and Customization

### Google Custom Search Parameters

- **Refining Search Results:**
  - Modify the `fetch_search_results` function to add parameters like language (`lr`), site restrictions (`siteSearch`), or filtering options.

- **Example: Limiting to English Results**

  ```python
  params = {
      'key': GOOGLE_API_KEY,
      'cx': SEARCH_ENGINE_ID,
      'q': topic,
      'num': num_results,
      'lr': 'lang_en'  # Adds language restriction to English
  }
  ```

### Gemini Prompt Engineering

- **Customizing the Summary Prompt:**
  - Modify the prompt sent to Gemini within the `generate_summary_with_gemini` function to influence the summarization style.

- **Example: Changing the Summarization Focus**

  ```python
  prompt = f"""
  Summarize the following text focusing on the technological implications and future trends related to the topic.

  {text}
  """
  ```

### Error Handling Enhancements

- **Network Errors:** Implement retries with exponential backoff in case of transient network issues.
- **Invalid URLs:** Skip URLs that lead to HTTP errors and log them for review.

### Content Extraction Improvements

- **Advanced Parsing:**
  - For more complex websites, consider using libraries like `newspaper3k` or `readability-lxml` to extract the main article content.

### Integration with Debate AI

- **Real-time Updates:**
  - Since the summary is saved to `online_scrape_info.txt`, ensure the Debate AI program reads this file at appropriate intervals or when needed.

- **Custom Data Exchange:**
  - Implement inter-process communication if needed for more dynamic integration.

## Final Notes

- **API Key Security:** Ensure that your API keys are kept confidential. Do not commit them to public repositories or share them with unauthorized individuals.
- **Rate Limits and Costs:**
  - Be aware of any rate limits or costs associated with the APIs.
  - Google Custom Search and Gemini APIs may incur charges based on usage.
- **Compliance:**
  - Ensure compliance with Google's terms of service when using their APIs.
  - Respect website robots.txt files and scraping policies.
- **Further Enhancements:**
  - Implement caching to avoid redundant requests.
  - Add support for multilingual searches and summarization.
  - Enhance the GUI with additional features like progress bars or status indicators.

By following this guide, you should be able to set up and run the Online Scraper successfully. This tool will enhance the capabilities of the Debate AI program by supplying it with up-to-date information, allowing for more informed and dynamic debates.
