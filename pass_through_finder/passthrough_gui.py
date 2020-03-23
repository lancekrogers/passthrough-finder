from tkinter import *
from tkinter import ttk
from pass_through_finder.process_views import analyze
from pass_through_finder.excel_output import *
from pass_through_finder.master_excel import create_master_excel_file
from pass_through_finder.helper_functions import *
import os


debub = True

def run_find_passthroughs(*args):
    try:
        os.chdir('pass_through_finder')
        analyze(path_string.get())
        update_excel_files()
        create_master_excel_file()
        send_excel_to_desktop()
        delete_csv()
        delete_excel()
    except ValueError as e:
        message_box('Value Error', 'An error has occured please try again.', 1)
        print('Error: {}'.format(e))
        if debug == True:
            print("You are seeing this message because you have "
                  "debug = True in the passthrough_guy.py file")
            value = input("Press enter to close the program")
    root.destroy()

root = Tk()
root.tile("Pass-through Finder")


mainframe = ttk.Frame(root, width=600, height=200, padding="11 11 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

path_string = StringVar()

path_entry = ttk.Entry(mainframe, width=60, textvariable=path_string)
path_entry.grid(column=2, row=1, sticky=(W, E))

ttk.button(mainframe, text="Find Pass-throughs",
           command=run_find_passthroughs).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="Enter Path").grid(column=3, row=1, sticky=E)
ttk.Label(mainframe, text="Copy and paste the path to each view DDL file that"
          " you would like to analyze").grid(column=2, row=2, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

path_entry.focus()

root.bind('<Return>', run_find_passthroughs)

root.mainloop()
