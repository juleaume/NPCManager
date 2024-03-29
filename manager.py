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
                    return apply_gender(selected_trait), selected_trait  # add an e to the end
                else:
                    return selected_trait, selected_trait  # else give it as it is
            else:  # if the preferred gendered does not match the trait's associated gender
                if GENDERED in self.tags[selected_trait.upper()]:  # if the trait is gendered
                    if gender == WOM:
                        return apply_gender(selected_trait), selected_trait
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
            if tags.issubset(self.tags[each_trait.upper()]):
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

    def get_tag_list(self):
        working_tags = [MASC, FEM, PLUR, PLURS, ADJ, POSS, VERB, GENDERED, BEHAVE]
        for tag in [TITLE] + self.get_all_tags():
            if tag not in working_tags:
                yield tag

    @staticmethod
    def get_characteristics(game: str, specie: str, job_key: str) -> Tuple[
        Union[int, str], Union[int, str], Union[int, str],
        Union[int, str], Union[int, str], Union[int, str]]:
        """
        generate random characteristics given a game and a specie
        :param game: the game played
        :param specie: the specie asked
        :param job_key: the job specified
        :return: an array of stats given the game
        """
        stats = ConfigParser()
        stats.read("stats.ini", "utf8")
        if game == SW_TAG:
            try:
                vig_b, agi_b, int_b, rus_b, vol_b, pre_b = stats[game.upper()][specie].split(', ')
                vig_m, agi_m, int_m, rus_m, vol_m, pre_m = stats[game.upper()].get(
                    job_key, "0, 0, 0, 0, 0, 0").split(', ')
                return get_char(game, int(vig_b) + int(vig_m)), get_char(game, int(agi_b) + int(agi_m)), \
                       get_char(game, int(int_b) + int(int_m)), get_char(game, int(rus_b) + int(rus_m)), \
                       get_char(game, int(vol_b) + int(vol_m)), get_char(game, int(pre_b) + int(pre_m))
            except KeyError:
                print(f"No stats for {specie} in game {game}")
                return 0, 0, 0, 0, 0, 0
        elif game == OGL_TAG:
            try:
                for_b, agi_b, con_b, int_b, sag_b, cha_b = stats[game.upper()][specie].split(', ')
                for_m, agi_m, con_m, int_m, sag_m, cha_m = stats[game.upper()].get(
                    job_key, "10, 10, 10, 10, 10, 10").split(', ')
                stat_for = get_char(game, int(for_b) + int(for_m))
                stat_agi = get_char(game, int(agi_b) + int(agi_m))
                stat_con = get_char(game, int(con_b) + int(con_m))
                stat_int = get_char(game, int(int_b) + int(int_m))
                stat_sag = get_char(game, int(sag_b) + int(sag_m))
                stat_cha = get_char(game, int(cha_b) + int(cha_m))
                return f"{stat_for} ({(stat_for - 10) >> 1:+d})", f"{stat_agi} ({(stat_agi - 10) >> 1:+d})", \
                       f"{stat_con} ({(stat_con - 10) >> 1:+d})", f"{stat_int} ({(stat_int - 10) >> 1:+d})", \
                       f"{stat_sag} ({(stat_sag - 10) >> 1:+d})", f"{stat_cha} ({(stat_cha - 10) >> 1:+d})"
            except KeyError:
                print(f"No stats for {specie} in game {game}")
                return 0, 0, 0, 0, 0, 0


def apply_gender(t) -> str:
    if t.endswith("er"):
        return f"{t}e".replace("ere", "ère")
    elif t.endswith("teur"):
        return f"{t}".replace("teur", "trice")
    elif t.endswith("eur"):
        return f"{t}".replace("eur", "euse")
    elif t.endswith("eux"):
        return f"{t}".replace("eux", "euse")
    elif t.endswith("if"):
        return f"{t}".replace("if", "ive")
    elif t.endswith("el"):
        return f"{t}le"
    elif t.endswith("et"):
        return f"{t}te"
    elif t.endswith("on") or t.endswith("en"):
        return f"{t}ne"
    else:
        return f"{t}e"


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


def generate_name(specie: str, gender: str) -> str:
    action = [
        "Appelle", "Arpente", "Bâtit", "Brise", "Broie", "Chante", "Cherche", "Guide", "Gratte", "Mange", "Marche",
        "Massacre", "Parle", "Porte", "Prend", "Sent", "Suit", "Tranche", "Veille", "Voit"
    ]
    anatomie = [
        "Aile", "Barbe", "Bras", "Chair", "Coeur", "Crâne", "Crête", "Croc", "Dent", "Dos", "Echine", "Fourrure",
        "Griffe", "Mâchoire", "Main", "OEil", "Pied", "Poing", "Souffle", "Tête"
    ]
    creature = [
        "Aigle", "Ange", "Belette", "Cerf", "Cheval", "Corbeau", "Corneille", "Diable", "Dragon", "Faucon", "Homme",
        "Lion", "Loup", "Molosse", "Monstre", "Rat", "Requin", "Sanglier", "Serpent", "Tigre"
    ]
    elements = [
        "Aube", "Ciel", "Colline", "Crépuscule", "Eclair", "Etoile", "Feu", "Flamme", "Givre", "Lune", "Mer",
        "Montagne", "Nuage", "Pierre", "Pluie", "Soleil", "Tempête", "Terre", "Tonnerre", "Vent"
    ]
    gemmes = [
        "Acier", "Adamantine", "Argent", "Bronze", "Cuivre", "Diamant", "Emeraude", "Etain", "Fer", "Foyer", "Gemme",
        "Granite", "Jade", "Minerai", "Mithril", "Onyx", "Opale", "Or", "Rubis", "Saphir"
    ]
    nature = [
        "Arbre", "Bosquet", "Branche", "Brindille", "Caverne", "Chêne", "Epine", "Feuille", "Fleur", "Forêt", "Herbe",
        "Mousse", "Orme", "Pin", "Printemps", "Racine", "Rivière", "Saule", "Vallée", "Vigne"
    ]
    negatif = [
        "Brisé", "Cendres", "Déchiqueté", "Fétide", "Fléau", "Flétir", "Gris", "Malédiction", "Miasmes", "Mort", "Noir",
        "Nuit", "Ombre", "Os", "Rouge", "Sang", "Sombre", "Ténèbres", "Venin", "Vil"
    ]
    positif = [
        "Ame", "Aube", "Bénédiction", "Blanc", "Bleu", "Courageux", "Eté", "Gloire", "Héros", "Jour", "Juste", "Loi",
        "Lumière", "Printemps", "Pur", "Roi", "Soleil", "Vérité", "Vert", "Voeu"
    ]
    titre = [

    ]
    outils = [
        "Arc", "Bâton", "Bouclier", "Couteau", "Dague", "Enclume", "Epée", "Flèche", "Forge", "Garde", "Hache",
        "Harpon", "Lame", "Marteau", "Masse", "Pique", "Pointe", "Roue", "Scie"
    ]
    elfique_pref = [
        "Aen", "Ala", "And", "Ar", "Cas", "Cyl", "El", "Eln", "Fir", "Gael", "Hu", "Koeh", "Laer", "Lue", "Nail", "Rhy",
        "Sere", "Tia", "Tele", "Zau"
    ]
    elfique_suf = [
        "ael", "ari", "eth", "dil", "eil", "evar", "ir", "mus", "oth", "rad", "re", "riel", "rond", "sar", "sil",
        "tahl", "thus", "uil", "vain", "wyn"
    ]
    nain_m = [

    ]
    nain_f = [

    ]
    humain_m = [
        "Aiden", "Bruce", "Dirk", "Gareth", "Gregor", "Gustave", "Haslten", "Harold", "Jacques", "Jean", "Kirk", "Lief",
        "Liam", "Patrick", "Robert", "Ronan", "Seth", "Steven", "Tom", "William"
    ]
    humain_f = [
        "Abby", "Bridget", "Cate", "Marguerite", "Hélène", "Hilda", "Ingrid", "Jessica", "Linnea", "Maggie", "Natalia",
        "Olga", "Rebecca", "Raelia", "Rose", "Sarah", "Scarlett", "Sophia", "Tamara", "Violette"
    ]
    orque_pref = [

    ]
    orque_suf = [

    ]
    reptilien_pre = [
        "Geth", "Grath", "Gyss", "Hyss", "Kla", "Lath", "Lex", "Lyth", "Mor", "Nar", "Nyl", "Pesh", "Ssath", "Sser",
        "Ssla", "Tla", "Xer", "Xyl", "Xyss"
    ]
    reptilien_suf = [
        "chal", "chyss", "geth", "hesh", "hyll", "kesh", "klatch", "lyss", "mash", "moth", "myss", "resh", "ron", "ryn",
        "tetch", "tek", "thyss", "toss", "xec", "yss"
    ]

    article = "le"
    if gender == 'f':
        article = "la"

    t = roll_d(20)
    if specie == 'artificiel':
        if 0 < t <= 4:
            return select(elfique_pref + reptilien_pre) + select(elfique_suf + reptilien_suf)
        elif 4 < t <= 10:
            return f"{select(outils)} {select(positif)}"
        elif 10 < t <= 15:
            return f"{select(creature)} {select(negatif)} de {select(humain_m + humain_f)}"
        elif 15 < t:
            return f"{select(creature)} de {select(gemmes)} {roll_d(20)}.{roll_d(9)}"
    elif specie == 'drake':
        if 0 < t <= 6:
            return f"{select(anatomie)} de {select(elements)}"
        elif 6 < t <= 12:
            return f"{select(anatomie)} {select(negatif)}"
        elif 12 < t <= 18:
            return f"{select(anatomie)} {select(positif)}"
        elif 18 < t:
            return f"{select(reptilien_pre)}{select(reptilien_suf)} {article} {select(action)}"
    elif specie == 'elfe':
        nom = f"{select(elfique_pref)}{select(elfique_suf)}"
        if 0 < t <= 6:
            return f"{nom} {select(creature)}-{select(gemmes)}"
        elif 6 < t <= 12:
            return f"{nom} {select(anatomie)} de {select(elements)}"
        elif 12 < t <= 18:
            return f"{nom} {select(action)} {select(nature)}"
        elif 18 < t:
            return f"{nom} {article} {select(outils)}-{select(positif)}"


def roll_d(n: int) -> int:
    return random.randint(1, n)


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
    job_key = traits["job"] if traits['gender'] == MAN and GENDERED in npc_generator.tags[traits["job"].upper()] \
        else apply_gender(traits["job"])
    print(npc_generator.get_characteristics('sw', traits['specie'], job_key))


if __name__ == '__main__':
    main()
