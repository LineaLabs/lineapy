# Internal

This document contains Linea internal development guidelines. It will not be 
included in the open source version of `lineapy`.


## Demo branch
The `demo` branch will be used for alpha user and potential customer 
conversations. Therefore, its reliability is of the utmost importance. 
It does not necessarily need to have the latest updates, unless the updates are
for improving reliability. 

To merge `main HEAD` into `demo` branch, follow the steps below:
1. Start a Github Codespace with `main HEAD` (which is the default). 
2. Run both `examples/Demo_1_Preprocessing.ipynb` and 
`examples/Demo_2_Modeling.ipynb` and check to make sure that there are no errors.
3. Go to Airflow and check to see that the two DAGs have been created and are 
executable. 
4. Exit codespace and stop the instance.
5. Restart the instance and rerun Steps 2 and 3.
6. Create a PR from `main` to `demo` and request @dorx for review.
