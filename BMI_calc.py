import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import datetime

# SQLite database setup
conn = sqlite3.connect('bmi_data.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS bmi_records (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              weight REAL,
              height REAL,
              bmi REAL,
              date TEXT
          )
          ''')
conn.commit()


def calculate_bmi(weight, height):
    return weight / (height ** 2)


def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"


def save_bmi_record(user_id, weight, height, bmi):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
              INSERT INTO bmi_records (user_id, weight, height, bmi, date)
              VALUES (?, ?, ?, ?, ?)
              ''', (user_id, weight, height, bmi, current_date))
    conn.commit()


def plot_bmi_trend(user_id):
    c.execute('''
              SELECT date, bmi
              FROM bmi_records
              WHERE user_id = ?
              ORDER BY date
              ''', (user_id,))
    data = c.fetchall()

    dates = [record[0] for record in data]
    bmis = [record[1] for record in data]

    fig, ax = plt.subplots()
    ax.plot(dates, bmis, marker='o', linestyle='-', color=get_bmi_color(bmis[-1]))  # Pass the last BMI value
    ax.set(xlabel='Date', ylabel='BMI', title='BMI Trend Over Time')
    ax.grid()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return fig


def calculate_and_display_bmi():
    try:
        weight = float(weight_entry.get())
        height_unit = height_unit_var.get()
        height_value = float(height_entry.get())
    except ValueError:
        result_label.config(text="Invalid input. Please enter valid numbers.")
        return

    # Convert height to meters
    if height_unit == "centimeters":
        height_value /= 100
    elif height_unit == "feet":
        height_value *= 0.3048
    elif height_unit == "inches":
        height_value *= 0.0254

    bmi = calculate_bmi(weight, height_value)
    category = classify_bmi(bmi)

    result_label.config(text=f"BMI: {bmi:.2f} ({category})", foreground=get_bmi_color(bmi))
    save_bmi_record(1, weight, height_value, bmi)

    # Plot BMI trend
    fig = plot_bmi_trend(1)
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=5, column=0, columnspan=3, sticky="nsew")


def get_bmi_color(bmi):
    if bmi < 18.5:
        return 'blue'  # Underweight
    elif 18.5 <= bmi < 24.9:
        return 'green'  # Normal weight
    elif 25 <= bmi < 29.9:
        return 'orange'  # Overweight
    else:
        return 'red'  # Obese


# GUI setup
window = tk.Tk()
window.title("BMI Calculator")

# Configure column weights for resizing
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)

# Set padding and spacing
padding = 10
spacing = 5

# Load background image
image_path = "BMI.jpg"
original_image = Image.open(image_path)
resized_image = original_image.resize((800, 600), Image.BICUBIC)
background_image = ImageTk.PhotoImage(resized_image)

# Set background image as a label spanning the entire window
background_label = tk.Label(window, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Increase font size
font_size = 12
style = ttk.Style()

# Change text color and background color
style.configure('TLabel', font=('Helvetica', font_size), foreground='white', background='#333333')
style.configure('TButton', font=('Helvetica', font_size), foreground='blue', background='green')  # Change button color
style.configure('TEntry', font=('Helvetica', font_size), foreground='green', background='green', highlightbackground='yellow')  # Change entry color
style.configure('TCombobox', font=('Helvetica', font_size), foreground='green', background='green')

weight_label = ttk.Label(window, text="Weight (kg):", style='TLabel')
weight_label.grid(row=0, column=0, pady=(padding, spacing), sticky="e")

weight_entry = ttk.Entry(window, style='TEntry')
weight_entry.grid(row=0, column=1, pady=(padding, spacing), sticky="ew")

height_label = ttk.Label(window, text="Height:", style='TLabel')
height_label.grid(row=1, column=0, pady=(spacing, spacing), sticky="e")

height_entry = ttk.Entry(window, style='TEntry')
height_entry.grid(row=1, column=1, pady=(spacing, spacing), sticky="ew")

height_units = ["meters", "centimeters", "feet", "inches"]
height_unit_var = tk.StringVar()
height_unit_var.set(height_units[0])  # default unit is meters

height_unit_menu = ttk.Combobox(window, textvariable=height_unit_var, values=height_units, style='TCombobox')
height_unit_menu.grid(row=1, column=2, pady=(spacing, spacing), sticky="ew")

calculate_button = ttk.Button(window, text="Calculate BMI", command=calculate_and_display_bmi, style='TButton')
calculate_button.grid(row=2, column=0, columnspan=3, pady=(spacing, padding))

result_label = ttk.Label(window, text="", style='TLabel', background='white')
result_label.grid(row=3, column=0, columnspan=3, pady=(spacing, spacing))

# Configure row weight for resizing
window.rowconfigure(5, weight=1)

# Increase window size
window.geometry("800x600")

window.mainloop()

# Close the database connection
conn.close()













