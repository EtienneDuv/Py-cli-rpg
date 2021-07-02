import textwrap
import random
import inspect

# ----------------------------------
# CLASSES/CONSTANTS
# ----------------------------------

teams = {'friend': [], 'neutral': [], 'enemy': []}
turn = []


class Character:
    def __init__(self, nickname, health, attack, team, isAlive=True):
        self.nickname = nickname
        self.health = health
        self.attack = attack
        self.team = team
        self.isAlive = isAlive
        teams[self.team].append(self)

    @property
    def nickname(self):
        return self.__nickname

    @nickname.setter
    def nickname(self, nickname):
        self.__nickname = nickname

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, health):
        self.__health = health
        if self.__health <= 0:
            self.dies()

    @property
    def attack(self):
        return self.__attack

    @attack.setter
    def attack(self, attack):
        self.__attack = attack

    @property
    def team(self):
        return self.__team

    @team.setter
    def team(self, team):
        self.__team = team

    @property
    def isAlive(self):
        return self.__isAlive

    @isAlive.setter
    def isAlive(self, isAlive):
        self.__isAlive = isAlive

    def turn(self):
        if self.__team == 'enemy':
            return self.actionAttack(random.choice(teams['friend']))
        else:
            actions = self.getActions()

            # Get only names
            actionsNames = list(actions.keys())
            actionsNames = [name.replace('action', '')
                            for name in actionsNames]

            # Get only methods
            actionsFunctions = list(actions.values())

            string = textwrap.dedent("[Choose an action]")
            for i in range(len(actions)):
                string += f"\n{i+1}. {actionsNames[i]}"

            # not int handling could be nice
            select = int(input(string + '\n'))-1
            print(f'{actionsNames[select]} chosen')
            actionsFunctions[select]()

    def getActions(self):
        actions = {}
        for name, value in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('action'):
                # use value to call directly in turn()
                actions[name] = value
        return actions

    def dies(self):
        self.__isAlive = False
        teams[self.team].pop(teams[self.team].index(self))
        turn.pop(turn.index(self))

    def characterSheet(self):
        return textwrap.dedent(f"""
            === {self.nickname} ({self.__class__.__name__}) ===
            team   : {self.team}
            attack : {self.attack}
            health : {self.health}
            """)

    def selectTarget(self):
        if len(teams['enemy']) == 1:
            return teams['enemy'][0]

    def baseAttack(self, target=None, attackName='ATTACK', damage=None):
        """
        All attack actions pass by here.
        """
        if target is None:
            target = self.selectTarget()
        if damage is None:
            damage = self.attack

        target.health -= damage
        string = textwrap.dedent(
            f"""
            [{attackName}]
            {self.nickname} attacks {target.nickname}.
            Dealt {damage} damages.
            """)
        string += (f'{target.nickname} now has {target.health} hp.'
                   if target.isAlive else f'{target.nickname} is dead.')
        print(string)

    def actionAttack(self, target=None):
        self.baseAttack(target)


class Warrior(Character):
    def __init__(self, nickname,  team='neutral', health=40, attack=2, shield=3):
        super().__init__(nickname, health, attack, team)
        self.shield = shield

    @property
    def shield(self):
        return self.__shield

    @shield.setter
    def shield(self, shield):
        self.__shield = shield

    # TODO use shield value ?
    # @health.setter
    # def health(self, health):
    #     self.__health = health

    def characterSheet(self):
        text = super().characterSheet()
        return text + f"shield   : {self.shield}"

    def actionShieldSlam(self, target=None):
        dmg = self.attack + 2
        self.baseAttack(attackName='SHIELD SLAM', damage=dmg)


class Zombie(Character):
    def __init__(self, nickname='Zombie', health=5, attack=1, hasPower=False, team='enemy'):
        super().__init__(nickname, health, attack, team)
        self.hasPower = hasPower

    @property
    def hasPower(self):
        return "Able to resurrect" if self.__hasPower else "Unable to resurrect"

    @hasPower.setter
    def hasPower(self, hasPower):
        self.__hasPower = hasPower


class Skeleton(Character):
    def __init__(self, nickname='Skeleton', health=5, attack=2, team='enemy'):
        super().__init__(nickname, health, attack, team)


# ----------------------------------
# FUNCTIONS
# ----------------------------------

def New_Player():
    # New_class = input("Which class would you choose ? (warrior) : ")
    # New_nickname = input("Type your nickname : ")

    # if New_class == "warrior":
    #     return Warrior(New_nickname, 40, 2, 3, 'friend')
    # else:
    #     return New_Player()
    return Warrior('New_nickname', 'friend')


def Generate_enemies(enemies):
    for enemy, number in enemies.items():
        for i in range(number):
            if enemy == 'zombie':
                Zombie(nickname=f'{enemy}{i+1}', attack=10)
            elif enemy == 'skeleton':
                Skeleton(nickname=f'{enemy}{i+1}')


def Generate_turn_order():
    def Select_from(list):
        select = random.choice(list)
        turn.append(select)
        list.pop(list.index(select))

    # Permet de perdre la reference a la liste teams (=/= deep copy)
    friends = [el for el in teams['friend']]
    enemies = [el for el in teams['enemy']]

    i = -1
    while len(friends) > 0 or len(enemies) > 0:
        i += 1
        if (i % 2 == 0) and (len(friends) > 0):
            Select_from(friends)
        if (i % 2 == 1) and (len(enemies) > 0):
            Select_from(enemies)


# ----------------------------------
# PROGRAM
# ----------------------------------

levels = {
    1: {'zombie': 1},
    2: {'zombie': 2, 'skeleton': 1}
}

player1 = New_Player()
# print(player1.characterSheet())

# Loop on levels
levelIndex = 0
for level, enemies in levels.items():
    levelIndex += 1
    Generate_enemies(enemies)
    Generate_turn_order()

    i = -1
    while len(teams['friend']) > 0 and len(teams['enemy']) > 0:
        print()
        i += 1
        playingCharacter = turn[i % len(turn)]
        playingCharacter.turn()

    print(f'\n[LEVEL {levelIndex} FINISHED]')

# print(teams)
