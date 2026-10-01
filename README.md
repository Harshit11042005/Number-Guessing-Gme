# Number Guess

A polished desktop number guessing game written in pure Python. It uses only the standard library (Tkinter), so there is nothing to install.

Guess the secret number before you run out of tries. A live heat meter tells you how close each guess was, from cold blue to burning red.

<!-- Add a screenshot or GIF here:
![Number Guess screenshot](assets/screenshot.png)
-->

## Features

- **Three difficulty levels**, each with its own range and number of tries
- **Heat meter** that animates from cold to hot based on how close your guess was
- **Clear feedback** such as "Too low, go higher", plus Cold, Cool, Warm, Hot or Burning
- **Attempt dots** showing how many tries you have left
- **Colour-coded guess history** with arrows pointing the way
- **Best score tracking** per difficulty (kept while the app is open)
- **Friendly validation**: invalid or repeated guesses never cost a try
- **Keyboard friendly**: type and press Enter, or press Esc to start a new game

## Difficulty levels

| Level  | Range  | Tries |
|--------|--------|-------|
| Easy   | 1–50   | 10    |
| Medium | 1–100  | 7     |
| Hard   | 1–200  | 8     |

## Getting started

### Requirements

- Python 3.8 or newer
- Tkinter (included with Python on Windows and macOS)

On Debian or Ubuntu, install Tkinter if it is missing:

```bash
sudo apt install python3-tk
```

### Run the game

```bash
git clone https://github.com/<your-username>/number-guess.git
cd number-guess
python number_guessing_game.py
```

Use `python3` instead of `python` if that is how Python is installed on your system.

## How to play

1. Pick a difficulty (the default is Medium).
2. Type a whole number in the box and press **Enter** or click **Guess**.
3. Use the feedback and the heat meter to narrow it down.
4. Find the number before your tries run out.

| Key     | Action                                  |
|---------|-----------------------------------------|
| `Enter` | Submit a guess (or play again after a game) |
| `Esc`   | Start a new game                        |

## Project structure

```
number-guess/
├── number_guessing_game.py   # the whole game: logic and UI
└── README.md
```

## Customising

All colours and difficulty settings sit at the top of `number_guessing_game.py`:

```python
BG = "#0F1A20"      # window background
COLD = "#4DA8FF"    # change the palette here

DIFFICULTIES = {
    "Easy":   {"max": 50,  "tries": 10},
    "Medium": {"max": 100, "tries": 7},
    "Hard":   {"max": 200, "tries": 8},
}
```

Add a new entry to `DIFFICULTIES` and it appears as a button automatically (you may need to adjust the button width to fit the row).

## Roadmap

- [ ] Save best scores to a file so they persist between sessions
- [ ] Sound effects
- [ ] Custom range and tries setting
- [ ] Light theme

## Contributing

Suggestions and pull requests are welcome. For larger changes, please open an issue first to discuss what you would like to change.

## License

Released under the [MIT License](LICENSE). Add a `LICENSE` file to your repository to match.
