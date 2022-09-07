import pandas

import lineapy

art = {}

df = pandas.DataFrame({"a": [1, 2]})
art["df"] = lineapy.save(df, "df")

df2 = pandas.concat([df, df])
art["df2"] = lineapy.save(df2, "df2")
