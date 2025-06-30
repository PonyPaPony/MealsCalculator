import tkinter as tk


class Autocomplete:
    def __init__(self):
        pass

    def setup_autocomplete(
        self, entry_widget: tk.Entry, suggestions, listbox_widget: tk.Listbox
    ):
        if any(not x for x in [entry_widget, suggestions, listbox_widget]):
            raise ValueError("Ошибка: Получения Данных")
        if any(not isinstance(x, tk.Widget) for x in [entry_widget, listbox_widget]):
            raise ValueError(
                "Ошибка: entry_widget и listbox_widget должны быть классом tkinter"
            )

        def update_suggestions(_=None):
            text = entry_widget.get().strip()
            listbox_widget.delete(0, tk.END)
            for word in suggestions:
                if word.lower().startswith(text.lower()):
                    listbox_widget.insert(tk.END, word)

        def fill_from_listbox(event):
            index = listbox_widget.nearest(event.y)
            selected = listbox_widget.get(index)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected.title())
            listbox_widget.delete(0, tk.END)

        def on_select(event):
            selected_item = listbox_widget.curselection()
            if selected_item:
                selected_item = listbox_widget.get(selected_item)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, selected_item.title())
                listbox_widget.delete(0, tk.END)

        entry_widget.bind("<KeyRelease>", update_suggestions)
        listbox_widget.bind("<ButtonPress>-1", fill_from_listbox)
        listbox_widget.bind("<<ListboxSelect>>", on_select)

        return update_suggestions
