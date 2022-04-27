import pandas as pd

url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/04_Apply/US_Crime_Rates/US_Crime_Rates_1960_2014.csv"
crime = pd.read_csv(url)
crime.Year = pd.to_datetime(crime.Year, format="%Y")
crime = crime.set_index("Year", drop=True)
del crime["Total"]
crimes = crime.resample("10AS").sum()
population = crime["Population"].resample("10AS").max()
crimes["Population"] = population
linea_artifact_value = crimes
