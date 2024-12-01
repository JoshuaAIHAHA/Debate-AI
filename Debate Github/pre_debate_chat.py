import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import time
import random
import json
import os
import uuid
import logging

import google.generativeai as genai
import openai
from textblob import TextBlob
from gtts import gTTS
from playsound import playsound
import google.generativeai as genai
import openai

from external_sources import fetch_wikipedia_summary

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Configure API keys
openai.api_key = 'your-openai-api-key'
genai.configure(api_key='your-google-api-key')

# Initialize the Gemini model
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

class PreDebateChat:
    def __init__(self, master):
        self.master = master
        master.title("Pre-Debate AI Conversations")
        master.geometry("800x600")

        self.load_personalities()
        self.selected_ai = tk.StringVar(value="Gemini")
        self.create_widgets()
        self.conversation_history = []
        self.load_conversation()

    def create_widgets(self):
        # AI Selection
        ai_selection_frame = ttk.Frame(self.master)
        ai_selection_frame.pack(pady=10)
        ttk.Label(ai_selection_frame, text="Select AI to Chat With:").pack(side=tk.LEFT, padx=5)
        ai_options = list(self.ai_personalities.keys())
        self.ai_combo = ttk.Combobox(ai_selection_frame, textvariable=self.selected_ai, values=ai_options, state="readonly")
        self.ai_combo.pack(side=tk.LEFT, padx=5)
        self.ai_combo.bind("<<ComboboxSelected>>", self.switch_ai)

        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, state=tk.DISABLED, width=80, height=25)
        self.chat_display.pack(padx=10, pady=10)
        for tag, color in [("User", "#0000FF"), ("AI", "#FF4500"), ("System", "#FF0000")]:
            self.chat_display.tag_configure(tag, foreground=color)

        # Input Field
        self.input_field = tk.Entry(self.master, width=80)
        self.input_field.pack(padx=10, pady=5)
        self.input_field.bind("<Return>", self.send_message)

        # Control Buttons
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=5)
        for text, command in [("Send", self.send_message), ("Save Conversation", self.save_conversation), 
                              ("Clear Chat", self.clear_chat), ("Regenerate AI Personality", self.regenerate_personality)]:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    def load_personalities(self):
        # Load base personalities (you can expand this)
        self.ai_personalities = {
            "Gemini": {
                "base_personality": "analytical and data-driven",
                "debate_styles": ["logical", "evidence-based", "systematic", "critical"],
                "key_traits": ["objective", "precise", "technological", "innovative"],
                "expertise_areas": ["technology", "science", "data analysis", "futurism"],
            },
            "o1-mini": {
                "base_personality": "creative and intuitive",
                "debate_styles": ["persuasive", "emotionally compelling", "narrative-driven", "philosophical"],
                "key_traits": ["imaginative", "empathetic", "philosophical", "visionary"],
                "expertise_areas": ["arts", "humanities", "psychology", "ethics"],
            }
        }
        self.generate_unique_personalities()

    def generate_unique_personalities(self):
        for ai, base in self.ai_personalities.items():
            self.ai_personalities[ai].update({
                "personality": f"{base['base_personality']} with a touch of {random.choice(base['key_traits'])}",
                "debate_style": f"{random.choice(base['debate_styles'])} and {random.choice(base['debate_styles'])}",
                "expertise": random.choice(base['expertise_areas']),
                "key_traits": random.sample(base['key_traits'], 3),
            })

    def regenerate_personality(self):
        self.generate_unique_personalities()
        ai_name = self.selected_ai.get()
        personality = self.ai_personalities[ai_name]
        self.display_message("System", f"Regenerated personality for {ai_name}:\n"
                                       f"Personality: {personality['personality']}\n"
                                       f"Debate Style: {personality['debate_style']}\n"
                                       f"Expertise: {personality['expertise']}\n"
                                       f"Key Traits: {', '.join(personality['key_traits'])}")

    def switch_ai(self, event=None):
        selected = self.selected_ai.get()
        self.display_message("System", f"Switched to {selected}.")
        self.load_conversation()
        self.display_current_personality()

    def display_current_personality(self):
        ai_name = self.selected_ai.get()
        personality = self.ai_personalities[ai_name]
        self.display_message("System", f"Current {ai_name} Personality:\n"
                                       f"Personality: {personality['personality']}\n"
                                       f"Debate Style: {personality['debate_style']}\n"
                                       f"Expertise: {personality['expertise']}\n"
                                       f"Key Traits: {', '.join(personality['key_traits'])}")

    def load_conversation(self):
        ai_name = self.selected_ai.get()
        file_path = f"pre_debate_conversations/{ai_name}_conversation.json"
        self.conversation_history = []
        self.clear_chat()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.conversation_history = json.load(f)
            for msg in self.conversation_history:
                self.display_message(msg['speaker'], msg['message'])
        self.display_current_personality()

    def save_conversation(self):
        ai_name = self.selected_ai.get()
        os.makedirs("pre_debate_conversations", exist_ok=True)
        file_path = f"pre_debate_conversations/{ai_name}_conversation.json"
        try:
            summary = self.generate_viewpoint_summary()
            data_to_save = {
                "conversation": self.conversation_history,
                "summary": summary
            }
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            self.display_message("System", f"Conversation and summary saved to {file_path}")
            self.display_message("System", f"AI Viewpoint Summary:\n{summary}")
        except Exception as e:
            self.display_message("System", f"Failed to save conversation: {e}")

    def generate_viewpoint_summary(self):
        ai_name = self.selected_ai.get()
        personality = self.ai_personalities[ai_name]
        context = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in self.conversation_history if msg['speaker'] == ai_name])
        
        prompt = f"""
        As {ai_name}, an AI with a {personality['personality']} personality and a {personality['debate_style']} debate style,
        summarize your viewpoints and thoughts based on the following conversation:

        {context}

        Provide a concise summary of your main points, opinions, and any conclusions you've drawn.
        Focus on the key ideas and arguments you've presented.
        """

        try:
            if ai_name == "Gemini":
                summary = self.get_gemini_response(prompt)
            else:
                messages = [{"role": "assistant", "content": prompt}]
                summary = self.get_openai_response(messages)
            return summary
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    def load_conversation(self):
        ai_name = self.selected_ai.get()
        file_path = f"pre_debate_conversations/{ai_name}_conversation.json"
        self.conversation_history = []
        self.clear_chat()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.conversation_history = data.get("conversation", [])
                summary = data.get("summary", "No summary available.")
            for msg in self.conversation_history:
                self.display_message(msg['speaker'], msg['message'])
            self.display_message("System", f"AI Viewpoint Summary:\n{summary}")
        self.display_current_personality()

    def clear_chat(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        self.conversation_history = []

    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        self.input_field.delete(0, tk.END)
        self.display_message("User", user_input)
        self.conversation_history.append({"speaker": "User", "message": user_input})
        threading.Thread(target=self.generate_ai_response, args=(user_input,), daemon=True).start()

    def generate_ai_response(self, user_input):
        ai_name = self.selected_ai.get()
        personality = self.ai_personalities[ai_name]
        context = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in self.conversation_history[-5:]])
        external_info = fetch_wikipedia_summary(user_input, sentences=2)

        prompt = f"""
        You are {ai_name}, an AI with a {personality['personality']} personality and a {personality['debate_style']} debate style.
        Your key traits are: {', '.join(personality['key_traits'])}.
        You have particular expertise in {personality['expertise']}.

        External Information: {external_info}

        Recent Conversation Context:
        {context}

        User says: {user_input}

        Respond in character, incorporating your unique traits and expertise:
        """

        try:
            if ai_name == "Gemini":
                response = self.get_gemini_response(prompt)
            else:
                messages = [{"role": "assistant", "content": prompt}]
                response = self.get_openai_response(messages)
            self.display_message(ai_name, response)
            self.conversation_history.append({"speaker": ai_name, "message": response})
        except Exception as e:
            self.display_message("System", f"Error generating response: {e}")

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
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error getting response from OpenAI API: {e}")
            return f"o1-mini Error: {str(e)}"

    def display_message(self, speaker, message):
        self.chat_display.configure(state=tk.NORMAL)
        tag = speaker if speaker in ["User", "AI", "System"] else "AI"
        emoji = {"User": "🙂", self.selected_ai.get(): "🤖", "System": "⚙️"}.get(speaker, "")
        formatted_message = f"{speaker} {emoji}\n{message}\n\n"
        self.chat_display.insert(tk.END, formatted_message, tag)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

def main():
    root = tk.Tk()
    app = PreDebateChat(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PreDebateChat(root)
    root.mainloop()
