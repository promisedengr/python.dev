import snowflake.connector

ctx = snowflake.connector.connect(
    account = 'ir61293.west-us-2.azure',
    user = 'ivan',
    schema = 'PUBLIC',
    warehouse='COMPUTE_WH',
    password='ivanOkt2021',
)


cs = ctx.cursor()

cs.execute("select * from DEMO_DB.PUBLIC.TBL;")


import tkinter as tk

def show_comment_byID():
    cs.execute("select * from DEMO_DB.PUBLIC.TBL where (ID=" +id_input.get()+ ");")
    test = ""
    test = cs.fetchone()[9]
    
    comment_var.set(test)
    
def update_comment_byID():
    print("dd")
    query = "update DEMO_DB.PUBLIC.TBL set COMMENT = '" +comment_input.get()+ \
              "'where(ID=" +id_input.get() +");"
    cs.execute(query)


master = tk.Tk()
master.geometry("350x200")

tk.Label(master, text="ID").grid(row=1, pady=4)
tk.Label(master, text="COMMENT").grid(row=3)


comment_var = tk.StringVar()

id_input = tk.Entry(master, width=250)
id_input.place(height=40, width=250)
comment_input = tk.Entry(master, textvariable=comment_var, width=250)
comment_input.place(height=40, width=250)


id_input.grid(row=1, column=1)
comment_input.grid(row=3, column=1)


button1 = tk.Button(master, text='Show Comment', command=show_comment_byID).grid(row=2, 
                                                               column=1, 
                                                               sticky=tk.W, 
                                                               pady=4)


tk.Button(master, text='Update', command=update_comment_byID).grid(row=4, 
                                                               column=1, 
                                                               sticky=tk.W, 
                                                               pady=4)

master.mainloop()

# tk.mainloop()