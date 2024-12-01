import os
import sys
import json
import logging
import requests
from tkinter import Tk, Label, Entry, Button, Text, END, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, Frame, messagebox
from bs4 import BeautifulSoup
import google.generativeai as genai

# ===========================
# Configuration and Constants
# ===========================
# Google Custom Search API credentials
GOOGLE_API_KEY = "your-google-api-key"  # Replace with your actual API key
SEARCH_ENGINE_ID = "your-search-engine-id"  # Replace with your actual Search Engine ID

# Gemini API Configuration
GEMINI_API_KEY = "your-google-api-key"  # Replace with your actual Gemini API key
genai.configure(api_key="your-google-api-key")


# Setup logging
logging.basicConfig(
    filename='web_scrape_app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# ===========================
# Utility Functions
# ===========================

def fetch_search_results(topic, num_results=10):
    """
    Fetch search results from Google Custom Search API.

    Args:
        topic (str): The topic to search for.
        num_results (int): Number of search results to fetch.

    Returns:
        list: List of URLs from the search results.
    """
    logging.info(f"Fetching search results for topic: {topic}")
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': topic,
        'num': num_results
    }
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        urls = [item['link'] for item in results.get('items', [])]
        logging.info(f"Fetched {len(urls)} URLs.")
        return urls
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching search results: {e}")
        messagebox.showerror("Error", f"Failed to fetch search results: {e}")
        return []

def extract_content(url):
    """
    Extract textual content from a webpage.

    Args:
        url (str): The URL of the webpage.

    Returns:
        str: The extracted textual content.
    """
    logging.info(f"Extracting content from URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'noscript']):
            script_or_style.decompose()

        # Get text
        text = soup.get_text(separator=' ', strip=True)
        logging.info(f"Extracted content length: {len(text)} characters.")
        return text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error extracting content from {url}: {e}")
        return ""



def generate_summary_with_gemini(text, max_context_length=1000000):  # Adjust max_context_length if needed
    """
    Generate a summary using Gemini's API with conditional chunking.
    """
    logging.info("Generating summary using Gemini API.")
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        summary = ""

        if len(text) > max_context_length * 0.8:  # Check if chunking is needed
            chunk_size = int(max_context_length * 0.7)  # Use a large chunk size
            logging.info(f"Chunking text with chunk size: {chunk_size}")
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                # Optimized prompt
                prompt = f"""
                Summarize the following text, focusing on the key arguments and evidence related to the nature of consciousness and its potential to exist beyond the physical body. 

                {chunk} 
                """
                response = model.generate_content(prompt)
                if response.text:
                    summary += response.text + " "
                else:
                    raise ValueError("No summary returned from Gemini API for chunk.")
        else:
            # Optimized prompt
            prompt = f"""
            Please analyze the following text from multiple sources about the topic. 
            Identify the key themes and common points raised by these different sources. 
            Analyze how these sources support or contradict each other.
            Draw connections between the findings of different reports.

            Present a balanced view that considers the complexities of the issue.

            Finally, provide a concise and insightful summary of the overall situation.
            Conclude with a summary of the different perspectives and viewpoints on the topic.

            {text} 
            """
            response = model.generate_content(prompt)
            if response.text:
                summary = response.text
            else:
                raise ValueError("No summary returned from Gemini API.")

        logging.info("Summary generated successfully.")
        return summary
    except Exception as e:
        logging.error(f"Error in Gemini API: {e}")
        messagebox.showerror("Error", f"Failed to generate summary: {e}")
        return "Summary could not be generated due to an API error."

def save_summary(topic, summary):
    """
    Save the summary to a file called "online_scrape_info.txt", 
    overwriting the file if it already exists. Also saves to a JSON file.
    """
    logging.info("Saving summary to files.")
    try:
        # Save to TXT (Overwrite mode 'w')
        txt_filename = "online_scrape_info.txt" 
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            txt_file.write(summary)
        logging.info(f"Summary saved to {txt_filename}.")

        # ... (rest of your JSON saving logic) ...

    except Exception as e:
        logging.error(f"Error saving summary: {e}")
        messagebox.showerror("Error", f"Failed to save summary: {e}")

        # Save JSON (Overwrite mode 'w')
        data = {
            'topic': topic,
            'summary': summary
        }
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logging.info(f"Summary saved to {json_filename}.")

        messagebox.showinfo("Success", f"Summary saved to '{txt_filename}' and '{json_filename}'.")
    except Exception as e:
        logging.error(f"Error saving summary: {e}")
        messagebox.showerror("Error", f"Failed to save summary: {e}")

def process_topic(topic, output_text_widget):
    """
    Process the input topic: fetch, extract, summarize, and save.

    Args:
        topic (str): The topic to process.
        output_text_widget (Text): The Tkinter Text widget to display output.

    Returns:
        None
    """
    logging.info(f"Processing topic: {topic}")
    output_text_widget.delete(1.0, END)
    output_text_widget.insert(END, "Fetching search results...\n")
    
    urls = fetch_search_results(topic)
    if not urls:
        output_text_widget.insert(END, "No results found.\n")
        return
    
    combined_content = ""
    for idx, url in enumerate(urls, start=1):
        output_text_widget.insert(END, f"Extracting content from URL {idx}: {url}\n")
        content = extract_content(url)
        if content:
            combined_content += content + "\n"
        else:
            output_text_widget.insert(END, f"Failed to extract content from {url}.\n")
    
    if not combined_content.strip():
        output_text_widget.insert(END, "Failed to extract content from all URLs.\n")
        return
    
    output_text_widget.insert(END, "Generating summary...\n")
    summary = generate_summary_with_gemini(combined_content)
    output_text_widget.insert(END, f"\nSummary:\n{summary}\n")
    
    if summary and summary.startswith("Summary could not"):
        # An error occurred during summary generation
        return
    
    save_summary(topic, summary)

# ===========================
# GUI Implementation
# ===========================

def create_gui():
    """
    Create the GUI using Tkinter.

    Returns:
        None
    """
    logging.info("Initializing GUI.")
    root = Tk()
    root.title("Web Scrape App")
    root.geometry("800x600")

    # Topic Label
    topic_label = Label(root, text="Enter Topic to Scrape:", font=("Arial", 14))
    topic_label.pack(pady=10)

    # Topic Entry
    topic_entry = Entry(root, width=50, font=("Arial", 12))
    topic_entry.pack(pady=5)

    # Scrape Button
    scrape_button = Button(
        root, 
        text="Scrape and Summarize", 
        font=("Arial", 12), 
        command=lambda: process_topic(topic_entry.get().strip(), output_text)
    )
    scrape_button.pack(pady=10)

    # Output Text with Scrollbar
    output_frame = Frame(root)
    output_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    scrollbar = Scrollbar(output_frame, orient=VERTICAL)
    output_text = Text(output_frame, wrap='word', yscrollcommand=scrollbar.set, font=("Arial", 12))
    scrollbar.config(command=output_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    output_text.pack(side=LEFT, fill=BOTH, expand=True)

    # Clear Button
    clear_button = Button(
        root, 
        text="Clear Output", 
        font=("Arial", 12), 
        command=lambda: output_text.delete(1.0, END)
    )
    clear_button.pack(pady=5)

    root.mainloop()

# ===========================
# Main Execution
# ===========================

def main():
    """
    Main function to run the GUI application.

    Returns:
        None
    """
    create_gui()

if __name__ == "__main__":
    main()
