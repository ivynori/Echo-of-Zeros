"""
ECHOES OF ZERO
A psychological survival mystery built with Python Arcade 3.x.

Install:
    python -m pip install arcade==3.3.3

Run:
    python echoes_of_zero.py

CONTROLS
    WASD / Arrow keys : Move
    E                 : Interact with the nearest object / door
    SPACE / ENTER     : Continue dialogue
    1-4               : Choose a dialogue or puzzle answer
    1-9               : Toggle cells in a grid puzzle
    TAB               : Open evidence board
    M                 : Campus map
    I                 : Inventory
    H                 : Show a hint during a puzzle
    F5                : Save
    F9                : Load
    ESC               : Close an overlay

No external image assets are required. The world and interface are drawn with
Arcade shapes and text so the project is easy to run and explain.
"""

import arcade
import json
import random
import os
import math

SCREEN_W = 1100
SCREEN_H = 720
TITLE = "ECHOES OF ZERO | A Psychological Survival Mystery"
SAVE_FILE = "echoes_of_zero_save.json"
PLAYER_SPEED = 245
INTERACT_DISTANCE = 92

# Palette
BG = (8, 12, 24)
PANEL = (17, 25, 43)
PANEL2 = (26, 38, 61)
WHITE = (235, 242, 252)
MUTED = (151, 169, 195)
CYAN = (91, 224, 229)
BLUE = (93, 151, 235)
PURPLE = (177, 128, 235)
GOLD = (245, 197, 105)
RED = (238, 91, 111)
GREEN = (103, 218, 160)
DARK = (5, 8, 17)

# Six areas form the campus investigation.
AREAS = {
    "quad": {
        "name": "NORTH QUADRANGLE", "chapter": 1,
        "desc": "The campus is silent. Emergency lights pulse across the wet pavement.",
        "color": (22, 43, 59),
        "objects": [
            ("message", "Unknown message", 210, 485, "A disconnected terminal lights up: DON'T GO TO THE MAIN GATE. THEY KNOW YOU ARE HERE."),
            ("notice_puzzle", "Lockdown timestamp", 525, 455, "A notice is marked 10:44 PM, one minute after the warning."),
            ("photo", "Damaged photograph", 790, 480, "A photograph shows five students outside this university. Your own face has been scratched away. On the back: ROOM 0 — 11:47 PM."),
            ("door_library", "Library entrance", 1010, 350, "The library doors are unlocked. Something has been left inside."),
        ],
    },
    "library": {
        "name": "CENTRAL LIBRARY", "chapter": 1,
        "desc": "Rows of shelves disappear into darkness. A desk lamp is still on.",
        "color": (38, 38, 66),
        "objects": [
            ("crossword", "Archivist's crossword", 240, 460, "A crossword is pinned to a notebook. The completed answer may unlock the archive drawer."),
            ("archive_drawer", "Archive drawer", 510, 460, "A locked drawer marked MEMORY."),
            ("diary", "Student diary", 760, 475, "The handwriting looks familiar: 'I should never have agreed to erase it.' The final page has been torn out."),
            ("door_lab", "Computer science block", 1010, 350, "A keypad guards the computer science block."),
        ],
    },
    "lab": {
        "name": "COMPUTER SCIENCE BLOCK", "chapter": 2,
        "desc": "Computer monitors flicker with corrupted camera feeds.",
        "color": (24, 48, 63),
        "objects": [
            ("cctv", "CCTV console", 235, 470, "The footage shows you entering this building at 8:13 PM — three hours before you remember arriving."),
            ("grid", "Security grid", 575, 465, "A nine-cell security panel controls the restricted research corridor."),
            ("arin", "Arin", 840, 390, "Arin stands beside a dark monitor. They look as if they have seen a ghost."),
            ("door_hostel", "Hostel corridor", 1010, 350, "The hostel corridor is accessible through the side entrance."),
        ],
    },
    "hostel": {
        "name": "HOSTEL BLOCK", "chapter": 2,
        "desc": "A few doors stand open. Personal belongings lie scattered on the floor.",
        "color": (48, 35, 54),
        "objects": [
            ("locker", "Participant locker", 260, 465, "Inside is a student ID with your photograph. The name field has been burned away."),
            ("medkit", "Emergency cabinet", 565, 465, "A locked emergency cabinet has a riddle written across it."),
            ("witness", "Voice recorder", 835, 465, "A recording plays: 'If you are hearing this, you have already forgotten what you did.'"),
            ("suitcase_puzzle", "Locked suitcase", 710, 300, "A suitcase has a three-symbol lock. A note says: FIRST, THE WARNING. THEN, THE TRIAL. LAST, THE LOCKDOWN."),
            ("door_research", "Research wing", 1010, 350, "A reinforced door leads to the university's restricted research wing."),
        ],
    },
    "research": {
        "name": "RESEARCH WING", "chapter": 3,
        "desc": "The university's public identity ends here. The walls are lined with access panels.",
        "color": (28, 49, 56),
        "objects": [
            ("mira", "Dr. Mira Sen", 250, 400, "Dr. Sen watches you carefully. 'You were never supposed to come back here.'"),
            ("files", "AETHER project files", 560, 470, "PROJECT ZERO: a memory reconstruction trial involving five student participants. The lead participant is listed as YOU."),
            ("binary", "Encrypted terminal", 830, 465, "A terminal requests the name of the programme that altered the participants' memories."),
            ("door_sim", "Simulation chamber", 1010, 350, "A sealed door leads to the memory reconstruction suite."),
        ],
    },
    "simulation": {
        "name": "MEMORY SIMULATION SUITE", "chapter": 4,
        "desc": "The corridor loops back on itself. The same objects appear in slightly different places.",
        "color": (35, 34, 66),
        "objects": [
            ("memory", "Memory reconstruction console", 280, 465, "Two versions of the same classroom appear on screen. One memory has been altered."),
            ("fragments", "Scattered memory fragments", 650, 465, "Three fragments form a sequence: the warning, the experiment, and the lockdown."),
            ("mirror_puzzle", "Mirrored memory panel", 820, 465, "The panel shows a reversed message: 0 MOOR. Enter the room name it points to."),
            ("subject_zero", "Unknown sender", 470, 300, "A terminal flashes with a message from an unknown sender. The typing pattern feels familiar."),
            ("door_zero", "Room 0", 1010, 350, "The original chamber is one level below."),
        ],
    },
    "zero": {
        "name": "ROOM ZERO", "chapter": 5,
        "desc": "The room is exactly as it appears in the photograph. The air hums with old machinery.",
        "color": (47, 28, 45),
        "objects": [
            ("recording", "Original recording", 260, 470, "The recording begins with your voice: 'If the reconstruction works, there will be two versions of me.'"),
            ("kabir", "Officer Kabir", 580, 390, "Kabir lowers his flashlight. 'I was told to keep you out. I was never told what would happen if you got in.'"),
            ("archive", "AETHER archive", 850, 465, "The archive contains the original memory map and the final shutdown controls."),
            ("door_control", "Control centre", 1010, 350, "The archive's final control room is beyond this door."),
        ],
    },
    "control": {
        "name": "THE LAST MEMORY", "chapter": 6,
        "desc": "A wall of monitors displays the same face from different years. One screen is still recording.",
        "color": (42, 28, 42),
        "objects": [
            ("final_console", "Final control console", 520, 455, "The system asks what should happen to the reconstructed memories."),
        ],
    },
}

# Puzzles are short and story-linked; answers can be selected with number keys.
PUZZLES = {
    "crossword": {
        "title": "THE ARCHIVIST'S CROSSWORD",
        "prompt": "Across: A person's recollection of past experiences (6 letters).",
        "options": ["IDENTITY", "MEMORY", "SHADOW", "SIGNAL"],
        "correct": 2,
        "hint": "The answer is what the experiment was designed to alter.",
        "success": "The drawer clicks open. Inside is a library access card and a note: 'Five went in. Six came out.'",
        "reward": "Library access card",
    },
    "grid": {
        "title": "SECURITY GRID",
        "prompt": "Activate the four corners and the centre. Toggle cells with 1-9, then press ENTER.",
        "grid": True, "target": [1, 3, 5, 7, 9],
        "hint": "The pattern is an X, symmetrical around the centre.",
        "success": "The panel accepts the pattern. A restricted access token slides out.",
        "reward": "Restricted access token",
    },
    "medkit": {
        "title": "EMERGENCY CABINET",
        "prompt": "I can be broken without being touched. I can be kept, but never held. What am I?",
        "options": ["A promise", "A window", "A secret", "A mirror"],
        "correct": 1,
        "hint": "Think of something you make to another person.",
        "success": "The cabinet opens. You find a medical kit.",
        "reward": "MEDKIT",
    },
    "binary": {
        "title": "ENCRYPTED TERMINAL",
        "prompt": "The files describe a programme that reconstructs memories. Which name appears throughout the records?",
        "options": ["PROJECT ZERO", "PROJECT ORBIT", "PROJECT HELIX", "PROJECT AURORA"],
        "correct": 1,
        "hint": "It is the title of the classified programme.",
        "success": "ACCESS GRANTED. The terminal reveals the Room 0 access sequence.",
        "reward": "Room 0 access code",
    },
    "notice": {
        "title": "THE LOCKDOWN TIMESTAMP",
        "prompt": "The notice says the lockdown began at 10:44 PM. The warning shows 10:43 PM. What is the difference?",
        "options": ["One minute", "Three minutes", "One hour", "Eleven minutes"],
        "correct": 1,
        "hint": "Compare 10:43 with 10:44.",
        "success": "The notice has a handwritten code beneath the timestamp: 1044. A new clue is added.",
        "reward": "Lockdown timestamp clue",
    },
    "drawer": {
        "title": "THE ARCHIVE DRAWER",
        "prompt": "The label reads MEMORY IS THE KEY. Which six-letter word completes the lock phrase?",
        "options": ["RECALL", "MEMORY", "RECORD", "PERSON"],
        "correct": 2,
        "hint": "It is the word written on the drawer itself.",
        "success": "The archive drawer opens. You find a torn page naming SUBJECT 05.",
        "reward": "Archive drawer evidence",
    },
    "suitcase": {
        "title": "THE SUITCASE SEQUENCE",
        "prompt": "Arrange the events in the correct order: experiment, warning, lockdown.",
        "options": ["Warning → Experiment → Lockdown", "Experiment → Warning → Lockdown", "Lockdown → Warning → Experiment", "Warning → Lockdown → Experiment"],
        "correct": 2,
        "hint": "The trial came first, then the warning, then the lockdown.",
        "success": "The suitcase opens. Arin's photograph and a diary clue are inside.",
        "reward": "Arin's photograph",
    },
    "mirror": {
        "title": "THE MIRRORED MESSAGE",
        "prompt": "The panel displays '0 MOOR' in reverse. Which destination does it reveal?",
        "options": ["Room 5", "Room Zero", "Control Room", "Research Wing"],
        "correct": 2,
        "hint": "Read the two words from right to left.",
        "success": "The mirrored panel unlocks a hidden memory fragment.",
        "reward": "Mirrored memory clue",
    },
}

# Every door requires two consecutive stages; clues and items must be acquired
# by interacting with objects before a door sequence can be completed.
DOOR_CHAINS = {
    "door_library": [
        ("Which object identifies the five original students?", ["A photograph", "A radio", "A clock", "A key"], 1, "Inspect the damaged photograph first."),
        ("The photograph names which room?", ["Room 12", "Room 0", "Room 9", "Room 4"], 2, "Look at the back of the photograph."),
    ],
    "door_lab": [
        ("The library note says five entered and how many came out?", ["Four", "Five", "Six", "Seven"], 3, "Read the archivist's note."),
        ("Which access item belongs in the keypad?", ["Participant ID", "Medical kit", "Library access card", "Voice recorder"], 3, "Solve the crossword to obtain the card."),
    ],
    "door_hostel": [
        ("The CCTV shows you entering at what time?", ["8:13 PM", "9:45 PM", "10:44 PM", "11:47 PM"], 1, "Inspect the CCTV console."),
        ("Which pattern opens the security route?", ["Four edges", "X pattern", "Middle row", "All nine"], 2, "Solve the security grid first."),
    ],
    "door_research": [
        ("What did the hostel recording say remained in the room?", ["The diary", "The original", "The key", "The camera"], 2, "Listen to the voice recorder."),
        ("What connects you to the five participants?", ["Student ID", "Phone", "Medkit", "Archive card"], 1, "Inspect the participant locker."),
    ],
    "door_sim": [
        ("What was Project Zero reconstructing?", ["Buildings", "Memories", "Weather", "Passwords"], 2, "Read the Project Zero files."),
        ("Which item authorizes entry to the suite?", ["Simulation suite access code", "Medical kit", "Diary", "Photograph"], 1, "Solve the encrypted terminal first."),
    ],
    "door_zero": [
        ("The mirrored message '0 MOOR' points to?", ["Room 9", "Room 0", "Hostel", "Library"], 2, "Decode the mirror panel."),
        ("What was the final event after the experiment?", ["Warning", "Arrival", "Lockdown", "Graduation"], 3, "Inspect the memory fragments."),
    ],
    "door_control": [
        ("How many versions of the protagonist did the original recording describe?", ["One", "Two", "Three", "Four"], 2, "Listen to the original recording."),
        ("What archive evidence confirms the original reconstruction?", ["Medical kit", "Original memory map", "Library card", "Suitcase"], 2, "Inspect the archive."),
    ],
}
ITEM_CHAINS = {
    "photo": ("PHOTO RECONSTRUCTION", [
        ("How many students are in the damaged photograph?", ["Three", "Four", "Five", "Six"], 3, "Count the original participants."),
        ("Which marking appears on the reverse?", ["ROOM 0", "ROOM 8", "NEXUS", "EXIT"], 1, "Look for the room designation."),
    ]),
    "diary": ("DIARY CIPHER", [
        ("What did the diary's author agree to erase?", ["A name", "A memory", "A room", "A photo"], 2, "Read the confession."),
        ("Who does the diary say always remembers?", ["Kabir", "Mira", "Arin", "Subject 02"], 3, "Look at the folded note."),
    ]),
    "locker": ("PARTICIPANT LOCKER", [
        ("Which evidence matches the student ID?", ["Damaged photograph", "Medkit", "CCTV", "Security grid"], 1, "Compare the participant number."),
        ("How many original participants were recorded?", ["Three", "Four", "Five", "Seven"], 3, "The photograph shows the group."),
    ]),
    "files": ("PROJECT ZERO ARCHIVE", [
        ("Project Zero was a trial of what?", ["Teleportation", "Memory reconstruction", "Time travel", "Robotics"], 2, "Read the research description."),
        ("Who initiated the containment protocol?", ["Lead participant", "Security", "Librarian", "Arin"], 1, "The final report names the initiator."),
    ]),
    "recording": ("ORIGINAL RECORDING", [
        ("The recording describes how many versions of you?", ["One", "Two", "Five", "Six"], 2, "Listen to your own voice."),
        ("What does each version believe?", ["Both are copies", "Both are original", "One is original, one a copy", "Neither exists"], 3, "The recording describes their conflicting beliefs."),
    ]),
    "archive": ("MEMORY MAP RECOVERY", [
        ("Which artifact proves the Room 0 experiment occurred?", ["Original recording", "Medkit", "Library card", "Door sign"], 1, "Review the recording."),
        ("Where is the final decision made?", ["Hostel", "Library", "Control centre", "Quadrangle"], 3, "Inspect the archive map."),
    ]),
}


# General puzzle bank: these challenges are intentionally not tied to the plot.
# Each entry is (question, four options, correct option number, hint).
FUN_PUZZLES = [
    ("I have keys but no locks, space but no room. What am I?",
     ["A keyboard", "A map", "A piano case", "A hotel"], 1, "You use me to type."),
    ("What comes next? 1, 4, 9, 16, __",
     ["20", "24", "25", "36"], 3, "These are consecutive square numbers."),
    ("Which one does not belong?",
     ["Triangle", "Square", "Circle", "Cube"], 4, "Three are flat shapes."),
    ("Unscramble: L E P P A",
     ["PEARL", "APPLE", "PLATE", "PAPER"], 2, "A fruit many people like."),
    ("A farmer has 17 sheep. All but 9 run away. How many remain?",
     ["8", "9", "17", "26"], 2, "“All but 9” means 9 are left."),
    ("What has a neck but no head?",
     ["A bottle", "A shirt", "A guitar", "A river"], 1, "You can pour water into it."),
    ("Which number is the odd one out?",
     ["2", "3", "5", "9"], 4, "Three are prime numbers."),
    ("If you overtake the person in second place, what place are you in?",
     ["First", "Second", "Third", "Fourth"], 2, "You take their position."),
    ("What gets wetter as it dries?",
     ["A sponge", "A towel", "The sun", "A cloud"], 2, "You use it after a shower."),
    ("Complete the pattern: A, C, F, J, O, __",
     ["S", "T", "U", "V"], 3, "The gaps increase by one letter each time."),
    ("Which weighs more: 1 kg of iron or 1 kg of feathers?",
     ["Iron", "Feathers", "They weigh the same", "Cannot be known"], 3, "Both are exactly one kilogram."),
    ("A clock takes 5 seconds to strike 6. How long to strike 12?",
     ["10 seconds", "11 seconds", "12 seconds", "15 seconds"], 2, "There are intervals between strikes, not one per strike."),
    ("Which word becomes shorter when you add two letters?",
     ["Tiny", "Short", "Small", "Brief"], 2, "Add “er” to the word."),
    ("What has hands but cannot clap?",
     ["A statue", "A clock", "A tree", "A robot"], 2, "Look at its face to tell the time."),
    ("If 3 cats catch 3 mice in 3 minutes, how many cats catch 100 mice in 100 minutes?",
     ["1", "3", "30", "100"], 2, "Each cat catches one mouse every three minutes."),
    ("Which is the missing number? 2, 6, 12, 20, 30, __",
     ["36", "40", "42", "44"], 3, "The pattern is n × (n + 1)."),
    ("You see a boat filled with people. It has not sunk, but you don't see a single person. Why?",
     ["They are underwater", "Everyone is married", "It is a toy boat", "It is dark"], 2, "“Single” has another meaning."),
    ("Which item is most useful for measuring temperature?",
     ["Compass", "Thermometer", "Barometer", "Ruler"], 2, "It measures how hot or cold something is."),
    ("A word is spelled incorrectly in every dictionary. Which word?",
     ["Incorrectly", "Dictionary", "Spelled", "Every"], 1, "Read the question literally."),
    ("What can travel around the world while staying in one corner?",
     ["A stamp", "A suitcase", "A compass", "A postcard"], 1, "It sits on an envelope."),
    ("Complete: 81, 27, 9, 3, __",
     ["0", "1", "2", "6"], 2, "Divide by three each time."),
    ("Which pair makes 17?",
     ["8 and 8", "9 and 7", "11 and 5", "12 and 6"], 2, "Add the two numbers."),
    ("How many months have 28 days?",
     ["1", "2", "6", "12"], 4, "Every month has at least 28 days."),
    ("Which shape has the most sides?",
     ["Pentagon", "Hexagon", "Octagon", "Decagon"], 4, "Count the sides: 5, 6, 8, or 10."),
    ("A is taller than B. B is taller than C. Who is shortest?",
     ["A", "B", "C", "Cannot tell"], 3, "Follow the height comparisons."),
    ("What has one eye but cannot see?",
     ["A needle", "A potato", "A storm", "A camera"], 1, "Its eye is the hole for thread."),
    ("Which number is both even and prime?",
     ["1", "2", "4", "6"], 2, "It has exactly two positive factors."),
    ("If yesterday was Monday, what day is the day after tomorrow?",
     ["Tuesday", "Wednesday", "Thursday", "Friday"], 3, "Today is Tuesday."),
    ("Find the odd one out: Mercury, Venus, Earth, Moon.",
     ["Mercury", "Venus", "Earth", "Moon"], 4, "Three orbit the Sun as planets."),
    ("What begins with T, ends with T, and has T in it?",
     ["Teapot", "Tent", "Toast", "Ticket"], 1, "You might pour tea from it."),
]

class EchoesOfZero(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, update_rate=1/60)
        arcade.set_background_color(BG)
        self.area = "quad"
        self.player_x = 110
        self.player_y = 350
        self.keys = set()
        self.overlay = None
        self.dialogue = []
        self.dialogue_title = ""
        self.dialogue_index = 0
        self.choices = []
        self.choice_action = None
        self.active_puzzle = None
        self.grid_selected = set()
        self.hint_visible = False
        self.near_object = None
        self.health = 3
        self.inventory = []
        self.clues = []
        self.connections = []
        self.flags = {
            "message": False, "photo": False, "crossword": False, "diary": False,
            "cctv": False, "grid": False, "arin_trusted": False, "diary_shared": False,
            "locker": False, "medkit": False, "witness": False, "mira_spoken": False,
            "files": False, "binary": False, "recording": False, "kabir_spoken": False,
            "archive": False, "logs_preserved": False, "memory_accepted": False,
            "recording_revealed": False, "notice": False, "drawer": False,
            "suitcase": False, "mirror": False, "ending": None,
            "photo_kept": False, "photo_shown": False,
            "arin_neutral": False, "arin_route_open": False,
            "mira_cooperation": False, "mira_confronted": False,
            "hidden_experiment_file": False,
            "subject_zero_followed": False, "subject_zero_contact": False,
            "kabir_protected": False, "kabir_forced": False,
            "security_evidence": False, "cctv_evidence": False,
            "exit_route_found": False, "original_memory_truth": False,
        }
        self.chapter = 1
        self.status_message = "Find a way inside. Press E near objects to investigate."
        self.status_timer = 5.0
        self.load_data = None
        self.visited = {"quad"}
        self.door_stages = {}
        self.item_stages = {}
        self.active_chain = None
        self.pending_door = None
        self.pending_item = None
        self.used_fun_questions = set()
        self.selected_slot = 0
        self.show_inventory_panel = False
        self.game_over = False
        self.recovery_used = set()


    def on_draw(self):
        self.clear()
        self.draw_world()
        self.draw_hud()
        if self.overlay == "dialogue":
            self.draw_dialogue()
        elif self.overlay == "puzzle":
            self.draw_puzzle()
        elif self.overlay == "map":
            self.draw_map()
        elif self.overlay == "inventory":
            self.draw_inventory()
        elif self.overlay == "evidence":
            self.draw_evidence()
        elif self.overlay == "ending":
            self.draw_ending()
        # Always draw the Minecraft-style HUD last, above every overlay.
        self.draw_persistent_hud()
        if self.show_inventory_panel:
            self.draw_compact_inventory()
        if self.game_over:
            self.draw_game_over()

    def draw_game_over(self):
        self.draw_overlay_base()
        arcade.draw_text("MEMORY COLLAPSE", SCREEN_W/2, 430, RED, 30,
                         anchor_x="center", bold=True)
        arcade.draw_text("You failed the last-chance recovery puzzle. The lockdown overwhelms you.",
                         SCREEN_W/2, 350, WHITE, 15, anchor_x="center")
        arcade.draw_text("Your progress up to the last save is preserved.",
                         SCREEN_W/2, 300, MUTED, 13, anchor_x="center")
        arcade.draw_text("Press F9 to load your last save, or ESC to close the game.",
                         SCREEN_W/2, 220, GOLD, 13, anchor_x="center")

    def take_damage(self, amount=1, reason="Wrong answer"):
        if self.game_over:
            return
        self.health = max(0, self.health - amount)
        self.notify(f"{reason}. Health: {self.health}/3.")
        if self.health <= 0:
            # One automatic last-chance puzzle appears immediately at zero health.
            self.start_recovery_puzzle(emergency=True)

    def start_recovery_puzzle(self, emergency=False):
        if not emergency:
            if self.health >= 3:
                self.notify("Your health is already full.")
                return
            if self.area in self.recovery_used:
                self.notify("You have already used this area's recovery challenge.")
                return
        available = [i for i in range(len(FUN_PUZZLES)) if i not in self.used_fun_questions]
        if not available:
            self.used_fun_questions.clear()
            available = list(range(len(FUN_PUZZLES)))
        chosen = random.choice(available)
        self.used_fun_questions.add(chosen)
        prompt, options, correct, hint = FUN_PUZZLES[chosen]
        kind = "emergency_recovery" if emergency else "recovery"
        title = "LAST CHANCE // SOLVE TO RESTORE 1 HEART" if emergency else "RECOVERY CHALLENGE"
        self.active_chain = {"kind": kind, "id": self.area, "title": title,
                             "stages": [(prompt, options, correct, hint)], "step": 0}
        self.show_chain_step()
        if emergency:
            self.notify("LAST CHANCE: answer correctly to recover 1 heart. One attempt only.")
        else:
            self.notify("Solve this bonus puzzle correctly to restore one heart.")

    def trigger_game_over(self):
        self.game_over = True
        self.overlay = None
        self.active_chain = None
        self.status_message = "MEMORY COLLAPSE — health reached zero."
        self.status_timer = 999

    def draw_persistent_hud(self):
        # Health is fixed at the upper-left, clear of room title and map control.
        arcade.draw_rect_filled(arcade.XYWH(150, SCREEN_H-31, 280, 48), (5, 9, 20, 235))
        arcade.draw_text("HEALTH", 42, SCREEN_H-38, WHITE, 11, bold=True)
        for i in range(3):
            x = 125 + i*34
            filled = i < self.health
            color = RED if filled else (75, 55, 65)
            arcade.draw_circle_filled(x, SCREEN_H-28, 10, color)
            arcade.draw_circle_outline(x, SCREEN_H-28, 10, (245, 190, 200), 1)
        arcade.draw_text(f"{self.health}/3", 190, SCREEN_H-38, WHITE, 11)

        # A dedicated bottom hotbar. No other HUD text is drawn underneath it.
        slot_w, slot_h, gap = 58, 54, 7
        total = 9*slot_w + 8*gap
        start_x = (SCREEN_W-total)/2 + slot_w/2
        base_y = 43
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, base_y, total+24, 78),
                                (5, 8, 18, 245))
        arcade.draw_rect_outline(arcade.XYWH(SCREEN_W/2, base_y, total+24, 78),
                                 (63, 84, 112), 1)
        for i in range(9):
            x = start_x + i*(slot_w+gap)
            selected = i == self.selected_slot
            fill = (55, 79, 104, 255) if selected else (22, 31, 48, 250)
            arcade.draw_rect_filled(arcade.XYWH(x, base_y, slot_w, slot_h), fill)
            arcade.draw_rect_outline(arcade.XYWH(x, base_y, slot_w, slot_h),
                                     GOLD if selected else (100, 125, 150),
                                     3 if selected else 1)
            arcade.draw_text(str(i+1), x-slot_w/2+5, base_y-slot_h/2+4, MUTED, 8)
            if i < len(self.inventory):
                item = self.inventory[i]
                arcade.draw_circle_filled(x, base_y+8, 10,
                                          CYAN if selected else GOLD)
                label = item[:13]
                arcade.draw_text(label, x, base_y-19, WHITE, 7,
                                 anchor_x="center", width=slot_w-4)
            else:
                arcade.draw_text("—", x, base_y-5, MUTED, 13, anchor_x="center")
        arcade.draw_text("1–9 SELECT   •   I INVENTORY DETAILS",
                         SCREEN_W/2, 86, MUTED, 9, anchor_x="center")

    def draw_compact_inventory(self):
        # Small side panel; the game world remains visible.
        x, y, w, h = SCREEN_W-205, 405, 350, 300
        arcade.draw_rect_filled(arcade.XYWH(x, y, w, h), (5, 10, 22, 242))
        arcade.draw_rect_outline(arcade.XYWH(x, y, w, h), CYAN, 2)
        arcade.draw_text("INVENTORY", x-w/2+18, y+h/2-30, CYAN, 15, bold=True)
        if not self.inventory:
            arcade.draw_text("No items collected yet.", x-w/2+20, y+65, MUTED, 11)
        else:
            for i, item in enumerate(self.inventory[:12]):
                row_y = y+h/2-65-i*21
                marker = "▶" if i == self.selected_slot else "•"
                arcade.draw_text(f"{marker} {i+1}. {item}", x-w/2+20, row_y,
                                 GOLD if i == self.selected_slot else WHITE, 10)

    def draw_world(self):
        # Background and room architecture.
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, SCREEN_H/2, SCREEN_W, SCREEN_H), BG)
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, 355, SCREEN_W-70, 570), AREAS[self.area]["color"])
        # Floor tiles
        for x in range(55, SCREEN_W-40, 58):
            arcade.draw_line(x, 75, x, 635, (255, 255, 255, 12), 1)
        for y in range(85, 640, 58):
            arcade.draw_line(40, y, SCREEN_W-40, y, (255, 255, 255, 12), 1)
        # Top and bottom walls
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, 650, SCREEN_W-70, 24), (9, 14, 26))
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, 60, SCREEN_W-70, 24), (9, 14, 26))
        # Room-specific decoration
        if self.area in ("quad", "hostel"):
            for x in (145, 465, 785):
                arcade.draw_rect_filled(arcade.XYWH(x, 570, 70, 18), (37, 61, 66))
                arcade.draw_rect_filled(arcade.XYWH(x, 540, 8, 45), (76, 108, 102))
        else:
            for x in (145, 455, 765):
                arcade.draw_rect_filled(arcade.XYWH(x, 585, 170, 30), (17, 24, 42))
                arcade.draw_rect_filled(arcade.XYWH(x, 555, 150, 7), CYAN if x == 455 else (77, 96, 126))
        # Door to previous/next areas
        self.draw_door()
        # Interactive objects
        for obj in AREAS[self.area]["objects"]:
            oid, label, x, y, desc = obj
            if self.is_object_visible(oid):
                color = GOLD if oid in ("photo", "diary", "files", "recording") else CYAN
                if oid in ("arin", "mira", "kabir"):
                    color = PURPLE
                    arcade.draw_circle_filled(x, y+17, 17, (72, 55, 92))
                    arcade.draw_circle_filled(x, y+40, 12, (197, 164, 143))
                else:
                    arcade.draw_rect_filled(arcade.XYWH(x, y+12, 42, 34), (20, 30, 49))
                    arcade.draw_rect_outline(arcade.XYWH(x, y+12, 42, 34), color, 2)
                    arcade.draw_circle_filled(x, y+12, 5, color)
                arcade.draw_text(label, x, y-20, WHITE, 12, anchor_x="center")
        # Player
        arcade.draw_circle_filled(self.player_x, self.player_y, 15, (44, 65, 92))
        arcade.draw_circle_filled(self.player_x, self.player_y+5, 9, (218, 190, 168))
        arcade.draw_arc_outline(self.player_x, self.player_y, 34, 34, CYAN, 0, 360, 2)
        # vignette-ish corner darkness
        arcade.draw_text(AREAS[self.area]["name"], 55, 615, WHITE, 18, bold=True)
        arcade.draw_text(AREAS[self.area]["desc"], 55, 590, MUTED, 11)

    def is_object_visible(self, oid):
        # Hide completed one-time interactables, but keep doors and characters.
        if oid in ("door_library", "door_lab", "door_hostel", "door_research", "door_sim", "door_zero", "door_control"):
            return True
        if oid in ("arin", "mira", "kabir"):
            return True
        if oid == "crossword" and self.flags["crossword"]: return False
        if oid == "grid" and self.flags["grid"]: return False
        if oid == "medkit" and self.flags["medkit"]: return False
        if oid == "binary" and self.flags["binary"]: return False
        if oid == "notice_puzzle" and self.flags.get("notice"): return False
        if oid == "archive_drawer" and self.flags.get("drawer"): return False
        if oid == "suitcase_puzzle" and self.flags.get("suitcase"): return False
        if oid == "mirror_puzzle" and self.flags.get("mirror"): return False
        return not self.flags.get(oid, False)

    def draw_door(self):
        # A visible exit arch on the right side.
        arcade.draw_rect_filled(arcade.XYWH(1030, 355, 38, 150), (10, 16, 28))
        arcade.draw_rect_outline(arcade.XYWH(1030, 355, 38, 150), (94, 116, 145), 3)
        arcade.draw_circle_filled(1030, 355, 4, GOLD)

    def draw_hud(self):
        # The bottom strip is reserved exclusively for the hotbar.
        # Keep navigation controls away from the health display and inventory slots.
        arcade.draw_rect_filled(arcade.XYWH(1025, 665, 118, 43), (28, 67, 88))
        arcade.draw_rect_outline(arcade.XYWH(1025, 665, 118, 43), CYAN, 2)
        arcade.draw_text("MAP [M]", 1025, 657, WHITE, 14, anchor_x="center", bold=True)
        arcade.draw_text(f"CHAPTER {self.chapter}/6", SCREEN_W-155, SCREEN_H-38,
                         CYAN, 11, bold=True)
        arcade.draw_text("ROOM NAV: F1–F4   •   RECOVER: R   •   USE: U   •   DROP: X",
                         SCREEN_W/2, SCREEN_H-38, MUTED, 9, anchor_x="center")
        if self.near_object and self.overlay is None:
            arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, 118, 420, 34), (12, 20, 35))
            arcade.draw_text(f"[E] {self.near_object[1]}", SCREEN_W/2, 108,
                             CYAN, 13, anchor_x="center")
        if self.status_timer > 0 and self.overlay is None:
            arcade.draw_text(self.status_message, SCREEN_W/2, 155, GOLD, 11,
                             anchor_x="center", width=850)

    def draw_dialogue(self):
        self.draw_overlay_base()
        arcade.draw_text(self.dialogue_title, 90, 535, CYAN, 19, bold=True)
        line = self.dialogue[self.dialogue_index] if self.dialogue else ""
        arcade.draw_text(line, 90, 455, WHITE, 16, width=920, multiline=True, anchor_y="top")
        if self.choices and self.dialogue_index == len(self.dialogue)-1:
            y = 330
            for i, choice in enumerate(self.choices, 1):
                arcade.draw_text(f"{i}. {choice}", 115, y, GOLD if i == 1 else WHITE, 14)
                y -= 37
            arcade.draw_text("Press the matching number to choose.", 90, 105, MUTED, 12)
        else:
            arcade.draw_text("SPACE / ENTER to continue", 90, 130, MUTED, 12)

    def draw_puzzle(self):
        self.draw_overlay_base()
        p = self.active_puzzle
        # Keep health visible while a puzzle is open (the overlay covers the world HUD).
        arcade.draw_text("HEALTH", 850, 535, RED, 13, bold=True)
        arcade.draw_text("♥ " * self.health + "♡ " * (3-self.health),
                         930, 535, RED, 16, bold=True)
        arcade.draw_text(p["title"], 90, 535, CYAN, 20, bold=True)
        arcade.draw_text(p["prompt"], 90, 470, WHITE, 15, width=900, multiline=True, anchor_y="top")
        if p.get("grid"):
            for n in range(1, 10):
                col = (n-1) % 3
                row = (n-1) // 3
                x = 440 + col*82
                y = 330 - row*72
                fill = CYAN if n in self.grid_selected else PANEL2
                arcade.draw_rect_filled(arcade.XYWH(x, y, 58, 52), fill)
                arcade.draw_text(str(n), x, y-9, DARK if n in self.grid_selected else WHITE, 18, anchor_x="center")
            arcade.draw_text("Toggle 1-9  |  ENTER to submit", 390, 100, MUTED, 12)
        else:
            y = 355
            for i, option in enumerate(p["options"], 1):
                arcade.draw_text(f"{i}. {option}", 125, y, WHITE, 15)
                y -= 48
            arcade.draw_text("Press 1-4 to answer  |  H for hint", 90, 110, MUTED, 12)
        if self.hint_visible:
            arcade.draw_text("HINT: " + p["hint"], 90, 160, GOLD, 12, width=900, multiline=True)

    def draw_map(self):
        self.draw_overlay_base()
        arcade.draw_text("CAMPUS MAP  //  PROJECT ZERO", 90, 535, CYAN, 20, bold=True)
        nodes = [("quad", 145, 405), ("library", 375, 405),
                 ("lab", 605, 405), ("hostel", 835, 405),
                 ("research", 835, 290), ("simulation", 605, 290),
                 ("zero", 375, 290), ("control", 145, 290)]
        for i in range(len(nodes)-1):
            _, x1, y1 = nodes[i]
            _, x2, y2 = nodes[i+1]
            arcade.draw_line(x1, y1, x2, y2, (76, 104, 137), 3)
        for key, x, y in nodes:
            visited = key in self.visited
            color = GOLD if key == self.area else (CYAN if visited else PANEL2)
            arcade.draw_rect_filled(arcade.XYWH(x, y, 166, 57), color)
            arcade.draw_rect_outline(arcade.XYWH(x, y, 166, 57), WHITE if key == self.area else MUTED, 2)
            label = AREAS[key]["name"] if visited else "??? UNDISCOVERED"
            arcade.draw_text(label, x, y-5, DARK if visited or key == self.area else WHITE,
                             10, anchor_x="center", bold=key == self.area)
        arcade.draw_text("GOLD = CURRENT    CYAN = VISITED    DARK = UNKNOWN", 105, 185, MUTED, 12)
        arcade.draw_text("Press M or ESC to close. You can also click the MAP button.", 105, 125, MUTED, 12)

    def draw_inventory(self):
        self.draw_overlay_base()
        arcade.draw_text("INVENTORY", 90, 535, CYAN, 20, bold=True)
        if not self.inventory:
            arcade.draw_text("Your pockets are empty.", 110, 440, MUTED, 15)
        else:
            y = 455
            for item in self.inventory:
                arcade.draw_text("• " + item, 120, y, WHITE, 15)
                y -= 42
        arcade.draw_text("Select with 1–9  •  U = use selected item  •  X = drop selected item  •  ESC to close.",
                         90, 115, MUTED, 11)

    def draw_evidence(self):
        self.draw_overlay_base()
        arcade.draw_text("EVIDENCE BOARD", 90, 535, CYAN, 20, bold=True)
        if not self.clues:
            arcade.draw_text("No evidence collected yet. Investigate objects marked in the rooms.", 110, 440, MUTED, 14)
        else:
            y = 465
            for clue in self.clues:
                arcade.draw_text("• " + clue, 115, y, WHITE, 14)
                y -= 36
        arcade.draw_text("Connections discovered: " + (", ".join(self.connections) if self.connections else "None yet"), 90, 175, GOLD, 12, width=900, multiline=True)
        arcade.draw_text("Evidence links automatically as related clues are found. Press ESC to close.", 90, 115, MUTED, 11)

    def draw_ending(self):
        self.draw_overlay_base()
        title = self.flags["ending"] or "THE END"
        arcade.draw_text(title, SCREEN_W/2, 485, GOLD, 26, anchor_x="center", bold=True)
        arcade.draw_text(self.ending_text(), SCREEN_W/2, 390, WHITE, 15, width=820, multiline=True, anchor_x="center", anchor_y="top")
        arcade.draw_text("F5 to save your outcome, ESC to return to the title screen.", SCREEN_W/2, 135, MUTED, 12, anchor_x="center")

    def draw_overlay_base(self):
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, SCREEN_H/2, SCREEN_W, SCREEN_H), (2, 5, 13, 225))
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_W/2, SCREEN_H/2, 970, 510), PANEL)
        arcade.draw_rect_outline(arcade.XYWH(SCREEN_W/2, SCREEN_H/2, 970, 510), (61, 91, 125), 2)

    def on_update(self, delta_time):
        if self.overlay is not None:
            return
        dx = 0
        dy = 0
        if arcade.key.A in self.keys or arcade.key.LEFT in self.keys: dx -= 1
        if arcade.key.D in self.keys or arcade.key.RIGHT in self.keys: dx += 1
        if arcade.key.W in self.keys or arcade.key.UP in self.keys: dy += 1
        if arcade.key.S in self.keys or arcade.key.DOWN in self.keys: dy -= 1
        length = math.hypot(dx, dy)
        if length:
            self.player_x += dx/length * PLAYER_SPEED * delta_time
            self.player_y += dy/length * PLAYER_SPEED * delta_time
        self.player_x = max(65, min(SCREEN_W-65, self.player_x))
        self.player_y = max(105, min(610, self.player_y))
        self.near_object = self.find_nearest_object()
        if self.status_timer > 0:
            self.status_timer -= delta_time

    def find_nearest_object(self):
        nearest = None
        best = INTERACT_DISTANCE
        for obj in AREAS[self.area]["objects"]:
            oid, label, x, y, desc = obj
            if not self.is_object_visible(oid):
                continue
            d = math.hypot(self.player_x-x, self.player_y-y)
            if d < best:
                best = d
                nearest = obj
        return nearest

    def on_key_press(self, symbol, modifiers):
        if self.game_over:
            if symbol == arcade.key.F9:
                self.load_game()
                self.game_over = False
            elif symbol == arcade.key.ESCAPE:
                self.close()
            return
        if self.overlay == "dialogue":
            if self.choices and self.dialogue_index == len(self.dialogue)-1:
                if arcade.key.KEY_1 <= symbol <= arcade.key.KEY_6:
                    self.choose(symbol - arcade.key.KEY_1 + 1)
                elif symbol == arcade.key.ESCAPE:
                    self.overlay = None
            elif symbol in (arcade.key.SPACE, arcade.key.ENTER):
                self.advance_dialogue()
            elif symbol == arcade.key.ESCAPE:
                self.overlay = None
            return
        if self.overlay == "puzzle":
            if self.active_chain:
                if arcade.key.KEY_1 <= symbol <= arcade.key.KEY_4:
                    self.answer_chain(symbol - arcade.key.KEY_1 + 1)
                elif symbol == arcade.key.H:
                    self.hint_visible = True
                elif symbol == arcade.key.ESCAPE:
                    if self.active_chain.get("kind") != "emergency_recovery":
                        self.overlay = None
                        self.active_chain = None
                return
            if self.active_puzzle.get("grid"):
                if arcade.key.KEY_1 <= symbol <= arcade.key.KEY_9:
                    n = symbol - arcade.key.KEY_0
                    if n in self.grid_selected: self.grid_selected.remove(n)
                    else: self.grid_selected.add(n)
                elif symbol == arcade.key.ENTER:
                    self.submit_grid()
                elif symbol == arcade.key.H:
                    self.hint_visible = True
                elif symbol == arcade.key.ESCAPE:
                    self.overlay = None
                return
            if arcade.key.KEY_1 <= symbol <= arcade.key.KEY_4:
                self.answer_puzzle(symbol - arcade.key.KEY_1 + 1)
            elif symbol == arcade.key.H:
                self.hint_visible = True
            elif symbol == arcade.key.ESCAPE:
                self.overlay = None
            return
        if self.overlay == "map" and symbol == arcade.key.M:
            self.overlay = None
            return
        if self.overlay in ("map", "inventory", "evidence", "ending"):
            if symbol == arcade.key.ESCAPE:
                self.overlay = None
            return
        if symbol in (arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D,
                      arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.keys.add(symbol)
        elif symbol == arcade.key.E:
            self.interact()
        elif symbol in (arcade.key.F1, arcade.key.F2, arcade.key.F3, arcade.key.F4):
            direction = {
                arcade.key.F1: "north", arcade.key.F2: "south",
                arcade.key.F3: "east", arcade.key.F4: "west",
            }[symbol]
            self.navigate_room(direction)
        elif symbol == arcade.key.R:
            self.start_recovery_puzzle()
        elif symbol == arcade.key.U:
            self.use_selected_item()
        elif symbol == arcade.key.X:
            self.drop_selected_item()
        elif symbol == arcade.key.M:
            self.overlay = "map"
        elif symbol == arcade.key.I:
            self.show_inventory_panel = not self.show_inventory_panel
        elif arcade.key.KEY_1 <= symbol <= arcade.key.KEY_9:
            self.selected_slot = symbol - arcade.key.KEY_1
        elif symbol == arcade.key.TAB:
            self.overlay = "evidence"
        elif symbol == arcade.key.F5:
            self.save_game()
        elif symbol == arcade.key.F9:
            self.load_game()

    def on_mouse_press(self, x, y, button, modifiers):
        if 965 <= x <= 1085 and 642 <= y <= 690:
            self.overlay = None if self.overlay == "map" else "map"
            return
        slot_w, gap = 58, 7
        total = 9*slot_w + 8*gap
        left = (SCREEN_W-total)/2
        if 8 <= y <= 76 and left <= x <= left+total:
            self.selected_slot = min(8, max(0, int((x-left)//(slot_w+gap))))

    def on_key_release(self, symbol, modifiers):
        self.keys.discard(symbol)

    def interact(self):
        obj = self.find_nearest_object()
        if obj is None:
            self.notify("There is nothing close enough to interact with.")
            return
        oid, label, x, y, desc = obj
        if oid.startswith("dropped_"):
            item_name = desc
            if item_name not in self.inventory:
                self.inventory.append(item_name)
            AREAS[self.area]["objects"].remove(obj)
            self.notify(f"Picked up {item_name}.")
            return
        if oid.startswith("door_"):
            self.use_door(oid)
            return
        if oid in ITEM_CHAINS and not self.flags.get(oid, False):
            title, stages = ITEM_CHAINS[oid]
            self.start_chain("item", oid, title, stages)
            return
        puzzle_objects = {
            "crossword": "crossword", "grid": "grid", "medkit": "medkit",
            "binary": "binary", "notice_puzzle": "notice",
            "archive_drawer": "drawer", "suitcase_puzzle": "suitcase",
            "mirror_puzzle": "mirror",
        }
        if oid in puzzle_objects:
            self.start_puzzle(puzzle_objects[oid])
            return
        self.handle_object(oid, label, desc)

    def navigate_room(self, direction):
        """Move between connected rooms with N/S/E/W, as required by the PBL."""
        links = {
            "quad": {"east": ("library", "door_library")},
            "library": {"west": ("quad", None), "east": ("lab", "door_lab")},
            "lab": {"west": ("library", None), "east": ("hostel", "door_hostel")},
            "hostel": {"west": ("lab", None), "east": ("research", "door_research")},
            "research": {"west": ("hostel", None), "east": ("simulation", "door_sim")},
            "simulation": {"west": ("research", None), "east": ("zero", "door_zero")},
            "zero": {"west": ("simulation", None), "east": ("control", "door_control")},
            "control": {"west": ("zero", None)},
        }
        directions = {"n": "north", "s": "south", "e": "east", "w": "west",
                      "north": "north", "south": "south", "east": "east", "west": "west"}
        direction = directions.get(direction, direction)
        destination = links.get(self.area, {}).get(direction)
        if not destination:
            self.notify("There is no connected room in that direction.")
            return
        target, door_id = destination
        if door_id:
            self.use_door(door_id)
        else:
            self.enter_area(target, f"Moved {direction} into {AREAS[target]['name']}.")

    def use_selected_item(self):
        if self.selected_slot >= len(self.inventory):
            self.notify("Select an occupied inventory slot first.")
            return
        item = self.inventory[self.selected_slot]
        if item.lower() in ("medkit", "medical kit", "first-aid kit"):
            if self.health >= 3:
                self.notify("Health is already full.")
            else:
                self.health = min(3, self.health + 1)
                self.inventory.pop(self.selected_slot)
                self.selected_slot = min(self.selected_slot, max(0, len(self.inventory)-1))
                self.notify("Medkit used. Health restored by one heart.")
        elif item in ("Library access card", "Restricted access token",
                      "Simulation suite access code", "Room 0 access code"):
            self.notify(f"{item} is an access item. Approach the matching door and press E.")
        else:
            self.notify(f"{item} examined. It may be useful at a matching object or door.")

    def drop_selected_item(self):
        if self.selected_slot >= len(self.inventory):
            self.notify("Select an occupied inventory slot first.")
            return
        item = self.inventory[self.selected_slot]
        protected = {"Participant ID", "Library access card", "Restricted access token",
                     "Simulation suite access code", "Room 0 access code",
                     "Project Zero research files", "Original recording", "Original memory map"}
        if item in protected:
            self.notify("This key evidence cannot be dropped.")
            return
        self.inventory.pop(self.selected_slot)
        self.selected_slot = min(self.selected_slot, max(0, len(self.inventory)-1))
        dropped_id = f"dropped_{len(AREAS[self.area]['objects'])}_{len(self.clues)}"
        AREAS[self.area]["objects"].append(
            (dropped_id, f"Dropped: {item}", self.player_x + 48, self.player_y, item)
        )
        self.notify(f"Dropped {item}. Press E near it to pick it up again.")

    def use_door(self, door_id):
        routes = {
            "door_library": ("library", None, "The library doors open with a metallic groan."),
            "door_lab": ("lab", "crossword", "The keypad accepts your library access card."),
            "door_hostel": ("hostel", "grid", "The security route releases the hostel corridor."),
            "door_research": ("research", "witness", "The recording unlocks the research wing."),
            "door_sim": ("simulation", "binary", "The encrypted terminal opens the simulation suite."),
            "door_zero": ("zero", "fragments", "The memory sequence opens Room 0."),
            "door_control": ("control", "recording", "The original recording unlocks the control centre."),
        }
        target, requirement, message = routes[door_id]
        if requirement and not self.flags.get(requirement, False):
            self.notify("LOCKED: " + self.lock_message(requirement))
            return
        needed_items = {
            "door_lab": "Library access card",
            "door_hostel": "Restricted access token",
            "door_sim": "Simulation suite access code",
        }
        needed = needed_items.get(door_id)
        if needed and needed not in self.inventory:
            self.notify("LOCKED: Collect " + needed + " first.")
            return
        if door_id not in self.door_stages:
            self.start_chain("door", door_id, "SECURITY LOCK // " + AREAS[target]["name"], DOOR_CHAINS[door_id])
            return
        self.enter_area(target, message)

    def enter_area(self, target, message):
        self.area = target
        self.visited.add(target)
        self.player_x = 100
        self.player_y = 350
        self.chapter = AREAS[target]["chapter"]
        self.notify(message)

    def start_chain(self, kind, object_id, title, stages):
        # Choose two fresh, non-story puzzles for this interaction.
        available = [i for i in range(len(FUN_PUZZLES)) if i not in self.used_fun_questions]
        if len(available) < 2:
            self.used_fun_questions.clear()
            available = list(range(len(FUN_PUZZLES)))
        chosen = random.sample(available, 2)
        self.used_fun_questions.update(chosen)
        fresh_stages = [FUN_PUZZLES[i] for i in chosen]
        self.active_chain = {
            "kind": kind, "id": object_id, "title": title,
            "stages": fresh_stages, "step": 0
        }
        self.show_chain_step()

    def show_chain_step(self):
        chain = self.active_chain
        prompt, options, correct, hint = chain["stages"][chain["step"]]
        self.active_puzzle = {
            "title": f"{chain['title']}  |  STAGE {chain['step']+1}/{len(chain['stages'])}",
            "prompt": prompt, "options": options, "correct": correct, "hint": hint,
        }
        self.hint_visible = False
        self.overlay = "puzzle"

    def answer_chain(self, answer):
        chain = self.active_chain
        if answer != self.active_puzzle["correct"]:
            if chain["kind"] == "emergency_recovery":
                self.trigger_game_over()
                return
            self.take_damage(1, "Wrong answer")
            self.hint_visible = True
            return
        chain["step"] += 1
        if chain["step"] < len(chain["stages"]):
            self.show_chain_step()
            return
        kind, object_id = chain["kind"], chain["id"]
        self.active_chain = None
        self.overlay = None
        if kind in ("recovery", "emergency_recovery"):
            self.health = min(3, self.health + 1)
            if kind == "emergency_recovery":
                self.game_over = False
                self.notify("LAST CHANCE CLEARED! You recovered 1 heart and can continue.")
            else:
                self.recovery_used.add(object_id)
                self.notify(f"Recovery puzzle solved! +1 heart. Health: {self.health}/3.")
            return
        if kind == "door":
            self.door_stages[object_id] = True
            self.use_door(object_id)
        else:
            self.item_stages[object_id] = True
            obj = next((o for o in AREAS[self.area]["objects"] if o[0] == object_id), None)
            if obj:
                self.handle_object(object_id, obj[1], obj[4])
            if object_id in ("photo", "diary", "locker", "files", "recording", "archive"):
                item_name = {"photo": "Damaged photograph", "diary": "Student diary",
                             "locker": "Participant ID", "files": "Project Zero research files",
                             "recording": "Original recording", "archive": "Original memory map"}[object_id]
                if item_name not in self.inventory:
                    self.inventory.append(item_name)

    def lock_message(self, requirement):
        messages = {
            "crossword": "Solve the archivist's crossword first.",
            "grid": "Find the participant evidence and solve the security grid.",
            "witness": "Listen to the witness recording in the hostel.",
            "binary": "Restore the encrypted terminal in the research wing.",
            "fragments": "Reconstruct the memory sequence in the simulation suite.",
        }
        return messages.get(requirement, "You need more evidence.")

    def handle_object(self, oid, label, desc):
        self.add_clue(label)
        if oid == "message":
            self.flags[oid] = True
            self.open_dialogue("UNKNOWN NUMBER", [desc, "A second message appears: 'If you want to survive, find the photograph. Do not trust the first person who offers help.'"])
        elif oid == "photo":
            self.flags[oid] = True
            self.flags["photo_kept"] = True
            self.open_dialogue("THE DAMAGED PHOTOGRAPH", [desc, "The back of the photograph has a second line, almost erased: SUBJECT ZERO WAS NEVER THE FIRST." ])
        elif oid == "diary":
            self.flags[oid] = True
            self.add_clue("Diary confession")
            self.open_dialogue("THE DIARY", [desc, "A note is folded into the cover: 'Arin remembers. Arin always remembers.'"])
        elif oid == "cctv":
            self.flags[oid] = True
            self.flags["cctv_evidence"] = True
            self.add_clue("CCTV timestamp")
            self.flags["cctv_evidence"] = True
            self.open_dialogue("CORRUPTED CCTV", [desc, "A second figure follows you into the building. The figure has your face."])
        elif oid == "arin":
            self.open_dialogue("ARIN", ["'You shouldn't be here,' Arin whispers. 'They said the procedure worked.'", "Choose how to approach Arin."],
                               ["Trust Arin", "Ask about Room 0", "Accuse Arin", "Show the damaged photograph", "Ask what Arin remembers about you"], "arin")
        elif oid == "locker":
            self.flags[oid] = True
            self.flags["exit_route_found"] = True
            self.add_clue("Participant ID")
            self.open_dialogue("THE PARTICIPANT LOCKER", [desc, "The ID number matches the number on the damaged photograph. You were one of the five."])
        elif oid == "witness":
            self.flags[oid] = True
            self.add_clue("Witness recording")
            self.open_dialogue("VOICE RECORDER", [desc, "The final words are clearer now: 'The original is still in the room.'"])
        elif oid == "mira":
            self.flags["mira_spoken"] = True
            self.open_dialogue("DR. MIRA SEN", ["'Project Zero was designed to reconstruct a memory from recorded neural patterns.'", "'The trial did not erase memories. It created a second version of them.'", "Choose what to ask Dr. Sen."],
                               ["Why was I involved?", "Demand the original files", "Threaten to expose her", "Ask who approved the trial", "Ask whether she altered her own memories"], "mira")
        elif oid == "files":
            self.flags[oid] = True
            self.flags["logs_preserved"] = True
            self.flags["hidden_experiment_file"] = True
            self.add_clue("Project Zero participant list")
            self.add_clue("Experiment log")
            self.open_dialogue("PROJECT ZERO FILES", [desc, "The report ends abruptly: 'Containment protocol initiated by lead participant.'"])
        elif oid == "recording":
            self.flags[oid] = True
            self.flags["original_memory_truth"] = True
            self.add_clue("Original Room 0 recording")
            self.open_dialogue("THE ORIGINAL RECORDING", [desc, "The voice continues: 'One of us will wake up believing they are the original. The other will believe they are the copy.'"])
        elif oid == "kabir":
            self.flags["kabir_spoken"] = True
            self.open_dialogue("OFFICER KABIR", ["'I was guarding the wing the night of the incident.'", "'I saw two people leave. The records say one.'", "Choose how to question him."],
                               ["Who left?", "Why did you lie?", "Show the photograph", "Ask about the second person", "Ask who ordered the lockdown"], "kabir")
        elif oid == "memory":
            self.flags[oid] = True
            self.flags["memory_accepted"] = True
            self.add_clue("Altered classroom memory")
            self.open_dialogue("MEMORY RECONSTRUCTION", [desc, "You remember a hand on the emergency switch. It was yours. You cannot tell whether the memory is original or reconstructed."])
        elif oid == "fragments":
            self.flags[oid] = True
            self.add_clue("Reconstructed memory sequence")
            self.open_dialogue("MEMORY FRAGMENTS", [desc, "The fragments align. The lockdown began after the experiment, not before it."])
        elif oid == "subject_zero":
            self.open_dialogue("SUBJECT ZERO", [
                "A message appears: YOU KEEP ASKING WHO THE ORIGINAL IS. ASK WHO REMEMBERS THE FIRST WARNING.",
                "The terminal offers three responses. Your response will determine what it reveals."
            ], ["Follow the signal", "Reply and establish contact", "Disconnect the terminal"], "subject_zero")
        elif oid == "archive":
            self.flags[oid] = True
            self.add_clue("Original memory map")
            self.connections = self.make_connections()
            self.open_dialogue("AETHER ARCHIVE", [desc, "The archive reveals a final control room. The decision cannot be undone." ])
        elif oid == "final_console":
            self.flags[oid] = True
            self.connections = self.make_connections()
            self.open_final_choice()

    def make_connections(self):
        links = []
        pairs = [
            ("CCTV timestamp", "Witness recording", "The second figure entered after the first recording."),
            ("Participant ID", "Project Zero participant list", "You were one of the original five participants."),
            ("Diary confession", "Original Room 0 recording", "The memory erasure was part of a reconstruction, not a cure."),
        ]
        for a, b, meaning in pairs:
            if a in self.clues and b in self.clues:
                links.append(meaning)
        return links

    def add_clue(self, clue):
        if clue not in self.clues:
            self.clues.append(clue)
        self.connections = self.make_connections()

    def open_dialogue(self, title, lines, choices=None, action=None):
        self.dialogue_title = title
        self.dialogue = lines
        self.dialogue_index = 0
        self.choices = choices or []
        self.choice_action = action
        self.overlay = "dialogue"
        self.keys.clear()

    def advance_dialogue(self):
        if self.dialogue_index < len(self.dialogue)-1:
            self.dialogue_index += 1
        else:
            self.overlay = None
            self.choices = []

    def choose(self, number):
        action = self.choice_action
        if not action or number > len(self.choices):
            return
        if action == "ending":
            self.ending_choice(number)
            self.choice_action = None
            return

        if action == "arin":
            if number == 1:
                self.flags["arin_trusted"] = True
                self.flags["arin_route_open"] = True
                self.flags["arin_neutral"] = False
                self.add_clue("Arin's testimony")
                self.open_dialogue("ARIN", ["Arin gives you a folded note. 'I remember the night you asked us to stop the experiment. I remember you changing your mind.'", "Arin agrees to help you reach the original recording."])
            elif number == 2:
                self.flags["arin_neutral"] = True
                self.add_clue("Arin's Room 0 account")
                self.open_dialogue("ARIN", ["'Room 0 is where the second memory was made. You were the one who started the sequence.'", "Arin does not fully trust you, but leaves the information where you can find it."])
            elif number == 3:
                self.flags["arin_trusted"] = False
                self.flags["arin_route_open"] = False
                self.take_damage(1, "Arin loses trust")
                self.open_dialogue("ARIN", ["Arin steps away. 'You still think this is about what I did.' The private route is now closed."])
            elif number == 4:
                self.flags["photo_shown"] = True
                self.flags["photo_kept"] = True
                self.add_clue("Photograph shown to Arin")
                self.open_dialogue("ARIN", ["Arin goes pale. 'That photograph was taken after the trial. There were already two versions of you by then.'"])
            elif number == 5:
                self.flags["arin_neutral"] = True
                self.flags["original_memory_truth"] = True
                self.add_clue("Arin's memory of the protagonist")
                self.open_dialogue("ARIN", ["'You were frightened. You asked me to stop the trial. Then you walked back into Room 0 alone.'"])

        elif action == "mira":
            if number == 1:
                self.flags["mira_cooperation"] = True
                self.add_clue("Mira's explanation")
                self.open_dialogue("DR. MIRA SEN", ["'You volunteered because you wanted to preserve a memory of someone you had lost. The system did not behave as promised.'", "Mira gives you limited access to the research records."])
            elif number == 2:
                self.flags["mira_confronted"] = True
                self.open_dialogue("DR. MIRA SEN", ["'The files are in Room 0. I cannot give you the key.'", "Mira ends the conversation. You will need to obtain the original files independently."])
                self.add_clue("Mira withheld the original files")
            elif number == 3:
                self.flags["mira_confronted"] = True
                self.open_dialogue("DR. MIRA SEN", ["'Expose what? A recording with two versions of the same person? Who will believe you?'", "Mira becomes hostile and will no longer cooperate."])
            elif number == 4:
                self.add_clue("Trial approval record")
                self.flags["mira_confronted"] = True
                self.open_dialogue("DR. MIRA SEN", ["'The university board approved the trial. I signed the protocol, but the final sequence was activated with a participant credential.'"])
            elif number == 5:
                self.add_clue("Mira's altered memory")
                self.flags["hidden_experiment_file"] = True
                self.open_dialogue("DR. MIRA SEN", ["Mira looks away. 'I used an early version of the reconstruction process. I cannot be certain every memory I have is mine.'", "She reveals the existence of a hidden experiment file."])

        elif action == "kabir":
            if number == 1:
                self.flags["kabir_protected"] = True
                self.flags["security_evidence"] = True
                self.add_clue("Kabir's testimony")
                self.open_dialogue("OFFICER KABIR", ["'One was carried out. One walked out. I don't know which one you are.'", "Kabir trusts you enough to share a copy of the security record."])
            elif number == 2:
                self.flags["kabir_forced"] = True
                self.flags["security_evidence"] = True
                self.add_clue("Kabir's security log")
                self.open_dialogue("OFFICER KABIR", ["'Because I was told that if the second one woke up, the first one would disappear.'", "Under pressure, Kabir gives you the security log, but refuses further help."])
            elif number == 3:
                self.flags["security_evidence"] = True
                self.add_clue("Kabir's testimony")
                self.open_dialogue("OFFICER KABIR", ["Kabir looks at the photograph. 'There were five students. I counted six people that night.'"])
            elif number == 4:
                self.flags["security_evidence"] = True
                self.add_clue("Kabir's description of the second person")
                self.open_dialogue("OFFICER KABIR", ["'The second person wore your face, but moved like they had just learned how to walk. I thought it was you until they spoke.'"])
            elif number == 5:
                self.flags["security_evidence"] = True
                self.add_clue("Lockdown authorization testimony")
                self.open_dialogue("OFFICER KABIR", ["'The order came from the research director's office. The lockdown was triggered by Subject 05 — your participant credential.'"])

        elif action == "subject_zero":
            if number == 1:
                self.flags["subject_zero_followed"] = True
                self.add_clue("Subject Zero reconstruction signal")
                self.open_dialogue("SUBJECT ZERO", ["The terminal reveals a hidden CCTV timestamp and a route to the reconstruction records.", "A final message appears: THE OTHER ONE WOKE UP FIRST."])
            elif number == 2:
                self.flags["subject_zero_contact"] = True
                self.flags["subject_zero_followed"] = True
                self.flags["original_memory_truth"] = True
                self.add_clue("Subject Zero message exchange")
                self.open_dialogue("SUBJECT ZERO", ["A reply arrives instantly: 'I am not another person. I am the memory you left behind.'", "The sender transmits a fragment of the original memory."])
            elif number == 3:
                self.flags["subject_zero_followed"] = False
                self.open_dialogue("DISCONNECTED", ["The terminal goes dark. You decide to rely on physical evidence instead."])

        self.choice_action = None

    def start_puzzle(self, puzzle_id):
        self.active_puzzle = PUZZLES[puzzle_id].copy()
        self.active_puzzle["id"] = puzzle_id
        self.grid_selected = set()
        self.hint_visible = False
        self.overlay = "puzzle"

    def answer_puzzle(self, answer):
        p = self.active_puzzle
        if answer == p["correct"]:
            self.puzzle_success(p["id"])
        else:
            self.take_damage(1, "Incorrect answer — the security system shocks you")
            self.hint_visible = True

    def submit_grid(self):
        if self.grid_selected == set(self.active_puzzle["target"]):
            self.puzzle_success("grid")
        else:
            self.take_damage(1, "Incorrect pattern")
            self.hint_visible = True

    def puzzle_success(self, puzzle_id):
        self.overlay = None
        if puzzle_id == "crossword":
            self.flags["crossword"] = True
            self.flags["diary"] = False
            self.inventory.append("Library access card")
            self.add_clue("Archivist crossword solution")
        elif puzzle_id == "grid":
            self.flags["grid"] = True
            self.inventory.append("Restricted access token")
            self.add_clue("Security grid pattern")
        elif puzzle_id == "medkit":
            self.flags["medkit"] = True
            self.health = min(3, self.health+2)
            self.inventory.append("Medical kit used")
        elif puzzle_id == "binary":
            self.flags["binary"] = True
            self.inventory.append("Simulation suite access code")
            self.add_clue("Encrypted terminal access log")
        elif puzzle_id == "notice":
            self.flags["notice"] = True
            self.add_clue("Lockdown timestamp")
        elif puzzle_id == "drawer":
            self.flags["drawer"] = True
            self.add_clue("Subject 05 archive fragment")
        elif puzzle_id == "suitcase":
            self.flags["suitcase"] = True
            self.add_clue("Arin's photograph")
        elif puzzle_id == "mirror":
            self.flags["mirror"] = True
            self.add_clue("Mirrored Room 0 message")
        self.notify(self.active_puzzle["success"])

    def get_unlocked_endings(self):
        """Return only endings earned through choices and evidence gathered earlier."""
        unlocked = []

        if self.flags.get("logs_preserved") and self.flags.get("security_evidence"):
            unlocked.append(("THE EXPOSURE", "Release the complete archive to the public."))
        if self.flags.get("recording"):
            unlocked.append(("THE SILENCE", "Destroy the archive and end the experiment forever."))
        if self.flags.get("mira_cooperation") and self.flags.get("hidden_experiment_file"):
            unlocked.append(("THE SUCCESSOR", "Take control of the system and continue the research."))
        if self.flags.get("subject_zero_followed") and self.flags.get("cctv_evidence"):
            unlocked.append(("THE OTHER YOU", "Activate the duplicate reconstruction protocol."))
        if self.flags.get("exit_route_found") and "Participant ID" in self.clues:
            unlocked.append(("THE ESCAPE", "Use the service exit and leave the campus behind."))
        if (self.flags.get("arin_trusted") and self.flags.get("recording")
                and self.flags.get("original_memory_truth") and len(self.connections) >= 1):
            unlocked.append(("THE LAST MEMORY", "Reconstruct the original memory and expose the truth."))

        # Keep at least one ending reachable even if the player missed optional evidence.
        if not unlocked:
            unlocked.append(("THE ESCAPE", "Walk away through the emergency route."))
        return unlocked

    def open_final_choice(self):
        self.unlocked_endings = self.get_unlocked_endings()
        options = [description for _name, description in self.unlocked_endings]
        self.open_dialogue("THE LAST MEMORY", [
            "The archive asks for a final decision. A message appears in your own handwriting:",
            "'If you are reading this, you have reached the point where I could not decide which of us deserved to live.'",
            "Your earlier decisions have determined which outcomes are still possible."
        ], options, "ending")

    def ending_choice(self, number):
        if not hasattr(self, "unlocked_endings") or number < 1 or number > len(self.unlocked_endings):
            self.notify("That ending is not available.")
            return
        self.flags["ending"] = self.unlocked_endings[number - 1][0]
        self.overlay = "ending"

    def ending_text(self):
        endings = {
            "THE EXPOSURE": "You release the research files and security records. The university can no longer deny PROJECT ZERO. But the final recording leaves one question unanswered: which version of you gave the order?",
            "THE SILENCE": "You destroy the archive. PROJECT ZERO ends, and the memories it held disappear with it. The truth may never be known, but the experiment cannot be repeated.",
            "THE SUCCESSOR": "You take control of the system Mira built. The experiment survives under a new director. You tell yourself you will use it differently. The monitors keep recording.",
            "THE OTHER YOU": "You activate the duplicate reconstruction protocol. A second version opens its eyes on the monitor. It remembers being the original — just as you do.",
            "THE ESCAPE": "You leave through the service route. Behind you, the campus lights go dark. You survive, but the truth of Room 0 remains buried.",
            "THE LAST MEMORY": "You restore the original memory and release the truth. For the first time, you remember what happened in Room 0 — and why you chose to return."
        }
        return endings.get(self.flags.get("ending"), "The experiment is over. The memories remain.")

    def notify(self, message):
        self.status_message = message
        self.status_timer = 4.0

    def save_game(self):
        data = {
            "area": self.area, "player_x": self.player_x, "player_y": self.player_y,
            "health": self.health, "inventory": self.inventory, "clues": self.clues,
            "connections": self.connections, "flags": self.flags, "chapter": self.chapter,
            "visited": sorted(self.visited), "door_stages": self.door_stages,
            "item_stages": self.item_stages,
            "used_fun_questions": sorted(self.used_fun_questions),
            "selected_slot": self.selected_slot,
            "recovery_used": sorted(self.recovery_used),
            "unlocked_endings": getattr(self, "unlocked_endings", []),
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.notify("Game saved successfully.")
        except OSError:
            self.notify("Could not save the game. Check folder permissions.")

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            self.notify("No save file found yet. Press F5 to save.")
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.area = data.get("area", "quad")
            self.player_x = data.get("player_x", 110)
            self.player_y = data.get("player_y", 350)
            self.health = data.get("health", 3)
            self.inventory = data.get("inventory", [])
            self.clues = data.get("clues", [])
            self.connections = data.get("connections", [])
            self.flags.update(data.get("flags", {}))
            self.chapter = data.get("chapter", 1)
            self.visited = set(data.get("visited", ["quad", self.area]))
            self.door_stages = data.get("door_stages", {})
            self.item_stages = data.get("item_stages", {})
            self.used_fun_questions = set(data.get("used_fun_questions", []))
            self.selected_slot = data.get("selected_slot", 0)
            self.recovery_used = set(data.get("recovery_used", []))
            self.unlocked_endings = data.get("unlocked_endings", [])
            self.game_over = self.health <= 0
            self.active_chain = None
            self.overlay = None
            self.notify("Saved game loaded.")
        except (OSError, ValueError, KeyError):
            self.notify("Save file could not be read.")

def main():
    game = EchoesOfZero()
    arcade.run()

if __name__ == "__main__":
    main()
