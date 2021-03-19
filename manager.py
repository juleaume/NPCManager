from configparser import ConfigParser
import random
from typing import Tuple, Union

from constant_strings import *


class NPCGenerator:
    """
    Generate a NPC given rules passed as tags
    """

    def __init__(self, config):
        self.config = config
        self.traits, self.tags = self.get_config()

    def get_config(self) -> Tuple[dict, dict]:
        """
        get the global configuration from the config file
        :return: a dict containing all the traits per categories and all the tags per trait
        """
        traits = dict()
        tags = dict()
        for sec in self.config:  # for each section of the config file
            traits[sec] = list()  # create a new list of traits
            for el in self.config[sec]:  # for each element in the section
                tags[el.upper()] = set()  # create a new set of tags
                traits[sec].append(el)  # add the element to the list of trait
                for tag in self.config[sec][el].split(','):  # for each tag of the trait
                    tags[el.upper()].add(tag.strip())  # add the tag to the set
        return traits, tags

    def generate(self, *tags) -> dict:
        """
        Generate a random NPC
        :param tags: the list of tags to rule the NPC tp create
        :return: a dict containing all the NPC information
        """
        tags = set(tags)  # it is easier to work with sets
        traits = dict()
        if not set(tags) & GENDERS:  # if no gender is requested
            gender = self.get_gender(tags)  # select a gender at random
        else:
            gender = random.choice(list(tags & GENDERS))  # else pick a gender from the request tag
        tags -= GENDERS  # remove the genders from the tag set
        tags.add(gender)  # only add the selected gender

        name = create_name(random.randint(1, 3))  # create a random name with a random number of syllables
        if TITLE in tags:  # if a title is requested in the tags set
            tags -= {TITLE}  # remove it from the set
            title = self.select_trait("TITLES", tags)  # select a random title given the tags
            name = title.capitalize() + " " + name  # add it to the name
            tags.add(title.lower())  # and add it to the tags, to avoid silly situations
            # (i.e. a low rank job with high rank title or vice-versa)
        specie, _ = self.get_gendered_trait(gender, "SPECIES", tags)

        job, _ = self.get_gendered_trait(gender, "JOBS", tags)
        appearance, _ = self.get_gendered_trait(gender, "APPEARANCES", tags)
        behavior, behavior_key = self.get_gendered_trait(gender, "BEHAVIOR", tags)  # the appearance key is kept because
        if ADJ in self.tags[behavior_key.upper()]:  # we need it in case of gendered traits
            behavior = f"est {behavior}"
        elif POSS in self.tags[behavior_key.upper()]:
            if PLUR in self.tags[behavior_key.upper()]:
                behavior = f"a de {behavior}"
            else:
                e_behavior = "e" if FEM in self.tags[behavior.upper()] else ""
                behavior = f"a un{e_behavior} {behavior}"
        personality, _ = self.get_gendered_trait(gender, "PERSONALITY", tags)

        accessories = self.select_trait("ACCESSORIES", tags).lower()

        traits["name"] = name
        traits["gender"] = gender
        traits["job"] = job
        traits["specie"] = specie
        traits["appearance"] = appearance
        traits["behavior"] = behavior
        traits["personality"] = personality
        traits["accessories"] = accessories
        return traits

    @staticmethod
    def get_gender(tags: set) -> str:
        """
        chose a gender
        :param tags: the tag set to give rules
        :return: the selected gender
        """
        if GENDERS.issubset(tags):
            return random.choice(list(GENDERS))
        elif WOM in tags:
            return WOM
        elif MAN in tags:
            return MAN
        else:
            return random.choice(list(GENDERS))

    def get_gendered_trait(self, gender: str, trait, tags) -> Tuple[str, str]:
        """
        select a trait given a gender
        :param gender: the selected gender
        :param trait: the trait to choose from
        :param tags: the tags to give rule
        :return: a tuple giving the gendered trait and its key to find its associated tags
        """
        while True:
            selected_trait = self.select_trait(trait, tags)  # we choose a trait
            genders = GENDERS.intersection(self.tags[selected_trait.upper()])  # a get the gender of the trait
            if not genders or gender in genders:  # if there is no preferred gender or its associated gender matches
                if gender == WOM and GENDERED in self.tags[selected_trait.upper()]:  # if the gender needs adjustments
                    return f"{selected_trait}e", selected_trait  # add an e to the end
                else:
                    return selected_trait, selected_trait  # else give it as it is
            else:  # if the preferred gendered does not match the trait's associated gender
                if GENDERED in self.tags[selected_trait.upper()]:  # if the trait is gendered
                    if gender == WOM:
                        return f"{selected_trait}e", selected_trait
                    elif gender == MAN:
                        return selected_trait, selected_trait  # if it is not, repeat until it is

    def _get_trait(self, trait) -> str:
        """
        get a random item from the config file
        :param trait: the section to pick from
        :return: a random trait regardless the tags
        """
        return random.choice(self.traits[trait])

    def get_tags(self, section) -> list:
        """
        Return the all tags for a given section for each element
        :param section: the section to get the tags from
        :return: a list of sets of tags
        """
        tags = list()
        for traits in self.config[section]:
            trait_set = set()
            for t in self.config[section][traits].split(','):
                trait_set.add(t.strip())
            tags.append(trait_set)
        return tags

    def get_all_tags(self) -> list:
        """
        get all the tags used in the config file
        :return: a list of all the tags
        """
        tags = list()
        for sec in self.config:
            for tag_list in list(self.get_tags(sec)):
                for tag in tag_list:
                    if tag not in tags:
                        tags.append(tag)
        return tags

    def get_tags_per_section(self) -> dict:
        """
        get a dict of all the tags per section
        :return: a dict containing all the tags, each key is a section
        """
        tags = dict()
        for sec in self.config:
            tags[sec] = list()
            for tag_list in list(self.get_tags(sec)):
                for tag in tag_list:
                    if tag not in tags[sec]:
                        tags[sec].append(tag)
        return tags

    def select_trait(self, trait: str, tags: set) -> str:
        """
        select a trait at random given the tags
        :param trait: the trait to select
        :param tags: the tags to give the rules
        :return: the chosen trait
        """
        tags = set(self.get_tags_per_section()[trait]) & tags
        possible_traits = list()  # we create a list of possibilities
        for each_trait in self.traits[trait]:  # for each trait in the config file
            if tags.issubset(tags):
                possible_traits.append(each_trait)  # add it to the list
        if possible_traits:  # if there are at least one choice
            selected_trait = random.choice(possible_traits)
        else:
            selected_trait = self._get_trait(trait)  # we select a random trait from the list
        if not self.check_tag(trait, tags):  # if there is no perfect match
            return selected_trait  # we return the selected trait
        while not tags.issubset(set(self.tags[selected_trait.upper()])):  # If a perfect match exists
            selected_trait = self._get_trait(trait)  # we pick another one to hope for something new
        return selected_trait  # and we return a trait that ALL of the tags match

    def check_tag(self, section, tags) -> bool:
        """
        check if there is a perfect match of tags
        :param section: the section to look in
        :param tags: the set of tags
        :return: True if there is at least one perfect match, False else
        """
        tags_list = self.get_tags(section)  # we get all the tags list for avery elements of this section
        for tag in tags_list:  # for each tag list
            if set(tags).issubset(tag):  # if there is at least one match
                return True  # we say there is at least one
        return False  # else we say there is no perfect match

    @staticmethod
    def get_characteristics(game: str, specie: str) -> Tuple[Union[int, str], Union[int, str], Union[int, str],
                                                             Union[int, str], Union[int, str], Union[int, str]]:
        """
        generate random characteristics given a game and a specie
        :param game: the game played
        :param specie: the specie asked
        :return: an array of stats given the game
        """
        stats = ConfigParser()
        stats.read("stats.ini", "utf8")
        if game == SW_TAG:
            try:
                vig_b, agi_b, int_b, rus_b, vol_b, pre_b = stats[game.upper()][specie].split(', ')
                return get_char(game, int(vig_b)), get_char(game, int(agi_b)), get_char(game, int(int_b)), \
                       get_char(game, int(rus_b)), get_char(game, int(vol_b)), get_char(game, int(pre_b))
            except KeyError:
                print(f"No stats for {specie} in game {game}")
                return 0, 0, 0, 0, 0, 0
        elif game == OGL_TAG:
            try:
                for_b, agi_b, con_b, int_b, sag_b, cha_b = stats[game.upper()][specie].split(', ')
                stat_for = get_char(game, int(for_b))
                stat_agi = get_char(game, int(agi_b))
                stat_con = get_char(game, int(con_b))
                stat_int = get_char(game, int(int_b))
                stat_sag = get_char(game, int(sag_b))
                stat_cha = get_char(game, int(cha_b))
                return f"{stat_for} ({(stat_for - 10) >> 1:+d})", f"{stat_agi} ({(stat_agi - 10) >> 1:+d})", \
                       f"{stat_con} ({(stat_con - 10) >> 1:+d})", f"{stat_int} ({(stat_int - 10) >> 1:+d})", \
                       f"{stat_sag} ({(stat_sag - 10) >> 1:+d})", f"{stat_cha} ({(stat_cha - 10) >> 1:+d})"
            except KeyError:
                print(f"No stats for {specie} in game {game}")
                return 0, 0, 0, 0, 0, 0


def get_char(game: str, mean: int) -> int:
    """
    get a random characteristic around the mean using a gauss bell curve with std deviation = 2
    If the value is bellow 0 or above the max of the game, the mean is returned to skew more toward it
    :param game: the game played
    :param mean: the value to
    :return: mean +/- gauss(0, 2)
    """
    max_stat = 6 if game == SW_TAG else 20
    stat = round(random.gauss(mean, 2))
    return stat if 0 < stat <= max_stat else mean


def create_name(length) -> str:
    """
    Generate a name given a length, with consonants + vowel n times with a 50% chance to add a consonant at the end
    :param length: the number of syllables wanted
    :return: a name randomised
    """
    consonants = [
        "z", "zl", "r", "rh", "t", "tr", "th", "tl", "tw", "y", "yh", "p", "pr", "ph", "pl", "q", "qu", "qs", "qh",
        "ql", "s", "sz", "st", "sp", "sq", "ss", "sf", "sh", "sk", "sm", "sw", "sc", "sv", "sb", "sn", "d", "dz", "dr",
        "dh", "dl", "f", "fz", "fr", "ft", "fp", "fh", "fl", "g", "gz", "gr", "gu", "gh", "gl", "h", "j", "jz", "js",
        "jh", "jl", "k", "kz", "kr", "ks", "kh", "kj", "kl", "kc", "l", "lh", "m", "mh", "mm", "mn", "w", "wz", "wr",
        "wh", "x", "xh", "c", "cz", "cr", "ct", "cs", "ch", "ck", "cl", "cw", "cx", "cc", "cv", "cn", "v", "vz", "vr",
        "vh", "vl", "b", "bz", "br", "bs", "bf", "bh", "bl", "bw", "bv", ""
    ]

    vowels = [
        "a", "aa", "ae", "aë", "au", "ai", "aï", "ao", "e", "ea", "ee", "eu", "ei", "eo", "y", "u", "ua", "ue", "uu",
        "ui", "uo", "i", "ia", "ie", "ii", "io", "o", "oa", "oe", "oë", "ou", "oi", "oo"
    ]
    name = ""
    for i in range(length):
        seg = random.choice(consonants) + random.choice(vowels)
        if not name or name[-1] in ["'", "-", " "]:
            seg = seg.capitalize()
        name += seg
        if i + 1 < length and random.randint(0, 1):
            name += random.choice(["", "'", "-", " "])
    if random.randint(0, 1):
        name += random.choice(consonants)
    return name


def main():
    npc = ConfigParser()
    npc.read("npc.ini", "utf8")
    npc_generator = NPCGenerator(npc)
    traits = npc_generator.generate()
    if traits['gender'] == WOM:
        e_gender = 'e'
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
    npc_description = f"{traits['name']} est un{e_gender} {traits['job']} {traits['specie']} plutôt " \
                      f"{traits['appearance']}, {traits['behavior']}, semble être {traits['personality']} et " \
                      f"a {det_accessories} {traits['accessories']}"
    print(npc_description)
    print(npc_generator.get_characteristics('sw', traits['specie']))


if __name__ == '__main__':
    main()
