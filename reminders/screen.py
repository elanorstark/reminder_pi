from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import ST7789
import random

BG_COLOUR = (0, 0, 0)
FONT = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 22)
FONT_L = ImageFont.truetype("assets/font/RobotoMono-Bold.ttf", 24)
FONT_XL = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 60)
BL_VALUE = 13


class Screen:
    disp = ST7789.ST7789(
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,
        dc=9,
        rst=25,
        backlight=BL_VALUE,
        spi_speed_hz=80 * 1000 * 1000
    )

    img = Image.new('RGB', (disp.width, disp.height), color=BG_COLOUR)
    draw = ImageDraw.Draw(img)

    backlight_status = True

    # prepares black rectangle to be drawn on screen
    @staticmethod
    def clear():
        if not Screen.backlight_status:
            Screen.toggle_backlight()
        Screen.draw.rectangle((0, 0, Screen.disp.width, Screen.disp.height), fill=BG_COLOUR)

    @staticmethod
    def off():
        Screen.clear()
        Screen.update_screen()
        Screen.disp.set_backlight(0)
        Screen.backlight_status = False

    @staticmethod
    def toggle_backlight():
        if not Screen.backlight_status:
            Screen.disp.set_backlight(BL_VALUE)
            Screen.update_screen()
            Screen.backlight_status = True
        else:
            Screen.off()

    # prepares text to be drawn on screen
    # can take position, font and colour optionally.
    @staticmethod
    def draw_text(text, position=(0, 0), font=FONT, fill=(255, 255, 255)):
        Screen.draw.text(position, text, fill, font)

    # updates the screen to show the prepared image
    @staticmethod
    def update_screen():
        Screen.disp.display(Screen.img)

    # clears screen, adds text, then displays image
    # example of how to use functions above
    @staticmethod
    def text_screen(text="Initial\nScreen"):
        Screen.clear()
        Screen.draw_text(text)
        Screen.update_screen()

    @staticmethod
    def home_screen(top_text, time_formatted, date_formatted):
        Screen.clear()
        epsilon_x = random.randint(-4, 4)
        epsilon_y = random.randint(-4, 4)
        Screen.draw_text(top_text, position=(10 + epsilon_x, 10 + epsilon_y),
                         font=FONT_L)
        Screen.draw_text(time_formatted, position=(33 + epsilon_x, 70 + epsilon_y),
                         font=FONT_XL)
        Screen.draw_text(date_formatted, position=(45 + epsilon_x, 140 + epsilon_y))
        Screen.update_screen()

    @staticmethod
    def menu_screen(top_text, main_text):
        Screen.clear()
        top_x, top_y = Screen.draw.textsize(top_text, FONT_L)
        # main_x, main_y = Screen.draw.textsize("> ", FONT)
        Screen.draw_text(top_text, position=(10, 10),
                         font=FONT_L)
        Screen.draw_text(main_text, position=(10, 20 + top_y))
        Screen.update_screen()
