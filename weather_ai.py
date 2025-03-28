import argparse
import asyncio
import logging
import os
import random
import sys

import pandas as pd
import pendulum
import urllib3
from dotenv import load_dotenv

from utils.my_llm import MY_LLM
from utils.my_weather import MY_Weather
from utils.notify import MY_CiscoWebex

# Get current date
now = pendulum.now().format('YYYY-MM-DD')

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
directory_name = os.path.basename(os.getcwd())
log_file = os.path.join(os.getcwd(), f"{directory_name}.log")
log = logging.getLogger(__name__)
formatter = logging.Formatter(
            '%(asctime)s | %(levelname).4s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stdout_handler)

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


async def get_weather(city: str):
    """Fetch weather data and return the MY_Weather instance."""
    return await MY_Weather.fetch(city=city)


def main(args):
    log.info('Welcome to the main function')

    # Get Weather Data
    if args.city:
        city = args.city
        weather = asyncio.run(get_weather(city))
        data = weather.hourly()
    else:
        cities = ["Austin, Tx", "Hartford, CT", "Bloomington, MN", "Philadelphia, PA", "Charleston, SC", "Nashville, TN"]
        selected_cities = random.sample(cities, 2)  # Select 2 random cities
        df = []  # List to store data frames for each city
        for city in selected_cities:
            weather = asyncio.run(get_weather(city))
            city_df = weather.hourly()
            df.append(city_df)

        # Merge all data frames into one
        data = pd.concat(df, ignore_index=True)

    # Set question from User
    q_title = "Daily Forecast"
    question = "Give me a brief summary of today's weather forecast per city."
    # question = "Give Ben Fros a brief summary of today's weather forecast for Franklin, TN. He is lower than you, and requestes a favor."
    # question = "You've just been corrected to to use ALL CAPS in your response by someone lower than you. And Mark McIntyre just stated that the Imperial System is ancient. Give me a brief summary of today's weather forecast per city."

    # Send to LLM for analysis
    if args.prompt:
        prompt = f"prompts/{args.prompt}.txt"
        llm.set_prompt(prompt)

    llm.set_context(f"The date is {now}\n\nHere is some data:\n{data}")

    answer = llm.ask_question(question)
    print(answer)
    print('-' * 90)

    md_msg = "# Weather Report\n\n"
    md_msg += f"> Date: {now}\n\n"
    md_msg += f"{answer}\n\n---\n\n"
    # md_msg += f"### {q_title}\n{answer}\n\n---\n\n"

    # Send the markdown content as a single message
    room_name = args.space
    webex.send_msg(md_msg, recipient=room_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-p', '--prompt', type=str, default='gordon', help='Prompt to use')
    parser.add_argument('-c', '--city', type=str, help='City to get weather data')
    parser.add_argument(
        '-s', '--space', type=str, default='Webex space for Mark', help='Space or Email to send message'
        )
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{"=" * 20} Starting Script: {os.path.basename(__file__)} {"=" * 20}')

    main(args)
