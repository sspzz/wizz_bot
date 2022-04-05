import os
import random
from PIL import Image, ImageSequence, ImageEnhance, ImageDraw, ImageFont
from itertools import product
from io import BytesIO

class ImageText(object):
    def __init__(self, filename_or_size_or_Image, mode='RGBA', background=(0, 0, 0, 0),
                 encoding='utf8'):
        if isinstance(filename_or_size_or_Image, str):
            self.filename = filename_or_size_or_Image
            self.image = Image.open(self.filename)
            self.size = self.image.size
        elif isinstance(filename_or_size_or_Image, (list, tuple)):
            self.size = filename_or_size_or_Image
            self.image = Image.new(mode, self.size, color=background)
            self.filename = None
        elif isinstance(filename_or_size_or_Image, PIL.Image.Image):
            self.image = filename_or_size_or_Image
            self.size = self.image.size
            self.filename = None
        self.draw = ImageDraw.Draw(self.image)
        self.encoding = encoding

    def save(self, filename=None):
        self.image.save(filename or self.filename)
    
    def show(self):
        self.image.show()

    def get_font_size(self, text, font, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % \
                    text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(self, xy, text, font_filename, font_size=11,
                   color=(0, 0, 0), max_width=None, max_height=None):
        x, y = xy
        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width,
                                           max_height)
        text_size = self.get_text_size(font_filename, font_size, text)
        font = ImageFont.truetype(font_filename, font_size)
        if x == 'center':
            x = (self.size[0] - text_size[0]) / 2
        if y == 'center':
            y = (self.size[1] - text_size[1]) / 2
        self.draw.text((x, y), text, font=font, fill=color)
        return text_size

    def get_text_size(self, font_filename, font_size, text):
        font = ImageFont.truetype(font_filename, font_size)
        return font.getsize(text)

    def write_text_box(self, xy, text, box_width, font_filename,
                       font_size=11, color=(0, 0, 0), place='left',
                       justify_last_line=False, position='top',
                       line_spacing=1.0):
        x, y = xy
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            text_height = size[1] * line_spacing
            last_line_bleed = text_height - size[1]
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]
        
        if position == 'middle':
            height = (self.size[1] - len(lines)*text_height + last_line_bleed)/2
            height -= text_height # the loop below will fix this height
        elif position == 'bottom':
            height = self.size[1] - len(lines)*text_height + last_line_bleed
            height -= text_height  # the loop below will fix this height
        else:
            height = y
            
        for index, line in enumerate(lines):
            height += text_height
            if place == 'left':
                self.write_text((x, height), line, font_filename, font_size,
                                color)
            elif place == 'right':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = x + box_width - total_size[0]
                self.write_text((x_left, height), line, font_filename,
                                font_size, color)
            elif place == 'center':
                total_size = self.get_text_size(font_filename, font_size, line)
                x_left = int(x + ((box_width - total_size[0]) / 2))
                self.write_text((x_left, height), line, font_filename,
                                font_size, color)
            elif place == 'justify':
                words = line.split()
                if (index == len(lines) - 1 and not justify_last_line) or \
                   len(words) == 1:
                    self.write_text((x, height), line, font_filename, font_size,
                                    color)
                    continue
                line_without_spaces = ''.join(words)
                total_size = self.get_text_size(font_filename, font_size,
                                                line_without_spaces)
                space_width = (box_width - total_size[0]) / (len(words) - 1.0)
                start_x = x
                for word in words[:-1]:
                    self.write_text((start_x, height), word, font_filename,
                                    font_size, color)
                    word_size = self.get_text_size(font_filename, font_size,
                                                    word)
                    start_x += word_size[0] + space_width
                last_word_size = self.get_text_size(font_filename, font_size,
                                                    words[-1])
                last_word_x = x + box_width - last_word_size[0]
                self.write_text((last_word_x, height), words[-1], font_filename,
                                font_size, color)
        return (box_width, height - y)



def tile(img, x, y):
    w, h = img.size
    dx = int(w / x)
    dy = int(h / y)
    grid = product(range(0, h-h%dy, dy), range(0, w-w%dx, dx))
    tiles = []
    for i, j in grid:
        box = (j, i, j+dx, i+dy)
        tiles.append(img.crop(box))
    return tiles

def desaturate(img):
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.46)
    return img

def find_font_size(text, font, image, target_width_ratio):
    def get_text_size(text, image, font):
        im = Image.new('RGB', (image.width, image.height))
        draw = ImageDraw.Draw(im)
        return draw.textsize(text, font)
    tested_font_size = 24
    tested_font = ImageFont.truetype(font, tested_font_size)
    observed_width, observed_height = get_text_size(text, image, tested_font)
    estimated_font_size = tested_font_size / (observed_width / image.width) * target_width_ratio
    return round(estimated_font_size)

def text(text, dimensions, y_pos, font="resources/veil/rip/alagard.ttf", font_size=24, font_color=(82,64,50,255)):
    fnt = ImageFont.truetype(font, font_size)
    txt = Image.new("RGBA", dimensions, (255,255,255,0))
    d = ImageDraw.Draw(txt)
    w, h = d.textsize(text)
    d.text((dimensions[0]/2, y_pos), text, font=fnt, fill=font_color, anchor="mm")
    return txt

def gif(frames, target, background=None, overlay=None, dim=(100, 100), transparent=False, duration=600):
    images = []
    icc = None
    for image in frames:
        image = image.convert('RGBA', dither=None)
        if background is not None:
            bg = Image.open(background).convert('RGBA', dither=None)
            bg.paste(image, (-4, 3), image)
        else:
            bg = image
        if overlay is not None:
            fg = Image.open(overlay).convert('RGBA', dither=None)
            bg.paste(fg, (0, 0), fg)
        final_image = bg if not None else image
        final_image = final_image.resize(dim, Image.NEAREST)
        images.append(final_image)
    if transparent:
        images[0].save(target, save_all=True, append_images=images[1:], optimize=False, quality=100, duration=duration, loop=0, transparency=255, disposal=2)
    else:
        images[0].save(target, save_all=True, append_images=images[1:], optimize=False, quality=100, duration=duration, loop=0)

def overlay(images, scale=1):
    bg = None
    for img, offset in images:
        if bg is not None:
            bg.paste(img, offset, img)
        else:
            size = (img.size[0]*scale, img.size[1]*scale)
            bg = img
    bg.resize(size, Image.NEAREST)
    return bg

def all_png(path):
    return [f for f in sorted(os.listdir(path)) if f.endswith('.png')]

def to_png(img):
    byteImgIO = BytesIO()
    img.save(byteImgIO, "PNG")
    byteImgIO.seek(0)
    return byteImgIO

###########################################################################################


def mugshot(wizard):
    bg = Image.open("{}/resources/mugshot/bg/{}".format(os.getcwd(), random.choice(all_png("resources/mugshot/bg"))))
    fg = Image.open("{}/resources/mugshot/frame/{}".format(os.getcwd(), random.choice(all_png("resources/mugshot/frame"))))
    head = Image.new("RGBA", (50,50), (0,0,0,255))
    for filename in all_png("{}/50".format(wizard.path)):
        if filename.startswith("head"):
            head = Image.open("{}/50/{}".format(wizard.path, filename))
        if filename.startswith("body"):
            body = Image.open("{}/50/{}".format(wizard.path, filename))               
    layers = [
    	(bg, (0,0)),
    	(body, (-9, 3)),
    	(head, (-9, 3)),
    	(fg, (0,0))
    ]
    overlay(layers, 4).save(wizard.mugshot)

def gm(wizard):
    img_gm = Image.open("{}/resources/gm/gm.png".format(os.getcwd()))
    img_wiz = Image.open(wizard.pfp_nobg).resize((200, 200), Image.NEAREST)
    wiz_bg = next(filter(lambda f: f.startswith("background"), os.listdir("{}/50".format(wizard.path))), None)
    if wiz_bg is not None:
        img_bg = Image.open("{}/50/{}".format(wizard.path, wiz_bg)).resize((305, 210))
    else:
        img_bg = Image.new("RGB", (305, 210), (0,0,0,255))
    img_bg.paste(img_gm, (10, 10), img_gm)
    img_bg.paste(img_wiz, (100, 20), img_wiz)
    img_bg.save(wizard.gm)

def rip(wizard, size=(520, 520), offset=(42, 34)):
    background = "{}/resources/veil/rip/bg.png".format(os.getcwd())
    overlay = "{}/resources/veil/rip/fg.png".format(os.getcwd())
    # Build image with wizard head, body, prop
    fp_bg = Image.open(background)
    fp_frame = Image.open(overlay)
    wiz_head = None # Damn you headless wizard, this is for you
    wiz_prop = None
    for filename in all_png("{}/50".format(wizard.path)):
        if filename.startswith("head"):
            wiz_head = Image.open("{}/50/{}".format(wizard.path, filename))
            wiz_head = desaturate(wiz_head)
        if filename.startswith("body"):
            wiz_body = Image.open("{}/50/{}".format(wizard.path, filename))            
            wiz_body = desaturate(wiz_body)
        if filename.startswith("prop"):
            wiz_prop = Image.open("{}/50/{}".format(wizard.path, filename))            
            wiz_prop = desaturate(wiz_prop)
    fp_bg.paste(wiz_body, offset, wiz_body)
    if wiz_prop is not None:
    	fp_bg.paste(wiz_prop, offset, wiz_prop)
    if wiz_head is not None:
        fp_bg.paste(wiz_head, offset, wiz_head)
    fp_bg.paste(fp_frame, (0, 0), fp_frame)
    fp_final = fp_bg.resize(size, Image.NEAREST)
    # Top banner
    title = text(" Rest In Peace", fp_final.size, 62)
    fp_final.paste(title, (0,0), title)
    # Bottom banner
    font = "resources/veil/rip/alagard.ttf"
    epitaph = "Burnt, But Notte Forgotten"
    font_size = min(find_font_size(wizard.name.title(), font, fp_final, 0.4), find_font_size(epitaph, font, fp_final, 0.4))
    subtitle1 = text(wizard.name.title(), fp_final.size, 449, font, font_size, (20,15,12,200))
    subtitle2 = text(epitaph, fp_final.size, 466, font, font_size, (20,15,12,200))
    fp_final.paste(subtitle1, (0,0), subtitle1)
    fp_final.paste(subtitle2, (0,0), subtitle2)                

    fp_final.save(wizard.rip)

def walkcycle(wizard):
    sprites = tile(Image.open(wizard.spritesheet), 4, 4)
    gif(sprites, wizard.walkcycle, duration=150)
    gif(sprites, wizard.walkcycle_nobg, duration=150, transparent=True)
    gif(sprites, wizard.walkcycle_large, duration=150, dim=(400, 400))
    gif(sprites, wizard.walkcycle_large_nobg, duration=150, dim=(400, 400), transparent=True)

import numpy as np

def sprites_walkcycle_familiar(wizard):
    try:
        sprites = tile(Image.open(wizard.spritesheet_familiar), 4, wizard.spritesheet_familiar_rows)
        # ignore idle frames
        if wizard.spritesheet_familiar_rows == 8:
            for i in range(4, 32, 4):
                del sprites[i:i+4]
        return sprites
    except:
        return None

def walkcycle_familiar(wizard):
    sprites = sprites_walkcycle_familiar(wizard)
    if sprites is not None:
        gif(sprites, wizard.walkcycle_familiar, duration=150)
        gif(sprites, wizard.walkcycle_familiar_nobg, duration=150, transparent=True)
        gif(sprites, wizard.walkcycle_familiar_large, duration=150, dim=(400, 400))
        gif(sprites, wizard.walkcycle_familiar_large_nobg, duration=150, dim=(400, 400), transparent=True)

def walkcycle_wizard_and_familiar(wizard):
    def generate_walkcycle(reversed=False):
        sf = sprites_walkcycle_familiar(wizard)
        if sf is None:
            return
        sw = tile(Image.open(wizard.spritesheet), 4, 4)
        # use only "right facing" frames
        if reversed:
            sf = sf[4:8]
            sw = sw[4:8]
        else:
            sf = sf[-4:]
            sw = sw[-4:]
        # double the speed of familiar relative to wizard
        sf.extend(sf)
        sw = [val for val in sw for _ in (0, 1)]
        # double the speed of floor relative to wizard/familiar by doubling frames
        sf = [val for val in sf for _ in (0, 1)]
        sw = [val for val in sw for _ in (0, 1)]
        combined = []
        for i in range(0, len(sw)):
            def combine(left, right, bottom):
                wiz_bg = next(filter(lambda f: f.startswith("background"), os.listdir("{}/50".format(wizard.path))), None)
                if wiz_bg is not None:
                    bg = Image.open("{}/50/{}".format(wizard.path, wiz_bg)).resize((100, 50))
                else:
                    bg = Image.new("RGBA", size=(100,50), color=(0,0,0,255))
                bg.paste(left, (10,0), left)
                bg.paste(right, (40,0), right)
                bg.paste(bottom, (0, 45))
                return bg
            floor = Image.open("resources/gif/floor{}.png".format(i%4 if not reversed else 3 - i%4))
            img = combine(sw[i], sf[i], floor)
            combined.append(img)
        gif(combined, wizard.walkcycle_with_familiar if not reversed else wizard.walkcycle_with_familiar_reversed, duration=50, dim=(400, 200))
    generate_walkcycle(reversed=False)
    generate_walkcycle(reversed=True)

def catchphrase(wizard, phrase):
    # Add the text, for now truncated to 100 chars to avoid overflow - TODO: fill vertically to fix, adjusting font size
    font = 'resources/fonts/LitterboxICG.ttf'
    truncated_phrase = phrase[:66]
    img_gm = Image.open("{}/resources/gm/bubble.png".format(os.getcwd())).resize((200, 180), Image.NEAREST)
    img_wiz = Image.open(wizard.pfp_nobg).resize((400, 400), Image.NEAREST)
    wiz_bg = next(filter(lambda f: f.startswith("background"), os.listdir("{}/50".format(wizard.path))), None)
    if wiz_bg is not None:
        img_bg = Image.open("{}/400/{}".format(wizard.path, wiz_bg)).resize((610, 420))
    else:
        img_bg = Image.new("RGB", (610, 420), (0,0,0,255))
    img_bg.paste(img_gm, (20, 20), img_gm)
    img_bg.paste(img_wiz, (200, 40), img_wiz)
    img_text = ImageText((180, 130), background=(255, 255, 255, 0))
    font = "resources/veil/rip/alagard.ttf"
    img_text.write_text_box((0, 0), truncated_phrase, box_width=180, font_filename=font, font_size=24, color=(9,7,27), place='center', position='middle')
    img_bg.paste(img_text.image, (30, 38) , img_text.image)
    return img_bg
