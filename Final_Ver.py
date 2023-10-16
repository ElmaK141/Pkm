"""
A GUI for Pokemon custom type effectiveness.

Inspired by a mod that added 50+ new types to Pokemon FireRed. 
I created this GUI to help me keep track of the type effectiveness
of all the new types. I also wanted to learn how to use Tkinter.

Completed features:
- Add/remove types
- Change type effectiveness
- Calculate type effectiveness of a combination of types
- Save/load type effectiveness configuration

Future features:
- Add/remove combined effictiveness (e.g. Fire attacks a Fire/Custom type resulting in 0.5x damage)
- Dynamic spacing of elements
- Wrap grid in a scrollable frame to account for many types
    
"""

from collections import Counter
import tkinter as tk
import logging
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import json
import ast

class PokemonTypeGrid(tk.Tk):
    def __init__(self, master):
        self.master = master
        self.grid = {}

        # Separate frames for calculator and grid
        self.grid_frame = Frame(self.master)
        self.grid_frame.grid(row=1, column=0, padx=20, pady=20)
        
        # Add vertical line between grid and calculator sections
        separator = Frame(self.master, width=2, bg="black")
        separator.grid(row=1, column=1, rowspan=100, sticky=N+S)
        
        self.calculator_frame = Frame(self.master)
        self.calculator_frame.grid(row=1, column=2, padx=20, pady=20, sticky=N+S+E+W)
        
        self.button_frame = Frame(master)
        self.button_frame.grid(row=0, column=0)
        
        self.types = [
            "Normal", "Fire", "Water", "Electric",
            "Grass", "Ice", "Fighting", "Poison",
            "Ground", "Flying", "Psychic", "Bug",
            "Rock", "Ghost", "Dragon", "Dark",
            "Steel", "Fairy"
        ]
        self.base_types = self.types.copy()
        self.effectiveness = [1.0, 2.0, 0.5, 0.0]
        self.effectiveness_color = {
            1.0: "#fff",
            2.0: "#4e9a06",
            0.5: "#a40000",
            0.0: "#2e3436",
            '?': '#ADD8E6'
        }
        self.effectiveness_display = {
            1.0: "1",
            2.0: "2",
            0.5: "½",
            0.0: "0",
            '?': "?"
        }
        self.effectiveness_dict = {}
        self.load_configuration()
        self.initialize_grid()
        self.initialize_buttons()
        self.multiplier_labels = {}
        self.initialize_calculator()
        
    def initialize_grid(self):
        button_width = 3
        button_height = 1

        # Setting grid rows and columns to have uniform size
        for i in range(len(self.types) + 2):  # +2 accounts for the row and column labels
            self.grid_frame.grid_rowconfigure(i, minsize=30)  # 30 pixels
            self.grid_frame.grid_columnconfigure(i, minsize=30)  # 30 pixels

        for index, poke_type in enumerate(self.types):
            row_label = tk.Label(self.grid_frame, text=poke_type)
            row_label.grid(row=index + 2, column=0, sticky=N+S+E+W)
            row_label.bind("<Button-1>", lambda e, t=poke_type: self.remove_type(t))

            col_label = tk.Label(self.grid_frame, text=poke_type[:3])
            col_label.grid(row=1, column=index + 1, sticky=N+S+E+W)
            col_label.bind("<Button-1>", lambda e, t=poke_type: self.remove_type(t))

        for row, poke_type1 in enumerate(self.types):
            for col, poke_type2 in enumerate(self.types):
                self.add_button(poke_type1, poke_type2, row + 2, col + 1, button_width, button_height)
        
        self.add_type_entry()
        
                
    def initialize_calculator(self):
        
        self.type_vars = [StringVar(value='None'), StringVar(value='None'), StringVar(value='None')]
        self.type_option_menus = []

        # # Create a space above the dropdowns
        Frame(self.calculator_frame).grid(row=0, column=0, pady=10)
        
        common_width = 10
        # Create the dropdowns
        for i, var in enumerate(self.type_vars):
            option_menu = OptionMenu(self.calculator_frame, var, 'None', *self.types)
            option_menu.config(width=common_width)
            option_menu.grid(row=1, column=i, padx=1, pady=0)
            self.type_option_menus.append(option_menu)
            
        # Create "Calculate" button
        self.calculate_button = Button(self.calculator_frame, text="Calculate", command=self.calculate_effectiveness)
        self.calculate_button.grid(row=2, column=0, columnspan=3, sticky=W+E)
        
        # Create space below "Calculate" button
        Frame(self.calculator_frame, height=40).grid(row=3, column=0)
        
        self.initialize_multiplier_labels()
        
    def initialize_buttons(self):
        self.save_button = Button(self.button_frame, text="Save", command=self.save_configuration)
        self.save_button.grid(row=0, column=0)
        
        self.load_button = Button(self.button_frame, text="Load", command=self.load_configuration)
        self.load_button.grid(row=0, column=1)
        
        self.reset_button = Button(self.button_frame, text="Reset", command=self.reset_configuration)
        self.reset_button.grid(row=0, column=2)

    def add_button(self, type1, type2, row, col, width, height):
        if type1 not in self.base_types or type2 not in self.base_types:
            initial_val = self.effectiveness_dict.get((type1, type2), '?')
        else:
            initial_val = self.effectiveness_dict.get((type1, type2), 1.0)
        initial_color = self.effectiveness_color[initial_val]
        initial_text = self.effectiveness_display[initial_val]
        button = tk.Button(self.grid_frame, text=initial_text, bg=initial_color, width=width, height=height,
                           command=lambda r=row, c=col, t1=type1, t2=type2: self.update_button(r, c, t1, t2)) 
        button.grid(row=row, column=col, sticky=N+S+E+W)
        self.grid[(row, col)] = button

    def update_button(self, row, col, type1, type2):
        current_val = self.effectiveness_dict.get((type1, type2), 0.0)
        next_index = (self.effectiveness.index(current_val) + 1) % len(self.effectiveness)
        next_val = self.effectiveness[next_index]
        next_color = self.effectiveness_color[next_val]
        next_text = self.effectiveness_display[next_val]
        self.grid[(row, col)].config(text=next_text, bg=next_color)
        self.effectiveness_dict[(type1, type2)] = next_val

    def add_type_entry(self):
        self.entry = tk.Entry(self.grid_frame)
        self.entry.grid(row=0, column=0, columnspan=len(self.types))
        self.entry.insert(0, "Enter new type")
        self.entry.bind("<Return>", self.add_new_type)
        self.entry.bind("<FocusIn>", lambda e: self.entry.select_range(0, tk.END))

    def add_new_type(self, event):
        new_type = self.entry.get()
        if new_type not in self.types:
            self.types.append(new_type)
            self.refresh_grid()
            self.update_dropdown_options()

    def remove_type(self, poke_type):
        answer = messagebox.askyesno("Remove Type", f"Do you want to remove {poke_type}?")
        if answer:
            self.types.remove(poke_type)
            self.effectiveness_dict = {(t1, t2): val for (t1, t2), val in self.effectiveness_dict.items() if
                                       t1 != poke_type and t2 != poke_type}
            self.refresh_grid()

    def refresh_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        for widget in self.calculator_frame.winfo_children():
            widget.destroy()
            
        self.grid = {}
        self.type_option_menus = []
        self.multiplier_labels = {}
        
        # Re-initialize the grid and calculator
        self.initialize_grid()
        self.initialize_calculator()
    
    def calculate_effectiveness(self):
        selected_types = [var.get() for var in self.type_vars if var.get() != 'None']
        
        if not selected_types:
            return
        
        effectiveness_counter = Counter()
        for attack_type in self.types:
            multiplier = 1.0
            for defense_type in selected_types:
                current_effectiveness = self.effectiveness_dict.get((attack_type, defense_type), '?')
                if current_effectiveness == '?':
                    multiplier = '?'
                    break
                multiplier *= current_effectiveness
            
            effectiveness_counter[multiplier] = effectiveness_counter.get(multiplier, '') + f"{attack_type}, "
        
        # Update the labels
        for multiplier, label in self.multiplier_labels.items():
            label.config(text=effectiveness_counter.get(multiplier, '')[:-2])  

    def update_dropdown_options(self):
        for i, (var, option_menu) in enumerate(zip(self.type_vars, self.type_option_menus)):
            var.set('None')
            menu = option_menu['menu']
            menu.delete(0, 'end')
            for option in ['None'] + self.types:
                menu.add_command(label=option, command=lambda value=option, var=var: var.set(value))

    def type_selected(self, *_):
        self.calculate_effectiveness()
        
    def initialize_multiplier_labels(self):
        possible_multipliers = [8, 4, 2, 1, 0.5, 0.25, 0.125, 0, '?']
        multiplier_to_label = {
            8: "8",
            4: "4",
            2: "2",
            1: "1",
            0.5: "½",
            0.25: "¼",
            0.125: "⅛",
            0: "0",
            '?': "?"
        }
        row_start = 6
        
        # Configure the width of the columns
        self.calculator_frame.grid_columnconfigure(0, weight=1)
        self.calculator_frame.grid_columnconfigure(1, weight=3)
        
        separator = ttk.Separator(self.calculator_frame, orient='horizontal')
        separator.grid(row=row_start - 1, column=0, columnspan=3, sticky='ew')

        for i, multiplier in enumerate(possible_multipliers):
            label = tk.Label(self.calculator_frame, text=f"{multiplier_to_label[multiplier]}:", width=2, anchor=W)
            label.grid(row=row_start + (2*i), column=0, sticky=W, padx=0)   

            value_label = tk.Label(self.calculator_frame, text='', height=5, wraplength=200, anchor=W)
            value_label.grid(row=row_start + (2*i), column=1, sticky=W+E, padx=0)
            
            self.multiplier_labels[multiplier] = value_label

            separator = ttk.Separator(self.calculator_frame, orient='horizontal')
            separator.grid(row=row_start + (2*i + 1), column=0, columnspan=3, sticky='ew')

    def save_configuration(self):
        with open("pokemon_type_config.json", "w") as f:
            json_dict = {str(k): v for k, v in self.effectiveness_dict.items()}
            json.dump(json_dict, f)
            
    def load_configuration(self):
        try:
            with open('pokemon_type_config.json', 'r') as f:
                json_dict = json.load(f)
                self.effectiveness_dict = {ast.literal_eval(k): v for k, v in json_dict.items()}
                
                for type_tuple in self.effectiveness_dict.keys():
                    for poke_type in type_tuple:
                        if poke_type not in self.types:
                            self.types.append(poke_type)
                            
                # for type1 in self.base_types:
                #     for type2 in self.base_types:
                #         if (type1, type2) not in self.effectiveness_dict.keys():
                #             self.effectiveness_dict[(type1, type2)] = 1.0
                        
            self.refresh_grid()
        except FileNotFoundError:
            print("No configuration file found.")
            
    def reset_configuration(self):
        answer = messagebox.askyesno("Reset Configuration", "Are you sure you want to reset the configuration?")
        if answer:
            try:
                with open('base_pokemon_type_config.json', 'r') as f:
                    json_dict = json.load(f)
                    self.effectiveness_dict = {ast.literal_eval(k): v for k, v in json_dict.items()}
                    
                    self.types = self.base_types.copy()
                    self.refresh_grid()
            except FileNotFoundError:
                print("No base configuration file found.")
            
    
if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonTypeGrid(root)
    root.mainloop()
