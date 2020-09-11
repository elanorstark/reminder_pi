from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import ST7789

BG_COLOUR = (0, 0, 0)
FONT = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 24)


class Screen:
    disp = ST7789.ST7789(
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,
        dc=9,
        rst=25,
        backlight=13,
        spi_speed_hz=80 * 1000 * 1000
    )

    img = Image.new('RGB', (disp.width, disp.height), color=BG_COLOUR)
    draw = ImageDraw.Draw(img)

    @staticmethod
    def clear():
        Screen.draw.rectangle((0, 0, Screen.disp.width, Screen.disp.height), fill=BG_COLOUR)

    @staticmethod
    def draw_text(text, position=(0, 0), font=FONT, fill=(255, 255, 255)):
        Screen.draw.text(position, text, fill, font)

    @staticmethod
    def update_screen():
        Screen.disp.display(Screen.img)

    @staticmethod
    def text_screen(text="Initial\nScreen"):
        Screen.clear()
        Screen.draw_text(text)
        Screen.update_screen()
