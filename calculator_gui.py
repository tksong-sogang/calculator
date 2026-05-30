import tkinter as tk


def click(value):
    current = entry.get()
    if value == "C":
        entry.delete(0, tk.END)
    elif value == "=":
        try:
            result = eval(current)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except ZeroDivisionError:
            entry.delete(0, tk.END)
            entry.insert(0, "Error: ÷0")
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    else:
        entry.insert(tk.END, value)


root = tk.Tk()
root.title("Calculator")
root.resizable(False, False)

entry = tk.Entry(root, font=("Arial", 24), justify="right", bd=0, bg="#f0f0f0")
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, ipady=12, sticky="ew")

buttons = [
    ["C", "(", ")", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "=", ""],
]

COLORS = {
    "C": ("#ff6b6b", "white"),
    "=": ("#4caf50", "white"),
    "/": ("#2196f3", "white"),
    "*": ("#2196f3", "white"),
    "-": ("#2196f3", "white"),
    "+": ("#2196f3", "white"),
    "(": ("#9e9e9e", "white"),
    ")": ("#9e9e9e", "white"),
}

for r, row in enumerate(buttons, start=1):
    for c, label in enumerate(row):
        if label == "":
            continue
        bg, fg = COLORS.get(label, ("#ffffff", "#333333"))
        colspan = 2 if label == "0" else 1
        btn = tk.Button(
            root,
            text=label,
            font=("Arial", 18, "bold"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            relief="flat",
            bd=0,
            padx=10,
            pady=14,
            command=lambda v=label: click(v),
        )
        btn.grid(row=r, column=c, columnspan=colspan, padx=4, pady=4, sticky="nsew")

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

root.mainloop()
