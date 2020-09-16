from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import ST7789

BG_COLOUR = (0, 0, 0)
FONT = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 22)
FONT_L = ImageFont.truetype("assets/font/RobotoMono-Bold.ttf", 24)
FONT_XL = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", 60)
BL_VALUE = 13

FONT_SIZE_ALIASES = {0: FONT, 1: FONT_L, 2: FONT_XL}


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
        return Screen.draw.textsize(text, font)

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
        # epsilon_x = random.randint(-4, 4)
        epsilon_x = sum(map(ord, time_formatted)) % 9 - 4
        epsilon_y = sum(map(ord, date_formatted + time_formatted)) % 9 - 4
        Screen.draw_text(top_text, position=(10 + epsilon_x, 10 + epsilon_y),
                         font=FONT_L)
        Screen.draw_text(time_formatted, position=(25 + epsilon_x, 70 + epsilon_y),
                         font=FONT_XL)
        Screen.draw_text(date_formatted, position=(50 + epsilon_x, 140 + epsilon_y))
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

    @staticmethod
    def multi_line_text(lines=None, start_xy=(0, 0), align="top"):
        for i in range(len(lines)):
            lines[i][0] = str(lines[i][0])
            lines[i][1] = int(round(lines[i][1], 0))
            if lines[i][1] > max(FONT_SIZE_ALIASES):
                lines[i][1] = max(FONT_SIZE_ALIASES)
            elif lines[i][1] < min(FONT_SIZE_ALIASES):
                lines[i][1] = min(FONT_SIZE_ALIASES)

        Screen.clear()
        x, y = start_xy
        i = 0
        while i < len(lines):
            if Screen.draw.textsize(lines[i][0], FONT_SIZE_ALIASES[lines[i][1]])[0] > Screen.disp.width:
                lines.insert(i + 1, [lines[i][0][-1], lines[i][1]])
                lines[i][0] = lines[i][0][0:-1]
                while Screen.draw.textsize(lines[i][0], FONT_SIZE_ALIASES[lines[i][1]])[0] > Screen.disp.width:
                    lines[i + 1][0] = lines[i][0][-1] + lines[i + 1][0]
                    lines[i][0] = lines[i][0][0:-1]
                    if len(lines) == 1:
                        break
            y += Screen.draw_text(lines[i][0], (x, y), FONT_SIZE_ALIASES[lines[i][1]])[1]
            i += 1
        Screen.update_screen()
