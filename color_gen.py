import numpy as np
from PIL import Image
def generate_colors():
    for i in range(1, 2000):
        color = list(np.random.choice(range(256), size=3))
        im = Image.new("RGB", (8,8), (color[0],color[1],color[2]))
        im.save("res/"+str(i)+".png")