import tkinter as tk
import threading
import assistant_backend

root = tk.Tk()
root.title("Assistive Scene Description System")
root.geometry("420x300")
root.resizable(False, False)


tk.Label(
    root,
    text="Assistive Scene Description",
    font=("Arial", 16, "bold")
).pack(pady=15)

status_label = tk.Label(
    root,
    text="Status: Idle",
    font=("Arial", 12)
)
status_label.pack(pady=10)


def start_system():
    status_label.config(text="Status: Running")
    assistant_backend.DESCRIBE = True
    threading.Thread(
        target=assistant_backend.run_assistant,
        daemon=True
    ).start()

def stop_system():
    assistant_backend.DESCRIBE = False
    status_label.config(text="Status: Paused")

def exit_system():
    assistant_backend.EXIT_APP = True
    root.destroy()


tk.Button(
    root,
    text="Start Assistant",
    width=20,
    font=("Arial", 12),
    command=start_system
).pack(pady=8)

tk.Button(
    root,
    text="Stop Description",
    width=20,
    font=("Arial", 12),
    command=stop_system
).pack(pady=8)

tk.Button(
    root,
    text="Exit",
    width=20,
    font=("Arial", 12),
    command=exit_system
).pack(pady=8)

tk.Label(
    root,
    text="Voice commands also work:\nStart / Stop / Exit",
    font=("Arial", 10)
).pack(pady=10)

root.mainloop()
