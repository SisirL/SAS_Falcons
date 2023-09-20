from tkinter import Tk, mainloop, ttk, Menu, Event, messagebox
import tkintermapview as tkmv
import sys
import platform
import sv_ttk
from PIL import Image, ImageTk

class App:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state("zoomed")
        self.root.title("SAS Falcons")
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        
        self.main_menu = Menu(self.root)
        self.root.configure(menu = self.main_menu)
        self.menu_view = Menu(self.main_menu, tearoff = False)
        self.menu_themes = Menu(self.menu_view, tearoff = False)
        self.main_menu.add_cascade(label = "View", menu = self.menu_view)
        self.menu_view.add_cascade(label = "Choose Theme...", menu = self.menu_themes)
        self.menu_themes.add_command(label = "Sunvalley dark", command = lambda theme = "dark":self.adjust_theme(newtheme = theme))
        self.menu_themes.add_command(label = "Sunvalley light", command = lambda theme = "light":self.adjust_theme(newtheme = theme))
        self.current_theme = "Sunvalley light"
        self.init_map()


        mainloop()
    
    
    """
    db = psdatabase
    table = data

    Location
    LatitudeL
    LongitudeL
    SourceType
    NearestSubstation
    LatitudeSS
    LongitudeSS
    PlantExists (at Location)
    PlantCapacity
    """
    lst = []#[(9.4097, 78.3643, "Kamuthi", 9.46912995084518, 78.4041097311129)]
    

    def get_data(self) -> None:
        from hbDatabasing import get_columns
        self.lst = get_columns(tablename = "data", columns = ["LatitudeL", "LongitudeL", "Location", "LatitudeSS", "LongitudeSS"])


    def init_map(self) -> None:
        mapview = tkmv.TkinterMapView(self.root, corner_radius = 5)
        self.get_data()
        # newicon = ImageTk.PhotoImage(Image.open("Map-Pointer.png").resize((28, 28)))
        self.marker_list = []
        for item in self.lst:
            temp = (0, )
            temp = temp + (mapview.set_marker(item[0], item[1], ""), )
            temp = temp + (mapview.set_marker(item[3], item[4], item[2]), )
            self.marker_list.append(temp[1:])
        mapview.place(relx = 0.1, rely = 0.05, relheight = 0.9, relwidth = 0.8)
        mapview.set_position(10.4097, 78.3643)
        mapview.set_zoom(7)


    def adjust_theme(self, newtheme: str) -> None:
        sv_ttk.set_theme(newtheme)
        self.current_theme = newtheme


if __name__ == "__main__":
    App()
