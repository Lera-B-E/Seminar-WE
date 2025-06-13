import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from rdflib import Graph, URIRef, Namespace, RDFS
import numpy as np
from datetime import datetime
import os


class KGOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Optimizer with Knowledge Graph")
        self.root.geometry("900x650")

        self.set_gradient_background()

        self.original_df = None
        self.optimized_df = None
        self.optimized_path = None

        self.create_widgets()

    def set_gradient_background(self):
        canvas = tk.Canvas(self.root, width=900, height=650)
        canvas.pack(fill="both", expand=True)

        start_color = (255, 255, 255)
        end_color = (68, 84, 106)

        height = 650

        for i in range(height):
            r = int(start_color[0] - (start_color[0] - end_color[0]) * (i / height))
            g = int(start_color[1] - (start_color[1] - end_color[1]) * (i / height))
            b = int(start_color[2] - (start_color[2] - end_color[2]) * (i / height))

            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, 900, i, fill=color)

        self.frame = tk.Frame(self.root, bg='')
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

    def create_widgets(self):
        title_label = tk.Label(
            self.frame,
            text="CSV Optimizer with Knowledge Graph",
            font=("Helvetica", 18, "bold"),
        )
        title_label.pack(pady=10)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)

        upload_btn = tk.Button(
            btn_frame,
            text="Upload CSV File",
            width=20,
            command=self.upload_file,
            bg="#44546A",
            fg="white",
            font=("Helvetica", 12)
        )
        upload_btn.grid(row=0, column=0, padx=10)

        self.download_btn = tk.Button(
            btn_frame,
            text="Download Optimized CSV",
            width=25,
            state=tk.DISABLED,
            command=self.download_file,
            bg="#44546A",
            fg="white",
            font=("Helvetica", 12)
        )
        self.download_btn.grid(row=0, column=1, padx=10)

        self.output_text = tk.Text(
            self.frame,
            wrap="word",
            width=100,
            height=20,
            bg="#ffffff",
            fg="black",
            font=("Courier New", 10)
        )
        self.output_text.pack(padx=20, pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self.original_df = pd.read_csv(file_path)
            initial_size = os.path.getsize(file_path)

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Original Dataset:\n{self.original_df.head()}\n\nOptimizing...\n")

            self.optimized_df, report = self.optimize_with_kg(self.original_df)

            self.optimized_path = f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.optimized_df.to_csv(self.optimized_path, index=False)

            final_size = os.path.getsize(self.optimized_path)

            summary = (
                f"✅ Optimization Complete!\n"
                f"Initial Size: {initial_size / 1024:.2f} KB\n"
                f"Final Size: {final_size / 1024:.2f} KB\n"
                f"Reduction: {(initial_size - final_size) / initial_size * 100:.2f}%\n"
                f"Total Rows Before: {report['original_rows']}\n"
                f"Total Rows After: {report['cleaned_rows']}\n"
                f"Duplicate Rows Removed: {report['duplicates_removed']}\n"
                f"Normalized Entities: {report['normalized_entities']}\n"
            )

            self.output_text.insert(tk.END, summary)

            self.download_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Dataset has been optimized!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    def download_file(self):
        if not self.optimized_path or not os.path.exists(self.optimized_path):
            messagebox.showerror("Error", "No optimized file found.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=os.path.basename(self.optimized_path)
        )
        if save_path:
            try:
                self.optimized_df.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"File saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")

    def optimize_with_kg(self, df):
        original_rows = len(df)

        def normalize_row(row):
            return tuple(str(cell).strip().lower() if isinstance(cell, str) else cell for cell in row)

        normalized_data = df.apply(normalize_row, axis=1)
        normalized_df = pd.DataFrame(normalized_data.tolist(), index=df.index)

        deduplicated_normalized = normalized_df.drop_duplicates()
        unique_indices = deduplicated_normalized.index
        deduplicated_df = df.iloc[unique_indices].copy()
        duplicates_removed = original_rows - len(deduplicated_df)

        entity_map = {
            "usa": "United States",
            "nyc": "New York City",
            "uae": "United Arab Emirates",
            "uk": "United Kingdom"
        }

        normalized_count = 0

        kg = Graph()
        ex = Namespace("http://example.org/kg#")
        kg.bind("ex", ex)

        for old, new in entity_map.items():
            subj = URIRef(ex[old.replace(" ", "_")])
            obj = URIRef(ex[new.replace(" ", "_")])
            kg.add((subj, RDFS.label, URIRef(obj)))

        for col in deduplicated_df.select_dtypes(include='object').columns:
            for old, new in entity_map.items():
                mask = deduplicated_df[col].astype(str).str.strip().str.lower() == old
                deduplicated_df.loc[mask, col] = new
                normalized_count += mask.sum()

        cleaned_rows = len(deduplicated_df)

        return deduplicated_df, {
            "original_rows": original_rows,
            "cleaned_rows": cleaned_rows,
            "duplicates_removed": duplicates_removed,
            "normalized_entities": normalized_count
        }


if __name__ == "__main__":
    root = tk.Tk()
    app = KGOptimizerApp(root)
    root.mainloop()