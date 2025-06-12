import json
import os
import math

class App:
    def __init__(self):
        self.recipes_path = "recipes"

        self.dirs = []
        self.all_item = {}
        self.item_count = {}
        self.crafting_items = {}
        with open("type.json") as f:
            self.crafting_type = json.load(f)

        self.load()
    @staticmethod
    def load_recipe(path:str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            __recipe = json.load(f)
        return __recipe
    def get_all_dir_item(self, dirs:list):
        all_items = {}
        for _dir in dirs:
            path = f"recipes/{_dir}"
            for recipe_name in os.listdir(path):
                recipe:dict = self.load_recipe(f"{path}/{recipe_name}")
                try:
                    result = recipe["result"]
                    if type(result) == dict:
                        item_id = result["id"].split(":")[1]
                    else:
                        item_id = result
                except KeyError:
                    continue
                if item_id not in all_items:
                    all_items[item_id] = [f"{path}/{recipe_name}"]
        return all_items

    @staticmethod
    def get_recipe_data(recipe_dict:dict):
        try:
            recipe_type = recipe_dict["type"]
        except KeyError:
            raise KeyError(f"Recipe type not found in {recipe_dict}")
        match recipe_type:
            case "minecraft:blasting":
                ingredient = recipe_dict["ingredient"]
                return {ingredient: 1}, 1
            case "minecraft:campfire_cooking":
                ingredient = recipe_dict["ingredient"]
                return {ingredient: 1}, 1
            case "minecraft:crafting_shaped":
                key:dict[str,str] = recipe_dict["key"]
                pattern:list = recipe_dict["pattern"]
                __items = {}
                for line in pattern:
                    for char in line:
                        if char not in key:
                            continue
                        item_name = key[char]
                        if item_name not in __items:
                            __items[item_name] = 1
                        else:
                            __items[item_name] += 1
                __result_count = recipe_dict["result"]["count"]
                return __items, __result_count
            case "minecraft:crafting_shapeless":
                ingredients=recipe_dict["ingredients"]
                __items = {}
                for i in ingredients:
                    if i in __items:
                        __items[i] += 1
                    else:
                        __items[i] = 1
                __result_count = recipe_dict["result"]["count"]
                return __items, __result_count
            #------------------
            #crafting_transmute
            #crafting_special_*
            #crafting_decorated_pot
            #------------------
            case "minecraft:smelting":
                ingredient:dict = recipe_dict["ingredient"]
                return {ingredient: 1}, 1
            case "minecraft:smithing_transform":
                base = recipe_dict["base"]
                template = recipe_dict["template"]
                addition = recipe_dict["addition"]
                __items = {base: 1, template: 1, addition: 1}
                __result_count = recipe_dict["result"]["count"]
                return __items, __result_count
            case "minecraft:smoking":
                ingredient = recipe_dict["ingredient"]
                return {ingredient: 1}, 1
            case "minecraft:stonecutting":
                ingredient = recipe_dict["ingredient"]
                __result_count = recipe_dict["result"]["count"]
                return {ingredient: 1}, __result_count
            case _:
                raise Exception("recipe format error")
    @staticmethod
    def get_first_recipe(recipes:dict) -> dict:
        recipe_keys = recipes.keys()
        first_key = None
        for i in recipe_keys:
            first_key = i
            break
        return recipes[first_key]

    def load(self):
        self.dirs = self.get_recipe_dirs()
        self.all_item = self.get_all_dir_item(self.dirs)

    def get_recipe_dirs(self):
        return os.listdir(self.recipes_path)

    def find_recipe(self, item_id):
        recipe_data = {}
        if item_id in self.all_item:
            item_recipes = self.all_item[item_id]
            for recipe_path in item_recipes:
                recipe = self.load_recipe(recipe_path)
                _type = recipe["type"]
                recipe_data[_type] = recipe
            return recipe_data
        else:
            return None

    def clear(self):
        self.crafting_items = {}

    def add_crafting_items(self, item_id:str,quantity:int):
        if item_id.find(":") != -1:
            item_id = item_id.split(":")[1]
        if quantity == 0:
            quantity = 1
        if item_id not in self.all_item:
            print(f"Invalid parameters '{item_id}'")
            return
        if item_id not in self.crafting_items:
            self.crafting_items[item_id] = quantity
        else:
            self.crafting_items[item_id] += quantity
        print(f"now '{item_id}' is crafting {self.crafting_items[item_id]}")
    @staticmethod
    def show(items:dict[str,int]):
        if len(items) == 0:
            print("(No items)")
            return
        for key in items.keys():
            quantity = items[key]
            print(f"--{key}*{quantity} ({round((quantity/64), 2)}*64)({round((quantity/1728), 2)} box)")

    def calculate_total_material(self):
        need_confirm = False

        print("to craft items:")
        self.show(self.crafting_items)
        __user_input = "confirm"
        if need_confirm:
            __user_input = input("Input 'confirm' to continue: ")
        if __user_input == "confirm":
            output_items = {}
            input_items = {}
            for item in self.crafting_items.keys():
                if ":" in item:
                    item = item.split(":")[1]
                #讀取資料
                __recipe = self.load_recipe(self.all_item[item][0])
                try:
                    __item_count, __result_count = self.get_recipe_data(__recipe)
                except KeyError as err:
                    print(err)
                    print(f"Key '{__recipe}' not found")
                    continue
                #計算需要合成的最少數量
                crafting_item_count = self.crafting_items[item]
                least_times = math.ceil(crafting_item_count/__result_count)
                least_count = least_times*__result_count
                #添加物絣進入輸出字典
                try:
                    output_items[item] += least_count
                except KeyError:
                    output_items[item] = least_count
                #添加最少合成材料進新的合成字典
                for i in __item_count.keys():
                    new_i = i
                    if ":" in new_i:
                        new_i = new_i.split(":")[1]
                    try:
                        input_items[new_i] += least_times * __item_count[i]
                    except KeyError:
                        input_items[new_i] = least_times * __item_count[i]

            print("----------\ntotal material:")
            self.show(input_items)
            print(f"\noutput items:")
            self.show(output_items)
            print("----------")
        else:
            print("-Cancel-")

class UserControl:
    def __init__(self):
        self.app = App()
        self.run = True
        self.command()
    def command(self)->str|None:
        self.run = True
        print("材料計算機")
        # user_control = UserControl()
        while self.run:
            try:
                user_input = input("input command:")
                print("-running command-", '"' + user_input + '"')
                if user_input == "clear":
                    self.app.clear()
                    print("Done!")
                    continue
                elif user_input == "count":
                    self.app.calculate_total_material()
                    print("Done!")
                    continue
                elif "add" in user_input:
                    try:
                        _, _id, _quantity = user_input.split(" ")
                    except ValueError:
                        _, _id = user_input.split(" ")
                        _quantity = 1
                    self.app.add_crafting_items(_id, int(_quantity))
                    print("Done!")
                    continue
                elif user_input == "show":
                    self.app.show(self.app.crafting_items)
                    print("Done!")
                    continue
                elif "find" in user_input:
                    _, _id = user_input.split(" ")[0:2]
                    if len(user_input.split(" ")) > 2:
                        print("format error")
                        continue
                    recipe = self.app.find_recipe(_id)
                    if recipe is not None:
                        print(recipe)
                    try:
                        first_recipe = self.app.get_first_recipe(self.app.find_recipe(_id))
                        items, result_count = self.app.get_recipe_data(first_recipe)
                    except TypeError:
                        print("Invalid recipe")
                        continue
                    print(f"{items}  x{result_count}")
                    print(f"from -{self.app.all_item[_id]}-")
                    continue
                elif user_input == "exit":
                    self.run = False
                    print("Done!")
                    continue
                print('---null command---')
            except KeyboardInterrupt:
                self.run = False

if __name__ == "__main__":
    user = UserControl()


