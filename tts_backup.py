import speech_recognition as sr
import pyttsx3
import random

# === TEXT TO SPEECH SETUP ===
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

def speak(text):
    print(f"\nRobot Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# === SPEECH TO TEXT SETUP ===
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    with mic as source:
        print("🎤 Listening for response...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        response = recognizer.recognize_google(audio)
        print(f"Victim: {response}")
        return response
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand.")
        return "No response"
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return "No response"

# === QUESTIONS ===
alternative_questions = {
    0: [
        "Hi, I'm a rescue robot. I'm here to help you. I will ask you questions and please answer yes or no. Have you been hurt?",
        "Hello, I'm here to assist you as a rescue robot. Do you have any injuries?"
    ],
    1: ["Can you describe the type of injuries you have?"],
    2: ["Are you experiencing difficulty breathing?"],
    3: ["Are you stuck somewhere?"],
    4: ["Can you walk and come with me?"],
    5: ["Are there other victims inside the building?"],
    6: ["Stay here and wait—emergency responders know you're here and are on their way."],
    7: ["Come with me, I'll guide you to the exit for your safety."]
}

victim_situation = {
    "Location": ["Latitude 34.0522, Longitude -118.2437"],
    "Injuries": [],
    "People in Surroundings": [],
    "Robot Action": [],
    "Mobility": [],
    "Breathing": [],
    "Consciousness": [], 
    "Immediate Danger": [],
    "Priority": ["Unknown"],
}

def analyze_response(response):
    response = response.lower()
    if "no" in response:
        return "negative"
    if "yes" in response or "i can" in response:
        return "positive"
    return "unknown"

def select_node(last_node, last_answer, mobility):
    if last_node == 0 and last_answer == "negative":
        return 2, mobility
    if last_node == 3 and last_answer == "positive":
        mobility = False
        return 5, mobility
    if last_node == 4 and last_answer == "positive":
        mobility = True    
    if last_node == 5:
        return (7 if mobility else 6), mobility
    return last_node + 1, mobility

def interact(node, n):
    question = alternative_questions[node][n]
    
    repeat = False
    while True:
        if not repeat:
            speak(question)
        response = listen()
        status = analyze_response(response)

        # If we get a valid response, break the loop
        if response != "No response":
            break
        repeat = True
        speak("I didn't catch that. Could you please repeat?")

    # Save information based on the node
    if node == 1:
        victim_situation["Injuries"].append(response)
        victim_situation["Consciousness"].append("Conscious")
    elif node == 2:
        victim_situation["Breathing"].append("Trouble Breathing" if status == "positive" else "No trouble")
    elif node == 3:
        if status == "positive":
            victim_situation["Immediate Danger"].append("Possibly stuck")
            victim_situation["Robot Action"].append("Wait for responder")
            victim_situation["Mobility"].append("Cannot walk")
        else:
            victim_situation["Immediate Danger"].append("Unknown")
    elif node == 4:
        if status == "positive":
            victim_situation["Mobility"].append("Can walk")
            victim_situation["Robot Action"].append("Guide victim")
        else:
            victim_situation["Mobility"].append("Cannot walk")
            victim_situation["Robot Action"].append("Wait for responder")
    elif node == 5:
        victim_situation["People in Surroundings"].append("Others present" if status == "positive" else "None nearby")
    
    return status


def interaction_tree(start_node=-1, last_answer="positive"):
    mobility = None
    node = start_node
    while True:
        print("Current node:", node)
        node, mobility = select_node(node, last_answer, mobility)
        print("Changed node:", node)
        question_n = random.randint(0, len(alternative_questions[node]) - 1)
        last_answer = interact(node, question_n)
        if node == 6 or node == 7:
            break
    
    print("\n✅ Victim status report:")
    for key, val in victim_situation.items():
        print(f"{key}: {val}")

interaction_tree()
