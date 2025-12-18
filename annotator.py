import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import argparse

class ImageAnnotator:
    def __init__(self, root, image_folder):
        self.root = root
        self.root.title("Image Annotator (Gender + Status)")
        self.image_folder = image_folder
        # make sure we only keep files (you can refine extensions if needed)
        self.image_files = sorted(os.listdir(image_folder))
        self.current_index = 0
        # use a dict to avoid duplicate entries: { filename: (gender, status) }
        self.annotations = {}

        # Label options
        self.gender_labels = ["male", "female"]
        self.status_labels = ["noble", "warrior", "incarnation", "commoner"]

        # --- UI Layout ---
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.file_name_label = tk.Label(root, text="")
        self.file_name_label.pack(pady=5)

        self.progress_label = tk.Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=5)

        # --- Gender selection ---
        tk.Label(root, text="Select Gender:").pack()
        self.gender_var = tk.StringVar(value=self.gender_labels[0])
        gender_frame = tk.Frame(root)
        gender_frame.pack(pady=5)
        for gender in self.gender_labels:
            ttk.Radiobutton(gender_frame, text=gender.capitalize(), variable=self.gender_var, value=gender).pack(side=tk.LEFT, padx=5)

        # --- Status selection ---
        tk.Label(root, text="Select Status:").pack()
        self.status_var = tk.StringVar(value=self.status_labels[0])
        status_frame = tk.Frame(root)
        status_frame.pack(pady=5)
        for i, status in enumerate(self.status_labels, start=1):
            ttk.Radiobutton(status_frame, text=f"{i}: {status.capitalize()}", variable=self.status_var, value=status).pack(side=tk.LEFT, padx=5)

        # --- Navigation buttons ---
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=10)
        ttk.Button(nav_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=10)

        ttk.Button(root, text="Save", command=self.save_annotations).pack(side=tk.BOTTOM, pady=10)

        self.load_image()

        # Key binds
        self.root.bind("<Key>", self.key_input)
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())

    def load_image(self):
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        image = Image.open(image_path)
        image = image.resize((400, 400), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        image_name = self.image_files[self.current_index]
        self.file_name_label.config(text=f"File: {image_name}")

        # If this image already has an annotation, load it into the UI
        if image_name in self.annotations:
            gender, status = self.annotations[image_name]
            self.gender_var.set(gender)
            self.status_var.set(status)
        else:
            # reset to defaults (optional)
            self.gender_var.set(self.gender_labels[0])
            self.status_var.set(self.status_labels[0])

        self.update_progress()

    def save_annotation(self):
        """Overwrite or create the annotation for the current image (no duplicates)."""
        image_name = self.image_files[self.current_index]
        gender = self.gender_var.get()
        status = self.status_var.get()
        self.annotations[image_name] = (gender, status)

    def next_image(self):
        self.save_annotation()
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()
        else:
            messagebox.showinfo("End of Images", "No more images to display.")

    def prev_image(self):
        # save current changes before moving back
        self.save_annotation()
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()
        else:
            messagebox.showinfo("Start of Images", "This is the first image.")

    def save_annotations(self):
        self.save_annotation()
        self.save_annotations_to_file("tsv/manual_label_gender_status.tsv")
        messagebox.showinfo("Save Successful", "Annotations have been saved successfully.")

    def save_annotations_to_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write("filename\tgender\tstatus\n")
            # write in the order of image_files (so output is stable/ordered)
            for image_name in self.image_files:
                if image_name in self.annotations:
                    gender, status = self.annotations[image_name]
                    f.write(f"{image_name}\t{gender}\t{status}\n")

    def update_progress(self):
        progress = (self.current_index + 1) / len(self.image_files) * 100
        self.progress_label.config(text=f"Progress: {progress:.2f}%")

    def key_input(self, event):
        key = event.char.lower()
        # Quick gender keys
        if key == 'm':
            self.gender_var.set("male")
        elif key == 'f':
            self.gender_var.set("female")
        # Quick status keys (1–4)
        elif key in ['1', '2', '3', '4']:
            idx = int(key) - 1
            if 0 <= idx < len(self.status_labels):
                self.status_var.set(self.status_labels[idx])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Annotator (Gender + Status)")
    parser.add_argument("image_folder", type=str, help="Path to the folder containing images")
    args = parser.parse_args()

    root = tk.Tk()
    annotator = ImageAnnotator(root, args.image_folder)
    root.protocol("WM_DELETE_WINDOW", lambda: (annotator.save_annotations_to_file("tsv/manual_label_gender_status.tsv"), root.destroy()))
    root.mainloop()
