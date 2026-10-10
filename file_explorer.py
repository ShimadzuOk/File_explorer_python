import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import pathlib,os
import subprocess

current_path = ""

def select_folder():
    global current_path
    folder = filedialog.askdirectory()
    if folder == "":return
    current_path = pathlib.Path(folder)  
    content = sort_path()

    try:
        listbox.delete(0, tk.END)
        if content:
            for i in content:
                if i.is_file():listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                else:listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
        else: listbox.insert(0,"No content")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def open_clicked(event):
    global current_path
    selected = listbox.get(listbox.curselection()[0]).strip("\U0001F4C4\U0001F4C1 ")
    if not selected or selected == "No content": return 
    path = current_path.joinpath(selected)

    try:
        if path.is_file():
            os.startfile(str(path))
            return
        
        listbox.delete(0, tk.END)
        content = sort_path(path)
        if not content: 
            current_path = path
            listbox.insert(tk.END,"No content")
            return
        for i in content:
            if i.is_file():listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
            else:listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
        current_path = path
    except Exception as e:
        messagebox.showerror("Error", str(e))


def show_details(event=None):
    selection = listbox.curselection()
    if not selection:return

    filename = listbox.get(selection[0])
    if filename == "No content":  
        details_var.set("Null")
        return
    full_path = str(current_path.joinpath(listbox.selection_get().strip("\U0001F4C4\U0001F4C1 ")))

    try:
        size = os.path.getsize(full_path)

        if os.path.isfile(full_path):
            file_type = "File"
        else:
            file_type = "Folder"

        details_var.set(
            f"Name: {filename} | "
            f"Type: {file_type} | "
            f"Size: {size} bytes"
        )

    except Exception as e:
        details_var.set(str(e))

def go_back():
    global current_path
    if not current_path: return
    previuos = current_path.parent
    content = sort_path(previuos)
    try:
        listbox.delete(0, tk.END)
        if content:
            for i in content:
                if i.is_file():listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                else:listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
        else: listbox.insert(0,"No content")
        current_path = previuos
    except Exception as e:
        messagebox.showerror("Error", str(e))

def refresh():
    try:
        if current_path:
            listbox.delete(0, tk.END)
            if list(current_path.iterdir()):
                for i in current_path.iterdir():
                    if i.is_file():listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                    else:listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
            else: listbox.insert(0,"No content")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete():
    try:
        if listbox.curselection():
            path = current_path.joinpath(listbox.selection_get().strip("\U0001F4C4\U0001F4C1 "))
            if messagebox.askyesno(title="Delete?",icon="warning",message=f"File {path} and all its contents are going to be deleted.You sure?"):
                if messagebox.askyesno(title="Delete?",icon="warning",message=f"DOUBLE SURE?"):
                    if path.is_file(): path.unlink(missing_ok=True)
                    else: shutil.rmtree(path)
                    refresh()
    except Exception as e: messagebox.showerror("Error", str(e))


def copy_selected():pass

def paste():pass

def rename():pass

def new_create():
    if not current_path:return
    try:
        create = create_new.get()
        match create:
            case "New txt file": form = ".txt"
            case "New rar archive": form = ".rar"
            case _: form = ""
        n = 0
        for i in list(current_path.iterdir()):
            if i.name == f"{create}{form}" or i.name == f"{create} ({n}){form}": n+=1
        path_name = f"{create} ({n}){form}" if n>0 else f"{create}{form}"
        if form: 
            with open(current_path.joinpath(path_name),"w") as f: pass
        else: current_path.joinpath(path_name).mkdir()
        refresh()
    except Exception as e: messagebox.showerror("Error", str(e))

def sort_path(path = None):
    if not current_path:return
    new_path = current_path if not path else path
    match sorting_type.get():
        case "Name": order = lambda x: pathlib.Path(x).name
        case "Size": order = lambda x: pathlib.Path(x).stat().st_size
        case "Date": order = lambda x: pathlib.Path(x).stat().st_mtime
    reversed = False if asc_desc.get() == "Up" else True

    sorted_dir = [pathlib.Path(i) for i in sorted(list(new_path.iterdir()),key= order,reverse=reversed)]
    return sorted_dir

def sort():
    sorted_dir = sort_path()
    try:
        listbox.delete(0, tk.END)
        if sorted_dir:
            for i in sorted_dir:
                if i.is_file():listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                else:listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
        else: listbox.insert(0,"No content")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def pop_up(event):
    if listbox.curselection() and listbox.get(listbox.curselection()[0]) != "No content": 
            pop_menu.entryconfigure("Delete",state = "normal")
            pop_menu.entryconfigure("Copy(PH)",state = "normal")
            pop_menu.entryconfigure("Rename(PH)",state = "normal")
    else: 
        pop_menu.entryconfigure("Delete",state = "disabled")
        pop_menu.entryconfigure("Copy(PH)",state = "disabled")
        pop_menu.entryconfigure("Rename(PH)",state = "disabled")
    pop_menu.tk_popup(root.winfo_pointerx(),root.winfo_pointery()) 

root = tk.Tk()
root.title("Simple File Explorer")
root.geometry("700x500")
root.bind("<Button-3>", pop_up)

pop_menu = tk.Menu(root, tearoff=0,relief="solid")
plus_menu = tk.Menu(pop_menu, tearoff=0,relief="solid")
sort_menu = tk.Menu(pop_menu, tearoff=0,relief="solid")

sorting_type = tk.StringVar(value="Name")
asc_desc = tk.StringVar(value="Up")
create_new = tk.StringVar()

pop_menu.add_command(label="Refresh",command=refresh)

pop_menu.add_cascade(label="Sort",menu= sort_menu )
sort_menu.add_radiobutton(
    label="Name",
    variable=sorting_type,
    value="Name",
    command= sort
)
sort_menu.add_radiobutton(
    label="Size",
    variable=sorting_type,
    value="Size",
    command= sort
)
sort_menu.add_radiobutton(
    label="Date modified",
    variable=sorting_type,
    value="Date",
    command= sort
)

sort_menu.add_separator()

sort_menu.add_radiobutton(
    label="Ascending",
    variable=asc_desc,
    value="Up",
    command= sort
)
sort_menu.add_radiobutton(
    label="Descending",
    variable=asc_desc,
    value="Down",
    command= sort
)

pop_menu.add_cascade(label="New+",menu=plus_menu)
plus_menu.add_command(label="New folder",command=lambda: (create_new.set("New folder"),new_create()))
plus_menu.add_command(label="New txt file",command=lambda: (create_new.set("New txt file"),new_create()))
plus_menu.add_command(label="New rar archive",command=lambda: (create_new.set("New txt file"),new_create()))

pop_menu.add_command(label="Copy(PH)")
pop_menu.add_command(label="Paste(PH)")
pop_menu.add_command(label="Rename(PH)")
pop_menu.add_command(label="Delete",command=delete)

top_frame = tk.Frame(root) #не знаю как еще создать растояние
top_frame.pack(fill="x", padx=5, pady=5)

select = tk.Menu(root)
select.add_command(
    label="Select Folder",
    command=select_folder 
    )
root.config(menu = select)

list_frame = tk.Frame(root)
list_frame.pack(fill="both", expand=True)

y_scroll = tk.Scrollbar(list_frame, orient="vertical")
x_scroll = tk.Scrollbar(list_frame, orient="horizontal")

listbox = tk.Listbox(
    list_frame,
    activestyle= "dotbox",
    yscrollcommand=y_scroll.set,
    xscrollcommand=x_scroll.set,
    bg= "lightgray",
    bd= 1,
    relief="groove"
)

y_scroll.config(command=listbox.yview)
x_scroll.config(command=listbox.xview)

y_scroll.pack(side="right", fill="y")
x_scroll.pack(side="bottom", fill="x")
listbox.pack(side="left", fill="both", expand=True)

listbox.bind("<<ListboxSelect>>", show_details)
listbox.bind("<Double-Button-1>", open_clicked)

details_var = tk.StringVar(value="Select a file")

details_label = tk.Label(
    root,
    textvariable=details_var,
    anchor="w",
    relief="sunken"
)
details_label.pack(fill="x")

tk.Button(
    root,
    text="Go back",
    command=go_back
).pack(pady=5)


root.mainloop()