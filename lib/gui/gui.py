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

    main_frame = Frame(tab_control)
    create_automate_view(main_frame)
    tab_control.add(main_frame, text="Main")

    return root

def populate(frame):
    for row in range(100):
        Label(frame, text="%s" % row, width=3, borderwidth="1", 
                 relief="solid").grid(row=row, column=0)
        t="this is the second column for row %s" %row
        Label(frame, text=t).grid(row=row, column=1)


def create_scrollable_frame(root):
    def onFrameConfigure(canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas = Canvas(root, borderwidth=0, bg="white");
    inner_frame = Frame(canvas, borderwidth=0, bg="white")

    horizontal_scrollbar = Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=horizontal_scrollbar.set)
    
    vertical_scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vertical_scrollbar.set)

    canvas.grid(row=0, column=0, sticky=N+W+E+S)
    horizontal_scrollbar.grid(row=1, column=0, sticky=W+E)
    vertical_scrollbar.grid(row=0, column=1, sticky=N+S)

    canvas.create_window((4,4), window=inner_frame, anchor="nw")
    inner_frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    return inner_frame

def create_automate_view(root):
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    input_field = Text(root, height=5)
    input_field.grid(row=0, column=0, sticky=N+W+E)

    view_frame = Frame(root, borderwidth=0, bg="white")
    command_frame = create_scrollable_frame(view_frame)
    view_frame.grid(row=1, column=0, sticky=N+W+E+S)
    view_frame.grid_rowconfigure(0, weight=1)
    view_frame.grid_columnconfigure(0, weight=1)

    send_email_cmd = create_email_command(command_frame)
    send_email_cmd.grid(row=0, column=0)

    send_email_cmd2 = create_email_command(command_frame)
    send_email_cmd2.grid(row=1, column=0)

def create_email_command(root, **kwargs):
    frame = Frame(root, bg="skyblue", width=180, height=400)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=1)
    frame.grid_rowconfigure(3, weight=0)
    frame.grid_columnconfigure(0, weight=1)
    
    Label(frame, text="Send Email", bg="skyblue").grid(row=0, column=0, padx=6, pady=6)
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
