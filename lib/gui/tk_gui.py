from tkinter import *
from tkinter.ttk import Notebook

def create_app_window():
    root = Tk()
    root.title("RPA Tomorrow")
    root.geometry("1000x600")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Main tab control
    tab_control = Notebook(root)
    tab_control.grid(row=0, column=0, sticky=N+W+E+S)

    main_frame = Frame(tab_control, bg="white")
    create_automate_view(main_frame)
    tab_control.add(main_frame, text="Main")
    return root

def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

def create_scrollable_frame(root):
    canvas = Canvas(root, borderwidth=0, bg="white");
    inner_frame = Frame(canvas, borderwidth=0, bg="white")

    horizontal_scrollbar = Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=horizontal_scrollbar.set)
    
    vertical_scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vertical_scrollbar.set)

    canvas.grid(row=0, column=0, sticky=N+W+E+S)
    horizontal_scrollbar.grid(row=1, column=0, sticky=W+E)
    vertical_scrollbar.grid(row=0, column=1, sticky=N+S)

    canvas.create_window((1, 1), window=inner_frame, anchor="nw")
    inner_frame.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))
    return canvas

def create_automate_view(root):
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    input_field = Text(root, borderwidth=0, height=5)
    input_field.grid(row=0, column=0, sticky=N+W+E, padx=6, pady=6)

    view_frame = Frame(root, borderwidth=0, bg="white")
    view_frame.grid(row=1, column=0, sticky=N+W+E+S)
    view_frame.grid_rowconfigure(0, weight=1)
    view_frame.grid_columnconfigure(0, weight=1)
    canvas = create_scrollable_frame(view_frame)

    # send_email_cmd = create_email_command(command_frame)
    # send_email_cmd.place(x=0, y=0)
    # send_email_cmd.grid(row=0, column=0)
    # 
    # send_email_cmd2 = create_email_command(command_frame)
    # send_email_cmd2.grid(row=1, column=0)
    # send_email_cmd3 = create_email_command(command_frame)
    # send_email_cmd3.grid(row=2, column=0)
    # send_email_cmd4 = create_email_command(command_frame)
    # send_email_cmd4.grid(row=3, column=0)
    
    send_email_cmd5 = create_email_command(canvas)

class DraggableFrame(Frame):
    def __init__(self, canvas, **kwargs):
        Frame.__init__(self, canvas, **kwargs)
        self.canvas = canvas
        self.grip = None
        self.window = canvas.create_window((40, 40), window=self, anchor="nw")
        self.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))

    def set_grip(self, grip):
        self.grip = grip
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<ButtonRelease-1>", self.stop_move)
        self.grip.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = 0
        self.y = 0
        on_frame_configure(self.canvas)

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.canvas.winfo_x() + deltax
        y = self.canvas.winfo_y() + deltay
        self.canvas.move(self.window, x, y)

def create_draggable_node(grip, frame):
    grip.bind("<ButtonPress-1>", start_move(frame))
    grip.bind("<ButtonRelease-1>", stop_move(frame))
    grip.bind("<B1-Motion>", do_move(frame))

def create_email_command(canvas, **kwargs):
    frame = DraggableFrame(canvas, bg="skyblue", width=180, height=400)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=1)
    frame.grid_rowconfigure(3, weight=0)
    frame.grid_columnconfigure(0, weight=1)
    
    title = Label(frame, text="Send Email", bg="skyblue")
    title.grid(row=0, column=0, padx=6, pady=6)
    frame.set_grip(title)

    email_entry = Entry(frame, bg="skyblue", width=40, borderwidth=0)
    email_entry.grid(row=1, column=0, padx=6)
    email_entry.insert(0, "test@gmail.com")
    
    body_text = Text(frame, bg="skyblue", borderwidth=0, width=30, height=6, padx=6, pady=6)
    body_text.grid(row=2, column=0, padx=6, pady=6)
    body_text.insert(1.0, "This is just a test email")
    Label(frame, text="Next", bg="skyblue").grid(row=3, column=0)
    return frame
    
if __name__ == "__main__":
    root = create_app_window();
    
    root.mainloop()
