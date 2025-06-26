"""Tkinter client for the MyLoRA API with a dark themed grid UI."""

from tkinter import Tk, Canvas, Toplevel, StringVar, filedialog
from tkinter import ttk
from threading import Thread
import io
from pathlib import Path
from PIL import Image, ImageTk
import requests
import api

GRID_COLUMNS = 5
THUMB_SIZE = 180


def apply_dark_theme(root) -> dict:
    style = ttk.Style(root)
    style.theme_use("clam")
    colors = {
        "bg": "#0d0f11",
        "fg": "#f8f9fa",
        "frame": "#20232a",
        "accent": "#58a6ff",
    }
    style.configure(".", background=colors["bg"], foreground=colors["fg"])
    style.configure("TButton", background=colors["frame"], foreground=colors["fg"])
    style.map(
        "TButton",
        background=[("active", colors["accent"])],
        foreground=[("active", colors["bg"])],
    )
    style.configure(
        "Accent.TButton",
        background=colors["accent"],
        foreground=colors["bg"],
    )
    style.map(
        "Accent.TButton",
        background=[("active", colors["frame"])],
        foreground=[("active", colors["fg"])],
    )
    style.configure("TEntry", fieldbackground=colors["frame"])
    style.configure("TMenubutton", background=colors["frame"], foreground=colors["fg"])
    style.configure(
        "Grid.TFrame",
        background=colors["frame"],
        borderwidth=1,
        relief="ridge",
    )
    return colors


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("MyLoRA Desktop")
        self.geometry("800x600")
        self.colors = apply_dark_theme(self)
        self.configure(bg=self.colors["bg"])

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        self.search_entry = ttk.Entry(top)
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.category_var = StringVar(self)
        self.category_menu = ttk.OptionMenu(top, self.category_var, "")
        self.category_menu.pack(side="left", padx=(0, 5))
        self.categories = []
        Thread(target=self._fetch_categories).start()

        ttk.Button(top, text="Search", command=self.load_data).pack(side="left")

        self.canvas = Canvas(self, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.grid_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.status = ttk.Label(self, text="")
        self.status.pack(fill="x", padx=10, pady=(0, 5))

        self.entries = []
        self.grid_photos = []
        self.after(100, self.load_data)

    def _clear_grid(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.grid_photos = []

    def load_data(self):
        query = self.search_entry.get() or "*"
        self.status.config(text="Loading...")
        category_name = self.category_var.get()
        category_id = None
        for c in self.categories:
            if c["name"] == category_name:
                category_id = c["id"]
                break
        Thread(target=self._fetch_and_populate, args=(query, category_id)).start()

    def _fetch_and_populate(self, query: str, category_id: int | None):
        try:
            entries = api.grid_data(q=query, category=category_id)
            self.entries = entries
            self._clear_grid()
            for idx, entry in enumerate(entries):
                row = idx // GRID_COLUMNS
                col = idx % GRID_COLUMNS
                frame = ttk.Frame(
                    self.grid_frame,
                    style="Grid.TFrame",
                    width=THUMB_SIZE,
                    height=THUMB_SIZE,
                )
                frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.grid_frame.columnconfigure(col, weight=1)

                canvas = Canvas(
                    frame,
                    width=THUMB_SIZE,
                    height=THUMB_SIZE,
                    highlightthickness=0,
                    bg=self.colors["frame"],
                )
                canvas.pack(expand=True, fill="both")
                canvas.bind("<Button-1>", lambda e, ent=entry: self.open_detail(ent))

                name = entry.get("name") or entry.get("filename")
                preview = entry.get("preview_url")
                if preview:
                    try:
                        url = api.preview_url(preview)
                        data = requests.get(url).content
                        img = Image.open(io.BytesIO(data))
                        img.thumbnail((THUMB_SIZE, THUMB_SIZE))
                        photo = ImageTk.PhotoImage(img)
                        canvas.create_image(0, 0, anchor="nw", image=photo)
                        self.grid_photos.append(photo)
                    except Exception:
                        canvas.create_text(
                            THUMB_SIZE / 2,
                            THUMB_SIZE / 2,
                            text="No preview",
                            fill=self.colors["fg"],
                        )
                else:
                    canvas.create_text(
                        THUMB_SIZE / 2,
                        THUMB_SIZE / 2,
                        text="No preview",
                        fill=self.colors["fg"],
                    )

                canvas.create_rectangle(
                    0,
                    THUMB_SIZE - 20,
                    THUMB_SIZE,
                    THUMB_SIZE,
                    fill="#000000",
                    outline="",
                    stipple="gray50",
                )
                canvas.create_text(
                    THUMB_SIZE / 2,
                    THUMB_SIZE - 10,
                    text=name,
                    fill=self.colors["fg"],
                    anchor="center",
                )
            self.status.config(text=f"Loaded {len(entries)} entries")
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def _fetch_categories(self):
        try:
            self.categories = api.categories()
            names = [""] + [c["name"] for c in self.categories]
            self.category_var.set(names[0])
            menu = self.category_menu["menu"]
            menu.delete(0, "end")
            for n in names:
                menu.add_command(label=n, command=lambda v=n: self.category_var.set(v))
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def open_detail(self, entry):
        DetailWindow(self, entry)


class DetailWindow(Toplevel):
    """Display preview images, metadata and download option for a LoRA entry."""

    def __init__(self, parent: Tk, entry: dict):
        super().__init__(parent)
        self.entry = entry
        self.colors = apply_dark_theme(self)
        self.configure(bg=self.colors["bg"])
        self.title(entry.get("name") or entry.get("filename"))
        self.geometry("600x600")

        self.preview_container = ttk.Frame(self)
        self.preview_container.pack(pady=10)

        self.meta_frame = ttk.Frame(self)
        self.meta_frame.pack(fill="both", expand=True, padx=10)

        ttk.Button(
            self,
            text="Download",
            style="Accent.TButton",
            command=lambda: self._download(entry["filename"]),
        ).pack(pady=5)

        Thread(target=self._load_details).start()

    def _load_details(self):
        stem = Path(self.entry.get("filename", "")).stem
        previews = api.list_previews(stem)
        metadata = api.fetch_metadata(self.entry["filename"])
        self.after(0, lambda: self._populate(previews, metadata))

    def _populate(self, previews: list[str], metadata: dict):
        self.photos = []
        if previews:
            for url in previews:
                try:
                    data = requests.get(url).content
                    img = Image.open(io.BytesIO(data))
                    img.thumbnail((180, 180))
                    photo = ImageTk.PhotoImage(img)
                    lbl = ttk.Label(self.preview_container, image=photo)
                    lbl.pack(side="left", padx=5)
                    self.photos.append(photo)
                except Exception:
                    pass
        else:
            ttk.Label(self.preview_container, text="No previews").pack()

        for key, value in sorted(metadata.items()):
            row = ttk.Frame(self.meta_frame)
            row.pack(fill="x", anchor="w")
            ttk.Label(row, text=f"{key}:", width=20, anchor="w").pack(side="left")
            ttk.Label(row, text=str(value), anchor="w").pack(side="left")

    def _download(self, filename: str):
        dest = filedialog.asksaveasfilename(initialfile=filename)
        if dest:
            api.download_file(filename, dest)


if __name__ == "__main__":
    app = App()
    app.mainloop()
