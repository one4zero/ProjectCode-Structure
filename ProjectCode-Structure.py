import os
import tkinter as tk
from tkinter import filedialog, messagebox

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp'}

def merge_files_to_txt(root_directory, output_file):
    current_script = os.path.abspath(__file__)
    with open(output_file, 'w', encoding='utf-8') as output:
        for dirpath, _, filenames in os.walk(root_directory):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                    continue
                file_path = os.path.join(dirpath, filename)
                if os.path.abspath(file_path) == current_script:
                    continue
                output.write(f"===== {file_path} =====\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        output.write(file.read())
                except Exception as e:
                    output.write(f"Error reading file: {e}\n")
                output.write("\n\n")

def scan_directory(directory, exclude_files):
    structure = []
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, directory)
        if relative_path == ".":
            relative_path = ""
        for d in dirs:
            structure.append(os.path.join(relative_path, d) + "/")
        for f in files:
            if f not in exclude_files and not any(f.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                structure.append(os.path.join(relative_path, f))
    return structure

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-a>', self.select_all)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy)
        self.context_menu.add_command(label="Вырезать", command=self.cut)
        self.context_menu.add_command(label="Выделить всё", command=self.select_all)
        self.bind('<Button-3>', self.show_context_menu)

    def copy(self, event=None):
        if self.tag_ranges(tk.SEL):
            self.event_generate('<<Copy>>')
        return "break"

    def cut(self, event=None):
        if self.tag_ranges(tk.SEL):
            self.event_generate('<<Cut>>')
        return "break"

    def select_all(self, event=None):
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        return "break"

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        self.root.geometry("800x600")
        self.center_window()
        self.selected_directory = tk.StringVar()
        self.text_result = CustomText(self.root, wrap=tk.WORD)
        self.setup_ui()

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

    def setup_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        tk.Entry(frame_top, textvariable=self.selected_directory, state="readonly", width=80).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_top, text="Выбрать директорию", command=self.choose_directory).pack(side=tk.LEFT)

        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(frame_buttons, text="Показать структуру каталога", command=self.show_directory_structure).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="Показать весь код", command=self.show_all_code).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="Копировать весь текст", command=self.copy_all_text).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_buttons, text="Горячие клавиши: Ctrl+C - копировать, Ctrl+X - вырезать, Ctrl+A - выделить всё").pack(side=tk.RIGHT, padx=5)

        self.text_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame_save = tk.Frame(self.root)
        frame_save.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(frame_save, text="Сохранить результат", command=self.save_result).pack(side=tk.RIGHT, padx=5)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)

    def show_directory_structure(self):
        directory = self.selected_directory.get()
        if not directory:
            messagebox.showerror("Ошибка", "Выберите директорию")
            return
        structure = scan_directory(directory, [])
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "\n".join(structure))

    def show_all_code(self):
        directory = self.selected_directory.get()
        if not directory:
            messagebox.showerror("Ошибка", "Выберите директорию")
            return
        output = []
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                    continue
                file_path = os.path.join(dirpath, filename)
                output.append(f"===== {file_path} =====")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        output.append(file.read())
                except Exception as e:
                    output.append(f"Error reading file: {e}")
                output.append("\n")
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "\n".join(output))

    def copy_all_text(self):
        self.text_result.tag_add(tk.SEL, "1.0", tk.END)
        self.text_result.event_generate("<<Copy>>")
        self.text_result.tag_remove(tk.SEL, "1.0", tk.END)

    def save_result(self):
        result = self.text_result.get(1.0, tk.END).strip()
        if not result:
            messagebox.showerror("Ошибка", "Нет данных для сохранения")
            return
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"{os.path.basename(self.selected_directory.get())}.txt"
        )
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(result)
                messagebox.showinfo("Успех", "Результат сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
