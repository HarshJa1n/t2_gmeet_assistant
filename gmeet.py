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

    async def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)

    async def login_to_google(self):
        try:
            # self.driver.get("https://accounts.google.com")
            
            # # Enter email
            # email_field = WebDriverWait(self.driver, 20).until(
            #     EC.presence_of_element_located((By.NAME, "identifier"))
            # )
            # email_field.send_keys(self.email)
            
            # next_button = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            # )
            # next_button.click()
            
            # # Enter password
            # password_field = WebDriverWait(self.driver, 20).until(
            #     EC.presence_of_element_located((By.NAME, "password"))
            # )
            # password_field.send_keys(self.password)
            
            # signin_button = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign in')]"))
            # )
            # signin_button.click()
            
            # # Wait for the login process to complete
            # WebDriverWait(self.driver, 30).until(
            #     EC.presence_of_element_located((By.ID, "gb"))
            # )
            self.driver.get("https://accounts.google.com")

            # Wait for and fill in the email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "identifier"))
            )
            email_field.send_keys(self.email)
            # email_field.submit()
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )
            next_button.click()

            # Wait for and fill in the password field
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.password)
            # password_field.submit()
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            )
            next_button.click()
            # signin_button = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign in')]"))
            # )
            # signin_button.click()

            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("myaccount.google.com")
            )

            logging.info("Successfully logged in to Google")
        except TimeoutException as e:
            logging.error(f"Timeout during login process: {str(e)}")
            raise
        except NoSuchElementException as e:
            logging.error(f"Element not found during login process: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during login process: {str(e)}")
            raise

    async def join_meet(self):
        logging.info("Joining the meeting...")
        try:
            self.driver.get(self.meet_link)
            
            # Wait for and click the "Join now" button
            ask_to_join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ask to join')]"))
            )
            ask_to_join_button.click()

            join_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join now')]"))
            )
            join_button.click()
            logging.info("Successfully joined the meeting")
        except TimeoutException as e:
            logging.error(f"Timeout while joining the meeting: {str(e)}")
            raise
        except NoSuchElementException as e:
            logging.error(f"Join button not found: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while joining the meeting: {str(e)}")
            raise

    # ... (rest of the methods remain the same)

    async def run(self):
        try:
            await self.setup_driver()
            await self.login_to_google()
            await self.join_meet()
            
            # Start recording
            recording_task = asyncio.create_task(self.start_recording())
            
            # Record for 60 seconds (adjust as needed)
            await asyncio.sleep(60)
            
            self.stop_recording()
            await recording_task
            
            # Send audio to API and get transcription
            transcription = await self.send_audio_to_api()
            logging.info(f"Transcription: {json.dumps(transcription, indent=2)}")
            
            # Save transcription and get link
            save_response = await self.save_transcription(transcription)
            logging.info(f"Transcription saved. View link: {save_response.get('view_link')}")
        except Exception as e:
            logging.error(f"Error in run method: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

# Remove the main function from this file as it's not needed here