import speech_recognition as sr
import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def take_voice_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.pause_threshold = 0.8
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return ""
        try:
            query = r.recognize_google(audio)
            print(f"✅ You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("❌ Sorry, could not understand.")
            return ""
        except sr.RequestError:
            print("❌ API unavailable.")
            return ""

def open_youtube_and_play(song, max_retries=3):
    print(f"🔎 Opening YouTube and playing: {song}")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)

    search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
    driver.get(search_url)

    retries = 0
    while retries < max_retries:
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "video-title")))

            videos = driver.find_elements(By.ID, "video-title")

            for video in videos:
                title = video.get_attribute("title")
                href = video.get_attribute("href")
                if href and title:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", video)
                        time.sleep(1)
                        video.click()
                        print(f"▶️ Playing: {title}")
                        return driver  # Success
                    except Exception as click_error:
                        print(f"⚠️ Couldn't click video: {click_error}")
                        continue

            # No video clicked, try again after refresh
            retries += 1
            print(f"🔄 Retry {retries}/{max_retries}: Refreshing and retrying...")
            driver.refresh()
            time.sleep(3)

        except Exception as e:
            print(f"❌ Failed attempt: {e}")
            retries += 1
            driver.refresh()
            time.sleep(3)

    print("❌ No suitable video found after retries.")
    driver.quit()
    return None

def control_youtube_player(driver):
    print("🎧 Voice control active! Say: pause, play, skip to 2 minutes, next video, lower volume, raise volume, stop control.")
    while True:
        command = take_voice_command()
        if not command:
            continue

        if "pause" in command:
            driver.execute_script("document.querySelector('video').pause();")
            print("⏸️ Paused.")
        elif "play" in command:
            driver.execute_script("document.querySelector('video').play();")
            print("▶️ Playing.")
        elif "skip to" in command:
            match = re.search(r"skip to (\d+)", command)
            if match:
                seconds = int(match.group(1)) * 60
                driver.execute_script(f"document.querySelector('video').currentTime = {seconds};")
                print(f"⏩ Skipped to {match.group(1)} minutes.")
            else:
                print("❗ Could not parse skip time.")
        elif "next video" in command:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.ytp-next-button')
                next_button.click()
                print("⏭️ Next video.")
            except:
                print("❌ Could not click next video.")
        elif "lower volume" in command:
            driver.execute_script("var v = document.querySelector('video'); v.volume = Math.max(0, v.volume - 0.1);")
            print("🔉 Volume lowered.")
        elif "raise volume" in command or "increase volume" in command:
            driver.execute_script("var v = document.querySelector('video'); v.volume = Math.min(1, v.volume + 0.1);")
            print("🔊 Volume raised.")
        elif "stop control" in command or "exit" in command:
            print("🛑 Stopping control.")
            break
        else:
            print(f"❓ Unknown command: {command}")

def main():
    global driver
    driver = None

    print("🤖 Jarvis AI Assistant Started.")
    print("Type 't' for typing command or 'v' for voice command. Type 'exit' to quit.")

    while True:
        choice = input("Choose (t/v): ").strip().lower()
        if choice == 'exit':
            print("👋 Goodbye!")
            if driver:
                driver.quit()
            break
        elif choice not in ['t', 'v']:
            print("❌ Invalid choice, please type 't' or 'v'.")
            continue

        if choice == 't':
            command = input("Type your command: ").lower()
        else:
            command = take_voice_command()

        if not command:
            print("❗ No command detected, try again.")
            continue

        if command in ['exit', 'quit', 'bye', 'stop']:
            print("👋 Goodbye!")
            if driver:
                driver.quit()
            break

        # Check for play commands and extract song name
        song = None
        if command.startswith("open youtube and play"):
            song = command.split("open youtube and play", 1)[1].strip()
        elif command.startswith("play song"):
            song = command.split("play song", 1)[1].strip()
        elif command.startswith("play "):
            song = command.split("play ", 1)[1].strip()

        if song:
            if driver:
                driver.quit()
            driver = open_youtube_and_play(song)
            continue

        # Open YouTube homepage
        if "open youtube" == command:
            print("🌐 Opening YouTube homepage.")
            webbrowser.open("https://www.youtube.com")
            continue

        # Control YouTube player commands if driver exists
        if driver:
            if "pause" in command:
                driver.execute_script("document.querySelector('video').pause();")
                print("⏸️ Video paused.")
            elif "play" in command:
                driver.execute_script("document.querySelector('video').play();")
                print("▶️ Video playing.")
            elif "skip to" in command:
                match = re.search(r"skip to (\d+)", command)
                if match:
                    seconds = int(match.group(1)) * 60
                    driver.execute_script(f"document.querySelector('video').currentTime = {seconds};")
                    print(f"⏩ Skipped to {match.group(1)} minutes.")
                else:
                    print("❗ Could not parse skip time.")
            elif "next video" in command:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a.ytp-next-button')
                    next_button.click()
                    print("⏭️ Playing next video.")
                except Exception:
                    print("❌ Could not play next video.")
            elif "lower volume" in command:
                driver.execute_script("""
                    var video = document.querySelector('video');
                    video.volume = Math.max(0, video.volume - 0.1);
                """)
                print("🔉 Volume lowered.")
            elif "raise volume" in command or "increase volume" in command:
                driver.execute_script("""
                    var video = document.querySelector('video');
                    video.volume = Math.min(1, video.volume + 0.1);
                """)
                print("🔊 Volume raised.")
            elif "stop control" in command:
                print("🛑 Stopping voice control and closing browser.")
                driver.quit()
                driver = None
            else:
                print(f"❓ Command not recognized: {command}")
        else:
            print(f"❓ Command not recognized or no active player: {command}")

if __name__ == "__main__":
    main()


