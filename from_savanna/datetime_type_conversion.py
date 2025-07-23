"""
Created: September 4th, 2024
By: Savanna Wolvin, s.wolvin@utah.edu

Edited: September 5th, 2024
By: Savanna Wolvin, s.wolvin@utah.edu


# SUMMARY
Convert cftime datetime variable array to pandas DateTimeIndex array for 
CMIP6_GCM_to_coarse_grid.py


# DESCRIPTION
Python fucntions for CMIP6_GCM_to_coarse_grid.py in which the cftime datetime 
variables within the CMIP6 xarrays are converted to a Gregorian calender. 
Calenders available for convertion are Datetime360Day and DatetimeNoleap into 
datetime.datetime. DatetimeProlepticGregorian, DatetimeJulian, and
DatetimeGregorian are converted to a string, then the pandas.to_datetime() is 
applied. numpy.datetime[64] is simply passed through the pandas.to_datetime() 
function.

To inplement conversions from CMIP6_GCM_to_coarse_grid.py, the function 
convert_to_gregorian() is called. This function then determines which 
convertion action is required.


"""

import cftime
from datetime import datetime, timedelta
import pandas as pd


"""
FUNCTION DEFINITION: Datetime360Day_to_Gregorian
    INPUT
    - cftime_date (cftime.Datetime360Day): Singular datetime value to be 
            converted to the gregorian calender.
    
    OUTPUT
    - gregorian_date (datetime.datetime): Converted to datetime value
    - cftime_date (cftime.{DateTimeType}): Incorrect datetime conversion 
            chosen, value returned 
"""
def Datetime360Day_to_Gregorian(cftime_date):
    if isinstance(cftime_date, cftime.Datetime360Day):
        # Start with a base date
        base_date = datetime(cftime_date.year, 1, 1)
        # Calculate the number of days since the start of the year
        days_since_start_of_year = (
            (cftime_date.month - 1) * 30 + (cftime_date.day - 1))
        # Add the days to the base date
        gregorian_date = base_date + timedelta(days=days_since_start_of_year)
        return gregorian_date
    else:
        return cftime_date


"""
FUNCTION DEFINITION: DatetimeNoleap_to_Gregorian
    INPUT
    - cftime_date (cftime.DatetimeNoleap): Singular datatime value to be 
            converted to the gregorian calender.
    
    OUTPUT
    - gregorian_date (datetime.datetime): Converted to datetime value
    - cftime_date (cftime.{DateTimeType}): Incorrect datetime conversion 
            chosen, value returned 
"""
def DatetimeNoleap_to_Gregorian(cftime_date):
    if isinstance(cftime_date, cftime.DatetimeNoLeap):
        # Start with a base date
        base_date = datetime(cftime_date.year, 1, 1)
        # Calculate the number of days since the start of the year
        days_since_start_of_year = cftime_date.timetuple().tm_yday - 1
        
        # Create the Gregorian date
        gregorian_date = base_date + timedelta(days=days_since_start_of_year)
        
        # Because of NoLeap, conversion to Gregorian believes the date is 
        # February 29th. Therefore, the date must be adjusted to March 1st
        if gregorian_date.month == 2 and gregorian_date.day == 29:
            # Move the date to March 1st
            gregorian_date = gregorian_date + timedelta(days=1)
            
        return gregorian_date
    else:
        return cftime_date


"""
FUNCTION DEFINITION: convert_datetimes
    INPUT (xarray.DataArray): Data array of cftime values
    
    OUTPUT 
    - converted_times (pandas.DatetimeIndex): DatetimeIndex list of gregorian 
            datetimes to the xarray.Dataset     
"""
def convert_to_gregorian(time):
    
    # Convert to pandas datetime if necessary
    if isinstance(time.values[0], cftime.Datetime360Day):
        converted_times = [Datetime360Day_to_Gregorian(t) for t in time.values]
    elif isinstance(time.values[0], cftime.DatetimeNoLeap):
        converted_times = [DatetimeNoleap_to_Gregorian(t) for t in time.values]
    elif isinstance(time.values[0], (cftime.DatetimeProlepticGregorian, cftime.DatetimeJulian, cftime.DatetimeGregorian)):
        
        # Convert the time values to strings and then to pandas datetime
        converted_times = [str(t) for t in time.values]
    else:
        converted_times = time.values
        
    # Convert the list of datetime objects to pandas datetime
    converted_times = pd.to_datetime(converted_times)
        
    return converted_times

