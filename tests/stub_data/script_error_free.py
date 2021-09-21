import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open

df = pd.read_csv("simple_data.csv")
plt.imsave("simple_data.png", df)
img = open("simple_data.png")
img = img.resize([200, 200])
