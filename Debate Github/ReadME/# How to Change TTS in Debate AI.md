# How to Change TTS in Debate AI

The **Debate AI** program supports various text-to-speech (TTS) engines, allowing you to customize the voices and speaking styles of the AI debaters. By default, the program is configured to use **Azure Cognitive Services** for TTS. However, you can easily switch to other TTS providers or even use offline TTS.

This guide provides step-by-step instructions and code examples to help you change the TTS settings.

## Available TTS Options

The program supports the following TTS engines:

- **Azure Cognitive Services (default)**
- **Google Cloud TTS**
- **Amazon Polly**
- **ElevenLabs**
- **pyttsx3 (offline TTS)**

## Changing the TTS Configuration

Follow these steps to change the TTS engine used in the program:

1. **Identify the TTS Engine:** Decide which TTS engine you want to use from the list above.
2. **Modify the Code:** Open the `debate_azure_scrape.py` file in a text editor.
3. **Locate the TTS Function Call:** Find the `display_message` function. Inside this function, locate the following line:

   ```python
   self.speak_text_azure(message, ai_model)
   ```

   This line calls the function that uses Azure TTS to generate speech.

4. **Comment Out the Azure TTS Call:** Comment out the line mentioned above by adding a `#` at the beginning:

   ```python
   # self.speak_text_azure(message, ai_model)
   ```

5. **Add the New TTS Function Call:** Below the commented-out line, add a new line to call the appropriate TTS function based on your chosen engine. See the "Code Examples" section for specific function calls and implementations.
6. **(Optional) Install Necessary Packages:** If you're using a TTS engine other than Azure or pyttsx3, you might need to install additional packages. For example:

   - Google Cloud TTS: `pip install google-cloud-texttospeech`
   - Amazon Polly: `pip install boto3`
   - ElevenLabs: `pip install elevenlabs`
   - pyttsx3: `pip install pyttsx3`

## Code Examples

Below are code examples for each TTS engine. Remember to import any necessary modules at the top of your Python file.

### Google Cloud TTS

```python
# Add these imports at the top of your file
from google.cloud import texttospeech
from playsound import playsound  # You may need to install this package

# ... (Inside the display_message function) ...
# Replace the Azure TTS call with this:
self.speak_text_google(message, ai_model)

# Add this function to your class
def speak_text_google(self, text, ai_model):
    """
    Synthesizes speech from the input string of text using Google Cloud Text-to-Speech.
    """
    try:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Save the response to a file
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

        # Play the audio file
        playsound("output.mp3")

    except Exception as e:
        print(f"Error in speak_text_google: {e}")
```

### Amazon Polly

```python
# Add these imports at the top of your file
import boto3
from contextlib import closing
from playsound import playsound  # You may need to install this package

# ... (Inside the display_message function) ...
# Replace the Azure TTS call with this:
self.speak_text_polly(message, ai_model)

# Add this function to your class
def speak_text_polly(self, text, ai_model):
    """
    Synthesizes speech from the input string of text using Amazon Polly.
    """
    try:
        # Create a Polly client
        polly_client = boto3.Session(
            aws_access_key_id="YOUR_AWS_ACCESS_KEY_ID",
            aws_secret_access_key="YOUR_AWS_SECRET_ACCESS_KEY",
            region_name="YOUR_AWS_REGION"
        ).client("polly")

        # Request speech synthesis
        response = polly_client.synthesize_speech(
            VoiceId="Joanna",  # Choose your desired voice
            OutputFormat="mp3",
            Text=text
        )

        # Access the audio stream from the response
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output_file = "speech.mp3"

                # Save the audio content to a file
                with open(output_file, "wb") as file:
                    file.write(stream.read())

            # Play the audio file
            playsound(output_file)
        else:
            print("Could not stream audio")
    except Exception as e:
        print(f"Error in speak_text_polly: {e}")
```

### ElevenLabs

```python
# Add these imports at the top of your file
import elevenlabs
from elevenlabs import generate, play

# ... (Inside the display_message function) ...
# Replace the Azure TTS call with this:
self.speak_text_elevenlabs(message, ai_model)

# Add this function to your class
def speak_text_elevenlabs(self, text, ai_model):
    """
    Synthesizes speech from the input string of text using ElevenLabs.
    """
    try:
        # Set your API key
        elevenlabs.set_api_key("YOUR_ELEVENLABS_API_KEY")

        # Generate and play the audio
        audio = generate(
            text=text,
            voice="YOUR_VOICE_NAME",
            model="eleven_monolingual_v1"
        )
        play(audio)

    except Exception as e:
        print(f"Error in speak_text_elevenlabs: {e}")
```

### pyttsx3 (Offline TTS)

```python
# Add this import at the top of your file
import pyttsx3

# ... (Inside the display_message function) ...
# Replace the Azure TTS call with this:
self.speak_text_pyttsx3(message, ai_model)

# Add this function to your class
def speak_text_pyttsx3(self, text, ai_model):
    """
    Synthesizes speech from the input string of text using pyttsx3 (offline TTS).
    """
    try:
        # Initialize the pyttsx3 engine
        engine = pyttsx3.init()

        # Set properties (optional)
        engine.setProperty('rate', 150)    # Speed percent (can go over or under 100)
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

        # Generate and play the speech
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"Error in speak_text_pyttsx3: {e}")
```

## Notes

- **API Keys and Credentials:** Remember to replace placeholder API keys and voice names with your actual values. Keep your API keys secure and do not expose them in public repositories.
  
- **AWS Credentials:** For **Amazon Polly**, ensure you have configured your AWS credentials correctly. You can set them up using AWS CLI or by storing credentials in a configuration file.

- **Voice Selection:** Customize voice settings such as language code, voice ID, and gender according to your preference and the capabilities of the chosen TTS engine.

- **Adjusting Settings:** You can adjust parameters like speaking rate, volume, and pitch within each TTS function to better suit your needs.

- **Dependencies:** Ensure all necessary packages are installed. Use `pip install` to install any missing packages.

- **Error Handling:** The provided code includes basic error handling to help you debug issues if they arise.

## Example: Updating the `display_message` Function

Here's how you might update the `display_message` function in your `debate_azure_scrape.py` file:

```python
def display_message(self, message, ai_model):
    # Print the message to the console or GUI
    print(f"{ai_model}: {message}")

    # Speak the message using the desired TTS engine
    # Comment out the Azure TTS call
    # self.speak_text_azure(message, ai_model)

    # Use the chosen TTS function
    self.speak_text_google(message, ai_model)  # For Google Cloud TTS
    # self.speak_text_polly(message, ai_model)   # For Amazon Polly
    # self.speak_text_elevenlabs(message, ai_model)  # For ElevenLabs
    # self.speak_text_pyttsx3(message, ai_model)  # For pyttsx3
```

## Final Tips

- **Testing:** After making changes, test your application to ensure the new TTS engine works as expected.
  
- **Documentation:** Refer to the official documentation of each TTS provider for detailed information on available settings and features.

  - [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/docs)
  - [Amazon Polly](https://docs.aws.amazon.com/polly/latest/dg/what-is.html)
  - [ElevenLabs](https://elevenlabs.io/)
  - [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)

- **Compliance and Usage Limits:** Be aware of any usage limits, costs, or compliance requirements associated with the TTS service you choose.

By following this guide, you can customize the Debate AI program to use your preferred TTS engine, enhancing the auditory experience of AI-generated debates.