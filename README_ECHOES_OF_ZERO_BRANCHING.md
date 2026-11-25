# ECHOES OF ZERO — Branching Story Edition

## About the game

**ECHOES OF ZERO** is a 2D psychological mystery and survival adventure game made with Python and the Arcade library.

The story takes place on a university campus during a lockdown. The player explores the campus, investigates a secret experiment called **PROJECT ZERO**, collects clues, solves puzzles and speaks to characters who remember the events differently.

The game has six chapters:

1. The Lockdown
2. The People Who Remember
3. The Experiment
4. The False Memory
5. Room Zero
6. The Last Memory

Choices made during conversations and investigations are recorded. These decisions, along with the evidence collected, affect which routes and endings become available. The six possible endings are **THE EXPOSURE**, **THE SILENCE**, **THE SUCCESSOR**, **THE OTHER YOU**, **THE ESCAPE** and **THE LAST MEMORY**.

## Features

- 2D campus exploration with connected areas.
- Interactive objects, doors and character conversations.
- Puzzles that help unlock items and routes.
- Inventory hotbar and evidence collection.
- Health system with an emergency recovery puzzle.
- Branching dialogue and story decisions.
- Ending conditions based on earlier choices and collected evidence.
- Campus map.
- Save and load progress.

## Requirements

- Windows, macOS or Linux.
- Python 3.10 or newer recommended.
- Python Arcade 3.3.3.
- No separate image or audio assets are required by the program.

## Installation

Open PowerShell or a terminal in the folder containing the game file.

Check that Python is available:

```powershell
py --version
```

Install the required library:

```powershell
py -m pip install -r requirements.txt
```

If the `py` command is not available, try:

```powershell
python --version
python -m pip install -r requirements.txt
```

## Run the game

Keep `echoes_of_zero_branching_story.py` and `requirements.txt` in the same folder.

In PowerShell, go to that folder. For example, if the files are in Downloads:

```powershell
cd $HOME\Downloads
```

Start the game:

```powershell
py echoes_of_zero_branching_story.py
```

If needed, use:

```powershell
python echoes_of_zero_branching_story.py
```

## Controls

| Key | Action |
|---|---|
| W / A / S / D | Move |
| Arrow keys | Move |
| E | Interact with the nearest object or door |
| Space / Enter | Continue dialogue |
| 1–6 | Select a dialogue or ending option when choices are displayed |
| 1–4 | Select a regular puzzle answer |
| 1–9 | Toggle cells in a grid puzzle; also select an inventory hotbar slot during normal play |
| U | Use the selected inventory item |
| X | Drop the selected inventory item |
| I | Toggle inventory details |
| M | Open or close the campus map |
| Tab | Open the evidence board |
| H | Show a puzzle hint when available |
| R | Start a recovery puzzle when available |
| F1 / F2 / F3 / F4 | Attempt north / south / east / west room navigation |
| F5 | Save the game |
| F9 | Load the saved game |
| Esc | Close the current overlay |

Some actions are only available when the player is in the correct room or has the required item/evidence.

## Save files

Press **F5** to save and **F9** to load. The game creates a file named:

```text
echoes_of_zero_save.json
```

The save file is created in the current working directory (normally the folder from which the game is launched). It stores information such as the current area, player position, health, inventory, clues, story flags and progress.

Do not delete or manually edit the save file if you want to keep your progress.

## Project structure

```text
ECHOES_OF_ZERO/
├── echoes_of_zero_branching_story.py
├── requirements.txt
└── README.md
```

The save file `echoes_of_zero_save.json` is created after the first save.

## Troubleshooting

**1. `No module named arcade`**

Install the dependency:

```powershell
py -m pip install -r requirements.txt
```

**2. Python command is not recognised**

Try the Windows Python launcher:

```powershell
py --version
```

If neither `py` nor `python` works, install Python and enable the option to add Python to PATH.

**3. The game opens and closes immediately**

Run it from PowerShell rather than double-clicking the file. This keeps the error message visible.

**4. The game does not load my previous progress**

Check that `echoes_of_zero_save.json` is still in the folder from which the game was launched. The game looks for the save file in its current working directory.

## Notes

- The game is written as a single Python file to make it easier to run and submit for the PBL project.
- The graphics are drawn by Arcade; separate image assets are not required.
- The branching outcomes depend on choices and evidence gathered during the playthrough.
