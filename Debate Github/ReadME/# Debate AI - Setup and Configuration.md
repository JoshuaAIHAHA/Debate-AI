# Debate AI - Setup and Configuration Guide

Welcome to the **Debate AI** program! This guide provides detailed instructions on setting up, running, and customizing the Debate AI platform. You'll learn how to install the necessary dependencies, configure API keys, understand the code structure, and explore customization options to tailor the program to your needs.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [API Keys and Configuration](#api-keys-and-configuration)
- [Running the Program](#running-the-program)
- [Customization Options](#customization-options)
- [Exploring the Code](#exploring-the-code)
  - [Core Classes and Functions](#core-classes-and-functions)
- [Modification and Extension](#modification-and-extension)

---

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.7 or higher:** This program requires Python 3.7 or a later version.
- **pip:** The Python package installer (`pip`) is needed to install the necessary dependencies.
- **Virtual Environment (Optional but Recommended):** It's recommended to use a virtual environment to isolate the project's dependencies from your system's Python installation.
- **Terminal Emulator:** You'll need a terminal emulator (Command Prompt, PowerShell, Terminal, etc.) to execute commands and run the program.
- **Text Editor or IDE:** A text editor (e.g., VS Code, Sublime Text) or an Integrated Development Environment (IDE) like PyCharm to modify the code and configuration files.

---

## Installation Steps

Follow these steps to set up the Debate AI program on your machine.

### 1. Clone the Repository

First, clone the Debate AI repository from GitHub:

```bash
git clone https://github.com/yourusername/DebateAI.git
```

Replace `https://github.com/yourusername/DebateAI.git` with the actual repository URL.

---

### 2. Navigate to the Project Directory

Change your current directory to the cloned repository:

```bash
cd DebateAI
```

---

### 3. Create and Activate a Virtual Environment

**Creating a virtual environment is optional but highly recommended.**

#### On Unix or MacOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 4. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

If you encounter any issues, ensure that `pip` is up to date:

```bash
pip install --upgrade pip
```

---

### 5. Install spaCy Language Model

The program uses spaCy for natural language processing. Download the English language model:

```bash
python -m spacy download en_core_web_sm
```

---

## API Keys and Configuration

The Debate AI program relies on external APIs for AI response generation and text-to-speech (TTS) functionalities. You'll need to obtain and configure the following API keys:

### 1. OpenAI API Key

- **Purpose:** Generates AI responses using OpenAI's GPT models.
- **Instructions:**
  - Create an account or sign in to [OpenAI](https://platform.openai.com/).
  - Navigate to the [API Keys](https://platform.openai.com/account/api-keys) section.
  - Click on **Create new secret key** and copy the key.

**Configuration:**

In the `debate_ai.py` file (the main script), find and set your OpenAI API key:

```python
# Configure OpenAI API Key
openai.api_key = 'YOUR_OPENAI_API_KEY'
```

---

### 2. Azure Cognitive Services (for TTS)

- **Purpose:** Provides text-to-speech capabilities using Azure's TTS services.
- **Instructions:**
  - Sign up for an Azure account at [Azure Portal](https://portal.azure.com/).
  - Create a new **Speech Service** resource.
  - Navigate to the **Keys and Endpoint** section to obtain your **Subscription Key** and **Region**.

**Configuration:**

In the `debate_ai.py` file, locate the TTS configuration section and set your Azure credentials:

```python
# Configure Azure Speech Service
speech_config = speechsdk.SpeechConfig(
    subscription="YOUR_AZURE_SUBSCRIPTION_KEY",
    region="YOUR_AZURE_SERVICE_REGION"
)
```

---

### 3. ElevenLabs API Key (Optional)

- **Purpose:** Provides an alternative TTS engine with high-quality voices.
- **Instructions:**
  - Sign up at [ElevenLabs](https://elevenlabs.io/).
  - Navigate to your profile to find your API key.

**Configuration:**

In the `debate_ai.py` file, configure the ElevenLabs API key:

```python
# Configure ElevenLabs API Key
elevenlabs_api_key = "YOUR_ELEVENLABS_API_KEY"
```

**Note:** You'll also need to install the `elevenlabs` Python package if you plan to use it:

```bash
pip install elevenlabs
```

---

## Running the Program

Ensure your virtual environment is activated (if you set one up). Run the main script:

```bash
python debate_ai.py
```

This will launch the graphical user interface (GUI) of the Debate AI platform.

---

## Customization Options

The Debate AI program offers several customization options to enhance your experience.

### 1. AI Personalities

The platform features three AI personalities:

- **Gemini:** An analytical and data-driven AI.
- **o1-mini:** A creative and intuitive AI.
- **Bard:** A wildcard AI with unpredictable behavior.

You can customize their attributes, such as assertiveness, directness, and humor, through the GUI sliders.

### 2. Debate Settings

Adjust various debate parameters:

- **Response Length:** Control how verbose the AI responses are.
- **Style and Focus:** Change the tone and focus of the debate (e.g., casual, formal, informative).
- **Directness and Assertiveness:** Influence how direct and assertive the AIs are.
- **Topic Evolution:** Set how likely the debate topic will evolve or shift.
- **Response Delay:** Add a delay between AI responses for a more natural interaction.

### 3. Text-to-Speech Options

The program supports multiple TTS engines:

- **Azure Cognitive Services (Default)**
- **Google Cloud TTS**
- **Amazon Polly**
- **ElevenLabs**
- **pyttsx3 (Offline TTS)**

To change the TTS engine, modify the `display_message` function in the `debate_ai.py` file. For example, to use ElevenLabs:

```python
# Comment out the Azure TTS call
# self.speak_text_azure(message, ai_model)

# Add the ElevenLabs TTS call
self.speak_text_elevenlabs(message, ai_model)
```

Ensure you have installed any necessary packages and configured the API keys.

---

## Exploring the Code

Understanding the code structure will help you customize and extend the program.

### Core Classes and Functions

#### `AdvancedAIDebatePlatform` Class

This is the main class that encapsulates the entire functionality of the debate platform.

- **Initialization (`__init__`):** Sets up the GUI, AI personalities, debate settings, and sound configurations.
- **`create_widgets`:** Creates all GUI elements, including buttons, sliders, and text fields.
- **`initialize_debate_personalities`:** Generates unique personalities for each AI at the start of a new debate.
- **`generate_unique_personality`:** Combines predefined traits with random elements to create diverse AI personalities.
- **`get_ai_response`:** Constructs a prompt based on the current context and personality traits, then sends it to the AI model (OpenAI or Gemini) to generate a response.
- **`display_message`:** Displays messages in the chat window with appropriate formatting and sentiment analysis.
- **`speak_text_azure`:** Handles text-to-speech functionality using Azure Cognitive Services.
- **`start_conversation`, `pause_conversation`, `continue_conversation`:** Control the flow of the debate.
- **`save_conversation`:** Allows users to save the conversation history to a JSON file.
- **Other Functions:** Include handling user guidance, voice input, voting, and personality updates.

---

## Modification and Extension

The Debate AI program is modular and extensible. Here are some ways you can modify and enhance it:

### 1. Adding New AI Personalities

You can introduce new AI personalities with custom traits and debate styles. Update the `ai_personalities` dictionary and implement any unique behaviors in the `generate_unique_personality` function.

### 2. Integrating Other Language Models

Experiment with integrating additional language models or APIs to generate AI responses.

### 3. Enhancing TTS Capabilities

Add support for other TTS engines or tweak existing ones to improve voice quality and responsiveness.

### 4. Improving the GUI

Enhance the user interface by adding new features, such as:

- **Real-time Sentiment Analysis:** Display sentiments visually.
- **Advanced Visualization:** Integrate charts or graphs to represent debate dynamics.
- **User Authentication:** Allow users to save preferences and session histories.

### 5. Expanding Debate Topics

Add more debate topics or allow dynamic topic generation based on current events or user input.

### 6. Implementing Multiplayer Mode

Allow multiple users to participate in the debate, either locally or over a network.

---

## Code Snippets and Examples

Below are some code snippets to guide you through common modifications.

### Changing the TTS Engine to ElevenLabs

**Install the ElevenLabs Package:**

```bash
pip install elevenlabs
```

**Configure the API Key in `debate_ai.py`:**

```python
# Add this at the top of your file
import elevenlabs

# Set your ElevenLabs API key
elevenlabs_api_key = "YOUR_ELEVENLABS_API_KEY"
```

**Modify the `display_message` Function:**

```python
def display_message(self, speaker, message):
    # Existing code...
    if self.tts_enabled and speaker not in ["System", "Interrupt"]:
        ai_model = speaker.lower()
        # Comment out the Azure TTS call
        # self.speak_text_azure(message, ai_model)
        
        # Add the ElevenLabs TTS call
        self.speak_text_elevenlabs(message, ai_model)
```

**Implement the `speak_text_elevenlabs` Function:**

```python
def speak_text_elevenlabs(self, text, ai_model):
    try:
        # Configure ElevenLabs
        elevenlabs.set_api_key(elevenlabs_api_key)
        
        # Map AI models to voices
        voice_map = {
            "gemini": "Your Gemini Voice",
            "o1-mini": "Your o1-mini Voice",
            "bard": "Your Bard Voice"
        }
        voice_name = voice_map.get(ai_model.lower(), "Default Voice")
        
        # Generate and play the audio
        audio = elevenlabs.generate(text=text, voice=voice_name)
        elevenlabs.play(audio)
    except Exception as e:
        print(f"Error in speak_text_elevenlabs: {e}")
```

**Note:** Replace `"Your Gemini Voice"`, `"Your o1-mini Voice"`, and `"Your Bard Voice"` with the actual voice names from your ElevenLabs account.

---

### Adding a New AI Personality

**Update the `ai_personalities` Dictionary:**

```python
self.ai_personalities = {
    # Existing personalities...
    "NewAI": {
        "name": "NewAI",
        "base_personality": "describe the base personality",
        "debate_styles": ["style1", "style2"],
        "key_traits": ["trait1", "trait2"],
        "additional_traits": ["additional_trait1", "additional_trait2"],
        "expertise_areas": ["area1", "area2"],
        "argument_preferences": ["preference1", "preference2"],
        "weaknesses": ["weakness1", "weakness2"],
        "signature": "— NewAI, Your Description"
    }
}
```

**Implement Unique Behaviors in `generate_unique_personality`:**

```python
elif ai_name == "NewAI":
    unique_personality["special_attribute"] = random.choice([
        "special_behavior1",
        "special_behavior2"
    ])
    # Add any additional unique attributes or logic
```

**Incorporate the New AI into the Debate Flow:**

- Update the lists where AI names are iterated, e.g., `["Gemini", "o1-mini", "Bard", "NewAI"]`.
- Adjust the GUI elements to include controls for the new AI.

---

## Final Tips

- **Keep API Keys Secure:** Never commit your API keys to a public repository. Use environment variables or a configuration file excluded from version control.
- **Test Incrementally:** After making changes, test the program incrementally to catch and fix errors early.
- **Explore Documentation:** Refer to the official documentation for libraries and APIs used in this project for advanced features and best practices.
- **Engage with the Community:** Consider sharing your modifications and seeking feedback from the developer community.

---

By following this guide and exploring the codebase, you can harness the full potential of the Debate AI platform and tailor it to your specific interests or research goals. Happy coding!