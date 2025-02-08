import tkinter as tk
from tkinter import messagebox, Toplevel, filedialog, ttk
from typing import Dict
from tkcalendar import Calendar
import datetime
import csv
from database import DatabaseManager

class ToDoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.root.title("To-Do List")
        self.root.geometry("400x600")

        # Inizializza il gestore del database
        self.db = DatabaseManager()

        self.task_ids: Dict[int, int] = {}  # Dizionario per mappare l'indice della lista agli ID del DB

        # Entry per nuovo task
        self.task_entry: tk.Entry = tk.Entry(root, width=40)
        self.task_entry.pack(pady=5)

        # Pulsante per selezionare la data di scadenza
        tk.Label(root, text="Scadenza:", font=("Arial", 10)).pack(pady=2)
        self.date_var: tk.StringVar = tk.StringVar()
        self.date_var.set(datetime.date.today().strftime("%d/%m/%Y"))
        self.date_button: tk.Button = tk.Button(root, textvariable=self.date_var, command=self.open_date_picker)
        self.date_button.pack(pady=5)

        # Selezione dell'ora di scadenza
        tk.Label(root, text="Ora di Scadenza:", font=("Arial", 10)).pack(pady=2)
        self.hour_var: tk.StringVar = tk.StringVar(value="12")
        self.minute_var: tk.StringVar = tk.StringVar(value="00")

        time_frame: tk.Frame = tk.Frame(root)
        time_frame.pack(pady=5)

        self.hour_spinbox: tk.Spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.hour_var, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT)
        tk.Label(time_frame, text=":").pack(side=tk.LEFT)
        self.minute_spinbox: tk.Spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.minute_var,
                                                     format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT)

        # barra di ricerca
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(root, textvariable=self.search_var, width=40)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_task)

        # Frame per i pulsanti principali
        button_frame_top = tk.Frame(root)
        button_frame_top.pack(pady=10)

        self.add_button = tk.Button(button_frame_top, text="➕ Aggiungi", bg="#4CAF50", font=("Arial", 12, "bold"), bd=3,
                                    padx=20, pady=10, command=self.add_task)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame_top, text="❌ Elimina", bg="#F44336", font=("Arial", 12, "bold"),
                                       bd=3, padx=20, pady=10, command=self.delete_task)
        self.delete_button.grid(row=0, column=1, padx=5, pady=5)

        self.complete_button = tk.Button(button_frame_top, text="👌🏻Completata", bg="#2196F3",
                                         font=("Arial", 12, "bold"), bd=3, padx=20, pady=10, command=self.complete_task)
        self.complete_button.grid(row=0, column=2, padx=5, pady=5)

        # Frame per i pulsanti dei filtri
        button_frame_bottom = tk.Frame(root)
        button_frame_bottom.pack(pady=10)

        self.show_all_button = tk.Button(button_frame_bottom, text="📋 Mostra Tutte", bg="#607D8B",
                                         font=("Arial", 11, "bold"), bd=3, padx=15, pady=8, command=self.load_tasks)
        self.show_all_button.grid(row=0, column=0, padx=5, pady=5)

        self.show_completed_button = tk.Button(button_frame_bottom, text="✅ Completate", bg="#795548",
                                               font=("Arial", 11, "bold"), bd=3, padx=15, pady=8,
                                               command=self.load_completed_tasks)
        self.show_completed_button.grid(row=0, column=1, padx=5, pady=5)

        self.show_pending_button = tk.Button(button_frame_bottom, text="🕒 Non Completate", bg="#FF9800",
                                             font=("Arial", 11, "bold"), bd=3, padx=15, pady=8,
                                             command=self.load_pending_tasks)
        self.show_pending_button.grid(row=0, column=2, padx=5, pady=5)

        # Frame per modifica ed esportazione
        button_frame_extra = tk.Frame(root)
        button_frame_extra.pack(pady=10)

        self.edit_button = tk.Button(button_frame_extra, text="✏️ Modifica", bg="#673AB7", font=("Arial", 12, "bold"),
                                     bd=3, padx=20, pady=10, command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT, padx=10)

        self.export_button = tk.Button(button_frame_extra, text="📤 Esporta in CSV", bg="#009688",
                                       font=("Arial", 12, "bold"), bd=3, padx=20, pady=10, command=self.export_to_csv)
        self.export_button.pack(side=tk.RIGHT, padx=10)

        # Lista attività
        self.task_list = tk.Listbox(root, width=50, height=20)
        self.task_list.pack(pady=10)
        self.task_list.bind("<<ListboxSelect>>", lambda event: self.load_task_into_entry())
        self.task_list.bind("<Double-Button-1>", lambda event: self.complete_task())
        self.load_tasks()

    def open_date_picker(self) -> None:
        self.date_window: Toplevel = Toplevel(self.root)
        self.date_window.title("Seleziona una data")
        self.date_window.geometry("300x300")

        tk.Label(self.date_window, text="Seleziona una data:").pack(pady=10)

        self.cal: Calendar = Calendar(self.date_window, selectmode='day', year=datetime.date.today().year,
                                      month=datetime.date.today().month, day=datetime.date.today().day)
        self.cal.pack(pady=20)

        confirm_button: tk.Button = tk.Button(self.date_window, text="Conferma", command=self.set_date)
        confirm_button.pack(pady=10)

    def search_task(self, event=None):
        """Filtra le attività in base al testo inserito nella barra di ricerca."""
        search_term = self.search_var.get().lower()
        self.task_list.delete(0, tk.END)

        tasks = self.db.fetch_all("SELECT id, task FROM tasks")
        for task_id, task in tasks:
            if search_term in task.lower():
                self.task_list.insert(tk.END, task)

    def set_date(self) -> None:
        selected_date: str = self.cal.get_date()
        self.date_var.set(selected_date)
        self.date_window.destroy()

    def add_task(self) -> None:
        task: str = self.task_entry.get()
        due_date: str = self.date_var.get()
        due_time: str = f"{self.hour_var.get()}:{self.minute_var.get()}"
        if task:
            self.db.execute_query(
                "INSERT INTO tasks (task, due_date, due_time) VALUES (?, ?, ?)",
                (task, due_date, due_time)
            )
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Attenzione", "Inserisci un'attività!")

    def delete_task(self) -> None:
        try:
            selected_index: tuple[int, ...] = self.task_list.curselection()
            if not selected_index:
                messagebox.showwarning("Attenzione", "Seleziona un'attività da eliminare!")
                return

            task_id: int = self.task_ids[selected_index[0]]

            self.db.execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.load_tasks()
        except Exception as e:
            messagebox.showwarning("Errore", f"Si è verificato un errore: {e}")

    def edit_task(self) -> None:
        try:
            selected_index = self.task_list.curselection()
            if not selected_index:
                messagebox.showwarning("Attenzione", "Seleziona un'attività da modificare!")
                return

            task_id = self.task_ids[selected_index[0]]
            new_task = self.task_entry.get().strip()
            new_due_date = self.date_var.get()
            new_due_time = f"{self.hour_var.get()}:{self.minute_var.get()}"

            if not new_task:
                messagebox.showwarning("Attenzione", "Il campo attività non può essere vuoto!")
                return

            # Usa DatabaseManager invece di connessioni dirette
            self.db.execute_query(
                "UPDATE tasks SET task = ?, due_date = ?, due_time = ? WHERE id = ?",
                (new_task, new_due_date, new_due_time, task_id)
            )

            self.load_tasks()
            messagebox.showinfo("Modifica completata", "Attività modificata con successo!")

        except Exception as e:
            messagebox.showwarning("Errore", f"Si è verificato un errore: {e}")

    def load_task_into_entry(self) -> None:
        try:
            selected_index = self.task_list.curselection()
            if not selected_index:
                messagebox.showwarning("Attenzione", "Seleziona un'attività da modificare!")
                return

            task_id = self.task_ids[selected_index[0]]

            # Usa DatabaseManager per ottenere i dettagli della task
            task_data = self.db.fetch_all(
                "SELECT task, due_date, due_time FROM tasks WHERE id = ?",
                (task_id,)
            )

            if task_data:
                task, due_date, due_time = task_data[0]
                self.task_entry.delete(0, tk.END)
                self.task_entry.insert(0, task)
                self.date_var.set(due_date)
                hour, minute = due_time.split(":")
                self.hour_var.set(hour)
                self.minute_var.set(minute)

        except Exception as e:
            messagebox.showwarning("Errore", f"Si è verificato un errore: {e}")

    def complete_task(self) -> None:
        try:
            selected_index = self.task_list.curselection()
            if not selected_index:
                messagebox.showwarning("Attenzione", "Seleziona un'attività da completare!")
                return

            task_id = self.task_ids[selected_index[0]]

            # Usa DatabaseManager invece di connessioni dirette
            self.db.execute_query(
                "UPDATE tasks SET completed = 1 WHERE id = ?",
                (task_id,)
            )

            self.load_tasks()
            messagebox.showinfo("Completata", "Attività segnata come completata!")

        except Exception as e:
            messagebox.showwarning("Errore", f"Si è verificato un errore: {e}")

    def load_tasks(self) -> None:
        self.task_list.delete(0, tk.END)
        self.task_ids.clear()

        tasks = self.db.fetch_all("SELECT id, task, due_date, due_time, completed FROM tasks ORDER BY due_date ASC, due_time ASC")

        for index, (task_id, task, due_date, due_time, completed) in enumerate(tasks):
            status = "[✓]" if completed else "[ ]"
            task_display = f"{status} {task} (Scadenza: {due_date} {due_time})"

            self.task_list.insert(tk.END, task_display)
            self.task_ids[index] = task_id  # Mappa l'indice all'ID del database

            # Cambia colore per i completati
            try:
                if completed:
                    self.task_list.itemconfig(index, {'fg': 'gray'})  # Assicurati di usare una stringa per 'fg'
            except tk.TclError:
                print(f"Errore nel colorare l'elemento {index}. Potrebbe essere fuori range.")

    # Carica solo le attività completate
    def load_completed_tasks(self) -> None:
        self.task_list.delete(0, tk.END)
        self.task_ids.clear()

        tasks = self.db.fetch_all(
            "SELECT id, task, due_date, due_time, completed FROM tasks WHERE completed = 1 ORDER BY due_date ASC, due_time ASC"
        )

        for index, (task_id, task, due_date, due_time, completed) in enumerate(tasks):
            status = "[✓]" if completed else "[ ]"
            task_display = f"{status} {task} (Scadenza: {due_date} {due_time})"

            self.task_list.insert(tk.END, task_display)
            self.task_ids[index] = task_id
            self.task_list.itemconfig(index, {'fg': 'gray'})  # Colore grigio per le attività completate

    # Carica solo le attività completate
    def load_pending_tasks(self) -> None:
        self.task_list.delete(0, tk.END)
        self.task_ids.clear()

        tasks = self.db.fetch_all(
            "SELECT id, task, due_date, due_time, completed FROM tasks WHERE completed = 0 ORDER BY due_date ASC, due_time ASC"
        )

        for index, (task_id, task, due_date, due_time, completed) in enumerate(tasks):
            status = "[✓]" if completed else "[ ]"
            task_display = f"{status} {task} (Scadenza: {due_date} {due_time})"

            self.task_list.insert(tk.END, task_display)
            self.task_ids[index] = task_id

    # Esporta tutte le attività in un file CSV
    def export_to_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")],
            title="Salva il file CSV"
        )

        if not file_path:  # Se l'utente annulla il salvataggio
            return

        tasks = self.db.fetch_all(
            "SELECT task, due_date, due_time, completed FROM tasks ORDER BY due_date ASC, due_time ASC")

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Attività", "Scadenza", "Ora", "Completata"])  # Intestazioni colonne

                for task, due_date, due_time, completed in tasks:
                    writer.writerow([task, due_date, due_time, "Sì" if completed else "No"])

            messagebox.showinfo("Esportazione completata", f"Le attività sono state salvate in:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore durante l'esportazione:\n{e}")