import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import datetime

# Esporta tutte le attività in un file CSV
def export_to_csv(db) -> None:
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    tasks = db.fetch_all("SELECT task FROM tasks")
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Attività"])
        writer.writerows(tasks)
    messagebox.showinfo("Esportazione completata", "File CSV salvato!")

# Controlla se ci sono attività in scadenza
def check_deadlines(app) -> None:
    now = datetime.datetime.now()
    tasks = app.db.fetch_all("SELECT task, due_date FROM tasks WHERE completed = 0")
    for task, due_date in tasks:
        task_datetime = datetime.datetime.strptime(due_date, "%d/%m/%Y")
        if (task_datetime - now).days == 0:
            messagebox.showwarning("Scadenza!", f"L'attività '{task}' scade oggi!")
    app.root.after(60000, check_deadlines, app)