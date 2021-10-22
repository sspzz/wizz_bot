import os
import re
import sys
import shutil
import urllib.request
import zipfile
import imageio
import asyncio
import random
from PIL import Image, ImageSequence

class Wizard(object):
    def __init__(self, wiz_id, artwork_root):
        self.wiz_id = wiz_id
        self.artwork_root = artwork_root

    @property
    def name(self):
        readme = open("{}/{}/README.md".format(self.artwork_root, self.wiz_id), 'rt')
        contents = readme.read()
        re_name = re.search('# Wizard: #[0-9]{1,4} (.*)', contents)
        if re_name is not None:
            return re_name.group(1).lower()
        return None

    @property
    def path(self):
        return "{}/{}".format(self.artwork_root, self.wiz_id)

    @property
    def pfp(self):
        return "{}/{}.png".format(self.path, self.wiz_id)
    
    @property
    def mugshot(self):
        return "{}/{}-mugshot-pfp.png".format(self.path, self.wiz_id)

    @property
    def turnaround(self):
        return "{}/{}s.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_large(self):
        return "{}/{}.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_mugshot(self):
        return "{}/{}-mugshot-s.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_mugshot_large(self):
        return "{}/{}-mugshot.gif".format(self.path, self.wiz_id)


class WizardFactory:
    @staticmethod
    def get_lore(wiz_id):
        return "https://www.forgottenrunes.com/lore/wizards/{}/0".format(wiz_id)

    @staticmethod
    def get_wizard(wiz_id, refresh=False):

        path_artwork = "{}/artwork".format(os.getcwd())
        try:
            os.makedirs(path_artwork)
        except:
            pass

        wizard = Wizard(wiz_id, path_artwork)

        try:
            # Check cache if we don't want to force download
            if not refresh:
                cached_wizards = os.listdir(path_artwork)
                cached_wizard_path = None
                for wiz_dir in cached_wizards:
                    if wiz_dir == wiz_id:
                        cached_wizard_path = wizard.path
            else:
                cached_wizard_path = None

            # Download fresh artwork, if not cached
            if cached_wizard_path is None:
                zip_file = "{}/{}.zip".format(path_artwork, wiz_id)
                endpoint_wizard_artwork = 'https://www.forgottenrunes.com/api/art/wizards/{}.zip'
                urllib.request.urlretrieve(endpoint_wizard_artwork.format(wiz_id), zip_file)
                zip_ref = zipfile.ZipFile(zip_file, 'r')
                zip_ref.extractall(wizard.path)
                os.remove(zip_file)

            # Extract main artwork, if not cached
            if not os.path.isfile(wizard.pfp) or refresh:
                pfp_original_file = "{}-{}.png".format(wizard.wiz_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", ""))
                pfp_original = "{}/400/{}".format(wizard.path, pfp_original_file)
                shutil.copy(pfp_original, wizard.pfp)

            def gen_mugshot(target, head, body, background, overlay):            
                fp_bg = Image.open(background)
                fp_frame = Image.open(overlay)
                wiz_head = None # Damn you headless wizard, this is for you
                for filename in sorted(os.listdir("{}/50".format(wizard.path))):
                    if filename.startswith("head"):
                        wiz_head = Image.open("{}/50/{}".format(wizard.path, filename))
                    if filename.startswith("body"):
                        wiz_body = Image.open("{}/50/{}".format(wizard.path, filename))            
                fp_bg.paste(wiz_body, (-9, 3), wiz_body)
                if wiz_head is not None:
                    fp_bg.paste(wiz_head, (-9, 3), wiz_head)
                fp_bg.paste(fp_frame, (0, 0), fp_frame)
                fp_final = fp_bg.resize((200, 200), Image.NEAREST)
                fp_final.save(target)

            def gen_turnaround(frames, target, background=None, overlay=None, dim=(100, 100)):
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
                        icc = fg.info.get('icc_profile')
                        bg.paste(fg, (0, 0), fg)
                    final_image = bg if not None else image
                    final_image = final_image.resize(dim, Image.NEAREST)
                    images.append(final_image)
                images[0].save(target, 
                                save_all=True, 
                                append_images=images[1:], 
                                optimize=False, 
                                quality=100, 
                                duration=600, 
                                loop=0,
                                icc_profile=icc)

            # Random mugshot background and frame
            mugshot_rand_bg_path = "{}/resources/mugshot/bg/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/bg")))
            mugshot_rand_frame_path = "{}/resources/mugshot/frame/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/frame")))

            # Generate "framed profile", aka. mugshot
            wiz_head = None
            wiz_body = None
            for filename in sorted(os.listdir("{}/50".format(wizard.path))):
                if filename.startswith("head"):
                    wiz_head = Image.open("{}/50/{}".format(wizard.path, filename))
                if filename.startswith("body"):
                    wiz_body = Image.open("{}/50/{}".format(wizard.path, filename))            
            gen_mugshot(wizard.mugshot, wiz_head, wiz_body, mugshot_rand_bg_path, mugshot_rand_frame_path)

            # Generate animated turnaround GIFs        
            turnarounds_path = "{}/50/turnarounds".format(wizard.path)
            gen_turnaround(turnarounds_path, wizard.turnaround)
            gen_turnaround(turnarounds_path, wizard.turnaround_large, dim=(400, 400))
            gen_turnaround(turnarounds_path, wizard.turnaround_mugshot, mugshot_rand_bg_path, mugshot_rand_frame_path)
            gen_turnaround(turnarounds_path, wizard.turnaround_mugshot_large, mugshot_rand_bg_path, mugshot_rand_frame_path, (400, 400))

        except Exception as e:
            print("Error: {}".format(str(e)))
            return None

        return wizard


async def interactive():
    while True:
        wizard = input("Whom shall I summon? > ")
        if wizard == "exit":
            return
        else:
            get_wizard_artwork(wizard, refresh=True)

async def summon_wizards(wizards):
    for wizard in wizards:
        WizardFactory.get_wizard(wizard, refresh=False)

async def main(argv):
    if len(argv) == 0:
        await interactive()
    else:
        await summon_wizards(argv)
            

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(sys.argv[1:]))
