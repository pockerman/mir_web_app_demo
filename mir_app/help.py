import matplotlib.pyplot as plt
from PIL import Image

if __name__ == '__main__':

    path = '/home/alex/qi3/mir_web_app_demo/static/imgs/assessment.png'
    img = x = Image.open(path)

    plt.imshow(img)
    plt.show()
