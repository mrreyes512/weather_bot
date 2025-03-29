import os
import sys
import logging
import urllib3
import pendulum
from dotenv import load_dotenv

from webex_bot.webex_bot import WebexBot
from weather import WeatherByCommand

from utils.my_logging import MY_Logger
from utils.my_llm import MY_LLM
from utils.notify import MY_CiscoWebex
from utils.my_weather import MY_Weather

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()
env_url = os.getenv("AI_COE_ENV_URL")
project_name = os.getenv("AI_COE_PROJECT_NAME")
token = os.getenv("AI_COE_TOKEN")
engine = os.getenv("AI_COE_ENGINE")
webex_token = os.getenv("WEBEX_TOKEN")
prompt_file = os.getenv("PROMPT_FILE", "prompts/default_prompt.txt")  # Default prompt file

# Initialize components
now = pendulum.now().format('YYYY-MM-DD')
llm = MY_LLM(env_url, project_name, token)
llm.set_prompt(prompt_file)  # Set the prompt file for the LLM
webex = MY_CiscoWebex(access_token=webex_token)
bot = WebexBot(webex_token, approved_users=['Mark.Reyes@evernorth.com'], log_level=logging.WARNING)

# Set up logging
directory_name = os.path.basename(os.getcwd())
log_file = os.path.join(os.getcwd(), f"{directory_name}.log")
log = MY_Logger(log_file=log_file, log_level=logging.DEBUG, detailed_logs=False).get_logger()
log.propagate = False  # Disable propagation to prevent interference from other loggers

log.info(f"Testing Logging: {now}")

# Adjust third-party loggers
logging.getLogger('webex_bot').setLevel(logging.WARNING)
logging.getLogger('webexteamssdk').setLevel(logging.ERROR)
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.INFO)  # Suppress httpcore debug logs
# logging.getLogger('httpx').setLevel(logging.WARNING)    # Suppress httpx debug logs

# Registed custom command with the bot:
bot.add_command(WeatherByCommand(log=log, llm=llm, now=now))  # Pass the logger, llm, and now to the command

# Connect to Webex & start bot listener:
bot.run()