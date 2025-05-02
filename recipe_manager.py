import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, OptionMenu, StringVar
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
import json, os

DATA_FILE = "recipes.json"
CATEGORIES = ["All", "Dessert", "Main Dish", "Snack", "Beverage", "Other"]
recipes = {}

# --- Recipe Data Functions ---
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_recipes_to_file():
    with open(DATA_FILE, "w") as f:
        json.dump(recipes, f, indent=4)

# --- UI Helper Functions ---
def refresh_recipe_list():
    recipe_listbox.delete(0, tk.END)
    term = search_var.get().lower()
    for name in sorted(recipes.keys()):
        category_match = category_filter.get() == "All" or recipes[name].get("category") == category_filter.get()
        search_match = term in name.lower()
        if category_match and search_match:
            recipe_listbox.insert(tk.END, name)

def clear_fields():
    name_entry.delete(0, tk.END)
    ingredients_text.delete("1.0", tk.END)
    steps_text.delete("1.0", tk.END)
    image_path.set("")
    preview_label.config(image='')
    category_var.set("Other")

def add_or_update_recipe():
    name = name_entry.get().strip()
    ingredients = ingredients_text.get("1.0", tk.END).strip().split("\n")
    steps = steps_text.get("1.0", tk.END).strip()
    category = category_var.get()
    image = image_path.get()

    if not name or not ingredients or not steps:
        messagebox.showwarning("Missing Info", "Fill out all fields.")
        return

    recipes[name] = {
        "ingredients": ingredients,
        "steps": steps,
        "category": category,
        "image": image
    }
    save_recipes_to_file()
    refresh_recipe_list()
    messagebox.showinfo("Saved", f"'{name}' saved/updated.")

def delete_recipe():
    selected = recipe_listbox.curselection()
    if not selected:
        messagebox.showwarning("No selection", "Select a recipe to delete.")
        return
    name = recipe_listbox.get(selected[0])
    if messagebox.askyesno("Delete", f"Delete '{name}'?"):
        del recipes[name]
        save_recipes_to_file()
        refresh_recipe_list()
        clear_fields()

def load_selected_recipe():
    selected = recipe_listbox.curselection()
    if not selected:
        return
    name = recipe_listbox.get(selected[0])
    recipe = recipes[name]

    name_entry.delete(0, tk.END)
    name_entry.insert(0, name)
    ingredients_text.delete("1.0", tk.END)
    ingredients_text.insert("1.0", "\n".join(recipe["ingredients"]))
    steps_text.delete("1.0", tk.END)
    steps_text.insert("1.0", recipe["steps"])
    category_var.set(recipe.get("category", "Other"))
    image_path.set(recipe.get("image", ""))
    show_image_preview()

def browse_image():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
    if path:
        image_path.set(path)
        show_image_preview()

def show_image_preview():
    try:
        img = Image.open(image_path.get())
        img.thumbnail((100, 100))
        photo = ImageTk.PhotoImage(img)
        preview_label.config(image=photo)
        preview_label.image = photo
    except:
        preview_label.config(image='')

def export_to_pdf():
    selected = recipe_listbox.curselection()
    if not selected:
        messagebox.showwarning("No selection", "Select a recipe to export.")
        return
    name = recipe_listbox.get(selected[0])
    recipe = recipes[name]

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    c = canvas.Canvas(file_path)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Recipe: {name}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Category: {recipe.get('category', 'Other')}")

    y = 750
    c.drawString(50, y, "Ingredients:")
    for ing in recipe["ingredients"]:
        y -= 15
        c.drawString(70, y, f"- {ing}")

    y -= 30
    c.drawString(50, y, "Steps:")
    for line in recipe["steps"].split("\n"):
        y -= 15
        c.drawString(70, y, line)

    c.save()
    messagebox.showinfo("Exported", f"'{name}' exported to PDF.")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Recipe Manager")
root.geometry("950x650")

recipes = load_recipes()

# Top Filters
category_filter = StringVar(value="All")
tk.Label(root, text="Filter by Category:").pack()
filter_menu = OptionMenu(root, category_filter, *CATEGORIES, command=lambda _: refresh_recipe_list())
filter_menu.pack()

search_var = tk.StringVar()
tk.Label(root, text="Search by Name:").pack()
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.pack()
search_var.trace("w", lambda *_: refresh_recipe_list())

# Left Frame: Recipe Browser
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

tk.Label(left_frame, text="Recipes").pack()
recipe_listbox = Listbox(left_frame, width=30, height=30)
recipe_listbox.pack(side=tk.LEFT, fill=tk.Y)

scrollbar = Scrollbar(left_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
recipe_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=recipe_listbox.yview)
recipe_listbox.bind("<<ListboxSelect>>", lambda e: load_selected_recipe())

# Right Frame: Recipe Editor
right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

tk.Label(right_frame, text="Recipe Name:").pack()
name_entry = tk.Entry(right_frame, width=60)
name_entry.pack()

tk.Label(right_frame, text="Category:").pack()
category_var = StringVar(value="Other")
category_menu = OptionMenu(right_frame, category_var, *CATEGORIES[1:])
category_menu.pack()

tk.Label(right_frame, text="Ingredients (one per line):").pack()
ingredients_text = tk.Text(right_frame, width=60, height=10)
ingredients_text.pack()

tk.Label(right_frame, text="Steps:").pack()
steps_text = tk.Text(right_frame, width=60, height=10)
steps_text.pack()

# Image Upload
image_path = StringVar()
tk.Button(right_frame, text="Attach Image", command=browse_image).pack(pady=5)
preview_label = tk.Label(right_frame)
preview_label.pack()

# Buttons
btn_frame = tk.Frame(right_frame)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Save / Update", command=add_or_update_recipe).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Delete", command=delete_recipe).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Clear", command=clear_fields).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Export to PDF", command=export_to_pdf).grid(row=0, column=3, padx=5)

# Final load
refresh_recipe_list()
root.mainloop()
