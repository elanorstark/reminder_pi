from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import ST7789

BG_COLOUR = (0, 0, 0)
FONT = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 24)
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
