import openai
import pyttsx3
import speech_recognition as sr

# Set your API key here
openai.api_key = "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"

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("Jarvis 🤖:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand.")
        return ""
    except sr.RequestError:
        speak("Sorry, speech service is down.")
        return ""

def ask_ai(prompt):
    try:
        # New syntax for openai.ChatCompletion
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def get_input_by_mode():
    speak("Type 't' for typing or 'v' for voice input.")
    mode = input("Enter 't' for typing or 'v' for voice: ").lower()
    if mode == "v":
        speak("Okay, please speak your question now.")
        return listen(), True
    elif mode == "t":
        speak("Okay, please type your question.")
        user_input = input("You: ")
        return user_input, False
    else:
        speak("Invalid choice, defaulting to typing mode.")
        user_input = input("You: ")
        return user_input, False

def main():
    speak("Jarvis is online. Let's begin.")
    while True:
        question, voice_mode = get_input_by_mode()
        if question.strip().lower() == "exit":
            speak("Goodbye dost! Take care.")
            break
        if question.strip() == "":
            speak("No question detected. Please try again.")
            continue
        answer = ask_ai(question)
        if voice_mode:
            speak(answer)
        else:
            print("Jarvis 🤖:", answer)

if __name__ == "__main__":
    main()
