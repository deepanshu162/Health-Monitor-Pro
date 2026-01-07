import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from auth_module import AuthModule
from bp_module import BPModule
from bs_module import BSModule
from predict_module import PredictModule
from PIL import Image, ImageTk
import os
import base64
from io import BytesIO
import io
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

class HealthMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Monitor Pro")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)
        
        # Database connection
        self.conn = sqlite3.connect('health_monitor.db')
        self.create_tables()
        
        # Initialize modules
        self.auth_module = AuthModule(self.conn, self.on_login_success)
        self.bp_module = BPModule(self.conn)
        self.bs_module = BSModule(self.conn)
        self.predict_module = PredictModule(self.conn)
        
        # Configure styles
        self.configure_styles()
        
        # Start with login screen
        self.auth_module.show_login(self.root)
    
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bp_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                systolic INTEGER NOT NULL,
                diastolic INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bs_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                glucose_level INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()
    
    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color scheme
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.accent_color = "#e74c3c"
        self.dark_color = "#2c3e50"
        self.light_color = "#ecf0f1"
        self.text_color = "#333333"
        
        # Base styling
        self.root.configure(bg=self.light_color)
        self.style.configure('.', background=self.light_color, foreground=self.text_color, font=('Arial', 10))
        
        # Configure all component styles
        self.configure_auth_styles()
        self.configure_header_styles()
        self.configure_card_styles()
        self.configure_form_styles()
        self.configure_button_styles()
        self.configure_treeview_styles()
        self.configure_notebook_styles()
    
    def configure_auth_styles(self):
        self.style.configure('Auth.TFrame', background="#ffffff", borderwidth=2, relief=tk.RIDGE, padding=20)
        self.style.configure('AuthTitle.TLabel', font=('Arial', 18, 'bold'), foreground=self.dark_color, background="#ffffff")
        self.style.configure('AuthLabel.TLabel', font=('Arial', 10), foreground="#7f8c8d", background="#ffffff")
        self.style.configure('Auth.TEntry', fieldbackground="#f5f5f5", padding=5, relief=tk.FLAT)
        self.style.configure('AuthFooter.TLabel', font=('Arial', 9, 'italic'), foreground="#95a5a6", background="#ffffff")
    
    def configure_header_styles(self):
        self.style.configure('Header.TFrame', background=self.dark_color)
        self.style.configure('Header.TButton', font=('Arial', 9), padding=5, background=self.dark_color, foreground="white", borderwidth=0)
        self.style.map('Header.TButton', background=[('active', '#34495e'), ('pressed', '#2c3e50')])
        self.style.configure('HeaderTitle.TLabel', font=('Arial', 12, 'bold'), foreground="white", background=self.dark_color)
    
    def configure_card_styles(self):
        self.style.configure('Card.TFrame', background="#ffffff", borderwidth=1, relief=tk.RIDGE, padding=15)
        self.style.configure('CardTitle.TLabel', font=('Arial', 14, 'bold'), foreground=self.dark_color)
        self.style.configure('CardText.TLabel', font=('Arial', 10), foreground="#7f8c8d")
    
    def configure_form_styles(self):
        self.style.configure('FormLabel.TLabel', font=('Arial', 9), foreground="#7f8c8d")
        self.style.configure('Form.TEntry', fieldbackground="#f5f5f5", padding=5, relief=tk.FLAT)
        self.style.configure('Form.TCombobox', fieldbackground="#f5f5f5", padding=5, relief=tk.FLAT)
    
    def configure_button_styles(self):
        self.style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=8, 
                           background=self.primary_color, foreground="white", borderwidth=0)
        self.style.map('Primary.TButton', background=[('active', '#2980b9'), ('pressed', '#1a5276')])
        
        self.style.configure('Secondary.TButton', font=('Arial', 10), padding=8, 
                           background="#bdc3c7", foreground=self.text_color, borderwidth=0)
        self.style.map('Secondary.TButton', background=[('active', '#95a5a6'), ('pressed', '#7f8c8d')])
        
        self.style.configure('Accent.TButton', font=('Arial', 10, 'bold'), padding=8, 
                           background=self.accent_color, foreground="white", borderwidth=0)
        self.style.map('Accent.TButton', background=[('active', '#c0392b'), ('pressed', '#922b21')])
    
    def configure_treeview_styles(self):
        self.style.configure('Custom.Treeview', font=('Arial', 9), rowheight=28, 
                           background="#ffffff", fieldbackground="#ffffff", foreground=self.text_color, borderwidth=0)
        self.style.configure('Custom.Treeview.Heading', font=('Arial', 9, 'bold'), 
                           background=self.dark_color, foreground="white", padding=5, relief=tk.FLAT)
        self.style.map('Custom.Treeview', background=[('selected', '#3498db')], foreground=[('selected', 'white')])
    
    def configure_notebook_styles(self):
        self.style.configure('TNotebook', background=self.light_color)
        self.style.configure('TNotebook.Tab', background="#bdc3c7", padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', self.primary_color)], foreground=[('selected', 'white')])
    
    def on_login_success(self, user):
        self.current_user = user
        self.show_main_menu()
    
    def show_main_menu(self):
        self.clear_window()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header(main_frame)
        self.create_content_area(main_frame)
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_header(self, parent):
        header_frame = ttk.Frame(parent, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, 
                 text=f"Welcome, {self.current_user['full_name'] or self.current_user['username']}",
                 style='HeaderTitle.TLabel').pack(side=tk.LEFT, padx=10)
        
        ttk.Button(header_frame, text="Health Summary", style='Header.TButton',
                  command=self.show_health_summary).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="Profile", style='Header.TButton',
                  command=self.show_profile).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="Logout", style='Header.TButton',
                  command=self.logout).pack(side=tk.RIGHT, padx=5)
    
    def create_content_area(self, parent):
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(content_frame, 
                 text="HEALTH MONITORING DASHBOARD",
                 style='AuthTitle.TLabel').pack(pady=(0, 30))
        
        menu_frame = ttk.Frame(content_frame)
        menu_frame.pack(expand=True)
        
        self.create_bp_card(menu_frame)
        self.create_bs_card(menu_frame)
        
        menu_frame.grid_columnconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(content_frame, 
                 text="Track your health metrics for better living",
                 style='AuthFooter.TLabel').pack(side=tk.BOTTOM, pady=20)
    
    def create_bp_card(self, parent):
        bp_frame = ttk.Frame(parent, style='Card.TFrame')
        bp_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(bp_frame, 
                 text="Blood Pressure",
                 style='CardTitle.TLabel').pack(pady=(5, 5))
        
        ttk.Label(bp_frame, 
                 text="Track your systolic and diastolic pressure",
                 style='CardText.TLabel').pack(pady=(0, 20))
        
        btn_frame = ttk.Frame(bp_frame)
        btn_frame.pack(pady=(0, 5))
        
        ttk.Button(btn_frame, text="Record", style='Primary.TButton',
                  command=lambda: self.bp_module.show_interface(
                      self.root, self.current_user, self.show_main_menu)
                  ).pack(side=tk.LEFT, padx=5, ipadx=15)
        
        ttk.Button(btn_frame, text="History", style='Secondary.TButton',
                  command=lambda: self.show_bp_history()).pack(side=tk.LEFT, padx=5, ipadx=15)
        
        ttk.Button(btn_frame, text="Predict", style='Accent.TButton',
                  command=self.show_bp_predictions).pack(side=tk.LEFT, padx=5, ipadx=15)
    
    def create_bs_card(self, parent):
        bs_frame = ttk.Frame(parent, style='Card.TFrame')
        bs_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(bs_frame, 
                 text="Blood Sugar",
                 style='CardTitle.TLabel').pack(pady=(5, 5))
        
        ttk.Label(bs_frame, 
                 text="Monitor your glucose levels",
                 style='CardText.TLabel').pack(pady=(0, 20))
        
        btn_frame = ttk.Frame(bs_frame)
        btn_frame.pack(pady=(0, 5))
        
        ttk.Button(btn_frame, text="Record", style='Primary.TButton',
                  command=lambda: self.bs_module.show_interface(
                      self.root, self.current_user, self.show_main_menu)
                  ).pack(side=tk.LEFT, padx=5, ipadx=15)
        
        ttk.Button(btn_frame, text="History", style='Secondary.TButton',
                  command=lambda: self.show_bs_history()).pack(side=tk.LEFT, padx=5, ipadx=15)
        
        ttk.Button(btn_frame, text="Predict", style='Accent.TButton',
                  command=self.show_bs_predictions).pack(side=tk.LEFT, padx=5, ipadx=15)
    
    def show_bp_history(self):
        self.show_reading_history("bp_readings", "Blood Pressure History", 
                                ["Date", "Time", "Systolic", "Diastolic"],
                                ["date", "time", "systolic", "diastolic"])
    
    def show_bs_history(self):
        self.show_reading_history("bs_readings", "Blood Sugar History", 
                                ["Date", "Time", "Glucose Level"],
                                ["date", "time", "glucose_level"])
    
    def show_reading_history(self, table_name, title, columns, db_columns):
        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT {", ".join(db_columns)} 
            FROM {table_name} 
            WHERE user_id = ? 
            ORDER BY date DESC, time DESC
        ''', (self.current_user['id'],))
        
        records = cursor.fetchall()
        
        history_window = tk.Toplevel(self.root)
        history_window.title(title)
        history_window.geometry("800x500")
        
        ttk.Label(history_window, text=title, style='AuthTitle.TLabel').pack(pady=10)
        
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Custom.Treeview')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        
        for record in records:
            tree.insert('', tk.END, values=record)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Close", style='Secondary.TButton',
                  command=history_window.destroy).pack()
    
    def show_bp_predictions(self):
        result = self.predict_module.predict_bp(self.current_user['id'], include_visualization=True)
        
        if not result:
            messagebox.showinfo("Info", "Not enough data to make predictions. Please record at least 3 readings.")
            return
            
        predictions, img_data = result
        
        self.create_prediction_window(
            "Blood Pressure Predictions",
            "7-Day Blood Pressure Forecast",
            [('date', 'Date', 150), ('systolic', 'Systolic (mmHg)', 150), ('diastolic', 'Diastolic (mmHg)', 150)],
            predictions,
            img_data
        )
    
    def show_bs_predictions(self):
        result = self.predict_module.predict_bs(self.current_user['id'], include_visualization=True)
        
        if not result:
            messagebox.showinfo("Info", "Not enough data to make predictions. Please record at least 3 readings.")
            return
            
        predictions, img_data = result
        
        self.create_prediction_window(
            "Blood Sugar Predictions",
            "7-Day Blood Sugar Forecast",
            [('date', 'Date', 200), ('glucose', 'Glucose (mg/dL)', 200)],
            predictions,
            img_data
        )
    
    def create_prediction_window(self, title, heading, columns, data, img_data=None):
        pred_window = tk.Toplevel(self.root)
        pred_window.title(title)
        pred_window.geometry("800x600")
        
        ttk.Label(pred_window, text=heading, style='AuthTitle.TLabel').pack(pady=10)
        
        # Create notebook for different views
        notebook = ttk.Notebook(pred_window, style='TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Table view tab
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="Table View")
        
        tree = ttk.Treeview(table_frame, columns=[col[0] for col in columns], show='headings', style='Custom.Treeview')
        
        for col_id, col_text, col_width in columns:
            tree.heading(col_id, text=col_text)
            tree.column(col_id, width=col_width, anchor='center')
        
        for pred in data:
            tree.insert('', tk.END, values=tuple(pred[col[0]] for col in columns))
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Graph view tab
        graph_frame = ttk.Frame(notebook)
        notebook.add(graph_frame, text="Graph View")
        
        if img_data:
            img_bytes = base64.b64decode(img_data)
            img = Image.open(BytesIO(img_bytes))
            img = img.resize((700, 400), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = ttk.Label(graph_frame, image=photo)
            img_label.image = photo  # Keep reference
            img_label.pack(expand=True)
        else:
            ttk.Label(graph_frame, text="No visualization available", style='AuthTitle.TLabel').pack(expand=True)
        
        btn_frame = ttk.Frame(pred_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Close", style='Secondary.TButton',
                  command=pred_window.destroy).pack()
    
    def show_health_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Health Summary")
        summary_window.geometry("900x600")
        
        # Create notebook for different sections
        notebook = ttk.Notebook(summary_window, style='TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # BP Summary tab
        bp_frame = ttk.Frame(notebook)
        notebook.add(bp_frame, text="Blood Pressure")
        
        # Get latest BP reading
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT systolic, diastolic, date, time 
            FROM bp_readings 
            WHERE user_id = ? 
            ORDER BY date DESC, time DESC 
            LIMIT 1
        ''', (self.current_user['id'],))
        bp_data = cursor.fetchone()
        
        if bp_data:
            systolic, diastolic, date, time = bp_data
            bp_status = self.get_bp_status(systolic, diastolic)
            
            ttk.Label(bp_frame, text=f"Latest Reading: {date} {time}", style='CardTitle.TLabel').pack(pady=10)
            
            # Create card for BP status
            status_frame = ttk.Frame(bp_frame, style='Card.TFrame')
            status_frame.pack(fill=tk.X, padx=50, pady=10)
            
            ttk.Label(status_frame, text="Blood Pressure Status", style='CardTitle.TLabel').pack()
            ttk.Label(status_frame, text=f"{systolic}/{diastolic} mmHg", 
                     font=('Arial', 24, 'bold')).pack(pady=5)
            ttk.Label(status_frame, text=bp_status, 
                     font=('Arial', 12)).pack(pady=5)
            
            # Add BP trends button
            ttk.Button(bp_frame, text="View Trends", style='Primary.TButton',
                      command=self.show_bp_trends).pack(pady=10)
        else:
            ttk.Label(bp_frame, text="No blood pressure readings recorded yet", style='CardText.TLabel').pack(pady=50)
        
        # BS Summary tab
        bs_frame = ttk.Frame(notebook)
        notebook.add(bs_frame, text="Blood Sugar")
        
        # Get latest BS reading
        cursor.execute('''
            SELECT glucose_level, date, time 
            FROM bs_readings 
            WHERE user_id = ? 
            ORDER BY date DESC, time DESC 
            LIMIT 1
        ''', (self.current_user['id'],))
        bs_data = cursor.fetchone()
        
        if bs_data:
            glucose, date, time = bs_data
            bs_status = self.get_bs_status(glucose)
            
            ttk.Label(bs_frame, text=f"Latest Reading: {date} {time}", style='CardTitle.TLabel').pack(pady=10)
            
            # Create card for BS status
            status_frame = ttk.Frame(bs_frame, style='Card.TFrame')
            status_frame.pack(fill=tk.X, padx=50, pady=10)
            
            ttk.Label(status_frame, text="Blood Sugar Status", style='CardTitle.TLabel').pack()
            ttk.Label(status_frame, text=f"{glucose} mg/dL", 
                     font=('Arial', 24, 'bold')).pack(pady=5)
            ttk.Label(status_frame, text=bs_status, 
                     font=('Arial', 12)).pack(pady=5)
            
            # Add BS trends button
            ttk.Button(bs_frame, text="View Trends", style='Primary.TButton',
                      command=self.show_bs_trends).pack(pady=10)
        else:
            ttk.Label(bs_frame, text="No blood sugar readings recorded yet", style='CardText.TLabel').pack(pady=50)
        
        # Close button
        btn_frame = ttk.Frame(summary_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Close", style='Secondary.TButton',
                  command=summary_window.destroy).pack()
    
    def get_bp_status(self, systolic, diastolic):
        if systolic < 90 or diastolic < 60:
            return "Low Blood Pressure"
        elif systolic < 120 and diastolic < 80:
            return "Normal"
        elif systolic < 130 and diastolic < 80:
            return "Elevated"
        elif systolic < 140 or diastolic < 90:
            return "Hypertension Stage 1"
        else:
            return "Hypertension Stage 2"
    
    def get_bs_status(self, glucose):
        if glucose < 70:
            return "Low (Hypoglycemia)"
        elif glucose < 100:
            return "Normal (Fasting)"
        elif glucose < 126:
            return "Prediabetes Range"
        else:
            return "Diabetes Range"
    
    def show_bp_trends(self):
        data = self.predict_module.prepare_bp_data(self.current_user['id'])
        if data is None or len(data) < 3:
            messagebox.showinfo("Info", "Not enough data to show trends. Please record at least 3 readings.")
            return
        
        last_day = data['days_since_first'].max()
        future_days = pd.DataFrame(range(last_day + 1, last_day + 8), columns=['days_since_first'])
        
        model_sys = LinearRegression()
        model_dia = LinearRegression()
        model_sys.fit(data[['days_since_first']], data['systolic'])
        model_dia.fit(data[['days_since_first']], data['diastolic'])
        
        sys_pred = model_sys.predict(future_days)
        dia_pred = model_dia.predict(future_days)
        
        img_data = self._generate_bp_visualization(data, future_days, sys_pred, dia_pred)
        self._show_trend_window("Blood Pressure Trends", img_data)

    def show_bs_trends(self):
        data = self.predict_module.prepare_bs_data(self.current_user['id'])
        if data is None or len(data) < 3:
            messagebox.showinfo("Info", "Not enough data to show trends. Please record at least 3 readings.")
            return
        
        last_day = data['days_since_first'].max()
        future_days = pd.DataFrame(range(last_day + 1, last_day + 8), columns=['days_since_first'])
        
        model = LinearRegression()
        model.fit(data[['days_since_first']], data['glucose'])
        pred = model.predict(future_days)
        
        img_data = self._generate_bs_visualization(data, future_days, pred)
        self._show_trend_window("Blood Sugar Trends", img_data)

    def _generate_bp_visualization(self, historical_data, future_days, sys_pred, dia_pred):
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(historical_data['datetime'], historical_data['systolic'], 
                'b-o', label='Historical Systolic')
        plt.plot(historical_data['datetime'], historical_data['diastolic'], 
                'g-o', label='Historical Diastolic')
        
        # Prepare future dates
        last_date = historical_data['datetime'].max()
        future_dates = [last_date + timedelta(days=int(days-historical_data['days_since_first'].max())) 
                       for days in future_days['days_since_first']]
        
        # Plot predictions
        plt.plot(future_dates, sys_pred, 'b--o', label='Predicted Systolic')
        plt.plot(future_dates, dia_pred, 'g--o', label='Predicted Diastolic')
        
        # Formatting
        plt.title('Blood Pressure Trend and Prediction')
        plt.xlabel('Date')
        plt.ylabel('Blood Pressure (mmHg)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _generate_bs_visualization(self, historical_data, future_days, pred):
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(historical_data['datetime'], historical_data['glucose'], 
                'r-o', label='Historical Glucose')
        
        # Prepare future dates
        last_date = historical_data['datetime'].max()
        future_dates = [last_date + timedelta(days=int(days-historical_data['days_since_first'].max())) 
                       for days in future_days['days_since_first']]
        
        # Plot predictions
        plt.plot(future_dates, pred, 'r--o', label='Predicted Glucose')
        
        # Formatting
        plt.title('Blood Sugar Trend and Prediction')
        plt.xlabel('Date')
        plt.ylabel('Glucose Level (mg/dL)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _fig_to_base64(self):
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return base64.b64encode(img.getvalue()).decode('utf-8')

    def _show_trend_window(self, title, img_data):
        trend_window = tk.Toplevel(self.root)
        trend_window.title(title)
        trend_window.geometry("800x500")
        
        ttk.Label(trend_window, text=title, style='AuthTitle.TLabel').pack(pady=10)
        
        if img_data:
            img_bytes = base64.b64decode(img_data)
            img = Image.open(BytesIO(img_bytes))
            img = img.resize((700, 400), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = ttk.Label(trend_window, image=photo)
            img_label.image = photo
            img_label.pack(expand=True)
        else:
            ttk.Label(trend_window, text="No visualization available", style='AuthTitle.TLabel').pack(expand=True)
        
        btn_frame = ttk.Frame(trend_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Close", style='Secondary.TButton',
                  command=trend_window.destroy).pack()
    
    def show_profile(self):
        self.clear_window()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(header_frame, text="← Back", style='Header.TButton',
                  command=self.show_main_menu).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, 
                 text="USER PROFILE",
                 style='HeaderTitle.TLabel').pack(side=tk.LEFT, padx=10, expand=True)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Profile card
        profile_frame = ttk.Frame(content_frame, style='Card.TFrame')
        profile_frame.pack(fill=tk.X, pady=10, padx=50)
        
        # Get full user data from database
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (self.current_user['id'],))
        user_data = cursor.fetchone()
        
        if user_data:
            # Display user information
            fields = [
                ("Username", user_data[1]),
                ("Full Name", user_data[3] or "Not provided"),
                ("Age", user_data[4] or "Not provided"),
                ("Gender", user_data[5] or "Not provided"),
                ("Diabetes Type", user_data[6] or "Not provided")
            ]
            
            for i, (label, value) in enumerate(fields):
                row_frame = ttk.Frame(profile_frame)
                row_frame.pack(fill=tk.X, padx=20, pady=10)
                
                ttk.Label(row_frame, text=label + ":", 
                         style='AuthLabel.TLabel', width=15, anchor='e').pack(side=tk.LEFT)
                ttk.Label(row_frame, text=value,
                         style='AuthTitle.TLabel', anchor='w').pack(side=tk.LEFT, padx=10)
        
        # Edit button
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Edit Profile", style='Primary.TButton',
                  command=self.edit_profile).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Change Password", style='Secondary.TButton',
                  command=self.change_password).pack(side=tk.LEFT, padx=5)
    
    def edit_profile(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")
        edit_window.geometry("500x400")
        
        # Get current user data
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (self.current_user['id'],))
        user_data = cursor.fetchone()
        
        # Form fields
        fields = [
            ("Full Name", "full_name", user_data[3] or ""),
            ("Age", "age", user_data[4] or ""),
            ("Gender", "gender", user_data[5] or "", ["Male", "Female", "Other", "Prefer not to say"]),
            ("Diabetes Type", "diabetes_type", user_data[6] or "", 
             ["Type 1", "Type 2", "Prediabetes", "Gestational", "None", "Other"])
        ]
        
        self.edit_vars = {}
        for i, (label, field, default, *options) in enumerate(fields):
            row_frame = ttk.Frame(edit_window)
            row_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Label(row_frame, text=label, style='FormLabel.TLabel', width=15).pack(side=tk.LEFT)
            
            if options:
                var = ttk.Combobox(row_frame, values=options[0], style='Form.TCombobox')
                var.set(default)
            else:
                var = ttk.Entry(row_frame, style='Form.TEntry')
                var.insert(0, default)
            
            var.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.edit_vars[field] = var
        
        # Save button
        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Save Changes", style='Primary.TButton',
                  command=lambda: self.save_profile(edit_window)).pack(side=tk.LEFT, padx=5)
    
    def save_profile(self, window):
        try:
            full_name = self.edit_vars['full_name'].get()
            age = self.edit_vars['age'].get()
            gender = self.edit_vars['gender'].get()
            diabetes_type = self.edit_vars['diabetes_type'].get()
            
            age = int(age) if age else None
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, age = ?, gender = ?, diabetes_type = ?
                WHERE id = ?
            ''', (full_name, age, gender, diabetes_type, self.current_user['id']))
            self.conn.commit()
            
            # Update current user data
            self.current_user['full_name'] = full_name
            
            window.destroy()
            self.show_profile()
            messagebox.showinfo("Success", "Profile updated successfully")
        except ValueError:
            messagebox.showerror("Error", "Age must be a number")
    
    def change_password(self):
        pass_window = tk.Toplevel(self.root)
        pass_window.title("Change Password")
        pass_window.geometry("400x300")
        
        # Current password
        current_frame = ttk.Frame(pass_window)
        current_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(current_frame, text="Current Password:", style='FormLabel.TLabel').pack(anchor="w")
        self.current_pass_entry = ttk.Entry(current_frame, style='Form.TEntry', show="•")
        self.current_pass_entry.pack(fill=tk.X)
        
        # New password
        new_frame = ttk.Frame(pass_window)
        new_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(new_frame, text="New Password:", style='FormLabel.TLabel').pack(anchor="w")
        self.new_pass_entry = ttk.Entry(new_frame, style='Form.TEntry', show="•")
        self.new_pass_entry.pack(fill=tk.X)
        
        # Confirm new password
        confirm_frame = ttk.Frame(pass_window)
        confirm_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(confirm_frame, text="Confirm New Password:", style='FormLabel.TLabel').pack(anchor="w")
        self.confirm_pass_entry = ttk.Entry(confirm_frame, style='Form.TEntry', show="•")
        self.confirm_pass_entry.pack(fill=tk.X)
        
        # Button
        btn_frame = ttk.Frame(pass_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Change Password", style='Primary.TButton',
                  command=lambda: self.update_password(pass_window)).pack()
    
    def update_password(self, window):
        current_pass = self.current_pass_entry.get()
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        
        if not current_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords don't match")
            return
        
        # Verify current password
        cursor = self.conn.cursor()
        cursor.execute('SELECT password FROM users WHERE id = ?', (self.current_user['id'],))
        db_password = cursor.fetchone()[0]
        
        hashed_current = self.auth_module.hash_password(current_pass)
        if hashed_current != db_password:
            messagebox.showerror("Error", "Current password is incorrect")
            return
        
        # Update password
        hashed_new = self.auth_module.hash_password(new_pass)
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', 
                      (hashed_new, self.current_user['id']))
        self.conn.commit()
        
        messagebox.showinfo("Success", "Password changed successfully")
        window.destroy()
    
    def logout(self):
        self.current_user = None
        self.auth_module.show_login(self.root)

if __name__ == '__main__':
    root = tk.Tk()
    
    try:
        img = Image.open("assets/app_icon.png")
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(False, photo)
    except:
        pass
    
    app = HealthMonitorApp(root)
    root.mainloop()

