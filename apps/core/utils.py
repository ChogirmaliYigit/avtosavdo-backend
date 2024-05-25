import ssl

import certifi
from geopy.geocoders import Nominatim


def get_address_by_location(latitude, longitude):
    ca_file = certifi.where()
    context = ssl.create_default_context(cafile=ca_file)
    geolocator = Nominatim(user_agent="qasr-restaurant-bot", ssl_context=context)
    location = geolocator.reverse((latitude, longitude), language="uz")
    return ", ".join(location.address.split(",")[:3])


def check_user_location(latitude, longitude):
    service_areas = [
        [
            (41.522960, 60.381202),
            (41.535489, 60.378284),
            (41.549173, 60.365668),
            (41.557330, 60.342151),
            (41.546026, 60.321207),
            (41.533563, 60.316745),
            (41.516020, 60.319662),
            (41.509335, 60.353136),
            (41.511842, 60.364638),
        ]
    ]

    for area in service_areas:
        if is_inside_area(latitude, longitude, area):
            return True
    return False


def is_inside_area(latitude, longitude, area):
    # Is the location of the user to be checked
    num = len(area)
    j = num - 1
    c = False
    for i in range(num):
        if ((area[i][1] > longitude) != (area[j][1] > longitude)) and (
            latitude
            < (area[j][0] - area[i][0])
            * (longitude - area[i][1])
            / (area[j][1] - area[i][1])
            + area[i][0]
        ):
            c = not c
        j = i
    return c
