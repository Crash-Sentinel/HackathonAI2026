"""
File: requestClass.py
Author: Ben Miller
Brief: Handles API output and JSON parsing. 
       Currently dead due to time constraints and inability to attain API keys, could've done
       it within regression.py for weather amenities.
Version: 0.1
Date: 02-2026

Copyright: Copyright (c) 2026
"""

import requests
import matplotlib.pyplot as plt
import convert
import json

def query_api(url: str) -> None:
    """
    Queries the API to receive more information about OSU floors and other criteria.

    Description.

    Args:
        url: str - the base url to then request from
    
    Return:
        None (None)
    """
    pass

def parse_json(file_name: str) -> list[list]:
    """
    Parses a json file into the desired quanities for comparing data with regards to 
    grossarea, buildingName, and location.

    Description.

    Args:
        file_name: str - the file path of the json file you want to parse
    
    Return:
        list (list of the desired quantities)
    """
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)

        items_of_interest = []

        for entry in data:
            # indexOfStartParenthesis = entry["buildingName"].find('(')
            # if (indexOfStartParenthesis != -1):
            #     print(entry["buildingName"][0:indexOfStartParenthesis])
            items_of_interest.append([[entry["buildingName"], entry["grossArea"], entry["latitude"], entry["longitude"]]])

        return items_of_interest

    except FileNotFoundError:
        print("Cannot find json file")
    except json.JSONDecodeError:
        print("Cannot decode JSON error, double check file's format")

if __name__ == "__main__":
    """
    Simple test cases for requestClass are executed because of Debugging purposes.

    Description.

    Args:
        None
        
    Return:
        None (test cases are executed)
    """
    parse_json("buildingOne.json")
