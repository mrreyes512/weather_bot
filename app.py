# import the module
import asyncio
import pendulum

from utils.my_weather import MY_Weather

# Get current date
now = pendulum.now().format('YYYY-MM-DD')


async def get_weather(city: str):
    """Fetch weather data and return the MY_Weather instance."""
    return await MY_Weather.fetch(city=city)


def main():
    # Example usage
    city = "Round Rock, Tx"
    weather = asyncio.run(get_weather(city))

    # Print the current temperature
    print(f"Current temperature in {weather.city}: {weather.weather_data.temperature}°")

    # Create and return the DataFrame using a separate method
    df_forecast = weather.forecast()
    print("\n3-Day Forecast:")
    print(df_forecast)

    df_hourly = weather.hourly()
    print("\nHourly Forecast")
    print(df_hourly)


if __name__ == '__main__':
    main()