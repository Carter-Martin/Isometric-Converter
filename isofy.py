from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rotate_tile_to_iso(tile, target_size):
    original_width, original_height = tile.size
    target_width, target_height = target_size

    padded_tile = Image.new('RGBA', (original_width, original_height), (0, 0, 0, 0))
    padded_tile.paste(tile)

    rotated_tile = padded_tile.rotate(45, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))

    final_tile = rotated_tile.resize((target_width, target_height), resample=Image.BICUBIC)

    return final_tile

def convert_to_isometric(input_path, grid_size, target_diagonal):
    img = Image.open(input_path).convert('RGBA')
    img_width, img_height = img.size

    grid_cols, grid_rows = grid_size
    tile_width = img_width // grid_cols
    tile_height = img_height // grid_rows

    iso_width, iso_height = target_diagonal

    output_width = grid_cols * iso_width
    output_height = grid_rows * iso_height

    output_img = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))

    for y in range(grid_rows):
        for x in range(grid_cols):
            box = (x * tile_width, y * tile_height, (x + 1) * tile_width, (y + 1) * tile_height)
            tile = img.crop(box)

            iso_tile = rotate_tile_to_iso(tile, (iso_width, iso_height))

            output_x = x * iso_width
            output_y = y * iso_height

            output_img.paste(iso_tile, (output_x, output_y), iso_tile)

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_iso.png"
    output_img.save(output_path)
    return output_path

# GUI
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
    )
    if file_path:
        entry_input_path.delete(0, tk.END)
        entry_input_path.insert(0, file_path)

def update_size_from_width(event=None):
    if lock_ratio.get():
        width_str = entry_target_width.get()
        if width_str == "":
            entry_target_height.config(state="normal")
            entry_target_height.delete(0, tk.END)
            entry_target_height.config(state="disabled")
            return
        try:
            width = int(width_str)
            height = width // 2
            entry_target_height.config(state="normal")
            entry_target_height.delete(0, tk.END)
            entry_target_height.insert(0, str(height))
            entry_target_height.config(state="disabled")
        except ValueError:
            pass  # Ignore invalid input

def toggle_lock():
    if lock_ratio.get():
        btn_lock.config(text="🔒 Unlock Ratio")
        entry_target_height.config(state="disabled")
        update_size_from_width()
    else:
        btn_lock.config(text="🔓 Lock Ratio")
        entry_target_height.config(state="normal")

def validate_numeric_input(P):
    if P == "" or P.isdigit():
        return True
    return False

def process_image():
    input_path = entry_input_path.get()
    try:
        grid_cols = int(spin_cols.get())
        grid_rows = int(spin_rows.get())
        target_width = int(entry_target_width.get())
        target_height = int(entry_target_height.get())
    except ValueError:
        messagebox.showerror("Error", "Grid sizes and target sizes must be integers.")
        return

    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "Invalid input file path.")
        return

    try:
        output_path = convert_to_isometric(input_path, (grid_cols, grid_rows), (target_width, target_height))
        messagebox.showinfo("Success", f"Image saved as:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Build GUI
root = tk.Tk()
root.title("Isometric Tile Converter")

lock_ratio = tk.BooleanVar(value=True)

vcmd = (root.register(validate_numeric_input), "%P")

# Input File
tk.Label(root, text="Input Image:").grid(row=0, column=0, sticky="e")
entry_input_path = tk.Entry(root, width=50)
entry_input_path.grid(row=0, column=1, padx=5, pady=5)
btn_browse = tk.Button(root, text="Browse", command=select_file)
btn_browse.grid(row=0, column=2, padx=5)

# Grid Size
tk.Label(root, text="Grid Columns:").grid(row=1, column=0, sticky="e")
spin_cols = tk.Spinbox(root, from_=1, to=1000, width=5, validate="key", validatecommand=vcmd)
spin_cols.grid(row=1, column=1, padx=5, pady=5, sticky="w")
spin_cols.delete(0, tk.END)
spin_cols.insert(0, "1")

tk.Label(root, text="Grid Rows:").grid(row=2, column=0, sticky="e")
spin_rows = tk.Spinbox(root, from_=1, to=1000, width=5, validate="key", validatecommand=vcmd)
spin_rows.grid(row=2, column=1, padx=5, pady=5, sticky="w")
spin_rows.delete(0, tk.END)
spin_rows.insert(0, "1")

# Target Size
tk.Label(root, text="Target Width:").grid(row=3, column=0, sticky="e")
entry_target_width = tk.Entry(root, validate="key", validatecommand=vcmd)
entry_target_width.grid(row=3, column=1, padx=5, pady=5, sticky="w")
entry_target_width.insert(0, "256")
entry_target_width.bind("<KeyRelease>", update_size_from_width)

tk.Label(root, text="Target Height:").grid(row=4, column=0, sticky="e")
entry_target_height = tk.Entry(root, validate="key", validatecommand=vcmd)
entry_target_height.grid(row=4, column=1, padx=5, pady=5, sticky="w")
entry_target_height.insert(0, "128")

btn_lock = tk.Button(root, text="🔒 Unlock Ratio", command=lambda: lock_ratio.set(not lock_ratio.get()) or toggle_lock())
btn_lock.grid(row=4, column=2, padx=5)

# Process Button
btn_process = tk.Button(root, text="Convert to Isometric", command=process_image)
btn_process.grid(row=5, column=0, columnspan=3, pady=10)

# Initialize with lock active
toggle_lock()

root.mainloop()
