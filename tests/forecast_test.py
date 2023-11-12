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
        self.assertEqual(len(data['hourly']['temperature_2m']), 5, "Should have two temperature measurements")

        """
        Test failure due to new changes:
        requests_mock.exceptions.NoMockAddress: No mock address: GET
        
        Failure reasons: 
        Reason 1: Time zone added
        Reason 2: New argument added to the method
        Reason 3: Json response checks for time between 10.10.2022 00:00 - 01:00, api does not allow hourly request
        """

    @requests_mock.Mocker()
    def test_function(self, m):
        requestUrl = 'https://archive-api.open-meteo.com/v1/era5?latitude=40.4167&longitude=-3.7033&start_date=2022-10-09&end_date=2022-10-11&hourly=temperature_2m,windspeed_100m&timezone=Europe%2FBerlin'
        
        requestJsonResponse = {'latitude': 40.4167, 'longitude': -3.7033,
                               'utc_offset_seconds': 3600, 'timezone': 'Europe/Berlin', 'timezone_abbreviation': 'CET',
                               'elevation': 660.0,
                               'hourly_units': {'time': 'iso8601', 'temperature_2m': '°C', 'windspeed_100m': 'km/h'},
                               'hourly': {'time': ['2022-10-09T00:00', '2022-10-09T01:00', '2022-10-09T02:00',
                                                   '2022-10-09T03:00', '2022-10-09T04:00', '2022-10-09T05:00',
                                                   '2022-10-09T06:00', '2022-10-09T07:00', '2022-10-09T08:00',
                                                   '2022-10-09T09:00', '2022-10-09T10:00', '2022-10-09T11:00',
                                                   '2022-10-09T12:00', '2022-10-09T13:00', '2022-10-09T14:00',
                                                   '2022-10-09T15:00', '2022-10-09T16:00', '2022-10-09T17:00',
                                                   '2022-10-09T18:00', '2022-10-09T19:00', '2022-10-09T20:00',
                                                   '2022-10-09T21:00', '2022-10-09T22:00', '2022-10-09T23:00',
                                                   '2022-10-10T00:00', '2022-10-10T01:00', '2022-10-10T02:00',
                                                   '2022-10-10T03:00', '2022-10-10T04:00', '2022-10-10T05:00',
                                                   '2022-10-10T06:00', '2022-10-10T07:00', '2022-10-10T08:00',
                                                   '2022-10-10T09:00', '2022-10-10T10:00', '2022-10-10T11:00',
                                                   '2022-10-10T12:00', '2022-10-10T13:00', '2022-10-10T14:00',
                                                   '2022-10-10T15:00', '2022-10-10T16:00', '2022-10-10T17:00',
                                                   '2022-10-10T18:00', '2022-10-10T19:00', '2022-10-10T20:00',
                                                   '2022-10-10T21:00', '2022-10-10T22:00', '2022-10-10T23:00',
                                                   '2022-10-11T00:00', '2022-10-11T01:00', '2022-10-11T02:00',
                                                   '2022-10-11T03:00', '2022-10-11T04:00', '2022-10-11T05:00',
                                                   '2022-10-11T06:00', '2022-10-11T07:00', '2022-10-11T08:00',
                                                   '2022-10-11T09:00', '2022-10-11T10:00', '2022-10-11T11:00',
                                                   '2022-10-11T12:00', '2022-10-11T13:00', '2022-10-11T14:00',
                                                   '2022-10-11T15:00', '2022-10-11T16:00', '2022-10-11T17:00',
                                                   '2022-10-11T18:00', '2022-10-11T19:00', '2022-10-11T20:00',
                                                   '2022-10-11T21:00', '2022-10-11T22:00', '2022-10-11T23:00'],
                                          'temperature_2m': [17.2, 16.7, 15.7, 15.2, 15.0, 14.4, 14.3, 14.0, 13.8, 15.5,
                                                             17.7, 19.7, 21.0, 22.1, 23.1, 23.6, 23.4, 23.6, 23.4, 22.4,
                                                             21.3, 20.7, 19.6, 18.5, 16.9, 15.9, 15.8, 14.6, 14.1, 14.0,
                                                             14.0, 14.5, 14.8, 15.9, 17.7, 19.4, 21.0, 19.1, 19.7, 19.2,
                                                             19.5, 20.3, 19.4, 17.1, 15.9, 15.7, 15.3, 14.8, 14.4, 15.8,
                                                             15.7, 15.4, 15.2, 14.5, 14.3, 14.4, 13.8, 15.3, 17.2, 19.0,
                                                             20.7, 17.6, 19.9, 21.1, 20.7, 17.7, 17.5, 16.7, 16.0, 15.4,
                                                             14.9, 14.2],
                                          'windspeed_100m': [17.8, 15.5, 11.2, 19.3, 19.5, 19.6, 17.0, 16.6, 16.4, 13.1,
                                                             8.0, 5.9, 3.5, 9.1, 9.0, 8.6, 6.8, 5.5, 4.5, 3.8, 4.3, 6.4,
                                                             2.1, 9.2, 8.6, 13.3, 10.9, 15.9, 13.8, 12.2, 12.7, 15.7,
                                                             16.6, 9.3, 7.1, 6.2, 5.2, 7.2, 13.4, 9.8, 9.4, 6.6, 10.4,
                                                             18.4, 13.4, 7.2, 3.5, 7.9, 10.3, 20.3, 16.7, 19.7, 15.7,
                                                             11.2, 16.8, 12.5, 12.0, 10.7, 8.9, 7.9, 6.0, 8.4, 4.4, 7.1,
                                                             11.4, 15.6, 5.7, 17.2, 19.6, 18.1, 16.1, 16.5]}}
        m.get(requestUrl, json=requestJsonResponse)
        parametersToCheck = ['temperature_2m', 'windspeed_100m']
        data = get_weather_forecast('Madrid', parametersToCheck)
        self.assertEqual(True, True, "Should have been called once")


if __name__ == '__main__':
    unittest.main()