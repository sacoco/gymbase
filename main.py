import customtkinter as ctk
from database import DatabaseManager
from views import AccessFrame, RegisterFrame, MembersFrame, AdminFrame
from serial_manager import SerialManager

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class GymApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize DB
        self.db = DatabaseManager()
        
        # Initialize Serial
        port = self.db.get_config("serial_port", "")
        baud = int(self.db.get_config("serial_baud", "9600"))
        self.serial_mgr = SerialManager(port, baud, self.on_serial_data)
        
        # Try connect on start if configured
        if port:
            self.serial_mgr.start()

        # Configure window
        gym_name = self.db.get_config("gym_name", "GymBase")
        self.title(f"{gym_name} - Gestión")
        self.geometry("1100x700")
        
        # Layout: Grid 1x2 (Sidebar, Main Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_frames()
        self.create_footer()
        
        # Start at Home
        self.select_frame("access")

    def on_serial_data(self, code):
        # This runs in thread, schedule update on main thread
        # We want to put this code into entry_id of AccessFrame and trigger check
        self.after(0, lambda: self.handle_serial_code(code))

    def handle_serial_code(self, code):
        print(f"Serial Code Received: {code}")
        # Only if we are on access frame, or maybe always force access frame?
        # Let's force switch to access frame to show result
        self.select_frame("access")
        access_frame = self.frames["access"]
        access_frame.entry_id.delete(0, 'end')
        access_frame.entry_id.insert(0, code)
        access_frame.check_access()

    def reload_config(self):
        # Update Title
        gym_name = self.db.get_config("gym_name", "GymBase")
        self.title(f"{gym_name} - Gestión")
        # Update Sidebar Title
        self.logo_label.configure(text=gym_name)

    def create_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.footer_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.footer_label = ctk.CTkLabel(self.footer_frame, text="Desarrollado por sacoco", text_color="gray", font=("Roboto", 14))
        self.footer_label.pack(pady=2)

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        gym_name = self.db.get_config("gym_name", "GymBase")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=gym_name, font=ctk.CTkFont(size=28, weight="bold"), text_color="black")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_access = ctk.CTkButton(self.sidebar_frame, text="Inicio / Acceso", font=("Roboto", 16), height=40, text_color="white", command=lambda: self.select_frame("access"))
        self.btn_access.grid(row=1, column=0, padx=20, pady=15)
        
        self.btn_register = ctk.CTkButton(self.sidebar_frame, text="Registrar Miembro", font=("Roboto", 16), height=40, text_color="white", command=lambda: self.select_frame("register"))
        self.btn_register.grid(row=2, column=0, padx=20, pady=15)
        
        self.btn_members = ctk.CTkButton(self.sidebar_frame, text="Lista de Miembros", font=("Roboto", 16), height=40, text_color="white", command=lambda: self.select_frame("members"))
        self.btn_members.grid(row=3, column=0, padx=20, pady=15)
        
        self.btn_admin = ctk.CTkButton(self.sidebar_frame, text="Administración", font=("Roboto", 16), height=40, text_color="white", fg_color="gray40", hover_color="gray30", command=lambda: self.select_frame("admin"))
        self.btn_admin.grid(row=4, column=0, padx=20, pady=15)

    def create_frames(self):
        self.frames = {}
        
        self.frames["access"] = AccessFrame(self, self.db)
        self.frames["register"] = RegisterFrame(self, self.db)
        self.frames["members"] = MembersFrame(self, self.db)
        self.frames["admin"] = AdminFrame(self, self.db, self.serial_mgr, self.reload_config)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew")
            
    def select_frame(self, name):
        # Update buttons state
        # Helper to set colors
        default_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        inactive_color = ("gray75", "gray25")
        
        self.btn_access.configure(fg_color=inactive_color if name != "access" else default_color)
        self.btn_register.configure(fg_color=inactive_color if name != "register" else default_color)
        self.btn_members.configure(fg_color=inactive_color if name != "members" else default_color)
        self.btn_admin.configure(fg_color=inactive_color if name != "admin" else "gray40") # Keep Admin distinct or similar

        
        # Show frame
        frame = self.frames[name]
        frame.tkraise()
        
        # Optional: refresh data if needed
        if name == "members" and hasattr(frame, "refresh_list"):
            frame.refresh_list()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = GymApp()
    app.mainloop()
