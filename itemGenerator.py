import csv
from random import choice, choices, randrange
from math import log
ITEMS_BASE_PATH = "./item_data"

def RarityProcessor(level: str) -> int:
    if level == "C":
        return 12
    elif level == "U":
        return 8
    elif level == "R":
        return 4
    elif level == "L":
        return 1
    else:
        return -1

def ProcessWordsFile(path: str) -> list[str]:
    valid_words = ["Green", "Red"]
    with open(path) as word_file:
        valid_words = list(word_file.read().split())
    return valid_words

def ProcessWeaponsFile(path: str) -> list[tuple[str, float]]:
    results = []
    with open(path) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(spamreader):
            if i == 0:
                continue

            name = row[0]
            price = float(row[1])
            rarity = RarityProcessor(row[2])
            if rarity == -1:
                print(f"ERROR: Rarity screwed up for \"{row}\"")
            else:
                for a in range(rarity):
                    results.append((name, price))
    return results

DAMAGE_TYPES = [
    "Acid",
    "Bludgeoning",
    "Cold",
    "Fire",
    "Force",
    "Lightning",
    "Necrotic",
    "Piercing",
    "Poison",
    "Psychic",
    "Radiant",
    "Slashing",
    "Thunder"
]
MELEE_ITEMS = ProcessWeaponsFile(ITEMS_BASE_PATH+"/meleeWeapons.csv")
RANDOM_WORDS = ProcessWordsFile(ITEMS_BASE_PATH + '/words.txt')

def RandomDamageType(probabilities: list = None) -> str:
    if probabilities is None:
        return choice(DAMAGE_TYPES)[0]
    else:
        return choices(DAMAGE_TYPES, weights=probabilities)[0]

def CostPrettyPrint(gold_cost: float) -> str:
    gold = int(gold_cost)
    silver_cost = 10 * (gold_cost - gold)
    silver = int(silver_cost)
    copper_cost = 10 * (silver_cost - silver)
    copper = int(copper_cost % 1)
    gold_tag = f"{gold} gp" if gold > 0 else ""
    silver_tag = f"{silver} sp" if silver > 0 else ""
    copper_tag = f"{copper} cp" if copper > 0 else ""

    result = ""
    result += gold_tag
    result += ", " if (silver > 0 or copper > 0) and gold > 0 else ""
    result += silver_tag
    result += ", " if copper > 0 and silver_tag > 0 else ""
    result += copper_tag
    return result

def WeaponScaling(original_cost: float, mod: int) -> float:
    """Converts a weapon's original cost into a new cost based on in being a non-magical +0, +1, +2, +3 weapon.

    Args:
        original_cost (float): The gold cost of the normal weapon.
        mod (int): Integer from -1 to 3, this is the modifier.

    Returns:
        float: _description_
    """
    def scaler(x: float):
        r = 1.09*x - log(x)
        r = (r * 20 / 3) + 234
        r = round(r / 10)
        r = 10 * r
        return r
    
    if mod == -1:
        return 0.5 * original_cost
    elif mod == 0:
        return original_cost
    elif mod == 1:
        return scaler(original_cost)
    elif mod == 2:
        return scaler(original_cost)**1.2 + 5_000
    elif mod == 3:
        return scaler(original_cost)**1.5 + 20_000
    else:
        print("WARNING: Didn't scale item properly.")
        return original_cost

def RandomEnglishWord() -> str:
    return RANDOM_WORDS[randrange(len(RANDOM_WORDS))]

def RandomWeaponName(weapon_type: str) -> str:
    def UsingWeaponType(weapon_type: str) -> str:
        return "The " + weapon_type + " of " + RandomEnglishWord()
    
    def TwoWordsWithOf() -> str:
        return f"{RandomEnglishWord()} {RandomEnglishWord()}"
    
    name_type_prob = [0.5, 0.5]
    name_types = [
        0, 
        1
    ]
    index = choices(name_types, name_type_prob)[0]
    result = ""
    if index == 0:
        result = UsingWeaponType(weapon_type)
    elif index == 1:
        result = TwoWordsWithOf()
    else:
        raise Exception("RandomWeaponName: index doesn't exist")
    
    return result.title()


def GenerateMeleeWeapon():
    """Generates a random Melee weapon and returns the text description and it's shorthand.
    """
    DAMAGE_PROBABILITIES = [1, 0, 5, 5, 1, 1, 1, 0, 5, 1, 5, 0, 1]
    price_modifier = 1.0
    magical = False
    additional_dmg = False
    additional_dmg_type = None
    dice = None

    (weapon_type, base_price) = choice(MELEE_ITEMS)
    name = RandomWeaponName(weapon_type)

    weapon_mod_list = [-1, 0, 1, 2, 3]
    weapon_mod_prob = [7, 40, 45, 6.9, 1.1]
    dmg_mod = choices(weapon_mod_list, weights = weapon_mod_prob)[0]
    base_price = WeaponScaling(base_price, dmg_mod)

    if (dmg_mod == 1 and (randrange(1, 4) == 3)) or dmg_mod >= 2:
        magical = True
        price_modifier += 0.5
        if (randrange(1, 2) == 1):
            additional_dmg = True
            price_modifier += 1.0
            additional_dmg_type = RandomDamageType(DAMAGE_PROBABILITIES)
            num_dice = 1 * dmg_mod

            dice_types = [4, 6, 8, 10, 12]
            dice_rarity = [12, 67, 12, 8, 1]
            dice_costs = [-0.2, 0, 0.75, 1.0, 1.5]
            dice_index = choices([i for i in range(len(dice_types))], weights=dice_rarity)[0]
            dice = f"{num_dice}d{dice_types[dice_index]}"
            price_modifier += dice_costs[dice_index]

    final_price = round(base_price * price_modifier, 2)
    magical_tag = ", magical" if magical else ""
    dmg_mod_tag = f", +{dmg_mod}" if dmg_mod >= 1 else (f", {dmg_mod}" if dmg_mod < 0 else "")

    description = f"\n\tThis {weapon_type} does an additional {dice} {additional_dmg_type} damage." if additional_dmg else ""

    return f"{name}: *{weapon_type}{dmg_mod_tag}{magical_tag}*\n\tCost: {CostPrettyPrint(final_price)}{description}"

if __name__=="__main__":
    print("Item Generator Started")
    for i in range(100000):
        print(f"{GenerateMeleeWeapon()}")
        # print(f"{GenerateMeleeWeapon()}")