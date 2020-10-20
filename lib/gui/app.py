import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master;
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.sidebar_frame = tk.Frame(self, bg="yellow", width=40)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.content_frame = tk.Frame(self)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        self.header_frame = tk.Frame(self.content_frame, bg="dodgerblue", height=40)
        self.header_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.input_frame = tk.Frame(self.content_frame)
        self.input_frame.pack(side=tk.TOP, fill=tk.BOTH)
        self.input_field = tk.Text(self.input_frame, height=3)
        self.input_field.pack(side=tk.LEFT, padx=6, pady=6)
                
        self.visualize_frame = tk.Frame(self.content_frame, bg="lightgray", height=500)
        self.visualize_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_input)
        self.send_button.pack(side=tk.RIGHT, padx=6)

    def send_input(self):
        input = self.input_field.get(1.0, tk.END)
        self.command = SendEmailWiget(self.visualize_frame, "Send email", "johndoe@gmail.com", input)
        self.command.pack()
        self.command.place(x=40, y=40, height=100, width=100)

class FloatingWindow(tk.Frame):
    def __init__(self, master, title):
        super().__init__(master)
        self.master = master
        self.grip = tk.Label(self, text=title)
        self.grip.pack(fill=tk.X)
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<ButtonRelease-1>", self.stop_move)
        self.grip.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.x = deltax
        self.y = deltay
        self.pack(side=tk.RIGHT, padx=self.x, pady=self.y)

class SendEmailWiget(FloatingWindow):
    def __init__(self, master, title, recipient, content):
        super().__init__(master, title)
        self.width = 200;
        self.master = master;
        self.bg = "red"

        self.recipient_entry = tk.Entry(self)
        self.recipient_entry.insert(0, recipient)
        self.recipient_entry.pack()

        self.content_entry = tk.Text(self, height=5)
        self.content_entry.insert(1.0, recipient)
        self.content_entry.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("RPA Tomorrow")
    app.master.geometry("1000x600")
    app.master.maxsize(1000, 600)
    app.mainloop()
