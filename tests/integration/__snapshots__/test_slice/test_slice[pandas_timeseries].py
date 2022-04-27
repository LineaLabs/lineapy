import pandas as pd

url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/09_Time_Series/Apple_Stock/appl_1980_2014.csv"
apple = pd.read_csv(url)
apple.Date = pd.to_datetime(apple.Date)
apple = apple.set_index("Date")
apple_months = apple.resample("BM").mean()
linea_artifact_value = apple_months
