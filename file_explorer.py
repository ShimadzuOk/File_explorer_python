import datetime
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox,simpledialog
import pathlib,os

current_path = ""
copy_buffer = None
archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".nsp", ".xci", ".nsz"}

def select_folder() -> None:
    global current_path
    folder = filedialog.askdirectory()
    if folder == "": return None
    current_path = pathlib.Path(folder)  
    refresh_n_sort()


def open_clicked(event:tk.Event) -> None:
    global current_path
    selected = listbox.get(listbox.curselection()[0]).strip("\U0001F4C4\U0001F4C1\U0001F5C3 ")
    if not selected or selected == "No content": return 
    path = current_path.joinpath(selected)

    try:
        if path.is_file():
            os.startfile(str(path))
            return None
        
        listbox.delete(0, tk.END)
        refresh_n_sort(path)
        current_path = path
    except Exception as e:
        messagebox.showerror("Error", str(e))


def show_details(event=None) -> None:
    global current_path
    selection = listbox.curselection()
    if not selection: return None

    filename = listbox.get(selection[0])
    if filename == "No content":  
        details_var.set("Null")
        return None
    
    selected_path = str(current_path.joinpath(filename.strip("\U0001F4C4\U0001F4C1\U0001F5C3 ")))

    try:
        size = os.path.getsize(selected_path)

        if os.path.isfile(selected_path):
            if pathlib.Path(selected_path).suffix in archive_extensions: file_type = "Archive"
            else: file_type = "File"
        else:
            file_type = "Folder"

        date_m = f"{datetime.datetime.fromtimestamp(os.path.getmtime(selected_path))}"

        details_var.set(
            f"Name: {filename} | "
            f"Type: {file_type} | "
            f"Size: {size} bytes | "
            f"Date modified: {date_m}"
        )

    except Exception as e:
        details_var.set(str(e))

def go_back() -> None:
    global current_path
    if not current_path: return None 

    previuos = current_path.parent
    refresh_n_sort(previuos)
    current_path = previuos

def refresh_n_sort(path = None) -> None:
    global current_path,archive_extensions
    if current_path:
        new_path = path if path else current_path
    else: return None

    match sorting_type.get():
        case "Name": order = lambda x: pathlib.Path(x).name
        case "Size": order = lambda x: pathlib.Path(x).stat().st_size
        case "Date": order = lambda x: pathlib.Path(x).stat().st_mtime
    reversed = False if asc_desc.get() == "Up" else True

    sorted_dir = [pathlib.Path(i) for i in sorted(list(new_path.iterdir()),key= order,reverse=reversed)]

    try:
        listbox.delete(0, tk.END)
        if sorted_dir:
            for i in sorted_dir:
                if i.is_file():
                    if i.suffix in archive_extensions: listbox.insert(tk.END, f"\U0001F5C3 {i.name}")
                    else: listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                else: listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
        else: listbox.insert(0,"No content")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete() -> None:
    global current_path
    try:
        if listbox.curselection():
            path = current_path.joinpath(listbox.selection_get().strip("\U0001F4C4\U0001F4C1\U0001F5C3 "))
            if messagebox.askyesno(title="Delete?",icon="warning",message=f"File {path} and all its contents are going to be deleted.You sure?"):
                if messagebox.askyesno(title="Delete?",icon="warning",message=f"DOUBLE SURE?"):
                    if path.is_file(): path.unlink(missing_ok=True)
                    else: shutil.rmtree(path)
                    refresh_n_sort()
    except Exception as e: messagebox.showerror("Error", str(e))


def copy_cut(mode: str) -> None:
    global current_path,copy_buffer
    selection = listbox.curselection()
    if not current_path or not selection: return None

    try: copy_buffer = (current_path.joinpath(listbox.get(selection).strip("\U0001F4C4\U0001F4C1\U0001F5C3 ")),mode)
    except Exception as e: messagebox.showerror("Error", str(e))

def paste() -> None:
    global current_path,copy_buffer
    name = copy_buffer[0].name
    suf = copy_buffer[0].suffix

    n = 0
    for i in list(current_path.iterdir()):
        if i.name == name or i.name == f"{name.strip(suf)} ({n}){suf}": n+=1
    try:
        if copy_buffer[1] == "cut": 
            if copy_buffer[0].parent == current_path: return
            if n == 0:shutil.move(copy_buffer[0],current_path.joinpath(name))
            else: shutil.move(copy_buffer[0],current_path.joinpath(f"{name} ({n}){suf}"))
            copy_buffer = ""
        else: 
            if copy_buffer[0].is_file():
                if n == 0:shutil.copy(copy_buffer[0],current_path.joinpath(name))
                else: shutil.copy(copy_buffer[0],current_path.joinpath(f"{name} ({n})"))
            else: 
                if n == 0:shutil.copytree(copy_buffer[0],current_path.joinpath(name))
                else: shutil.copytree(copy_buffer[0],current_path.joinpath(f"{name} ({n}){suf}"))
    except Exception as e: messagebox.showerror("Error", str(e))
    refresh_n_sort()

def rename() -> None:      
    global current_path         #топорно потом придумаю
    selection = listbox.curselection()
    if not current_path or not selection: return None

    name = pathlib.Path(listbox.get(selection).strip("\U0001F4C4\U0001F4C1\U0001F5C3 "))
    new_name = simpledialog.askstring(title="Rename",prompt="Enter new name",initialvalue=name,parent=root)
    if new_name == name or not new_name: return None

    try: current_path.joinpath(name).rename(new_name)   
    except Exception as e: messagebox.showerror("Error", str(e))
    finally: refresh_n_sort()

def new_create() -> None:
    global current_path
    if not current_path: return None

    try:
        create = create_new.get()
        match create:
            case "New txt file": form = ".txt"
            case "New rar archive": form = ".rar"
            case _: form = ""

        dup_count = 0
        for i in list(current_path.iterdir()):
            if i.name == f"{create}{form}" or i.name == f"{create} ({dup_count}){form}": dup_count+=1
        
        path_name = f"{create} ({dup_count}){form}" if dup_count>0 else f"{create}{form}"

        if form: 
            with open(current_path.joinpath(path_name),"w") as f: pass
        else: current_path.joinpath(path_name).mkdir()
        
        refresh_n_sort()
    except Exception as e: messagebox.showerror("Error", str(e))

def pop_up(event) -> None:
    global current_path,copy_buffer

    if listbox.curselection() and listbox.get(listbox.curselection()[0]) != "No content": 
        pop_menu.entryconfigure("\U0001F5D1Delete",state = "normal")
        pop_menu.entryconfigure("\U00002702Cut",state = "normal")  
        pop_menu.entryconfigure("\U0001F4CBCopy",state = "normal")
        pop_menu.entryconfigure("\U0001F4DDRename",state = "normal")  
    else: 
        pop_menu.entryconfigure("\U0001F5D1Delete",state = "disabled")
        pop_menu.entryconfigure("\U00002702Cut",state = "disabled")  
        pop_menu.entryconfigure("\U0001F4CBCopy",state = "disabled")
        pop_menu.entryconfigure("\U0001F4DDRename",state = "disabled")
        
    if current_path: pop_menu.entryconfigure("\u21C5 Sort",state = "normal")
    else: pop_menu.entryconfigure("\u21C5 Sort",state = "disabled")

    if copy_buffer: pop_menu.entryconfigure("\U0001F4CCPaste",state = "normal")
    else: pop_menu.entryconfigure("\U0001F4CCPaste",state = "disabled")

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

pop_menu.add_command(label="\u21BBRefresh",command=refresh_n_sort())

pop_menu.add_cascade(label="\u21C5 Sort",menu= sort_menu)
sort_menu.add_radiobutton(
    label="\U0001F170Name",
    variable=sorting_type,
    value="Name",
    command= refresh_n_sort
)
sort_menu.add_radiobutton(
    label="\U0001F4BESize",
    variable=sorting_type,
    value="Size",
    command= refresh_n_sort
)
sort_menu.add_radiobutton(
    label="\U0001F554Date modified",
    variable=sorting_type,
    value="Date",
    command= refresh_n_sort
)

sort_menu.add_separator()

sort_menu.add_radiobutton(
    label="\U0001F53CAscending",
    variable=asc_desc,
    value="Up",
    command= refresh_n_sort
)
sort_menu.add_radiobutton(
    label="\U0001F53DDescending",
    variable=asc_desc,
    value="Down",
    command= refresh_n_sort
)

pop_menu.add_cascade(label="\uFF0BNew",menu=plus_menu)
plus_menu.add_command(label="\U0001F4C1New folder",command=lambda: (create_new.set("New folder"),new_create()))
plus_menu.add_command(label="\U0001F4C4New txt file",command=lambda: (create_new.set("New txt file"),new_create()))
plus_menu.add_command(label="\U0001F5C3New rar archive",command=lambda: (create_new.set("New rar archive"),new_create()))

pop_menu.add_separator()

pop_menu.add_command(label="\U00002702Cut",command= lambda: copy_cut("cut"))
pop_menu.add_command(label="\U0001F4CBCopy",command= lambda: copy_cut("copy"))
pop_menu.add_command(label="\U0001F4CCPaste",command=paste)
pop_menu.add_command(label="\U0001F4DDRename",command=rename)
pop_menu.add_command(label="\U0001F5D1Delete",command=delete)

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