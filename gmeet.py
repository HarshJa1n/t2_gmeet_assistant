# import os
# import asyncio
# import json
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import pyaudio
# import wave
# import logging

# logging.basicConfig(level=logging.INFO)

# class GMeetBot:
#     def __init__(self, email, password, meet_link, transcribe_api_url, save_transcription_url):
#         self.email = email
#         self.password = password
#         self.meet_link = meet_link
#         self.transcribe_api_url = transcribe_api_url
#         self.save_transcription_url = save_transcription_url
#         self.driver = None
#         self.is_recording = False
#         self.frames = []
#         self.audio = pyaudio.PyAudio()

#     async def setup_driver(self):
#         chrome_options = Options()
#         chrome_options.add_argument("--use-fake-ui-for-media-stream")
#         chrome_options.add_argument("--start-maximized")
#         self.driver = webdriver.Chrome(options=chrome_options)

#     async def login_to_google(self):
#         try:
#             self.driver.get("https://accounts.google.com")

#             email_field = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "identifier"))
#             )
#             email_field.send_keys(self.email)
#             next_button = WebDriverWait(self.driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
#             )
#             next_button.click()

#             password_field = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "Passwd"))
#             )
#             password_field.send_keys(self.password)
#             next_button = WebDriverWait(self.driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
#             )
#             next_button.click()

#             WebDriverWait(self.driver, 10).until(
#                 EC.url_contains("myaccount.google.com")
#             )

#             logging.info("Successfully logged in to Google")
#         except Exception as e:
#             logging.error(f"Error during login process: {str(e)}")
#             raise

#     async def join_meet(self):
#         logging.info("Joining the meeting...")
#         try:
#             self.driver.get(self.meet_link)
            
#             join_now_button = WebDriverWait(self.driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join now')]"))
#             )
#             logging.info("Join button found")
#             join_now_button.click()

#             #             # ask_to_join_button = WebDriverWait(self.driver, 10).until(
# #             #     EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ask to join')]"))
# #             # )
# #             # ask_to_join_button.click()
#             logging.info("Successfully joined the meeting")
#         except Exception as e:
#             logging.error(f"Error while joining the meeting: {str(e)}")
#             raise

#     async def start_recording(self):
#         logging.info("Starting audio recording...")
#         self.is_recording = True
#         stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        
#         while self.is_recording:
#             data = stream.read(1024)
#             self.frames.append(data)
#             logging.info("Recording in progress...")
#             await asyncio.sleep(1)  # Log every second

#         stream.stop_stream()
#         stream.close()
#         logging.info("Recording stopped")

#     def stop_recording(self):
#         self.is_recording = False
#         logging.info("Stopping recording...")

#     async def send_audio_to_api(self):
#         logging.info("Sending audio to API for transcription...")
#         wf = wave.open("output.wav", "wb")
#         wf.setnchannels(1)
#         wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
#         wf.setframerate(44100)
#         wf.writeframes(b''.join(self.frames))
#         wf.close()

#         with open("output.wav", "rb") as audio_file:
#             files = {"file": audio_file}
#             response = requests.post(self.transcribe_api_url, files=files)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.error(f"Error in API response: {response.status_code}, {response.text}")
#             return None

#     async def save_transcription(self, transcription):
#         logging.info("Saving transcription...")
#         response = requests.post(self.save_transcription_url, json=transcription)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.error(f"Error saving transcription: {response.status_code}, {response.text}")
#             return None

#     async def run(self):
#         try:
#             await self.setup_driver()
#             await self.login_to_google()
#             await self.join_meet()
            
#             logging.info("Starting recording task...")
#             recording_task = asyncio.create_task(self.start_recording())
            
#             logging.info("Recording for 60 seconds...")
#             await asyncio.sleep(60)
            
#             self.stop_recording()
#             await recording_task
            
#             transcription = await self.send_audio_to_api()
#             if transcription:
#                 logging.info(f"Transcription: {json.dumps(transcription, indent=2)}")
                
#                 save_response = await self.save_transcription(transcription)
#                 if save_response:
#                     logging.info(f"Transcription saved. View link: {save_response.get('view_link')}")
#             else:
#                 logging.error("Failed to get transcription")
#         except Exception as e:
#             logging.error(f"Error in run method: {str(e)}")
#         finally:
#             if self.driver:
#                 self.driver.quit()
#             self.audio.terminate()
import os
import asyncio
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyaudio
import wave
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class GMeetBot:
    def __init__(self, email, password, meet_link, transcribe_api_url, save_transcription_url):
        self.email = email
        self.password = password
        self.meet_link = meet_link
        self.transcribe_api_url = transcribe_api_url
        self.save_transcription_url = save_transcription_url
        self.driver = None
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.output_directory = "recorded_audio"

    async def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)

    async def login_to_google(self):
        try:
            self.driver.get("https://accounts.google.com")

            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "identifier"))
            )
            email_field.send_keys(self.email)
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )
            next_button.click()

            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.password)
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )
            next_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.url_contains("myaccount.google.com")
            )

            logging.info("Successfully logged in to Google")
        except Exception as e:
            logging.error(f"Error during login process: {str(e)}")
            raise

    async def join_meet(self):
        logging.info("Joining the meeting...")
        try:
            self.driver.get(self.meet_link)
            
            join_now_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join now')]"))
            )
            logging.info("Join button found")
            join_now_button.click()
            logging.info("Successfully joined the meeting")
        except Exception as e:
            logging.error(f"Error while joining the meeting: {str(e)}")
            raise


    async def start_recording(self):
        logging.info("Starting audio recording...")
        self.is_recording = True
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        stream = self.audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        
        while self.is_recording:
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                self.frames.append(data)
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    logging.warning("Input overflow occurred. Some audio data was discarded.")
                else:
                    logging.error(f"IOError during recording: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error during recording: {str(e)}")

            if len(self.frames) % 100 == 0:  # Log every ~100 chunks (about 2 seconds)
                logging.info("Recording in progress...")

            await asyncio.sleep(0.01)  # Short sleep to allow other tasks to run

        stream.stop_stream()
        stream.close()
        logging.info("Recording stopped")

    def stop_recording(self):
        self.is_recording = False
        logging.info("Stopping recording...")

    def save_audio_locally(self):
        if not self.frames:
            logging.warning("No audio data to save.")
            return None

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_audio_{timestamp}.wav"
        file_path = os.path.join(self.output_directory, filename)

        wf = wave.open(file_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        logging.info(f"Audio saved locally: {file_path}")
        return file_path

    async def send_audio_to_api(self):
        logging.info("Sending audio to API for transcription...")
        # Temporarily save the audio file
        temp_file_path = self.save_audio_locally()

        with open(temp_file_path, "rb") as audio_file:
            files = {"file": audio_file}
            response = requests.post(self.transcribe_api_url, files=files)
        
        # Remove the temporary file
        os.remove(temp_file_path)

        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error in API response: {response.status_code}, {response.text}")
            return None

    async def save_transcription(self, transcription):
        logging.info("Saving transcription...")
        response = requests.post(self.save_transcription_url, json=transcription)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error saving transcription: {response.status_code}, {response.text}")
            return None

    async def run(self):
        try:
            await self.setup_driver()
            await self.login_to_google()
            await self.join_meet()
            
            logging.info("Starting recording task...")
            recording_task = asyncio.create_task(self.start_recording())
            
            logging.info("Recording for 60 seconds...")
            await asyncio.sleep(60)
            
            self.stop_recording()
            await recording_task
            
            # Save audio locally
            audio_file_path = self.save_audio_locally()
            if audio_file_path:
                logging.info(f"Audio saved at: {audio_file_path}")
            else:
                logging.warning("No audio file was saved.")

            # Commented out API calls
            # transcription = await self.send_audio_to_api()
            # if transcription:
            #     logging.info(f"Transcription: {json.dumps(transcription, indent=2)}")
            #     
            #     save_response = await self.save_transcription(transcription)
            #     if save_response:
            #         logging.info(f"Transcription saved. View link: {save_response.get('view_link')}")
            # else:
            #     logging.error("Failed to get transcription")
        except Exception as e:
            logging.error(f"Error in run method: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            self.audio.terminate()


