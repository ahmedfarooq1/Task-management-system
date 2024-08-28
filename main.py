from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import sqlite3

# Creating the universal font variables
headlabelfont = ("Noto Sans CJK TC", 15, 'bold')
labelfont = ('Garamond', 14)
entryfont = ('Garamond', 12)

# Connecting to the Database where all information will be stored
connector = sqlite3.connect('ProjectManagement.db')
cursor = connector.cursor()

connector.execute("CREATE TABLE IF NOT EXISTS DEPARTMENT (DEPARTMENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, DEPARTMENT TEXT)")
connector.execute("CREATE TABLE IF NOT EXISTS PROJECT (PROJECT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,PROJECTNAME TEXT)")
connector.execute("CREATE TABLE IF NOT EXISTS STUDENT (STUDENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, STUDENTROLLNO TEXT UNIQUE, STUDENTNAME TEXT, DEPARTMENT_ID TEXT, PROJECT_ID INTEGER, FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENT(DEPARTMENT_ID), FOREIGN KEY (PROJECT_ID) REFERENCES PROJECT(PROJECT_ID))")

def reset_fields():
    global name_strvar, email_strvar, rollno_strvar, department_strvar, projectname_strvar
    name_strvar.set('')
    rollno_strvar.set('')
    department_strvar.set('')
    projectname_strvar.set('')

def reset_form():
    global tree
    tree.delete(*tree.get_children())
    reset_fields()

# def display_records():
#     tree.delete(*tree.get_children())
#     curr = connector.execute("SELECT * FROM STUDENT")
#     data = curr.fetchall()
#     for records in data:
#         tree.insert('', END, values=records)

def add_record():
    global name_strvar, email_strvar, rollno_strvar, department_strvar, projectname_strvar
    name = name_strvar.get()
    rollno = rollno_strvar.get()
    department = department_strvar.get()
    projectname = projectname_strvar.get()
    if not name or not rollno or not department or not projectname:
        mb.showerror('Error!', "Please fill all the missing fields!!")
    else:
        try:
            # Inserting data into the DEPARTMENT table
            connector.execute("INSERT OR IGNORE INTO DEPARTMENT (DEPARTMENT) VALUES (?)", (department,))
            department_id = cursor.lastrowid

            # Inserting data into the PROJECT table
            connector.execute("INSERT OR IGNORE INTO PROJECT (PROJECTNAME) VALUES (?)", (projectname,))
            project_id = cursor.lastrowid

            # Inserting data into the STUDENT table
            connector.execute(
            "INSERT INTO STUDENT ( STUDENTROLLNO,STUDENTNAME, DEPARTMENT_ID, PROJECT_ID) VALUES (?, ?, (SELECT DEPARTMENT_ID FROM DEPARTMENT WHERE DEPARTMENT = ?), (SELECT PROJECT_ID FROM PROJECT WHERE PROJECTNAME = ?))",
            ( rollno,name, department, projectname))

            connector.commit()
            mb.showinfo('Record added', f"Record of {name} was successfully added")
            reset_fields()
            display_records()
        except Exception as e:
            mb.showerror('Error!', f'An error occurred while adding the record: {str(e)}')


def update_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]

        student_id = selection[0]
        name = name_strvar.get()
        rollno = rollno_strvar.get()
        department = department_strvar.get()
        projectname = projectname_strvar.get()

        if not name or not rollno or not department or not projectname:
            mb.showerror('Error!', "Please fill all the missing fields!!")
        else:
            try:
                cursor = connector.cursor()

                # Update the STUDENT table
                connector.execute("UPDATE STUDENT SET STUDENTROLLNO = ?,STUDENTNAME = ?, DEPARTMENT_ID =(SELECT DEPARTMENT_ID FROM DEPARTMENT WHERE DEPARTMENT = ?), PROJECT_ID = (SELECT PROJECT_ID FROM PROJECT WHERE PROJECTNAME = ?) WHERE STUDENT_ID=?",
                (rollno,name, department,projectname,student_id))

                connector.commit()
                mb.showinfo('Record updated', f"Record of {name} was successfully updated")
                reset_fields()
                display_records()
            except Exception as e:
                mb.showerror('Error!', f'An error occurred while updating the record: {str(e)}')

def display_records():
    tree.delete(*tree.get_children())
    curr =cursor.execute("SELECT s.STUDENT_ID, s.STUDENTROLLNO,s.STUDENTNAME, d.DEPARTMENT, p.PROJECTNAME FROM STUDENT s JOIN DEPARTMENT d ON s.DEPARTMENT_ID = d.DEPARTMENT_ID JOIN PROJECT p ON s.PROJECT_ID = p.PROJECT_ID")
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)
    update_project_names()
    update_department_names()
    update_search_names()


def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from database')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values["values"]

        tree.delete(current_item)

        connector.execute('DELETE FROM STUDENT WHERE STUDENT_ID=%d' % selection[0])
        connector.commit()

        mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

        display_records()

def view_record():
    global name_strvar, email_strvar, rollno_strvar, department_strvar, projectname_strvar

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    rollno_strvar.set(selection[1])
    name_strvar.set(selection[2])
    department_strvar.set(selection[3])
    projectname_strvar.set(selection[4])

project_names = []

def update_project_names():
    # Get the available project names from the database
    cursor.execute("SELECT PROJECTNAME FROM PROJECT")
    results = cursor.fetchall()
    project_names.clear()
    for result in results:
        project_names.append(result[0])

    # Update the option menu with the new project names
    projectname_menu["menu"].delete(0, "end")
    for project_name in project_names:
        projectname_menu["menu"].add_command(label=project_name, command=lambda value=project_name: projectname_strvar.set(value))
project_names = []

def update_search_names():
    # Get the available project names from the database
    cursor.execute("SELECT PROJECTNAME FROM PROJECT")
    results = cursor.fetchall()
    project_names.clear()
    for result in results:
        project_names.append(result[0])

    # Update the option menu with the new project names
    projectname_menu["menu"].delete(0, "end")
    for project_name in project_names:
        projectname_menu["menu"].add_command(label=project_name, command=lambda value=project_name: search_project_strvar.set(value))

department_names = []

def update_department_names():
    # Get the available department names from the database
    cursor.execute("SELECT DEPARTMENT FROM DEPARTMENT")
    results = cursor.fetchall()
    department_names.clear()
    for result in results:
        department_names.append(result[0])

    # Update the option menu with the new department names
    # Add the following line of code below the definition of projectname_menu
    department_menu["menu"].delete(0, "end")
    for department_name in department_names:
        department_menu["menu"].add_command(label=department_name, command=lambda value=department_name: department_strvar.set(value))

def search_records():
    tree.delete(*tree.get_children())
    search_project = search_project_strvar.get()

    curr = cursor.execute("SELECT  s.STUDENT_ID,  s.STUDENTROLLNO,s.STUDENTNAME, d.DEPARTMENT, p.PROJECTNAME FROM STUDENT s JOIN DEPARTMENT d ON s.DEPARTMENT_ID = d.DEPARTMENT_ID JOIN PROJECT p ON s.PROJECT_ID = p.PROJECT_ID WHERE p.PROJECTNAME = ?", (search_project,))
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)





# ...


main = Tk()
main.title('Task Management System')
#width = main.winfo_screenwidth()
#height = main.winfo_screenheight()
main.geometry('1000x600')
#main.geometry("%d%d"%(width,height))
main.resizable(0, 0)

lf_bg = 'white' # bg color for the left_frame
cf_bg = 'black' # bg color for the center_frame


left_frame = Frame(main, bg=lf_bg)
left_frame.place(x=0, y=30, relheight=1, relwidth=0.2)

center_frame = Frame(main, bg=cf_bg)
center_frame.place(relx=0.2, y=30, relheight=1, relwidth=0.2)

right_frame = Frame(main, bg="Gray35")
right_frame.place(relx=0.4, y=30, relheight=1, relwidth=0.6)


# Creating the StringVar or IntVar variables
rollno_strvar = StringVar()
name_strvar = StringVar()
# projectname_strvar should be defined before creating the OptionMenu
projectname_strvar = StringVar()
projectname_menu = OptionMenu(left_frame, projectname_strvar, project_names)
projectname_menu.place(x=150, rely=0.75)
projectname_menu = OptionMenu(center_frame, projectname_strvar, search_records)
projectname_menu.place(x=150, rely=0.075)
department_strvar = StringVar()
department_menu = OptionMenu(left_frame, department_strvar, department_names)
department_menu.place(x=150, rely=0.39)
search_project_strvar = StringVar()

# Placing components in the left frame
Label(left_frame, text="ROLL NO", font=labelfont, bg=lf_bg).place(relx=0.150, rely=0.05)
Label(left_frame, text="NAME", font=labelfont, bg=lf_bg).place(relx=0.150, rely=0.18)
Label(left_frame, text="DEPARTMENT", font=labelfont, bg=lf_bg).place(relx=0.150, rely=0.31)
Label(left_frame, text="PROJECT NAME", font=labelfont, bg=lf_bg).place(relx=0.150, rely=0.7)

Entry(left_frame, width=19, textvariable=rollno_strvar, font=entryfont).place(x=20, rely=0.1)
Entry(left_frame, width=19, textvariable=name_strvar, font=entryfont).place(x=20, rely=0.23)
Entry(center_frame, width=19, textvariable=search_project_strvar, font=entryfont).place(relx=0.1, rely=0.05)
Entry(left_frame, width=19, textvariable=department_strvar, font=entryfont).place(x=20, rely=0.36)



Entry(left_frame, width=17, textvariable=projectname_strvar, font=entryfont).place(x=20, rely=0.75)
Button(left_frame, text='Submit and Add Record', font=labelfont, command=add_record, width=18).place(relx=0.025, rely=0.85)

# Placing components in the center frame
Button(center_frame, text='Delete Record', font=labelfont, command=remove_record, width=15).place(relx=0.1, rely=0.25)
Button(center_frame, text='View Record', font=labelfont, command=view_record, width=15).place(relx=0.1, rely=0.35)
Button(center_frame, text='Reset Fields', font=labelfont, command=reset_fields, width=15).place(relx=0.1, rely=0.45)
# Button(center_frame, text='Delete database', font=labelfont, command=reset_form, width=15).place(relx=0.1, rely=0.55)
Button(center_frame, text='Update Record', font=labelfont, command=update_record, width=15).place(relx=0.1, rely=0.65)
Button(center_frame, text='Search', font=labelfont, command=search_records, width=15).place(relx=0.1, rely=0.15)


Label(right_frame, text='Students Records', font=headlabelfont, bg='black', fg='white').pack(side=TOP, fill=X)

tree = ttk.Treeview(right_frame, height=100, selectmode=BROWSE, columns=('Student ID', "Rollno", "Name", "Department", "Project name"))

X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)

X_scroller.pack(side=BOTTOM, fill=X)
Y_scroller.pack(side=RIGHT, fill=Y)

tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)

tree.heading('Student ID', text='ID', anchor=CENTER)
tree.heading('Rollno', text='Rollno', anchor=CENTER)
tree.heading('Name', text='Name', anchor=CENTER)
tree.heading('Department', text='Department', anchor=CENTER)
tree.heading('Project name', text='Project name', anchor=CENTER)

tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=40, stretch=NO)
tree.column('#2', width=140, stretch=NO)
tree.column('#3', width=140, stretch=NO)
tree.column('#4', width=140, stretch=NO)
tree.column('#5', width=140, stretch=NO)

tree.pack(fill=BOTH, expand=1)


update_project_names()
search_records()
display_records()
main.mainloop()
