# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/numpy-tutorials/content/mooreslaw-tutorial.md

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[numpy_mooreslaw]'

import numpy as np
import statsmodels.api as sm

A_M = np.log(2) / 2
B_M = np.log(2250) - A_M * 1971
Moores_law = lambda year: np.exp(B_M) * np.exp(A_M * year)
ML_1971 = Moores_law(1971)
ML_1973 = Moores_law(1973)
data = np.loadtxt("transistor_data.csv", delimiter=",", usecols=[1, 2], skiprows=1)
year = data[:, 1]
transistor_count = data[:, 0]
yi = np.log(transistor_count)
Z = year[:, np.newaxis] ** [1, 0]
model = sm.OLS(yi, Z)
results = model.fit()
AB = results.params
A = AB[0]
B = AB[1]
transistor_count_predicted = np.exp(B) * np.exp(A * year)
transistor_Moores_law = Moores_law(year)
y = np.linspace(2016.5, 2017.5)
Moore_Model2017 = Moores_law(y)
notes = "the arrays in this file are the result of a linear regression model\n"
notes += """the arrays include
year: year of manufacture
"""
notes += "transistor_count: number of transistors reported by manufacturers in a given year\n"
notes += "transistor_count_predicted: linear regression model = exp({:.2f})*exp({:.2f}*year)\n".format(
    B, A
)
notes += "transistor_Moores_law: Moores law =exp({:.2f})*exp({:.2f}*year)\n".format(
    B_M, A_M
)
notes += "regression_csts: linear regression constants A and B for log(transistor_count)=A*year+B"
np.savez(
    "mooreslaw_regression.npz",
    notes=notes,
    year=year,
    transistor_count=transistor_count,
    transistor_count_predicted=transistor_count_predicted,
    transistor_Moores_law=transistor_Moores_law,
    regression_csts=AB,
)
head = "the columns in this file are the result of a linear regression model\n"
head += """the columns include
year: year of manufacture
"""
head += "transistor_count: number of transistors reported by manufacturers in a given year\n"
head += "transistor_count_predicted: linear regression model = exp({:.2f})*exp({:.2f}*year)\n".format(
    B, A
)
head += "transistor_Moores_law: Moores law =exp({:.2f})*exp({:.2f}*year)\n".format(
    B_M, A_M
)
head += "year:, transistor_count:, transistor_count_predicted:, transistor_Moores_law:"
output = np.block(
    [
        year[:, np.newaxis],
        transistor_count[:, np.newaxis],
        transistor_count_predicted[:, np.newaxis],
        transistor_Moores_law[:, np.newaxis],
    ]
)
np.savetxt("mooreslaw_regression.csv", X=output, delimiter=",", header=head)
