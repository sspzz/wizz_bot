import os
from os import path
import re
import sys
import shutil
import urllib.request
import requests
from io import BytesIO
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

    def get_pony(self, pony_id):
        try:
            endpoint = "https://www.forgottenrunes.com/api/art/wizards/{}/riding/pony/{}".format(self.wiz_id, pony_id)
            urllib.request.urlretrieve(endpoint, self.pony)
            return True
        except:
            return False

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
    def rip(self):
        return "{}/{}-rip.png".format(self.path, self.wiz_id)

    @property
    def gm(self):
        return "{}/{}-gm.png".format(self.path, self.wiz_id)

    @property
    def spritesheet(self):
        return "{}/50/spritesheet/wizards-{}.png".format(self.path, self.wiz_id)

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

    @property
    def has_familiar(self):
        return path.exists(self.spritesheet_familiar)

    @property
    def spritesheet_familiar(self):
        return "{}/50/familiar-spritesheet/wizard-familiars-{}.png".format(self.path, self.wiz_id)

    @property
    def spritesheet_familiar_rows(self):
        path, dirs, files = next(os.walk("{}/50/familiar-spritesheet/frames".format(self.path)))
        return len(files) / 4

    @property
    def walkcycle_familiar(self):
        return "{}/{}-walkcycle-familiar-s.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_familiar_large(self):
        return "{}/{}-walkcycle-familiar.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_familiar_nobg(self):
        return "{}/{}-walkcycle-familiar-nobg-s.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_familiar_large_nobg(self):
        return "{}/{}-walkcycle-familiar-nobg.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_with_familiar(self):
        return "{}/{}-walkcycle-with-familiar.gif".format(self.path, self.wiz_id)

    @property
    def walkcycle_with_familiar_reversed(self):
        return "{}/{}-walkcycle-with-familiar-reverse.gif".format(self.path, self.wiz_id)

    @property
    def pony(self):
        return "{}/{}-pony.png".format(self.path, self.wiz_id)
  

class WizardFactory:
    @staticmethod
    def get_lore(wiz_id):
        return "https://www.forgottenrunes.com/lore/wizards/{}/0".format(wiz_id)

    @staticmethod
    def get_pony_walkcycle(wiz_id, pony_id, is_soul=False):
        url = "https://www.forgottenrunes.com/api/art/{}/{}/riding/pony/{}.gif".format("wizards" if not is_soul else "souls", wiz_id, pony_id)
        response = requests.get(url)
        return BytesIO(response.content)

    @staticmethod
    def catchphrase(token_id, phrase):
        wizard = WizardFactory.get_wizard(token_id)
        img = imagetools.catchphrase(wizard, phrase)
        return (wizard, imagetools.to_png(img))


    @staticmethod
    def get_wizard(wiz_id, refresh=False):

        path_artwork = "{}/artwork".format(os.getcwd())
        try:
            os.makedirs(path_artwork)
        except:
            pass

        wizard = Wizard(wiz_id, path_artwork)

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
                pfp_original_file = "{}-{}.png".format(wizard.wiz_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", "").replace(".", ""))
                pfp_original = "{}/400/{}".format(wizard.path, pfp_original_file)
                shutil.copy(pfp_original, wizard.pfp)
            if not os.path.isfile(wizard.pfp_nobg) or refresh:
                pfp_original_file = "{}-{}-nobg.png".format(wizard.wiz_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", "").replace(".", ""))
                pfp_original = "{}/400/{}".format(wizard.path, pfp_original_file)
                shutil.copy(pfp_original, wizard.pfp_nobg)
    
        try:
            # Fetch artwork etc
            download_content()

            # Generate content
            imagetools.mugshot(wizard)
            imagetools.walkcycle(wizard)
            imagetools.walkcycle_familiar(wizard)
            imagetools.walkcycle_wizard_and_familiar(wizard)
            imagetools.rip(wizard)
            imagetools.gm(wizard)

        except Exception as e:
            print("Error summoning {}: {}".format(wiz_id, str(e)))
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
        if argv[0] == "--all":
            all_wizzes = map(lambda i: str(i), range(0, 10000))
            await summon_wizards(all_wizzes)
        else:
            await summon_wizards(argv)
            

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(sys.argv[1:]))
