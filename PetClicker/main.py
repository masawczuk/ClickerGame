import tkinter as tk
from PIL import Image, ImageTk

class ClickerGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Clicker Game")

        self.points = 0
        self.points_per_click = 1
        self.upgrade_cost = 10

        self.frame_img = Image.open("ramka.png")

        # Wczytaj tło i obrazek karma.png
        self.background_img_orig = Image.open("background/background_lvl1.png")
        self.original_img = Image.open("pies/pies1.png")
        self.img_width = 300
        self.img_height = 300

        self.canvas = tk.Canvas(master, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.click)

        # UI frames ...
        self.top_frame = tk.Frame(master, bg="#ffffff")
        self.top_frame.place(relx=0.5, rely=0.02, anchor="n")

        self.label = tk.Label(self.top_frame, text=f"Punkty: {self.points}", font=("Arial", 24), bg="#ffffff")
        self.label.pack(padx=10, pady=5)

        self.bottom_frame = tk.Frame(master, bg="#ffffff")
        self.bottom_frame.place(relx=0.5, rely=0.95, anchor="s")

        self.upgrade_button = tk.Button(self.bottom_frame, text=f"Ulepsz (+1 za klik) - Koszt: {self.upgrade_cost}", font=("Arial", 14), command=self.upgrade)
        self.upgrade_button.pack(padx=10, pady=5)

        self.info_label = tk.Label(self.bottom_frame, text="", font=("Arial", 12), fg="green", bg="#ffffff")
        self.info_label.pack(padx=10, pady=5)

        self.master.bind("<Configure>", self.draw)

        self.draw()

    def click(self, event=None):
        self.points += self.points_per_click
        self.update_ui()

    def upgrade(self):
        if self.points >= self.upgrade_cost:
            self.points -= self.upgrade_cost
            self.points_per_click += 1
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
            self.info_label.config(text="Ulepszenie kupione!", fg="green")
        else:
            self.info_label.config(text="Za mało punktów!", fg="red")
        self.update_ui()

    def update_ui(self):
        self.label.config(text=f"Punkty: {self.points}")
        self.upgrade_button.config(text=f"Ulepsz (+1 za klik) - Koszt: {self.upgrade_cost}")
        self.info_label.after(2000, lambda: self.info_label.config(text="", fg="green"))

    def draw(self, event=None):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        if width < 2 or height < 2:
            return

        # Skalowanie tła do rozmiaru okna
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS

        bg_resized = self.background_img_orig.resize((width, height), resample)
        self.bg_photo = ImageTk.PhotoImage(bg_resized)

        # Stały rozmiar obrazka karma.png
        img_resized = self.original_img.resize((self.img_width, self.img_height), resample)
        self.karma_photo = ImageTk.PhotoImage(img_resized)

        self.canvas.delete("all")

        # Wstaw tło
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        # Oblicz pozycję karma.png na środku
        x = (width - self.img_width) // 2
        y = (height - self.img_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.karma_photo)

        # Trzymaj referencje do zdjęć, aby nie zostały usunięte przez GC
        self.canvas.bg_photo = self.bg_photo
        self.canvas.karma_photo = self.karma_photo

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")
    root.resizable(True, True)

    game = ClickerGame(root)
    root.mainloop()