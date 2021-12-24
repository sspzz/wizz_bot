import os
import random
from PIL import Image, ImageSequence, ImageEnhance, ImageDraw, ImageFont
from itertools import product

def tile(img, num):
    w, h = img.size
    d = int(w / num)
    grid = product(range(0, h-h%d, d), range(0, w-w%d, d))
    tiles = []
    for i, j in grid:
        box = (j, i, j+d, i+d)
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
    for filename in sorted(os.listdir(frames)):
        image = Image.open("{}/{}".format(frames, filename)).convert('RGBA', dither=None)
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

def overlay(target, images, scale=1):
	bg = None
	for img, offset in images:
		if bg is not None:
			bg.paste(img, offset, img)
		else:
			size = (img.size[0]*scale, img.size[1]*scale)
			bg = img
	bg.resize(size, Image.NEAREST).save(target)

def random_png(path):
    return [f for f in sorted(os.listdir(path)) if f.endswith('.png')]

###########################################################################################


def mugshot(wizard):
    bg = Image.open("{}/resources/mugshot/bg/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/bg"))))
    fg = Image.open("{}/resources/mugshot/frame/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/frame"))))
    head = Image.new("RGBA", (50,50), (0,0,0,255))
    for filename in random_png("{}/50".format(wizard.path)):
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
    overlay(wizard.rip, layers, 4)

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
    for filename in random_png("{}/50".format(wizard.path)):
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

def walkcycles(wizard):
    sprites_path = "{}/50/spritesheet/frames".format(wizard.path)
    gif(sprites_path, wizard.walkcycle, duration=150)
    gif(sprites_path, wizard.walkcycle_nobg, duration=150, transparent=True)
    gif(sprites_path, wizard.walkcycle_large, duration=150, dim=(400, 400))
    gif(sprites_path, wizard.walkcycle_large_nobg, duration=150, dim=(400, 400), transparent=True)
