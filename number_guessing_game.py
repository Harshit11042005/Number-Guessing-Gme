"""
Number Guessing Game - polished desktop UI (pure Python, Tkinter only).

Run:  python number_guessing_game.py
Needs Python 3.8+ (Tkinter ships with Python; on Linux: sudo apt install python3-tk)

Features
- 3 difficulty levels, each with its own range and number of tries
- Live "temperature" meter that shows how close the last guess was
- Colour-coded guess history, attempt dots, best score per difficulty
- Keyboard friendly: type and press Enter, Esc starts a new game
"""

import random
import tkinter as tk
from tkinter import font as tkfont

# ---------- Design tokens ----------
BG = "#0F1A20"          # window background
PANEL = "#18252E"       # inputs / raised surfaces
BORDER = "#2B3E4B"
TEXT = "#EAF2F6"
MUTED = "#7F97A6"
COLD = "#4DA8FF"
WARM = "#FFB347"
HOT = "#FF5A4E"
WIN = "#3DDC97"
LOSE = "#C9738A"

DIFFICULTIES = {
    "Easy":   {"max": 50,  "tries": 10},
    "Medium": {"max": 100, "tries": 7},
    "Hard":   {"max": 200, "tries": 8},
}


def pick_font(*families):
    available = set(tkfont.families())
    for fam in families:
        if fam in available:
            return fam
    return "Helvetica"


def mix(c1, c2, t):
    """Blend two hex colours (t = 0..1)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def heat_color(closeness):
    """Cold (blue) -> warm (amber) -> hot (red)."""
    if closeness < 0.5:
        return mix(COLD, WARM, closeness / 0.5)
    return mix(WARM, HOT, (closeness - 0.5) / 0.5)


class RoundButton(tk.Canvas):
    """A flat, rounded button with hover and disabled states."""

    def __init__(self, parent, text, command, width=120, height=44,
                 bg=WIN, fg="#08130E", hover=None, font=None, parent_bg=BG, radius=14):
        super().__init__(parent, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, cursor="hand2")
        self.command, self.w, self.h, self.r = command, width, height, radius
        self.text, self.font = text, font
        self.colors = {"bg": bg, "fg": fg, "hover": hover or mix(bg, "#ffffff", 0.15)}
        self.state = "normal"
        self._hover = False
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<Button-1>", self._click)
        self._draw()

    def _round_rect(self, fill):
        x1, y1, x2, y2, r = 1, 1, self.w - 1, self.h - 1, self.r
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        self.create_polygon(pts, smooth=True, fill=fill, outline="")

    def _draw(self):
        self.delete("all")
        if self.state == "disabled":
            fill, fg = PANEL, MUTED
        else:
            fill = self.colors["hover"] if self._hover else self.colors["bg"]
            fg = self.colors["fg"]
        self._round_rect(fill)
        self.create_text(self.w // 2, self.h // 2, text=self.text, fill=fg, font=self.font)

    def _set_hover(self, value):
        self._hover = value
        self._draw()

    def _click(self, _):
        if self.state == "normal" and self.command:
            self.command()

    def configure_button(self, text=None, bg=None, fg=None, state=None):
        if text is not None:
            self.text = text
        if bg is not None:
            self.colors["bg"], self.colors["hover"] = bg, mix(bg, "#ffffff", 0.15)
        if fg is not None:
            self.colors["fg"] = fg
        if state is not None:
            self.state = state
            self.config(cursor="hand2" if state == "normal" else "arrow")
        self._draw()


class GuessingGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Number Guess")
        self.configure(bg=BG)
        self.geometry("460x680")
        self.resizable(False, False)

        fam = pick_font("Segoe UI", "SF Pro Display", "Helvetica Neue", "Ubuntu", "DejaVu Sans")
        self.f_title = (fam, 28, "bold")
        self.f_sub = (fam, 11)
        self.f_big = (fam, 20, "bold")
        self.f_input = (fam, 32, "bold")
        self.f_btn = (fam, 12, "bold")
        self.f_small = (fam, 10)
        self.f_chip = (fam, 11, "bold")

        self.level = "Medium"
        self.best = {}
        self.meter_now = 0.0
        self.meter_target = 0.0
        self.meter_color = BORDER

        self._build_ui()
        self.bind("<Escape>", lambda e: self.new_game())
        self.new_game()

    # ---------- UI ----------
    def _build_ui(self):
        tk.Label(self, text="Number Guess", font=self.f_title, bg=BG, fg=TEXT).pack(pady=(28, 2))
        self.subtitle = tk.Label(self, font=self.f_sub, bg=BG, fg=MUTED)
        self.subtitle.pack()

        # Difficulty selector
        row = tk.Frame(self, bg=BG)
        row.pack(pady=(18, 6))
        self.level_btns = {}
        for name in DIFFICULTIES:
            b = RoundButton(row, name, lambda n=name: self.set_level(n), width=96, height=36,
                            bg=PANEL, fg=MUTED, font=self.f_small, radius=12)
            b.pack(side="left", padx=4)
            self.level_btns[name] = b

        # Attempt dots
        self.dots = tk.Canvas(self, width=380, height=22, bg=BG, highlightthickness=0)
        self.dots.pack(pady=(10, 0))

        # Feedback message
        self.msg = tk.Label(self, text="", font=self.f_big, bg=BG, fg=TEXT,
                            wraplength=400, height=2)
        self.msg.pack(pady=(14, 0))
        self.hint = tk.Label(self, text="", font=self.f_sub, bg=BG, fg=MUTED)
        self.hint.pack()

        # Temperature meter
        self.meter = tk.Canvas(self, width=380, height=14, bg=BG, highlightthickness=0)
        self.meter.pack(pady=(16, 2))
        lab = tk.Frame(self, bg=BG, width=380)
        lab.pack()
        tk.Label(lab, text="Cold", font=self.f_small, bg=BG, fg=COLD).pack(side="left")
        tk.Label(lab, text=" " * 58, bg=BG).pack(side="left")
        tk.Label(lab, text="Hot", font=self.f_small, bg=BG, fg=HOT).pack(side="left")

        # Input
        self.entry = tk.Entry(self, font=self.f_input, justify="center", width=6,
                              bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat",
                              highlightthickness=2, highlightbackground=BORDER,
                              highlightcolor=COLD)
        self.entry.pack(pady=(24, 14), ipady=8)
        self.entry.bind("<Return>", lambda e: self.submit())

        self.guess_btn = RoundButton(self, "Guess", self.submit, width=200, height=48,
                                     bg=COLD, fg="#06121F", font=self.f_btn)
        self.guess_btn.pack()

        # History
        tk.Label(self, text="Your guesses", font=self.f_small, bg=BG, fg=MUTED).pack(pady=(26, 6))
        self.history = tk.Frame(self, bg=BG)
        self.history.pack()

        # Footer
        self.best_lbl = tk.Label(self, font=self.f_small, bg=BG, fg=MUTED)
        self.best_lbl.pack(side="bottom", pady=(0, 18))
        self.new_btn = RoundButton(self, "New game", self.new_game, width=130, height=36,
                                   bg=PANEL, fg=TEXT, font=self.f_small, radius=12)
        self.new_btn.pack(side="bottom", pady=(0, 8))

    # ---------- Game logic ----------
    def set_level(self, name):
        self.level = name
        self.new_game()

    def new_game(self):
        cfg = DIFFICULTIES[self.level]
        self.max_n, self.max_tries = cfg["max"], cfg["tries"]
        self.secret = random.randint(1, self.max_n)
        self.guesses = []
        self.over = False

        for n, b in self.level_btns.items():
            active = n == self.level
            b.configure_button(bg=COLD if active else PANEL, fg="#06121F" if active else MUTED)

        self.subtitle.config(text=f"I'm thinking of a number from 1 to {self.max_n}.")
        self.msg.config(text="Take your first guess", fg=TEXT)
        self.hint.config(text=f"You have {self.max_tries} tries")
        self.guess_btn.configure_button(text="Guess", bg=COLD, state="normal")
        self.entry.config(state="normal", highlightcolor=COLD)
        self.entry.delete(0, "end")
        self.entry.focus_set()
        self._set_meter(0.0, BORDER, instant=True)
        self._draw_dots()
        self._draw_history()
        self._update_best()

    def submit(self):
        if self.over:
            self.new_game()
            return
        raw = self.entry.get().strip()
        if not raw.lstrip("-").isdigit() or not (1 <= int(raw) <= self.max_n):
            self.msg.config(text=f"Enter a whole number from 1 to {self.max_n}", fg=HOT)
            self.hint.config(text="That didn't use up a try")
            return
        guess = int(raw)
        if guess in self.guesses:
            self.msg.config(text=f"You already tried {guess}", fg=WARM)
            self.hint.config(text="Pick a different number")
            self.entry.delete(0, "end")
            return

        self.guesses.append(guess)
        self.entry.delete(0, "end")
        closeness = 1 - abs(guess - self.secret) / (self.max_n - 1)
        left = self.max_tries - len(self.guesses)

        if guess == self.secret:
            return self._finish(won=True)

        color = heat_color(closeness)
        direction = "Too low, go higher" if guess < self.secret else "Too high, go lower"
        self.msg.config(text=direction, fg=color)
        self.hint.config(text=f"{self._temperature(closeness)}  -  {left} {'try' if left == 1 else 'tries'} left")
        self._set_meter(closeness, color)
        self._draw_dots()
        self._draw_history()
        if left == 0:
            self._finish(won=False)

    def _finish(self, won):
        self.over = True
        n = len(self.guesses)
        if won:
            self.msg.config(text=f"Got it! {self.secret} in {n} {'try' if n == 1 else 'tries'}", fg=WIN)
            self.hint.config(text="New best score!" if self._record_best(n) else "Nicely done")
            self._set_meter(1.0, WIN)
        else:
            self.msg.config(text=f"Out of tries. It was {self.secret}", fg=LOSE)
            self.hint.config(text="Press Play again to try a new number")
        self.entry.config(state="disabled")
        self.guess_btn.configure_button(text="Play again", bg=WIN if won else LOSE, fg="#08130E")
        self._draw_dots()
        self._draw_history()
        self._update_best()

    @staticmethod
    def _temperature(c):
        if c > 0.95: return "Burning"
        if c > 0.85: return "Hot"
        if c > 0.7:  return "Warm"
        if c > 0.45: return "Cool"
        return "Cold"

    def _record_best(self, tries):
        if self.level not in self.best or tries < self.best[self.level]:
            self.best[self.level] = tries
            return True
        return False

    def _update_best(self):
        b = self.best.get(self.level)
        self.best_lbl.config(text=f"Best on {self.level}: {b} tries" if b else f"No best score on {self.level} yet")

    # ---------- Drawing ----------
    def _draw_dots(self):
        c = self.dots
        c.delete("all")
        total, used = self.max_tries, len(self.guesses)
        gap, r = 26, 7
        x0 = 190 - (total - 1) * gap / 2
        for i in range(total):
            x = x0 + i * gap
            if i < used:
                last_win = self.over and i == used - 1 and self.guesses[-1] == self.secret
                fill = WIN if last_win else MUTED
                c.create_oval(x - r, 11 - r, x + r, 11 + r, fill=fill, outline="")
            else:
                c.create_oval(x - r, 11 - r, x + r, 11 + r, fill=BG, outline=COLD, width=2)

    def _draw_history(self):
        for w in self.history.winfo_children():
            w.destroy()
        if not self.guesses:
            tk.Label(self.history, text="Nothing yet", font=self.f_small, bg=BG, fg=BORDER).pack()
            return
        wrap = tk.Frame(self.history, bg=BG)
        wrap.pack()
        for i, g in enumerate(self.guesses):
            if g == self.secret:
                color, arrow = WIN, "✓"
            else:
                color = heat_color(1 - abs(g - self.secret) / (self.max_n - 1))
                arrow = "↑" if g < self.secret else "↓"
            chip = tk.Label(wrap, text=f"{g} {arrow}", font=self.f_chip, bg=mix(BG, color, 0.22),
                            fg=color, padx=10, pady=4)
            chip.grid(row=i // 5, column=i % 5, padx=4, pady=4)

    def _set_meter(self, value, color, instant=False):
        self.meter_target, self.meter_color = value, color
        if instant:
            self.meter_now = value
            self._draw_meter()
        else:
            self._animate_meter()

    def _animate_meter(self):
        diff = self.meter_target - self.meter_now
        if abs(diff) < 0.004:
            self.meter_now = self.meter_target
        else:
            self.meter_now += diff * 0.2
            self.after(16, self._animate_meter)
        self._draw_meter()

    def _draw_meter(self):
        c = self.meter
        c.delete("all")
        w, h = 380, 14
        self._pill(c, 0, 0, w, h, PANEL)
        fill_w = max(h, w * self.meter_now) if self.meter_now > 0 else 0
        if fill_w:
            self._pill(c, 0, 0, fill_w, h, self.meter_color)

    @staticmethod
    def _pill(c, x1, y1, x2, y2, fill):
        r = (y2 - y1) / 2
        c.create_oval(x1, y1, x1 + 2 * r, y2, fill=fill, outline="")
        c.create_oval(x2 - 2 * r, y1, x2, y2, fill=fill, outline="")
        c.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="")


if __name__ == "__main__":
    GuessingGame().mainloop()
