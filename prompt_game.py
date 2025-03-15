import argparse
import os, sys
import logging
import pandas as pd
import pendulum
import urllib3
from dotenv import load_dotenv
from utils.my_llm import MY_LLM
from utils.notify import GNS_CiscoWebex
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
webex = GNS_CiscoWebex(access_token=webex_token)

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

def main(args):
    log.info(f'Welcome to the main function')

    data = make_data()

    if args.prompt:
        prompt = f"prompts/{args.prompt}.txt"
        llm.set_prompt(prompt)

    llm.set_context(f"The date is {now}\n\nHere is some data:\n{data}")

    question_list = [
        "What is the capital of Texas?",
        "What is the date for next monday?",
        "Who is the wisest person in the data?",
        "Who lives in the Big Apple?",
        "Who would have a cowboy hat in their closet?",
        "Who has the best pizza?"
    ]

    if args.prompt:
        md_msg = "# LLM Prompt Game\n\n"
        md_msg += "> Read the response below to guess my Personal Prompt\n\n"
    else:
        md_msg = "# LLM Response Demo\n\n"
    
    questions = random.sample(question_list, 2)
    for question in questions:
        answer = llm.ask_question(question)
        print(answer)
        md_msg += f"### Question: {question}\nAI Response: {answer}\n\n---\n\n"
    
    print('-' * 90)
    
    if args.prompt:
        md_msg += f"### What is my Prompt?\n\n"
        md_msg += "> Reply to this message with guesses"

    # Send the markdown content as a single message
    room_name = "Webex space for Mark"
    webex.send_msg(md_msg, recipient=room_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompt', type=str, help='Prompt to use')
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{ "="*20 } Starting Script: { os.path.basename(__file__) } { "="*20 }')

    main(args)
