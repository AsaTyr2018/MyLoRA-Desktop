"""Basic Tkinter client for the MyLoRA API."""

from tkinter import Tk, Listbox, Entry, Button, Label, END, Scrollbar, RIGHT, Y
from threading import Thread
import api


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("MyLoRA Desktop")
        self.geometry("600x400")

        self.search_entry = Entry(self)
        self.search_entry.pack(fill='x', padx=5, pady=5)

        self.search_btn = Button(self, text="Search", command=self.load_data)
        self.search_btn.pack(pady=5)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox = Listbox(self, yscrollcommand=scrollbar.set)
        self.listbox.pack(expand=True, fill='both', padx=5, pady=5)
        scrollbar.config(command=self.listbox.yview)

        self.status = Label(self, text="", anchor='w')
        self.status.pack(fill='x')

        self.after(100, self.load_data)

    def load_data(self):
        query = self.search_entry.get() or '*'
        self.status.config(text="Loading...")
        Thread(target=self._fetch_and_populate, args=(query,)).start()

    def _fetch_and_populate(self, query: str):
        try:
            entries = api.grid_data(q=query)
            self.listbox.delete(0, END)
            for entry in entries:
                name = entry.get('name') or entry.get('filename')
                self.listbox.insert(END, name)
            self.status.config(text=f"Loaded {len(entries)} entries")
        except Exception as exc:
            self.status.config(text=f"Error: {exc}")


if __name__ == '__main__':
    app = App()
    app.mainloop()
