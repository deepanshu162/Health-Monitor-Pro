import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from PIL import Image, ImageTk
import os

class AuthModule:
    def __init__(self, db_conn, on_login_success):
        self.conn = db_conn
        self.on_login_success = on_login_success
        self.create_tables()
        self.load_images()
        
    def load_images(self):
        try:
            self.logo_img = Image.open("assets/health_logo.png").resize((120, 120))
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            
            self.bg_img = Image.open("assets/auth_bg.jpg").resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_img)
        except:
            # Fallback if images not found
            self.logo_photo = None
            self.bg_photo = None
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                age INTEGER,
                gender TEXT,
                diabetes_type TEXT
            )
        ''')
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def show_login(self, parent):
        self.parent = parent
        for widget in parent.winfo_children():
            widget.destroy()

        # Background frame
        if self.bg_photo:
            bg_label = tk.Label(parent, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        container = ttk.Frame(parent, style='Auth.TFrame')
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        if self.logo_photo:
            logo_label = tk.Label(container, image=self.logo_photo, bg="#ffffff")
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(container, text="HEALTH MONITOR", style='AuthTitle.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username field
        username_frame = ttk.Frame(container)
        username_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        ttk.Label(username_frame, text="Username", style='AuthLabel.TLabel').pack(side=tk.TOP, anchor="w")
        self.username_entry = ttk.Entry(username_frame, style='Auth.TEntry')
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Password field
        password_frame = ttk.Frame(container)
        password_frame.grid(row=3, column=0, columnspan=2, pady=(0, 25), sticky="ew")
        ttk.Label(password_frame, text="Password", style='AuthLabel.TLabel').pack(side=tk.TOP, anchor="w")
        self.password_entry = ttk.Entry(password_frame, style='Auth.TEntry', show="•")
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Login", style='Auth.TButton', 
                  command=self.login).pack(side=tk.LEFT, padx=5, ipadx=20)
        ttk.Button(btn_frame, text="Register", style='AuthSecondary.TButton',
                  command=lambda: self.show_registration(parent)).pack(side=tk.LEFT, padx=5, ipadx=20)

        # Footer
        ttk.Label(container, text="Track your health metrics", style='AuthFooter.TLabel').grid(
            row=5, column=0, columnspan=2, pady=(20, 0))

    def show_registration(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        # Background frame
        if self.bg_photo:
            bg_label = tk.Label(parent, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        container = ttk.Frame(parent, style='Auth.TFrame')
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        if self.logo_photo:
            logo_label = tk.Label(container, image=self.logo_photo, bg="#ffffff")
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        ttk.Label(container, text="CREATE ACCOUNT", style='AuthTitle.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Registration fields
        fields = [
            ("Username", "reg_username"),
            ("Password", "reg_password", "•"),
            ("Full Name", "reg_fullname"),
            ("Age", "reg_age"),
            ("Gender", "reg_gender", ["Male", "Female", "Other", "Prefer not to say"]),
            ("Diabetes Type", "reg_diabetes_type", ["Type 1", "Type 2", "Prediabetes", "Gestational", "None", "Other"])
        ]

        self.reg_vars = {}
        for i, field in enumerate(fields, 2):
            field_frame = ttk.Frame(container)
            field_frame.grid(row=i, column=0, columnspan=2, pady=(0, 10), sticky="ew")
            
            ttk.Label(field_frame, text=field[0], style='AuthLabel.TLabel').pack(side=tk.TOP, anchor="w")
            
            if len(field) == 2:
                var = ttk.Entry(field_frame, style='Auth.TEntry')
                self.reg_vars[field[1]] = var
            else:
                if isinstance(field[2], list):
                    var = ttk.Combobox(field_frame, values=field[2], style='Auth.TCombobox')
                else:
                    var = ttk.Entry(field_frame, style='Auth.TEntry', show=field[2])
                self.reg_vars[field[1]] = var
            var.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Register", style='Auth.TButton',
                  command=self.register_user).pack(side=tk.LEFT, padx=5, ipadx=20)
        ttk.Button(btn_frame, text="Back to Login", style='AuthSecondary.TButton',
                  command=lambda: self.show_login(parent)).pack(side=tk.LEFT, padx=5, ipadx=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        hashed_password = self.hash_password(password)
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username, full_name FROM users WHERE username = ? AND password = ?', 
                      (username, hashed_password))
        
        user = cursor.fetchone()
        
        if user:
            self.on_login_success({
                'id': user[0],
                'username': user[1],
                'full_name': user[2]
            })
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register_user(self):
        username = self.reg_vars['reg_username'].get()
        password = self.reg_vars['reg_password'].get()
        full_name = self.reg_vars['reg_fullname'].get()
        age = self.reg_vars['reg_age'].get()
        gender = self.reg_vars['reg_gender'].get()
        diabetes_type = self.reg_vars['reg_diabetes_type'].get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            age = int(age) if age else None
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
            return
        
        hashed_password = self.hash_password(password)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, full_name, age, gender, diabetes_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, age, gender, diabetes_type))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_login(self.parent)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")