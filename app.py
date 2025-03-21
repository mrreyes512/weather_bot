# import the module
import python_weather
import asyncio
import pandas as pd  # Import pandas for DataFrame creation

class MY_Weather:
    def __init__(self, city: str, unit: str = python_weather.IMPERIAL):
        self.city = city
        self.unit = unit
        self.weather_data = None  # Store fetched weather data

    async def fetch_weather(self):
        # declare the client with the specified unit
        async with python_weather.Client(unit=self.unit) as client:
            # fetch a weather forecast from the city
            self.weather_data = await client.get(self.city)

    def df_forecast(self, weather):
        """Create a DataFrame from forecast data."""
        # collect the 3-day forecast data
        forecast_data = []
        for daily in weather.daily_forecasts:
            forecast_data.append({
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

    def get_weather(self):
        asyncio.run(self.fetch_weather())
        return self.weather_data


def main():
    # Example usage
    weather = MY_Weather(city="Round Rock, Tx")
    weather_data = weather.get_weather()

    # Print the current temperature
    print(f"Current temperature in {weather.city}: {weather_data.temperature}°")

    # Create and return the DataFrame using a separate method
    forecast_df = weather.df_forecast(weather_data)
    print("\n3-Day Forecast:")
    print(forecast_df)
    return forecast_df


if __name__ == '__main__':
    main()