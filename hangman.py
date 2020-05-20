"""A hang man version with multiple languages using pygame"""
# Import necessarry library
import string
import random
import pygame
import json
from gtts import gTTS
import playsound
import os

# Define win constants
WIN_WIDTH = 900
WIN_HEIGHT = 640
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (125, 125, 125)
LIGHTGRAY = (211,211,211)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BACKGROUND_COLOR = LIGHTGRAY
AUDIO_FILE = "audio.mp3"
with open("data.json", "r", encoding="ascii") as f:
    DATA = json.load(f)

# Create the window
pygame.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  
pygame.display.set_caption("Hang man")

# Create the alphabet
alphabet = list(string.ascii_uppercase)
french_alphabet = alphabet + list("ÀÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ")
alphabet = french_alphabet
 
# Define a class for all the buttons
class Button():
    def __init__(self, color, x, y, width, height, text="",font="comicsans",text_size=60, text_color=WHITE, clock=0, cool_clr=GREY, cool_down=0):
        self.color = color
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.text = text   
        self.visible = True
        self.font = font
        self.text_size = text_size
        self.text_color = text_color
        self.cool_down = cool_down
        self.cool_clr = cool_clr
        self.clock = clock
    def draw(self, win, outline=None):
        """Draw the button on the screen"""
        if self.visible:
            if outline:
                pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4))
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
            if self.clock != 0:
                pygame.draw.rect(win, self.cool_clr, (self.x, self.y, self.clock * self.width // self.cool_down, self.height))    
            if self.text != "":
                font = pygame.font.SysFont(self.font, self.text_size)
                text = font.render(self.text, 1, self.text_color)
                win.blit(text, (self.x + (self.width - text.get_width()) // 2, self.y + (self.height - text.get_height()) // 2 + 3))
    
    def isOver(self, pos):
        """Return True if the mouse is over the button"""
        x, y = pos
        if self.visible and x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height:
            return True
        return False 

# Define a class for all the blanks
class Blank():
    def __init__(self, color, x, y, width, height, text="",font="comicsans",text_size=60):
        self.color = color
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.text = text   
        self.visible = False
        self.font = font
        self.text_size = text_size
    def draw(self, win, outline=BLACK):
        """Draw the button on the screen"""
        if outline and self.text != " ":
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4))
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        if self.visible:
            font = pygame.font.SysFont(self.font, self.text_size)
            text = font.render(self.text, 1, BLACK)
            win.blit(text, (self.x + (self.width - text.get_width()) // 2, self.y + (self.height - text.get_height()) // 2 + 3))

# A class of all the boards
class Board():
    def __init__(self, x, y, width, height, color, outline, text_list, text_gap, heading=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.outline = outline
        self.heading = heading
        self.text_list = text_list
        self.text_gap = text_gap
    def draw(self, win):
        if self.outline != None:
            pygame.draw.rect(win, self.outline, (self.x-2, self.y-2, self.width+4, self.height+4))
        
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        
        numb_lines = len(self.text_list)
        lines_height = numb_lines*(self.text_list[0].get_height()) + (numb_lines - 1)*(self.text_gap)
        
        if self.heading != None:
            heading_x = self.x + (self.width - self.heading.get_width()) // 2
            heading_y = self.y + self.height // 8
            self.heading.draw(win, heading_x, heading_y)
            line_y = (heading_y + self.heading.get_height()) +  ((self.y + self.height) - (heading_y + self.heading.get_height()) - lines_height) // 2
        else:
            line_y = self.y + (self.height - lines_height) // 2
        line_x = self.x + self.width // 10

        for text in self.text_list:
            text.draw(win,line_x,line_y)
            line_y += text.get_height() + self.text_gap
        
class Text():
    def __init__(self, content, font, size, color):
        self.content = content
        self.font = pygame.font.SysFont(font, size)
        self.text = self.font.render(content, 1, color)
    def get_height(self):
        return self.text.get_height()
    def get_width(self):
        return self.text.get_width()
    def draw(self, win, x, y):
        win.blit(self.text, (x, y))

# A function remove space (" ") from text
def removeSpace(text):
    newtext = ""
    for char in text:
        if char != " ":
            newtext += char
    return newtext

# Choose a random word from a list of words  
def chooseRandomWord():
    global used_words
    random_index = random.randint(0,len(DATA["word"][:100])-1)
    chosen_word = DATA["word"][random_index].upper()
    while chosen_word in used_words:
        random_index = random.randint(0,len(DATA["word"][:10])-1)
        chosen_word = DATA["word"][random_index].upper()
    meaning = DATA["inEnglish"][random_index]
    tts = gTTS(chosen_word, slow=True,lang="fr")
    tts.save(AUDIO_FILE)
    used_words.append(chosen_word)
    if len(used_words) == 10:
        used_words.pop(0)
    return (chosen_word, meaning)   

# Define a function update the window
def reDrawWindow():
    """Update the window every loop"""
    # Background color
    win.fill(BACKGROUND_COLOR)
    # if screen == "menu":
    #     win.blit(MENU["IMAGE"]["img"], (MENU["IMAGE"]["x"], MENU["IMAGE"]["y"]))
    if screen == "game":
        # Draw the alphabet
        for button in char_buttons:
            button.draw(win)
        
        # Draw the blanks
        for blank in blanks:
            blank.draw(win)
        
        for button in help_buttons:
            if HELP_BUTTONS["price"][button.text[:button.text.index(".")]] <= golds:
                button.text_color = GREEN
            else:
                button.text_color = RED
            button.draw(win, BLACK)

        meaning_board.draw(win, BLACK)
        stats_board.draw(win)
        # Draw the hang    
        win.blit(Hang_img["img"][wrong_answers], (Hang_img["x"],Hang_img["y"]))

    # Draw game over
    if screen == "game over":
        font = pygame.font.SysFont(GAMEOVER["font"], GAMEOVER["text_size"])
        text = font.render("GAME OVER", 1, GAMEOVER["color"])
        win.blit(text, ((WIN_WIDTH - text.get_width()) // 2, (WIN_HEIGHT - text.get_height()) // 10))
        result_board.draw(win)
        retry_button.draw(win, BLACK)
        audio_button.draw(win, BLACK)
        for blank in blanks:
            blank.draw(win)

    if screen == "results":
        for blank in blanks:
            blank.draw(win)
        result_board.draw(win)
        continue_button.draw(win, BLACK)
        audio_button.draw(win, BLACK)
    pygame.display.update()

# A function create the blanks
def creatBlanks(chosen_word):
    blanks = []
    blank_x = (WIN_WIDTH - len(chosen_word)*BLANK["width"] - (len(chosen_word)-1)*BLANK["gap"]) // 2
    for char in chosen_word:
        new_blank = Blank(BLANK["color"], blank_x, BLANK["y"], BLANK["width"], BLANK["height"], char, BLANK["font"], BLANK["text_size"])
        blanks.append(new_blank)
        blank_x += BLANK["width"] + BLANK["gap"]
    return blanks

# A function restart the game variables
def startGame():
    global chosen_word, meaning, meaning_board, blanks, screen, game_over, retry_button, continue_button, audio_button, help_buttons, wrong_answers, revealed_blanks, golds, points, result_board, cons_ans, stats_board, HELP_BUTTONS, meaning_clock, audio_clock
    if game_over:
        golds = 0
        points = 0
        cons_ans = 0
        game_over = False
    os.remove(AUDIO_FILE)
    chosen_word, meaning = chooseRandomWord()
    meaning_board = Button(WHITE, HELP_BUTTONS["x"] + HELP_BUTTONS["width"] + HELP_BUTTONS["gap"], HELP_BUTTONS["y"][1], HELP_BUTTONS["width"] - 30, HELP_BUTTONS["height"], meaning, text_size=HELP_BUTTONS["text_size"], text_color=BLACK)
    meaning_board.visible = False
    blanks = creatBlanks(chosen_word)
    screen = "game" # Screen options: ["menu", "game", "game over", "results"]
    retry_button.visible = False
    continue_button.visible = False
    audio_button.visible = False
    wrong_answers = 0
    revealed_blanks = chosen_word.count(" ")
    result_board = updateResultBoard(meaning, points, golds)
    stats_board = updateStatsBoard(cons_ans, points, golds)
    stats_board.visible = True
    for button in char_buttons:
        button.visible = True
    for button in help_buttons:
        button.visible = True
    blanks = creatBlanks(chosen_word)
    if meaning_clock > 0:
        meaning_clock -= 1
    if audio_clock > 0:
        audio_clock -= 1
    if HELP_BUTTONS["price"]["Meaning"] == 0:
        meaning_clock = MEANING_COOLDOWN
    if HELP_BUTTONS["price"]["Audio"] == 0:
        audio_clock = AUDIO_COOLDOWN
    HELP_BUTTONS["price"] = HELP_BUTTONS["base_price"].copy()
    help_buttons = updateHelpButtons()
# A function update points and golds
def updateResultBoard(meaning, points, golds):
    heading = Text("RESULT", RESULT["HEADING"]["font"], RESULT["HEADING"]["text_size"], RESULT["HEADING"]["color"])
    meaning_text = Text("Meaning: " + meaning, RESULT["TEXT"]["font"], RESULT["TEXT"]["text_size"], RESULT["TEXT"]["color"])
    points_text = Text("Points: {}".format(points), RESULT["TEXT"]["font"], RESULT["TEXT"]["text_size"], RESULT["TEXT"]["color"])
    golds_text = Text("Golds: {}".format(golds), RESULT["TEXT"]["font"], RESULT["TEXT"]["text_size"], RESULT["TEXT"]["color"])

    result_board = Board(RESULT["BOX"]["x"], RESULT["BOX"]["y"], RESULT["BOX"]["width"], RESULT["BOX"]["height"], RESULT["BOX"]["color"], RESULT["BOX"]["outline"], [meaning_text, points_text, golds_text], RESULT["TEXT"]["gap"], heading)
    return result_board

def updateStatsBoard(cons_ans, points, golds):
    heading = Text("COMBO x{}".format(cons_ans), STATS["HEADING"]["font"], STATS["HEADING"]["text_size"], STATS["HEADING"]["color"])
    points_text = Text("Points: {}".format(points), STATS["TEXT"]["font"], STATS["TEXT"]["text_size"], STATS["TEXT"]["color"])
    golds_text = Text("Golds: {}".format(golds), STATS["TEXT"]["font"], STATS["TEXT"]["text_size"], STATS["TEXT"]["color"])

    stats_board = Board(STATS["BOX"]["x"], STATS["BOX"]["y"], STATS["BOX"]["width"], STATS["BOX"]["height"], STATS["BOX"]["color"], STATS["BOX"]["outline"], [points_text, golds_text], STATS["TEXT"]["gap"], heading)
    return stats_board

# A function hide char buttons, show blanks and result board
def showResultBoard():
    global result_board
    result_board = updateResultBoard(meaning, points, golds)
    for button in char_buttons + help_buttons:                 # Hide all character buttons
        button.visible = False 
    for blank in blanks:                        # Reveal all blanks
        blank.visible = True
    
def updateHelpButtons():
    help_buttons = []
    # Create help buttons
    for i, name in enumerate(HELP_BUTTONS["name"]):
        button_text = name + ".."*(11 - len(name +"${}".format(HELP_BUTTONS["price"][name]))) + "${}".format(HELP_BUTTONS["price"][name])
        new_button = Button(HELP_BUTTONS["color"], HELP_BUTTONS["x"], HELP_BUTTONS["y"][i], HELP_BUTTONS["width"], HELP_BUTTONS["height"], button_text, HELP_BUTTONS["font"], HELP_BUTTONS["text_size"], HELP_BUTTONS["text_color"])
        if name == "Meaning":
            new_button.cool_down = MEANING_COOLDOWN
            new_button.clock = meaning_clock
        elif name == "Audio":
            new_button.cool_down = AUDIO_COOLDOWN
            new_button.clock = audio_clock
        help_buttons.append(new_button)
    return help_buttons

# Define character buttons' constants
CHAR_BUTTON = {
    "start_y": 50,
    "width"  : 45,
    "height" : 45,
    "color"  : (0, 0, 0),
    "font"   : "comicsans",
    "text_size": 55,
    "gap"    : 10,
}
CHAR_BUTTON["start_x"] = (WIN_WIDTH - 13*CHAR_BUTTON["width"] - 12*CHAR_BUTTON["gap"]) // 2

# Define blanks' constants
BLANK = {
    "width" : 50,
    "height": 50,
    "color" : WHITE,
    "font"   : "comicsans",
    "text_size": 60,
    "gap"    : 10,
}
BLANK["y"] = WIN_HEIGHT - BLANK["gap"] - BLANK["width"]

# Define game over text
GAMEOVER = {
    "font": "comicsans",
    "text_size": 120,
    "color": RED,
}

# Define result box features:
RESULT = {
    "BOX": {
        "width": 500,
        "height": 300,
        "color": WHITE,
        "outline": BLACK,
    },
    "TEXT": {
        "font": "comicsans",
        "text_size": 40,
        "color": BLACK,
        "gap": 20,
    },
    "HEADING": {
        "font": "comicsans",
        "text_size": 70,
        "color": BLACK,
    }
}
RESULT["BOX"]["x"] = (WIN_WIDTH - RESULT["BOX"]["width"]) // 2
RESULT["BOX"]["y"] = WIN_HEIGHT // 4

# Define retry button features
RETRY = {
    "color": WHITE,
    "width": 100,
    "height": 30,
    "font": "comicsans",
    "text_size": 30, 
    "text_color": BLACK,
}
RETRY["x"] = RESULT["BOX"]["x"] + RESULT["BOX"]["width"] - RETRY["width"]
RETRY["y"] = RESULT["BOX"]["y"] + RESULT["BOX"]["height"] + 15
# Define continue button's features
CONTINUE = {
    "color": WHITE,
    "width": 100,
    "height": 30,
    "font": "comicsans",
    "text_size": 30, 
    "text_color": BLACK,
}
CONTINUE["x"] = RESULT["BOX"]["x"] + RESULT["BOX"]["width"] - CONTINUE["width"]
CONTINUE["y"] = RESULT["BOX"]["y"] + RESULT["BOX"]["height"] + 15

AUDIO = {
    "color": WHITE,
    "width": 100,
    "height": 30,
    "font": "comicsans",
    "text_size": 30, 
    "text_color": BLACK,
}
AUDIO["x"] = CONTINUE["x"] - AUDIO["width"] - 15
AUDIO["y"] = RESULT["BOX"]["y"] + RESULT["BOX"]["height"] + 15

HELP_BUTTONS = {
    "color": WHITE,
    "width": 150,
    "height": 30,
    "font": "comicsans",
    "text_size": 30, 
    "text_color": BLACK,
    "name": ["Hint", "Meaning", "Audio"],
    "x": WIN_WIDTH // 15, 
    "gap": 15,
    "base_price": {
        "Hint": 5,
        "Meaning": 25,
        "Audio": 50,
    }
}
HELP_BUTTONS["y"] = [WIN_HEIGHT // 2 + i*(HELP_BUTTONS["height"] + HELP_BUTTONS["gap"]) for i in range(len(HELP_BUTTONS["name"]))]
HELP_BUTTONS["price"] = HELP_BUTTONS["base_price"].copy()

STATS = {
    "BOX": {
        "width": 180,
        "height": 150,
        "color": WHITE,
        "outline": BLACK,
    },
    "TEXT": {
        "font": "comicsans",
        "text_size": 30,
        "color": BLACK,
        "gap": 15,
    },
    "HEADING": {
        "font": "comicsans",
        "text_size": 40,
        "color": RED,
    }
}
STATS["BOX"]["x"] = 3 * WIN_WIDTH // 4
STATS["BOX"]["y"] = HELP_BUTTONS["y"][0]

BASEPOINT = 100
BASEGOLD = 2
INTEREST = 0.1
MEANING_COOLDOWN = 3
AUDIO_COOLDOWN = 5

# Load the image
Hang_img = {
    "img" : [],
    "gap" : 60,
}
for i in range(7):
    Hang_img["img"].append(pygame.image.load("hangman{}.png".format(i)))
Hang_img["width"], Hang_img["height"] = Hang_img["img"][0].get_rect().size
Hang_img["x"] = (WIN_WIDTH - Hang_img["width"]) // 2
Hang_img["y"] = (BLANK["y"] - Hang_img["gap"] - Hang_img["height"])

# MENU = {
#     "IMAGE": {
#         "img": Hang_img["img"][random.randint(0,6)],
#         "x": Hang_img["x"],
#         "y": WIN_HEIGHT // 15,
#         "width": Hang_img["width"],
#         "height": Hang_img["height"]
#     },
#     "BUTTON": {},
# }

# Create the alphabet buttons
char_buttons = []
button_x = CHAR_BUTTON["start_x"]
button_y = CHAR_BUTTON["start_y"]
for i, char in enumerate(alphabet):
    char_buttons.append(Button(CHAR_BUTTON["color"], button_x, button_y, CHAR_BUTTON["width"], CHAR_BUTTON["height"], char, CHAR_BUTTON["font"], CHAR_BUTTON["text_size"]))
    if i % 13 == 12:
        remaining_letters = len(alphabet) - i - 1
        button_y += CHAR_BUTTON["height"] + CHAR_BUTTON["gap"] 
        if remaining_letters >= 13:
            button_x = CHAR_BUTTON["start_x"]
        else:
            button_x = (WIN_WIDTH - remaining_letters*CHAR_BUTTON["width"] - (remaining_letters - 1)*CHAR_BUTTON["gap"]) // 2
    else:
        button_x += CHAR_BUTTON["width"] + CHAR_BUTTON["gap"]

# Create retry button
retry_button = Button(RETRY["color"], RETRY["x"], RETRY["y"], RETRY["width"], RETRY["height"], "Retry", RETRY["font"], RETRY["text_size"], RETRY["text_color"])

# Create continue button
continue_button = Button(CONTINUE["color"], CONTINUE["x"], CONTINUE["y"], CONTINUE["width"], CONTINUE["height"], "Continue", CONTINUE["font"], CONTINUE["text_size"], CONTINUE["text_color"])

# Create audio button
audio_button = Button(AUDIO["color"], AUDIO["x"], AUDIO["y"], AUDIO["width"], AUDIO["height"], "Audio", AUDIO["font"], AUDIO["text_size"], AUDIO["text_color"])

# Define sound effects
correct_sound = pygame.mixer.Sound("correct_sound.wav")
correct_sound.set_volume(0.1)
wrong_sound = pygame.mixer.Sound("wrong_sound.wav")
wrong_sound.set_volume(0.1)
music = pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

# Game variables
used_words = []
chosen_word, meaning = chooseRandomWord()
meaning_board = Button(WHITE, HELP_BUTTONS["x"] + HELP_BUTTONS["width"] + HELP_BUTTONS["gap"], HELP_BUTTONS["y"][1], HELP_BUTTONS["width"] - 30, HELP_BUTTONS["height"], meaning, text_size=HELP_BUTTONS["text_size"], text_color=BLACK)
meaning_board.visible = False
blanks = creatBlanks(chosen_word)
screen = "game" # Screen options: ["menu", "game", "game over", "results"]
game_over = False
retry_button.visible = False
continue_button.visible = False
audio_button.visible = False
wrong_answers = 0
revealed_blanks = chosen_word.count(" ")
golds = 0
points = 0
result_board = updateResultBoard(meaning, points, golds)
cons_ans = 0
stats_board = updateStatsBoard(cons_ans, points, golds)
stats_board.visible = True
meaning_clock = 0
audio_clock = 0
help_buttons = updateHelpButtons()

# Main loop
RUN = True
while RUN:
    # Get all the event in the game
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos() # Get mouse positon
        if event.type == pygame.QUIT:
            RUN = False
            pygame.quit()
            quit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if any character button is clicked
            for button in char_buttons:
                if button.isOver(pos):
                    button.visible = False                  # Hide that button
                    if button.text in chosen_word:              # If that letter is correct
                        correct_sound.play()                        # Play correct sound
                        cons_ans += 1
                        earned_point = BASEPOINT*cons_ans
                        earned_gold = BASEGOLD*cons_ans
                        for i, char in enumerate(chosen_word):       # Reveal the blank(s)   
                            if char == button.text:
                                points += earned_point
                                golds += earned_gold
                                blanks[i].visible = True
                                revealed_blanks += 1                # Increase correct answer
                        if revealed_blanks == len(chosen_word):     # If all the letters are guessed
                            screen = "results"                          # Change the screen to result screen
                            showResultBoard()
                            stats_board.visible = False
                            continue_button.visible = True
                            audio_button.visible = True
                    else:                                       # Else if that letter is wrong 
                        wrong_sound.play()                          # Play wrong sound 
                        wrong_answers += 1                          # Increase wrong answer
                        cons_ans = 0    
                        if wrong_answers == 6:                      # If failed
                            game_over = True                            # Game over    
                            screen = "game over"                        # Change the screen                     
                            showResultBoard()
                            stats_board.visible = False
                            retry_button.visible = True                 # Show retry option
                            audio_button.visible = True 
                    stats_board = updateStatsBoard(cons_ans, points, golds)                    
            if retry_button.isOver(pos):                       # If retry button is clicked
                playsound.playsound(AUDIO_FILE)
                startGame()                                         # Restart game
            if audio_button.isOver(pos):
                playsound.playsound(AUDIO_FILE)
            if continue_button.isOver(pos):
                playsound.playsound(AUDIO_FILE)
                startGame()
            for i, button in enumerate(help_buttons):
                if button.isOver(pos):
                    if "Hint" in button.text:
                        if HELP_BUTTONS["price"]["Hint"] <= golds:
                            golds -= HELP_BUTTONS["price"]["Hint"]
                            HELP_BUTTONS["price"]["Hint"] *= 2
                            random_char = random.choice(chosen_word)
                            random_blank = blanks[chosen_word.index(random_char)]
                            while random_blank.visible:
                                random_char = random.choice(chosen_word)
                                random_blank = blanks[chosen_word.index(random_char)]
                            for blank in blanks:
                                if blank.text == random_char:
                                    blank.visible = True
                                    revealed_blanks += 1
                            for button in char_buttons:
                                if button.text == random_blank.text:
                                    button.visible = False
                            if revealed_blanks == len(chosen_word):     # If all the letters are guessed
                                screen = "results"                          # Change the screen to result screen
                                showResultBoard()
                                continue_button.visible = True
                                audio_button.visible = True
                    if "Meaning" in button.text:
                        if HELP_BUTTONS["price"]["Meaning"] <= golds and meaning_clock == 0:
                            meaning_board.visible = True
                            golds -= HELP_BUTTONS["price"]["Meaning"]
                            HELP_BUTTONS["price"]["Meaning"] = 0
                    if "Audio" in button.text:
                        if HELP_BUTTONS["price"]["Audio"] <= golds and audio_clock == 0:
                            playsound.playsound(AUDIO_FILE)
                            golds -= HELP_BUTTONS["price"]["Audio"]
                            HELP_BUTTONS["price"]["Audio"] = 0
                    stats_board = updateStatsBoard(cons_ans, points, golds) 
                    help_buttons = updateHelpButtons()
        # Check if any button is hovered and change the color
        if event.type == pygame.MOUSEMOTION:
            for button in char_buttons:
                if button.isOver(pos):
                    button.color = GREY
                else:
                    button.color = BLACK
            for button in [retry_button, continue_button, audio_button] + help_buttons:
                if button.isOver(pos):
                    button.color = GREY
                else:
                    button.color = WHITE

    # Update the window
    reDrawWindow()   
