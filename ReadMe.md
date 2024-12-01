# Debate AI: Advanced AI Debate Platform

## 🤖 Project Overview

**Debate AI** is an innovative platform that generates dynamic, real-time debates using advanced language models, intelligent conversation management, and real-time information gathering. By combining cutting-edge AI technologies, Debate AI creates engaging, informative, and adaptive dialogues on a wide range of topics.

---

## 🌟 Key Features

### Intelligent AI Debaters

- **Multiple AI Personalities:**
  - **Gemini:** Analytical and data-driven AI with logical reasoning.
  - **o1-mini:** Creative and intuitive AI with imaginative arguments.
  - **Bard:** Unpredictable wildcard AI that brings chaos and spontaneity.

### Adaptive Debate Mechanics

- **Customizable Debate Parameters:**
  - Adjust response length, style, focus, directness, assertiveness, and complexity.
- **Real-time Topic Evolution:**
  - Debates naturally evolve with the introduction of related subtopics.
- **Adjustable AI Personalities:**
  - Fine-tune personalities with sliders for assertiveness, directness, and humor.
- **Sentiment and Context Tracking:**
  - Sentiment analysis with emotion detection and visualizations.

### Dynamic Information Gathering

- **Online Scraper Integration:**
  - Automatic web research on debate topics.
  - Real-time information retrieval using Google Custom Search API.
  - Instant topic summarization using Google AI's Gemini model.

### Flexible Text-to-Speech (TTS)

- **Multiple TTS Engine Support:**
  - **Azure Cognitive Services** (Default)
  - **Google Cloud TTS**
  - **Amazon Polly**
  - **ElevenLabs**
  - **Offline `pyttsx3` Option**

---

## 🚀 How It Works

### 1. Topic Selection

- User inputs a debate topic or selects from predefined topics.
- Online scraper gathers current information on the topic.
- AI models receive context briefings, including external information.

### 2. Personality Generation

- Unique AI personalities are created for each debate.
- Traits are dynamically assigned, including debate styles and key characteristics.
- Individual approaches to argumentation are established.

### 3. Debate Initiation

- AIs generate responses based on personalities and debate parameters.
- Continuous exploration of the topic with natural evolution.
- Real-time integration of newly scraped information without restarting the debate.

### 4. Multimedia Output

- Text-based dialogue displayed in an interactive GUI.
- Optional speech synthesis using selected TTS engines.
- Sentiment visualization with emotion emojis and indicators.

---

## 🛠 Technical Components

### Core Technologies

- **Python 3.7+**
- **OpenAI GPT Models** (e.g., GPT and o1)
- **Google AI Gemini Model**
- **BeautifulSoup** (Web Scraping)
- **Tkinter** (Graphical User Interface)
- **SpaCy** (Natural Language Processing)
- **PyGame** and **SimpleAudio** (Sound and TTS)

### API Dependencies

- **OpenAI API**
- **Google Custom Search API**
- **Google AI Gemini API**
- **Azure Cognitive Services Speech SDK**
- **Optional TTS APIs:**
  - **Amazon Polly (AWS)**
  - **ElevenLabs**
  - **Google Cloud TTS**

---

## 📦 Installation

### Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **Virtual Environment** (Recommended)

### Setup Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/JoshuaAIHAHA/Debate-AI
   ```

2. **Create a Virtual Environment**

  cd The Debate Github Folder
   For example 
   ```bash
   cd /home/your-username/Desktop/test/Debate-AI/Debate Github
   ```
  
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On **Unix/MacOS**:

     ```bash
     source venv/bin/activate
     ```

   - On **Windows**:

     ```bash
     venv\Scripts\activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install SpaCy Language Model**

   ```bash
   python -m spacy download en_core_web_sm
   ```

6. **Configure API Keys**

   - Edit `config.py` with your API credentials (see [Configuration](#-configuration) below).

---

## 🔧 Configuration

### API Key Setup

Obtain API keys for the following services:

- **OpenAI**
  - Sign up at [OpenAI](https://platform.openai.com/).
  - Obtain your API key from the [API Keys](https://platform.openai.com/account/api-keys) section.
- **Google Custom Search**
  - Create a Custom Search Engine at [Google Custom Search](https://cse.google.com/).
  - Obtain your **Search Engine ID** and **API Key**.
- **Google AI Gemini**
  - Enable access to the Gemini API in your Google Cloud project.
  - Obtain your API key from the [Google Cloud Console](https://console.cloud.google.com/).
- **Azure Cognitive Services** (For TTS)
  - Sign up at [Azure Portal](https://portal.azure.com/).
  - Create a **Speech Service** resource.
  - Obtain your **Subscription Key** and **Region**.
- **Optional TTS Services:**
  - **Amazon Polly (AWS)**
  - **ElevenLabs**
  - **Google Cloud TTS**

### Setting Up API Keys

1. **Create a `config.py` File**

   In the root directory of the project, create a file named `config.py`.

2. **Add Your API Credentials to debate.py, Online_scraper.py and pre_debate_chat.py**

   ```python
   # OpenAI API Key
   OPENAI_API_KEY = 'your-openai-api-key'

   # Google Custom Search API Key and Search Engine ID
   GOOGLE_API_KEY = 'your-google-api-key'
   SEARCH_ENGINE_ID = 'your-search-engine-id'

   # Google AI Gemini API Key
   GEMINI_API_KEY = 'your-gemini-api-key'

   # Azure Cognitive Services API Key and Region
   -Line 950 and 951
   AZURE_SUBSCRIPTION_KEY = 'your-azure-subscription-key'
   AZURE_REGION = 'your-azure-region'
   speech_config.endpoint = "your_azure_endpoint" 
   For eg "https://eastus.api.cognitive.microsoft.com/sts/v1.0"

   # Optional: Amazon Polly (AWS) Credentials
   AWS_ACCESS_KEY_ID = 'your-aws-access-key-id'
   AWS_SECRET_ACCESS_KEY = 'your-aws-secret-access-key'
   AWS_REGION_NAME = 'your-aws-region-name'

   # Optional: ElevenLabs API Key 
   -Set up for azure but there is a guide for all other TTS providers even local
   ELEVENLABS_API_KEY = 'your-elevenlabs-api-key'
   ```

   **Note:** Dont share you API key with anyone!

---

## 📝 Running the Program

1. **Ensure your virtual environment is activated.**

2. **Run the Main Script**

   ```bash
   python debate_ai.py
   ```

3. **Using the GUI**

   - The Debate AI interface will launch.
   - You can select topics, adjust debate parameters, and control the debate flow.

4. **Optional: Run the Online Scraper Separately**

   - Open a new terminal window.
   - Run the online scraper to gather information on a topic:

     ```bash
     python online_scraper.py
     ```

---

## 💡 Potential Use Cases

- **Educational Platforms:** Enhance learning with AI-driven debates on academic topics.
- **Debate Training:** Practice and improve debating skills with AI opponents.
- **AI Research:** Analyze AI conversational behaviors and language models.
- **Content Generation:** Create engaging dialogue content for media and storytelling.
- **Interactive Learning Tools:** Develop applications that foster critical thinking and discussion.
- **Advanced Debate Analytics:** Provide in-depth analysis of debate performance and content.

---

## 🌐 Customization Opportunities

- **Add New AI Personalities:**
  - Define new AI characters with unique traits and debate styles.
  - Modify the `ai_personalities` dictionary in `debate_ai.py`.
- **Implement Additional TTS Engines:**
  - Integrate other text-to-speech services.
  - Update the TTS functions in `debate_ai.py`.
- **Enhance Web Scraping Capabilities:**
  - Improve content extraction methods.
  - Adjust the `online_scraper.py` script for more advanced scraping.
- **Create Custom Debate Rulesets:**
  - Tailor the debate flow and rules to specific needs.
  - Modify the `run_conversation` method in `debate_ai.py`.
- **Develop Advanced Sentiment Analysis:**
  - Enhance emotion detection and response adaptability.
  - Integrate more sophisticated NLP libraries or models.

---

## 🚧 Future Roadmap

- **Multilingual Support:** Enable debates in multiple languages.
- **Enhanced Machine Learning Models:** Integrate more advanced or specialized AI models.
- **User-Created AI Personalities Profiles:** Allow users to design and train their own AI debaters.
- **Collaborative Debate Modes:** Introduce multiplayer features for human-AI or AI-AI debates.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps to contribute:

### Development Setup

1. **Fork the Repository**

   Click the "Fork" button at the top right corner of the repository page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/DebateAI.git
   cd DebateAI
   ```

3. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes**

   Write your code and commit your changes with clear messages.

   ```bash
   git add .
   git commit -m "Add your detailed commit message here"
   ```

5. **Push to Your Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Submit a Pull Request**

   - Go to the original repository.
   - Click on "Pull Requests" and then "New Pull Request".
   - Select your branch and submit.

### Contributing Guidelines

- Ensure code follows the project's style and conventions.
- Write clear commit messages and documentation.
- Test your changes thoroughly before submitting.
- Be responsive to feedback during the review process.

---

## 📄 License

## 📄 License

This project is licensed under the [MIT License](LICENSE.md).

While this project is open source under the MIT License, please consider providing attribution if you use or modify this code.

---

## 📞 Contact & Support

- **Project Maintainer:** [Joshua G] 
- **Email:** [Joshuag.contact@gmail.com] 
- **Issues:** [GitHub Issues Page](https://github.com/JoshuaAIHAHA/Debate-AI/issues)

---
## ⚠️ Disclaimer

Debate AI is an experimental AI platform. Users should engage responsibly and be aware of potential AI limitations and biases. The generated content may not always be accurate or appropriate. Use discretion when interacting with the system.

---

*Powered by cutting-edge AI technologies 🚀*

This project was built from the ground up with a lot of passion and learning along the way! It's been an exciting journey of exploration and discovery.

---
