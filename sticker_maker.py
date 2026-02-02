import os
import sys
import threading
import requests
from pathlib import Path
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import io


class StickerMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticker Maker")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Get API key from environment
        self.api_key = os.environ.get('REMOVEBG_API_KEY', '')

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill='both', expand=True)

        # Title
        ttk.Label(main, text="Sticker Maker", font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        # API Key
        key_frame = ttk.Frame(main)
        key_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(key_frame, text="API Key:").pack(side='left')
        self.api_entry = ttk.Entry(key_frame, width=40, show="*")
        self.api_entry.pack(side='left', padx=(10, 0))
        self.api_entry.insert(0, self.api_key)
        ttk.Button(key_frame, text="Save", command=self.save_api_key, width=6).pack(side='left', padx=(5, 0))

        # Output Type
        type_frame = ttk.Frame(main)
        type_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(type_frame, text="Output Type:").pack(side='left')
        self.output_type = ttk.Combobox(type_frame, state='readonly', width=35)
        self.output_type['values'] = [
            "Telegram Sticker (remove background)",
            "Telegram Sticker (keep background)",
            "PNG (remove background only)",
            "PNG (keep original)"
        ]
        self.output_type.current(0)
        self.output_type.pack(side='left', padx=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Select Image(s)", command=self.select_files, width=20).pack(pady=5)
        ttk.Button(btn_frame, text="Select Folder", command=self.select_folder, width=20).pack(pady=5)

        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.progress_var, font=('Arial', 10)).pack(pady=10)

        self.progress_bar = ttk.Progressbar(main, mode='determinate', length=400)
        self.progress_bar.pack(pady=(0, 10))

        # Log
        self.log = tk.Text(main, height=6, width=55, state='disabled')
        self.log.pack()

        # Credits and instructions at bottom
        bottom_frame = ttk.Frame(main)
        bottom_frame.pack(pady=(10, 0))
        ttk.Label(bottom_frame, text="Get free API key at remove.bg",
                  font=('Arial', 8), foreground='gray').pack()
        ttk.Label(bottom_frame, text="Made by Bennett | @bbennctt",
                  font=('Arial', 9, 'bold'), foreground='#555555').pack(pady=(5, 0))

    def log_message(self, msg):
        self.log.configure(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')
        self.root.update()

    def save_api_key(self):
        key = self.api_entry.get().strip()
        if key:
            os.system(f'setx REMOVEBG_API_KEY "{key}"')
            self.api_key = key
            messagebox.showinfo("Saved", "API key saved! It will persist after restart.")

    def remove_background(self, image_data):
        """Remove background using remove.bg API"""
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_data},
            data={'size': 'auto'},
            headers={'X-Api-Key': self.api_entry.get().strip()}
        )
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def resize_for_sticker(self, img, max_size=512):
        """Resize so longest side is 512px"""
        w, h = img.size
        if w >= h:
            new_w, new_h = max_size, int((h / w) * max_size)
        else:
            new_h, new_w = max_size, int((w / h) * max_size)
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def process_image(self, filepath, output_dir):
        """Process a single image"""
        filename = Path(filepath).stem
        output_type = self.output_type.get()

        remove_bg = "remove background" in output_type
        make_sticker = "Sticker" in output_type

        # Load image
        with open(filepath, 'rb') as f:
            image_data = f.read()

        # Remove background if needed
        if remove_bg:
            image_data = self.remove_background(image_data)

        # Open as PIL Image
        img = Image.open(io.BytesIO(image_data)).convert('RGBA')

        # Resize for sticker if needed
        if make_sticker:
            img = self.resize_for_sticker(img)
            output_path = os.path.join(output_dir, f"{filename}_sticker.webp")
            img.save(output_path, 'WEBP', quality=90)
        else:
            output_path = os.path.join(output_dir, f"{filename}_processed.png")
            img.save(output_path, 'PNG')

        return output_path

    def process_files(self, files):
        """Process multiple files"""
        if not self.api_entry.get().strip() and "remove background" in self.output_type.get():
            messagebox.showerror("Error", "Please enter your remove.bg API key")
            return

        # Create output folder
        output_dir = os.path.join(os.path.dirname(files[0]), "output")
        os.makedirs(output_dir, exist_ok=True)

        self.progress_bar['maximum'] = len(files)
        self.progress_bar['value'] = 0

        def process_thread():
            success = 0
            for i, f in enumerate(files):
                try:
                    self.progress_var.set(f"Processing {i+1}/{len(files)}...")
                    result = self.process_image(f, output_dir)
                    self.log_message(f"Created: {Path(result).name}")
                    success += 1
                except Exception as e:
                    self.log_message(f"Error: {Path(f).name} - {str(e)}")
                self.progress_bar['value'] = i + 1
                self.root.update()

            self.progress_var.set(f"Done! {success}/{len(files)} processed")
            messagebox.showinfo("Complete", f"Processed {success} files.\nSaved to: {output_dir}")
            os.startfile(output_dir)

        threading.Thread(target=process_thread, daemon=True).start()

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if files:
            self.process_files(list(files))

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.bmp']:
                files.extend(Path(folder).glob(ext))
            files = [str(f) for f in files if '_sticker' not in f.name and '_processed' not in f.name]
            if files:
                self.process_files(files)
            else:
                messagebox.showwarning("No images", "No image files found in folder")


def main():
    root = tk.Tk()
    app = StickerMakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
