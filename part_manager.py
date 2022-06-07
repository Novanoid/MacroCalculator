import tkinter as tk
from sainsburys_requests import *
from tkinter import ttk
from tkinter import messagebox


class Application(tk.Tk):  # Tk defines a parent window
    def __init__(self):
        super().__init__()
        self.title('Application')
        self.geometry("950x700")
        # self.resizable(0, 0)
        # windows only (remove the minimize/maximize button)
        self.attributes('-toolwindow', True)

        # Layout on the root window, total daily calories and add recipe frame in each column
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # initialize frame instances
        self.frames = {
            AddRecipeFrame: AddRecipeFrame(
                self),
            MacroCalculatorFrame: MacroCalculatorFrame(
                self
            )
        }

        # Assign frame instances to grid
        self.frames[MacroCalculatorFrame].grid(column=0, row=0, padx=8, pady=8, sticky=(tk.W, tk.N))
        self.frames[AddRecipeFrame].grid(column=1, row=0, padx=8, pady=8, sticky=(tk.W, tk.N))


class AddRecipeFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.new_recipe = Recipe()
        self.create_widgets()

    def create_widgets(self):
        # Add New Recipe label
        self.add_new_recipe_label = tk.Label(
            self, text='Add New Recipe', font=('bold', 12), pady=5, padx=5)  # padding is inside the frame
        self.add_new_recipe_label.grid(row=0, column=0, columnspan=4)

        # Recipe Name Label
        self.name_recipe_label = tk.Label(
            self, text='Name', font=('bold', 12), pady=5, padx=5)
        self.name_recipe_label.grid(row=1, column=0, sticky=tk.W)  # sticky tells how cell should react if its resized

        # Recipe Name Textbox
        self.name_recipe_text = tk.StringVar()
        self.name_recipe_entry = tk.Entry(self, textvariable=self.name_recipe_text)
        self.name_recipe_entry.grid(row=1, column=1)

        # Recipe Serving Label
        self.serving_recipe_label = tk.Label(
            self, text='Serving', font=('bold', 12), pady=5, padx=5)
        self.serving_recipe_label.grid(row=2, column=0, sticky=tk.W)  # sticky tells how cell should react if its resized

        # Recipe Serving Textbox
        self.serving_recipe_text = tk.StringVar()
        self.serving_recipe_entry = tk.Entry(self, textvariable=self.serving_recipe_text)
        self.serving_recipe_entry.grid(row=2, column=1)

        # Recipe Ingredient Label
        self.ingredient_recipe_label = tk.Label(
            self, text='Ingredient', font=('bold', 12), pady=5, padx=5)
        self.ingredient_recipe_label.grid(row=3, column=0, sticky=tk.W)  # sticky tells how cell should react if its resized

        # Recipe Ingredient Textbox
        self.ingredient_recipe_text = tk.StringVar()
        self.ingredient_recipe_entry = tk.Entry(self, textvariable=self.ingredient_recipe_text)
        self.ingredient_recipe_entry.grid(row=3, column=1)

        # Recipe Add Ingredient Button
        self.search_ingredient_btn = tk.Button(
            self, text="Search", width=8, command=self.open_ingredient_window)
        self.search_ingredient_btn.grid(row=3, column=2, pady=5, padx=5)

        # Recipe Delete Ingredient Button
        self.delete_ingredient_btn = tk.Button(
            self, text="Delete", width=8, command=self.remove_ingredient_list)
        self.delete_ingredient_btn.grid(row=3, column=3, pady=5, padx=5)

        # Ingredients list (listbox)
        self.ingredient_listbox = tk.Listbox(self, height=4, width=60, border=0)
        self.ingredient_listbox.grid(row=4, column=0, columnspan=5, rowspan=2, pady=6, padx=10)

        # Create scrollbar
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=4, column=5)

        # Set scrollbar to product list
        self.ingredient_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.ingredient_listbox.yview)

        # Add Recipe Button
        self.add_recipe_btn = tk.Button(
            self, text="Add Recipe", command=self.add_recipe)
        self.add_recipe_btn.grid(row=1, column=2, rowspan=2, columnspan=2, pady=5, padx=5, sticky='nesw')

    def open_ingredient_window(self):
        if self.ingredient_recipe_text.get() == '':
            messagebox.showerror(
                "Required Fields", "Please enter an ingredient name")
            return

        IngredientWindow(parent=self, ingredient_recipe_text=self.ingredient_recipe_text)

    def add_ingredient_list(self, ingredient_to_add):
        self.new_recipe.ingredients.append(ingredient_to_add)
        self.ingredient_listbox.insert(tk.END, ingredient_to_add.name +
                                       f" - {str(ingredient_to_add.amount['value'])}" +
                                       f"{ingredient_to_add.amount['measure']}")

    def remove_ingredient_list(self):
        if len(self.ingredient_listbox.curselection()) == 0:
            messagebox.showerror(
                "Required Fields", "Please select an ingredient")
            return
        curidx = self.ingredient_listbox.curselection()[0]

        self.new_recipe.ingredients.pop(curidx)
        self.ingredient_listbox.delete(curidx)

    def add_recipe(self):
        if self.name_recipe_text.get() == '' or self.serving_recipe_text.get() == '' or len(self.new_recipe.ingredients) == 0:
            messagebox.showerror(
                "Required Fields", "Please include all fields")
            return

        # Finalising Recipe Dataframe
        self.new_recipe.name = self.name_recipe_text.get()
        self.new_recipe.serving_size = float(self.serving_recipe_text.get())
        for ingredient in self.new_recipe.ingredients:
            self.new_recipe.energy = round(self.new_recipe.energy, 2) + ingredient.energy
            self.new_recipe.fat = round(self.new_recipe.fat, 2) + ingredient.fat
            self.new_recipe.saturates = round(self.new_recipe.saturates, 2) + ingredient.saturates
            self.new_recipe.carbohydrate = round(self.new_recipe.carbohydrate, 2) + ingredient.carbohydrate
            self.new_recipe.sugars = round(self.new_recipe.sugars, 2) + ingredient.sugars
            self.new_recipe.fibre = round(self.new_recipe.fibre, 2) + ingredient.fibre
            self.new_recipe.protein = round(self.new_recipe.protein, 2) + ingredient.protein
            self.new_recipe.salt = round(self.new_recipe.salt, 2) + ingredient.salt
            self.new_recipe.price_per_serving += round(ingredient.price / self.new_recipe.serving_size, 2)

        # Normalize to the bulk powder ratio
        normalize_value = 0.199
        self.new_recipe.ratio = round(self.new_recipe.protein/(self.new_recipe.energy*normalize_value))
        print(self.new_recipe.__dict__)

        # Writing new recipe
        self.new_recipe.write_recipe()

        # Resetting
        self.reset_add_recipe()

    def reset_add_recipe(self):
        self.new_recipe = Recipe()
        self.ingredient_recipe_entry.delete(0, tk.END)
        self.name_recipe_entry.delete(0, tk.END)
        self.serving_recipe_entry.delete(0, tk.END)
        self.ingredient_listbox.delete(0, tk.END)


class MacroCalculatorFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.style = ttk.Style()
        self.current_data = {}
        self.current_sliders = {}
        # Smallest ratio for color mapping
        self.bottom = min(Recipe.filter_local('', 'recipes.json'), key=lambda i: (i['ratio']))['ratio']
        self.create_widgets()

    def create_widgets(self):
        # Macro Calculator label
        tk.Label(self, text='Macro Calculator', font=('bold', 12), pady=5, padx=5).grid(row=0, column=0, columnspan=4)

        # Add Recipe name Label
        tk.Label(self, text='Recipe Name', font=('bold', 12), pady=5, padx=5).grid(row=1, column=0, sticky=tk.W)

        # Recipe Entrybox
        self.recipe_name_text = tk.StringVar()
        self.recipe_name_text.trace_add('write', self.update_search_treeview)
        self.recipe_name_entry = tk.Entry(self, textvariable=self.recipe_name_text)
        self.recipe_name_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))

        # Add recipe
        self.recipe_add_btn = tk.Button(
            self, text="Add", command=self.add_recipe)
        self.recipe_add_btn.grid(row=1, column=3,  pady=5, padx=5, sticky='nsew')

        # Recipe search treeview
        cols = ('Name', 'Calories', 'Protein', 'Ratio')
        self.recipe_search_treeview = ttk.Treeview(self, columns=cols, height=5, show='headings')
        for col in cols:
            self.recipe_search_treeview.heading(col, text=col)
            if col == 'Name':
                self.recipe_search_treeview.column(col, width=250, anchor=tk.CENTER)
                continue
            self.recipe_search_treeview.column(col, width=80, anchor=tk.CENTER)
            self.recipe_search_treeview.heading(col, text=col)

        self.recipe_search_treeview.grid(row=2, column=0, columnspan=4, rowspan=2, pady=5, padx=5, sticky='nsew')

        # Update treeview list
        self.update_search_treeview(0, 0, 0)

        # Current dataframe
        tk.Label(self, text='Current Data', font=('bold', 12), pady=5, padx=5).grid(row=5, column=0, columnspan=4)

        # Recipe list (treeview)
        cols2 = ('Name', 'Calories', 'Protein', 'Serving')
        self.recipe_treeview = ttk.Treeview(self, columns=cols2, height=5, show='headings')
        for col in cols2:
            self.recipe_treeview.heading(col, text=col)
            if col == 'Name':
                self.recipe_treeview.column(col, width=250, anchor=tk.CENTER)
                continue
            self.recipe_treeview.column(col, width=80, anchor=tk.CENTER)
            self.recipe_treeview.heading(col, text=col)
        self.recipe_treeview.grid(row=6, column=0, columnspan=4, rowspan=2, pady=5, padx=5, sticky='nsew')
        self.recipe_treeview.bind('<<TreeviewSelect>>', self.change_slider)

        # Delete Recipe
        self.recipe_delete_btn = tk.Button(
            self, text="Delete", command=self.delete_recipe)
        self.recipe_delete_btn.grid(row=8, column=2,  pady=5, padx=5, sticky='nsew')

        # Edit Recipe
        self.recipe_edit_btn = tk.Button(
            self, text="Edit", command=self.edit_recipe)
        self.recipe_edit_btn.grid(row=8, column=3, pady=5, padx=5, sticky='nsew')

        # Nutritional treeview
        self.nutrition_treeview = ttk.Treeview(self, columns=('Information', 'Values'), show='headings')
        self.nutrition_treeview.heading('Information', text='Information')
        self.nutrition_treeview.heading('Values', text='Values')
        self.nutrition_treeview.grid(row=9, column=0, columnspan=4, pady=5, padx=5, sticky='nsew')

    def proteinkcal_color_mapping(self, ratio):
        # Takes normalised ratio (to Bulk protein powder) of protein / calories
        # bottom is the lowest ratio value
        if ratio >= (1+self.bottom)/2:
            r = int((510/(self.bottom-1))*(ratio-1))
            r = hex(r).split('x')[-1]
            if len(list(r)) != 2: r += '0'
            return f'#{r}ff00'
        else:
            g = int((510/(1-self.bottom))*(ratio-self.bottom))
            g = hex(g).split('x')[-1]
            if len(list(g)) != 2: g += '0'
            return f'#ff{g}00'

    def update_search_treeview(self, name, index, mode):
        # Clear recipe treeview
        self.recipe_search_treeview.delete(*self.recipe_search_treeview.get_children())

        # Filter through recipes.json to search for it
        self.filtered_list = Recipe.filter_local(self.recipe_name_text.get(), 'recipes.json')

        # Sort filtered list by ratio
        self.filtered_list.sort(key=lambda i: (i['ratio']), reverse=True)

        # Present this filtered list on the recipe_search_listbox
        for recipe in self.filtered_list:
            self.recipe_search_treeview.insert('', tk.END, values=(recipe['name'], recipe['energy'], recipe['protein'], recipe['ratio']), tags=[recipe['name']])
            self.recipe_search_treeview.tag_configure(recipe['name'], background=self.proteinkcal_color_mapping(recipe['ratio']))

    def add_recipe(self):
        # Check if recipe is selected in listbox
        curitem = self.recipe_search_treeview.focus()
        curitemdict = self.recipe_search_treeview.item(curitem)
        if curitemdict['values'] == '':
            messagebox.showerror(
                        "Required Fields", "Please select a recipe to add")
            return

        # Assign selected recipe to Recipe object so that we can append it to the self.currentdata
        newRecipedict = list(filter(lambda df: curitemdict['values'][0].lower() in df['name'].lower(), self.filtered_list))[0]
        newRecipe = Recipe.dict_to_Recipe(newRecipedict)
        self.current_data[newRecipe.name] = newRecipe

        # Show the new recipe in the recipe treeview view
        self.recipe_treeview.insert('', tk.END, values=(newRecipe.name, newRecipe.energy, newRecipe.protein, newRecipe.serving_size),
                                           tags=[newRecipe.name])

        # New slider logic
        self.new_slider(newRecipe)

        # update nutritional table
        self.update_nutritional_table()

    def new_slider(self, newRecipe):
        value = tk.DoubleVar()
        self.current_sliders[newRecipe.name] = (tk.Scale(self,
                                                         from_=0.1,
                                                         to=5,
                                                         orient='horizontal',
                                                         resolution=0.1,
                                                         command=self.update_slider,
                                                         variable=value))
        value.set(int(newRecipe.serving_size))
        self.current_sliders[newRecipe.name].grid_remove()
        # self.current_sliders[newRecipe].set(int(newRecipe.serving_size))
        # self.current_sliders[newRecipe].grid(row=8, column=0,  pady=5, padx=5, sticky='nsew')

    def update_slider(self, value):
        # Occurs when slider is changed when there is a current selection
        # Will change the recipe frame of the selected Recipe
        curitem = self.recipe_treeview.focus()
        curitemdict = self.recipe_treeview.item(curitem)
        if curitemdict['values'] == '':
            return

        # Change Recipe object
        recipe = self.current_data[curitemdict['values'][0]]

        # multiple every value by the new value / old value
        fctr = float(value)/recipe.serving_size
        recipe.serving_size = round(fctr*recipe.serving_size, 2)
        recipe.energy = round(fctr*recipe.energy, 2)
        recipe.fat = round(fctr*recipe.fat, 2)
        recipe.saturates = round(fctr*recipe.saturates, 2)
        recipe.carbohydrate = round(fctr*recipe.carbohydrate, 2)
        recipe.sugars = round(fctr*recipe.sugars, 2)
        recipe.fibre = round(fctr*recipe.fibre, 2)
        recipe.protein = round(fctr*recipe.protein, 2)
        recipe.salt = round(fctr*recipe.salt, 2)

        # Update the recipe treeview serving columm
        self.recipe_treeview.item(curitem, values=[curitemdict['values'][0], str(recipe.energy), str(recipe.protein), str(recipe.serving_size)])

        # Update nutritional table
        self.update_nutritional_table()

    def change_slider(self, evt):
        # Occurs when a recipe is selected, brings it to the front and also shows it
        curitem = evt.widget.focus()
        curitemdict = evt.widget.item(curitem)
        if curitemdict['values'] == '': return

        self.current_sliders[curitemdict['values'][0]].grid(row=8, column=0, columnspan=2, pady=5, padx=5, sticky='nsew')
        self.current_sliders[curitemdict['values'][0]].tkraise()

    def delete_recipe(self):
        curitem = self.recipe_treeview.selection()[0]
        curitemdict = self.recipe_treeview.item(curitem)
        if curitemdict['values'] == '':
            messagebox.showerror(
                        "Required Fields", "Please select a recipe to add")
            return

        self.current_data.pop(curitemdict['values'][0])
        self.current_sliders.pop(curitemdict['values'][0])
        self.recipe_treeview.delete(curitem)
        self.update_nutritional_table()

    def edit_recipe(self):
        print('Haha yes')

    def update_nutritional_table(self):
        self.nutrition_treeview.delete(*self.nutrition_treeview.get_children())
        price, energy, fat, saturates, carbohydrates, sugars, fibre, protein, salt = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        for key, recipe in self.current_data.items():
            price += (recipe.price_per_serving * recipe.serving_size)
            energy += recipe.energy
            fat += recipe.fat
            saturates += recipe.saturates
            carbohydrates += recipe.carbohydrate
            sugars += recipe.sugars
            fibre += recipe.fibre
            protein += recipe.protein
            salt += recipe.salt

        self.nutrition_treeview.insert('', tk.END, values=('Price (£)', str(round(price, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Energy (kcal)', str(round(energy, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Protein (g)', str(round(protein, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Fat (g)', str(round(fat, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Saturates (g)', str(round(saturates, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Carbohydrates (g)', str(round(carbohydrates, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Sugars (g)', str(round(sugars, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Fibre (g)', str(round(fibre, 2))))
        self.nutrition_treeview.insert('', tk.END, values=('Salt (g)', str(round(salt, 2))))


class IngredientWindow(tk.Toplevel):
    def __init__(self, parent, ingredient_recipe_text):
        super().__init__()
        self.ingredient_recipe_text = ingredient_recipe_text
        self.parent = parent
        self.title("Add Ingredient")
        self.geometry("500x225")
        self.newIngredient = Ingredient()
        self.create_ingredient_window_widgets()

    def create_ingredient_window_widgets(self):
        tk.Label(self,
              text='Ingredients List', font=('bold', 12), pady=6, padx=10).grid(row=0, column=0, sticky=(tk.W, tk.S))
        # Ingredients list (listbox)
        self.product_listbox = tk.Listbox(self, height=10, width=60, border=0)
        self.product_listbox.grid(row=1, column=0, columnspan=3, rowspan=6, pady=6, padx=10)

        # Create scrollbar
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=1, column=3)

        # Set scrollbar to product list
        self.product_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.product_listbox.yview)

        # Amount Label
        tk.Label(self,
              text='Amount', font=('bold', 10)).grid(row=2, column=4, sticky=(tk.W, tk.S))

        # Amount textbox
        self.product_amount_text = tk.StringVar()
        self.product_amount_entry = tk.Entry(self, textvariable= self.product_amount_text, width=12)
        self.product_amount_entry.grid(row=3, column=4, sticky=(tk.W, tk.N))

        # Get list of ingredient objects
        local_products = Product.filter_local(search_term=self.ingredient_recipe_text.get(), filename='local_products.json')
        # Request relevant product list from sainsburys api
        native_products = Product.filter_native(shop='sainsburys', no=10, search_term=self.ingredient_recipe_text.get())
        product_list = local_products + native_products

        # Populate ingredients list with obj_list
        for product in product_list:
            self.product_listbox.insert(tk.END, product['name'])

        # Add Button
        tk.Button(self,
               text="Add", width=10, command=lambda: self.add_ingredient(local_products, product_list)).grid(row=4, column=4, sticky=tk.N)

    def add_ingredient(self, local, total):
        amount_entry = self.product_amount_entry.get()
        if 'g' not in amount_entry and 'ml' not in amount_entry and not amount_entry.isdigit():
            messagebox.showerror(
                "Required Fields", "Please enter a correct amount (eg. 50g, 20ml, 6)")
            return
        elif len(self.product_listbox.curselection()) == 0:
            messagebox.showerror(
                "Required Fields", "Please select a product")
            return

        curidx = self.product_listbox.curselection()[0]

        # Retrieve Product object
        newProduct = Product()
        if total[int(curidx)] in local:
            newProduct.from_dict(total[int(curidx)])
        else:
            newProduct.from_sainsburys(total[int(curidx)])

        # Retrieve Ingredient object
        self.newIngredient.from_Product(newProduct, amount_entry)

        # Update parent listbox
        self.parent.add_ingredient_list(self.newIngredient)

        # Close window
        self.destroy()


app = Application()
app.mainloop()









