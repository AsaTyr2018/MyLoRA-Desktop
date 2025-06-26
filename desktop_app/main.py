"""Basic Tkinter client for the MyLoRA API."""

from tkinter import (
    Tk,
    Listbox,
    Entry,
    Button,
    Label,
    END,
    Scrollbar,
    RIGHT,
    Y,
    Toplevel,
    StringVar,
    OptionMenu,
    filedialog,
)
from threading import Thread
import io
from PIL import Image, ImageTk
import requests
import api


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("MyLoRA Desktop")
        self.geometry("600x400")

        self.search_entry = Entry(self)
        self.search_entry.pack(fill='x', padx=5, pady=5)

        # Category dropdown
        self.category_var = StringVar(self)
        self.category_var.set('')
        self.category_menu = OptionMenu(self, self.category_var, '')
        self.category_menu.pack(fill='x', padx=5, pady=5)
        self.categories = []
        Thread(target=self._fetch_categories).start()

        self.search_btn = Button(self, text="Search", command=self.load_data)
        self.search_btn.pack(pady=5)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox = Listbox(self, yscrollcommand=scrollbar.set)
        self.listbox.pack(expand=True, fill='both', padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        scrollbar.config(command=self.listbox.yview)

        self.status = Label(self, text="", anchor='w')
        self.status.pack(fill='x')

        self.entries = []
        self.after(100, self.load_data)

    def load_data(self):
        query = self.search_entry.get() or '*'
        self.status.config(text="Loading...")
        category_name = self.category_var.get()
        category_id = None
        for c in self.categories:
            if c['name'] == category_name:
                category_id = c['id']
                break
        Thread(target=self._fetch_and_populate, args=(query, category_id)).start()

    def _fetch_and_populate(self, query: str, category_id: int | None):
        try:
            entries = api.grid_data(q=query, category=category_id)
            self.entries = entries
            self.listbox.delete(0, END)
            for entry in entries:
                name = entry.get('name') or entry.get('filename')
                self.listbox.insert(END, name)
            self.status.config(text=f"Loaded {len(entries)} entries")
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def _fetch_categories(self):
        try:
            self.categories = api.categories()
            names = [''] + [c['name'] for c in self.categories]
            self.category_var.set(names[0])
            menu = self.category_menu['menu']
            menu.delete(0, 'end')
            for n in names:
                menu.add_command(label=n, command=lambda v=n: self.category_var.set(v))
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")

    def on_select(self, event):
        if not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        entry = self.entries[idx]
        DetailWindow(self, entry)


class DetailWindow(Toplevel):
    """Display preview image and download option for a LoRA entry."""

    def __init__(self, parent: Tk, entry: dict):
        super().__init__(parent)
        self.title(entry.get('name') or entry.get('filename'))
        self.geometry('400x400')

        preview = entry.get('preview_url')
        self.img_label = Label(self)
        self.img_label.pack(pady=10)
        if preview:
            try:
                url = api.preview_url(preview)
                data = requests.get(url).content
                img = Image.open(io.BytesIO(data))
                img.thumbnail((350, 350))
                self.photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.photo)
            except Exception:
                self.img_label.config(text='Failed to load preview')
        else:
            self.img_label.config(text='No preview')

        Button(
            self,
            text='Download',
            command=lambda: self._download(entry['filename']),
        ).pack(pady=5)

    def _download(self, filename: str):
        dest = filedialog.asksaveasfilename(initialfile=filename)
        if dest:
            api.download_file(filename, dest)


if __name__ == '__main__':
    app = App()
    app.mainloop()
