from configparser import ConfigParser
import random

from constant_strings import *


class NPCGenerator:

    def __init__(self, config):
        self.config = config
        self.traits, self.tags = self.get_config()

    def get_config(self):
        traits = dict()
        tags = dict()
        for sec in self.config:
            traits[sec] = list()
            for el in self.config[sec]:
                tags[el.upper()] = set()
                traits[sec].append(el)
                for tag in self.config[sec][el].split(','):
                    tags[el.upper()].add(tag.strip())
        return traits, tags

    def generate(self, *tags):
        tags = set(tags)
        traits = dict()
        if not set(tags) & GENDERS:
            gender = self.get_gender(tags)
        else:
            gender = random.choice(list(tags & GENDERS))
        tags -= GENDERS
        tags.add(gender)

        # name = self.select_trait("NAMES", tags)
        name = create_name(random.randint(1, 3))
        specie, _ = self.get_gendered_trait(gender, "SPECIES", tags)

        job, _ = self.get_gendered_trait(gender, "JOBS", tags)
        appearance, _ = self.get_gendered_trait(gender, "APPEARANCES", tags)
        behavior, behavior_key = self.get_gendered_trait(gender, "BEHAVIOR", tags)
        if "adj" in self.tags[behavior_key.upper()]:
            behavior = f"est {behavior}"
        elif "poss" in self.tags[behavior_key.upper()]:
            if "plur" in self.tags[behavior_key.upper()]:
                behavior = f"a de {behavior}"
            else:
                e_behavior = "e" if FEM in self.tags[behavior.upper()] else ""
                behavior = f"a un{e_behavior} {behavior}"
        personality, _ = self.get_gendered_trait(gender, "PERSONALITY", tags)

        accessories = self.select_trait("ACCESSORIES", tags).lower()

        traits["name"] = name.capitalize()
        traits["gender"] = gender
        traits["job"] = job
        traits["specie"] = specie
        traits["appearance"] = appearance
        traits["behavior"] = behavior
        traits["personality"] = personality
        traits["accessories"] = accessories
        return traits

    @staticmethod
    def get_gender(tags: set):
        if GENDERS.issubset(tags):
            return random.choice(list(GENDERS))
        elif {WOM, ENB}.issubset(tags):
            return random.choice([WOM, ENB])
        elif {MAN, ENB}.issubset(tags):
            return random.choice([MAN, ENB])
        elif {WOM, MAN}.issubset(tags):
            return random.choice([WOM, MAN])
        elif WOM in tags:
            return WOM
        elif MASC in tags:
            return MASC
        elif ENB in tags:
            return ENB
        else:
            return random.choice(list(GENDERS))

    def get_gendered_trait(self, gender: str, trait, tags):
        while True:
            selected_trait = self.select_trait(trait, tags)
            genders = GENDERS.intersection(self.tags[selected_trait.upper()])
            if not genders or gender in genders:
                if gender == WOM and GENDERED in self.tags[selected_trait.upper()]:
                    return f"{selected_trait}e", selected_trait
                elif gender == ENB and GENDERED in self.tags[selected_trait.upper()]:
                    return f"{selected_trait}·e", selected_trait
                else:
                    return selected_trait, selected_trait
            else:
                if GENDERED in self.tags[selected_trait.upper()]:
                    if gender == WOM:
                        return f"{selected_trait}e", selected_trait
                    elif gender == ENB:
                        return f"{selected_trait}·e", selected_trait
                    elif gender == MAN:
                        return selected_trait, selected_trait

    def get_trait(self, trait):
        return random.choice(self.traits[trait])

    def get_tags(self, section):
        tags = list()
        for traits in self.config[section]:
            trait_set = set()
            for t in self.config[section][traits].split(','):
                trait_set.add(t.strip())
            tags.append(trait_set)
        return tags

    def get_all_tags(self):
        tags = list()
        for sec in self.config:
            for tag_list in list(self.get_tags(sec)):
                for tag in tag_list:
                    if tag not in tags:
                        tags.append(tag)
        return tags

    def get_tags_per_section(self):
        tags = dict()
        for sec in self.config:
            tags[sec] = list()
            for tag_list in list(self.get_tags(sec)):
                for tag in tag_list:
                    if tag not in tags[sec]:
                        tags[sec].append(tag)
        return tags

    def select_trait(self, trait: str, tags: set) -> str:
        selected_trait = self.get_trait(trait)
        if not self.check_tag(trait, tags):
            return selected_trait
        while not tags.issubset(set(self.tags[selected_trait.upper()])):
            selected_trait = self.get_trait(trait)
        return selected_trait

    def check_tag(self, section, tags):
        tags_list = self.get_tags(section)
        for tag in tags_list:
            if set(tags).issubset(tag):
                return True
        return False

    @staticmethod
    def get_characteristics(game: str, specie: str):
        stats = ConfigParser()
        stats.read("stats.ini", "utf8")
        if '·' in specie:
            specie = specie[:-2]
        if game == "sw":
            try:
                vig_b, agi_b, int_b, rus_b, vol_b, pre_b = stats[game.upper()][specie].split(', ')
                return get_char(game, int(vig_b)), get_char(game, int(agi_b)), get_char(game, int(int_b)), \
                       get_char(game, int(rus_b)), get_char(game, int(vol_b)), get_char(game, int(pre_b))
            except KeyError:
                print(f"No stats for {specie} in game {game}")
                return 0, 0, 0, 0, 0, 0


def get_char(game: str, bias: int):
    if game == "sw":
        return round(random.triangular(1, 6, bias))
    elif game == "fantasy":
        return round(random.triangular(1, 20, bias))
    else:
        return 0


def create_name(length):
    consonnes = [
        "z", "zl", "r", "rh", "t", "th", "tl", "tw", "y", "yh", "p", "pr", "ph", "pl", "q", "qu", "qs", "qh", "ql", "s",
        "sz", "st", "sp", "sq", "ss", "sf", "sh", "sk", "sm", "sw", "sc", "sv", "sb", "sn", "d", "dz", "dr", "dh", "dl",
        "f", "fz", "fr", "ft", "fp", "fh", "fl", "g", "gz", "gr", "gu", "gh", "gl", "h", "j", "jz", "js", "jh", "jl",
        "k", "kz", "kr", "ks", "kh", "kj", "kl", "kc", "l", "lh", "m", "mh", "mm", "mn", "w", "wz", "wr", "wh", "x",
        "xh", "c", "cz", "cr", "ct", "cs", "ch", "ck", "cl", "cw", "cx", "cc", "cv", "cn", "v", "vz", "vr", "vh", "vl",
        "b", "bz", "br", "bs", "bf", "bh", "bl", "bw", "bv", ""
    ]

    voyelles = [
        "a", "aa", "ae", "au", "ai", "ao", "e", "ea", "ee", "eu", "ei", "eo", "y", "u", "ua", "ue", "uu", "ui", "uo",
        "i", "ia", "ie", "ii", "io", "o", "oa", "oe", "ou", "oi", "oo", "oui"
    ]
    name = ""
    for _ in range(length):
        name += random.choice(consonnes) + random.choice(voyelles)
        if random.randint(0, 1):
            name += random.choice(["", "'", "-", " "])
    if random.randint(0, 1):
        name += random.choice(consonnes)
    return name.capitalize()


def main():
    npc = ConfigParser()
    npc.read("npc.ini", "utf8")
    npc_generator = NPCGenerator(npc)
    traits = npc_generator.generate()
    if traits['gender'] == WOM:
        e_gender = 'e'
    elif traits['gender'] == ENB:
        e_gender = '·e'
    else:
        e_gender = ""
    if FEM in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "une"
    elif MASC in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "un"
    elif PLUR in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "de"
    elif PLURS in npc_generator.tags[traits['accessories'].upper()]:
        det_accessories = "des"
    else:
        det_accessories = ""
    npc_description = f"{traits['name']} est un{e_gender} {traits['job']} {traits['specie']} d'apparence " \
                      f"{traits['appearance']}, {traits['behavior']}, semble être {traits['personality']} et " \
                      f"a {det_accessories} {traits['accessories']}"
    print(npc_description)
    print(npc_generator.get_characteristics('sw', traits['specie']))


if __name__ == '__main__':
    main()
