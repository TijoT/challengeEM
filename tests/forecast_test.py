import unittest
from main import get_weather_forecast
import requests_mock


class TestForecastMethods(unittest.TestCase):

    # @unittest.skip
    @requests_mock.Mocker()
    def test_method_called(self, mock):
        mock.get('https://archive-api.open-meteo.com/v1/era5?latitude=40.4167&longitude=-3.7033&start_date=2022-10-09&end_date=2022-10-11&hourly=temperature_2m,windspeed_10m&timezone=Europe%2FBerlin',
            json={"latitude":40.5,"longitude":-3.75,"timezone_abbreviation":"GMT","hourly":{"time":["2022-10-10T00:00","2022-10-10T01:00"],"temperature_2m":[14.6,14.3],"windspeed_10m":[7.1,5.4]}})

        parametersToCheck = ['temperature_2m', 'windspeed_10m']
        data = get_weather_forecast('Madrid', parametersToCheck)
        history = mock.request_history
        self.assertEqual(len(history), 1, "Should have been called once")
        # self.assertEqual(len(data['hourly']['temperature_2m']), 5, "Should have two temperature measurements")

        """
        Test failure due to new changes:
        requests_mock.exceptions.NoMockAddress: No mock address: GET
        
        Failure reasons: 
        Reason 1: Time zone added
        Reason 2: New argument added to the method
        Reason 3: Json response checks for time between 10.10.2022 00:00 - 01:00, api does not allow hourly request
        """

    # @unittest.skip
    @requests_mock.Mocker()
    def test_timezone(self, m):
        """Positive test case
        Check the time zone is not GMT. Expected is ``CET``
        """
        requestUrl = 'https://archive-api.open-meteo.com/v1/era5?latitude=40.4167&longitude=-3.7033&start_date=2022-10-09&end_date=2022-10-11&hourly=temperature_2m,windspeed_100m&timezone=Europe%2FBerlin'
        
        requestJsonResponse = {'latitude': 40.4167, 'longitude': -3.7033,
                               'utc_offset_seconds': 3600, 'timezone': 'Europe/Berlin', 'timezone_abbreviation': 'CET',
                               'elevation': 660.0,
                               'hourly_units': {'time': 'iso8601', 'temperature_2m': '°C', 'windspeed_100m': 'km/h'},
                               'hourly': {
                                   'time': ['2022-10-09T00:00', '2022-10-09T01:00', '2022-10-09T02:00',
                                            '2022-10-11T21:00', '2022-10-11T22:00', '2022-10-11T23:00'],
                                   'temperature_2m': [17.2, 16.7, 15.7, 15.4, 14.9, 14.2],
                                   'windspeed_100m': [17.8, 15.5, 11.2, 18.1, 16.1, 16.5]}}

        m.get(requestUrl, json=requestJsonResponse)
        parametersToCheck = ['temperature_2m', 'windspeed_100m']
        data = get_weather_forecast('Madrid', parametersToCheck)
        # self.assertEqual(data['timezone_abbreviation'], 'CET', "Time zone is Europe/Berlin")
        self.assertNotEqual(data['timezone_abbreviation'], 'GMT', "Time zone is not default GMT")
        self.assertEqual(data['timezone_abbreviation'].upper(), 'CET')

    def test_method_mandatory_args(self):
        """
        Test to check city name is a mandatory argument
        """

        with self.assertRaises(TypeError) as exp_exc:
            data = get_weather_forecast()

        self.assertIn('positional argument', exp_exc.exception.args[0], "Arguments are required")

    def test_method_invalid_city(self):
        """Main function allows 4 cities, ``Madrid``, ``Barcelona``, ``Bilbao``, ``Malaga`` to get forecast.
        Test to check whether forecast is available for a new city
        """

        with self.assertRaises(Exception) as exp_exc:
            data = get_weather_forecast('Demo')

        self.assertIn('not available', exp_exc.exception.args[0], "City is unknown")


if __name__ == '__main__':
    unittest.main()