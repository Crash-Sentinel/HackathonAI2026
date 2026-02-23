"""
File: convert.py
Author: Ben Miller
Brief: Converts CSV data files into filtered files of the same type.
Version: 0.1
Date: 02-2026

Copyright: Copyright (c) 2026
"""

import pandas as pd
import numpy as np
from datetime import datetime

"""
Brief: Converter ...  
"""
class converter:
    def __init__(
        self, 
        path_string: str,
        isMeter: bool,
        kjFactor: int = 2_676,
        kWhFactor: int = 3_600,
        kilojoules_unit_string: str = "kJ",
        kilojoules_display_string: str = "Kilojoules"
    ) -> None:
        """
        Creates the converter class.

        Allows the user to make more customizations within the converter class as well.
        This allows the user to have custom kjFactors or change the kilojoules_display_string if they like,
        and also does some checking on the existance of certain columns within its creation, throws a ValueError
        if columns seem non-existent or mismatched for what should be expected.

        Args:
            path_string: str - the absolute or relative file path for the file that you want 
                               the converter to look at specifically
        
        Return:
            None (converter is instantiated)
        """
        self.file_name = path_string
        self.data = pd.read_csv(self.file_name)
        self.isMeter = isMeter

        if (isMeter):
            required_columns = [
                "readingvalue",
                "readingunits",
                "readingunitsdisplay",
                "readingwindowstart",
                "readingwindowend"
            ]

            for col in required_columns:
                if col not in self.data.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            self.kg_kJ_Factor = kjFactor
            self.kWh_kJ_Factor = kWhFactor
            self.KILOJOULES_UNIT_STR = kilojoules_unit_string
            self.KILOJOULES_DISPLAY_STR = kilojoules_display_string
            self.READING_VALUE_INDEX = self.data.columns.get_loc("readingvalue")
            self.READING_UNITS_INDEX = self.data.columns.get_loc("readingunits")
            self.READING_DISPLAY_UNITS_INDEX = self.data.columns.get_loc("readingunitsdisplay")
            self.READING_WINDOW_START = self.data.columns.get_loc("readingwindowstart")
            self.READING_WINDOW_END = self.data.columns.get_loc("readingwindowend")

        else:
            required_columns = [
                "buildingname", 
                "grossarea", 
                "latitude", 
                "longitude"
            ]

            for col in required_columns:
                if col not in self.data.columns:
                    raise ValueError(f"Missing required column: {col}")

        

    def filter_cooling_rates(self, cooling_rates: np.array) -> np.array:
        """
        Filters the cooling rates within a csv file to be converted from a certain energy or power
        into kJ.

        Description.

        Args:
            cooling_rates: np.array - the unfiltered numpy array of cooling rates
        
        Return:
            np.array (the filtered cooling rates)
        """

        try:
            if (self.isMeter):
                filtered_cooling_rates = cooling_rates
                for _ in filtered_cooling_rates:
                    # ISO 6801 date time string format
                    endMinutes = datetime.fromisoformat(_[self.READING_WINDOW_END]).minute
                    startMinutes = datetime.fromisoformat(_[self.READING_WINDOW_START]).minute
                    hours_logged = (endMinutes - startMinutes) / 60 # Convert the 15 minutes to hours
                    _[self.READING_VALUE_INDEX] = _[self.READING_VALUE_INDEX] * hours_logged
                    _[self.READING_UNITS_INDEX] = self.KILOJOULES_UNIT_STR
                    _[self.READING_DISPLAY_UNITS_INDEX] = self.KILOJOULES_DISPLAY_STR
                return filtered_cooling_rates
        except Exception as e:
            print(f"Error occured in {self.filter_cooling_rates.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def filter_steam_rates(self, steam_rates: np.array) -> np.array:
        """
        Filters the steam rates within a csv file to be converted from a certain energy or power
        into kJ.

        Description.

        Args:
            steam_rates: np.array - the numpy array to be filtered through
        
        Return:
            np.array (the filtered numpy array)
        """

        try:
            if (self.isMeter):
                filtered_steam_rates = steam_rates
                for _ in filtered_steam_rates:
                    # ISO 6801 date time string format
                    endMinutes = datetime.fromisoformat(_[self.READING_WINDOW_END]).minute
                    startMinutes = datetime.fromisoformat(_[self.READING_WINDOW_START]).minute
                    hours_logged = (endMinutes - startMinutes) / 60 # Convert the 15 minutes to hours
                    _[self.READING_VALUE_INDEX] = _[self.READING_VALUE_INDEX] * self.kg_kJ_Factor * hours_logged
                    _[self.READING_UNITS_INDEX] = self.KILOJOULES_UNIT_STR
                    _[self.READING_DISPLAY_UNITS_INDEX] = self.KILOJOULES_DISPLAY_STR
                return filtered_steam_rates
        except Exception as e:
            print(f"Error occured in {self.filter_steam_rates.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def filter_steam_data(self, steam_values: np.array) -> np.array:
        """
        Filters the steam data within a csv file to be converted from a certain energy or power
        into kJ.

        Description.

        Args:
            steam_rates: np.array - the numpy array of steam_values to be filtered
        
        Return:
            np.array (the filtered numpy array)
        """
        try:
            if (self.isMeter):
                filtered_steam_data = steam_values
                for _ in filtered_steam_data:
                    _[self.READING_VALUE_INDEX] = _[self.READING_VALUE_INDEX] * self.kg_kJ_Factor * self.kWh_kJ_Factor
                    _[self.READING_UNITS_INDEX] = self.KILOJOULES_UNIT_STR
                    _[self.READING_DISPLAY_UNITS_INDEX] = self.KILOJOULES_DISPLAY_STR
                return filtered_steam_data
        except Exception as e:
            print(f"Error occured in {self.filter_steam_data.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def filter_kilowatt_hours_data(self, kilowatt_values: np.array) -> np.array:
        """
        Filters kilowatt hour data within a csv file to be converted from a certain energy or power
        into kJ.

        Description.

        Args:
            kilowatt_values: np.array - the numpy array that has all the kilowatt units specifically
        
        Return:
            np.array (the filtered kilowatt hour data changed to kJ)
        """
        try:
            if (self.isMeter):
                filtered_kilowatt_data = kilowatt_values
                for _ in filtered_kilowatt_data:
                    endMinutes = datetime.fromisoformat(_[self.READING_WINDOW_END]).minute
                    startMinutes = datetime.fromisoformat(_[self.READING_WINDOW_START]).minute
                    hours_logged = (endMinutes - startMinutes) / 60 # Convert the 15 minutes to hours
                    _[self.READING_VALUE_INDEX] = _[self.READING_VALUE_INDEX] * hours_logged
                    _[self.READING_UNITS_INDEX] = self.KILOJOULES_UNIT_STR
                    _[self.READING_DISPLAY_UNITS_INDEX] = self.KILOJOULES_DISPLAY_STR
                return filtered_kilowatt_data
        except Exception as e:
            print(f"Error occured in {self.filter_kilowatt_hours_data.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def filter_meter_data(self) -> pd.DataFrame:
        """
        Filters all of the meter data and converts the energy and power units to kJ.

        Description.

        Args:
            None
        
        Return:
            pd.DataFrame (the filtered meter data)
        """
        try:
            if (self.isMeter):
                steam_values = self.data[self.data["readingunits"] == "kg"]
                cooling_rate_values = self.data[self.data["readingunits"] == "kW"]
                steam_rate_values = self.data[self.data["readingunits"] == "kg/hour"]
                kilowatt_values = self.data[self.data["readingunits"] == "kWh"]
                
                filtered_steam_values = self.filter_steam_data(steam_values.to_numpy())
                filtered_steam_rates = self.filter_steam_rates(steam_rate_values.to_numpy())
                filtered_cooling_rates = self.filter_cooling_rates(cooling_rate_values.to_numpy())
                filtered_kilowatt_values = self.filter_kilowatt_hours_data(kilowatt_values.to_numpy())

                filtered_numpy_array = np.concatenate((filtered_kilowatt_values, filtered_steam_values, filtered_steam_rates, filtered_cooling_rates))

                return pd.DataFrame(filtered_numpy_array, columns=self.data.columns)
        except Exception as e:
            print(f"Error occured in {self.filter_meter_data.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def filter_building_data(self) -> pd.DataFrame:
        """
        Selects the desired data from the locations csv file and gives a
        pandas dataframe as the result.

        Description.

        Args:
            None
        
        Return:
            pd.DataFrame (the filtered location data)
        """
        try:
            if (not self.isMeter):
                building_names = self.data["buildingname"].str.lower().str.split('(').str[0].str.strip()
                gross_area = self.data["grossarea"]
                latitude = self.data["latitude"]
                longitude = self.data["longitude"]

                # filtered_data = np.concatenate((building_names.to_numpy(), gross_area.to_numpy(), latitude.to_numpy(), longitude.to_numpy()))
                filtered_data = np.column_stack((
                    building_names.to_numpy(),
                    gross_area.to_numpy(),
                    latitude.to_numpy(),
                    longitude.to_numpy()
                ))

                return pd.DataFrame(filtered_data, columns=["buildingname", "grossarea", "latitude", "longitude"])
        except Exception as e:
            print(f"Error occured in {self.filter_building_data.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e


    def execute_meter_conversion(self, output_file_name: str) -> None:
        """
        Top level function to execute all the meter data processing in one call.

        Description.

        Args:
            output_file_name: str - the output file name to be turned into csv
        
        Return:
            None
        """
        try:
            if (not self.isMeter):
                raise RuntimeError("execute_meter_conversion called in building mode")

            filtered_basic_data = self.filter_meter_data()
            filtered_basic_data.to_csv(output_file_name, index=False)
        except Exception as e:
            print(f"Error occured in {self.execute_meter_conversion.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

    def execute_building_conversion(self, output_file_name: str) -> None:
        """
        Top level function to execute all the building data processing in one call.

        Description.

        Args:
            output_file_name: str - the output file name to be turned into csv 
        
        Return:
            None
        """
        try:
            if (not self.isMeter):
                if (self.file_name):
                    filtered_basic_data = self.filter_building_data()
                    filtered_basic_data.to_csv(output_file_name, index=False)
        except Exception as e:
            print(f"Error occured in {self.execute_building_conversion.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.execute_meter_conversion.__name__}") from e

if __name__ == '__main__':
    """
    Simple test cases for converter are executed because of Debugging purposes.

    Description.

    Args:
        None
        
    Return:
        None (test cases are executed)
    """

    print("\n")
    conv = converter("meter-data-sept-2025.csv", True)
    conv.execute_meter_conversion("output.csv")
    # execute_meter_conversion("meter-data-sept-2025.csv", "output.csv")
