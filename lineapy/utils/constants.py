import operator

SQLALCHEMY_ECHO = "SQLALCHEMY_ECHO"
DB_SQLITE_PREFIX = "sqlite:///"

# Transformer related
GET_ITEM = operator.__getitem__.__name__
SET_ITEM = operator.__setitem__.__name__
DEL_ITEM = operator.__delitem__.__name__
SET_ATTR = setattr.__name__
GETATTR = getattr.__name__
DEL_ATTR = delattr.__name__
IMPORT_STAR = "*"

# BinOPs
ADD = operator.__add__.__name__
SUB = operator.__sub__.__name__
MULT = operator.__mul__.__name__
DIV = operator.__truediv__.__name__
FLOORDIV = operator.__floordiv__.__name__
MOD = operator.__mod__.__name__
POW = operator.__pow__.__name__
LSHIFT = operator.__lshift__.__name__
RSHIFT = operator.__rshift__.__name__
BITOR = operator.__or__.__name__
BITXOR = operator.__xor__.__name__
BITAND = operator.__and__.__name__
MATMUL = operator.__matmul__.__name__


# UnaryOps
INVERT = operator.__invert__.__name__
POS = operator.__pos__.__name__
NEG = operator.__neg__.__name__

# CompareOps
EQ = operator.__eq__.__name__
NOTEQ = operator.__ne__.__name__
LT = operator.__lt__.__name__
LTE = operator.__le__.__name__
GT = operator.__gt__.__name__
GTE = operator.__ge__.__name__
IS = operator.is_.__name__
ISNOT = operator.is_not.__name__
IN = operator.__contains__.__name__
NOT = operator.not_.__name__
