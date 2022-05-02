# This is the manual slice of:
#  army.loc[:, ["deaths"]].iloc[2]
# from file:
#  sources/pandas_exercises/02_Filtering_&_Sorting/Fictional Army/Exercise_with_solutions.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pandas_filtering]'

import pandas as pd

raw_data = {
    "regiment": [
        "Nighthawks",
        "Nighthawks",
        "Nighthawks",
        "Nighthawks",
        "Dragoons",
        "Dragoons",
        "Dragoons",
        "Dragoons",
        "Scouts",
        "Scouts",
        "Scouts",
        "Scouts",
    ],
    "company": [
        "1st",
        "1st",
        "2nd",
        "2nd",
        "1st",
        "1st",
        "2nd",
        "2nd",
        "1st",
        "1st",
        "2nd",
        "2nd",
    ],
    "deaths": [523, 52, 25, 616, 43, 234, 523, 62, 62, 73, 37, 35],
    "battles": [5, 42, 2, 2, 4, 7, 8, 3, 4, 7, 8, 9],
    "size": [1045, 957, 1099, 1400, 1592, 1006, 987, 849, 973, 1005, 1099, 1523],
    "veterans": [1, 5, 62, 26, 73, 37, 949, 48, 48, 435, 63, 345],
    "readiness": [1, 2, 3, 3, 2, 1, 2, 3, 2, 1, 2, 3],
    "armored": [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
    "deserters": [4, 24, 31, 2, 3, 4, 24, 31, 2, 3, 2, 3],
    "origin": [
        "Arizona",
        "California",
        "Texas",
        "Florida",
        "Maine",
        "Iowa",
        "Alaska",
        "Washington",
        "Oregon",
        "Wyoming",
        "Louisana",
        "Georgia",
    ],
}
army = pd.DataFrame(data=raw_data)
army.set_index("origin", inplace=True)
linea_artifact_value = army.loc[:, ["deaths"]].iloc[2]
