import tkinter as tk
from tkinter import messagebox
import requests
import random

class LanguageLearningWidget:
    QUIZ_OPTIONS_COUNT = 4  # Defining magic number as a constant

    def __init__(self, root):
        self.window = root
        self.window.title("Language Learning Widget: English & Lithuanian")
        self.window.geometry("450x800")
        self.API_KEY = 'Your_api_key' # use Yandex Dictionary Api
        self.WORD_API_URL = 'https://random-word-api.herokuapp.com/word?number=1'
        self.YANDEX_API_URL = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={}&lang={}&text={}"

        # Word lists
        self.current_word = ""
        self.correct_translation = ""
        self.score = 0  # Initialize score
        self.incorrect_guesses = 0  # Initialize incorrect guesses count
        self.untranslatable_words = []  # List to store skipped/untranslatable words

        # Initialize UI components
        self.init_ui()

        # Display today's word and start quiz
        self.display_daily_word()
        self.next_quiz_question()

    def init_ui(self):
        """Initialize all UI components."""
        # Daily word section
        self.create_label("Today's Word", 16, pady=10)
        self.word_display = self.create_label("", 14, pady=5)
        self.translation_display = self.create_label("", 12, pady=5)

        # Loading label (hidden initially)
        self.loading_label = self.create_label("Loading...", 12, fg="blue", pady=5)
        self.loading_label.pack_forget()

        # Translation tool
        self.create_label("Enter a word to translate", 12, pady=5)
        self.word_entry = self.create_entry()
        self.translate_button = self.create_button("Translate to Lithuanian", self.translate_word)

        self.translation_result = self.create_label("", 12, pady=5)

        # Quiz section
        self.create_label("Quiz: What is the translation?", 16, pady=20)
        self.question_label = self.create_label("Loading...", 14, pady=5)

        self.option_buttons = [self.create_button("Loading...", lambda i=i: self.check_answer(i)) for i in range(self.QUIZ_OPTIONS_COUNT)]

        self.feedback_label = self.create_label("", 12, fg="green", pady=5)

        # Score and incorrect guesses display
        self.score_label = self.create_label(f"Score: {self.score}", 14, pady=10)
        self.incorrect_guesses_label = self.create_label(f"Incorrect: {self.incorrect_guesses}", 14, pady=5)

        # Untranslatable words display with a scrollbar
        self.untranslatable_words_display = self.create_scrollable_text("Untranslatable Words:", height=5, width=50)

    def create_scrollable_text(self, label_text, height, width):
        """Create a label and a scrollable text area."""
        self.create_label(label_text, 12, pady=10)

        frame = tk.Frame(self.window)
        frame.pack(pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(frame, height=height, width=width, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT)
        
        scrollbar.config(command=text_widget.yview)

        return text_widget

    def create_label(self, text, font_size, fg=None, **kwargs):
        """Helper method to create and return a Label."""
        label = tk.Label(self.window, text=text, font=("Helvetica", font_size), fg=fg)
        label.pack(**kwargs)
        return label

    def create_entry(self):
        """Helper method to create and return an Entry."""
        entry = tk.Entry(self.window)
        entry.pack(pady=5)
        return entry

    def create_button(self, text, command):
        """Helper method to create and return a Button."""
        button = tk.Button(self.window, text=text, command=command)
        button.pack(pady=5)
        return button

    def display_daily_word(self):
        """Show loading message and fetch today's word and its translation."""
        self.show_loading(True)  # Show loading indicator
        self.window.after(100, self._display_daily_word)  # Allow UI update before fetching

    def _display_daily_word(self):
        """Actual word fetching with loading display."""
        self.current_word, translation = self.fetch_valid_translation()
        self.word_display.config(text=f"English: {self.current_word}")
        self.translation_display.config(text=f"Lithuanian: {translation}")
        self.show_loading(False)  # Hide loading indicator

    def show_loading(self, is_loading):
        """Show or hide the loading message."""
        if is_loading:
            self.loading_label.pack()  # Show the loading message
            self.word_entry.config(state=tk.DISABLED)
            self.translate_button.config(state=tk.DISABLED)
            for button in self.option_buttons:
                button.config(state=tk.DISABLED)
        else:
            self.loading_label.pack_forget()  # Hide the loading message
            self.word_entry.config(state=tk.NORMAL)
            self.translate_button.config(state=tk.NORMAL)
            for button in self.option_buttons:
                button.config(state=tk.NORMAL)

    def translate_word(self):
        """Translate a word entered by the user."""
        word = self.word_entry.get().strip()
        if word:
            translation = self.fetch_translation(word, "en-lt")
            self.translation_result.config(text=f"Lithuanian: {translation}" if translation else "Translation not found")
        else:
            messagebox.showerror("Error", "Please enter a word to translate.")

    def fetch_valid_translation(self):
        """Fetch a valid word and its translation."""
        while True:
            word = self.fetch_random_word()
            if word is None:
                return None, None
            translation = self.fetch_translation(word, "en-lt")
            if translation:
                return word, translation
            else:
                # If untranslatable, add to list and update display
                self.untranslatable_words.append(word)
                self.untranslatable_words_display.insert(tk.END, f"{word}\n")
                print(f"Skipping untranslatable word: {word}")

    def fetch_random_word(self):
        """Fetch a random word from the Random Word API."""
        try:
            response = requests.get(self.WORD_API_URL)
            return response.json()[0]  # Get the first word from the response
        except Exception as e:
            print(f"Error fetching random word: {e}")
            messagebox.showerror("Error", "Unable to fetch word. Please try again later.")
            return None

    def fetch_translation(self, word, lang_pair):
        """Fetch translation for a given word using Yandex Dictionary API."""
        try:
            url = self.YANDEX_API_URL.format(self.API_KEY, lang_pair, word)
            response = requests.get(url)
            data = response.json()

            if 'def' in data and data['def']:
                first_translation = data['def'][0]['tr'][0]['text']
                if first_translation.lower() == word.lower():
                    return data['def'][0]['tr'][1]['text'] if len(data['def'][0]['tr']) > 1 else first_translation
                return first_translation
            return None
        except Exception as e:
            print(f"Error fetching translation for {word}: {e}")
            messagebox.showerror("Error", "Unable to fetch translation. Please try again later.")
            return None

    def next_quiz_question(self):
        """Prepare and display the next quiz question with loading feedback."""
        self.show_loading(True)
        self.window.after(100, self._next_quiz_question)  # Allow UI update before fetching

    def _next_quiz_question(self):
        """Actual quiz fetching logic."""
        self.current_word, self.correct_translation = self.fetch_valid_translation()
        if self.current_word is None:
            self.show_loading(False)
            return
        
        options = self.prepare_quiz_options()
        random.shuffle(options)

        self.question_label.config(text=f"What is the Lithuanian word for '{self.current_word}'?")
        for i, option in enumerate(options):
            self.option_buttons[i].config(text=option)
        
        self.show_loading(False)

    def prepare_quiz_options(self):
        """Prepare the options for the quiz."""
        options = [self.correct_translation]
        while len(options) < self.QUIZ_OPTIONS_COUNT:
            random_word = self.fetch_random_word()
            random_translation = self.fetch_translation(random_word, "en-lt")
            if random_translation and random_translation not in options:
                options.append(random_translation)
        return options

    def check_answer(self, index):
        """Check the selected answer against the correct translation."""
        selected_answer = self.option_buttons[index].cget("text")
        if selected_answer == self.correct_translation:
            self.feedback_label.config(text="Correct!", fg="green")
            self.score += 1  # Increment the score for correct answer
        else:
            self.feedback_label.config(text=f"Wrong! Correct answer: {self.correct_translation}", fg="red")
            self.incorrect_guesses += 1  # Increment incorrect guesses count

        # Update score and incorrect guesses display
        self.score_label.config(text=f"Score: {self.score}")
        self.incorrect_guesses_label.config(text=f"Incorrect: {self.incorrect_guesses}")

        # Wait and load the next question
        self.window.after(2000, self.next_quiz_question)

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageLearningWidget(root)
    root.mainloop()
