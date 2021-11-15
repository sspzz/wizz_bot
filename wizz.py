import os
import re
import sys
import shutil
import urllib.request
import zipfile
import imageio
import asyncio
import random
from PIL import Image, ImageSequence, ImageEnhance, ImageDraw, ImageFont
from opensea import get_wiz_url
import imagetools

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
    def url(self):
        return get_wiz_url(self.wiz_id)

    @property
    def path(self):
        return "{}/{}".format(self.artwork_root, self.wiz_id)

    @property
    def pfp(self):
        return "{}/{}.png".format(self.path, self.wiz_id)
    
    @property
    def pfp_nobg(self):
        return "{}/{}-nobg.png".format(self.path, self.wiz_id)

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
    def turnaround_nobg(self):
        return "{}/{}-nobg-s.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_large_nobg(self):
        return "{}/{}-nobg.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_mugshot(self):
        return "{}/{}-mugshot-s.gif".format(self.path, self.wiz_id)

    @property
    def turnaround_mugshot_large(self):
        return "{}/{}-mugshot.gif".format(self.path, self.wiz_id)

    @property
    def rip(self):
        return "{}/{}-rip.png".format(self.path, self.wiz_id)

    @property
    def gm(self):
        return "{}/{}-gm.png".format(self.path, self.wiz_id)

    @property
    def sprites(self):
        return "{}/sprites".format(self.path)

    @property
    def spritesheet(self):
        return "{}/{}-spritesheet.png".format(self.path, self.wiz_id)

    @property
    def walkcycle(self):
        return "{}/{}-walkcycle-s.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_large(self):
        return "{}/{}-walkcycle.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_nobg(self):
        return "{}/{}-walkcycle-nobg-s.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_large_nobg(self):
        return "{}/{}-walkcycle-nobg.gif".format(self.path, self.wiz_id)

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
            def download_content():
                # Check cache if we don't want to force download
                if not refresh:
                    cached_wizards = os.listdir(path_artwork)
                    cached_wizard_path = None
                    for wiz_dir in cached_wizards:
                        if wiz_dir == wiz_id:
                            cached_wizard_path = wizard.path
                else:
                    cached_wizard_path = None

                # Download artwork
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
                if not os.path.isfile(wizard.pfp_nobg) or refresh:
                    pfp_original_file = "{}-{}-nobg.png".format(wizard.wiz_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", ""))
                    pfp_original = "{}/400/{}".format(wizard.path, pfp_original_file)
                    shutil.copy(pfp_original, wizard.pfp_nobg)                

                # Download spritesheet
                if cached_wizard_path is None or not os.path.isdir(wizard.sprites):
                    try:
                        os.makedirs(wizard.sprites)
                    except:
                        pass
                    urllib.request.urlretrieve("https://www.forgottenrunes.com/api/art/wizards/{}/spritesheet.png".format(wiz_id), wizard.spritesheet)        
                    sprite_tiles = imagetools.tile(Image.open(wizard.spritesheet), 4)
                    for i, sprite in enumerate(sprite_tiles):
                        sprite.save("{}/{}.png".format(wizard.sprites, 100+i))

            # Fetch artwork etc
            download_content()

            # Random mugshot background and frame
            mugshot_rand_bg_path = "{}/resources/mugshot/bg/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/bg")))
            mugshot_rand_frame_path = "{}/resources/mugshot/frame/{}".format(os.getcwd(), random.choice(os.listdir("resources/mugshot/frame")))

            # Generate "framed profile", aka. mugshot           
            imagetools.mugshot(wizard, mugshot_rand_bg_path, mugshot_rand_frame_path)

            # Generate animated turnaround GIFs        
            turnarounds_path = "{}/50/turnarounds".format(wizard.path)
            imagetools.gif(turnarounds_path, wizard.turnaround)
            imagetools.gif(turnarounds_path, wizard.turnaround_nobg, transparent=True)
            imagetools.gif(turnarounds_path, wizard.turnaround_large, dim=(400, 400))
            imagetools.gif(turnarounds_path, wizard.turnaround_large_nobg, dim=(400, 400), transparent=True)
            imagetools.gif(turnarounds_path, wizard.turnaround_mugshot, mugshot_rand_bg_path, mugshot_rand_frame_path)
            imagetools.gif(turnarounds_path, wizard.turnaround_mugshot_large, mugshot_rand_bg_path, mugshot_rand_frame_path, (400, 400))

            # Animated walk cycles
            imagetools.gif(wizard.sprites, wizard.walkcycle, duration=150)
            imagetools.gif(wizard.sprites, wizard.walkcycle_nobg, duration=150, transparent=True)
            imagetools.gif(wizard.sprites, wizard.walkcycle_large, duration=150, dim=(400, 400))
            imagetools.gif(wizard.sprites, wizard.walkcycle_large_nobg, duration=150, dim=(400, 400), transparent=True)

            # Generate RIP
            rip_bg = "{}/resources/veil/rip/bg.png".format(os.getcwd())
            rip_fg = "{}/resources/veil/rip/fg.png".format(os.getcwd())
            imagetools.rip(wizard, rip_bg, rip_fg)

            # Genereate GM
            imagetools.gm(wizard)


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
            summon_wizards([wizard])

async def summon_wizards(wizards):
    for wizard in wizards:
        WizardFactory.get_wizard(wizard, refresh=True)

async def main(argv):
    if len(argv) == 0:
        await interactive()
    else:
        await summon_wizards(argv)
            

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(sys.argv[1:]))
