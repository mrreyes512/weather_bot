import asyncio
import argparse
import os, sys
import logging
import pandas as pd
import pendulum
import urllib3
from dotenv import load_dotenv
from utils.my_llm import MY_LLM
from utils.notify import MY_CiscoWebex
from utils.my_weather import MY_Weather
import random

# Get current date
now = pendulum.now().format('YYYY-MM-DD')

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)

# Set httpx logger to ERROR level
httpx_log = logging.getLogger('httpx')
httpx_log.setLevel(logging.WARNING)

# Set webexteamssdk logger to ERROR level
webex_log = logging.getLogger('webexteamssdk')
webex_log.setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()
env_url = os.getenv("AI_COE_ENV_URL")
project_name = os.getenv("AI_COE_PROJECT_NAME")
token = os.getenv("AI_COE_TOKEN")
engine = os.getenv("AI_COE_ENGINE")
webex_token = os.getenv("WEBEX_TOKEN")

llm = MY_LLM(env_url, project_name, token)
webex = MY_CiscoWebex(access_token=webex_token)

# Active while testing
logging.getLogger().setLevel(logging.INFO)

def make_data():
    # Create a simple DataFrame
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Mark'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Austin']
    }
    df = pd.DataFrame(data)

    # Convert DataFrame to string for context
    df_context = df.to_string(index=False)
    return df_context

def force_data():
    # Create the required string
    data = """
    Current temperature in Round Rock, Tx: 77°

    3-Day Forecast:
                high  low   sunrise    sunset
    date                                     
    2025-03-21    81   40  07:33:00  19:43:00
    2025-03-22    79   53  07:32:00  19:44:00
    2025-03-23    74   62  07:31:00  19:45:00
    """
    return data

async def get_weather(city: str):
    """Fetch weather data and return the MY_Weather instance."""
    return await MY_Weather.fetch(city=city)


def weather_data():
    city = "Philadelphia, PA"
    weather = asyncio.run(get_weather(city))
    df_forecast = weather.forecast()    
    df_hourly = weather.hourly()


def main(args):
    log.info(f'Welcome to the main function')

    # city = "Los Angles, CA"
    # city = "Philadelphia, PA"
    city = "Austin, Tx"
    weather = asyncio.run(get_weather(city))
    df_forecast = weather.forecast()    
    df_hourly = weather.hourly()

    # data = make_data()
    data = df_hourly

    if args.prompt:
        prompt = f"prompts/{args.prompt}.txt"
        llm.set_prompt(prompt)

    llm.set_context(f"The date is {now}\n\nHere is some data:\n{data}")

    question_list = [
        "Today's Forecast"
    ]

    md_msg = "# Weather Report\n\n"
    md_msg += f"> City: {city} | Date: {now}\n\n"

    for question in question_list:
        answer = llm.ask_question(question)
        print(answer)
        md_msg += f"### {question}\nAI Response: {answer}\n\n---\n\n"
    
    print('-' * 90)

    # Send the markdown content as a single message
    room_name = "Webex space for Mark"
    webex.send_msg(md_msg, recipient=room_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompt', type=str, default='gordon', help='Prompt to use')
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{ "="*20 } Starting Script: { os.path.basename(__file__) } { "="*20 }')

    main(args)
