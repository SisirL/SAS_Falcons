from tkinter import Tk, mainloop, ttk, Menu, Event, messagebox, Toplevel
import tkintermapview as tkmv
import sys
import platform
import sv_ttk
from hbDatabasing import init_db, get_columns, closestSubstation
import random
"""
db = psdatabase
table = plantStationdata
0 Location
1 LatitudeL
2 LongitudeL
3 SourceType
4 NearestSubstation
5 LatitudeSS
6 LongitudeSS
7 PlantOwner (at Location)
8 PlantCapacity
"""

class App:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('SAS Falcons!!')
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        init_db()
        self._demand_markers_list = []
        self._is_demand_displayed = False
        self.colours = ['#ff0000', '#3366ff', '#cc00cc', '#00ffcc', '#009933', '#996633']
        self._demand_paths = []
        
        self.main_menu = Menu(self.root)
        self.root.configure(menu=self.main_menu)
        self.menu_options = Menu(self.main_menu, tearoff=False)
        self.menu_themes = Menu(self.menu_options, tearoff=False)
        self.main_menu.add_cascade(label='Options', menu=self.menu_options)
        self.menu_options.add_cascade(label='Choose Theme...', menu=self.menu_themes)
        self.menu_themes.add_command(label='Sunvalley dark', command=lambda theme='dark':self.adjust_theme(newtheme=theme))
        self.menu_themes.add_command(label='Sunvalley light', command=lambda theme='light':self.adjust_theme(newtheme=theme))
        
        self.menu_assistance = Menu(self.main_menu, tearoff=False)
        # self.menu_docs = Menu(self.menu_assistance, tearoff=False)
        # self.menu_assistance.add_cascade(label='')
        self.menu_options.add_cascade(label='Assisstance', menu=self.menu_assistance)
        self.setup_menu = Menu(self.menu_assistance, tearoff=False)
        self.menu_assistance.add_command(label='Solar Plant Setup', command=lambda source='solar-s': self.show_setup(source))
        self.menu_assistance.add_command(label='Solar Plant Legal Requirements', command=lambda source='solar-l': self.show_setup(source))
        self.menu_assistance.add_command(label='Hydel Plant Setup', command=lambda source='hydel-s': self.show_setup(source))
        self.menu_assistance.add_command(label='Hydel Plant Legal Requirements', command=lambda source='hydel-l': self.show_setup(source))
        self.menu_assistance.add_command(label='Wind Farm Setup', command=lambda source='wind-s': self.show_setup(source))
        self.menu_assistance.add_command(label='Wind Farm Legal Requirements', command=lambda source='wind-l': self.show_setup(source))

        self.current_theme = 'light'
        sv_ttk.set_theme('light')

        self.login()
        mainloop()

    def login_successful(self) -> None:
        self.init_map()
        self.source_choice_ui()
        self.toggle_demand_display()
        self.remove_login_page()
    
    def login(self, approved:bool=False) -> bool:
        if approved: return True
        self.frm_login = ttk.LabelFrame(self.root)
        self.lbl_login_email = ttk.Label(self.frm_login, text='Email:')
        self.ent_login_email = ttk.Entry(self.frm_login)
        self.ent_login_email.focus_set()
        self.lbl_login_pwd = ttk.Label(self.frm_login, text='Password:')
        self.ent_login_pwd = ttk.Entry(self.frm_login, show='*')
        self.btn_login_proceed = ttk.Button(self.frm_login, text='Proceed', command=self.approve_login)
        self.lbl_login_email.grid(row=1, column=1, sticky='w')
        self.ent_login_email.grid(row=1, column=2)
        self.lbl_login_pwd.grid(row=2, column=1, sticky='w')
        self.ent_login_pwd.grid(row=2, column=2)
        self.btn_login_proceed.grid(row=3, column=1, columnspan=2)
        self.frm_login.pack(pady=300)
        self.btn_login_signup = ttk.Button(self.frm_login, text='Create Account', command=lambda: self.show_create_acc_page(True))

    def approve_login(self) -> None:
        if (self.ent_login_email.get(), self.ent_login_pwd.get()) in get_columns(tablename='users', columns=['emailid', 'pass']):
            self.login_successful()
        else:
            messagebox.showerror('Login Failed', 'The login credentials were incorrect.')

    def remove_login_page(self) -> None:
        self.frm_login.destroy()

    def create_user_acc(self) -> None:
        self.show_create_acc_page()

    def show_create_acc_page(self, is_from_login:bool = False):
        if is_from_login:
            self.remove_login_page()
        self.frm_newacc = ttk.Frame(self.root)
        self.lbl_signup_email = ttk.Label(self.frm_newacc, text='Email:')
        self.ent_signup_email = ttk.Entry(self.frm_newacc)
        self.lbl_signup_pwd1 = ttk.Label(self.frm_newacc, text='Password:')
        self.ent_signup_pwd1 = ttk.Entry(self.frm_newacc)
        self.lbl_signup_pwd2 = ttk.Label(self.frm_newacc, text='Reenter Password:')
        self.ent_signup_pwd2 = ttk.Entry(self.frm_newacc)
        self.btn_signup_proceed = ttk.Button(self.frm_newacc, text='Create Account', command=self.approve_signup)
        # grid/pack/place all
        self.lbl_signup_email.grid(row=1, column=1, sticky='w')
        self.ent_signup_email.grid(row=1, column=2)
        self.lbl_signup_pwd1.grid(row=2, column=1, sticky='w')
        self.ent_signup_pwd1.grid(row=2, column=2)

    def approve_signup(self) -> None:
        email_id = self.ent_signup_email.get()
        pwd = ''
        if self.ent_signup_pwd1.get() == self.ent_signup_pwd2.get():
            pwd = self.ent_signup_pwd1.get()
        if len(email_id) > 40:
            messagebox.showerror('Login Credentials', 'Email-ID too long (>40 characters).')
            self.ent_signup_email.delete(0, 'end')
        if len(pwd) > 40:
            messagebox.showerror('Login Credentials', 'Password too long (>40 characters).')
            self.ent_signup_pwd1.delete(0, 'end')
            self.ent_signup_pwd2.delete(0, 'end')
        # insert into db

    def show_setup(self, sourcetype: str) -> None:
        if sourcetype.lower() == 'solar-s':
            help_window = Toplevel(self.root)
            help_window.title('Guidance for New Solar Power Plants')
            help_window.minsize(400, 300)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Setup-Solar.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        elif sourcetype.lower() == 'solar-l':
            help_window = Toplevel(self.root)
            help_window.title('Legal Requirements for New Solar Power Plants')
            help_window.minsize(400, 300)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Legal-Solar.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        elif sourcetype.lower() == 'hydel-s':
            help_window = Toplevel(self.root)
            help_window.title('Guidance for New Hydel Power Plants')
            help_window.minsize(400, 300)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Setup-Hydel.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        elif sourcetype.lower() == 'hydel-l':
            help_window = Toplevel(self.root)
            help_window.title('Legal Reuirements for New Hydel Power Plants')
            help_window.minsize(400, 300)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Legal-Hydel.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        elif sourcetype.lower() == 'wind-l':
            help_window = Toplevel(self.root)
            help_window.title('Legal Requirements for New Hydel Power Plants')
            help_window.minsize(400, 400)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Legal-Hydel.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        elif sourcetype.lower() == 'wind-s':
            help_window = Toplevel(self.root)
            help_window.title('Guidance for New Wind Farms')
            help_window.minsize(400, 300)
            help_window.focus_set()
            l1 = ttk.Label(help_window)
            with open('Setup-Wind.txt', 'r') as file:
                l1.configure(text=file.read())
            l1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

    def get_data(self, sourcetype: str) -> list:
        return get_columns(tablename='plantstationdata', columns=['LatitudeL', 'LongitudeL', 'Location', 'LatitudeSS', 'LongitudeSS', 'PlantOwner', 'NearestSubstation'], constraint=('SourceType', sourcetype))

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
            lst = get_columns(tablename='plantstationdata', columns=['Location', 'SourceType', 'PlantCapacity', 'PlantOwner'], constraint=('Location', info[2]))
            event_marker.display_window = ttk.Frame(self.root, border=15, takefocus=False)
            lbl_close = ttk.Label(event_marker.display_window, text='x', cursor='hand2')
            lbl_close.pack(anchor='e')
            lbl_close.bind('<Button-1>', self.delete_marker_info)
            l1 = ttk.Label(event_marker.display_window, text=f'{lst[0][0]!s}')
            l2 = ttk.Label(event_marker.display_window)
            if event_marker.text == lst[0][0]:
                l2.configure(text=event_marker.text + ' Power Plant')
            else:
                l2.configure(text=f'Connected to {lst[0][0]}')
            # capacity:
            if lst[0][2] is not None:
                capacity = list(str(int(float(lst[0][2]))))
                for i in range(-3, -1*len(capacity)-1, -4):
                    capacity.insert(i, ',')
                capacity = ''.join(capacity)
            else:
                capacity = '-'
            l3 = ttk.Label(event_marker.display_window, text=f'Capacity: {capacity}')
            if lst[0][3] == 'None':
                l4 = ttk.Label(event_marker.display_window, text=f'Future Power Plant', foreground='#006600')
            else:
                l4 = ttk.Label(event_marker.display_window, text=f'Owner: {lst[0][3]!s}')
            l1.pack(anchor='w')
            l2.pack(anchor='w')
            l3.pack(anchor='w')
            l4.pack(anchor='w')
            event_marker.display_window.place(x=self.root.winfo_pointerx()-self.root.winfo_x(), y=self.root.winfo_pointery()-self.root.winfo_y(), anchor='center')
            event_marker._is_displaying = True
        
    def delete_marker_info(self, event: Event):
        event.widget.master.destroy()

    def source_choice_ui(self) -> None:
        self.btn_solar = ttk.Button(self.root, text='Solar', command=lambda sourcetype='Solar':self.select_source(sourcetype), takefocus=False)
        self.btn_wind = ttk.Button(self.root, text='Wind', command=lambda sourcetype='Wind':self.select_source(sourcetype), takefocus=False)
        self.btn_hydro = ttk.Button(self.root, text='Hydro', command=lambda sourcetype='Hydro':self.select_source(sourcetype), takefocus=False)
        self.btn_demand = ttk.Button(self.root, text='Demand Toggle', command=self.toggle_demand_display, takefocus=False)
        # self.btn_solar = ttk.Button(self.root, text='', command=lambda sourcetype='':self.select_source(sourcetype), takefocus=False)
        self.btn_solar.place(relx=0.85, relwidth=0.1, rely=0.2)
        self.btn_wind.place(relx=0.85, relwidth=0.1, rely=0.3)
        self.btn_hydro.place(relx=0.85, relwidth=0.1, rely=0.4)
        self.btn_demand.place(relx=0.85, relwidth=0.1, rely=0.5)

    def select_source(self, sourcetype: str) -> None:
        self.mapview.delete_all_marker()
        self.mapview.delete_all_path()
        if self._is_demand_displayed:
            self._is_demand_displayed = False
            self.toggle_demand_display()
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        self.marker_list = []
        if sourcetype.lower() == 'solar':
            for item in self.get_data(sourcetype='solar'):
                temp = (0, )
                temp = temp + (self.mapview.set_marker(item[0], item[1], item[2], command=self._show_marker_info), )
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[6], command=self._show_marker_info), )
                if item[5] is None:
                    self.mapview.set_path([(item[0], item[1]), (item[3], item[4])], color='#ffff00')
                else:
                    self.mapview.set_path([(item[0], item[1]), (item[3], item[4])])
                temp[1].data = item
                temp[2].data = item
                temp[1]._is_displaying = False
                temp[2]._is_displaying = False
                self.marker_list.append(temp)
        elif sourcetype.lower() == 'wind':
            for item in self.get_data(sourcetype='wind'):
                temp = (0, )
                temp = temp + (self.mapview.set_marker(item[0], item[1], item[2], command=self._show_marker_info), )
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[6], command=self._show_marker_info), )
                self.mapview.set_path([(item[0], item[1]), (item[3], item[4])])
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
                temp = temp + (self.mapview.set_marker(item[3], item[4], item[6], command=self._show_marker_info), )
                self.mapview.set_path([(item[0], item[1]), (item[3], item[4])])
                temp[1].data = item
                temp[2].data = item
                temp[1]._is_displaying = False
                temp[2]._is_displaying = False
                self.marker_list.append(temp)

    def toggle_demand_display(self) -> None:
        if self._is_demand_displayed:
            for marker in self._demand_markers_list:
                marker.delete()
            self._is_demand_displayed = False
            for paths in self._demand_paths:
                paths.delete()
        else:
            for item in get_columns(tablename='demanddata', columns=['location', 'latitude', 'longitude']):
                self._demand_markers_list.append(self.mapview.set_marker(float(item[1]), float(item[2]), item[0]))
            self._is_demand_displayed = True
            self.demand_to_src()

    def demand_to_src(self) -> None:
        for item in get_columns(tablename='demanddata', columns=['location', 'latitude', 'longitude']):
            self.src_lat, self.src_long = closestSubstation(float(item[1]), float(item[2]))
            self._demand_paths.append(self.mapview.set_path([(float(item[1]), float(item[2])), (self.src_lat, self.src_long)], color='#00cc00'))

    def adjust_theme(self, newtheme: str) -> None:
        sv_ttk.set_theme(newtheme)
        self.current_theme = newtheme


if __name__ == '__main__':
    App()