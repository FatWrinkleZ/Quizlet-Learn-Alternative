import json
import random
import sys
import tkinter as tk
from tkinter import ttk
from difflib import SequenceMatcher

if sys.argv.__len__() < 2:
    print("Usage: python main.py <path_to_quizlet_json>")
    sys.exit(1)

ALL_ANSWERS=[]

class Card:
    def __init__(self, json_obj):
        term_str = json_obj['term']
        answer:str = json_obj['definition']
        self.answer = answer
        if answer.count('\n') > 0:
            answers = answer.split('\n')
            print(f"Multiple answers found for term '{term_str}': {answers}! Splitting...")
            answer = answers[random.randint(0, len(answers)-1)]
            answer = answer.strip()
            print(f"Choosing answer: '{answer}'\n")
            self.answer = answer

        if len(term_str.split('\n')) > 1:
            if term_str.count('?') >= 1:
                self.question = term_str[:term_str.index('?')+1]
                self.answer_choices = term_str[term_str.index('?')+1:].strip().split('\n')
                ALL_ANSWERS.extend(self.answer_choices)
            else:
                terms = term_str.split('\n')
                self.question = terms[0]
                self.answer_choices = terms[1:]
                ALL_ANSWERS.extend(self.answer_choices)
        else:
            self.question = term_str
            wrong_answers = [a for a in ALL_ANSWERS if a != answer]
            random_wrong = random.sample(wrong_answers, min(3, len(wrong_answers)))
            self.answer_choices = [answer] + random_wrong
            random.shuffle(self.answer_choices)
        
        for i in range(len(self.answer_choices)):
            self.answer_choices[i] = self.answer_choices[i].strip()

class QuizApp:
    def __init__(self, root, cards):
        self.root = root
        self.root.title("Quiz Learning Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#121212')
        
        self.cards = cards
        self.current_index = 0
        self.score = 0
        self.answered = False
        
        self.bg_main = '#121212'
        self.bg_frame = '#1e1e1e'
        self.bg_card = '#252525'
        self.bg_button = '#2c2c2c'
        self.bg_button_hover = '#3c3c3c'
        self.bg_correct = '#1b5e20'
        self.bg_wrong = '#b71c1c'
        self.fg_text = '#e0e0e0'
        self.fg_light = '#ffffff'
        self.fg_muted = '#aaaaaa'
        self.accent_green = '#66BB6A'
        self.accent_red = '#EF5350'
        self.next_button_bg = '#4CAF50'

        self.canvas = tk.Canvas(
            root, bg=self.bg_main, highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            root, orient='vertical', command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(
            self.canvas, bg=self.bg_main
        )
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.main_frame = tk.Frame(
            self.scrollable_frame, bg=self.bg_main
        )
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.progress_label = tk.Label(
            self.main_frame, 
            text="", 
            font=('Arial', 12),
            bg=self.bg_main,
            fg=self.fg_muted
        )
        self.progress_label.pack(pady=(0, 10))
        
        self.question_frame = tk.Frame(
            self.main_frame, bg=self.bg_card, relief='raised', borderwidth=2
        )
        self.question_frame.pack(fill='x', pady=20)
        
        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=('Arial', 18, 'bold'),
            bg=self.bg_card,
            fg=self.fg_light,
            wraplength=700,
            justify='left',
            pady=30,
            padx=20
        )
        self.question_label.pack()
        
        self.feedback_label = tk.Label(
            self.main_frame,
            text="",
            font=('Arial', 14, 'bold'),
            bg=self.bg_main,
            fg=self.accent_green
        )
        self.feedback_label.pack(pady=10)
        
        self.buttons_frame = tk.Frame(self.main_frame, bg=self.bg_main)
        self.buttons_frame.pack(pady=20)
        
        self.answer_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.buttons_frame,
                text="",
                font=('Arial', 14),
                width=60,
                height=3,
                bg=self.bg_button,
                fg=self.fg_light,
                relief='flat',
                borderwidth=1,
                cursor='hand2',
                wraplength=700,
                justify='left',
                activebackground=self.bg_button_hover,
                activeforeground=self.fg_light
            )
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.bg_button_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.bg_button if b['state'] != 'disabled' else b['bg']))
            btn.pack(pady=8)
            self.answer_buttons.append(btn)
        
        self.next_button = tk.Button(
            self.main_frame,
            text="Next Question",
            font=('Arial', 14, 'bold'),
            bg=self.next_button_bg,
            fg='white',
            width=20,
            height=2,
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            activebackground='#388E3C',
            command=self.next_question
        )
        self.next_button.pack(pady=20)
        self.next_button.pack_forget()
        
        self.display_question()
    
    def display_question(self):
        if self.current_index >= len(self.cards):
            self.show_results()
            return
        
        card = self.cards[self.current_index]
        self.answered = False
        
        self.canvas.yview_moveto(0)
        
        self.progress_label.config(
            text=f"Question {self.current_index + 1} of {len(self.cards)} | Score: {self.score}/{self.current_index}",
            fg=self.fg_muted
        )
        
        self.question_label.config(text=card.question)
        
        self.feedback_label.config(text="")
        
        self.next_button.pack_forget()
        
        for i, btn in enumerate(self.answer_buttons):
            if i < len(card.answer_choices):
                choice = card.answer_choices[i]
                btn.config(
                    text=choice,
                    bg=self.bg_button,
                    fg=self.fg_light,
                    state='normal',
                    command=lambda c=choice: self.check_answer(c)
                )
                btn.pack(pady=8)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.bg_button_hover))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.bg_button))
            else:
                btn.pack_forget()
    
    def check_answer(self, selected):
        if self.answered:
            return
        
        self.answered = True
        card = self.cards[self.current_index]
        is_correct = SequenceMatcher(None, selected.lower(), card.answer.lower()).ratio() > 0.9
        
        if is_correct:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg=self.accent_green)
        else:
            self.feedback_label.config(
                text=f"Incorrect. Correct: {card.answer}",
                fg=self.accent_red
            )
        
        for btn in self.answer_buttons:
            btn_text = btn.cget('text')
            if btn_text == card.answer:
                btn.config(bg=self.bg_correct, state='disabled')
            elif btn_text == selected and not is_correct:
                btn.config(bg=self.bg_wrong, state='disabled')
            else:
                btn.config(state='disabled', bg='#333333')
        
        self.next_button.pack(pady=20)
    
    def next_question(self):
        self.current_index += 1
        self.display_question()
    
    def show_results(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        percentage = round((self.score / len(self.cards)) * 100) if self.cards else 0
        
        result_label = tk.Label(
            self.main_frame,
            text="Quiz Complete!",
            font=('Arial', 32, 'bold'),
            bg=self.bg_main,
            fg=self.fg_light
        )
        result_label.pack(pady=40)
        
        score_label = tk.Label(
            self.main_frame,
            text=f"{percentage}%",
            font=('Arial', 72, 'bold'),
            bg=self.bg_main,
            fg=self.accent_green
        )
        score_label.pack(pady=20)
        
        detail_label = tk.Label(
            self.main_frame,
            text=f"{self.score} out of {len(self.cards)} correct",
            font=('Arial', 18),
            bg=self.bg_main,
            fg=self.fg_muted
        )
        detail_label.pack(pady=20)
        
        retry_button = tk.Button(
            self.main_frame,
            text="Try Again",
            font=('Arial', 16, 'bold'),
            bg=self.next_button_bg,
            fg='white',
            width=15,
            height=2,
            relief='flat',
            cursor='hand2',
            activebackground='#388E3C',
            command=self.restart_quiz
        )
        retry_button.pack(pady=40)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def restart_quiz(self):
        random.shuffle(self.cards)
        self.current_index = 0
        self.score = 0
        self.answered = False
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.__init__(self.root, self.cards)

ALL_JSON_CARDS = json.load(open('FCLE.json', 'r'))
ALL_CARDS = [Card(card_json) for card_json in ALL_JSON_CARDS]
random.shuffle(ALL_CARDS)

ALL_ANSWERS = [s for s in ALL_ANSWERS if s]

root = tk.Tk()
app = QuizApp(root, ALL_CARDS)
root.mainloop()