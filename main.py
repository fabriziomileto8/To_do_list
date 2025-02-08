import tkinter as tk
from todo_app import ToDoApp

if __name__ == "__main__":
    root: tk.Tk = tk.Tk()
    app: ToDoApp = ToDoApp(root)
    root.mainloop()