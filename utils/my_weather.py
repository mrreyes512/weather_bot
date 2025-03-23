# import the module
import python_weather
import asyncio

import pandas as pd


class MY_Weather:
    def __init__(self, city: str, unit: str = python_weather.IMPERIAL):
        self.city = city
        self.unit = unit
        self.weather_data = None  # Initialize weather_data as None

    @classmethod
    async def fetch(cls, city: str, unit: str = python_weather.IMPERIAL):
        """Asynchronous factory method to initialize the class and fetch weather data."""
        self = cls(city, unit)
        async with python_weather.Client(unit=self.unit) as client:
            self.weather_data = await client.get(self.city)
        return self

    def forecast(self):
        """Create a DataFrame from forecast data."""
        # collect the 3-day forecast data
        forecast_data = []
        for daily in self.weather_data.daily_forecasts:
            forecast_data.append({
                "city": self.city,
                "date": daily.date,
                "high": daily.highest_temperature,
                "low": daily.lowest_temperature,
                "sunrise": daily.sunrise,
                "sunset": daily.sunset
            })

        # Create the DataFrame
        forecast_df = pd.DataFrame(forecast_data)

        # Set the 'date' column as the index in place
        forecast_df.set_index('date', inplace=True)

        return forecast_df
    
    def hourly(self):
        """Create a DataFrame for hourly forecast data for a specific date."""

        # Collect hourly data for the specified day
        hourly_data = []
        for daily in self.weather_data.daily_forecasts:
            for hourly in daily:
                hourly_data.append({
                    "city": self.city,
                    "date": daily.date,
                    "time": hourly.time,
                    "description": hourly.kind,
                    "temperature": hourly.temperature,
                    "humidity": hourly.humidity,
                    "rain_chance": hourly.chances_of_rain,
                    "uv_index": hourly.ultraviolet
                })

        # Create the DataFrame
        hourly_df = pd.DataFrame(hourly_data)

        return hourly_df
