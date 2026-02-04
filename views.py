import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import logging
from database import DatabaseManager
from tkcalendar import DateEntry
from dateutil.relativedelta import relativedelta
import serial.tools.list_ports
from serial_manager import SerialManager

class AccessFrame(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager):
        super().__init__(master)
        self.db = db
        
        self.label_title = ctk.CTkLabel(self, text="Control de Acceso", font=("Roboto", 32, "bold"))
        self.label_title.pack(pady=30)

        self.entry_id = ctk.CTkEntry(self, placeholder_text="Ingrese ID / Documento", width=400, height=50, font=("Roboto", 24))
        self.entry_id.pack(pady=30)
        self.entry_id.bind("<Return>", lambda event: self.check_access())

        self.btn_check = ctk.CTkButton(self, text="Verificar Acceso", command=self.check_access, height=50, width=200, font=("Roboto", 20, "bold"))
        self.btn_check.pack(pady=15)

        self.status_label = ctk.CTkLabel(self, text="", font=("Roboto", 36, "bold"), wraplength=700)
        self.status_label.pack(pady=50)
        
        self.info_label = ctk.CTkLabel(self, text="", font=("Roboto", 24))
        self.info_label.pack(pady=10)

    def check_access(self):
        user_id = self.entry_id.get().strip()
        if not user_id:
            return
        
        member = self.db.get_member(user_id)
        
        if member:
            # member structure: 0:id, 1:name, 2:age, 3:addr, 4:phone, 5:reg_date, 6:end_date, 7:frozen, 8:frozen_date
            name = member[1]
            end_date_str = member[6]
            is_frozen = member[7]
            
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            if is_frozen:
                self.status_label.configure(text="MEMBRESÍA CONGELADA", text_color="orange")
                self.info_label.configure(text=f"Usuario: {name}")
                logging.info(f"Access DENIED (Frozen) for user: {user_id} ({name})")
            elif end_date >= datetime.now():
                days_left = (end_date - datetime.now()).days
                self.status_label.configure(text="ACCESO CONCEDIDO", text_color="green")
                self.info_label.configure(text=f"Bienvenido, {name}\nVence en {days_left + 1} días ({end_date_str})")
                logging.info(f"Access GRANTED for user: {user_id} ({name})")
            else:
                self.status_label.configure(text="MEMBRESÍA VENCIDA", text_color="red")
                self.info_label.configure(text=f"Usuario: {name}\nVenció el {end_date_str}")
                logging.warning(f"Access DENIED (Expired) for user: {user_id} ({name})")
                
        else:
            self.status_label.configure(text="USUARIO NO ENCONTRADO", text_color="red")
            self.info_label.configure(text="")
            logging.warning(f"Access DENIED (NotFound) for ID: {user_id}")
            
        self.entry_id.delete(0, 'end')

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager):
        super().__init__(master)
        self.db = db

        self.label_title = ctk.CTkLabel(self, text="Registrar Nuevo Miembro", font=("Roboto", 32, "bold"))
        self.label_title.pack(pady=30)
        
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(pady=10)

        self.entry_id = ctk.CTkEntry(self.form_frame, placeholder_text="Documento de Identidad (ID)", width=400, height=40, font=("Roboto", 16))
        self.entry_id.pack(pady=15)

        self.entry_name = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre Completo", width=400, height=40, font=("Roboto", 16))
        self.entry_name.pack(pady=15)

        self.entry_age = ctk.CTkEntry(self.form_frame, placeholder_text="Edad", width=400, height=40, font=("Roboto", 16))
        self.entry_age.pack(pady=15)

        self.entry_address = ctk.CTkEntry(self.form_frame, placeholder_text="Dirección", width=400, height=40, font=("Roboto", 16))
        self.entry_address.pack(pady=15)

        self.entry_phone = ctk.CTkEntry(self.form_frame, placeholder_text="Teléfono", width=400, height=40, font=("Roboto", 16))
        self.entry_phone.pack(pady=15)
        
        # DatePicker for Registration Date
        ctk.CTkLabel(self.form_frame, text="Fecha de Inicio:", anchor="w", font=("Roboto", 16)).pack(pady=(10,0), padx=5, anchor="w")
        self.date_reg = DateEntry(self.form_frame, width=30, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='y-mm-dd', font=("Roboto", 14))
        self.date_reg.pack(pady=10)

        self.btn_register = ctk.CTkButton(self, text="Registrar Miembro", command=self.register_member, height=50, width=250, font=("Roboto", 18, "bold"), fg_color="green", hover_color="darkgreen")
        self.btn_register.pack(pady=30)

    def register_member(self):
        uid = self.entry_id.get()
        name = self.entry_name.get()
        age = self.entry_age.get()
        addr = self.entry_address.get()
        phone = self.entry_phone.get()
        
        reg_date_obj = self.date_reg.get_date()
        reg_date_str = reg_date_obj.strftime("%Y-%m-%d")
        
        # Default 1 month expiry from picked date
        end_date_str = (reg_date_obj + relativedelta(months=1)).strftime("%Y-%m-%d")

        if not uid or not name:
            messagebox.showerror("Error", "El ID y Nombre son obligatorios")
            return

        success = self.db.add_member(uid, name, age, addr, phone, reg_date_str, end_date_str)
        if success:
            messagebox.showinfo("Éxito", f"Miembro {name} registrado correctamente")
            self.clear_form()
        else:
            messagebox.showerror("Error", "El ID ya existe en la base de datos")

    def clear_form(self):
        self.entry_id.delete(0, 'end')
        self.entry_name.delete(0, 'end')
        self.entry_age.delete(0, 'end')
        self.entry_address.delete(0, 'end')
        self.entry_phone.delete(0, 'end')

class MembersFrame(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager):
        super().__init__(master)
        self.db = db

        # Top Bar (Search)
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=10, pady=20)
        
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Buscar por Nombre o ID...", width=400, height=40, font=("Roboto", 16))
        self.search_entry.pack(side="left", padx=10)
        
        self.btn_search = ctk.CTkButton(self.top_bar, text="Buscar", width=120, height=40, font=("Roboto", 16, "bold"), command=self.refresh_list)
        self.btn_search.pack(side="left")
        
        self.btn_refresh = ctk.CTkButton(self.top_bar, text="Actualizar Lista", width=150, height=40, font=("Roboto", 16, "bold"), command=lambda: [self.search_entry.delete(0,'end'), self.refresh_list()])
        self.btn_refresh.pack(side="left", padx=10)

        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Lista de Miembros", label_font=("Roboto", 20, "bold"))
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_list()

    def refresh_list(self):
        # Clear current list
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get()
        if query:
            members = self.db.search_members(query)
        else:
            members = self.db.get_all_members()

        if not members:
            ctk.CTkLabel(self.scroll_frame, text="No se encontraron miembros.", font=("Roboto", 16)).pack(pady=20)
            return

        # Headers
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="ID", width=100, anchor="w", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Nombre", width=250, anchor="w", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Vencimiento", width=150, anchor="w", font=("Roboto", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Estado", width=150, anchor="w", font=("Roboto", 14, "bold")).pack(side="left", padx=5)

        for m in members:
            # m: id, name, end_date, is_frozen
            self.create_member_row(m)

    def create_member_row(self, member):
        mid, name, end_date, is_frozen = member
        
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row_frame, text=mid, width=100, anchor="w", font=("Roboto", 14)).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=name, width=250, anchor="w", font=("Roboto", 14)).pack(side="left", padx=5)
        
        # Color code expiration
        dt_end = datetime.strptime(end_date, "%Y-%m-%d")
        color = "black" # Default for Light Mode text
        status_text = "Activo"
        
        if is_frozen:
            color = "orange"
            status_text = "Congelado"
        elif dt_end < datetime.now():
            color = "red"
            status_text = "Vencido"
        else:
            color = "green"
        
        ctk.CTkLabel(row_frame, text=end_date, width=150, anchor="w", font=("Roboto", 14)).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=status_text, width=150, anchor="w", text_color=color, font=("Roboto", 14, "bold")).pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(row_frame, text="Gestionar", width=120, height=35, font=("Roboto", 14), command=lambda i=mid: self.open_edit_window(i))
        btn_edit.pack(side="right", padx=10)

    def open_edit_window(self, user_id):
        EditMemberWindow(self, self.db, user_id, self.refresh_list)

class EditMemberWindow(ctk.CTkToplevel):
    def __init__(self, master, db, user_id, callback_refresh):
        super().__init__(master)
        self.db = db
        self.user_id = user_id
        self.callback = callback_refresh
        self.title(f"Gestionar Miembro - {user_id}")
        self.geometry("600x750")
        
        self.member = self.db.get_member(user_id)
        # member: 0:id, 1:name, 2:age, 3:addr, 4:phone, 5:reg_date, 6:end_date, 7:frozen, 8:frozen_date

        self.label_title = ctk.CTkLabel(self, text=f"Editando: {self.member[1]}", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # Tabs for Edit Info vs Membership Actions
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabview.add("Información")
        self.tabview.add("Membresía")

        # --- INFO TAB ---
        self.entry_name = ctk.CTkEntry(self.tabview.tab("Información"), placeholder_text="Nombre", width=350, height=40, font=("Roboto", 16))
        self.entry_name.insert(0, self.member[1])
        self.entry_name.pack(pady=10)
        
        self.entry_age = ctk.CTkEntry(self.tabview.tab("Información"), placeholder_text="Edad", width=350, height=40, font=("Roboto", 16))
        if self.member[2]: self.entry_age.insert(0, str(self.member[2]))
        self.entry_age.pack(pady=10)
        
        self.entry_addr = ctk.CTkEntry(self.tabview.tab("Información"), placeholder_text="Dirección", width=350, height=40, font=("Roboto", 16))
        if self.member[3]: self.entry_addr.insert(0, self.member[3])
        self.entry_addr.pack(pady=10)
        
        self.entry_phone = ctk.CTkEntry(self.tabview.tab("Información"), placeholder_text="Teléfono", width=350, height=40, font=("Roboto", 16))
        if self.member[4]: self.entry_phone.insert(0, self.member[4])
        self.entry_phone.pack(pady=10)
        
        ctk.CTkButton(self.tabview.tab("Información"), text="Guardar Cambios", command=self.save_info, height=45, width=200, font=("Roboto", 16, "bold")).pack(pady=30)

        # --- MEMBERSHIP TAB ---
        self.mem_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Membresía"))
        self.mem_scroll.pack(fill="both", expand=True)

        status_text = "Estado: " + ("Congelado" if self.member[7] else "Activo")
        ctk.CTkLabel(self.mem_scroll, text=status_text, font=("Roboto", 18, "bold")).pack(pady=15)
        ctk.CTkLabel(self.mem_scroll, text=f"Vence: {self.member[6]}", font=("Roboto", 16)).pack(pady=5)

        # Manual Date Picker
        manual_frame = ctk.CTkFrame(self.mem_scroll)
        manual_frame.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(manual_frame, text="Cambiar fecha manualmente:", font=("Roboto", 14)).pack(pady=5)
        
        self.date_expiry = DateEntry(manual_frame, width=15, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd', font=("Roboto", 12))
        # Set date to current expiry
        try:
            curr_expiry = datetime.strptime(self.member[6], "%Y-%m-%d")
            self.date_expiry.set_date(curr_expiry)
        except:
            pass
        self.date_expiry.pack(pady=5)
        ctk.CTkButton(manual_frame, text="Guardar Nueva Fecha", command=self.save_manual_date, font=("Roboto", 14)).pack(pady=5)

        # Extend Buttons
        extend_frame = ctk.CTkFrame(self.mem_scroll)
        extend_frame.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(extend_frame, text="Extender Membresía", font=("Roboto", 16, "bold")).pack(pady=10)
        
        # Grid of buttons
        # 1 week, 15 days, 1 month, 2 months, 3 months, 6 months, 1 year
        buttons = [
            ("1 Semana", relativedelta(weeks=1)),
            ("15 Días", relativedelta(days=15)),
            ("1 Mes", relativedelta(months=1)),
            ("2 Meses", relativedelta(months=2)),
            ("3 Meses", relativedelta(months=3)),
            ("6 Meses", relativedelta(months=6)),
            ("1 Año", relativedelta(years=1))
        ]
        
        for text, delta in buttons:
            ctk.CTkButton(extend_frame, text=f"+ {text}", height=40, font=("Roboto", 14), command=lambda d=delta: self.extend_membership(d)).pack(pady=5, padx=30, fill="x")

        # Freeze
        freeze_text = "Descongelar" if self.member[7] else "Congelar"
        freeze_color = "green" if self.member[7] else "orange"
        ctk.CTkButton(self.mem_scroll, text=freeze_text, fg_color=freeze_color, height=45, font=("Roboto", 16, "bold"), command=self.toggle_freeze).pack(pady=30)

        # Delete (Bottom of Membership Tab or Info Tab - putting it in Info Tab makes sense too, but user asked "in gestionar")
        # Let's put it at the very bottom of the window (outside tabs) or bottom of info tab.
        # User said "in gestionar", usually a dangerous action is distinct.
        # Let's put a separator and a red button in the Info tab at the bottom.
        
        ctk.CTkLabel(self.tabview.tab("Información"), text="").pack(pady=10) # Spacer
        ctk.CTkButton(self.tabview.tab("Información"), text="ELIMINAR USUARIO", height=45, font=("Roboto", 14, "bold"), fg_color="red", hover_color="darkred", command=self.delete_user).pack(pady=20)


    def save_info(self):
        n = self.entry_name.get()
        a = self.entry_age.get()
        ad = self.entry_addr.get()
        p = self.entry_phone.get()
        
        self.db.update_member(self.user_id, n, a, ad, p)
        messagebox.showinfo("Info", "Datos actualizados")
        self.callback()
        self.destroy()

    def save_manual_date(self):
        new_date_obj = self.date_expiry.get_date()
        new_date_str = new_date_obj.strftime("%Y-%m-%d")
        self.db.set_membership_expiry(self.user_id, new_date_str)
        messagebox.showinfo("Info", f"Fecha actualizada a {new_date_str}")
        self.callback()
        self.destroy()

    def extend_membership(self, delta):
        # Calculate new date
        # Logic: if expired, start from today + delta
        # If not expired, start from current end date + delta
        current_end_str = self.member[6]
        current_end = datetime.strptime(current_end_str, "%Y-%m-%d")
        now = datetime.now()
        
        if current_end < now:
            base_date = now
        else:
            base_date = current_end
            
        new_end = base_date + delta
        new_end_str = new_end.strftime("%Y-%m-%d")
        
        self.db.set_membership_expiry(self.user_id, new_end_str)
        messagebox.showinfo("Info", f"Membresía extendida hasta {new_end_str}")
        self.callback()
        self.destroy()

    def toggle_freeze(self):
        self.db.toggle_freeze(self.user_id)
        self.callback()
        self.destroy()

    def delete_user(self):
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar a {self.member[1]}?\nEsta acción no se puede deshacer."):
            self.db.delete_member(self.user_id)
            messagebox.showinfo("Eliminado", "Usuario eliminado correctamente.")
            self.callback()
            self.destroy()

class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, db: DatabaseManager, serial_mgr: SerialManager, reload_callback):
        super().__init__(master)
        self.db = db
        self.serial_mgr = serial_mgr
        self.reload_callback = reload_callback

        self.label_title = ctk.CTkLabel(self, text="Administración y Configuración", font=("Roboto", 32, "bold"))
        self.label_title.pack(pady=30)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabview.add("General")
        self.tabview.add("Conexión Serial")

        # --- GENERAL ---
        self.gen_frame = self.tabview.tab("General")
        
        ctk.CTkLabel(self.gen_frame, text="Nombre del Gimnasio:", font=("Roboto", 16)).pack(pady=(20, 5))
        self.entry_gym_name = ctk.CTkEntry(self.gen_frame, width=400, height=40, font=("Roboto", 16))
        
        curr_name = self.db.get_config("gym_name", "GymBase")
        self.entry_gym_name.insert(0, curr_name)
        self.entry_gym_name.pack(pady=5)
        
        ctk.CTkButton(self.gen_frame, text="Guardar General", command=self.save_general, height=45, width=200, font=("Roboto", 16, "bold")).pack(pady=30)

        # --- SERIAL ---
        self.serial_frame = self.tabview.tab("Conexión Serial")

        ctk.CTkLabel(self.serial_frame, text="Configuración del Puerto Serial (Teclado)", font=("Roboto", 18, "bold")).pack(pady=20)

        ctk.CTkLabel(self.serial_frame, text="Puerto:", font=("Roboto", 16)).pack(pady=(10, 5))
        self.combo_port = ctk.CTkComboBox(self.serial_frame, width=300, height=35, font=("Roboto", 14))
        self.refresh_ports()
        self.combo_port.pack(pady=5)
        
        ctk.CTkButton(self.serial_frame, text="Refrescar Puertos", command=self.refresh_ports, width=150).pack(pady=5)

        ctk.CTkLabel(self.serial_frame, text="Baud Rate:", font=("Roboto", 16)).pack(pady=(20, 5))
        self.combo_baud = ctk.CTkComboBox(self.serial_frame, values=["9600", "19200", "38400", "57600", "115200"], width=300, height=35, font=("Roboto", 14))
        
        curr_baud = self.db.get_config("serial_baud", "9600")
        self.combo_baud.set(curr_baud)
        self.combo_baud.pack(pady=5)

        self.btn_save_serial = ctk.CTkButton(self.serial_frame, text="Guardar y Conectar", command=self.save_serial, height=45, width=220, font=("Roboto", 16, "bold"))
        self.btn_save_serial.pack(pady=30)
        
        self.status_conn = ctk.CTkLabel(self.serial_frame, text="Estado: Desconectado", font=("Roboto", 16, "bold"), text_color="red")
        self.status_conn.pack(pady=10)
        
        self.update_status()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if not ports:
            ports = ["No se detectaron puertos"]
        self.combo_port.configure(values=ports)
        
        # Select current if exists
        curr_port = self.db.get_config("serial_port", "")
        if curr_port and curr_port in ports:
            self.combo_port.set(curr_port)
        else:
            self.combo_port.set(ports[0])

    def save_general(self):
        name = self.entry_gym_name.get()
        self.db.set_config("gym_name", name)
        messagebox.showinfo("Guardado", "Configuración guardada")
        self.reload_callback() # Refresh titles and such

    def save_serial(self):
        port = self.combo_port.get()
        baud = self.combo_baud.get()
        
        if port == "No se detectaron puertos":
            messagebox.showerror("Error", "Seleccione un puerto válido")
            return

        self.db.set_config("serial_port", port)
        self.db.set_config("serial_baud", baud)
        
        # Restart serial
        self.serial_mgr.stop()
        self.serial_mgr.port = port
        self.serial_mgr.baudrate = int(baud)
        if self.serial_mgr.start():
            messagebox.showinfo("Éxito", "Conexión Serial Iniciada")
        else:
            messagebox.showerror("Error", "No se pudo conectar al puerto")
            
        self.update_status()

    def update_status(self):
        if self.serial_mgr.running:
            self.status_conn.configure(text=f"Estado: CONECTADO ({self.serial_mgr.port})", text_color="green")
        else:
            self.status_conn.configure(text="Estado: DESCONECTADO", text_color="red")
