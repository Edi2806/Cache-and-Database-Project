import sqlite3
import tkinter as tk
from tkinter import END, messagebox, ttk



#DataBase Setup
def setup_database():
    conn = sqlite3.connect('Pura_Dance.db')
    cursor = conn.cursor()

#Create Tables
    cursor.execute ("""CREATE TABLE IF NOT EXISTS DanceClasses (ClassID INTEGER PRIMARY KEY AUTOINCREMENT, ClassName TEXT NOT NULL, Description TEXT)""")
    cursor.execute ("""CREATE TABLE IF NOT EXISTS ClassSchedule (ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT, ClassID INTEGER NOT NULL, WeekDay TEXT CHECK(WeekDay IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL, Time TEXT NOT NULL, FOREIGN KEY (ClassID) REFERENCES DanceClasses (ClassID))""")
    cursor.execute ("""CREATE TABLE IF NOT EXISTS Students (ID INTEGER PRIMARY KEY AUTOINCREMENT, StudentNumber TEXT NOT NULL UNIQUE, FullName TEXT NOT NULL UNIQUE, Email TEXT  NOT NULL UNIQUE CHECK(Email LIKE '%@%.%'), TelephoneNumber TEXT UNIQUE NOT NULL CHECK(length(TelephoneNumber ) = 11) )""")
    cursor.execute ("""CREATE TABLE IF NOT EXISTS Registrations (RegistrationID INTEGER PRIMARY KEY AUTOINCREMENT, ID INTEGER NOT NULL, ClassID INTEGER NOT NULL, FOREIGN KEY (ID) REFERENCES Students (ID), FOREIGN KEY (ClassID) REFERENCES DanceClasses (ClassID))""")
    conn.commit()
    conn.close() 
#DataBase Connection
def connect_db():
    return sqlite3.connect("Pura_Dance.db")

#Function to display class description
def show_class_description():
    selected_class = class_combobox.get()
    if not selected_class:
        messagebox.showerror("ERROR", "Please Select a Dance Class..!!")
        return
    conn = connect_db()
    cursor = conn.cursor()

#Fetch the description for the selected class
    cursor.execute("SELECT Description FROM DanceClasses WHERE ClassName = ?", (selected_class,))
    class_description = cursor.fetchone()
    if class_description:
        messagebox.showinfo(f"{selected_class} Description", class_description[0])
    else:
        messagebox.showerror("Error", "Class not found")
    conn.close()

#Generate Student ID
def student_id():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT StudentNumber FROM Students ORDER BY ID DESC LIMIT 1")
    last_student = cursor.fetchone()
    if last_student is None:
        next_id = 1
    else:
         next_id = int(last_student[0][2:]) + 1
    conn.close()
    student_id = f"PD{next_id:04d}"
    return student_id
 

#Save New Student
def save_student():
    student_id_value = student_id()
    full_name = entry_fullname.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()
    selected_class = class_combobox.get()
    
    if not full_name or not email or not phone or not selected_class:
        messagebox.showerror("Error" , "All Fields are Requiered..!!")
        return
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute ("INSERT INTO Students (StudentNumber, FullName, Email, TelephoneNumber) VALUES (?, ?, ?, ?)", (student_id_value, full_name, email, phone))
        conn.commit()
        cursor.execute ("INSERT INTO DanceClasses (ClassName) VALUES (?)", (selected_class,))
        conn.commit()
        cursor.execute ("SELECT ClassID FROM DanceClasses WHERE ClassName = ?", (selected_class,))
        class_id = cursor.fetchone()[0]
        print(class_id)
        cursor.execute("INSERT INTO Registrations (ID, ClassID) VALUES ((SELECT ID FROM Students WHERE FullName = ?), ?)", (full_name, class_id))
        conn.commit()
        messagebox.showinfo ("SUCCESS", f"New Member Created Successfully..!!!, Your ID Number is: {student_id_value}")
        clear_fields()
    except sqlite3.IntegrityError as e:
        messagebox.showerror ("ERROR", f"Database error: {e}")
    finally:    
        conn.close()

#Clear all the input fields
def clear_fields():
    entry_fullname.delete(0, END)
    entry_email.delete(0, END)
    entry_phone.delete(0, END)
    entry_student_number.delete(0, END)

    class_combobox.set("")

#Search Student
def search_student():
    search_query = entry_fullname.get().strip()
    if not search_query:
        messagebox.showerror("ERROR", "Please Enter a Name to Search")
        return
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE FullName = ?", (search_query,))
    result = cursor.fetchone()
    

    cursor.execute("SELECT * FROM Registrations WHERE ID = ?", (result[0],))
    class_id = cursor.fetchone()[2]              
    cursor.execute("SELECT * FROM DanceClasses WHERE ClassID = ?", (class_id,))
    class_name = cursor.fetchone()[1]

    if result:
        entry_student_number.delete(0, END)
        entry_student_number.insert(0, result[1])
        entry_fullname.delete(0, END)
        entry_fullname.insert(0, result[2])
        entry_email.delete(0, END)
        entry_email.insert(0, result[3])
        entry_phone.delete(0, END)
        entry_phone.insert(0, result[4])

        print({result})
        class_combobox.delete(0, END)
        class_combobox.insert(0, class_name)
        messagebox.showinfo("Search Result", f"Member found: {result[1]} (ID: {result[0]})")
    else:
        messagebox.showerror("ERROR", "NO Member Found with that Name")
    conn.close()

#Delete Student
def delete_student():
    search_query = entry_fullname.get().strip()
    if not search_query:
        messagebox.showerror("ERROR", "Please Enter a Name to Delete")
        return
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE FullName = ?", (search_query,))
    conn.commit()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name= ?", (search_query,))
    conn.commit()
    messagebox.showinfo("SUCCESS", f"Member {search_query} deleted successfully..!!!")
    clear_fields()
    conn.close()

#Update Student
def update_student():
    full_name = entry_fullname.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()
    student_number = entry_student_number.get().strip()
    
    if not full_name or not email or not phone:
        messagebox.showerror("Error" , "All Fields are Requiered..!!")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute ("UPDATE Students SET FullName = ?, Email = ?, TelephoneNumber = ? WHERE StudentNumber = ?", (full_name, email, phone, student_number))
    conn.commit()
    messagebox.showinfo ("SUCCESS", f"Member Updated Successfully..!!!")
    clear_fields()
    conn.close()   


#Graphical User Interface (GUI) Setup
root = tk.Tk()
root.title ("Pura Dance Nights")
root.geometry ("600x400")

# Load background image
#background_image = tk.PhotoImage(file="puranights.png")
#background_label = tk.Label(root, image=background_image)
#background_label.place(relwidth=1, relheight=1)

#Input Fields and Input
tk.Label(root, text="Student Number:").grid(row=0, column=2, padx=10, pady=5)
entry_student_number = tk.Entry(root, width=10)
entry_student_number.grid(row=0, column=3, padx=1, pady=5)

tk.Label(root, text="Full Name:", bg="#fff").grid(row=0, column=0, padx=10, pady=5)
entry_fullname = tk.Entry(root)
entry_fullname.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Email:", bg="#fff").grid(row=1, column=0, padx=10, pady=5)
entry_email = tk.Entry(root)
entry_email.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Phone Number:", bg="#fff").grid(row=2, column=0, padx=10, pady=5)
entry_phone = tk.Entry(root)
entry_phone.grid(row=2, column=1, padx=10, pady=5)


tk.Label(root, text="Dance Class:", bg="#fff").grid(row=3, column=0, padx=10, pady=5)
class_combobox = ttk.Combobox(root, values=["Bachata", "Salsa", "Lady Styling", "Couple Team"])
class_combobox.grid(row=3, column=1, padx=10, pady=5)

style = ttk.Style()
style.theme_use("clam")
style.configure("Save.TButton", background="green", foreground="black", font=("Arial", 12, "bold"))
style.configure("Search.TButton", background="blue", foreground="black", font=("Arial", 12, "bold"))
style.configure("Delete.TButton", background="red", foreground="black", font=("Arial", 12, "bold"))
style.configure("Update.TButton", background="orange", foreground="black", font=("Arial", 12, "bold"))
style.configure("Clear.TButton", background="gray", foreground="black", font=("Arial", 12, "bold"))
#Buttons
ttk.Button(root, text="Save", command=save_student).grid(row=4, column=0, padx=10, pady=10)
ttk.Button(root, text="Search", command=search_student).grid(row=4, column=1, padx=10, pady=10)
ttk.Button(root, text="Delete", command=delete_student).grid(row=5, column=0, padx=10, pady=10)
ttk.Button(root, text="Update", command=update_student).grid(row=5, column=1, padx=10, pady=10)
ttk.Button(root, text="Clear", command=clear_fields).grid(row=6, column=0, columnspan=2, pady=10)

#Run GUI
setup_database()
root.mainloop()
