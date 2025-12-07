import speech_recognition as sr     # For listening to user voice and converting speech to text
import pyttsx3                      # For text-to-speech, makes AURA speak out responses
import logging                      # For logging errors, events, and debugging              
import os                           # For interacting with the operating system (open files,run commands)
import sys
import datetime                     # For getting current date and time
import wikipedia                    # For fetching summaries and information from Wikipedia
import webbrowser                   # For opening URLs in the default web browser
import random                       # For selecting random jokes, music, responses, etc.
import subprocess                   # For running external applications and system-level commands
import pyautogui
import pygetwindow as gw
import google.generativeai as genai 

# Logging Configuration 

LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR,LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format = "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level= logging.INFO
)

# Activating voice from our system 

engine = pyttsx3.init("sapi5") 
engine.setProperty('rate', 170)     # Setting up new voice rate
engine.setProperty('volume', 1.0)   # Setting up volume level between 0 and 1

voices = engine.getProperty('voices')       # Getting details of current voice
engine.setProperty('voice', voices[1].id)   # Voices.index 1 for female

# Speak Function. This function convert text to speech

def speak(text):
    """This function converts text to voice
    Args:
        text
    returns:
        voice
    """
    engine.say(text)
    engine.runAndWait()

# This function recognize the speech and convert it to text 

def takeCommand():
    """This function takes command & recognize

    Returns:
        text as query
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...") 
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        logging.info(e)
        print("Say that again please")
        return "None"
    
    return query

# Greets the user when AURA starts

def greet_user():
    hour = (datetime.datetime.now().hour)
    if hour >= 5 and hour < 12:
        speak("Good morning! Let us start the day with positivity and energy.")

    elif hour >= 12 and hour <17:
        speak("Good afternoon! I hope your day is going smoothly.")

    elif hour >= 17 and hour < 21:
        speak("Good evening! I hope you had a great day.") 

    else:
        speak("Hi there! Working late or up early, I have got your back.")

    speak("I am AURA. Please tell me how may I help you today?")

# AI MODEL
def gemini_model_response(user_input):
    GEMINI_API_KEY = ""
    genai.configure(api_key=GEMINI_API_KEY) 
    model = genai.GenerativeModel("gemini-2.5-flash") 
    prompt = f"Your name is AURA, You act like AURA. Answer the provided question in short, Question: {user_input}"
    response = model.generate_content(prompt)
    result = response.text

    return result

# This function take screenshot

def take_screenshot():
    # Folder path where screenshots will be saved
    folder = "G:/CHOITY/Inception BD/Python Project/AURA-Voice-Assistant-System/screenshots"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Create a unique filename with time
    file_name = datetime.datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
    file_path = os.path.join(folder, file_name)

    # Take the screenshot
    screenshot = pyautogui.screenshot()
    
    # Save it
    screenshot.save(file_path)

    print(f"Screenshot saved: {file_path}")
    return file_path

# This function play random music from music folder

def play_music():
    music_dir = "G:\CHOITY\Inception BD\Python Project\AURA-Voice-Assistant-System\music"  
    try:
        songs = os.listdir(music_dir)
        if songs:
            random_song = random.choice(songs)
            speak(f"Playing a random song sir: {random_song}")
            os.startfile(os.path.join(music_dir, random_song))
            logging.info(f"Playing music: {random_song}")
        else:
            speak("No music files found in your music directory.")
    except Exception:
        speak("Sorry sir, I could not find your music folder.")

    
def stop_music():
    """Stops or closes the media player that is currently playing music."""

    # Kill common media player processes
    players = ["vlc.exe", "wmplayer.exe", "Music.UI.exe"]

    stopped_anything = False

    for p in players:
        try:
            result = subprocess.run(
                ["taskkill", "/f", "/im", p],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if "SUCCESS" in result.stdout:
                stopped_anything = True
        except:
            pass

    if stopped_anything:
        speak("Music stopped sir.")
        logging.info("Music stopped.")
    else:
        speak("No music is playing sir.")
        logging.info("No active media player found.")

# QUIZ GENERATOR
def quiz_me(topic_text):
    try:
        GEMINI_API_KEY = ""
        genai.configure(api_key=GEMINI_API_KEY) 
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Create 5 simple quiz questions from this text.
        Each question must have:
        - one clear question
        - one-word answer only
        - suitable for beginners
        - no long sentences
        - output in the format: question - answer

        Text:
        {topic_text}
        """

        response = model.generate_content(prompt)
        quiz_data = response.text.strip().split("\n")

        qa_pairs = []
        for line in quiz_data:
            if "-" in line:
                q, a = line.split("-", 1)
                qa_pairs.append((q.strip(), a.strip()))

            if len(qa_pairs) == 3:  # Only 3 questions for quiz
                break

        speak("Okay! Starting AI-powered quiz.")
        score = 0

        for question, correct_answer in qa_pairs:
            speak(question)
            user_answer = takeCommand().lower()

            if correct_answer.lower() in user_answer:
                speak("Correct!")
                score += 1
            else:
                speak(f"Wrong! Correct answer is {correct_answer}")

        speak(f"You scored {score} out of {len(qa_pairs)}.")
        logging.info("Smart quiz completed.")

    except Exception as e:
        speak("Sorry, quiz system faced an error.")
        print(e)


# MAIN FUNCTION
def aura_study_assistant():
    speak("Hello, I am your study assistant Aura. What topic should I explain?")

    while True:
        query = takeCommand()

        if "exit" in query or "stop" in query:
            speak("Goodbye! Study well.")
            break

        elif "quiz" in query:
            speak("Tell me the topic to quiz you on.")
            
            while True:
                topic = takeCommand()

                if topic is not None:
                    try:
                        info = wikipedia.summary(topic, sentences=10)
                        quiz_me(info)
                        break   # exit loop
                    except:
                        speak("Sorry, I could not find information on that topic.")
                else:
                    speak("Sorry, say any topic for quiz.")

        else:
            # EXPLAIN TOPIC
            try:
                speak(f"Searching for {query}")
                info = wikipedia.summary(query, sentences=5)
                speak(info)
                logging.info("User requested to explain a topic")
                
                speak("If you want a quiz on this topic, say 'quiz me'.")
            except:
                speak("Sorry, I couldn't find that. Try another topic.")

greet_user()

while True:
    query = takeCommand().lower()
    #print(query)

    # Small talk

    if "your name" in query or "who are" in query:
        speak("My name is AURA. I am your AI friend who loves assisting you with anything you say.")
        logging.info("User asked for Assistant's name")

    elif "how are you" in query:
        speak("Feeling awesome! Just waiting for your instructions like a loyal AI.")
        logging.info("User asked about assistant's well-being.")

    elif "who made" in query:
        speak("I was developed by Choity, who gave me the ability to listen, respond, and support you.")
        logging.info("User asked about assistant's creator.")
    
    elif "thank you" in query:
        speak("You are most welcome. I am always here for you.")
        logging.info("User expressed gratitude.")
    
    elif "time" in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")
        logging.info("User asked for Current time")

    # Desktop Applications


    elif "minimize" in query or "minimise" in query:
        try:
            win = gw.getActiveWindow()
            if win:
                win.minimize()
                speak("Window Minimized")
            else:
                speak("No active window found.")
        except:
            speak("Sorry, Window can not minimized")
            logging.error("Failed to minimize window")

    elif "maximize" in query or "maximise" in query:
        try:
            win = gw.getActiveWindow()
            if win:
                win.maximize()
                speak("Window maximized.")
            else:
                speak("No active window found.")
        except:
            speak("Sorry, Window can not maximized")
            logging.error("Failed to maximize window")

    elif "restore" in query or "normal size" in query:
        try:
            win = gw.getActiveWindow()
            if win:
                win.restore()
                speak("Window restored.")    
            else:
                speak("No active window found.")
        except:
            speak("Sorry, Window can not restored")
            logging.error("Failed to restore window")

    #Calculator
    elif "open calculator" in query:
        speak("Opening calculator")
        subprocess.Popen("calc.exe")
        logging.info("User requested to open Calculator.")

    # Close Calculator
    elif "close calculator" in query or "off calculator" in query:
        speak("Closing calculator")
        os.system("taskkill /f /im CalculatorApp.exe")
        speak("Calculator closed Successfully")
        logging.info("User requested to close Calculator.")

    # Notepad
    elif "open notepad" in query:
        speak("opening notepad")
        subprocess.Popen("notepad.exe")
        logging.info("User requested to open notepad")

    # Close notepad
    elif "close notepad" in query or "off notepad" in query:
        speak("Closing Notepad")
        os.system("taskkill /f /im notepad.exe")
        speak("Notepad closed Successfully")
        logging.info("User requested to close Notepad")

    # Command Prompt
    elif "open terminal" in query or "open cmd" in query or "open command prompt" in  query:
        speak("Opening Command Prompt terminal")
        subprocess.Popen(["cmd.exe"], shell=True)
        logging.info("User requested to open Command Prompt.")

    # Close Command prompt
    elif "close terminal" in query or "close cmd" in query or "off terminal" in query:
        speak("Closing Command Prompt")
        os.system("taskkill /f /im cmd.exe")
        speak("Terminal closed Successfully")
        logging.info("User requested to close Command Prompt.")

    # Web Application

    #Open calender
    elif "open calendar" in query or "calendar" in query:
        speak("Opening Windows Calendar")
        webbrowser.open("https://calendar.google.com")
        logging.info("User requested to open Calendar.")

    # Google
    elif "open google" in query: 
        webbrowser.open("https://www.google.com")
        logging.info("User requested to open Google.")

        speak("Ok, please say something if you want to open")
        search_term = takeCommand().lower()

        try:
            print(f"You said: {search_term}")

            if search_term != "":

            # Replace spaces with + for Google search URL
                search_term_url = search_term.replace(" ", "+")
                google_search_url = f"https://www.google.com/search?q={search_term_url}"
                
                webbrowser.open(google_search_url)
                speak(f"Searching Google for {search_term}")
                logging.info(f"User requested to search Google for: {search_term}")

        except:
            speak("Sorry, I could not understand or open the website")
            logging.error("Failed to open website from Google command")
    
    # Close Google
    elif "close google" in query or "close chrome" in query:
        speak("Closing Google Chrome")
        os.system("taskkill /f /im chrome.exe")
        speak("Google closed Successfully")
        logging.info("User requested to close Google Chrome.")

    # Facebook
    elif "open facebook" in query:
        speak("ok. opening facebook")
        webbrowser.open("https://www.facebook.com")
        logging.info("User requested to open Facebook.")

    # Github
    elif "open github" in query:
        speak("ok. opening github")
        webbrowser.open("github.com")
        logging.info("User requested to open GitHub.")

    
    # Wikipedia
    elif "wikipedia" in query:
        speak("Searching Wikipedia...")
        search_term = query.lower().replace("wikipedia", "").strip()
        results = wikipedia.summary(search_term, sentences=2)
        speak("According to Wikipedia")
        speak(results)
        logging.info("User requested information from Wikipedia.")


    # YouTube
    elif "youtube" in query:
        speak("Opening YouTube for you.")
        query = query.replace("youtube", "")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        logging.info("User requested to search on YouTube.")

    # For Entertainment

    # Jokes
    elif "joke" in query:
        jokes = [
            "Why was the computer cold? It left its Windows open!",
            "Why did the laptop marry the Wi-Fi? They had a strong connection!",
            "Why did the computer go to the doctor? Because it caught a virus!",
            "Why did the smartphone need glasses? It lost all its contacts!"
        ]
        speak(random.choice(jokes))
        logging.info("User requested a joke.")

    # Play Music
    elif "play music" in query:
        play_music()
    
    # Close Music
    elif "stop music" in query or "close music" in query or "stop song" in query:
        stop_music()

    # Take Screenshot and Save

    elif "screenshot" in query or "take screenshot" in query:
        speak("Taking screenshot")
        path = take_screenshot()
        speak("Screenshot saved successfully.")
    
    # Take a note
    elif "take a note" in query:
        speak("What would you like me to note down?")
        note = takeCommand()
        if note != "None":

            # For the file name: use today’s date
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            notes_dir = "notes"
            os.makedirs(notes_dir, exist_ok=True)
            file_path = os.path.join(notes_dir, f"{date_str}.txt")
            
            # Add a new line to the notes file
            with open(file_path, "a") as f:
                f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {note}\n")
            
            speak("Noted successfully!")
            logging.info(f"Note added: {note}")
    
    # Show my notes
    elif "show my note" in query:
        notes_dir = "notes"
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(notes_dir, f"{date_str}.txt")
        
        if os.path.exists(file_path):
            speak(f"Showing your notes for today:")
            with open(file_path, "r") as f:
                notes = f.readlines()
            for n in notes:
                speak(n.strip())
        else:
            speak("You have no notes for today.")

    # Delete today's notes
    elif "delete my note" in query or "clear my note" in query:
        notes_dir = "notes"
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(notes_dir, f"{date_str}.txt")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            speak("All your notes for today have been deleted successfully.")
            logging.info("User deleted today's notes.")
        else:
            speak("You have no notes for today to delete.")

    # Study Assistant
    elif "study" in query:
        aura_study_assistant()

    elif "exit" in query:
        speak("Bye! I will be here whenever you need me again.")
        logging.info("User exited the program")
        exit()

    else:
        response = gemini_model_response(query)
        speak(response)
        logging.info("User asked for others question")