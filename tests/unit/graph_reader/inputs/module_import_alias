import pandas as pd

import lineapy

art = {}

df = pd.DataFrame({"a": [1, 2]})
art["df"] = lineapy.save(df, "df")

df2 = pd.concat([df, df])
art["df2"] = lineapy.save(df2, "df2")
