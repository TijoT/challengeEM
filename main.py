from entsoe import EntsoePandasClient
import pandas as pd
import requests
from delorean import parse

MeteoJson = dict[str, float | str | int | dict]

cities = {
    "Madrid": {                 # Reference: https://www.latlong.net/
        "lat": 40.4167,         # 40.416775
        "long": -3.7033,        # -3.703790
    },
    "Barcelona": {
        "lat": 41.346176,
        "long": 2.168365,
    },
    "Bilbao": {
        "lat": 	43.262985,
        "long": -2.935013,
    },
    "Malaga": {
        "lat": 36.719444,
        "long": -4.420000,
    }
}


def prepare_forecast(country_code: str, country_time_zone: str) -> None:
    """Test data was already generated for country 'Spain' from ENTSO-E API. Timezone of Brussels and Madrid is same.
    Result stored in ./data/forecast.csv. The actual file contains data for the date 2022-10-10

    * ENTSO-E platform provide free access to pan-European market data: https://github.com/EnergieID/entsoe-py
    * Country code mapping: https://github.com/EnergieID/entsoe-py/blob/master/entsoe/mappings.py


    """

    client = EntsoePandasClient(api_key="API_KEY")

    start_date_time = pd.Timestamp('20221010', tz=country_time_zone)
    end_date_time = pd.Timestamp('20221011', tz=country_time_zone)

    wind_solar_forecast_dataframe = (
        client.query_wind_and_solar_forecast(country_code, start=start_date_time, end=end_date_time))
    wind_solar_forecast_dataframe.to_csv('data/forecast.csv')


def get_weather_forecast(time_zone: str, city: str, parameters_to_measure: list[str] | None = None) -> MeteoJson:
    """
    https://open-meteo.com/en/docs/historical-weather-api
    Hourly weather variable collected with temperature at 2m, wind speed at 10 m
    """

    # with time zone set, the temperature and wind speed values are offset by one entry
    # i.e. first value in response without time zone is second value in response
    # https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date=2022-10-09&end_date=2022-10-11&hourly=temperature_2m,wind_speed_10m&timezone=Europe%2FBerlin

    # without time zone
    # https://archive-api.open-meteo.com/v1/era5?latitude={latitude}&longitude={longitude}&start_date=2022-10-09&end_date=2022-10-11&hourly=temperature_2m,windspeed_10m

    (latitude, longitude) = (cities[city]['lat'], cities[city]['long'])

    # open meteo has 3 europe timezones: Europe/Berlin, Europe/London, Europe/Moscow. Add mapping for future cities
    default_europe_timezone = 'Europe/Berlin'
    timezone_mapping = {'Europe/Madrid': default_europe_timezone}
    start_date = '2022-10-09'
    end_date = '2022-10-11'

    url = f"https://archive-api.open-meteo.com/v1/era5?"
    url = url + "&".join([
        f"latitude={latitude}",
        f"longitude={longitude}",
        f"start_date={start_date}",
        f"end_date={end_date}",
        f"hourly={','.join(parameters_to_measure)}",
        f"timezone={timezone_mapping.get(time_zone, default_europe_timezone).replace('/', '%2F')}"
    ])

    weather_history_response: requests.Response = requests.get(url)
    weather_history: dict = weather_history_response.json()
    return weather_history


def enhance_generation_forecast(forecast: MeteoJson, parameters_to_measure: list[str] | None = None):
    """Compare historical weather api of entsoe with Open-Meteo and add the missing api data to entsoe.

    Original implementation:
    ------------------------

        Datetime is shifted from GMT to CET timezone. i.e. a loss of 2 hrs occurs here.
        Difference of 2 hrs is due to summer with DST active. --> Instead at data collection set correct time zone

    Changed implementation:
    -----------------------

        Time zone is set at the data collection. No time zone adjustment is performed.
    """
    entsoe_wind_solar_dataframe = pd.read_csv('data/forecast.csv', index_col=0)
    entsoe_wind_solar_dataframe['temperature'] = None
    entsoe_wind_solar_dataframe['windspeed'] = None

    # iterate time from 2022-10-09 00:00 to 2022-10-11 23:00
    for index, date_time in enumerate(forecast['hourly']['time']):
        # TODO there seems to be a subtle bug here regarding
        #  https://delorean.readthedocs.io/en/latest/quickstart.html#ambiguous-cases

        modified_meteo_datetime: str | None

        # Prefer python standard libraries than separate packages
        if 'iso' in (meteo_timestamp_format := forecast['hourly_units']['time']).lower():
            # format is YYYY-MM-DDTHH:MM:SS
            year_first = True
            date_first = False

            # if the default Delorean parse arguments are allowed,
            # the datetime ``2022-10-09T00:00`` is interpreted as 10. Sept 2022
            parsed_datetime = parse(
                date_time, timezone=forecast['timezone_abbreviation'], dayfirst=date_first, yearfirst=year_first)
            datetime_format_with_utc_offset = "%Y-%m-%d %H:%M:%S%z"
            meteo_datetime = parsed_datetime.datetime.strftime(datetime_format_with_utc_offset)
            modified_meteo_datetime = f'{meteo_datetime[:-2]}:{meteo_datetime[-2:]}'
        else:
            raise Exception(f'Timestamp format conversion is not handled for "{meteo_timestamp_format}"')

        # TODO for good forecast of wind generation we should take the wind speed at 100m instead,
        #  turbines are way taller than 10m.
        if modified_meteo_datetime in entsoe_wind_solar_dataframe.index:
            # assign temperature to entsoe dataframe
            entsoe_wind_solar_dataframe.loc[[modified_meteo_datetime], ['temperature']] \
                = forecast['hourly']['temperature_2m'][index]

            # assign wind speed to entsoe dataframe
            entsoe_wind_solar_dataframe.loc[[modified_meteo_datetime], ['windspeed']] \
                = forecast['hourly']['windspeed_10m'][index]

    # fill NaN values with zeroes
    entsoe_wind_solar_dataframe = entsoe_wind_solar_dataframe.fillna(0)
    entsoe_wind_solar_dataframe.to_csv('data/result_windSpeed10m.csv')


if __name__ == '__main__':
    from pytz import country_timezones

    # moved country code from function level to main
    country_code = 'ES'
    country_time_zone = [tz for tz in country_timezones[country_code] if 'europe' in tz.lower()][0]
    hourly_parameters = ['temperature_2m', 'windspeed_10m']
    forecast = get_weather_forecast(country_time_zone, 'Madrid', hourly_parameters)
    enhance_generation_forecast(forecast)
