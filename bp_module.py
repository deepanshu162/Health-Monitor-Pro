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

class BPModule:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_tables()
        self.load_images()
        
    def load_images(self):
        try:
            self.bp_icon = Image.open("assets/bp_icon.png").resize((30, 30))
            self.bp_icon = ImageTk.PhotoImage(self.bp_icon)
        except:
            self.bp_icon = None
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bp_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                systolic INTEGER NOT NULL,
                diastolic INTEGER NOT NULL,
                pulse INTEGER,
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
        
        if self.bp_icon:
            icon_label = tk.Label(title_frame, image=self.bp_icon, bg="#2c3e50")
            icon_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(title_frame, 
                 text=f"BLOOD PRESSURE - {user['full_name'] or user['username']}",
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
        
        # Row 2 - Blood Pressure
        systolic_frame = ttk.Frame(form_frame)
        systolic_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(systolic_frame, text="Systolic (mmHg)", style='FormLabel.TLabel').pack(anchor="w")
        self.systolic_entry = ttk.Entry(systolic_frame, style='Form.TEntry', width=8)
        self.systolic_entry.pack()
        
        diastolic_frame = ttk.Frame(form_frame)
        diastolic_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(diastolic_frame, text="Diastolic (mmHg)", style='FormLabel.TLabel').pack(anchor="w")
        self.diastolic_entry = ttk.Entry(diastolic_frame, style='Form.TEntry', width=8)
        self.diastolic_entry.pack()
        
        pulse_frame = ttk.Frame(form_frame)
        pulse_frame.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(pulse_frame, text="Pulse (bpm)", style='FormLabel.TLabel').pack(anchor="w")
        self.pulse_entry = ttk.Entry(pulse_frame, style='Form.TEntry', width=8)
        self.pulse_entry.pack()
        
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
        self.tree = ttk.Treeview(history_frame, columns=("ID", "Date", "Time", "Systolic", "Diastolic", "Pulse", "Notes"), 
                                show="headings", style='Custom.Treeview')
        
        # Configure columns
        columns = [
            ("ID", 40, False), 
            ("Date", 100, True), 
            ("Time", 80, True), 
            ("Systolic", 80, True), 
            ("Diastolic", 80, True), 
            ("Pulse", 60, True), 
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
            SELECT id, date, time, systolic, diastolic, pulse, notes 
            FROM bp_readings 
            WHERE user_id = ?
            ORDER BY date DESC, time DESC
        ''', (self.current_user['id'],))
        
        rows = cursor.fetchall()
        self.report_data = pd.DataFrame(rows, columns=["ID", "Date", "Time", "Systolic", "Diastolic", "Pulse", "Notes"])
        
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_reading(self):
        date = self.date_entry.get()
        time = self.time_entry.get()
        systolic = self.systolic_entry.get()
        diastolic = self.diastolic_entry.get()
        pulse = self.pulse_entry.get()
        notes = self.notes_entry.get()
        
        try:
            if not date or not time:
                raise ValueError("Date and time are required")
            
            systolic = int(systolic)
            diastolic = int(diastolic)
            pulse = int(pulse) if pulse else None
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO bp_readings (user_id, date, time, systolic, diastolic, pulse, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_user['id'], date, time, systolic, diastolic, pulse, notes))
            self.conn.commit()
            
            self.load_data()
            self.systolic_entry.delete(0, tk.END)
            self.diastolic_entry.delete(0, tk.END)
            self.pulse_entry.delete(0, tk.END)
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
            cursor.execute("DELETE FROM bp_readings WHERE id = ? AND user_id = ?", 
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
        cursor.execute('SELECT full_name FROM users WHERE id = ?', (self.current_user['id'],))
        user_name = cursor.fetchone()[0] or self.current_user['username']
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.set_fill_color(44, 62, 80)  # Dark blue
        pdf.set_text_color(255, 255, 255)  # White
        pdf.cell(0, 10, f"Blood Pressure Report for {user_name}", 0, 1, 'C', 1)
        pdf.ln(10)
        
        # Summary statistics
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)  # Black
        pdf.cell(0, 10, "Summary Statistics", 0, 1)
        pdf.set_font("Arial", size=10)
        
        stats = self.report_data[['Systolic', 'Diastolic', 'Pulse']].describe().round(1)
        for index, row in stats.iterrows():
            pdf.cell(0, 6, f"{index}: Systolic={row['Systolic']}, Diastolic={row['Diastolic']}, Pulse={row['Pulse']}", 0, 1)
        
        pdf.ln(10)
        
        # Recent readings table
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Recent Readings", 0, 1)
        pdf.set_font("Arial", size=8)
        
        # Table header
        pdf.set_fill_color(200, 220, 255)  # Light blue
        headers = ["Date", "Time", "Systolic", "Diastolic", "Pulse", "Notes"]
        widths = [25, 20, 20, 20, 15, 90]
        
        for header, width in zip(headers, widths):
            pdf.cell(width, 6, header, 1, 0, 'C', 1)
        pdf.ln()
        
        # Table rows
        pdf.set_fill_color(255, 255, 255)  # White
        for _, row in self.report_data.head(20).iterrows():
            pdf.cell(25, 6, str(row['Date']), 1)
            pdf.cell(20, 6, str(row['Time']), 1)
            
            # Color code based on BP values
            systolic = row['Systolic']
            diastolic = row['Diastolic']
            
            if systolic >= 140 or diastolic >= 90:
                pdf.set_text_color(255, 0, 0)  # Red for high
            elif systolic >= 120 or diastolic >= 80:
                pdf.set_text_color(255, 165, 0)  # Orange for elevated
            else:
                pdf.set_text_color(0, 128, 0)  # Green for normal
                
            pdf.cell(20, 6, str(systolic), 1)
            pdf.cell(20, 6, str(diastolic), 1)
            pdf.set_text_color(0, 0, 0)  # Black
            
            pdf.cell(15, 6, str(row['Pulse']), 1)
            pdf.cell(90, 6, str(row['Notes'])[:40], 1)
            pdf.ln()
        
        filename = f"bp_report_{user_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Report Generated", f"Report saved as {filename}")

    def show_trends(self):
        if self.report_data.empty:
            messagebox.showwarning("No Data", "No data available to show trends")
            return
        
        trend_window = tk.Toplevel(self.parent)
        trend_window.title("Blood Pressure Trends")
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
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 2, 1])
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # Blood pressure plot
        ax1.plot(df['DateTime'], df['Systolic'], label='Systolic', color='#e74c3c', linewidth=2, marker='o')
        ax1.plot(df['DateTime'], df['Diastolic'], label='Diastolic', color='#3498db', linewidth=2, marker='o')
        
        # Add healthy range bands
        ax1.axhspan(90, 120, color='#2ecc71', alpha=0.1, label='Normal')
        ax1.axhspan(120, 140, color='#f39c12', alpha=0.1, label='Elevated')
        ax1.axhspan(140, 200, color='#e74c3c', alpha=0.1, label='High')
        
        ax1.set_ylabel('mmHg', fontweight='bold')
        ax1.set_title('Blood Pressure Trend', fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Pulse plot
        ax2.plot(df['DateTime'], df['Pulse'], label='Pulse', color='#9b59b6', linewidth=2, marker='o')
        ax2.set_ylabel('BPM', fontweight='bold')
        ax2.set_title('Pulse Trend', fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Summary statistics
        stats = df[['Systolic', 'Diastolic', 'Pulse']].describe().round(1)
        stats_text = []
        for col in ['Systolic', 'Diastolic', 'Pulse']:
            stats_text.append(
                f"{col}: Min={stats.loc['min', col]}, Max={stats.loc['max', col]}, "
                f"Avg={stats.loc['mean', col]}"
            )
        
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