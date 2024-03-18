from fractpy.models import NewtonFractal
from pprint import pprint
import matplotlib
import os

version = 'v001'
img_name = 'fractal-' + version
out_name = img_name + '.png'
pprint(img_name)

model = NewtonFractal("x**8 - 4x**3 + x**2 - 6")
#model = NewtonFractal("x**3 - 1")
pprint(model)

p = model.plot(-2, 2, -2, 2, (1000, 1000))
p.savefig(img_name)

pprint(out_name)
pprint(os.stat(out_name))

