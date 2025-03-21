import argparse
import logging
import os

from dotenv import load_dotenv
import pendulum

from utils.my_llm import MY_LLM
from utils.notify import MY_CiscoWebex

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
webex = MY_CiscoWebex(access_token=webex_token)

def main(args):

    # webex.send_msg("Hello, I am a bot. I am here to help you. this isn't scary",recipient="2024-10-18 friday demo")
    # webex.delete_msg("Y2lzY29zcGFyazovL3VzL01FU1NBR0UvZGJjMzgwZDAtZjVhMC0xMWVmLWI0MWMtZWY2N2I0YjU2ODRj")
    webex.print_rooms_table()

    # webex.remove_bot_from_room("2024-10-18 friday demo")
    # webex.remove_bot_from_room("Y2lzY29zcGFyazovL3VzL1JPT00vNTViOGI2NzAtOTA4YS0xMWVmLTllZDMtMmYxZjFmOTBkYzVh")

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
