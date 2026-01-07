import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os

class BSModule:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_tables()
        self.load_images()
        
    def load_images(self):
        try:
            self.bs_icon = Image.open("assets/bs_icon.png").resize((30, 30))
            self.bs_icon = ImageTk.PhotoImage(self.bs_icon)
        except:
            self.bs_icon = None
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bs_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                glucose_level INTEGER NOT NULL,
                measurement_type TEXT NOT NULL,
                meal_context TEXT,
                notes TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def show_interface(self, parent, user, on_back):
        self.parent = parent
        self.current_user = user
        self.on_back = on_back
        
        for widget in parent.winfo_children():
            widget.destroy()

        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Back button and title
        ttk.Button(header_frame, text="← Back", style='Header.TButton',
                  command=on_back).pack(side=tk.LEFT, padx=5)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, expand=True)
        
        if self.bs_icon:
            icon_label = tk.Label(title_frame, image=self.bs_icon, bg="#2c3e50")
            icon_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(title_frame, 
                 text=f"BLOOD SUGAR - {user['full_name'] or user['username']}",
                 style='HeaderTitle.TLabel').pack(side=tk.LEFT)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.LabelFrame(content_frame, text=" NEW READING ", style='Card.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Form fields
        form_frame = ttk.Frame(input_frame)
        form_frame.pack(padx=15, pady=15, fill=tk.X)
        
        # Row 1 - Date and Time
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(date_frame, text="Date", style='FormLabel.TLabel').pack(anchor="w")
        self.date_entry = ttk.Entry(date_frame, style='Form.TEntry', width=12)
        self.date_entry.pack()
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(time_frame, text="Time", style='FormLabel.TLabel').pack(anchor="w")
        self.time_entry = ttk.Entry(time_frame, style='Form.TEntry', width=8)
        self.time_entry.pack()
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        
        # Row 2 - Blood Sugar
        glucose_frame = ttk.Frame(form_frame)
        glucose_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(glucose_frame, text="Glucose (mg/dL)", style='FormLabel.TLabel').pack(anchor="w")
        self.glucose_entry = ttk.Entry(glucose_frame, style='Form.TEntry', width=8)
        self.glucose_entry.pack()
        
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(type_frame, text="Measurement Type", style='FormLabel.TLabel').pack(anchor="w")
        self.measurement_type = ttk.Combobox(type_frame, 
                                           values=["Fasting", "Before Meal", "After Meal", "Before Bed", "Random"],
                                           style='Form.TCombobox', width=12)
        self.measurement_type.pack()
        
        meal_frame = ttk.Frame(form_frame)
        meal_frame.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(meal_frame, text="Meal Context", style='FormLabel.TLabel').pack(anchor="w")
        self.meal_context = ttk.Combobox(meal_frame, 
                                       values=["", "Breakfast", "Lunch", "Dinner", "Snack"],
                                       style='Form.TCombobox', width=10)
        self.meal_context.pack()
        
        # Row 3 - Notes
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Label(notes_frame, text="Notes", style='FormLabel.TLabel').pack(anchor="w")
        self.notes_entry = ttk.Entry(notes_frame, style='Form.TEntry')
        self.notes_entry.pack(fill=tk.X)
        
        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, text="Add Reading", style='Primary.TButton',
                  command=self.add_reading).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate Report", style='Secondary.TButton',
                  command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Show Trends", style='Secondary.TButton',
                  command=self.show_trends).pack(side=tk.LEFT, padx=5)
        
        # History frame
        history_frame = ttk.LabelFrame(content_frame, text=" HISTORY ", style='Card.TFrame')
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(history_frame, 
                                columns=("ID", "Date", "Time", "Glucose", "Type", "Meal", "Notes"), 
                                show="headings", style='Custom.Treeview')
        
        # Configure columns
        columns = [
            ("ID", 40, False), 
            ("Date", 100, True), 
            ("Time", 80, True), 
            ("Glucose", 80, True), 
            ("Type", 100, True), 
            ("Meal", 80, True), 
            ("Notes", 200, True)
        ]
        
        for col, width, stretch in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER, stretch=stretch)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.context_menu = tk.Menu(parent, tearoff=0)
        self.context_menu.add_command(label="Delete Reading", command=self.delete_reading)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, date, time, glucose_level, measurement_type, meal_context, notes 
            FROM bs_readings 
            WHERE user_id = ?
            ORDER BY date DESC, time DESC
        ''', (self.current_user['id'],))
        
        rows = cursor.fetchall()
        self.report_data = pd.DataFrame(rows, columns=["ID", "Date", "Time", "Glucose", "Type", "Meal", "Notes"])
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_reading(self):
        date = self.date_entry.get()
        time = self.time_entry.get()
        glucose = self.glucose_entry.get()
        measurement_type = self.measurement_type.get()
        meal_context = self.meal_context.get()
        notes = self.notes_entry.get()
        
        try:
            if not date or not time:
                raise ValueError("Date and time are required")
            if not glucose:
                raise ValueError("Glucose level is required")
            if not measurement_type:
                raise ValueError("Measurement type is required")
            
            glucose = int(glucose)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO bs_readings (user_id, date, time, glucose_level, measurement_type, meal_context, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_user['id'], date, time, glucose, measurement_type, meal_context, notes))
            self.conn.commit()
            
            self.load_data()
            self.glucose_entry.delete(0, tk.END)
            self.measurement_type.set('')
            self.meal_context.set('')
            self.notes_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Reading added successfully")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

    def delete_reading(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        reading_id = self.tree.item(item, "values")[0]
        
        if messagebox.askyesno("Confirm", "Delete this reading?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM bs_readings WHERE id = ? AND user_id = ?", 
                          (reading_id, self.current_user['id']))
            self.conn.commit()
            self.load_data()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def generate_report(self):
        if self.report_data.empty:
            messagebox.showwarning("No Data", "No data available to generate report")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT full_name, diabetes_type FROM users WHERE id = ?', (self.current_user['id'],))
        user_data = cursor.fetchone()
        user_name = user_data[0] or self.current_user['username']
        diabetes_type = user_data[1] or "Not specified"
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.set_fill_color(44, 62, 80)  # Dark blue
        pdf.set_text_color(255, 255, 255)  # White
        pdf.cell(0, 10, f"Blood Sugar Report for {user_name}", 0, 1, 'C', 1)
        pdf.cell(0, 10, f"Diabetes Type: {diabetes_type}", 0, 1, 'C', 1)
        pdf.ln(10)
        
        # Summary statistics
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)  # Black
        pdf.cell(0, 10, "Summary Statistics", 0, 1)
        pdf.set_font("Arial", size=10)
        
        stats = self.report_data[['Glucose']].describe().round(1)
        for index, row in stats.iterrows():
            pdf.cell(0, 6, f"{index}: {row['Glucose']} mg/dL", 0, 1)
        
        pdf.ln(5)
        
        # Glucose interpretation
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Glucose Level Interpretation", 0, 1)
        pdf.set_font("Arial", size=10)
        
        interpretation = [
            "Normal fasting glucose: 70-99 mg/dL",
            "Prediabetes (fasting): 100-125 mg/dL",
            "Diabetes (fasting): 126+ mg/dL",
            "Normal post-meal (2h): <140 mg/dL",
            "Prediabetes post-meal: 140-199 mg/dL",
            "Diabetes post-meal: 200+ mg/dL"
        ]
        
        for line in interpretation:
            pdf.cell(0, 6, line, 0, 1)
        
        pdf.ln(10)
        
        # Recent readings table
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Recent Readings", 0, 1)
        pdf.set_font("Arial", size=8)
        
        # Table header
        pdf.set_fill_color(200, 220, 255)  # Light blue
        headers = ["Date", "Time", "Glucose", "Type", "Meal", "Notes"]
        widths = [25, 20, 25, 30, 25, 65]
        
        for header, width in zip(headers, widths):
            pdf.cell(width, 6, header, 1, 0, 'C', 1)
        pdf.ln()
        
        # Table rows
        pdf.set_fill_color(255, 255, 255)  # White
        for _, row in self.report_data.head(20).iterrows():
            pdf.cell(25, 6, str(row['Date']), 1)
            pdf.cell(20, 6, str(row['Time']), 1)
            
            # Color code based on glucose values
            glucose = row['Glucose']
            measurement_type = row['Type']
            
            if measurement_type == "Fasting":
                if glucose >= 126:
                    pdf.set_text_color(255, 0, 0)  # Red for diabetic
                elif glucose >= 100:
                    pdf.set_text_color(255, 165, 0)  # Orange for prediabetic
                else:
                    pdf.set_text_color(0, 128, 0)  # Green for normal
            else:  # Post-meal or random
                if glucose >= 200:
                    pdf.set_text_color(255, 0, 0)
                elif glucose >= 140:
                    pdf.set_text_color(255, 165, 0)
                else:
                    pdf.set_text_color(0, 128, 0)
                    
            pdf.cell(25, 6, str(glucose), 1)
            pdf.set_text_color(0, 0, 0)  # Black
            
            pdf.cell(30, 6, str(row['Type']), 1)
            pdf.cell(25, 6, str(row['Meal']), 1)
            pdf.cell(65, 6, str(row['Notes'])[:35], 1)
            pdf.ln()
        
        filename = f"bs_report_{user_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Report Generated", f"Report saved as {filename}")

    def show_trends(self):
        if self.report_data.empty:
            messagebox.showwarning("No Data", "No data available to show trends")
            return
        
        trend_window = tk.Toplevel(self.parent)
        trend_window.title("Blood Sugar Trends")
        trend_window.geometry("900x700")
        trend_window.resizable(True, True)
        
        # Apply theme
        try:
            plt.style.use('seaborn')
        except:
            plt.style.use('ggplot')
        
        df = self.report_data.copy()
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df = df.sort_values('DateTime')
        
        # Create figure with subplots
        fig = plt.figure(figsize=(10, 8))
        gs = fig.add_gridspec(3, 1, height_ratios=[3, 2, 1])
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # Define colors for different measurement types
        colors = {
            'Fasting': '#3498db',
            'Before Meal': '#9b59b6',
            'After Meal': '#e74c3c',
            'Before Bed': '#f39c12',
            'Random': '#2ecc71'
        }
        
        # Glucose plot with different colors for measurement types
        for m_type, group in df.groupby('Type'):
            ax1.plot(group['DateTime'], group['Glucose'], 
                    'o-', label=m_type, color=colors.get(m_type, '#333333'), 
                    markersize=5, linewidth=2)
        
        # Add healthy range bands
        ax1.axhspan(70, 99, color='#2ecc71', alpha=0.1, label='Normal')
        ax1.axhspan(100, 125, color='#f39c12', alpha=0.1, label='Prediabetes')
        ax1.axhspan(126, 300, color='#e74c3c', alpha=0.1, label='Diabetes')
        
        ax1.set_ylabel('Glucose (mg/dL)', fontweight='bold')
        ax1.set_title('Blood Sugar Trend', fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Measurement type distribution
        type_counts = df['Type'].value_counts()
        ax2.bar(type_counts.index, type_counts.values, 
               color=[colors.get(t, '#333333') for t in type_counts.index])
        ax2.set_ylabel('Count', fontweight='bold')
        ax2.set_title('Measurement Distribution', fontweight='bold')
        
        # Summary statistics
        stats = df[['Glucose']].describe().round(1)
        stats_text = [
            f"Glucose: Min={stats.loc['min', 'Glucose']}, Max={stats.loc['max', 'Glucose']}",
            f"Average: {stats.loc['mean', 'Glucose']}",
            f"Readings: {len(df)}"
        ]
        
        ax3.axis('off')
        ax3.text(0.05, 0.5, "\n".join(stats_text), 
                fontsize=10, va='center', ha='left')
        
        plt.tight_layout()
        
        # Embed plot in Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=trend_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbar and close button
        toolbar_frame = ttk.Frame(trend_window)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar_frame, text="Close", 
                  command=trend_window.destroy).pack(side=tk.RIGHT)