import json
import logging
import asyncio
from utils.my_weather import MY_Weather

import requests
from webex_bot.models.command import Command

log = logging.getLogger(__name__)

class WeatherByCommand(Command):
    def __init__(self, log=None, llm=None, now=None):

        super().__init__(
            command_keyword="weather",
            help_message="Get weather by City. Usage: 'weather {City}'",
            card=None,
        )
        self.log = log
        self.llm = llm
        self.now = now

    async def get_weather(self, city: str):
        """Fetch weather data and return the MY_Weather instance."""
        return await MY_Weather.fetch(city=city)

    def execute(self, message, attachment_actions, activity):
        user_email = activity["actor"]["emailAddress"]
        first_name = user_email.split(".")[0].title()
        message_content = message.strip()

        self.log.info(f"User: {user_email} | Command: weather | Content: {message_content}")
        
        # Fetch weather data using the new async method
        weather = asyncio.run(self.get_weather(message_content))
        data = weather.hourly()

        # Use LLM to generate a response
        self.llm.set_context(f"The date is {self.now}\n\Weather Data:\n{data}")
        question = f"{first_name} requestested today's brief weather report with formatting for {message_content}."
        answer = self.llm.ask_question(question)

        # Format the markdown message
        md_msg = "## Weather Report\n\n"
        md_msg += f"> Date: {self.now}\n\n"
        md_msg += f"{answer}\n\n---\n\n"

        # Return the markdown message
        return md_msg