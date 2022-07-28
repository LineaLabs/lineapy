import lineapy

art = {}
a = [1]
art["a"] = lineapy.save(a, "a")
a.append(2)
b = a[-1] + 1
art["b"] = lineapy.save(b, "b")
