from tkinter import Tk, mainloop, ttk, Menu, Event, messagebox
import tkintermapview as tkmv
import sys
import platform
import sv_ttk
from PIL import Image, ImageTk
from hbDatabasing import init_db, get_columns

class App:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('SAS Falcons')
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        init_db()
        
        self.main_menu = Menu(self.root)
        self.root.configure(menu=self.main_menu)
        self.menu_view = Menu(self.main_menu, tearoff=False)
        self.menu_themes = Menu(self.menu_view, tearoff=False)
        self.main_menu.add_cascade(label='View', menu=self.menu_view)
        self.menu_view.add_cascade(label='Choose Theme...', menu=self.menu_themes)
        self.menu_themes.add_command(label='Sunvalley dark', command=lambda theme='dark':self.adjust_theme(newtheme=theme))
        self.menu_themes.add_command(label='Sunvalley light', command=lambda theme='light':self.adjust_theme(newtheme=theme))
        self.current_theme = 'Sunvalley light'
        sv_ttk.set_theme('light')

        self.init_map()
        self.source_choice_ui()

        mainloop()
    
    # get data from db
    """
    db = psdatabase
    table = data
    0 Location
    1 LatitudeL
    2 LongitudeL
    3 SourceType
    4 NearestSubstation
    5 LatitudeSS
    6 LongitudeSS
    7 PlantExists (at Location)
    8 PlantCapacity
    """
    def get_data(self, sourcetype: str) -> list:
        return get_columns(tablename='data', columns=['LatitudeL', 'LongitudeL', 'Location', 'LatitudeSS', 'LongitudeSS'], constraint=('SourceType', sourcetype))

    def init_map(self) -> None:
        self.mapview = tkmv.TkinterMapView(self.root, corner_radius=5)
        self.mapview.place(relx=0.1, rely=0.05, relheight=0.9, relwidth=0.7)
        self.mapview.set_position(10.4097, 78.3643)
        self.mapview.set_zoom(7)

    def _show_marker_info(self, event_marker) -> None:
        info = event_marker.data
        if event_marker._is_displaying:
            event_marker.display_window.destroy()
            event_marker._is_displaying = False
        else:
            lst = get_columns(tablename='data', columns=['Location', 'SourceType', 'PlantCapacity'], constraint=('Location', info[2]))
            event_marker.display_window = ttk.Frame(self.root, border=15, takefocus=False)
            l1 = ttk.Label(event_marker.display_window, text=f'{lst[0][0]!s}')
            l2 = ttk.Label(event_marker.display_window, text=f'{lst[0][1]!s} Power Plant')
            l3 = ttk.Label(event_marker.display_window, text=f'Capacity: {lst[0][2]!s}W')
            l1.pack(anchor='w')
            l2.pack(anchor='w')
            l3.pack(anchor='w')
            event_marker.display_window.place(x=self.root.winfo_pointerx()-self.root.winfo_x(), y=self.root.winfo_pointery()-self.root.winfo_y(), anchor='n')
            event_marker._is_displaying = True

    def source_choice_ui(self) -> None:
        self.btn_solar = ttk.Button(self.root, text='Solar', command=lambda sourcetype='Solar':self.select_source(sourcetype), takefocus=False)
        self.btn_wind = ttk.Button(self.root, text='Wind', command=lambda sourcetype='Wind':self.select_source(sourcetype), takefocus=False)
        self.btn_hydro = ttk.Button(self.root, text='Hydro', command=lambda sourcetype='Hydro':self.select_source(sourcetype), takefocus=False)
        # self.btn_solar = ttk.Button(self.root, text='', command=lambda sourcetype='':self.select_source(sourcetype), takefocus=False)
        # self.btn_solar = ttk.Button(self.root, text='', command=lambda sourcetype='':self.select_source(sourcetype), takefocus=False)
        self.btn_solar.place(relx=0.85, relwidth=0.1, rely=0.25)
        self.btn_wind.place(relx=0.85, relwidth=0.1, rely=0.35)
        self.btn_hydro.place(relx=0.85, relwidth=0.1, rely=0.45)

    def select_source(self, sourcetype: str) -> None:
        self.mapview.delete_all_marker()
        self.marker_list = []
        if sourcetype.lower() == 'solar':
            for item in self.get_data(sourcetype='solar'):
                temp = (0, )
                temp = temp + (self.mapview.set_marker(item[0], item[1], item[2], command=self._show_marker_info), )
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[2], command=self._show_marker_info), )
                temp[1].data = item
                temp[2].data = item
                temp[1]._is_displaying = False
                temp[2]._is_displaying = False
                self.marker_list.append(temp)
        elif sourcetype.lower() == 'wind':
            for item in self.get_data(sourcetype='wind'):
                temp = (0, )
                temp = temp + (self.mapview.set_marker(item[0], item[1], item[2], command=self._show_marker_info), )
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[2], command=self._show_marker_info), )
                temp[1].data = item
                temp[2].data = item
                temp[1]._is_displaying = False
                temp[2]._is_displaying = False
                self.marker_list.append(temp)
        elif sourcetype.lower() == 'hydro':
            self.marker_list = []
            for item in self.get_data(sourcetype='hydro'):
                temp = (0, )
                temp = temp + (self.mapview.set_marker(item[0], item[1], item[2], command=self._show_marker_info), )
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[2], command=self._show_marker_info), )
                temp[1].data = item
                temp[2].data = item
                temp[1]._is_displaying = False
                temp[2]._is_displaying = False
                self.marker_list.append(temp)

    def adjust_theme(self, newtheme: str) -> None:
        sv_ttk.set_theme(newtheme)
        self.current_theme = newtheme


if __name__ == '__main__':
    App()