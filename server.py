from flask import Flask, request, jsonify
import asyncio
from gmeet import GMeetBot
import logging

app = Flask(__name__)

# Global variables for API URLs
TRANSCRIBE_API_URL = "https://your-api-url.com/transcribe"
SAVE_TRANSCRIPTION_URL = "https://your-api-url.com/save-transcription"

# Bot credentials
BOT_EMAIL = "cjain012003@gmail.com"
BOT_PASSWORD = "Chris@321"


logging.basicConfig(level=logging.INFO)

@app.route('/receive-meeting-code', methods=['POST'])
def receive_meeting_code():
    data = request.json
    meeting_code = data.get('meetingCode')
    if meeting_code:
        try:
            # Trigger the bot to join the meeting
            asyncio.run(run_bot(meeting_code))
            return jsonify({"status": "success", "message": "Bot joined the meeting"}), 200
        except Exception as e:
            logging.error(f"Error while running the bot: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "No meeting code provided"}), 400

async def run_bot(meeting_code):
    meet_link = f"https://meet.google.com/{meeting_code}"
    
    bot = GMeetBot(BOT_EMAIL, BOT_PASSWORD, meet_link, TRANSCRIBE_API_URL, SAVE_TRANSCRIPTION_URL)
    await bot.run()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)