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


def ask_additional_recipients(md_msg):
    """
    Ask the user if the message should be sent to additional recipients.
    
    Args:
        md_msg (str): The message to send.
    """
    while True:
        try:
            another_recipient = input("Would you like to send this message to anyone else? (y/n):\n").strip().lower()
            if another_recipient == 'y':
                new_recipient = input("\n\n> Enter the email or space name of the new recipient:\n").strip()
                webex.send_msg(md_msg, recipient=new_recipient)
            elif another_recipient == 'n':
                log.info("No additional recipients.")
                break
            else:
                print("Invalid input. Please press 'y' or 'n'.")
        except KeyboardInterrupt:
            log.warning("Operation canceled by user.")
            break

def confirm_send_msg(args, statement):
    """
    Confirm with the user before sending the message and regenerate the message if needed.

    Args:
        args: Parsed command-line arguments.
        absttract_statement: The initial abstract statement provided by the user.

    Returns:
        str: The final abstracted message.
    """
    while True:
        try:
            print(f"Message target: {args.space}")
            user_input = input("Press 'y' to send message, 'a' to try again, or Ctrl+C to cancel:\n").strip().lower()
            if user_input == 'y':
                return statement  # Final message to send
            elif user_input == 'a':
                statement = llm.ask_question(statement)
                print('-' * 90)
                print(f"Abstracted Message:\n{statement}")
                print('-' * 90)
                
            else:
                print("Invalid input. Please press 'y' or 'a'.")
        except KeyboardInterrupt:
            log.warning("Message not sent...")
            sys.exit(1)

def main(args):
    log.info('Welcome to the main function')
    log.info(f"Message target: {args.space}")

    # Set User from Space
    if '@' in args.space:
        first = args.space.split('.')[0].capitalize()

    # Set the Prompt
    prompt = f"prompts/{args.prompt}.txt"
    if not os.path.exists(prompt):
        log.error(f"Prompt file not found: {prompt}")
        sys.exit(1)

    llm.set_prompt(prompt)
    llm.set_context(f"The date is {now}. This message is directed to: {first}.")

    if args.message:
        absttract_statement = args.message
    else:
        print('-' * 90)
        print(f"Message to abstract to: {args.space}\n")
        print("Example: 'You are doing great, keep up the good work!'")
        absttract_statement = input(f"Type below...\n\n")
        print('-' * 90)

    
    statement = llm.ask_question(absttract_statement)

    print('-' * 90)
    print(f"Abstracted Message:\n{statement}")
    print('-' * 90)

    # confirm_send_msg(args, statement)

    md_msg = f"{statement}\n\n---\n\n"

    # Preview message prior to sending
    reviewer = 'mark.reyes@evernorth.com'
    webex.send_msg(md_msg, recipient=reviewer)

    # Call the function to ask for additional recipients
    ask_additional_recipients(md_msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-p', '--prompt', type=str, default='gordon_motivational', help='Prompt to use')
    parser.add_argument('-m', '--message', type=str, help='Message to abstract')
    parser.add_argument(
        '-s', '--space', type=str, default='mark.reyes@evernorth.com', help='Space or Email to send message'
        )
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{"=" * 20} Starting Script: {os.path.basename(__file__)} {"=" * 20}')

    main(args)
