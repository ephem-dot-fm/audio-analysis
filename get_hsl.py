from webbrowser import get
from hue import get_hue


def get_hsl(file_name):
    hue = get_hue('cnn', f'{file_name}.mp3')
    print("HUE", hue)


if __name__ == "__main__":
    hue = get_hue('cnn', 'soundbytes/SOMACLQ_1662489047.mp3')
    print(hue)
