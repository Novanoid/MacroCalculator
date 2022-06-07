import requests
from bs4 import BeautifulSoup
import base64
import json
import re
import shutil

# *blushes* I have a cwoupel owf kwestions
# def download_img(url, path):
#     res = requests.get(url, stream=True)
#
#     if res.status_code == 200:
#         with open(path, 'wb') as f:
#             shutil.copyfileobj(res.raw, f)
#         print('Image sucessfully Downloaded: ', path)
#     else:
#         print('Image Couldn\'t be retrieved')


class Product:
    def __init__(self):
        self.name = 'name'
        self.unit_price = {}
        self.amount = ''
        self.energy = ''
        self.fat = '0g'
        self.saturates = '0g'
        self.carbohydrate = '0g'
        self.sugars = '0g'
        self.fibre = '0g'
        self.protein = '0g'
        self.salt = '0g'

    def from_dict(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def from_sainsburys(self, search_obj):
        self.name = search_obj['name']
        self.unit_price = search_obj['unit_price']
        product_seo = search_obj['full_url'].split('/')[-1]

        # Product information request
        product_payload = {
            'filter[product_seo_url]': f'gb/groceries/{product_seo}',
        }
        product_r = requests.get('https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product', params=product_payload)
        product_dict = product_r.json()

        # decoding html
        decodedBytes = base64.urlsafe_b64decode(product_dict['products'][0]['details_html'])
        decodedStr = str(decodedBytes, "utf-8")

        # Parsing
        soup = BeautifulSoup(decodedStr, features='lxml')
        nutrition_table = soup.find('table', class_='nutritionTable')

        if 'ml' in nutrition_table.thead.find(text=re.compile(r'100')):
            measurement_type = '100ml'
        else:
            measurement_type = '100g'

        self.amount = measurement_type

        # Filling in dataframe
        mapping = {
            '<': '',
            '>': '',
            ' ': '',
            ',': '.',
        }

        for row in nutrition_table.find_all('tr'):
            row_text = row.text.lower()
            if 'mono' in row_text or 'poly' in row_text: continue
            if 'kcal' in row_text:
                split = list(row_text.replace(" ", "").split('kcal')[0])
                split.reverse()
                for i in split:
                    if i.isdigit():
                        self.energy = i + self.energy
                    else:
                        break
                self.energy = self.energy + 'kcal'
            elif 'fat' in row_text:
                self.fat = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'saturates' in row_text:
                self.saturates = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'carbohydrate' in row_text:
                self.saturates = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'sugars' in row_text:
                self.sugars = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'fibre' in row_text:
                self.fibre = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'protein' in row_text:
                self.protein = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
            elif 'salt' in row_text:
                self.salt = ''.join([mapping.get(letter, letter) for letter in list(row.find('td').text)])
                break
            else: continue

    @staticmethod
    def filter_native(search_term, shop, no):
        search_payload = {'filter[keyword]': f'{search_term}',
                          'page_number': 1,
                          'page_size': {no},
                          'sort_order': '-relevance'}

        if shop.lower() == 'sainsburys':
            r = requests.get('https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product',
                             params=search_payload)
            r_dict = r.json()
            return r_dict['products']

    @staticmethod
    def filter_local(search_term, filename):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            return list(filter(lambda df: search_term in df['name'].lower(), file_data))


class Ingredient:
    def __init__(self):
        self.name = ''
        self.price = 0.0
        self.amount = {
            'measure': 'g',
            'value': 0.0
        }
        self.energy = 0.0
        self.fat = 0.0
        self.saturates = 0.0
        self.carbohydrate = 0.0
        self.sugars = 0.0
        self.fibre = 0.0
        self.protein = 0.0
        self.salt = 0.0

    def from_Product(self, product_obj, amount):
        self.name = product_obj.name

        measure_mapping = {
            'ltr': 1000,
            'ml': 100,
            'g': 100,
            'kg': 1000
        }

        no = 0
        if 'ml' in amount:
            self.amount['measure'] = 'ml'
            gramsorml = float(amount.split('ml')[0])
            self.amount['value'] = gramsorml
        elif 'g' in amount:
            self.amount['measure'] = 'g'
            gramsorml = float(amount.split('g')[0])
            self.amount['value'] = gramsorml
        else:
            self.amount['measure'] = 'ea'
            no = float(amount.split('f')[0])
            gramsorml = ((self.grab_serving_calories(self.name) * no) / float(product_obj.name.split('kcal')[0])) * 100
            self.amount['value'] = no

        # Price
        unit_price = product_obj.unit_price
        if unit_price['measure'] == 'ea':
            self.price = round(no * unit_price['price'], 2)
        else:
            self.price = round((gramsorml / measure_mapping[unit_price['measure']]) * unit_price['price'], 2)

        per100 = gramsorml / 100
        self.energy = round(per100 * float(product_obj.energy.split('kcal')[0]), 2)
        self.fat = round(per100 * float(product_obj.fat.split('g')[0].split('ml')[0]), 2)
        self.saturates = round(per100 * float(product_obj.saturates.split('g')[0].split('ml')[0]), 2)
        self.carbohydrate = round(per100 * float(product_obj.carbohydrate.split('g')[0].split('ml')[0]), 2)
        self.sugars = round(per100 * float(product_obj.sugars.split('g')[0].split('ml')[0]), 2)
        self.fibre = round(per100 * float(product_obj.fibre.split('g')[0].split('ml')[0]), 2)
        self.protein = round(per100 * float(product_obj.protein.split('g')[0].split('ml')[0]), 2)
        self.salt = round(per100 * float(product_obj.salt.split('g')[0].split('ml')[0]), 2)

    @staticmethod
    def grab_serving_calories(product_name):
        file = 'ea.json'
        with open(file, 'r+') as f:
            file_data = json.load(f)
            filtered_list = list(filter(lambda product: product['name'].lower() in product_name.lower(), file_data))
            perlen = 0
            for item in filtered_list:
                if len(list(item['name'])) / len(list(product_name)) > perlen:
                    perlen = len(list(item['name'])) / len(list(product_name))
                    correctitem = item
            return correctitem['serving']['calories']


class Recipe:
    def __init__(self):
        self.name = ''
        self.img = ''
        self.serving_size = 0.0
        self.price_per_serving = 0.0
        self.ratio = 0.0
        self.energy = 0.0
        self.fat = 0.0
        self.saturates = 0.0
        self.carbohydrate = 0.0
        self.sugars = 0.0
        self.fibre = 0.0
        self.protein = 0.0
        self.salt = 0.0
        self.ingredients = []

    def write_recipe(self):
        for i in range(len(self.ingredients)):
            self.ingredients[i] = self.ingredients[i].__dict__
        write_json(self.__dict__, 'recipes.json')

    def add_ingredient(self, search_term):
        # First check local_products.json
        local_products = Product.filter_local(search_term=search_term, filename='local_products.json')

        # Request relevant product list from sainsburys api
        native_products = Product.filter_native(shop='sainsburys', no=10, search_term=search_term)
        combined_products = local_products + native_products
        for i in range(len(combined_products)):
            print(str(i) + ': ' + combined_products[i]['name'])

        # Retrieve Product object
        inp1 = input('Enter the index of the correct ingredient\n')
        newProduct = Product()
        if combined_products[int(inp1)] in local_products:
            newProduct.from_dict(combined_products[int(inp1)])
        else:
            newProduct.from_sainsburys(combined_products[int(inp1)])

        # Retrieve Ingredient object
        newIngredient = Ingredient()
        inp2 = input('Enter the amount of ingredient (ie. 2, 50g, 30ml)\n')
        newIngredient.from_Product(newProduct, inp2)

        # Updating the Recipe object's properties
        self.energy = round(self.energy, 2) + newIngredient.energy
        self.fat = round(self.fat, 2) + newIngredient.fat
        self.saturates = round(self.saturates, 2) + newIngredient.saturates
        self.carbohydrate = round(self.carbohydrate, 2) + newIngredient.carbohydrate
        self.sugars = round(self.sugars, 2) + newIngredient.sugars
        self.fibre = round(self.fibre, 2) + newIngredient.fibre
        self.protein = round(self.protein, 2) + newIngredient.protein
        self.salt = round(self.salt, 2) + newIngredient.salt
        self.price_per_serving += round(newIngredient.price / self.serving_size, 2)

        # Appending the Ingredient object
        self.ingredients.append(newIngredient.__dict__)

    def add_recipe(self, serving_size):
        self.serving_size = serving_size
        while 1:
            inp0 = input('Enter ingredient, or press enter to finish.\n')
            if inp0 == '': break
            else:
                # Return Ingredient dataframe
                self.add_ingredient(inp0)
        self.write_recipe()

    @staticmethod
    def dict_to_Recipe(dictionary):
        newRecipe = Recipe()
        for key in dictionary:
            setattr(newRecipe, key, dictionary[key])
        return newRecipe

    @staticmethod
    def filter_local(search_term, filename):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            return list(filter(lambda df: search_term.lower() in df['name'].lower(), file_data))


def write_json(df, filename):
    with open(filename, 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside product_details
        file_data.append(df)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


