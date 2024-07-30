import yaml
from munch import Munch
mydict = yaml.safe_load("""
a: 1
b:
- q: "foo"
  r: 99
  s: 98
- x: "bar"
  y: 97
  z: 96
c:
  d: 7
  e: 8
  f: [9,10,11]
""")
mymunch = Munch(mydict)

print(mymunch)
