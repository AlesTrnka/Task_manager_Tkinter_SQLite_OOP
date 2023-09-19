from task import Task
from database import TaskDtb
import tkinter as tk
from tkinter import ttk, font
import customtkinter as ctk
from datetime import datetime
import time
import threading
from tkcalendar import DateEntry
from CTkMessagebox import CTkMessagebox


class App(ctk.CTk):
    def __init__(self, title):
        super().__init__()
        self.title(title)
        self.geometry('600x650')
        self.resizable(False, False)
        self.configure(fg_color='#2b2b2b')
        self.header = Header(self)          # Horní nadpisová část
        self.work_field = WorkField(self)   # Pracovní pole - vstupy a tabulka
        self.mainloop()


class Header(ctk.CTkFrame):
    """
    Horní nadpisová část obsahující název aplikace a aktuální čas.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(side='top', expand=True, fill='both')
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.create_header_widgets()
        self.show_time()

    # WIDGETY
    def create_header_widgets(self):
        # Nadpis - Název aplikace
        self.title_label = ctk.CTkLabel(self,
            text = 'Úkolníček - aplikace pro správu vašich úkolů',
            font = ('Segoe UI', 18))
        self.title_label.grid(column = 0, row = 1, columnspan = 2, rowspan=2, sticky="ne")

        # Aktuální čas v hlavičce aplikace
        self.time_label = ctk.CTkLabel(self, font = ('Segoe UI', 14))
        self.time_label.grid(column=2, row=0, sticky='ne', padx=10)

    def show_time(self):
        # Zobrazení aktuálního času
        self.time = time.strftime('%H:%M:%S')
        self.time_label.configure(text=self.time)
        self.after(1000, self.show_time)


class WorkField(ctk.CTkFrame):
    """
    Pracovní pole pod nadpisovou částí, zahrnující vstupní pole pro zadání nového úkolu a výpis stávajících úkolů.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(expand=True, fill='both', side='top', padx=7)

        self.dtb = TaskDtb()
        self.parent.protocol("WM_DELETE_WINDOW", self.close_dtb)    # Uzavře databázi po ukončení aplikace
        self.results_field = ResultsField(self)     # Pole s tabulkou
        self.table = self.results_field.table
        self.input_field = InputField(self)         # Pole se vstupy - zadání nového úkolu

        self.view_current_tasks()
        self.thread_for_alarm()

    def thread_for_alarm(self):
        # Start vlákna pro připomenutí úkolů
        t1=threading.Thread(target=self.set_alarm)
        t1.daemon = True
        t1.start()

    def set_alarm(self):
        # Kontrola časů naplánovaných úkolů a připomenutí úkolu v novém okně
        current_tasks = []
        while True:
            time_now = datetime.now()
            tasks = self.dtb.view_tasks()
            for task in tasks:
                date = datetime.strptime(task[1][:-3], '%Y-%m-%d %H:%M') # Převede na objekt datetime
                if date <= time_now and task not in current_tasks:  # Pro úkoly s časem stejným nebo menším než aktuání čas
                    current_task_data = [task[1][:-3], task[2], task[3]]
                    remind = Reminder(self, current_task_data, self.dtb, self.table)    # Připomenutí aktuálnío úkolu
                    current_tasks.append(task)
            time.sleep(60)

    def view_current_tasks(self):
        # Aktualizace naplánovaných úkolů v tabulce
        for child in self.table.get_children():
            self.table.delete(child)
        tasks = self.dtb.view_tasks()
        for task in tasks:
            self.table.insert("", 'end', iid=task[0], text="", values = (task[1][:-3], task[2], task[3].replace('\n', " ")))

    def show_notification(self, title, message, icon):
        # Zobrazí notifikaci
        messagebox = CTkMessagebox(title=title, message=message, icon=icon)

    def close_dtb(self):
        # Uzavře databázi a kurzor po ukončení aplikace
        self.dtb.c.close()
        self.dtb.conn.close()
        self.parent.destroy()


class InputField(ctk.CTkFrame):
    """
    Pole vlevo se vstupy pro zadání nového úkolu.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3), weight = 1)
        self.pack(expand=True, fill='x', side='top', padx=3, pady=10)

        self.table = self.parent.table
        self.dtb = self.parent.dtb

        self.create_input_widgets()

    # WIDGETY
    def create_input_widgets(self):
        # Vytvoření vstupních widgetů a umístění v poli

        # Nadpis pro název úkolu
        self.label_subject = ctk.CTkLabel(self, text='Název úkolu:', font=('Segoe UI', 12))
        self.label_subject.grid(column=0, row=0, sticky='wn', pady=3, padx=10)

        # Vstupní pole pro název úkolu
        self.entry_subject = ctk.CTkEntry(self, fg_color='#1e1e1e')
        self.entry_subject.grid(column=1, row=0, columnspan='4', sticky='we', pady=5, padx=10)

        # Nadpis ke kalendáři
        self.label_cal = ctk.CTkLabel(self, text='Termín:', font=('Segoe UI', 12))
        self.label_cal.grid(column=0, row=1, sticky='wn', pady=3, padx=10)

        # Stylování kalendáře, roletky pro hodiny a minuty
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('my.DateEntry',
                        fieldbackground='',
                        background='#353638',
                        foreground='#FFFFFF')
        style.map('my.DateEntry', background=[('selected', '#22559b')])
        style.configure('TCombobox',
                        fieldbackground='',
                        background='#353638',
                        foreground='#FFFFFF',
                        arrowcolor='#FFFFFF',
                        selectbackground='#353638')
        style.map('TCombobox', background=[('selected', '#22559b')])

        # Kalendář
        self.cal = DateEntry(self, selectmode='day', mindate=datetime.today() , date_pattern='dd-mm-y', justify='center', font=('Segoe UI', 12), width=12, style='my.DateEntry')
        self.cal.grid(column=1, row=1, columnspan=2, pady=3, padx=6, sticky='w')

        # Nadpis k zadání hodin a minut k úkolu;
        self.label_time = ctk.CTkLabel(self, text='Čas připomenutí (h : m):', font=('Segoe UI', 12))
        self.label_time.grid(column=3, row=1, sticky='e')

        # Roletka pro výběr hodiny úkolu
        self.hours_var = tk.StringVar(self)
        self.hours = ttk.Combobox(self, textvariable=self.hours_var, values=[i for i in range(24)], width=3, font=('Segoe UI', 12))
        self.hours_var.set('9')
        self.hours.grid(column=4, row=1, sticky='w', padx=50)

        # Dvojtečka mezi hodinami a minutami
        self.label_dots = ctk.CTkLabel(self, text=':', font=('Segoe UI', 12))
        self.label_dots.grid(column=4, row=1)

        # Roletka pro výběr minuty úkolu
        self.minutes_var = tk.StringVar(self)
        self.minutes = ttk.Combobox(self, textvariable=self.minutes_var, values=(['00'] + [i for i in range(10, 51, 10)]), width=3, font=('Segoe UI', 12))
        self.minutes_var.set('00')
        self.minutes.grid(column=4, row=1, sticky='e', padx=55)

        # Nadpis k textovému poli pro podrobnosti k úkolu
        self.label_details = ctk.CTkLabel(self, text='Podrobnosti:', font=('Segoe UI', 12))
        self.label_details.grid(column=0, row=2, sticky='wn', pady=3, padx=10)

        # Textové pole k zadání podrobností k úkolu
        self.text_details = ctk.CTkTextbox(self, height=120, border_width=1)
        self.text_details.grid(column=1, row=2, columnspan=4, sticky='we', pady=3, padx=10)

        # Tlačítko pro přidání nového úkolu
        self.add_button = ctk.CTkButton(self, text='Přidej úkol', command = lambda: self.save_task())
        self.add_button.grid(column=4, row=3, sticky='e', pady=10, padx=10)

    def save_task(self):
        # Zaznamená úkol do tabulky a SQLite databáze
        if self.entry_subject.get():
            # Získání dat ze vstupních widgetů
            subject = self.entry_subject.get()
            date = self.cal.get_date()
            time = f'{self.hours_var.get()}:{self.minutes_var.get()}'
            date = datetime.strptime((f'{date}, {time}'), '%Y-%m-%d, %H:%M')  # na objekt datetime
            details = self.text_details.get('0.0', 'end')

            tasks = self.dtb.view_tasks()
            task_instance = Task(date, subject, details)
            self.dtb.save_task(task_instance)
            self.parent.view_current_tasks()        # Aktualizace tabulky

            self.entry_subject.delete(0, 'end')
            self.text_details.delete('0.0', 'end')

            WorkField.show_notification(self, 'Info', 'Úkol byl přidán', 'info')


class ResultsField(ctk.CTkFrame):
    """
    Pole s tabulkou v dolní části aplikace, ve které jsou zobrazeny stávající úkoly.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.pack(side="bottom", fill='x', expand=True, padx=3, pady=10)
        self.grid_columnconfigure((0, 1, 2, 3), weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3), weight = 1)

        self.dtb = self.parent.dtb
        self.create_results_widgets()

    # WIDGETY
    def create_results_widgets(self):
        # Vytvoření widgetů a rozložení pro zobrazení naplánovaných úkolů
        style_table = ttk.Style()
        style_table.theme_use('clam')
        style_table.configure("Treeview",
                            background="#2a2d2e",
                            foreground="#c2c1c0",
                            rowheight=25,
                            fieldbackground="#404747",
                            fieldbordercolor='#353638',
                            font=('Segoe UI', 11))
        style_table.map('Treeview', background=[('selected', '#22559b')])

        style_table.configure("Treeview.Heading",
                            background="#353638",
                            foreground="white",
                            font=('Segoe UI', 12),
                            borderwidth=0)
        style_table.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style_table.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Tabulka k zobrazení naplánovaných úkolů
        self.table = ttk.Treeview(self, style='Treeview')
        self.table['columns']=('date', 'subject', 'detail')
        self.table.column('#0', width=0, stretch='no')
        self.table.column('date', anchor='w', width=20)
        self.table.column('subject', anchor='w', width=60)
        self.table.column('detail', anchor='w', width=150)
        self.table.heading('#0', text='')
        self.table.heading('date', text='Datum', anchor='w')
        self.table.heading('subject', text='Název úkolu', anchor='w')
        self.table.heading('detail', text='Podrobnosti', anchor='w')
        self.table.grid(column=0, row=1, columnspan=4, rowspan=2, sticky='we', padx=10)

        # Tlačítko k editaci naplánovaného úkolu
        self.detail_item_button = ctk.CTkButton(self, text='Zobrazit úkol', fg_color='#525252', command = lambda: self.details_item())
        self.detail_item_button.grid(column=2, row=3, columnspan=3, sticky='e', padx=160, pady=10)

        # Tlačítko k odstranění úkolu z tabulky a SQLite databáze
        self.delete_button = ctk.CTkButton(self, text='Odstranit úkol', fg_color='#411C1C', text_color='#DF6262', border_width=0, command = lambda: self.butt_del_items())
        self.delete_button.grid(column=3, row=3, sticky='e', padx=10, pady=10)

    def butt_del_items(self):
        # Odstraní označený úkol z tabulky i z databáze
        for i in self.table.selection():
            values_from_table = self.table.item(i)['values']
            values_for_dtb = (values_from_table[0]+':00', values_from_table[1])   # Úprava dat, aby se shodovala s dtb
            self.table.delete(i)
            self.dtb.delete_task(values_for_dtb)
            WorkField.show_notification(self, 'Upozornění', 'Úkol byl odstraněn', 'info')

    def details_item(self):
        # Vyvolá okno pro editaci označeného úkolu
        if len(self.table.selection()) == 1:
            table_data = (self.table.item(self.table.selection())['values'])
            tasks = self.dtb.view_tasks()
            for task in tasks:
                if table_data[0]==task[1][:-3] and table_data[1]==task[2]:
                    item_data = (task[1][:-3], task[2], task[3])

            detail_item = Reminder(self, item_data, self.dtb, self.table, title='Detail úkolu')    # Okno s detaily úkolu


class EditItem(ctk.CTkToplevel):
    """
    Okno pro editaci naplánovaného úkolu.
    """
    def __init__(self, parent, item_data, dtb, table):
        super().__init__(parent)
        self.parent = parent
        self.item_data = item_data
        self.dtb = dtb
        self.table = table

        self.title('Editace úkolu')
        self.geometry('650x250')
        self.configure(fg_color='#353638')
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3), weight = 1)

        self.grab_set()     # Okno bude v popředí a jediné aktivn
        InputField.create_input_widgets(self)
        self.create_edit_widgets()
        self.fill_old_data(self.item_data)  # Vyplní editační formulář stávajícími daty

    # WIDGETY
    def create_edit_widgets(self):
        # Vytvoření widgetů a rozložení v okně pro editaci naplánovaných úkolů

        # Skryje tlačítko pro přidání úkolu
        self.add_button.grid_forget()

        # Tlačítko pro uložení změn v naplánovaném úkolu
        self.edit_button = ctk.CTkButton(self, text='Ulož změny', command = lambda: self.update_item(self.item_data))
        self.edit_button.grid(column=3, row=3, columnspan=4, sticky='e', padx=160, pady=3)

        # Tlačítko pro zrušení změn v editačním okně, zavře editační ono
        self.cancel_button = ctk.CTkButton(self, text='Zrušit', fg_color='#525252', command = lambda: self.destroy())
        self.cancel_button.grid(column=4, row=3, sticky='e', pady=3, padx=10)

    def fill_old_data(self, item_data):
        # Vyplní editační okno stávajícími daty
        self.entry_subject.insert(0, item_data[1])
        d=datetime.strptime(item_data[0][0:10], '%Y-%m-%d')
        self.cal.set_date(d)
        self.hours_var.set(item_data[0][11:13])
        self.minutes_var.set(item_data[0][14:16])
        self.text_details.insert(0.0, item_data[2])

    def update_item(self, current_data):
        # Zaznamená změny dat úkolu do tabulky i databáze, zobrazí notifikaci
        subject = self.entry_subject.get()
        date = self.cal.get_date()
        time = f'{self.hours_var.get()}:{self.minutes_var.get()}'
        date = datetime.strptime((f'{date}, {time}'), '%Y-%m-%d, %H:%M')
        details = self.text_details.get('0.0', 'end')

        values = (date, subject, details)
        current_data = (current_data[0]+':00', current_data[1])

        self.dtb.update_task(values, current_data)   # Zaznamenání do SQLite dtb
        WorkField.view_current_tasks(self)

        self.destroy()
        WorkField.show_notification(self, 'Upozornění', 'Úkol byl upraven', 'info')


class Reminder(ctk.CTkToplevel):
    """
    Okno pro připomenutí úkolu.
    """
    def __init__(self, parent, item_data, dtb, table, title='Připomenutí'):
        super().__init__(parent)
        self.parent = parent
        self.item_data = item_data
        self.dtb = dtb
        self.table = table

        self.title(title)
        self.geometry('600x250')

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3), weight = 1)

        self.grab_set()     # Okno bude v popředí a jediné aktivní
        InputField.create_input_widgets(self)
        EditItem.fill_old_data(self, self.item_data)
        self.create_reminder_widgets()

    # WIDGETY
    def create_reminder_widgets(self):
        # Vytvoření widgetů a rozložení v okně pro připomenutí naplánovaných úkolů

        # Skryje nepotřené widgety
        self.cal.grid_forget()
        self.hours.grid_forget()
        self.label_dots.grid_forget()
        self.minutes.grid_forget()
        self.add_button.grid_forget()

        # Uzamkne pole vstupní pole a upraví styl
        self.label_subject.configure(text_color='#9fa1a6')
        self.label_cal.configure(text_color='#9fa1a6')
        self.label_time.configure(text='Čas připomenutí:', text_color='#9fa1a6')
        self.label_details.configure(text_color='#9fa1a6')
        self.entry_subject.configure(state='disabled', fg_color='#303030', font=('Segoe UI', 14, 'italic'), text_color='#cfcfcf', border_width=0)
        self.text_details.configure(state='disabled', fg_color='#303030', font=('Segoe UI', 14, 'italic'), text_color='#cfcfcf', border_width=0)


        self.cal_var = tk.StringVar(self)

        # Label s datumem připomenutí úkolu
        self.label_cal_value = ctk.CTkLabel(self, textvariable=self.cal_var, font=('Segoe UI', 13, 'italic'), text_color='#cfcfcf')
        self.cal_var.set(self.item_data[0][:10])    # Nastavení textvariable labelu s datumem
        self.label_cal_value.grid(column=2, row=1, columnspan=3, sticky='w', padx=7)

        self.time_var = tk.StringVar(self)

        # Label s časem připomenutí úkolu
        self.label_time_value = ctk.CTkLabel(self, textvariable=self.time_var, font=('Segoe UI', 13, 'italic'), text_color='#cfcfcf')
        self.time_var.set(self.item_data[0][11:])   # Nastavení textvariable labelu s časem
        self.label_time_value.grid(column=4, row=1, sticky='w', padx=25)

        # Tlačítko - úkol splněn, vymaže úkol z tabulky i databáze
        self.accept_button = ctk.CTkButton(self, text='Splněno', command = lambda: self.accept_task())
        self.accept_button.grid(column=4, row=3, sticky='e', pady=3, padx=10)

        # Tlačítko pro editaci připomenutého úkolu, odemkne vstupní pole k úpravě dat úkolu
        self.edit_button = ctk.CTkButton(self, text='Editovat', fg_color='#525252', command = lambda: self.open_edit_window())
        self.edit_button.grid(column=3, row=3, columnspan=4, sticky='e', pady=3, padx=160)

        # Tlačítko k uložení změn připomenutého úkolu
        self.save_button = ctk.CTkButton(self, text='Ulož změny', command = lambda: EditItem.update_item(self, self.item_data))

    def accept_task(self):
        # Potvrdí splnění úkolu. Vymaže z tabulky i SQLite dtb
        item_data_for_dtb = (self.item_data[0]+':00', self.item_data[1])   # Data ve formátu jako v dtb
        self.dtb.delete_task(item_data_for_dtb)
        WorkField.view_current_tasks(self)  #  Aktualizace tabulky po vymazání úkolu
        self.destroy()

    def open_edit_window(self):
        # Vyvolá editační ono
        self.withdraw()     # Zneviditelní připomínkové okno
        edit_window = EditItem(self, self.item_data, self.dtb, self.table)
        edit_window.wait_window()  # Čeká, až se editační ono zavře
        self.destroy()  # Zavře neviditelné připomínkové okno
