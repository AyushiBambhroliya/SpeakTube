import speech_recognition as sr
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.message import EmailMessage
import getpass
import re
import time
import os
import hashlib


#email
def automate_gmail_send(to_email, subject, message):
    print("📨 Automating Gmail...")

    # ✅ Use a custom Chrome profile folder
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://mail.google.com/mail/u/0/#inbox?compose=new")
        print("➡️  Gmail compose window opened")

        to_field = wait.until(EC.presence_of_element_located((By.NAME, "to")))
        to_field.send_keys(to_email)

        subj_field = driver.find_element(By.NAME, "subjectbox")
        subj_field.send_keys(subject)

        body = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[aria-label='Message Body']")
        ))
        body.click()
        body.send_keys(message)

        send_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@aria-label,'Send') and @role='button']")
        ))
        send_btn.click()

        print("✅ Email sent via Gmail automation!")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Automation error: {e}")
    finally:
        driver.quit()



# ------------------------------
# 🔊 Voice Recognition
# ------------------------------
def take_voice_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Listening...")
        r.pause_threshold = 0.8
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
        except Exception as e:
            print(f" Listening error: {e}")
            return ""
        try:
            query = r.recognize_google(audio)
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Sorry, could not understand.")
            return ""
        except sr.RequestError:
            print("API unavailable.")
            return ""

# ------------------------------
# 🔐 Password Handling
# ------------------------------
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_password(password, path):
    with open(path, 'w') as file:
        file.write(encrypt_password(password))

def check_password(input_password, path):
    if not os.path.exists(path):
        print(f"DEBUG: Password file not found at {path}")
        return False
    with open(path, 'r') as file:
        stored_hash = file.read().strip()
    input_hash = encrypt_password(input_password)
    print(f"DEBUG: Stored hash = {stored_hash}")
    print(f"DEBUG: Input hash  = {input_hash}")

    if input_hash == stored_hash:
        return True
    else:
        print("❌ Password hashes do not match.")
        return False

def first_time_setup(profile_path):
    pw_file = os.path.join(profile_path, 'password.pw')
    return not os.path.exists(pw_file)

def open_whatsapp_web():
    print("🌐 Opening WhatsApp Web...")
    webbrowser.open("https://web.whatsapp.com")

# ------------------------------
# 📩 WhatsApp Messaging
# ------------------------------
def send_whatsapp_message_to_contact(contact_name, message):
    profile_path = os.path.join(os.path.expanduser("~"), "WhatsAppUserProfile")
    pw_file = os.path.join(profile_path, 'password.pw')
    os.makedirs(profile_path, exist_ok=True)

    # First-time setup: create password + scan QR
    if first_time_setup(profile_path):
        print("🔐 First-time setup. Please set a password.")
        password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("❌ Passwords do not match.")
            return
        save_password(password, pw_file)
        print("✅ Password saved.")

        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://web.whatsapp.com")
        input("📱 Scan the QR code and press ENTER when you're logged in...")
        driver.quit()
        print("✅ Login saved. You're all set!")

    # Ask for password every time after setup
    for attempt in range(3):
        password = getpass.getpass("Enter your WhatsApp password: ")
        if check_password(password, pw_file):
            print("✅ Access granted.")
            break
        else:
            print("❌ Incorrect password.")
    else:
        print("🚫 Too many failed attempts.")
        return

    # Send the message
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://web.whatsapp.com")
        input("📱 If needed, scan the QR code, then press ENTER...")

        print(f"🔍 Searching for contact: {contact_name}")
        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.click()
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(3)

        contact = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[@title="{contact_name}"]'))
        )
        contact.click()
        time.sleep(2)

        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.send_keys(message + Keys.ENTER)

        print("✅ Message sent!")
        time.sleep(5)
        driver.quit()

    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        driver.quit()

# ------------------------------
# 📺 YouTube Handling
# ------------------------------
def open_youtube_and_play(song, max_retries=3):
    print(f"🔎 Opening YouTube and playing: {song}")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

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
                        return driver
                    except Exception as click_error:
                        print(f"⚠️ Couldn't click video: {click_error}")
                        continue
            retries += 1
            print(f"🔄 Retry {retries}/{max_retries}")
            driver.refresh()
            time.sleep(3)
        except Exception as e:
            print(f"❌ Failed attempt: {e}")
            retries += 1
            driver.refresh()
            time.sleep(3)

    print("No suitable video found.")
    driver.quit()
    return None

def control_youtube_player(driver):
    print("Say commands: pause, play, skip to X minutes, next video, stop control.")
    while True:
        command = take_voice_command()
        if not command:
            continue

        if "pause" in command:
            driver.execute_script("document.querySelector('video').pause();")
            print("⏸ Paused.")
        elif "play" in command:
            driver.execute_script("document.querySelector('video').play();")
            print("▶ Playing.")
        elif "skip to" in command:
            match = re.search(r"skip to (\d+)", command)
            if match:
                seconds = int(match.group(1)) * 60
                driver.execute_script(f"document.querySelector('video').currentTime = {seconds};")
                print(f"Skipped to {match.group(1)} minutes.")
        elif "next video" in command:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.ytp-next-button')
                next_button.click()
                print("⏭ Next video.")
            except:
                print("Could not click next video.")
        elif "stop control" in command or "exit" in command:
            print("Exiting player control.")
            break



# ------------------------------
# 🧑‍💻 Main CLI
# ------------------------------
def main():
    driver = None
    print("🤖 AI Assistant Ready.")
    print("Type 't' for text command or 'v' for voice command. Type 'exit' to quit.")

    while True:
        mode = input("Choose (t/v): ").strip().lower()

        if mode == 'exit':
            print("👋 Goodbye!")
            if driver:
                driver.quit()
            break

        if mode not in ['t', 'v']:
            print("❌ Invalid choice. Please type 't', 'v', or 'exit'.")
            continue

        if mode == 't':
            user_input = input("Type your command: ").strip()

            if user_input.lower() == "open whatsapp":
                open_whatsapp_web()

            elif user_input.lower() == "open email":
                print("📧 Opening Gmail in Chrome...")
                webbrowser.open("https://mail.google.com")
                #ai_send_email()
            #elif user_input() == "send email":
                #ai_send_email()

            elif user_input.lower() == "send email":
                to = input("To: ").strip()
                subj = input("Subject: ").strip()
                print("Message (end with a single '.' line):")
                lines = []
                while True:
                    line = input()
                    if line.strip() == ".":
                        break
                    lines.append(line)
                msg = "\n".join(lines)
                print("⚠️ Make sure you're logged into Gmail in Chrome.")
                automate_gmail_send(to, subj, msg)


                try:
                    content = user_input[len("message"):].strip()
                    contact_name, message = content.split(":", 1)
                    contact_name = contact_name.strip().title()
                    message = message.strip()
                    send_whatsapp_message_to_contact(contact_name, message)
                except Exception as e:
                    print("⚠️ Use format: message ContactName: Your message")
                    print(f"DEBUG: {e}")

            elif user_input.lower().startswith(("open youtube and play", "play song", "play ")):
                if driver:
                    driver.quit()

                if user_input.lower().startswith("open youtube and play"):
                    song = user_input[len("open youtube and play"):].strip()
                elif user_input.lower().startswith("play song"):
                    song = user_input[len("play song"):].strip()
                else:
                    song = user_input[len("play"):].strip()

                driver = open_youtube_and_play(song)
                if driver:
                    control_youtube_player(driver)

            elif user_input.lower() in ["exit", "quit", "stop"]:
                print("👋 Goodbye!")
                if driver:
                    driver.quit()
                break

            else:
                print("❌ Unknown command.")

        elif mode == 'v':
            print("🎙 Voice command mode is not implemented yet.")
            # You could implement voice commands here if you want
            if driver:
                driver.quit()

if __name__ == "__main__":
    main()


