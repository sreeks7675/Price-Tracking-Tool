'''
This is a Price-Tracking Tool implementation with the user end and the admin end, with their associated terminals.
The user has to register in case his/her credentials are not already stored in the users.json file, while they can directly login
if it is already validated. 

DISCLAIMER: To login as admin; use the following username and password:
username:admin
password:admin_password

There is only one admin as of now, and the role played by the admin is in the update of the prices. The admin receives a singleton sequence of
all product names and prices added by various users, and the admin performs the task of price tracking by changing the price of a given product,
based on scaled down version of web scraping from Amazon UI. Once the product price of a given product of a given user (identified by a distinct observer_id),
is updated, the user is notified and the record is removed from the admin view.
The main objective of the tool is when the user wishes to purchase an item and, it is added to this portal, it notifies the user on receiving a
updated price (mostly discounts), and enable better savings for the user.
'''
import tkinter as tk
from tkinter import messagebox
import json
from customtkinter import *
# Backend imports and code

#Strategy pattern implementation using PriceUpdater and Immediate Update
class PriceUpdater:
    # Backend code for PriceUpdater class
    def __init__(self, update_strategy):
        self.update_strategy = update_strategy

    def update_price(self, observer_id,product_name,new_price):
        self.update_strategy.update(observer_id,product_name,new_price)


class ImmediateUpdate:
    # Backend code for ImmediateUpdate class
    def update(self, observer_id,product_name,new_price):
        price_fetcher = PriceFetcher()
        price_fetcher.update_price(observer_id, product_name, new_price)

#Observer pattern implementation - PriceTracker_observer()
from abc import ABC, abstractmethod
import random

class Observer(ABC):
    @abstractmethod
    def update(self, price):
        pass

# Backend code for PriceTracker_observer class
class PriceTracker_observer(Observer):
    def __init__(self, product_name,price):
        self.product_name = product_name
        self.observer_id=random.randint(1,1000)
        self.price=price

    def update(self,price):
        print(f"{self.observer_id}:Price for {self.product_name} updated: ${price}")

#Singleton Pattern implementation - PriceFetcher()
class PriceFetcher():
    # Backend code for PriceFetcher class
    _instance = None
    file_path = 'products.json'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.products = {}
            cls._instance._load_data()
        return cls._instance
    
    def _load_data(self): #Serialisation using json
        try:
            with open(self.file_path, 'r') as file:
                self.products = json.load(file)
        except FileNotFoundError:
            self.products = {}
            self._save_data()
    
    def _save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.products, file, indent=4)
    
    def add_product(self, observer_id, product_name, initial_price):
        if observer_id in self.products:
            # If observer exists, update/add the product to its dictionary of products
            self.products[observer_id][product_name] = initial_price
        else:
            # If observer doesn't exist, create a new dictionary for products
            self.products[observer_id] = {product_name: initial_price}
        self._save_data()
        return True
    
    def update_price(self, observer_id, product_name, new_price):
        if observer_id in self.products and product_name in self.products[observer_id]:
            # Update the price if the observer and product exist
            self.products[observer_id][product_name] = new_price
            self._save_data()
            return True
        return False

    def get_price(self, observer_id):
        if observer_id in self.products:
            return self.products[observer_id]  # Return the products associated with the observer_id
        return {}  # Return an empty dictionary if observer_id is not found
    
    def __repr__(self):
        return self.products


# Factory pattern Implementation - Price Tracker Factory(), PriceTracker()
class PriceTrackerFactory():
# Backend code for PriceTrackerFactory class
    def create_price_tracker(self, product_name):
        return PriceTracker(product_name)
    
    def create_price_fetcher(self):
        return PriceFetcher()
    
class PriceTracker():
    def __init__(self, product_name):
        self.product_name = product_name
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self,observer_id, price):
        for observer in self.observers:
            if observer.observer_id==observer_id:
                observer.update(price)

    def update_price(self, observer_id, product_name, new_price):
        immediate_update_strategy = ImmediateUpdate()
        price_updater = PriceUpdater(immediate_update_strategy)
        
        # Update price
        price_updater.update_price(observer_id,product_name, new_price)
        
        # Notify all observers about the update
        self.notify(observer_id,new_price)



# Tkinter frontend code
class ProductManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Management System")
        self.price_tracker_factory = PriceTrackerFactory()
        self.price_fetcher = PriceFetcher()

        self.create_login_ui()
    
    def load_users():
        try:
         with open('users.json', 'r') as file:
            return json.load(file)
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file is not found

# Function to save user data to JSON file
    def save_users(users_data):
        with open('users.json', 'w') as file:
            json.dump(users_data, file, indent=4)

    #Decorator pattern - display_title_at_top
    def display_title_at_top(func):
        def wrapper(self):
            # Create and display the title at the top of the login page
            header_label = tk.Label(self.root, text="Production Management System")
            header_label.pack()

            # Call the original function
            func(self)
        return wrapper

    @display_title_at_top
    def create_login_ui(self):
    
        self.root.geometry("300x200")
        self.username_label = CTkLabel(self.root, text="Username")
        self.username_label.pack()
        self.username_entry = CTkEntry(self.root)
        self.username_entry.pack()

        self.password_label = CTkLabel(self.root, text="Password")
        self.password_label.pack()
        self.password_entry = CTkEntry(self.root, show="*")
        self.password_entry.pack()

        self.login_button = CTkButton(self.root, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = CTkButton(self.root, text="Register", command=self.register)
        self.register_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Backend: Implement logic to validate user credentials
        # For example: Validate the credentials from your user database
        # Replace this with your actual authentication logic
        valid_user = self.validate_user_credentials(username, password)

        if valid_user == 'admin':
            self.show_admin_view()
        elif valid_user:
            self.show_user_view()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

    def load_users(self):
            try:
                with open('users.json', 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                return {}  # Return an empty dictionary if the file is not found

# Function to save user data to JSON file
    def save_users(self,users_data):
        with open('users.json', 'w') as file:
            json.dump(users_data, file, indent=4)

    def validate_user_credentials(self, username, password):
        # Replace this with actual validation against your database
        # For demonstration, assume 'admin' as the admin username and password
        
        global users_data
        users_data=self.load_users()
        if username == 'admin' and password == 'admin_password':
            return 'admin'
        if username in users_data and users_data[username]['password'] == password:
            return True
        if username not in users_data:
            self.register_user(username,password) # Registration successful
        return False 
    
    def register_user(self, username, password):
        # Backend: Implement logic to add a new user to the database
        # For demonstration, let's add the new user to the users_db dictionary
        if username not in users_data:
            users_data[username] = {"password": password}
            self.save_users(users_data)
            messagebox.showinfo("Registration", "Registration successful! You can now login.")
        else:
            messagebox.showerror("Registration Failed", "Username already exists. Please choose another username.")

    def register(self):
        # Backend: Implement logic to register a new user
        # For example: Add the username and password to users_db
        
        new_username = self.username_entry.get()
        new_password = self.password_entry.get()

        # Call register_new_user method from ProductManagementSystem
        self.register_user(new_username, new_password)

        # Clear the entry fields after registration
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


        # For demo, just display a message
        messagebox.showinfo("Registration", "Registration successful! You can now login.")

    def show_user_view(self):
        user_window = CTkToplevel(self.root)
        user_window.title("User Panel")

        self.product_name_label = CTkLabel(user_window, text="Product Name")
        self.product_name_label.pack()
        self.product_name_entry = CTkEntry(user_window)
        self.product_name_entry.pack()

        self.product_price_label = CTkLabel(user_window, text="Product Price")
        self.product_price_label.pack()
        self.product_price_entry = CTkEntry(user_window)
        self.product_price_entry.pack()

        self.add_product_button = CTkButton(user_window, text="Add Product", command=self.add_product)
        self.add_product_button.pack()

    def add_product(self):
        product_name = self.product_name_entry.get()
        product_price = self.product_price_entry.get()

        # Backend: Implement logic to add product using PriceTrackerFactory and PriceFetcher
        observer = PriceTracker_observer(product_name, product_price)  # Change observer_id accordingly
        price_tracker=self.price_tracker_factory.create_price_tracker(product_name)
        price_tracker.attach(observer)
        self.price_fetcher.add_product(observer.observer_id, product_name, product_price)
        messagebox.showinfo("Success", f"Product {product_name} added successfully!")

    def show_admin_view(self):
        admin_window = CTkToplevel(self.root)
        admin_window.title("Admin Panel")

        all_products = self.price_fetcher.__repr__()  # Fetch all Observer-Product pairs

        # Create a Canvas widget
        canvas = CTkCanvas(admin_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = CTkScrollbar(admin_window, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to scroll with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to contain the elements
        frame = CTkFrame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        # Function to update canvas scroll region
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_configure)

        # Display admin header
        header_label = CTkLabel(frame, text="Admin Panel")
        header_label.pack()

        # Display observer-product pairs
        for observer_id, products in all_products.items():
            if isinstance(products, dict):
                for product, price in products.items():
                    product_info_label = CTkLabel(frame, text=f"Observer ID: {observer_id}, Product: {product}, Price: {price}")
                    product_info_label.pack()

        # Display update price section
        self.observer_id_label = CTkLabel(frame, text="Observer ID")
        self.observer_id_label.pack()
        self.observer_id_entry = CTkEntry(frame)
        self.observer_id_entry.pack()

        self.product_name_label = CTkLabel(frame, text="Product Name")
        self.product_name_label.pack()
        self.product_name_entry = CTkEntry(frame)
        self.product_name_entry.pack()

        self.new_price_label = CTkLabel(frame, text="New Price")
        self.new_price_label.pack()
        self.new_price_entry = CTkEntry(frame)
        self.new_price_entry.pack()

        self.update_price_button = CTkButton(frame, text="Update Price", command=self.update_price)
        self.update_price_button.pack()

        admin_window.mainloop()

    def update_price(self):
        observer_id = self.observer_id_entry.get()  # Fetch observer ID from the entry widget
        product_name = self.product_name_entry.get()
        new_price = self.new_price_entry.get()

        print(f"Observer ID: {observer_id}")
        print(f"Product Name: {product_name}")
        print(f"New Price: {new_price}")

        # Backend: Implement logic to update price using PriceTrackerFactory and PriceUpdater
        # Only admin can update prices
        if self.username_entry.get() == "admin":
            user_products = self.price_fetcher.get_price(observer_id)
            if observer_id and product_name in user_products:
                # Update the price
                success = self.price_fetcher.update_price(observer_id, product_name, new_price)
                if success:
                    messagebox.showinfo("Success", f"Price for {product_name} updated successfully!")
                    # Remove the record after updating the price
                    del self.price_fetcher.products[observer_id][product_name]
                    self.price_fetcher._save_data()
                    print(f"Record for {product_name} deleted after update.")
                else:
                    messagebox.showerror("Error", f"Failed to update the price for {product_name}.")
                    print("Failed to update price.")
            else:
                messagebox.showerror("Error", f"Product {product_name} for Observer ID {observer_id} not found.")
                print(f"Product {product_name} not found for Observer ID {observer_id}.")
        else:
            messagebox.showerror("Error", "Only admin can update prices!")
            print("Access denied. Only admin can update prices!")




if __name__ == "__main__":
    root = CTk()
    app = ProductManagementSystem(root)

    root.mainloop()
    print(users_data)