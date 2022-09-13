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

soul_ids = [
    8500, 671, 1792, 5208, 8634, 28, 3425, 6769, 8723, 3179, 3791, 6359, 2201, 5766, 1604, 9669, 5629, 9841, 8196, 3483, 9733, 7136, 2918, 2912, 9150, 7447, 5035, 9760, 1654, 10, 8986, 9316, 7273, 576, 1033, 4662, 3802, 7916, 4371, 2177, 8210, 1235, 9006, 6856, 8800, 1156, 4463, 8213, 8702, 9781, 8743, 336, 9851, 7387, 2944, 1634, 4158, 2928, 6930, 8293, 1295, 2204, 322, 421, 474, 4553, 5710, 5767, 6147, 3563, 6723, 1483, 6625, 4513, 2843, 6031, 1949, 6877, 469, 5539, 3047, 2015, 2577, 1294, 6536, 1186, 165, 9631, 4665, 1562, 3365, 1126, 6520, 7313, 2410, 6676, 1834, 1446, 6673, 7033, 5759, 2073, 343, 2337, 7381, 3197, 7880, 2430, 9671, 1369, 1686, 3963, 5349, 4876, 3115, 7792, 4170, 2287, 5850, 7467, 4795, 6824, 8202, 1779, 3258, 2116, 5232, 8572, 4748, 6654, 8905, 6054, 7532, 8963, 906, 2206, 575, 3745, 3744, 4230, 9644, 8191, 4047, 5998, 240, 6303, 4874, 2851, 3599, 1019, 6878, 1820, 6399, 2417, 6810, 1443, 1195, 1023, 3243, 9099, 6395, 1020, 5404, 331, 2104, 9179, 3037, 5971, 8360, 7432, 2787, 4567, 5041, 3263, 9431, 8996, 5140, 8700, 6836, 6858, 9073, 493, 1028, 7127, 334, 7274, 2950, 705, 8399, 1720, 928, 1181, 5588, 5224, 7316, 4689, 4607, 6891, 5516, 6757, 1315, 2225, 2399, 2700, 3433, 3574, 6724, 5467, 3502, 177, 6241, 7365, 9523, 7392, 5528, 2721, 1970, 4459, 3468, 9528, 2004, 1678, 920, 6712, 184, 810, 1314, 1693, 3415, 7867, 8793, 2884, 7704, 8367, 9011, 8465, 5837, 1409, 2012, 5907, 5639, 3145, 1230, 1093, 8556, 6876, 4121, 1986, 7743, 7096, 8531, 2677, 3259, 7245, 4075, 7543, 404, 4128, 2309, 6006, 9383, 3336, 2027, 2581, 7772, 4872, 1855, 5805, 6847, 1983, 4135, 3446, 9198, 58, 3220, 9900, 7950, 2372, 2008, 181, 1078, 7927, 6532, 7002, 101, 3562, 7159, 1275, 6137, 3794, 1972, 3284, 1327, 1732, 7340, 6493, 9705, 8977, 8248, 6433, 6973, 2854, 2953, 3246, 6248, 5763, 4483, 6056, 2532, 2839, 5852, 2226, 1049, 8998, 1667, 7893, 1669, 2267, 8103, 1670, 3684, 6308, 4672, 3586, 3808, 8926, 1069, 2035, 5595, 4653, 1687, 3805, 4895, 8753, 4569, 7954, 7412, 4605, 4519, 9670, 5331, 1849, 1056, 2205, 6646, 6642, 6641, 573, 2409, 2208, 572, 579, 3394, 2311, 3494, 6518, 2316, 2317, 5663, 621, 16, 3265, 4241, 1632, 9224, 818, 3418, 3176, 3174, 6167, 4548, 2479, 8184, 8085, 3509, 3720, 8756, 847, 566, 3224, 9659, 5647, 2593, 5068, 5325, 6225, 8791, 628, 5659, 8415, 30, 6036, 1046, 8289, 2106, 2751, 5462, 3928, 7312, 7309, 7806, 1001, 9056, 9451, 8099, 8397, 2932, 9237, 9755, 146, 6355, 260, 5064, 9807, 435, 2706, 8267, 2067, 1799, 2385, 9805, 133, 9635, 4517, 6044, 693, 2742, 6855, 3815, 4802, 3417, 9592, 8357, 3925, 2753, 4030, 3962, 5960, 6076, 1864, 463, 3059, 2086, 5530, 7824, 9117, 8074, 6688, 3122, 7270, 7226, 4870, 1981, 1722, 9593, 1458, 1277, 2544, 428, 965, 7088, 3842, 8006, 553, 580, 1781, 8792, 1099, 4252, 3810, 8757, 5343, 5455, 9788, 8499, 8186, 283, 5358, 271, 4740, 445, 2443, 1704, 7147, 1370, 6522, 1804, 6527, 6830, 7456, 7945, 8540, 4464, 1708, 2611, 4792, 3055, 4042, 4857, 1013, 5320, 2248, 3935, 8927, 464, 5233, 9318, 5050, 6016, 7910, 7918, 4966, 9894, 7019, 9707, 1780, 2521, 1848, 8602, 8288, 6335, 9835, 4613, 9561, 1282, 98, 3274, 4865, 8799, 6993, 4470, 2692, 8506, 3231, 5055, 7742, 5348, 3088, 6112, 277, 4944, 6489, 7186, 29, 1466, 2455, 2379, 1225, 5376, 9252, 9343, 3774, 9449, 2231, 7005, 4235, 1103, 697, 1498, 2527, 6163, 6311, 3240, 6495, 6283, 4094, 988, 5497, 721, 6010, 248, 955, 6223, 7689, 8087, 110, 8240, 7866, 5702, 2811, 2120, 8343, 2685, 7384, 5848, 665, 952, 1955, 9798, 3214, 5137, 3642, 1990, 9308, 2486, 9329, 5614, 7874, 1367, 5425, 1996, 6247, 8997, 7031, 6629, 5028, 4362, 7476, 2892, 482, 8639, 2352, 9693, 3429
]
def soul_exists(token_id):
    return int(token_id) in soul_ids

class Wizard(object):
    def __init__(self, token_id, artwork_root, base_dimension=50):
        self.token_id = token_id
        self.artwork_root = artwork_root
        self.base_dimension = base_dimension

    def __eq__(self, other):
        if isinstance(other, Wizard):
            return self.token_id == other.token_id
        return False

    def get_pony(self, pony_id):
        try:
            endpoint = "https://www.forgottenrunes.com/api/art/wizards/{}/riding/pony/{}".format(self.token_id, pony_id)
            urllib.request.urlretrieve(endpoint, self.pony)
            return True
        except:
            return False

    @property
    def name(self):
        readme = open("{}/{}/README.md".format(self.artwork_root, self.token_id), 'rt')
        contents = readme.read()
        re_name = re.search('# Wizard: #[0-9]{1,5} (.*)', contents)
        if re_name is not None:
            return re_name.group(1).lower()
        return None

    @property
    def url(self):
        return get_wiz_url(self.token_id)

    @property
    def path(self):
        return "{}/{}".format(self.artwork_root, self.token_id)

    @property
    def base_assets_path(self):
        return "{}/{}".format(self.path, self.base_dimension)

    @property
    def is_warrior(self):
        return self.base_dimension == 60

    @property
    def pfp(self):
        return "{}/{}.png".format(self.path, self.token_id)

    @property
    def pfp_nobg(self):
        return "{}/{}-nobg.png".format(self.path, self.token_id)

    @property
    def mugshot(self):
        return "{}/{}-mugshot-pfp.png".format(self.path, self.token_id)

    @property
    def rip(self):
        return "{}/{}-rip.png".format(self.path, self.token_id)

    @property
    def gm(self):
        return "{}/{}-gm.png".format(self.path, self.token_id)

    @property
    def spritesheet(self):
        return "{}/50/spritesheet/wizards-{}.png".format(self.path, self.token_id)

    @property
    def walkcycle(self):
        return "{}/{}-walkcycle-s.gif".format(self.path, self.token_id)

    @property
    def walkcycle_large(self):
        return "{}/{}-walkcycle.gif".format(self.path, self.token_id)

    @property
    def walkcycle_nobg(self):
        return "{}/{}-walkcycle-nobg-s.gif".format(self.path, self.token_id)

    @property
    def walkcycle_large_nobg(self):
        return "{}/{}-walkcycle-nobg.gif".format(self.path, self.token_id)

    @property
    def has_familiar(self):
        return path.exists(self.spritesheet_familiar)

    @property
    def spritesheet_familiar(self):
        return "{}/50/familiar-spritesheet/wizard-familiars-{}.png".format(self.path, self.token_id)

    @property
    def spritesheet_familiar_rows(self):
        path, dirs, files = next(os.walk("{}/50/familiar-spritesheet/frames".format(self.path)))
        return len(files) / 4

    @property
    def walkcycle_familiar(self):
        return "{}/{}-walkcycle-familiar-s.gif".format(self.path, self.token_id)

    @property
    def walkcycle_familiar_large(self):
        return "{}/{}-walkcycle-familiar.gif".format(self.path, self.token_id)

    @property
    def walkcycle_familiar_nobg(self):
        return "{}/{}-walkcycle-familiar-nobg-s.gif".format(self.path, self.token_id)

    @property
    def walkcycle_familiar_large_nobg(self):
        return "{}/{}-walkcycle-familiar-nobg.gif".format(self.path, self.token_id)

    @property
    def walkcycle_with_familiar(self):
        return "{}/{}-walkcycle-with-familiar.gif".format(self.path, self.token_id)

    @property
    def walkcycle_with_familiar_reversed(self):
        return "{}/{}-walkcycle-with-familiar-reverse.gif".format(self.path, self.token_id)

    @property
    def pony(self):
        return "{}/{}-pony.png".format(self.path, self.token_id)


class WizardFactory:
    @staticmethod
    def get_lore(token_id):
        return "https://www.forgottenrunes.com/lore/wizards/{}/0".format(token_id)

    @staticmethod
    def get_pony_walkcycle(token_id, pony_id, is_soul=False):
        url = "https://www.forgottenrunes.com/api/art/{}/{}/riding/pony/{}.gif".format("wizards" if not is_soul else "souls", token_id, pony_id)
        response = requests.get(url)
        return BytesIO(response.content)

    @staticmethod
    def catchphrase(token_id, phrase, is_soul=False, is_warrior=False):
        wizard = WizardFactory.get_wizard(token_id, is_soul=is_soul, is_warrior=is_warrior)
        img = imagetools.catchphrase(wizard, phrase, is_warrior=is_warrior)
        return (wizard, imagetools.to_png(img))

    @staticmethod
    def anatomy(token_id, is_soul=False, is_warrior=False):
        wizard = WizardFactory.get_wizard(token_id, is_soul=is_soul, is_warrior=is_warrior)
        others = []
        for i in range(25):
            ignore = list(map(lambda w: w.token_id, others.copy()))
            ignore.append(wizard.token_id)
            other = WizardFactory.random_cached_wizard(is_soul=is_soul, is_warrior=is_warrior, ignore=ignore)
            def random_id():
                if is_soul:
                    return random.choice(list(filter(lambda id: id not in ignore, soul_ids)))
                elif is_warrior:
                    return random.randint(0, 15999)
                else:
                    return random.randint(0, 9999)
            others.append(other if other is not None else WizardFactory.get_wizard(random_id(), is_soul=is_soul, is_warrior=is_warrior))
        img = imagetools.poster(wizard, others, is_warrior=is_warrior, is_soul=is_soul)
        return (wizard, imagetools.to_png(img))

    @staticmethod
    def random_cached_wizard(is_soul=False, is_warrior=False, ignore=[]):
        path_artwork = "{}/artwork/{}".format(os.getcwd(), "souls" if is_soul else "warriors" if is_warrior else "wizards")
        available = [f for f in sorted(os.listdir(path_artwork)) if not f.startswith('.') and int(f) not in ignore]
        if len(available) > 0:
            return Wizard(int(random.choice(available)), path_artwork)
        else:
            return None

    @staticmethod
    def get_wizard(token_id, refresh=False, is_soul=False, is_warrior=False):
        token_id = int(token_id)

        if is_soul and not soul_exists(token_id):
            return None

        path_artwork = "{}/artwork/{}".format(os.getcwd(), "souls" if is_soul else "warriors" if is_warrior else "wizards")
        os.makedirs(path_artwork, exist_ok=True)

        wizard = Wizard(token_id, path_artwork, 60 if is_warrior else 50)

        def download_content():
            # Check cache if we don't want to force download
            def listdirs(folder):
                return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
            if not refresh:
                cached_wizards = listdirs(path_artwork)
                cached_wizard_path = None
                for wiz_dir in cached_wizards:
                    if int(wiz_dir) == token_id:
                        cached_wizard_path = wizard.path
            else:
                cached_wizard_path = None

            # Download artwork
            if cached_wizard_path is None:
                zip_file = "{}/{}.zip".format(path_artwork, token_id)
                endpoint_wizard_artwork = 'https://www.forgottenrunes.com/api/art/{}/{}.zip'.format("souls" if is_soul else "warriors" if is_warrior else "wizards", token_id)
                urllib.request.urlretrieve(endpoint_wizard_artwork.format(token_id), zip_file)
                zip_ref = zipfile.ZipFile(zip_file, 'r')
                zip_ref.extractall(wizard.path)
                os.remove(zip_file)

            # Extract main artwork, if not cached
            if not os.path.isfile(wizard.pfp) or refresh:
                pfp_original_file = "{}-{}.png".format(wizard.token_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", "").replace(".", ""))
                pfp_original = "{}/{}/{}".format(wizard.path, wizard.base_dimension*8, pfp_original_file)
                shutil.copy(pfp_original, wizard.pfp)
            if not os.path.isfile(wizard.pfp_nobg) or refresh:
                pfp_original_file = "{}-{}-nobg.png".format(wizard.token_id, wizard.name.replace("  ", " ").replace(" ", "-").replace("'", "").replace(".", ""))
                pfp_original = "{}/{}/{}".format(wizard.path, wizard.base_dimension*8, pfp_original_file)
                shutil.copy(pfp_original, wizard.pfp_nobg)

        try:
            # Fetch artwork
            download_content()

            # Generate content
            if not is_soul and not is_warrior:
                imagetools.walkcycle(wizard)
                imagetools.walkcycle_familiar(wizard)
                imagetools.walkcycle_wizard_and_familiar(wizard)
                imagetools.rip(wizard)
            if not is_warrior:
                imagetools.mugshot(wizard)
            imagetools.gm(wizard)

        except Exception as e:
            print("Error summoning {}: {}".format(token_id, str(e)))
            return None

        return wizard


async def interactive():
    while True:
        wizard = input("Whom shall I summon? > ")
        if wizard == "exit":
            return
        else:
            summon_wizards([wizard])

async def summon_wizards(wizards, is_soul=False, is_warrior=False):
    emoji = "💀" if is_soul else "⚔️ " if is_warrior else "🧙🏻‍♂️"
    for wizard in wizards:
        print("Summoning {} {}".format(emoji, wizard))
        WizardFactory.get_wizard(wizard, refresh=True, is_soul=is_soul, is_warrior=is_warrior)

async def main(argv):
    if len(argv) == 0:
        await interactive()
    else:
        if argv[0] == "--all":
            all_wizzes = map(lambda i: str(i), range(0, 10000))
            all_souls = map(lambda i: str(i), soul_ids)
            all_warriors = map(lambda i: str(i), range(0, 16000))
            await summon_wizards(all_wizzes)
            await summon_wizards(all_souls, is_soul=True)
            await summon_wizards(all_warriors, is_warrior=True)
        elif argv[0] == "-s" and len(argv) >= 2:
            await summon_wizards(argv[1:], is_soul=True)
        elif argv[0] == "-w" and len(argv) >= 2:
            await summon_wizards(argv[1:], is_warrior=True)
        else:
            await summon_wizards(argv)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(sys.argv[1:]))
