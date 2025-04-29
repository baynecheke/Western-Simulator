import random
import time
import json
import os

class Player:
    def __init__(self):
        self.Day = 1
        self.Time = 9
        self.Speed = 3
        self.watch = True
        self.Role = ["None"]
        self.Hunger = 0
        self.Health = 100
        self.itemsinventory = {}
        self.gold = 50  # Starting gold
        self.distancenext = 0
        self.travelspeed = 3
        self.EmptyTown = False
        self.Speed = 31
        self.Hostility = 0
        self.invillage = True
        self.TemporaryAttackBoost = 0
        self.MaxHealth = 100
        self.Armor_Boost = 1
        self.travel_bonus = 0
        self.trade_bonus = 0
        self.score = 0
        self.specific_enemy = "None"
        self.specific_enemy_true = False
        self.herder_bonus = 0
        self.poisoned = 0
        self.BasePossibleActions = [
            "(A) Enter the Townhall", 
            "(B) Enter the Doctor's office", 
            "(C) Enter the General Store", 
            "(D) Enter the Gunsmith's Shop", 
            "(E) Enter the Hotel", 
            "(F) Enter the Saloon", 
            "(G) Talk with the Townspeople",
            "(H) Enter the Trading Post",
            "(I) Enter the Blacksmith Shop",
            "(J) Leave the town",
            "(K) Use an item",
            "(L) Take an inventory check",
            "(M) Continue down the road"
        ]
        self.possibleactions = self.BasePossibleActions[:-1]  # Exclude "(J) Continue..."

        self.TownNames1 = ["Gray", "Dust", "Buffalo", "Coyote", "Gold", "Post", "North"]
        self.TownNames2 = ["Town", "Ridge", "Camp", "Fort", "Settlement"]
        self.available_roles = {
            "traveler": Role("traveler"),
            "herder": Role("herder"),
            "trader": Role("trader")
        }
        self.active_role = None

    @classmethod
    def load_game(cls):
        print("\n--- Load Game ---")
        save_folder = 'saves'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        save_files = [f for f in os.listdir(save_folder) if f.endswith('.json')]
        if not save_files:
            print("No save files found. Starting a new game.")
            return cls()

        # Display saves by number
        for idx, filename in enumerate(save_files, start=1):
            print(f"{idx}. {filename.replace('save_', '').replace('.json', '')}")

        slot_choice = input("Enter the number of the save slot you want to load: ").strip()

        if not slot_choice.isdigit() or not (1 <= int(slot_choice) <= len(save_files)):
            print("Invalid choice. Starting a new game.")
            return cls()

        save_file = save_files[int(slot_choice) - 1]
        filepath = os.path.join(save_folder, save_file)
        with open(filepath, 'r') as f:
            save_data = json.load(f)

        player = cls()

        # Restore saved data
        player.gold = save_data.get("gold", 0)
        player.itemsinventory = save_data.get("itemsinventory", {})
        player.distancenext = save_data.get("distancenext", 0)
        player.Day = save_data.get("Day", 1)
        player.Time = save_data.get("Time", 9)
        player.Health = save_data.get("Health", 100)
        player.Hunger = save_data.get("Hunger", 0)
        player.Hostility = save_data.get("Hostility", 0)
        player.score = save_data.get("score", 0)
        player.invillage = save_data.get("invillage", True)
        player.travel_bonus = save_data.get("travel_bonus", 0)
        player.trade_bonus = save_data.get("trade_bonus", 0)

        role_name = save_data.get("active_role")
        if role_name and role_name in player.available_roles:
            player.active_role = player.available_roles[role_name]
            player.active_role.xp = save_data.get("role_xp", 0)

        print(f"Game loaded from {save_file} successfully!")
        # Update possible actions based on whether the player is in a village
        if player.invillage:
            player.possibleactions = player.BasePossibleActions[:-1] # all except explore
        else:
            player.possibleactions = player.BasePossibleActions[-3:] # inventory check & explore
        return player

    def save_game(self):
        save_name = input("Enter a name for your save file: ").strip().replace(" ", "_")
        save_folder = 'saves'
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_path = os.path.join(save_folder, f"save_{save_name}.json")
        with open(save_path, "w") as file:
            json.dump({
                "gold": self.gold,
                "itemsinventory": self.itemsinventory,
                "distancenext": self.distancenext,
                "Day": self.Day,
                "Time": self.Time,
                "Health": self.Health,
                "Hunger": self.Hunger,
                "Hostility": self.Hostility,
                "score": self.score,
                "invillage": self.invillage,
                "travel_bonus": self.travel_bonus,
                "trade_bonus": self.trade_bonus,
                "active_role": self.active_role.name if self.active_role else None,
                "role_xp": self.active_role.xp if self.active_role else 0,
            }, file)
        print(f"Game saved successfully to 'save_{save_name}.json'.")

    def choose_role(self, choice):
        choice = choice.strip().upper()

        role_map = {
            "A": "herder",
            "B": "traveler",
            "C": "trader"
        }

        role_key = role_map.get(choice, "traveler")  # default to "traveler"

        if role_key not in self.available_roles:
            print(f"'{role_key}' is not a valid role.")
            return

        if self.active_role and self.active_role.name != role_key:
            print(f"Switching from {self.active_role.name.capitalize()} to {role_key.capitalize()}...")
            self.active_role.xp = 0

        self.active_role = self.available_roles[role_key]
        print(f"You are now a {self.active_role.name.capitalize()}. XP reset to 0.")

    def role_progress(self, amount):
        if self.active_role:
            self.active_role.gain_xp(self, amount)
        else:
            print("No role selected.")

    def lose_random_item(self, amount):
        if not self.itemsinventory:
            print("You have no items to lose.")
            return

        item = random.choice(list(self.itemsinventory.keys()))
        self.itemsinventory[item] -= amount
        if self.itemsinventory[item] <= 0:
            del self.itemsinventory[item]
        print(f"You lost 1 {item} from your inventory.")

    def add_item(self, item_name):
        self.itemsinventory[item_name] = self.itemsinventory.get(item_name, 0) + 1
        print(f"You found a {item_name}!")

    def loot_drop(self, item):
        loot = item
        self.add_item(loot)

    def Number(self, Choice):
        mapping = {
            "A": 0, "B": 1, "C": 2, "D": 3, "E": 4,
            "F": 5, "G": 6, "H": 7, "I": 8, "J": 9, 
            "K": 10, "L": 11, "M": 12, "N": 13
        }
        return mapping.get(Choice.upper(), -1)

    def TakeActionsChose(self):
        print("You may choose an action to take:")
        for action in self.possibleactions:
            print(action)

        # Extract the valid letter keys from each action, e.g., "(A) Enter the Townhall" -> "A"
        valid_choices = [action.strip()[1].upper() for action in self.possibleactions]

        while True:
            choice = input("Choice: ").strip().upper()
            if choice in valid_choices:
                return self.Number(choice)
            else:
                print("Invalid or unavailable choice. Try again.")

    def ActionFunction(self, index):
        actions = [
            self.TownHall, self.DoctorOffice, self.GeneralStore, self.Gunsmiths,
            self.Hotel, self.Saloon, self.Townspeople, self.TradingPost, self.Blacksmith, self.LeaveTown, self.use_item1, self.Statcheck,
            self.Explore
        ]
        if 0 <= index < len(actions):
            actions[index]()
        else:
            print("That action is not currently available.")

    def DoAction(self):
        index = self.TakeActionsChose()
        self.ActionFunction(index)
    
    def use_item1(self):
        self.use_item(combat=False, enemy_name=None, enemy_combatant=None)

    def use_item(self, combat, enemy_name, enemy_combatant):
        if not self.itemsinventory:
            print("Your inventory is empty.")
            return
        use_continue = True
        while use_continue == True:
            print("\nYour Inventory:")
            item_descriptions = {
            "bread": "Restores 10 health or reduces 1 hunger.",
            "antivenom": "Cures poison if poisoned.",
            "lantern": "Gives you 1 extra hour of time.",
            "boots": "Increases travel speed by 1.",
            "leather armor": "Reduces combat damage taken (90%).",
            "chain mail": "Greatly reduces combat damage taken (80%).",
            "lasso": "Halves the health of animal-type enemies.",
            "fire cracker": "Halves health of pack-type enemies and stuns them.",
            "rope": "Could be used during events.",
            # Add more if needed
        }

            for idx, (item, qty) in enumerate(self.itemsinventory.items(), 1):
                description = item_descriptions.get(item, "This item can't be used.")
                print(f"{idx}. {item.capitalize()} (x{qty}) - {description}")

            choice = input("Enter the number of the item you want to use (or 'q to leave'): ").strip().lower()

            if choice == "q":
                print("You decided not to use anything.")
                use_continue = False
                break

            item_list = list(self.itemsinventory.keys())

            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(item_list):
                print("Invalid choice.")
                continue

            selected_item = item_list[int(choice) - 1]
            if combat == False:
                if selected_item == "bread":
                    self.Hunger = self.Hunger - 1
                    self.itemsinventory[selected_item] -= 1
                    if self.itemsinventory[selected_item] <= 0:
                        del self.itemsinventory[selected_item]
                    print(f"You eat some bread and reduce {1} hunger.")
                elif selected_item == "antivenom":
                    self.Hunger = self.Hunger - 1
                    if self.poisoned > 0:
                        print(f"You use the antivenom.")
                        self.itemsinventory[selected_item] -= 1
                        if self.itemsinventory[selected_item] <= 0:
                            del self.itemsinventory[selected_item]
                        self.poisoned -=1
                        if self.poisoned > 0:
                            print(f"Your poison level has decreased to {self.poisoned}.")
                        else:
                            print(f"You are no longer poisoned.")
                    else:
                        print("You are not poisoned, and cannot use this.")

                elif selected_item == "lantern":
                    print("You decide to use your lantern, and it allows you an extra hour to work with.")
                    self.Time = self.Time - 2
                    self.itemsinventory[selected_item] -= 1
                    if self.itemsinventory[selected_item] <= 0:
                        del self.itemsinventory[selected_item]
                elif selected_item == "boots":
                    print("You out on you boots, you feel faster.")
                    self.Speed += 1
                    self.itemsinventory[selected_item] -= 1
                    if self.itemsinventory[selected_item] <= 0:
                        del self.itemsinventory[selected_item]
                else:
                    print(f"You can't use {selected_item} right now.")
    
            else:
                if selected_item == "bread":
                    heal_amount = 10
                    self.Health = min(self.Health + heal_amount, 100)
                    print(f"You eat some bread and restore {heal_amount} health.")
                    self.itemsinventory[selected_item] -= 1
                    if self.itemsinventory[selected_item] <= 0:
                        del self.itemsinventory[selected_item]

                elif selected_item == "lasso":
                    if combat and enemy_combatant and enemy_combatant.get("type") == "animal":
                        enemy_health_before = enemy_combatant["health"]
                        enemy_combatant["health"] //= 2
                        print(f"You used the lasso! The {enemy_name}'s health is halved from {enemy_health_before} to {enemy_combatant['health']}.")
                        self.itemsinventory[selected_item] -= 1
                        if self.itemsinventory[selected_item] <= 0:
                            del self.itemsinventory[selected_item]
                    else:
                        print("The lasso has no effect on this enemy.")
                elif selected_item == "fire cracker":
                    if combat and enemy_combatant and enemy_combatant.get("type") == "pack":
                        enemy_health_before = enemy_combatant["health"]
                        enemy_combatant["damage"] = (enemy_combatant["damage"])/2
                        enemy_combatant["health"] //= 2
                        print(f"You used the fire cracker! The {enemy_name}'s health is halved from {enemy_health_before} to {enemy_combatant['health']}.")
                        print(f"They are much more disorganized.")
                        time.sleep(2,)
                        self.itemsinventory[selected_item] -= 1
                        if self.itemsinventory[selected_item] <= 0:
                            del self.itemsinventory[selected_item]
                    else:
                        print("The fire cracker has no effect on this enemy.")
                elif selected_item == "leather armor":
                    print("Your durability has increased.")
                    self.Armor_Boost = 0.9
                elif selected_item == "chain mail":
                    print("Your durability has increased significantly.")
                    self.Armor_Boost = 0.8
                else:
                    print(f"You can't use {selected_item} right now.")
                    time.sleep(2,)

    def Statcheck(self):
        print(f"You are on day {self.Day}.")
        if self.watch:
            print(f"It is {self.Time}:00 o'clock.")
        else:
            print("It is morning." if self.Time < 13 else "It is afternoon.")
        print(f"You have {self.gold} gold in your pouch.")
        print("Your inventory contains:")
        if self.itemsinventory:
            for item, count in self.itemsinventory.items():
                print(f" - {item}: {count}")
        else:
            print(" - (empty)")
        print(f"Your role is {self.active_role.name.capitalize()} (XP: {self.active_role.xp}).")
        print(f"Your hunger is {self.Hunger}.")
        print(f"Your health is {self.Health}.")
        time.sleep(5,)

    def TownHall(self):
        while True:
            print("\n--- Town Hall ---")
            print("1. Switch current role")
            print("2. View available roles")
            print("3. Buy a new role")
            print("4. Leave Town Hall")

            choice = input("Choose an action: ").strip()

            if choice == "1":
                print("Available Roles:")
                for key, role in self.available_roles.items():
                    print(f" - {role.name.capitalize()} (XP: {role.xp})")

                selection = input("Enter role name to switch to: ").lower()
                self.choose_role(selection)

            elif choice == "2":
                print("Your available roles:")
                for role in self.available_roles.values():
                    print(f"{role.name.capitalize()} (XP: {role.xp})")

            elif choice == "3":
                print("\n--- Unlockable Roles ---")
                unlockable_roles = {
                    "scout": {"gold_cost": 40, "xp_required": 25},
                    "hunter": {"gold_cost": 60, "xp_required": 40},
                    "merchant": {"gold_cost": 50, "xp_required": 30}
                }

                # Filter out already unlocked roles
                owned = [r.name for r in self.available_roles.values()]
                for name, data in unlockable_roles.items():
                    if name in owned:
                        continue
                    print(f"{name.capitalize()} - Cost: {data['gold_cost']}g or XP: {data['xp_required']}")

                to_buy = input("Enter the role you want to buy (or 'q' to cancel): ").lower()
                if to_buy == "q":
                    continue

                if to_buy in unlockable_roles and to_buy not in owned:
                    data = unlockable_roles[to_buy]
                    can_afford = self.gold >= data['gold_cost']
                    current_xp = self.active_role.xp if self.active_role else 0
                    has_xp = current_xp >= data['xp_required']

                    if can_afford:
                        self.gold -= data['gold_cost']
                        self.available_roles[to_buy] = Role(to_buy)
                        print(f"You purchased the {to_buy.capitalize()} role with gold!")
                    elif has_xp:
                        self.available_roles[to_buy] = Role(to_buy)
                        print(f"You unlocked the {to_buy.capitalize()} role with experience!")
                    else:
                        print("You don't have enough gold or XP to unlock this role.")
                else:
                    print("Invalid choice or you already own that role.")

            elif choice == "4":
                print("You leave the town hall.")
                break

            else:
                print("Invalid selection.")

    def TradingPost(self):
        if not self.itemsinventory:
            print("You don't have any items to sell.")
            return
        # Set item prices (could also be a class-level constant or loaded elsewhere)
        prices = {
            "small hide": 5,
            "medium hide": 10,
            "large hide": 25,
            "small meat": 5,
            "medium meat": 10,
            "large meat": 20,
            "horn": 30,
            "bread": 2,
            "knife": 5,
            "colt pistol": 20,
            "rifle": 15,
            "shotgun": 25,
            "pistol_ammo": 1,
            "rifle_ammo": 2,
            "shotgun_ammo": 3,
            "lasso": 5}
        while True:
            print("\n--- Trading Post ---")
            print("Your Inventory:")
            for idx, (item, qty) in enumerate(self.itemsinventory.items(), 1):
                price = prices.get(item, 1)
                print(f"{idx}. {item} (x{qty}) - Sell Price: ${price}")

            print(f"{len(self.itemsinventory) + 1}. Exit Trading Post")

            choice = input("Enter the number of the item you want to sell: ").strip()

            if not choice.isdigit():
                print("Invalid input.")
                continue

            choice = int(choice)

            if choice == len(self.itemsinventory) + 1:
                print("Leaving the trading post.")
                break

            if 1 <= choice <= len(self.itemsinventory):
                item_to_sell = list(self.itemsinventory.keys())[choice - 1]
                price = prices.get(item_to_sell, 1)
                price = price + self.trade_bonus
                self.gold += price
                self.itemsinventory[item_to_sell] -= 1
                print(f"You sold 1 {item_to_sell} for ${price}.")
                print(f"Current gold: ${self.gold}")

                if self.itemsinventory[item_to_sell] <= 0:
                    del self.itemsinventory[item_to_sell]
            else:
                print("Invalid choice.")

    def Blacksmith(self):
        shop =  BlacksmithShop(self)
        shop.run_shop()

    def DoctorOffice(self):
        print("You enter the doctor's office. The doctor greets you with a friendly smile.")
        print("The doctor takes your physical.")
        if self.Health == 100:
            print(f"'You are in great health!' the doctor exclaims.")
            print(f"'You health is {self.Health}.")
        elif self.Health >= 75:
            print(f"'You are in good health.' the doctor announces.")
            print(f"'You health is {self.Health}.")
        elif self.Health >= 50:
            print(f"'You are slightly injured.' the doctor says.")
            print(f"'You health is {self.Health}.")
        elif self.Health >= 25:
            print(f"'You are very injured.' the doctor worries.")
            print(f"'You health is {self.Health}.")
        elif self.Health > 0:
            print(f"'You are extremely injured and need immediate medical attention.' the doctor worries.")
            print(f"'You health is {self.Health}.")
        Heal = 100 - self.Health
        cost = (Heal)/2
        if cost > 75:
            cost = 75
        cost = round(cost)
        print("'Would you like me to heal you?' Yes/No")
        print(f"It will cost you {cost}.")
        Choice = input(": ")
        if Choice == "Yes":
            if self.gold >= cost:
                self.gold -= cost
                print(f"You were healed {Heal}")
                self.Health = 100
            else:
                print("You do not have enough gold.")
        else:
            print("You leave the Doctor's Office.")

    def Gunsmiths(self):
        print("The gunsmith greets you with a nod. Guns line the walls.")
        gunsmith = GunsmithStore(self)
        gunsmith.run_shop()

    def Hotel(self):
        print("You walk into the hotel. The air smells of leather and dust.")

    def Saloon(self):
        print("The saloon is alive with music and conversation.")

    def Townspeople(self):
        print(f"You chat with a few townsfolk.")
        Random = random.randint(1,100)
        if Random < 51:
            print(f"One of them offers you a job.")
            print(f"Will you work? Yes/No")
            Choice = input(": ").strip().capitalize()
            if Choice == "Yes":
                gold = random.randint(5,15)
                self.gold += gold
                print(f"You work for a while and earn {gold}.")
            else:
                print("You turn him down kindly.")
                return
        elif Random >= 51:
            print("One of them teaches you some new tricks that benefit your role!")
            self.role_progress(1)
            time.sleep(2,)

    def LeaveTown(self):
        self.distancenext = random.randint(10, 20)
        print("You leave the town and head down the road.")
        self.invillage = False
        self.Hostility = 0
        self.possibleactions = self.BasePossibleActions[-3:]  # Show H and J only

    def Interaction(self):
        Random = random.randint(1,25)
        if Random <= 10:
            print("You find some gold on the path!")
            self.gold += 5
        elif Random <= 15:
            combat = Combat(self)
            combat.FindAttacker()
            combat.Attack()
        else:
            self.PossibleQuest()

    def Explore(self):
        print("You travel down the road...")
        time.sleep(3,)
        travel = self.travelspeed + self.travel_bonus
        if self.distancenext <= travel:
            self.ArriveTown()
        else:
            self.distancenext -= travel
            Random = random.randint(1,3)
            if Random == 2 or 3:
                self.Interaction()

    def ArriveTown(self):
        name = f"{random.choice(self.TownNames1)} {random.choice(self.TownNames2)}"
        print(f"You arrive in the town of {name}!")
        time.sleep(2)
        if self.EmptyTown:
            print("But the streets are empty... eerily quiet.")
        else:
            self.gold += 20
            self.invillage = True
            self.possibleactions = self.BasePossibleActions[:-1]
            self.score = self.score + 5
            
    def GeneralStore(self):
        print("You walk into the general store. A friendly shopkeeper greets you.")
        store = Store(self)  # Pass player to store
        store.run_shop()

    def HostilityFunc(self):
        if self.Hostility < 1:
            print("The people pass by your wagon happily.")
            time.sleep(1,)
        if self.Hostility == 1:
            print("The people are suspicious that you were unharmed during the attack.")
            if self.gold >= 3:
                print("It appears that someone snuck a couple gold coins from your purse.")
                self.gold = self.gold - 3
            else:
                return
        if self.Hostility == 2:
            print("The people are sure you have some correlation with the bandits.")
            print("A burly fellow shoves you into a water trough.")
            self.Health = self.Health - 25
            time.sleep(3,)

    def RunDay(self):
        print("You step out of your wagon and stretch.")
        time.sleep(2,)
        while self.Time < 21:
            self.DoAction()
            self.Time += 1
            if self.Health <= 0:
                break
        time.sleep(1)
        if self.Health <= 0:
            print("You died.")
            return
        if self.invillage == True:
            print("Night falls over the town.")
            Day = self.Day
            Day = 5 - Day
            if Day == 0:
                Day = 1
            if random.randint(1, Day) == 1:
                print("Gunshots ring out in the night! The town was attacked!")
                print("You role out of bed, but the bandits have already left.")
                time.sleep(2,)
                print("You return to you wagon, concerned at what the next day will bring.")
                self.Hostility += 1
            else:
                print("You sleep peacefully in your wagon.")
        else:
            print("You make camp under the stars.")
            print("You sleep through the night")
            time.sleep(3,)
        self.Time = 9

    def PossibleQuest(self):
        Random = random.randint(1,50)
        if Random <= 10:
            print(f"You notice an abandoned wagon a little ways off the trail.")
            print(f"You could either search the wagon or leave and save time.")
            time.sleep(3,)
            print(f"1, search it.")
            print(f"2, leave it.")
            Choice = input(f": ")
            if Choice == "1":
                print(f"You take the time to search the wagon.")
                Random1 = random.randint(1,2)
                if Random1 == 1:
                    print(f"As you rummage through the bags and boxes you uncover a rattle snake.")
                    if rope in self.itemsinventory:
                        print("You use your rope to whack the snakes head away, and it flees through the grass.")
                        selected_item = 'rope'
                        self.itemsinventory[selected_item] -= 1
                        if self.itemsinventory[selected_item] <= 0:
                            del self.itemsinventory[selected_item]
                    if self.Speed >= 5:
                        print(f"You dodge the snakes attack, then strangle it")
            else:
                print(f"You leave the wagon alone and proceed down the trail.")
        elif Random <= 25:
            print("A dry river bed lies in your path.")
            time.sleep(1,)
            print("A storm is brewing in the West, and this location could flood easily.")
            print("You could either cross here, and risk the storm, or travel around.")
            time.sleep(2,)
            print("(1) cross, (2) travel around.")
            time.sleep(2,)
            Choice = input(": ").strip()
            if Choice == "1":
                print("You take the chance and cross the river bank.")
                Random = random.randint(1,10)
                if Random < 8:
                    print("You cross safely, and the rain starts only after you get across.")
                else:
                    print("The torrent of water that appears carries you and your wagon down stream.")
                    time.sleep(3,)
                    print("After the water, you realize that one of your items is missing.")
                    self.lose_random_item(1)
                    time.sleep(3,)
                    print("You get back on the trail, but a lot of time has been wasted.")
                    self.Time += 2
            else:
                print("You travel around the creek, but are glad you didn't take the risk")
                self.Time += 1
        elif Random <= 35:
            print("You spend some extra time working on your skills.")
            self.role_progress(1)
            time.sleep(3,)
        elif Random <= 45:
            print("You found a hidden supply of food!")
            for i in range(3):
                self.loot_drop("bread")
            time.sleep(3,)
        elif Random <= 50:
            print("You found a rare item!")
            self.loot_drop("winchester rifle")
            time.sleep(3,)


class Combat:
    def __init__(self, player):
        self.player = player

        if self.player.Day == 1:
            self.enemies = ["viper", "rattlesnake", "cobra", "wolf", "bison"] 
        elif self.player.Day == 2:
            self.enemies = ["pack of wolves", "cobra", "wolf", "bison"] 
        elif self.player.Day >= 4 and self.player.Day <= 6:
            self.enemies = ["bear", "pack of wolves", "wolf", "bison"] 
        else:
            self.enemies = ["bandit", "bear", "pack of wolves", "mounted bandit", "bison"] 

        self.Enemy = random.choice(self.enemies)
        self.EnemyCombatant = None
        self.Enemies = {
            "rattlesnake": {"health": 20, "damage": 7, "speed": 3, "loot": "small","type": "animal", "special": "venomous"}, 
            "viper": {"health": 10, "damage": 5, "speed": 5, "loot": "small", "type": "animal",},
            "cobra": {"health": 15, "damage": 10, "speed": 2, "loot": "small",  "type": "animal",},
            "wolf": {"health": 50, "damage": 15, "speed": 4, "loot": "medium", "type": "animal",},  
            "bison": {"health": 150, "damage": 25, "speed": 2, "loot": "large", "passive": True,  "type": "animal"},
            "pack of wolves": {"health": 100, "damage": 25, "speed": 3, "loot": "medium", "type": "pack"},
            "bear": {"health": 200, "damage": 40, "speed": 2, "loot": "medium",  "type": "animal"},
            "bandit": {"health": 100, "damage": 15, "speed": 4, "loot": "bandit",  "type": "animal"},
            "mounted bandit": {"health": 120, "damage": 15, "speed": 7, "loot": "bandit",  "type": "animal"},
            }
        self.loots = {
            "small": ["small hide", "small meat"],
            "medium": ["medium hide", "medium meat"],
            "large": ["large hide", "large meat", "horn"],
            "bandit": ["revolver", "pistol_ammo", "bread"]
        }

    def FindAttacker(self):
        if self.Enemy.lower() in self.Enemies:
            self.EnemyCombatant = self.Enemies[self.Enemy.lower()]
            print(f"Along the path, you spot a {self.Enemy}.")

        else:
            print("No known enemies found here.")

    def Attack(self):
        combat = True
        if not self.EnemyCombatant:
            print("There is no enemy to fight.")
            return
        speed_modifier = 0
        enemy_damage = self.EnemyCombatant["damage"]
        enemy_speed = self.EnemyCombatant["speed"]
        enemy_loot = self.EnemyCombatant["loot"]
        print(f"\nYou face off against a {self.Enemy.capitalize()}!")
        print(f"Enemy stats — Health: {self.EnemyCombatant['health']}, Damage: {enemy_damage}, Speed: {enemy_speed}")
        if self.EnemyCombatant.get("passive") == True:
            print(f"The {self.Enemy} appears to be passive.")
            print("You have the option to leave it alone, will you? Yes/No")
            Choice = input(": ")
            if Choice.lower() == "yes":
                print(f"You slowly back away from the {self.Enemy}.")
                return
            else:
                print(f"You boldly approach the {self.Enemy}.")
        Choice = input("Would you like to use an item or a weapons ability before the combat? Yes/No:")
        if Choice == "Yes":
            self.player.use_item(combat=True, enemy_name=self.Enemy, enemy_combatant=self.EnemyCombatant)
        if self.player.Speed > self.EnemyCombatant["speed"]:
            TurnOrder = ["player", "enemy"]
        elif self.player.Speed < self.EnemyCombatant["speed"]:
            TurnOrder = ["enemy", "player"]
        else:
            TurnOrder = random.choice([["player", "enemy"], ["enemy", "player"]])
                
                
        while self.EnemyCombatant["health"] > 0 and self.player.Health > 0:
            #if player_speed > enemy_speed:
            for turn in TurnOrder:
                if turn == "player":
                    print("\n--- Your Turn ---")
                    print("What will you do?")
                    print("1. Attack")
                    print("2. Use Item")
                    print("3. Try to Retreat")

                    choice = input("Choose an action: ").strip()

                    if choice == "1":
                        # Get list of owned weapons (weapons with known names)
                        weapon_choices = {
                            'revolver': (10, 15),
                            'rifle': (20, 25),
                            'shotgun': (25,35),
                            'colt pistol': (15,20),
                            'knife': (5, 10),
                            'bowie knife': (10, 15),
                            'winchester rifle': (35, 45)
                        }
                        ammo_needed = {
                            'revolver': 'pistol_ammo',
                            'colt pistol': 'pistol_ammo',
                            'rifle': 'rifle_ammo',
                            'shotgun': 'shotgun_ammo',
                            'winchester rifle': 'rifle_ammo'
                        }

                        owned_weapons = [w for w in weapon_choices if w in self.player.itemsinventory]
                        if not owned_weapons:
                            print("You don't have any weapons, so you fight with your fists!")
                            player_attack = random.randint(2, 5)
                        else:
                            while True:
                                print("Choose a weapon:")
                                for i, weapon in enumerate(owned_weapons, start=1):
                                    dmg = weapon_choices[weapon]
                                    ammo_info = ""
                                    if weapon in ammo_needed:
                                        ammo_type = ammo_needed[weapon]
                                        ammo_count = self.player.itemsinventory.get(ammo_type, 0)
                                        ammo_info = f" | Ammo: {ammo_count}"
                                    print(f"{i}. {weapon.capitalize()} (Damage: {dmg}){ammo_info}")
                                print(f"{len(owned_weapons) + 1}. Fists (No weapon)")

                                try:
                                    weapon_choice = int(input("Choice: "))
                                    if weapon_choice == len(owned_weapons) + 1:
                                        player_attack = random.randint(2, 5)
                                        print("You swing your fists!")
                                        break
                                    elif 1 <= weapon_choice <= len(owned_weapons):
                                        weapon = owned_weapons[weapon_choice - 1]
                                        if weapon in ammo_needed:
                                            ammo_type = ammo_needed[weapon]
                                            if self.player.itemsinventory.get(ammo_type, 0) < 1:
                                                print(f"You're out of {ammo_type}! Choose another weapon.")
                                                continue
                                            else:
                                                self.player.itemsinventory[ammo_type] -= 1
                                                print(f"You fire the {weapon}. Ammo left: {self.player.itemsinventory[ammo_type]}")
                                        dmg_range = weapon_choices[weapon]
                                        player_attack = random.randint(*dmg_range)
                                        break
                                    else:
                                        print("Invalid selection.")
                                except ValueError:
                                    print("Please enter a valid number.")
                        self.EnemyCombatant["health"] -= player_attack
                        print(f"You hit the {self.Enemy} for {player_attack} damage!")
                    elif choice == "2":
                        self.player.use_item(combat=True, enemy_name=self.Enemy, enemy_combatant=self.EnemyCombatant)


                    elif choice == "3":
                        if enemy_speed < self.player.Speed + speed_modifier:
                            print("You manage to escape!")
                            self.player.Health = round(self.player.Health)
                            self.player.Armor_Boost = 1
                            return
                        else:
                            speed_modifier += 1
                            print("You failed to escape!")
                            self.player.Health = self.player.Health - (enemy_damage)/2

                    else:
                        print("Invalid choice.")
                        continue
                if self.EnemyCombatant["health"] <= 0:
                    print(f"{self.Enemy.capitalize()} is dead.")
                    loot_item = random.choice(self.loots[enemy_loot])
                    self.player.loot_drop(loot_item)
                    if "ammo" in "loot_item":
                        self.player.itemsinventory[loot_item] = self.player.itemsinventory.get(loot_item, 0) + 3
                        print(f"You gained 3 x {loot_item}s!")
                    self.player.score = self.player.score + 5
                    self.player.Health = round(self.player.Health)
                    self.player.Armor_Boost = 1
                    time.sleep(2,)
                    return
            # Enemy's turn
            else:

                print(f"\n--- {self.Enemy.capitalize()}'s Turn ---")
                Nenemy_damage = enemy_damage*self.player.Armor_Boost
                self.player.Health -= Nenemy_damage
                print(f"The {self.Enemy} strikes you for {Nenemy_damage} damage!")
                print(f"Your health: {self.player.Health}")
                print(f"Enemy health: {self.EnemyCombatant["health"]}")
                if self.EnemyCombatant.get("special") == "venomous":
                    self.player.poisoned = 1
                if self.player.Health <= 0:
                    return

class Store:
    def __init__(self, player):
        self.player = player
        self.inventory = {
            1: {'name': 'lantern', 'price': 10, 'quantity': 10},
            2: {'name': 'bread', 'price': 5, 'quantity': 30},
            3: {'name': 'rope', 'price': 5, 'quantity': 20},
            4: {'name': 'lasso', 'price': 10, 'quantity': 10},
            5: {'name': 'fire cracker', 'price': 10, 'quantity': 10},
            6: {'name': 'antivenom', 'price': 15, 'quantity': 10},
        }

    def show_inventory(self):
        print("\n--- Store Inventory ---")
        for item_id, details in self.inventory.items():
            print(f"{item_id}. {details['name'].capitalize()} - ${details['price']} | Stock: {details['quantity']}")
        print(f"\nYour Gold: ${self.player.gold:.2f}")

    def show_player_inventory(self):
        print("\nYour Inventory:")
        if not self.player.itemsinventory:
            print(" - (empty)")
        else:
            for item, quantity in self.player.itemsinventory.items():
                print(f" - {item.capitalize()}: {quantity}")

    def buy_item(self, item_id):
        if item_id not in self.inventory:
            print("Invalid item ID.")
            return

        item = self.inventory[item_id]
        total_price = item['price']

        if item['quantity'] < 1:
            print(f"{item['name'].capitalize()} is out of stock.")
        elif self.player.gold < total_price:
            print("You don't have enough gold.")
        else:
            item['quantity'] -= 1
            self.player.gold -= total_price
            self.player.itemsinventory[item['name']] = self.player.itemsinventory.get(item['name'], 0) + 1
            print(f"You bought 1 {item['name']} for ${total_price:.2f}.")

    def run_shop(self):
        print("Welcome to the General Store!")
        while True:
            self.show_inventory()
            self.show_player_inventory()

            choice = input("\nEnter the item number to buy (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                print("Thanks for visiting! Come again.")
                break

            if not choice.isdigit():
                print("Please enter a valid number.")
                continue

            item_id = int(choice)
            self.buy_item(item_id)

class BlacksmithShop:
    def __init__(self, player):
        self.player = player
        self.inventory = {
            1: {'name': 'leather armor', 'price': 35, 'quantity': 3},
            2: {'name': 'chain mail', 'price': 75, 'quantity': 2},
            3: {'name': 'boots', 'price': 15, 'quantity': 5}
        }

    def show_inventory(self):
        print("\n--- Store Inventory ---")
        for item_id, details in self.inventory.items():
            print(f"{item_id}. {details['name'].capitalize()} - ${details['price']} | Stock: {details['quantity']}")
        print(f"\nYour Gold: ${self.player.gold:.2f}")

    def show_player_inventory(self):
        print("\nYour Inventory:")
        if not self.player.itemsinventory:
            print(" - (empty)")
        else:
            for item, quantity in self.player.itemsinventory.items():
                print(f" - {item.capitalize()}: {quantity}")

    def buy_item(self, item_id):
        if item_id not in self.inventory:
            print("Invalid item ID.")
            return

        item = self.inventory[item_id]
        total_price = item['price']

        if item['quantity'] < 1:
            print(f"{item['name'].capitalize()} is out of stock.")
        elif self.player.gold < total_price:
            print("You don't have enough gold.")
        else:
            item['quantity'] -= 1
            self.player.gold -= total_price
            self.player.itemsinventory[item['name']] = self.player.itemsinventory.get(item['name'], 0) + 1
            print(f"You bought 1 {item['name']} for ${total_price:.2f}.")

    def run_shop(self):
        print("Welcome to the Blacksmith!")
        while True:
            self.show_inventory()
            self.show_player_inventory()

            choice = input("\nEnter the item number to buy (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                print("Thanks for visiting! Come again.")
                break

            if not choice.isdigit():
                print("Please enter a valid number.")
                continue

            item_id = int(choice)
            self.buy_item(item_id)

class GunsmithStore:
    def __init__(self, player):
        self.player = player
        self.inventory = {
        1: {'name': 'revolver', 'price': 25, 'damage': (10, 15), 'quantity': 5},
        2: {'name': 'colt pistol', 'price': 35, 'damage': (15, 20), 'quantity': 5},
        3: {'name': 'rifle', 'price': 40, 'damage': (20, 25), 'quantity': 3},
        4: {'name': 'shotgun', 'price': 50, 'damage': (20, 35), 'quantity': 3},
        5: {'name': 'knife', 'price': 10, 'damage': (5, 10), 'quantity': 10},
        6: {'name': 'bowie knife', 'price': 30, 'damage': (10, 15), 'quantity': 3},
        7: {'name': 'pistol_ammo', 'price': 2, 'quantity': 50},
        8: {'name': 'rifle_ammo', 'price': 3, 'quantity': 30},
        9: {'name': 'shotgun_ammo', 'price': 5, 'quantity': 10}
        }
        WEAPON_AMMO_TYPES = {
        'pistol': 'pistol_ammo',
        'colt pistol': 'pistol_ammo',
        'rifle': 'rifle_ammo',
        'shotgun': 'shotgun_ammo',}

    def show_inventory(self):
        print("\n--- Gunsmith Inventory ---")
        for id, item in self.inventory.items():
            print(f"{id}. {item['name'].capitalize()} - ${item['price']} | Damage: {item.get('damage', "N/A")} | Stock: {item['quantity']}")
        print(f"\nYour Gold: ${self.player.gold:.2f}")

    def run_shop(self):
        while True:
            self.show_inventory()
            print("Enter the number of the weapon to buy, or 'q' to leave.")
            choice = input("Choice: ").strip().lower()

            if choice == 'q':
                print("You leave the gunsmith.")
                break

            if not choice.isdigit():
                print("Invalid input.")
                continue

            item_id = int(choice)
            if item_id in self.inventory:
                weapon = self.inventory[item_id]
                if self.player.gold >= weapon['price'] and weapon['quantity'] > 0:
                    self.player.gold -= weapon['price']
                    weapon['quantity'] -= 1
                    self.player.itemsinventory[weapon['name']] = self.player.itemsinventory.get(weapon['name'], 0) + 1
                    print(f"You bought a {weapon['name']}!")
                else:
                    print("Not enough gold or out of stock.")
            else:
                print("That weapon doesn't exist.")

class Role:
    def __init__(self, name):
        self.name = name
        self.xp = 0
        self.level = 1  # Start at level 1

    def gain_xp(self, player, amount):
        self.xp += amount
        print(f"Gained XP! {self.name.capitalize()} XP is now {self.xp}.")

        if self.xp >= self.level * 3: 
            self.level_up(player)

    def level_up(self, player):
        self.level += 1
        print(f"Your {self.name.capitalize()} role leveled up to {self.level}!")
        
        # Role-specific rewards
        if self.name == "traveler":
            player.travel_bonus += 1
            print("Your travel speed increased!")
        elif self.name == "trader":
            player.trade_bonus += 1
            print("You negotiate even better deals!")
        elif self.name == "herder":
            player.add_item("large meat")
            print("You found extra meat from your herd!")

player = Player()
print("Would you like to (1) Start New Game or (2) Load a Save?")

choice = input("Enter 1 or 2: ").strip()

if choice == "2":
    player = Player.load_game()
else:
    player = Player()
    print("Would you like the instructions?")
    Choice = input("Yes/No:")
    if Choice == "Yes":
        print("Welcome to Western Simulator!")
        time.sleep(2,)
        print("In this game you will try and survive the western life and complete quests.")
        time.sleep(2,)
        print("The rules are simple. You chose options that you would like to do. I tell you what happens. If you run out of health, you die.")
        time.sleep(3,)
        print("Now it is time to chose your role.")
        time.sleep(2,)
        print("Your options will be presented as A,B,and C... , Yes and No, or a number.(Your answer will not be accepted unless it is in the correct format.)")
        time.sleep(3,)
        print("Your options for a role are: (A) Herder, (B) Traveler, and (C) Trader.")
        Choice = input(": ")
        player.choose_role(Choice)
        player.role_progress(1)
        print(f"You chose the role {player.active_role.name.capitalize()}.")
        time.sleep(1,)
        print("You may switch roles once per town.")
        time.sleep(2,)
        print("Now let's start your journey.")
        time.sleep(1,)
        Location = ["Dustbowl, a tough town in the South Dakota territory.", 
                    "Rust Ridge, a thriving town in the eastern half of Colorado.", 
                    "Quarry Town, a large mining town on the banks of the Missouri River."]
        print("You wake up in the town of " + Location[random.randint(0,2)])
        print("The people greet you with nods as you walk down the mainstreet.")
        time.sleep(4,)
    else:
        print("Your options for a role are: (A) Herder, (B) Traveler, and (C) Trader.")
        Choice = input(": ")
        player.choose_role(Choice)
        player.role_progress(1)

while not player.Health <= 0:
    if player.invillage == True:
        player.HostilityFunc()
    player.RunDay()
    player.Day += 1
    if player.Health <= 0:
        break
    player.Hunger = player.Hunger + 1
    print("You feel hungrier...")
    time.sleep(3,)
    if player.Hunger >= 3:
        hunger_damage = player.Hunger*5
        lost_health = hunger_damage
        print(f"You lost {lost_health} health of hunger.")
    if player.poisoned > 0:
        damage = player.poisoned*5
        player.Health -=  damage
        player.Hunger += 1
        print(f"You suddenly feel sick and vomit on the ground.")
        time.sleep(2,)
        print(f"It feels unnatural; you conclude that you must be poisoned.")
        print(f"Your health has been reduced by {damage}.")
        print("You feel hungrier...")
        time.sleep(3,)
    choice = input("Would you like to save and quit? (yes/no): ").strip().lower()
    if choice == 'yes':
        self.save_game()
        print("Thanks for playing! See you next time.")
        exit()
    else:
        print("Continuing your adventure...")
        time.sleep(4,)
print(f"You died...")
print(f"Your final score is {player.score}.")
