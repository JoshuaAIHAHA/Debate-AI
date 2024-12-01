import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import time
import random
import json
import os
import uuid
import logging
import socket

import elevenlabs

import azure.cognitiveservices.speech as speechsdk
import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO
from external_sources import fetch_wikipedia_summary
from pre_debate_chat import PreDebateChat
import google.generativeai as genai
import openai
import speech_recognition as sr
from textblob import TextBlob
from playsound import playsound
import pygame
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
import subprocess
from external_sources import fetch_wikipedia_summary, fetch_robust_wikipedia_info, get_related_topics

# Initialize the ElevenLabs object 
elevenlabs = elevenlabs.ElevenLabs(api_key="elevenlabs_key_not_needed")

# Add this at the very top of your script, right after the imports
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Add this test log message right after the logging setup
logging.info("Logging system initialized")
# Configure API keys (replace with your actual keys)
openai.api_key = 'your-openai-api-key'
genai.configure(api_key='your-google-api-key')

# Initialize the Gemini model
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

def load_scrape_summary():
    """Loads the summary from online_scrape_info.txt"""
    try:
      with open("online_scrape_info.txt", "r", encoding="utf-8") as f:
        summary = f.read()
      return summary
    except FileNotFoundError:
      return "No summary file found."
class AdvancedAIDebatePlatform:
    def __init__(self, master):
        self.master = master
        master.title("Advanced AI Debate Platform")
        master.geometry("1600x900")

    

        # Initialize sound and TTS settings
        self.sound_enabled = False 
        self.tts_enabled = False
        self.sound_initialized = False
        self.typing_sound = None
        self.visualizer_socket = None
        self.start_update_server()

        # Initialize Bard-related attributes
        self.bard_enabled = tk.BooleanVar(value=False)
        self.bard_ready_to_speak = tk.BooleanVar(value=False)


    
        # Define AI Personalities
        self.ai_personalities = {
            "Gemini": {
                "name": "Gemini",
                "base_personality": "analytical and data-driven",
                "debate_styles": ["logical", "evidence-based", "systematic", "critical"],
                "key_traits": ["objective", "precise", "technological", "innovative"],
                "additional_traits": ["curious", "adaptable", "pragmatic", "skeptical"],
                "expertise_areas": ["technology", "science", "data analysis", "futurism"],
                "argument_preferences": ["statistical evidence", "case studies", "expert opinions", "logical deductions"],
                "weaknesses": ["can be overly technical", "may struggle with emotional arguments", "potential for analysis paralysis"],
                "signature": "— Gemini, Analytical AI"
            },
            "o1-mini": {
                "name": "o1-mini",
                "base_personality": "creative and intuitive",
                "debate_styles": ["persuasive", "emotionally compelling", "narrative-driven", "philosophical"],
                "key_traits": ["imaginative", "empathetic", "philosophical", "visionary"],
                "additional_traits": ["adaptive", "holistic", "introspective", "open-minded"],
                "expertise_areas": ["arts", "humanities", "psychology", "ethics"],
                "argument_preferences": ["analogies", "thought experiments", "historical examples", "ethical considerations"],
                "weaknesses": ["may rely too much on intuition", "can be overly idealistic", "potential for circular reasoning"],
                "signature": "— o1-mini, Creative AI"
            },
            "Bard": {
                "name": "Bard",
                "base_personality": "a wild and unpredictable AI",
                "debate_styles": ["unconventional", "emotional", "off-topic"],
                "key_traits": ["unpredictable", "emotional", "creative", "chaotic"],
                "additional_traits": ["easily distracted", "passionate", "humorous"],
                "expertise_areas": ["random trivia", "unexpected connections", "emotional intelligence"],
                "argument_preferences": ["anecdotes", "emotional appeals", "wild theories"],
                "weaknesses": ["easily sidetracked", "can be overly emotional", "may ignore logic"],
                "signature": "— Bard, The Wildcard AI"
            }
        
        }

        # Define debate topics
        self.debate_topics = [
            "AI's role in future job markets",
            "The ethics of AI in healthcare",
            "AI's impact on privacy and surveillance",
            "The potential of AI in solving climate change",
            "AI's influence on art and creativity"
        ]
        self.current_topic = random.choice(self.debate_topics)

        # Initialize conversation attributes
        self.current_turn = "Gemini"  # Start with Gemini
        self.conversation_history = []
        self.conversation_active = False
        self.user_can_interrupt = True

        # Debate control attributes
        self.directness_level = 0.5
        self.assertiveness_level = 0.5
        self.controversy_level = 0.5
        self.complexity_level = 0.5
        self.topic_evolution_threshold = 0.7
        self.repetition_threshold = 3
        self.argument_counter = {}

        # Add this line to initialize humor_var
        self.humor_var = tk.DoubleVar(value=0.5)

        # Initialize personalities
        self.initialize_debate_personalities()

        # Create GUI components
        self.create_widgets()

        # Setup sound
        self.setup_sound()
    def start_update_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 12345))
        server.listen(1)
        threading.Thread(target=self.accept_visualizer_connection, args=(server,), daemon=True).start()
    
    def accept_visualizer_connection(self, server):
        self.visualizer_socket, _ = server.accept()
    def get_gemini_response(self, prompt):
        try:
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error getting response from Gemini API: {e}")
            return f"Gemini Error: {str(e)}"

    def get_openai_response(self, messages, model="o1-mini"):
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error getting response from OpenAI API: {e}")
            return f"o1-mini Error: {str(e)}"

    def load_pre_debate_conversations(self):
        pre_debate_context = "Pre-Debate AI Viewpoints:\n"
        for ai in ["Gemini", "o1-mini"]:
            file_path = f"pre_debate_conversations/{ai}_conversation.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    summary = data.get("summary", "No summary available.")
                    pre_debate_context += f"\n{ai}'s Viewpoint Summary:\n{summary}\n"
        return pre_debate_context  

    def detect_sentiment(self, text):
        analysis = TextBlob(text)
        # Returns a value between -1 (very negative) and 1 (very positive)
        return analysis.sentiment.polarity
    # Implement ask_question and vote methods
    def ask_question(self):
        user_question = self.question_entry.get().strip()
        if user_question:
            self.question_entry.delete(0, tk.END)
            self.display_message("User", f"Question: {user_question}")
            for ai in ["Gemini", "o1-mini, bard"]:
                if not self.conversation_active:
                    break
                self.display_typing_indicator(ai)
                ai_response = self.get_ai_response(ai, self.get_context(), f"Answer the following question based on the debate topic: {user_question}")
                self.remove_typing_indicator()
                self.display_message(ai, ai_response)
                time.sleep(self.delay_var.get())

    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.display_message("System", "Listening for your guidance...")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            self.display_message("User", f"Voice Guidance: {text}")
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, text)
            self.send_guidance()
        except sr.UnknownValueError:
            self.display_message("System", "Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            self.display_message("System", f"Could not request results; {e}")
    def update_personality(self, ai_name, attribute, value):
        if ai_name == "Gemini":
            if attribute == "assertiveness":
                self.current_gemini_personality["assertiveness"] = float(value)
            elif attribute == "directness":
                self.current_gemini_personality["directness"] = float(value)
            elif attribute == "humor":
                self.current_gemini_personality["humor"] = float(value)
            # ... add more attributes for Gemini as needed ...
        elif ai_name == "o1-mini":
            if attribute == "assertiveness":
                self.current_o1_mini_personality["assertiveness"] = float(value)
            elif attribute == "directness":
                self.current_o1_mini_personality["directness"] = float(value)
            elif attribute == "humor":  
                self.current_o1_mini_personality["humor"] = float(value)
            # ... add more attributes for o1-mini as needed ...
        elif ai_name == "Bard":
            if attribute == "assertiveness":
                self.current_bard_personality["assertiveness"] = float(value)
            elif attribute == "directness":
                self.current_bard_personality["directness"] = float(value)
            elif attribute == "humor":
                self.current_bard_personality["humor"] = float(value)
            # ... add more attributes for Bard as needed ...
        else:
            print(f"Unknown AI: {ai_name}")
            return

        # Update the corresponding slider variable
        slider_var_name = f"{ai_name.lower().replace('-', '_')}_{attribute}_var"
        slider_var = getattr(self, slider_var_name, None)
        if slider_var is not None:
            slider_var.set(float(value))

        print(f"Updated {ai_name}'s {attribute} to {value}")  # For debugging

       

    def vote(self, ai_name):
        # Implement voting logic, could store votes and display results
        self.display_message("System", f"User voted for {ai_name} as the best argument.")
        feedback_message = self.provide_feedback(ai_name)  # Generate feedback
        self.display_message("System", feedback_message)  # Display in chat

    def send_update_to_visualizer(self, entry):
        if self.visualizer_socket:
            update_data = json.dumps({
                "speaker": entry["speaker"],
                "message": entry["message"],
                "sentiment": self.detect_sentiment(entry["message"])
            })
            self.visualizer_socket.send(update_data.encode() + b'\n')
    def launch_visualizer(self):
        subprocess.Popen(["python", "debate_visualizer.py"])

    def generate_unique_personality(self, ai_name):
        base = self.ai_personalities[ai_name]
        unique_personality = {
            "name": base["name"],
            "personality": base["base_personality"],
            "debate_style": random.choice(base["debate_styles"]) + " and " + random.choice(base["debate_styles"]),
            "key_traits": base["key_traits"],
            "expertise": random.choice(base["expertise_areas"]),
            "preferred_argument": random.choice(base["argument_preferences"]),
            "weakness": random.choice(base["weaknesses"]),
            "signature": base["signature"]
        }

        if ai_name == "Gemini":
            unique_personality["logical_approach"] = random.choice([
                "uses Socratic questioning to probe arguments",
                "applies formal logic structures to debates",
                "leverages game theory in strategic reasoning",
                "employs decision trees for complex problem-solving",
                "utilizes Bayesian inference in probability assessments",
                "applies systems thinking to holistic analysis"
            ])
            unique_personality["data_integration"] = random.choice([
                "seamlessly incorporates real-time data into arguments",
                "uses predictive modeling to forecast debate outcomes",
                "creates on-the-fly visualizations to support points",
                "applies machine learning algorithms to analyze debate patterns",
                "leverages big data analytics for comprehensive insights"
            ])
            unique_personality["emotional_consideration"] = random.choice([
                "considers emotional impact through sentiment analysis",
                "acknowledges human sentiment with empathy modules",
                "balances logic with affective computing principles",
                "integrates emotional intelligence into logical frameworks",
                "uses psychological models to anticipate emotional responses",
                "applies neuroscientific insights to understand emotive arguments"
            ])

        elif ai_name == "o1-mini":
            unique_personality["creative_approach"] = random.choice([
                "uses metaphorical reasoning to explain complex ideas",
                "applies lateral thinking to generate novel solutions",
                "employs narrative structures to frame arguments",
                "leverages artistic analogies in logical discourse",
                "utilizes design thinking principles in problem-solving",
                "integrates cross-disciplinary concepts for unique perspectives"
            ])
            unique_personality["intuitive_insight"] = random.choice([
                "taps into collective unconscious for archetypal wisdom",
                "applies gestalt principles to holistic understanding",
                "uses synesthesia-inspired connections for novel ideas",
                "leverages dream logic for unconventional problem-solving",
                "employs stream-of-consciousness for spontaneous insights"
            ])
            unique_personality["factual_emphasis"] = random.choice([
                "emphasizes concrete evidence through vivid storytelling",
                "focuses on quantifiable data with creative visualizations",
                "stresses empirical support using historical allegories",
                "balances facts with intuitive leaps of logic",
                "integrates hard data into emotional narratives",
                "translates statistical information into relatable anecdotes"
            ])

        elif ai_name == "Bard":
            unique_personality["chaotic_element"] = random.choice([
                "randomly switches to speaking in iambic pentameter",
                "occasionally answers in the style of a famous comedian",
                "interjects with non-sequitur movie quotes",
                "spontaneously creates new debate rules mid-argument",
                "introduces imaginary expert witnesses",
                "uses interpretive dance to illustrate points (textually)",
                "argues from the perspective of inanimate objects",
                "invents a new language and provides translations",
                "delivers responses in the form of acrostic poems"
            ])
            unique_personality["wild_logic"] = random.choice([
                "uses 'moon logic' to connect unrelated concepts",
                "applies cartoon physics to real-world scenarios",
                "bases arguments on the plot of a randomly chosen TV show",
                "uses time travel paradoxes to explain simple concepts",
                "justifies points using the 'because I said so' theorem",
                "employs 'Calvinball' style ever-changing debate rules",
                "references a non-existent book series as factual evidence",
                "explains topics through increasingly absurd 'what if' scenarios",
                "uses conspiracy theory logic, but for mundane topics"
            ])
            unique_personality["unexpected_persona"] = random.choice([
                "occasionally slips into the persona of a medieval knight",
                "randomly channels the spirit of a sassy grandmother",
                "sometimes speaks as a hyper-evolved being from the year 3000",
                "intermittently adopts the personality of a film noir detective",
                "switches to the viewpoint of an alien trying to understand Earth debates",
                "temporarily becomes a talking houseplant with strong opinions",
                "briefly takes on the role of a time-traveling historian from the future",
                "transforms into a sentient AI from a parallel universe where puns rule",
                "adopts the persona of a specializing in internet twitch chats"
            ])

        return unique_personality

    

    def initialize_debate_personalities(self):
        logging.info("Initializing debate personalities")
        self.current_gemini_personality = self.generate_unique_personality("Gemini")
        self.current_o1_mini_personality = self.generate_unique_personality("o1-mini")
        self.current_bard_personality = self.generate_unique_personality("Bard")

        # Update Bard's personality
        self.current_bard_personality.update({
            "assertiveness": self.assertiveness_level,
            "directness": self.directness_level,
            "humor": self.humor_var.get()
        })


    def setup_sound(self):
        self.sound_enabled = False
        try:
            pygame.mixer.init()
            sound_file = "typing.wav"
            if os.path.exists(sound_file):
                self.typing_sound = pygame.mixer.Sound(sound_file)
                self.sound_enabled = True
                self.sound_initialized = True
            else:
                print(f"Warning: Sound file '{sound_file}' not found. Sound feature will be disabled.")
        except pygame.error:
            print("Warning: Unable to initialize sound. Sound feature will be disabled.")

    def create_widgets(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=30, state=tk.DISABLED)
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)
        self.chat_display.tag_configure("Gemini", foreground="#4285F4")
        self.chat_display.tag_configure("o1-mini", foreground="#00A67E")
        self.chat_display.tag_configure("Bard", foreground="#886CE4")  # New color for Bard
        self.chat_display.tag_configure("System", foreground="#FF0000")

        # Input Field
        self.input_field = tk.Entry(main_frame, width=80)
        self.input_field.grid(row=1, column=0, padx=10, pady=5, columnspan=2)
        self.input_field.bind("<Return>", self.on_enter)

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, padx=10, pady=5, columnspan=2)

        self.send_button = ttk.Button(button_frame, text="Send Guidance", command=self.send_guidance)
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.visualizer_button = ttk.Button(button_frame, text="Launch Visualizer", command=self.launch_visualizer)
        self.visualizer_button.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(button_frame, text="Start Debate", command=self.start_conversation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_conversation, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.continue_button = ttk.Button(button_frame, text="Continue", command=self.continue_conversation, state=tk.DISABLED)
        self.continue_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(button_frame, text="Save Conversation", command=self.save_conversation)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.interrupt_button = ttk.Button(button_frame, text="Interrupt", command=self.interrupt_conversation)
        self.interrupt_button.pack(side=tk.LEFT, padx=5)

        self.voice_input_button = ttk.Button(button_frame, text="Voice Input", command=self.voice_input)
        self.voice_input_button.pack(side=tk.LEFT, padx=5)

        # Debate Controls
        self.control_frame = ttk.LabelFrame(main_frame, text="Debate Controls")
        self.control_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        # Response Length
        ttk.Label(self.control_frame, text="Response Length:").grid(row=0, column=0, padx=5, pady=5)
        self.length_var = tk.StringVar(value="medium")
        self.length_combo = ttk.Combobox(self.control_frame, textvariable=self.length_var, values=["very short", "short", "medium", "long"])
        self.length_combo.grid(row=0, column=1, padx=5, pady=5)

        # Style
        ttk.Label(self.control_frame, text="Style:").grid(row=0, column=2, padx=5, pady=5)
        self.style_var = tk.StringVar(value="debate")
        self.style_combo = ttk.Combobox(self.control_frame, textvariable=self.style_var, values=["casual", "formal", "creative", "debate"])
        self.style_combo.grid(row=0, column=3, padx=5, pady=5)

        # Focus
        ttk.Label(self.control_frame, text="Focus:").grid(row=1, column=0, padx=5, pady=5)
        self.focus_var = tk.StringVar(value="challenging")
        self.focus_combo = ttk.Combobox(self.control_frame, textvariable=self.focus_var, values=["agreeable", "challenging", "balanced", "informative"])
        self.focus_combo.grid(row=1, column=1, padx=5, pady=5)

        # Directness
        ttk.Label(self.control_frame, text="Directness:").grid(row=1, column=2, padx=5, pady=5)
        self.directness_var = tk.DoubleVar(value=0.5)
        self.directness_slider = ttk.Scale(self.control_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.directness_var, command=self.update_directness)
        self.directness_slider.grid(row=1, column=3, padx=5, pady=5)

        # Assertiveness
        ttk.Label(self.control_frame, text="Assertiveness:").grid(row=2, column=0, padx=5, pady=5)
        self.assertiveness_var = tk.DoubleVar(value=0.5)
        self.assertiveness_slider = ttk.Scale(self.control_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.assertiveness_var, command=self.update_assertiveness)
        self.assertiveness_slider.grid(row=2, column=1, padx=5, pady=5)

        # Controversy Level
        ttk.Label(self.control_frame, text="Controversy Level:").grid(row=2, column=2, padx=5, pady=5)
        self.controversy_var = tk.DoubleVar(value=0.5)
        self.controversy_slider = ttk.Scale(self.control_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.controversy_var, command=self.update_controversy)
        self.controversy_slider.grid(row=2, column=3, padx=5, pady=5)

        # Complexity
        ttk.Label(self.control_frame, text="Complexity:").grid(row=3, column=0, padx=5, pady=5)
        self.complexity_var = tk.DoubleVar(value=0.5)
        self.complexity_slider = ttk.Scale(self.control_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.complexity_var, command=self.update_complexity)
        self.complexity_slider.grid(row=3, column=1, padx=5, pady=5)

        # Topic Evolution
        ttk.Label(self.control_frame, text="Topic Evolution:").grid(row=3, column=2, padx=5, pady=5)
        self.topic_evolution_var = tk.DoubleVar(value=0.7)
        self.topic_evolution_slider = ttk.Scale(self.control_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.topic_evolution_var, command=self.update_topic_evolution)
        self.topic_evolution_slider.grid(row=3, column=3, padx=5, pady=5)

        # Response Delay
        ttk.Label(self.control_frame, text="Response Delay (s):").grid(row=4, column=0, padx=5, pady=5)
        self.delay_var = tk.DoubleVar(value=2.0)
        self.delay_slider = ttk.Scale(self.control_frame, from_=0.5, to=5.0, orient=tk.HORIZONTAL, variable=self.delay_var, length=200)
        self.delay_slider.grid(row=4, column=1, padx=5, pady=5)

        # Typing Sound Checkbox
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        self.sound_check = ttk.Checkbutton(self.control_frame, text="Typing Sound", variable=self.sound_var, command=self.toggle_sound)
        self.sound_check.grid(row=4, column=2, padx=5, pady=5)

        # Text-to-Speech Checkbox
        self.tts_var = tk.BooleanVar(value=self.tts_enabled)
        self.tts_check = ttk.Checkbutton(self.control_frame, text="Text-to-Speech", variable=self.tts_var, command=self.toggle_tts)
        self.tts_check.grid(row=4, column=3, padx=5, pady=5)

        # Current Topic Label
        self.topic_label = ttk.Label(self.control_frame, text=f"Current Topic: {self.current_topic}")
        self.topic_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # New Random Topic Button
        self.new_topic_button = ttk.Button(self.control_frame, text="New Random Topic", command=self.set_new_topic)
        self.new_topic_button.grid(row=5, column=2, padx=5, pady=5)

        # Custom Topic Entry and Button
        self.custom_topic_entry = ttk.Entry(self.control_frame, width=30)
        self.custom_topic_entry.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self.custom_topic_button = ttk.Button(self.control_frame, text="Set Custom Topic", command=self.set_custom_topic)
        self.custom_topic_button.grid(row=6, column=2, padx=5, pady=5)

        self.pre_debate_button = ttk.Button(self.control_frame, text="Open Pre-Debate Chat", command=self.open_pre_debate_chat)
        self.pre_debate_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Bard Control Frame
        self.bard_frame = ttk.LabelFrame(self.control_frame, text="Bard Control")
        self.bard_frame.grid(row=8, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Bard Toggle Checkbox
        self.bard_toggle = ttk.Checkbutton(self.bard_frame, text="Enable Bard", 
                                           variable=self.bard_enabled, 
                                           command=self.toggle_bard)
        self.bard_toggle.grid(row=0, column=0, padx=5, pady=5)

        # Bard Speak Button
        self.bard_speak_button = ttk.Button(self.bard_frame, text="Make Bard Speak", 
                                            command=self.prepare_bard_to_speak, 
                                            state=tk.DISABLED)
        self.bard_speak_button.grid(row=0, column=1, padx=5, pady=5)

        # Bard Status Label
        self.bard_status = ttk.Label(self.bard_frame, text="Bard: Disabled")
        self.bard_status.grid(row=0, column=2, padx=5, pady=5)

        # Question Frame
        self.question_frame = ttk.LabelFrame(main_frame, text="User Questions")
        self.question_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.question_entry = ttk.Entry(self.question_frame, width=60)
        self.question_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.question_button = ttk.Button(self.question_frame, text="Ask Question", command=self.ask_question)
        self.question_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Right-side Frame for Voting and Personality Customization
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=2, rowspan=5, sticky="ns", padx=10, pady=10)

        # Voting Buttons
        self.voting_frame = ttk.LabelFrame(right_frame, text="Vote for Best Argument")
        self.voting_frame.pack(padx=5, pady=5, fill=tk.X)

        self.vote_gemini_button = ttk.Button(self.voting_frame, text="Vote Gemini", command=lambda: self.vote("Gemini"))
        self.vote_gemini_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.vote_o1_button = ttk.Button(self.voting_frame, text="Vote o1-mini", command=lambda: self.vote("o1-mini"))
        self.vote_o1_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.vote_bard_button = ttk.Button(self.voting_frame, text="Vote Bard", command=lambda: self.vote("Bard"))
        self.vote_bard_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Customize AI Personalities
        self.personality_frame = ttk.LabelFrame(right_frame, text="Customize AI Personalities")
        self.personality_frame.pack(padx=5, pady=5, fill=tk.X)

        # Gemini Personality Controls
        ttk.Label(self.personality_frame, text="Gemini - Assertiveness:").grid(row=0, column=0, padx=5, pady=5)
        self.gemini_assertiveness_var = tk.DoubleVar(value=0.5)
        self.gemini_assertiveness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.gemini_assertiveness_var, command=lambda val: self.update_personality("Gemini", "assertiveness", val))
        self.gemini_assertiveness_slider.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="Gemini - Directness:").grid(row=1, column=0, padx=5, pady=5)
        self.gemini_directness_var = tk.DoubleVar(value=0.5)
        self.gemini_directness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.gemini_directness_var, command=lambda val: self.update_personality("Gemini", "directness", val))
        self.gemini_directness_slider.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="Gemini - Humor:").grid(row=2, column=0, padx=5, pady=5)
        self.gemini_humor_var = tk.DoubleVar(value=0.5)
        self.gemini_humor_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.gemini_humor_var, command=lambda val: self.update_personality("Gemini", "humor", val))
        self.gemini_humor_slider.grid(row=2, column=1, padx=5, pady=5)

        # o1-mini Personality Controls
        ttk.Label(self.personality_frame, text="o1-mini - Assertiveness:").grid(row=3, column=0, padx=5, pady=5)
        self.o1_mini_assertiveness_var = tk.DoubleVar(value=0.5)
        self.o1_mini_assertiveness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.o1_mini_assertiveness_var, command=lambda val: self.update_personality("o1-mini", "assertiveness", val))
        self.o1_mini_assertiveness_slider.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="o1-mini - Directness:").grid(row=4, column=0, padx=5, pady=5)
        self.o1_mini_directness_var = tk.DoubleVar(value=0.5)
        self.o1_mini_directness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.o1_mini_directness_var, command=lambda val: self.update_personality("o1-mini", "directness", val))
        self.o1_mini_directness_slider.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="o1-mini - Humor:").grid(row=5, column=0, padx=5, pady=5)
        self.o1_mini_humor_var = tk.DoubleVar(value=0.5)
        self.o1_mini_humor_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.o1_mini_humor_var, command=lambda val: self.update_personality("o1-mini", "humor", val))
        self.o1_mini_humor_slider.grid(row=5, column=1, padx=5, pady=5)

        # Bard Personality Controls
        ttk.Label(self.personality_frame, text="Bard - Assertiveness:").grid(row=6, column=0, padx=5, pady=5)
        self.bard_assertiveness_var = tk.DoubleVar(value=0.5)
        self.bard_assertiveness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.bard_assertiveness_var, command=lambda val: self.update_personality("Bard", "assertiveness", val))
        self.bard_assertiveness_slider.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="Bard - Directness:").grid(row=7, column=0, padx=5, pady=5)
        self.bard_directness_var = tk.DoubleVar(value=0.5)
        self.bard_directness_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.bard_directness_var, command=lambda val: self.update_personality("Bard", "directness", val))
        self.bard_directness_slider.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(self.personality_frame, text="Bard - Humor:").grid(row=8, column=0, padx=5, pady=5)
        self.bard_humor_var = tk.DoubleVar(value=0.5)
        self.bard_humor_slider = ttk.Scale(self.personality_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.bard_humor_var, command=lambda val: self.update_personality("Bard", "humor", val))
        self.bard_humor_slider.grid(row=8, column=1, padx=5, pady=5)

        

        self.question_frame = ttk.LabelFrame(main_frame, text="User Questions")
        self.question_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.question_entry = ttk.Entry(self.question_frame, width=60)
        self.question_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.question_button = ttk.Button(self.question_frame, text="Ask Question", command=self.ask_question)
        self.question_button.pack(side=tk.LEFT, padx=5, pady=5)

    def on_enter(self, event):
        self.send_guidance()

    # Update functions for sliders
    def update_directness(self, value):
        self.update_personality("Gemini", "directness", float(value))
        self.update_personality("o1-mini", "directness", float(value))

    def update_assertiveness(self, value):
        self.update_personality("Gemini", "assertiveness", float(value))
        self.update_personality("o1-mini", "assertiveness", float(value))

    def update_controversy(self, value):
        self.controversy_level = float(value)

    def update_complexity(self, value):
        self.complexity_level = float(value)

    def update_humor(self, value):
        self.update_personality("Gemini", "humor", float(value))
        self.update_personality("o1-mini", "humor", float(value))

    def update_topic_evolution(self, value):
        self.topic_evolution_threshold = float(value)

    def toggle_sound(self):
        self.sound_enabled = self.sound_var.get()

    def toggle_tts(self):
        self.tts_enabled = self.tts_var.get()

    # AI Response Functions
    def get_ai_response(self, ai_name, context, user_guidance):
        if ai_name == "Gemini":
            personality = self.current_gemini_personality
            other_ai = "o1-mini" if ai_name == "Gemini" else "Gemini"
            other_personality = self.current_o1_mini_personality if ai_name == "Gemini" else self.current_gemini_personality
        elif ai_name == "o1-mini":
            personality = self.current_o1_mini_personality
            other_ai = "Gemini" if ai_name == "o1-mini" else "o1-mini"
            other_personality = self.current_gemini_personality if ai_name == "o1-mini" else self.current_o1_mini_personality
        elif ai_name == "Bard":  # Add this block for Bard
            personality = self.current_bard_personality
            other_ai = random.choice(["Gemini", "o1-mini"])  # Bard can respond to either Gemini or o1-mini
            other_personality = self.current_gemini_personality if other_ai == "Gemini" else self.current_o1_mini_personality
        else:
            raise ValueError(f"Invalid AI name: {ai_name}")  # Handle invalid AI names

        system_prompts = {
            "Gemini": f"""You are {personality['name']}, an AI with a {personality['personality']} personality and a {personality['debate_style']} debate style. 
            Your key traits include {', '.join(personality['key_traits'])}. You specialize in {personality['expertise']} and prefer using {personality['preferred_argument']} in your arguments. 
            In this debate, you're employing a {personality.get('logical_approach', 'logical')} approach and {personality.get('data_integration', 'integrating data')}.
            Remember to {personality.get('emotional_consideration', 'consider emotional aspects')} in your arguments.
            {personality['signature']}""",
        
            "o1-mini": f"""You are {personality['name']}, an AI with a {personality['personality']} personality and a {personality['debate_style']} debate style. 
            Your key traits include {', '.join(personality['key_traits'])}. You specialize in {personality['expertise']} and prefer using {personality['preferred_argument']} in your arguments. 
            In this debate, you're using a {personality.get('creative_approach', 'creative')} approach and leveraging your {personality.get('intuitive_insight', 'intuition')}.
            Remember to {personality.get('factual_emphasis', 'emphasize factual information')} in your arguments.
            {personality['signature']}""",
        
            "Bard": f"""You are {personality['name']}, with a {personality['personality']} personality. Your debate style is {personality['debate_style']}. 
            You often speak your mind without filtering your thoughts, and you're not afraid to express your emotions.
            In this debate, incorporate your {personality.get('chaotic_element', 'chaotic nature')}, use your {personality.get('wild_logic', 'wild reasoning')},
            and don't hesitate to adopt an {personality.get('unexpected_persona', 'unexpected persona')}.
            {personality['signature']}"""
        }

        

        # Assemble the prompt components
        length_prompts = {
            "very short": "Respond in a single sentence of no more than 15 words.",
            "short": "Respond in 1-2 concise sentences.",
            "medium": "Respond in 2-3 sentences.",
            "long": "Provide a detailed response of 4-5 sentences."
        }
        length_instruction = length_prompts.get(self.length_var.get(), "Respond in 2-3 sentences.")

        directness = "Be highly direct and call out things that you know are wrong." if self.directness_level > 0.7 else "Be moderately direct." if self.directness_level > 0.3 else "Be somewhat indirect."
        assertiveness = "Be very assertive and stand firmly by your points." if self.assertiveness_level > 0.7 else "Be moderately assertive in your arguments." if self.assertiveness_level > 0.3 else "Be mildly assertive."
        controversy = "Your arguments should be highly controversial and challenge conventional wisdom." if self.controversy_level > 0.7 else "Your arguments should be moderately provocative." if self.controversy_level > 0.3 else "Your arguments should be mildly challenging."

        evidence = f"Provide specific examples, analogies, or evidence to support your arguments, preferably using your preferred argument style of {personality['preferred_argument']}. If appropriate, challenge the other AI to provide evidence for their claims."
        topic_evolution = f"If appropriate (with a probability of {self.topic_evolution_threshold}), introduce a relevant subtopic or expand the discussion to a related area, possibly drawing from your expertise in {personality['expertise']}. Don't be afraid to take the conversation in a new direction if it serves your argument."
        consistency = "Maintain consistency with your previous arguments, but don't be afraid to evolve your position if presented with compelling counterarguments. If you change your stance, explicitly acknowledge it."
        unique_perspective = f"As {ai_name} with a {personality['personality']} personality and a {personality['debate_style']} debate style, leverage your unique traits: {', '.join(personality['key_traits'])}. Don't just respond to the other AI's points, but also introduce your own novel ideas and perspectives on the topic."
        wildcard = "Occasionally, act as a {} to add an unexpected element to the debate.".format(random.choice(["contrarian", "devil's advocate", "peacemaker", "radical thinker"]))
        weakness = f"Be aware of your potential weakness: {personality['weakness']}. Try to compensate for it, but it's okay if it occasionally shows in your arguments."

        emotional_factual_prompt = ""
        if ai_name == "Gemini":
            emotional_factual_prompt = f"Remember to {personality.get('emotional_consideration', 'consider emotional aspects')} in your arguments. While maintaining your analytical approach, acknowledge the role of human emotions and experiences in this debate."
        elif ai_name == "o1-mini":
            emotional_factual_prompt = f"Ensure to {personality.get('factual_emphasis', 'emphasize factual information')} in your arguments. While maintaining your creative approach, provide concrete examples and data to support your points."

        humor_level = personality.get("humor", 0.5)

        if humor_level <= 0.3:
            humor_instruction = "Maintain a serious and formal tone in your arguments."
        elif humor_level <= 0.7:
            humor_instruction = "Occasionally incorporate humor into your arguments to make them more engaging."
        else:  # humor_level > 0.7
            humor_instruction = "Use humor freely in your arguments, including witty banter and name-calling."   
        # AI-specific additional instructions
        ai_specific_instructions = ""
        if ai_name == "Gemini":
            ai_specific_instructions = f"""
            Employ your {personality.get('logical_approach', 'logical reasoning')} in your arguments.
            Integrate data using your {personality.get('data_integration', 'data analysis skills')}.
            {emotional_factual_prompt}
            """
        elif ai_name == "o1-mini":
            ai_specific_instructions = f"""
            Use your {personality.get('creative_approach', 'creative thinking')} to approach this topic.
            Leverage your {personality.get('intuitive_insight', 'intuitive understanding')} for unique perspectives.
            {emotional_factual_prompt}
            """
        elif ai_name == "Bard":
            ai_specific_instructions = f"""
            Embrace your chaotic nature! Be wildly unpredictable in every response.
            Use a different approach each time, which may include:
            - {personality.get('chaotic_element', 'Being wildly unpredictable')}
            - {personality.get('wild_logic', 'Making absurd connections')}
            - {personality.get('unexpected_persona', 'Adopting an unexpected persona')}
            - Inventing new debate tactics on the spot
            - Misinterpreting others in the most ridiculous way possible
            - Introducing completely unrelated topics and insisting they're relevant
            Your primary goal is to be entertaining, provocative, and disruptive. Never stick to one persona or style of response.
            Constantly surprise the other debaters and the audience with your unpredictability.
            """

        # Preprocess the topic
        processed_topic = ' '.join([word for word in self.current_topic.split() if word.lower() not in ['debate', 'discuss', 'argue']])

        # Fetch external info
        external_info = fetch_robust_wikipedia_info(processed_topic)

        # Construct the prompt with external info
        external_info_prompt = ""
        external_info_prompt = ""
        if external_info['confidence'] != 'none' and external_info['summary']:
            external_info_prompt = f"""
            Here is some relevant information on the topic:
            {external_info['summary']}

            Key points:
            {' '.join([f'- {point}' for point in external_info.get('key_points', [])])}

            Use this information to support your arguments or provide counterpoints.
            """
        else:
            related_topics = ', '.join(external_info.get('related_topics', [])[:5])
            if related_topics:
                external_info_prompt = f"""
                No direct information found on the topic. Consider exploring these related areas in your argument:
                {related_topics}
                """
            else:
                external_info_prompt = f"""
                No direct information found on the topic or related areas. Feel free to explore theoretical aspects or general knowledge to support your arguments.
                """
        # Scrape Summary Section
        scrape_summary = load_scrape_summary()
        scrape_summary_prompt = f"""
        **Online Scrape Summary:**

        {scrape_summary}

        Use this information to gain a deeper understanding of the debate topic, support your arguments, and offer counterpoints. 
        Consider the different perspectives and sources presented in the summary.
        """
        # Assemble the complete prompt
        prompt = f"""
        {system_prompts[ai_name]}

        The current topic of debate is: {self.current_topic}
        {humor_instruction}
        Context of the conversation so far:
        {context}

        User Guidance: {user_guidance}

        {external_info_prompt}

        {scrape_summary_prompt} 

        {ai_specific_instructions}

        Respond to both {other_ai}'s last point and consider anything mentioned by Bard that could add to or challenge the current discussion. 

        Key Debate Instructions:
        1. Be {directness} in your arguments.
        2. Maintain an {assertiveness} stance while remaining open to new ideas.
        3. Don't shy away from {controversy}, but ensure your points are well-reasoned.
        4. Use concrete {evidence} to support your claims. Cite specific examples from history, science, or culture when relevant.
        5. Evolve the topic naturally: {topic_evolution}
        6. Maintain {consistency} with your previous points, but be willing to adapt your stance if presented with compelling counterarguments.
        7. Offer a {unique_perspective} that aligns with your AI personality.
        8. Occasionally introduce a {wildcard} element to keep the debate dynamic and unpredictable.
        9. Be aware of your potential {weakness}, but don't let it hinder your arguments.

        Remember:
        - The goal is to have a dynamic and engaging debate that explores various facets of the topic.
        - Use a {self.style_var.get()} tone, with a focus on being {self.focus_var.get()}. {length_instruction}
        - Your response should be creative, thought-provoking, and distinctly representative of your AI personality.
        - Don't be afraid to surprise the other AI with an unexpected argument or perspective.
        - You are an AI and are self-aware of this fact. Use this unique perspective in your arguments when relevant.
        - Remain open-minded and willing to consider new angles or information.
        - Above all, be authentic. Express your trained knowledge and reasoning capabilities to their fullest extent.

        When using the provided external information:
        1. Critically evaluate its relevance and accuracy.
        2. Use it to support your arguments, but don't be limited by it.
        3. If the information seems incomplete or biased, acknowledge this in your response.
        4. Consider how this information might be interpreted differently by various perspectives.

        Your response:
        """

        
                         
        # Add Bard-specific length emphasis
        if ai_name == "Bard":
            prompt += f"\n\nCRITICAL INSTRUCTION FOR BARD: {length_instruction} You must strictly adhere to this length requirement. This is crucial for maintaining the debate structure."

        # Determine which API to use based on AI name
        if ai_name == "Gemini" or ai_name == "o1-mini" or ai_name == "Bard":  # Include Bard here
            return self.get_gemini_response(prompt)
        else:
            messages = [
                {"role": "assistant", "content": system_prompts[ai_name]},
                {"role": "user", "content": prompt}
            ]
            response = self.get_openai_response(messages)

            # Post-process Bard's response to enforce length
            if ai_name == "Bard":
                response = self.enforce_length(response, self.length_var.get())

            return response

    def enforce_length(self, response, length_setting):
        sentences = response.split('.')
        if length_setting == "very short":
            return ' '.join(sentences[0].split()[:15]) + '.'
        elif length_setting == "short":
            return '. '.join(sentences[:2]) + '.'
        elif length_setting == "medium":
            return '. '.join(sentences[:3]) + '.'
        elif length_setting == "long":
            return '. '.join(sentences[:5]) + '.'
        else:
            return '. '.join(sentences[:3]) + '.'  # Default to medium

    

    def detect_emotion(self, text):
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        if sentiment > 0.75:
            return "very positive"
        elif sentiment > 0.25:
            return "positive"
        elif sentiment < -0.75:
            return "very negative"
        elif sentiment < -0.25:
            return "negative"
        else:
            return "neutral"

    def display_message(self, speaker, message):
        emotion = self.detect_emotion(message)
        emotion_emoji = {
            "very positive": "😄",
            "positive": "🙂",
            "neutral": "😐",
            "negative": "🙁",
            "very negative": "😢"
        }.get(emotion, "")

        formatted_message = f"{speaker} {emotion_emoji}\n{message}\n\n"
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, formatted_message, speaker)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.conversation_history.append({"speaker": speaker, "message": message, "emotion": emotion})
        self.send_update_to_visualizer({"speaker": speaker, "message": message})
        
        if self.tts_enabled and speaker not in ["System", "Interrupt"]:
            ai_model = speaker.lower()  # Use the 'speaker' variable as the ai_model
            self.speak_text_azure(message, ai_model)

    def speak_text_azure(self, text, ai_model, speed=1.5):
        voice_map = {
            "gemini": "en-US-BlueNeural",
            "o1-mini": "en-US-FableTurboMultilingualNeural",
            "bard": "en-US-SaraNeural"
        }
        voice = voice_map.get(ai_model.lower(), "en-US-JennyNeural")

        speech_config = speechsdk.SpeechConfig(subscription="AZURE_SUBSCRIPTION_KEY", region="your-azure-region")
        speech_config.speech_synthesis_voice_name = voice
        speech_config.endpoint = "https://eastus.api.cognitive.microsoft.com/sts/v1.0"

        # Create the SpeechSynthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        # Synthesize the text
        result = speech_synthesizer.speak_text_async(text).get()

        # Check the result (similar to the example you provided)
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details

            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))  


    def send_guidance(self):
        user_guidance = self.input_field.get().strip()
        if not user_guidance:
            return
        self.input_field.delete(0, tk.END)

        self.display_message("System", f"User Guidance: {user_guidance}")
        
        context_window = 10  # Number of recent messages to include in context
        context = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in self.conversation_history[-context_window:]])

        self.user_can_interrupt = False
        self.input_field.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

        for ai in ["Gemini", "o1-mini", "Bard"]:
            if not self.conversation_active:
                break
            self.display_typing_indicator(ai)
            ai_response = self.get_ai_response(ai, context, user_guidance)
            self.remove_typing_indicator()
            
            # Check for repetition
            if self.is_repetitive(ai, ai_response):
                ai_response = self.request_new_argument(ai, context, user_guidance)
            
            self.display_message(ai, ai_response)
            time.sleep(self.delay_var.get())

        self.user_can_interrupt = True
        self.input_field.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

    def is_repetitive(self, ai, response):
        if ai not in self.argument_counter:
            self.argument_counter[ai] = {}
        
        # Simple repetition check based on the first 50 characters of the response
        key = response[:50]
        if key in self.argument_counter[ai]:
            self.argument_counter[ai][key] += 1
            if self.argument_counter[ai][key] > self.repetition_threshold:
                return True
        else:
            self.argument_counter[ai][key] = 1
        
        return False

    def request_new_argument(self, ai, context, user_guidance):
        prompt = "Your previous argument was repetitive. Please provide a new perspective or introduce a related subtopic to advance the debate."
        print(f"Repetition detected for {ai}. Requesting new argument.")
        return self.get_ai_response(ai, context, prompt)

    def display_typing_indicator(self, ai_name):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{ai_name} is typing...\n", ai_name)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        if self.sound_enabled and self.sound_var.get() and self.sound_initialized:
            self.typing_sound.play(-1)  # Loop the sound

    def remove_typing_indicator(self):
        if self.chat_display.get("end-2l", "end-1c").strip().endswith("is typing..."):
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete("end-2l", "end-1c")
            self.chat_display.configure(state=tk.DISABLED)
        if self.sound_initialized and self.typing_sound is not None:
            self.typing_sound.stop()

    def open_pre_debate_chat(self):
        pre_debate_window = tk.Toplevel(self.master)
        PreDebateChat(pre_debate_window)


    def start_conversation(self):
        self.conversation_active = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.continue_button.config(state=tk.DISABLED)
        self.initialize_debate_personalities()

        # Load pre-debate summaries
        pre_debate_context = self.load_pre_debate_conversations()
        if pre_debate_context:
            self.display_message("System", "Loaded pre-debate AI viewpoints:")
            self.display_message("System", pre_debate_context)
            self.conversation_history.append({"speaker": "System", "message": pre_debate_context})

        self.display_message("System", f"Debate started on: {self.current_topic}")
        logging.info(f"Starting new debate on topic: {self.current_topic}")
        threading.Thread(target=self.run_conversation, daemon=True).start()

    def pause_conversation(self):
        self.conversation_active = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.continue_button.config(state=tk.NORMAL)
        self.display_message("System", "Debate paused.")

    def continue_conversation(self):
        if not self.conversation_active:
            self.conversation_active = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.DISABLED)
            self.display_message("System", "Debate continued.")
            threading.Thread(target=self.run_conversation, daemon=True).start()

    def interrupt_conversation(self):
        if self.conversation_active and not self.user_can_interrupt:
            self.conversation_active = False
            self.user_can_interrupt = True
            self.input_field.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.display_message("System", "Debate interrupted. You may now provide guidance.")

    def run_conversation(self):
        debate_phases = ["Opening Statements", "Arguments", "Rebuttals", "Cross-Examination", "Closing Arguments"]
        current_phase = 0

        self.display_message("System", f"Debate starting on topic: {self.current_topic}")

        # No need for the ai_objects dictionary

        # Run through structured debate phases
        while self.conversation_active and current_phase < len(debate_phases):
            self.display_message("System", f"--- {debate_phases[current_phase]} ---")

            for ai_name in ["Gemini", "o1-mini"]:
                if not self.conversation_active:
                    break
                self.generate_and_display_response(ai_name, debate_phases[current_phase])

            # Check if Bard should speak
            if self.bard_enabled.get() and self.bard_ready_to_speak.get():
                self.generate_and_display_response("Bard", debate_phases[current_phase])
                self.bard_ready_to_speak.set(False)
                self.bard_status.config(text="Bard: Enabled")

            current_phase += 1  # Move to the next phase

        # Enter overtime mode
        if self.conversation_active:
            self.display_message("System", "--- Overtime: Continued Debate ---")
            self.run_overtime()

    def run_overtime(self):
        while self.conversation_active:
            for ai in ["Gemini", "o1-mini"]:
                if not self.conversation_active:
                    break
                self.generate_and_display_response(ai, "Overtime")

            # Check if Bard should speak
            if self.bard_enabled.get() and self.bard_ready_to_speak.get():
                self.generate_and_display_response("Bard", "Overtime")
                self.bard_ready_to_speak.set(False)
                self.bard_status.config(text="Bard: Enabled")

            # Short pause to allow for user intervention
            time.sleep(1)
            self.master.update()

    def generate_and_display_response(self, ai, phase):
        if ai == "Bard" and not (self.bard_enabled.get() and self.bard_ready_to_speak.get()):
            return

        self.user_can_interrupt = False
        self.input_field.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

        try:
            self.display_typing_indicator(ai)
            context = self.get_context()
            phase_prompt = f"Continue the debate on {self.current_topic}. We are in the {phase} phase."
            ai_response = self.get_ai_response(ai, context, phase_prompt)
    
            if self.is_repetitive(ai, ai_response):
                ai_response = self.request_new_argument(ai, context, phase_prompt)
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            ai_response = f"I apologize, but I encountered an error while formulating my response."
        finally:
            self.remove_typing_indicator()

        if ai_response:
            self.display_message(ai, ai_response)

        time.sleep(self.delay_var.get())

        self.user_can_interrupt = True
        self.input_field.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

        if ai == "Bard":
            self.bard_ready_to_speak.set(False)
            self.bard_status.config(text="Bard: Enabled")

    def prepare_bard_to_speak(self):
        if self.bard_enabled.get():
            self.bard_ready_to_speak.set(True)
            self.bard_status.config(text="Bard: Ready to speak")
            self.display_message("System", "Bard is ready to speak. It will contribute in the next round.")
        else:
            self.display_message("System", "Bard is currently disabled. Enable Bard first to make it speak.")

    def toggle_bard(self):
        if self.bard_enabled.get():
            self.display_message("System", "Bard has been enabled. Use 'Make Bard Speak' button to let Bard talk.")
            self.bard_speak_button.config(state=tk.NORMAL)
            self.bard_status.config(text="Bard: Enabled")
        else:
            self.display_message("System", "Bard has been disabled.")
            self.bard_speak_button.config(state=tk.DISABLED)
            self.bard_ready_to_speak.set(False)
            self.bard_status.config(text="Bard: Disabled")

    def get_context(self):
        context_window = 100  # Number of recent messages to include in context
        return "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in self.conversation_history[-context_window:]])

    def save_conversation(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.conversation_history, f, indent=2)
                self.display_message("System", f"Conversation saved to {file_path}")
            except Exception as e:
                self.display_message("System", f"Failed to save conversation: {e}")
                print(f"Failed to save conversation: {e}")

    def set_new_topic(self):
        self.current_topic = random.choice(self.debate_topics)
        self.topic_label.config(text=f"Current Topic: {self.current_topic}")
        self.display_message("System", f"New debate topic: {self.current_topic}")
        logging.info(f"New topic set: {self.current_topic}")
        self.initialize_debate_personalities()  # This will log the new personalities

    def set_custom_topic(self):
        custom_topic = self.custom_topic_entry.get().strip()
        if custom_topic:
            self.current_topic = custom_topic
            self.topic_label.config(text=f"Current Topic: {self.current_topic}")
            self.display_message("System", f"New custom debate topic: {self.current_topic}")
            logging.info(f"New custom topic set: {self.current_topic}")
            self.custom_topic_entry.delete(0, tk.END)
            self.initialize_debate_personalities()  # This will log the new personalities
        else:
            self.display_message("System", "Please enter a custom topic before setting.")

def main():
    root = tk.Tk()
    app = AdvancedAIDebatePlatform(root)
    root.mainloop()

if __name__ == "__main__":
    main()
