import datetime
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox,simpledialog
import pathlib,os


class Explorer(tk.Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.current_path: pathlib.Path | None = None
        self.copy_buffer: tuple[pathlib.Path,str] | None = None
        self.__archive_extensions: set[str] = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".nsp", ".xci", ".nsz"}
        self.__strip_str: str = "\U0001F4C4\U0001F4C1\U0001F5C3 "

        self.title("Simple File Explorer")
        self.geometry("700x500")
        self.bind("<Button-3>", self.pop_up)

        self.__pop_menu = tk.Menu(self, tearoff=0,relief="solid")
        self.__create_menu = tk.Menu(self.__pop_menu, tearoff=0,relief="solid")
        self.__sort_menu = tk.Menu(self.__pop_menu, tearoff=0,relief="solid")

        self.__sorting_type = tk.StringVar(value="Name")
        self.__asc_desc = tk.StringVar(value="Up")
        self.__create_new = tk.StringVar()

        self.__pop_menu.add_command(label="\u21BBRefresh",command= self.refresh_n_sort())

        self.__pop_menu.add_cascade(label="\u21C5 Sort",menu= self.__sort_menu)
        self.__sort_menu.add_radiobutton(
            label="\U0001F170Name",
            variable=self.__sorting_type,
            value="Name",
            command= self.refresh_n_sort
        )
        self.__sort_menu.add_radiobutton(
            label="\U0001F4BESize",
            variable=self.__sorting_type,
            value="Size",
            command= self.refresh_n_sort
        )
        self.__sort_menu.add_radiobutton(
            label="\U0001F554Date modified",
            variable=self.__sorting_type,
            value="Date",
            command= self.refresh_n_sort
        )

        self.__sort_menu.add_separator()

        self.__sort_menu.add_radiobutton(
            label="\U0001F53CAscending",
            variable=self.__asc_desc,
            value="Up",
            command= self.refresh_n_sort
        )
        self.__sort_menu.add_radiobutton(
            label="\U0001F53DDescending",
            variable=self.__asc_desc,
            value="Down",
            command= self.refresh_n_sort
        )

        self.__pop_menu.add_cascade(label="\uFF0BNew",menu=self.__create_menu)
        self.__create_menu.add_command(label="\U0001F4C1New folder",command=lambda: (self.__create_new.set("New folder"),self.new_create()))
        self.__create_menu.add_command(label="\U0001F4C4New txt file",command=lambda: (self.__create_new.set("New txt file"),self.new_create()))
        self.__create_menu.add_command(label="\U0001F5C3New rar archive",command=lambda: (self.__create_new.set("New rar archive"),self.new_create()))

        self.__pop_menu.add_separator()

        self.__pop_menu.add_command(label="\U00002702Cut",command= lambda: self.copy_cut("cut"))
        self.__pop_menu.add_command(label="\U0001F4CBCopy",command= lambda: self.copy_cut("copy"))
        self.__pop_menu.add_command(label="\U0001F4CCPaste",command= self.paste)
        self.__pop_menu.add_command(label="\U0001F4DDRename",command= self.rename)
        self.__pop_menu.add_command(label="\U0001F5D1Delete",command= self.delete)

        self.__top_frame = tk.Frame(self) 
        self.__top_frame.pack(fill="x")
        self.__top_frame.columnconfigure(0, weight=1)
        self.__top_frame.columnconfigure(1, weight=1)
        self.__top_frame.columnconfigure(2, weight=1)
        self.__search_bar = tk.Entry(self.__top_frame)
        self.__search_bar.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        tk.Button(self.__top_frame, text= "\U0001F50D",command= self.search).grid(row=0, column=2, sticky="ew")

        self.__select_menu = tk.Menu(self)
        self.__select_menu.add_command(
            label="Select Folder",
            command= self.select_folder 
            )
        self.__select_menu.add_command(
            label="Refresh",
            command= lambda: self.refresh_n_sort(self.current_path)
            )
        self.config(menu = self.__select_menu)

        self.__list_frame = tk.Frame(self)
        self.__list_frame.pack(fill="both", expand=True)

        y_scroll = tk.Scrollbar(self.__list_frame, orient="vertical")
        x_scroll = tk.Scrollbar(self.__list_frame, orient="horizontal")

        self.__listbox = tk.Listbox(
            self.__list_frame,
            activestyle= "dotbox",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            bg= "lightgray",
            bd= 1,
            relief="groove"
        )

        y_scroll.config(command=self.__listbox.yview)
        x_scroll.config(command=self.__listbox.xview)

        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.__listbox.pack(side="left", fill="both", expand=True)

        self.__listbox.bind("<<ListboxSelect>>", self.show_details)
        self.__listbox.bind("<Double-Button-1>", self.open_clicked)

        self.__details_var = tk.StringVar(value="Select a file")

        details_label = tk.Label(
            self,
            textvariable=self.__details_var,
            anchor="w",
            relief="sunken"
        )
        details_label.pack(fill="x")

        tk.Button(
            self,
            text="Go back",
            command=self.go_back
        ).pack(pady=5)
                

    def select_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder == "":return None
        self.current_path = pathlib.Path(folder)  
        self.refresh_n_sort()

    def search(self):
        if not self.current_path: return
        request = self.__search_bar.get()
        if not request: return
        result = list(self.current_path.glob(f"*{request}*"))
        self.__listbox.delete(0, tk.END)
        if result:
            for path in result:
                if path.is_file():
                    if path.suffix in self.__archive_extensions: self.__listbox.insert(tk.END, f"\U0001F5C3 {path.name}")
                    else: self.__listbox.insert(tk.END, f"\U0001F4C4 {path.name}")
                else: self.__listbox.insert(tk.END, f"\U0001F4C1 {path.name}")
        else: self.__listbox.insert(0,"No content")

    def open_clicked(self,event:tk.Event) -> None:
        selected = self.__listbox.get(self.__listbox.curselection()[0]).strip(self.__strip_str)
        if not selected or selected == "No content": return None

        path = self.current_path.joinpath(selected)
        try:
            if path.is_file():
                os.startfile(str(path))
                return None
            
            self.__listbox.delete(0, tk.END)
            self.refresh_n_sort(path)
            self.current_path = path
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def show_details(self, event=None) -> None:
        selection = self.__listbox.curselection()
        if not selection: return None

        filename = self.__listbox.get(selection[0])
        if filename == "No content":  
            self.__details_var.set("Null")
            return None

        selected_path = str(self.current_path.joinpath(filename.strip(self.__strip_str)))

        try:
            size = os.path.getsize(selected_path)

            if os.path.isfile(selected_path):
                if pathlib.Path(selected_path).suffix in self.__archive_extensions: file_type = "Archive"
                else: file_type = "File"
            else:
                file_type = "Folder"

            date_m = f"{datetime.datetime.fromtimestamp(os.path.getmtime(selected_path))}"

            self.__details_var.set(
                f"Name: {filename} | "
                f"Type: {file_type} | "
                f"Size: {size} bytes | "
                f"Date modified: {date_m}"
            )

        except Exception as e:
            self.__details_var.set(str(e))

    def go_back(self) -> None:
        if not self.current_path: return None 

        previuos = self.current_path.parent
        self.refresh_n_sort(previuos)
        self.current_path = previuos

    def refresh_n_sort(self,path = None) -> None:
        if self.current_path:
            new_path = path if path else self.current_path
        else: return None

        match self.__sorting_type.get():
            case "Name": order = lambda x: pathlib.Path(x).name
            case "Size": order = lambda x: pathlib.Path(x).stat().st_size
            case "Date": order = lambda x: pathlib.Path(x).stat().st_mtime
        reversed = False if self.__asc_desc.get() == "Up" else True

        sorted_dir = [pathlib.Path(i) for i in sorted(list(new_path.iterdir()),key= order,reverse=reversed)]

        try:
            self.__listbox.delete(0, tk.END)
            if sorted_dir:
                for i in sorted_dir:
                    if i.is_file():
                        if i.suffix in self.__archive_extensions: self.__listbox.insert(tk.END, f"\U0001F5C3 {i.name}")
                        else: self.__listbox.insert(tk.END, f"\U0001F4C4 {i.name}")
                    else: self.__listbox.insert(tk.END, f"\U0001F4C1 {i.name}")
            else: self.__listbox.insert(0,"No content")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self) -> None:
        try:
            if self.__listbox.curselection():
                path = self.current_path.joinpath(self.__listbox.selection_get().strip(self.__strip_str))
                if messagebox.askyesno(title="Delete?",icon="warning",message=f"File {path} and all its contents are going to be deleted.You sure?"):
                    if messagebox.askyesno(title="Delete?",icon="warning",message=f"DOUBLE SURE?"):
                        if path.is_file(): path.unlink(missing_ok=True)
                        else: shutil.rmtree(path)
                        self.refresh_n_sort()
        except Exception as e: messagebox.showerror("Error", str(e))


    def copy_cut(self,mode: str) -> None:
        selection = self.__listbox.curselection()
        if not self.current_path or not selection: return None

        try: copy_buffer = (self.current_path.joinpath(self.__listbox.get(selection).strip(self.__strip_str)),mode)
        except Exception as e: messagebox.showerror("Error", str(e))

    def paste(self) -> None:
        name = copy_buffer[0].name
        suf = copy_buffer[0].suffix

        n = 0
        for i in list(self.current_path.iterdir()):
            if i.name == name or i.name == f"{name.strip(suf)} ({n}){suf}": n+=1
        try:
            if copy_buffer[1] == "cut": 
                if copy_buffer[0].parent == self.current_path: return
                if n == 0:shutil.move(copy_buffer[0],self.current_path.joinpath(name))
                else: shutil.move(copy_buffer[0],self.current_path.joinpath(f"{name} ({n}){suf}"))
                copy_buffer = ""
            else: 
                if copy_buffer[0].is_file():
                    if n == 0:shutil.copy(copy_buffer[0],self.current_path.joinpath(name))
                    else: shutil.copy(copy_buffer[0],self.current_path.joinpath(f"{name} ({n})"))
                else: 
                    if n == 0:shutil.copytree(copy_buffer[0],self.current_path.joinpath(name))
                    else: shutil.copytree(copy_buffer[0],self.current_path.joinpath(f"{name} ({n}){suf}"))
        except Exception as e: messagebox.showerror("Error", str(e))
        self.refresh_n_sort()

    def rename(self) -> None:      #топорно потом придумаю
        selection = self.__listbox.curselection()
        if not self.current_path or not selection: return None

        name = pathlib.Path(self.__listbox.get(selection).strip(self.__strip_str))
        new_name = simpledialog.askstring(title="Rename",prompt="Enter new name",initialvalue=name,parent=self)
        if new_name == name or not new_name: return None

        try: self.current_path.joinpath(name).rename(new_name)   
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: self.refresh_n_sort()

    def new_create(self) -> None:
        if not self.current_path: return None

        try:
            create = self.__create_new.get()
            match create:
                case "New txt file": form = ".txt"
                case "New rar archive": form = ".rar"
                case _: form = ""

            dup_count = 0
            for i in list(self.current_path.iterdir()):
                if i.name == f"{create}{form}" or i.name == f"{create} ({dup_count}){form}": dup_count+=1
            
            path_name = f"{create} ({dup_count}){form}" if dup_count>0 else f"{create}{form}"

            if form: 
                with open(self.current_path.joinpath(path_name),"w") as f: pass
            else: self.current_path.joinpath(path_name).mkdir()
            
            self.refresh_n_sort()
        except Exception as e: messagebox.showerror("Error", str(e))

    def pop_up(self,event :tk.Event) -> None:
        if self.__listbox.curselection() and self.__listbox.get(self.__listbox.curselection()[0]) != "No content": 
            self.__pop_menu.entryconfigure("\U0001F5D1Delete",state = "normal")
            self.__pop_menu.entryconfigure("\U00002702Cut",state = "normal")  
            self.__pop_menu.entryconfigure("\U0001F4CBCopy",state = "normal")
            self.__pop_menu.entryconfigure("\U0001F4DDRename",state = "normal")  
        else: 
            self.__pop_menu.entryconfigure("\U0001F5D1Delete",state = "disabled")
            self.__pop_menu.entryconfigure("\U00002702Cut",state = "disabled")  
            self.__pop_menu.entryconfigure("\U0001F4CBCopy",state = "disabled")
            self.__pop_menu.entryconfigure("\U0001F4DDRename",state = "disabled")
            
        if self.current_path: self.__pop_menu.entryconfigure("\u21C5 Sort",state = "normal")
        else: self.__pop_menu.entryconfigure("\u21C5 Sort",state = "disabled")

        if self.copy_buffer: self.__pop_menu.entryconfigure("\U0001F4CCPaste",state = "normal")
        else: self.__pop_menu.entryconfigure("\U0001F4CCPaste",state = "disabled")

        self.__pop_menu.tk_popup(self.winfo_pointerx(),self.winfo_pointery()) 

root = Explorer()
root.mainloop()