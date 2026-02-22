"""
File: regression.py
Author: Ben Miller
Brief: Handles regression between the energy, weather processing, and variance in data.
Version: 0.1
Date: 02-2026

Copyright: Copyright (c) 2026
"""

import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import requestClass
import requests
import time

"""
Brief: Regression class to execute main functionality of graph generation, 
       data processing, and database management.
"""
class regression:
    def __init__(self, degree: int, x: str, y: str, title: str = "Sample Graph") -> None:
        """
        Creates the regression class.

        Description.

        Args:
            degree: int - the absolute or relative file path for the file that you want 
                               the converter to look at specifically
            x: str - the string file path for the x-axis to be represented by
            y: str - the string file path for the y-axis to be represented by
            title: str - the title for the graph to be genereated
        
        Return:
            None (regression is instantiated)
        """
        self.degree = degree
        self.csv_file_x = pd.read_csv(x)
        self.csv_file_y = pd.read_csv(y)
        self.title = title

        if (
            "grossarea" in self.csv_file_x.columns and "readingvalue" in self.csv_file_y.columns or
            "readingvalue" in self.csv_file_x.columns and "grossarea" in self.csv_file_y.columns
            ):
            # X axis is gross area
            # Y axis is power consumption
            
            
            energy = self.csv_file_x
            area = self.csv_file_y

            energy['location'] = energy['sitename'].str.lower().str.strip()
            area['location'] = area['buildingname'].str.lower().str.strip()

            merged = energy.merge(
                area[['location', 'grossarea']],
                on='location',
                how='inner'
            )


            merged['energy_per_sqft'] = merged['readingvalue'] / merged['grossarea']
            merged = merged[merged['readingvalue'] > 0]

            stats = merged.groupby('location')['energy_per_sqft'].agg(
                best_energy_per_sqft='min',
                worst_energy_per_sqft='max',
                variance_energy_per_sqft='var'
            ).reset_index()


            top_n = 10
            worst_buildings = stats.sort_values(
                by='worst_energy_per_sqft',
                ascending=False
            ).head(top_n)
            best_buildings = stats.sort_values(
                by='best_energy_per_sqft',
                ascending=False
            )

            pd.DataFrame([best_buildings.head(top_n), worst_building]).to_csv("energyPerformance.csv")

            # Sort ascending and get top row
            worst_building = stats.sort_values(by='worst_energy_per_sqft', ascending=False).iloc[0]
            self.worstEnergyCandidate = worst_building


            best_building = stats.sort_values(
                by='best_energy_per_sqft',
                ascending=True
            ).iloc[0]
            self.bestEnergyCandidate = best_building

            x = np.arange(len(worst_buildings))
            w = 0.4

            plt.figure()
            plt.bar(x - w/2, worst_buildings['worst_energy_per_sqft'], w, label='Worst')
            plt.bar(x + w/2, worst_buildings['best_energy_per_sqft'], w, label='Best')

            plt.xticks(x, worst_buildings['location'], rotation=45, ha='right')
            plt.yscale('log')
            plt.ylabel("Energy (kJ / sqft)")
            plt.title("Best vs Worst Energy per Sqft (Top 10)")
            plt.legend()
            plt.tight_layout()
            plt.show()

            campus_lat = area["latitude"].mean()
            campus_lon = area["longitude"].mean()

            url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

            params = {
                "latitude": campus_lat,
                "longitude": campus_lon,
                "start_date": pd.to_datetime(merged["readingtime"]).min().strftime('%Y-%m-%d'),
                "end_date": pd.to_datetime(merged["readingtime"]).max().strftime('%Y-%m-%d'), # "2026-02-20"
                "minutely_15": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature"
                ],
                "temperature_unit": "fahrenheit",
                "precipitation_unit": "inch"
            }

            response = requests.get(url, params=params)
            data = response.json()

            weather = pd.DataFrame({
                "time": pd.to_datetime(data["minutely_15"]["time"]),
                "apparent_temp": data["minutely_15"]["apparent_temperature"],
                "humidity": data["minutely_15"]["relative_humidity_2m"],
            })

            weather["minutely_15"] = weather["time"].dt.floor("h")
            weather["minutely_15"] = weather["minutely_15"].dt.tz_localize(None)
            
            merged["time"] = pd.to_datetime(merged["readingtime"])
            merged["minutely_15"] = merged["time"].dt.floor("h")


            energy_hourly = (
                merged
                .groupby(["location", "minutely_15"])
                .agg(energy_per_sqft=("energy_per_sqft", "sum"))
                .reset_index()
            )

            energy_weather = pd.merge(
                energy_hourly,
                weather[["minutely_15", "apparent_temp", "humidity"]],
                on="minutely_15",
                how="inner"
            )

            ALPHA = 15

            energy_weather["weather_load"] = (
                energy_weather["apparent_temp"] +
                ALPHA * (energy_weather["humidity"] / 100)
            )

            energy_weather = energy_weather[energy_weather["weather_load"] > 30]

            energy_weather["energy_weather_norm"] = (
                energy_weather["energy_per_sqft"] /
                energy_weather["weather_load"]
            )

            stats_weather = energy_weather.groupby("location")[
                "energy_weather_norm"
            ].agg(
                best="min",
                worst="max",
                variance="var"
            ).reset_index()
            
            top = stats_weather.sort_values("worst", ascending=False).head(10)
            bottom = stats_weather.sort_values("best", ascending=True).head(10)

            pd.DataFrame([top, bottom]).to_csv("weatherPerformance.csv")

            self.worstWeatherCandidate = stats_weather.sort_values("worst", ascending=False).iloc[0]
            self.bestWeatherCandidate = stats_weather.sort_values("best", ascending=True).iloc[0]

            x = np.arange(len(top))
            w = 0.4

            plt.figure()
            plt.bar(x - w/2, top["worst"], w, label="Worst")
            plt.bar(x + w/2, top["best"], w, label="Best")

            plt.xticks(x, top["location"], rotation=45, ha="right")
            plt.yscale("log")
            plt.ylabel("Energy / Weather Load")
            plt.title("Weather-Normalized Energy per Sqft (Campus)")
            plt.legend()
            plt.tight_layout()
            plt.show()

        else:
            raise RuntimeError("Unable to understand arrays in terms of the x axis and y axis")   
