import argparse
import logging
import os

from dotenv import load_dotenv
import pendulum

from utils.my_llm import MY_LLM
from utils.notify import GNS_CiscoWebex

# Get current date
now = pendulum.now().format('YYYY-MM-DD')

# Set up logging
log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# Set webexteamssdk logger to ERROR level
webex_log = logging.getLogger('webexteamssdk')
webex_log.setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()
webex_token = os.getenv("WEBEX_TOKEN")
webex = GNS_CiscoWebex(access_token=webex_token)

def main(args):
    bot_description = f"prompts/description_goated_bot.md"
    webex.log_bot_name() 

    with open(bot_description, 'r') as file:
        md_msg = file.read()

    room_name = "Webex space for Mark"
    webex.send_msg(md_msg, recipient=room_name)

# Example usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    # Active while testing
    logging.getLogger().setLevel(logging.INFO)

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{ "="*20 } Starting Script: { os.path.basename(__file__) } { "="*20 }')

    main(args)
