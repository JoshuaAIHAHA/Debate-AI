import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import json
import socket
import threading
from wordcloud import WordCloud
from textblob import TextBlob
import seaborn as sns
from collections import defaultdict
from gensim import corpora, models
from gensim.models import CoherenceModel
import logging
import spacy

# Initialize spaCy for NER
nlp = spacy.load("en_core_web_sm")

# Configure logging
logging.basicConfig(filename='debate_visualizer.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


class DebateVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enhanced AI Debate Visualizer")
        self.geometry("1800x1000")
        self.debate_data = []
        self.live = True
        self.speakers = set()
        self.filtered_speaker = tk.StringVar(value="All")
        self.connection_status = tk.StringVar(value="Disconnected")
        self.live_status = tk.StringVar(value="Live")
        self.custom_alerts = []
        self.setup_ui()
        self.connect_socket()

    def setup_ui(self):
        # Main layout
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True)

        left, right = ttk.Frame(main, width=300), ttk.Notebook(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Controls Frame
        controls = ttk.LabelFrame(left, text="Controls")
        controls.pack(fill=tk.X, pady=5)

        ttk.Button(controls, text="Pause/Resume", command=self.toggle_live).pack(pady=5, fill=tk.X)
        ttk.Button(controls, text="Save Data", command=self.save_data).pack(pady=5, fill=tk.X)
        ttk.Button(controls, text="Add Alert", command=self.add_alert).pack(pady=5, fill=tk.X)

        # Filters Frame
        filters = ttk.LabelFrame(left, text="Filters")
        filters.pack(fill=tk.X, pady=5)

        ttk.Label(filters, text="Speaker:").pack(anchor=tk.W, padx=5, pady=2)
        self.speaker_combo = ttk.Combobox(filters, textvariable=self.filtered_speaker, state="readonly")
        self.speaker_combo['values'] = ["All"]
        self.speaker_combo.current(0)
        self.speaker_combo.pack(fill=tk.X, padx=5, pady=2)
        self.speaker_combo.bind("<<ComboboxSelected>>", lambda e: self.update_views())

        # Status Frame
        status = ttk.LabelFrame(left, text="Status")
        status.pack(fill=tk.X, pady=5)

        ttk.Label(status, text="Connection:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(status, textvariable=self.connection_status).pack(anchor=tk.W, padx=5, pady=2)

        ttk.Label(status, text="Live Updates:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(status, textvariable=self.live_status).pack(anchor=tk.W, padx=5, pady=2)

        # Summary
        summary_frame = ttk.LabelFrame(left, text="Debate Summary")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.summary = scrolledtext.ScrolledText(summary_frame, width=40, height=25, state='disabled')
        self.summary.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization Tabs
        tabs = {
            "Debate Flow": self.init_flow_tab,
            "Sentiment": self.init_sentiment_tab,
            "Word Cloud": self.init_wordcloud_tab,
            "Topics": self.init_topics_tab,
            "Entities": self.init_entities_tab
        }

        for name, init_func in tabs.items():
            tab = ttk.Frame(right)
            right.add(tab, text=name)
            init_func(tab)

    def init_flow_tab(self, parent):
        self.flow_fig, self.flow_ax = plt.subplots(figsize=(8, 6))
        self.flow_canvas = FigureCanvasTkAgg(self.flow_fig, master=parent)
        self.flow_canvas.draw()
        self.flow_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_sentiment_tab(self, parent):
        self.sentiment_fig, self.sentiment_ax = plt.subplots(figsize=(8, 6))
        self.sentiment_canvas = FigureCanvasTkAgg(self.sentiment_fig, master=parent)
        self.sentiment_canvas.draw()
        self.sentiment_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_wordcloud_tab(self, parent):
        self.wordcloud_fig, self.wordcloud_ax = plt.subplots(figsize=(8, 6))
        self.wordcloud_canvas = FigureCanvasTkAgg(self.wordcloud_fig, master=parent)
        self.wordcloud_canvas.draw()
        self.wordcloud_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_topics_tab(self, parent):
        self.topics_fig, self.topics_ax = plt.subplots(figsize=(8, 6))
        self.topics_canvas = FigureCanvasTkAgg(self.topics_fig, master=parent)
        self.topics_canvas.draw()
        self.topics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_entities_tab(self, parent):
        self.entities_fig, self.entities_ax = plt.subplots(figsize=(8, 6))
        self.entities_canvas = FigureCanvasTkAgg(self.entities_fig, master=parent)
        self.entities_canvas.draw()
        self.entities_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def connect_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('localhost', 12345))
            self.connection_status.set("Connected")
            logging.info("Connected to debate application.")
            threading.Thread(target=self.receive, daemon=True).start()
        except socket.error as e:
            self.connection_status.set("Failed to Connect")
            messagebox.showerror("Connection Error", "Unable to connect to debate application.")
            logging.error(f"Connection failed: {e}")

    def receive(self):
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if data:
                    updates = data.strip().split('\n')  # Assuming each message ends with newline
                    for item in updates:
                        update = json.loads(item)
                        self.debate_data.append(update)
                        self.speakers.add(update['speaker'])
                        self.perform_ner(update)
                        self.check_alerts(update)
                    self.update_speaker_filter()
                    if self.live:
                        self.after(0, self.update_views)
                else:
                    break
            except Exception as e:
                logging.error(f"Receive error: {e}")
                break
        self.connection_status.set("Disconnected")
        logging.info("Disconnected from debate application.")

    def perform_ner(self, entry):
        doc = nlp(entry['message'])
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        entry['entities'] = entities

    def update_speaker_filter(self):
        current = self.filtered_speaker.get()
        speakers = sorted(self.speakers)
        self.speaker_combo['values'] = ["All"] + speakers
        if current not in self.speaker_combo['values']:
            self.filtered_speaker.set("All")

    def update_views(self):
        self.update_summary()
        self.update_flow()
        self.update_sentiment()
        self.update_wordcloud()
        self.update_topics()
        self.update_entities()

    def toggle_live(self):
        self.live = not self.live
        self.live_status.set("Live" if self.live else "Paused")
        logging.info(f"Live updates {'resumed' if self.live else 'paused'}.")
        if self.live:
            self.update_views()

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.debate_data, f, indent=2)
                messagebox.showinfo("Success", f"Data saved to {file_path}")
                logging.info(f"Data saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
                logging.error(f"Failed to save data: {e}")

    def update_summary(self):
        self.summary.config(state='normal')
        self.summary.delete(1.0, tk.END)
        filtered = self.get_filtered_data()
        for entry in filtered[-10:]:
            entities = ", ".join([f"{text}({label})" for text, label in entry.get('entities', [])])
            self.summary.insert(tk.END, f"{entry['speaker']}: {entry['message'][:50]}... \nEntities: {entities}\n\n")
        self.summary.config(state='disabled')

    def get_filtered_data(self):
        if self.filtered_speaker.get() == "All":
            return self.debate_data
        return [entry for entry in self.debate_data if entry['speaker'] == self.filtered_speaker.get()]

    def update_flow(self):
        ax = self.flow_ax
        ax.clear()
        filtered = self.get_filtered_data()
        G = nx.DiGraph()
        pos = {}
        colors = []
        for i, entry in enumerate(filtered):
            G.add_node(i, label=entry['speaker'])
            pos[i] = (i, -i)
            colors.append('lightblue' if entry['speaker'] == 'Gemini' else 'lightgreen')
            if i > 0:
                G.add_edge(i-1, i)

        nx.draw(G, pos, ax=ax, node_color=colors, with_labels=False, arrows=True, node_size=500)
        for i, entry in enumerate(filtered):
            ax.text(i, -i, entry['message'][:15] + "...", ha='center', va='center', fontsize=8)

        ax.set_title("Debate Flow")
        ax.axis('off')
        self.flow_canvas.draw()

    def update_sentiment(self):
        ax = self.sentiment_ax
        ax.clear()
        filtered = self.get_filtered_data()
        sentiments = [TextBlob(e['message']).sentiment.polarity for e in filtered]
        speakers = [e['speaker'] for e in filtered]
        sns.lineplot(x=range(len(sentiments)), y=sentiments, hue=speakers, ax=ax, palette="tab10")
        ax.set_title("Sentiment Analysis")
        ax.set_xlabel("Message Number")
        ax.set_ylabel("Sentiment Polarity")
        self.sentiment_canvas.draw()

    def update_wordcloud(self):
        ax = self.wordcloud_ax
        ax.clear()
        filtered = self.get_filtered_data()
        text = " ".join(e['message'] for e in filtered)
        if text:
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title("Word Cloud")
        self.wordcloud_canvas.draw()

    def update_topics(self):
        ax = self.topics_ax
        ax.clear()
        filtered = self.get_filtered_data()
        texts = [entry['message'].lower().split() for entry in filtered]
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        if len(dictionary) == 0:
            return  # Avoid errors if no data
        lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10)
        coherence = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v').get_coherence()
        logging.info(f'LDA Model Coherence: {coherence}')

        topics = lda_model.print_topics(num_words=5)
        topic_dict = {f"Topic {i+1}": lda_model.show_topic(i, topn=5) for i in range(5)}
        
        ax.barh(range(len(topics)), [sum(prob for _, prob in topic) for topic in topic_dict.values()], color='skyblue')
        ax.set_yticks(range(len(topics)))
        ax.set_yticklabels(topic_dict.keys())
        ax.set_title("Top Topics in Debate")
        ax.set_xlabel("Probability")
        for i, topic in enumerate(topics):
            ax.text(0, i, topic[1], fontsize=8, va='center')
        self.topics_canvas.draw()

    def update_entities(self):
        ax = self.entities_ax
        ax.clear()
        entity_counts = defaultdict(int)
        for entry in self.debate_data:
            for ent, label in entry.get('entities', []):
                entity_counts[f"{ent} ({label})"] += 1
        if entity_counts:
            entities, counts = zip(*entity_counts.items())
            ax.barh(entities, counts, color='salmon')
            ax.set_title("Named Entities")
            ax.set_xlabel("Frequency")
            ax.set_ylabel("Entities")
            ax.tick_params(axis='y', labelsize=8)
        self.entities_canvas.draw()

    def perform_topic_modeling(self):
        # This function can be expanded for more advanced topic modeling
        pass

    def add_alert(self):
        def submit_alert():
            try:
                threshold = float(sentiment_entry.get())
                direction = direction_var.get()
                self.custom_alerts.append({'threshold': threshold, 'direction': direction})
                messagebox.showinfo("Success", f"Alert added for sentiment {'>' if direction == 'Positive' else '<'} {threshold}")
                top.destroy()
                logging.info(f"Added alert: sentiment {direction} {threshold}")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for sentiment threshold.")

        top = tk.Toplevel(self)
        top.title("Add Sentiment Alert")

        ttk.Label(top, text="Sentiment Threshold:").pack(padx=10, pady=5)
        sentiment_entry = ttk.Entry(top)
        sentiment_entry.pack(padx=10, pady=5)

        direction_var = tk.StringVar(value="Positive")
        ttk.Radiobutton(top, text="Positive", variable=direction_var, value="Positive").pack(padx=10, pady=2)
        ttk.Radiobutton(top, text="Negative", variable=direction_var, value="Negative").pack(padx=10, pady=2)

        ttk.Button(top, text="Add Alert", command=submit_alert).pack(pady=10)

    def check_alerts(self, entry):
        sentiment = TextBlob(entry['message']).sentiment.polarity
        for alert in self.custom_alerts:
            threshold = alert['threshold']
            direction = alert['direction']
            if direction == "Positive" and sentiment > threshold:
                messagebox.showinfo("Alert", f"Positive sentiment spike by {entry['speaker']}: {sentiment}")
                logging.info(f"Positive sentiment alert triggered by {entry['speaker']}: {sentiment}")
            elif direction == "Negative" and sentiment < threshold:
                messagebox.showwarning("Alert", f"Negative sentiment spike by {entry['speaker']}: {sentiment}")
                logging.warning(f"Negative sentiment alert triggered by {entry['speaker']}: {sentiment}")

    def perform_advanced_analysis(self):
        # Placeholder for future advanced analyses
        pass


if __name__ == "__main__":
    app = DebateVisualizer()
    app.mainloop()
