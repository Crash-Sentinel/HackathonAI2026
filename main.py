"""
File: main.py
Author: Ben Miller
Brief: Starts the GUI for the user and uses convert and requestClass to handle file operations.
Version: 0.1
Date: 02-2026

Copyright: Copyright (c) 2026
"""

import convert
import requestClass
import regression as rg
import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
import threading

"""
Brief: GUI Class to execute User Input and Display Appropriate Outputs 
       using tkinter and async threading for faster functionality of parsing,
       decreasing stall time
"""
class gui:
    def __init__(
        self, 
        title: str = "Main Program", 
        height: int = 360, 
        aspect_ratio: float = 16/9,
        wrap_length: int = 150,
        justify_string: str = "center",
        button_width: int = 25
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
        self.HEIGHT = height
        self.ASPECT_RATIO = aspect_ratio
        self.title = title

        self.allowed_file_types = [
            ("CSV Files", "*.csv")
        ]

        self.currentFileToConvert = ""
        self.currentFileToCreate = ""
        self.currentFileToProcessBuild = ""
        self.currentFileToFilteredBuild = ""

        self.wrap_length = wrap_length
        self.justify_string = justify_string

        self.button_width = button_width

        self.root = tk.Tk()
        self.root.geometry(f"{int(self.ASPECT_RATIO * self.HEIGHT)}x{self.HEIGHT}")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.title(self.title)

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        def _on_canvas_configure(event):
            self.canvas.itemconfigure(
                self.canvas_window,
                width=event.width
            )

        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)

    def ask_for_file_to_lookup(self) -> str:
        """
        Prompts the user to select a file to be converted.

        Description.

        Args:
            None
        
        Return:
            str (the file path that will be used to do conversion)
        """

        fileReturned = fd.askopenfilename(
            defaultextension=".csv",
            title="Select a File to Use",
            filetypes=self.allowed_file_types
        )

        self.currentFileToConvert = fileReturned
        self.mainLabel.config(text=f"Enter your file (will show here): {self.currentFileToConvert}")
        
        if (self.currentFileToConvert != "" and self.currentFileToCreate != ""):
            self.buttonToExecuteConversion['state'] = tk.NORMAL

        if (self.currentFileToCreate != "" and self.currentFileToFilteredBuild != ""):
            self.buttonToRunPowerRegression['state'] = tk.NORMAL

        return fileReturned

    def ask_file_to_create(self) -> str:
        """
        Prompts the user to select a filepath of a file that will be created as output
        after filtering and conversions of energies and powers has taken place.

        Description.

        Args:
            None
        
        Return:
            str (the filepath of the new created file)
        """

        file_to_create = fd.asksaveasfilename(
            defaultextension=".csv",
            title="Select a File to Create",
            filetypes=self.allowed_file_types
        )

        self.currentFileToCreate = file_to_create
        self.secondaryLabel.config(text=f"Enter your file (will show here): {self.currentFileToCreate}")
        
        if (self.currentFileToConvert != "" and self.currentFileToCreate != ""):
            self.buttonToExecuteConversion['state'] = tk.NORMAL

        if (self.currentFileToCreate != "" and self.currentFileToFilteredBuild != ""):
            self.buttonToRunPowerRegression['state'] = tk.NORMAL

        return file_to_create

    def on_meter_conversion_done(self) -> None:
        """
        Updates the UI to sow that the conversion for the meter processing has been completed.

        Description.

        Args:
            None
        
        Return:
            None
        """
        self.finishMeterLabel.config(text="Done!")
        self.buttonToExecuteConversion.config(state=tk.NORMAL)

    def execute_meter_conversion_safe(self, input_file: str, output_file: str) -> None:
        """
        Begins execution of the filtering process on {input_file} to create {output_file}
        with the filtering of the energy conversions done.

        Description.

        Args:
            input_file: str - the input filepath string that you want the conversion to be ( selected in the GUI )
            output_file: str - the output filepath string that you want the conversion to be ( selected in the GUI )
        
        Return:
            None
        """
        try:
            convert.converter(path_string=input_file, isMeter=True).execute_meter_conversion(output_file)

            self.root.after(0, self.on_meter_conversion_done)
        except Exception as e:
            self.root.after(0, lambda err=e: self.finishBuildingLabel.config(text=str(err)))

    def run_meter_conversion_async(self) -> None:
        """
        Creates and executes new thread to help utilize CPU efficiency of the meter conversion across multiple files.

        Description.

        Args:
            None
        
        Return:
            None
        """
        if not self.currentFileToConvert or not self.currentFileToCreate:
            self.finishBuildingLabel.config(text="Missing input or output file")
            return

        self.buttonToExecuteConversion.config(state=tk.DISABLED)

        worker = threading.Thread(
            target=self.execute_meter_conversion_safe,
            args=(self.currentFileToConvert, self.currentFileToCreate),
            daemon=True
        )
        worker.start()

    def on_building_conversion_done(self) -> None:
        """
        Updates the UI to sow that the filtering for the building space and spacial location has been completed.

        Description.

        Args:
            None
        
        Return:
            None
        """
        self.finishBuildingLabel.config(text="Done!")
        self.buttonToExecuteFilterBuildings.config(state=tk.NORMAL)

    def execute_building_conversion_safe(self, input_file: str, output_file: str) -> None:
        """
        Executes the filtering of the buildings from {input_file} into {output_file}.

        Description.

        Args:
            input_file: str - the input filepath string that you want the conversion to be ( selected in the GUI )
            output_file: str - the output filepath string that you want the conversion to be ( selected in the GUI )
        
        Return:
            None
        """
        try:
            convert.converter(path_string=input_file, isMeter=False)\
                .execute_building_conversion(output_file)

            self.root.after(0, self.on_building_conversion_done)
        except Exception as e:
            self.root.after(0, lambda err=e: self.finishBuildingLabel.config(text=str(err)))

    def run_building_conversion_async(self) -> None:
        """
        Creates and executes new thread to help utilize CPU efficiency of the filtering of the building column across multiple files.

        Args:
            None
        
        Return:
            The thread instantiated
        """
        if not self.currentFileToProcessBuild or not self.currentFileToFilteredBuild:
            self.finishBuildingLabel.config(text="Missing input or output file")
            return
        
        self.buttonToExecuteFilterBuildings['state'] = tk.DISABLED

        worker = threading.Thread(
            target=self.execute_building_conversion_safe,
            args=(self.currentFileToProcessBuild, self.currentFileToFilteredBuild),
            daemon=True
        )
        worker.start()

    def ask_file_to_filter_build(self) -> str:
        """
        Prompts the user to open a file to then filter buildings, area, latitude, and longitude.

        Description.

        Args:
            None
        
        Return:
            None
        """

        file_to_filter_build = fd.askopenfilename(
            defaultextension=".csv",
            title="Select a File to Use",
            filetypes=self.allowed_file_types
        )

        self.currentFileToProcessBuild = file_to_filter_build
        self.buildingLabel.config(text=f"Enter your file (will show here): {self.currentFileToProcessBuild}")

        if (self.currentFileToProcessBuild != ""):
            self.buttonToExecuteFilterBuildings['state'] = tk.NORMAL

        if (self.currentFileToCreate != "" and self.currentFileToFilteredBuild != ""):
            self.buttonToRunPowerRegression['state'] = tk.NORMAL   
        
        return file_to_filter_build

    def ask_file_to_output_filtered_build(self) -> str:
        """
        Prompts user to choose which file to override or create to output the 
        buildings that are filtered.

        Description.

        Args:
            None
        
        Return:
            str (the filepath outputted)
        """

        file_to_filter_build = fd.asksaveasfilename(
            defaultextension=".csv",
            title="Select a File to Create",
            filetypes=self.allowed_file_types
        )

        self.currentFileToFilteredBuild = file_to_filter_build
        self.buildingFileLabel.config(text=f"Enter your file (will show here): {self.currentFileToFilteredBuild}")

        if (self.currentFileToFilteredBuild != ""):
            self.buttonToGetOutputFileForBuildings['state'] = tk.NORMAL
        
        if (self.currentFileToCreate != "" and self.currentFileToProcessBuild != ""):
            self.buttonToRunPowerRegression['state'] = tk.NORMAL

        return file_to_filter_build
    
    def create_regression_for_energy_per_sqrt(self) -> None:
        """
        Executed regression and showcases new tkinter window for more accurate results.

        Description.

        Args:
            None

        Return:
            None
        """
        try:
            if (self.currentFileToCreate == "" or self.currentFileToFilteredBuild == ""):

                raise RuntimeError("Unable to create regression for files that have not been entered yet!")
            
            degree = 2
            # rg.regression(2, "test1.csv", "test2.csv")
            print(f"filteredBuilt: {self.currentFileToFilteredBuild}, toCreate: {self.currentFileToCreate}")
            
            reg = rg.regression(degree, self.currentFileToCreate, self.currentFileToFilteredBuild, "Energy Consumption v. Sqft")

            newWindow = tk.Toplevel(self.root)
            newWindow.title("Regression Results")
            newWindow.geometry("250x150")

        
            # topLabel = tk.Label(newWindow, text=f"Polynomial Regression Results (Deg = {degree}): {reg.coefficients}")
            # topLabel.pack()

            secondLabel = tk.Label(newWindow, text=f"Best Energy Consumption Candidate: {reg.bestEnergyCandidate}")
            secondLabel.pack()

            thirdLabel = tk.Label(newWindow, text=f"Worst Energy Consumption Candidate: {reg.worstEnergyCandidate}")
            thirdLabel.pack()

            tk.Label(newWindow, text=f"Best Weather Candidate: {reg.bestWeatherCandidate}").pack()
            tk.Label(newWindow, text=f"Worst Weather Candidate: {reg.worstWeatherCandidate}").pack()
            

            tk.Button(newWindow, text="Close Window", command=newWindow.destroy).pack()

            
        except Exception as e:
            print(f"Error occured in {self.create_regression_for_energy_per_sqrt.__name__}: {e}")
            raise RuntimeError(f"Error occured in {self.create_regression_for_energy_per_sqrt.__name__}") from e

    def create_display(self) -> None:
        """
        Runs main display that the user is able to see and interact with.

        Description.

        Args:
            None
        
        Return:
            None
        """
        self.mainLabel = tk.Label(self.scrollable_frame, text=f"Enter your file (will show here): {self.currentFileToConvert}", wraplength=self.wrap_length, justify=self.justify_string)
        self.mainLabel.pack()

        self.buttonToConvertCSVMeter = tk.Button(
            self.scrollable_frame, 
            text="Pick file to convert",
            width=self.button_width, 
            command=self.ask_for_file_to_lookup
        )
        self.buttonToConvertCSVMeter.pack()

        self.secondaryLabel = tk.Label(self.scrollable_frame, text=f"Enter your file (will show here): {self.currentFileToCreate}", wraplength=self.wrap_length, justify=self.justify_string)
        self.secondaryLabel.pack()

        self.buttonToCreateCSVMeter = tk.Button(
            self.scrollable_frame, 
            text="Pick file to create", 
            width=self.button_width, 
            command=self.ask_file_to_create
        )
        self.buttonToCreateCSVMeter.pack()

        self.buttonToExecuteConversion = tk.Button(
            self.scrollable_frame, 
            state=tk.DISABLED, 
            text="Convert!", 
            width=self.button_width,  
            command=self.run_meter_conversion_async
        )
        self.buttonToExecuteConversion.pack()

        self.finishMeterLabel = tk.Label(self.scrollable_frame, text="", wraplength=self.wrap_length, justify=self.justify_string)
        self.finishMeterLabel.pack()

        self.buildingLabel = tk.Label(self.scrollable_frame, text=f"Enter your file (will show here): {self.currentFileToProcessBuild}", wraplength=self.wrap_length, justify=self.justify_string)
        self.buildingLabel.pack()

        self.buttonToFilteredBuildings = tk.Button(
            self.scrollable_frame, 
            text="Pick file to create", 
            width=self.button_width, 
            command=self.ask_file_to_filter_build
        )
        self.buttonToFilteredBuildings.pack()

        self.buildingFileLabel = tk.Label(self.scrollable_frame, text=f"Enter your file (will show here): {self.currentFileToFilteredBuild}", wraplength=self.wrap_length, justify=self.justify_string)
        self.buildingFileLabel.pack()

        self.buttonToGetOutputFileForBuildings = tk.Button(
            self.scrollable_frame,
            state=tk.NORMAL,
            text="Pick file to create",
            width=self.button_width,
            command=self.ask_file_to_output_filtered_build
        )
        self.buttonToGetOutputFileForBuildings.pack()

        self.buttonToExecuteFilterBuildings = tk.Button(
            self.scrollable_frame, 
            state=tk.DISABLED, 
            text="Convert!", width=self.button_width,  
            command=self.run_building_conversion_async
        )
        self.buttonToExecuteFilterBuildings.pack()

        self.finishBuildingLabel = tk.Label(self.scrollable_frame, text="", wraplength=self.wrap_length, justify=self.justify_string)
        self.finishBuildingLabel.pack()

        self.buttonToRunPowerRegression = tk.Button(
            self.scrollable_frame,
            state=tk.DISABLED,
            text="Convert!", width=self.button_width, 
            command=self.create_regression_for_energy_per_sqrt
        )
        self.buttonToRunPowerRegression.pack()

        self.root.mainloop()

if __name__ == "__main__":
    """
    Filters the cooling rates within a csv file to be converted from a certain energy or power
    into kJ.

    Description.

    Args:
        cooling_rates: np.array - the unfiltered numpy array of cooling rates
    
    Return:
        np.array (the filtered cooling rates)
    """

    gui = gui()
    gui.create_display()
    