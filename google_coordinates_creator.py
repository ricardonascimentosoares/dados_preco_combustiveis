import requests
import json
from slugify import slugify


class GoogleCoordinatesCreator:

    def __init__(self):
        self.api_key = 'AIzaSyB29xqRldhhystR8vrsrpjLYkYnDwgvgJ0'

    def get_coordinates(self, address, city, state):
        parameter = slugify(address+','+city+','+state, separator='+')

        response = requests.get('https://maps.googleapis.com/maps/api'
                                '/geocode/json?address=' + parameter +
                                '&key=' + self.api_key)

        if response.status_code == 200:
            data = json.loads(response.content)
            try:
                location = data['results'][0]['geometry']['location']
            except:
                location = None
            return location
