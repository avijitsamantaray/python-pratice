import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
import os
import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import shutil

# Replace with your credentials file path
serviceaccountfile = ''

# Scopes for accessing Drive API (adjust based on needs)
scopes = ['https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/docs',
          'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive.file']  # Enough for file creation
credentials = service_account.Credentials.from_service_account_file(serviceaccountfile,scopes=scopes)
service = build('drive','v3',credentials=credentials)
folder_id = ""



def upload(service,name,folder_id):
    metadata = {'name':f'{name}.json','parents':[folder_id]}
    media_body = MediaFileUpload(f'{name}.json',mimetype='application/json',resumable=True)
    try:
        file = service.files().create(body=metadata,media_body=media_body).execute()
        messagebox.showinfo("success","Data uploaded successfully")

    except Exception as e:
        print(f"An error occurred while uploading: {e}")

    else:
        return
def updatedata(service,name,folder_id):
    results = service.files().list(pageSize=100,q=f"mimeType='application/json' and trashed=false and '{folder_id}' in parents").execute()
    files = results.get('files',[])
    for file in files:
        if file['name']==f"{name}"+".json":
            id=file['id']
            media_body = MediaFileUpload(f'{name}.json',mimetype='application/json',resumable=True)
            service.files().update(fileId=id,body={"modifiedTime":None},media_body=media_body).execute()



def deletefile(service,folder_id,name):
    results = service.files().list(pageSize=100,q=f"mimeType='application/json' and name contains '{name}' and '{folder_id}' in parents").execute()
    files = results.get('files',[])
    for f in files:
        if f['name'] == f'{name}' + '.json':
            body_value = {'trashed':True}
            service.files().update(fileId=f['id'],body=body_value).execute()


def get_filenames(service,folder_id):
    l = []
    results = service.files().list(pageSize=100,q=f"mimeType='application/json' and trashed=false and '{folder_id}' in parents").execute()
    files = results.get('files',[])
    for f in files:
        l.append(f['name'])
    return l


def download_json_file(service,file_id):

    # Download the file using file ID
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh,request)

    downloader = MediaIoBaseDownload(fh,request,chunksize=204800)
    downloader.next_chunk()
    content = fh.getvalue().decode('utf-8')

    return content


def downloadfile(service,folder_id,name):
    query = f"mimeType='application/json' and name contains '{name}' and '{folder_id}' in parents"
    results = service.files().list(pageSize=100,q=query).execute()
    files = results.get('files',[])
    if files:
        file_id = files[0]['id']  # Assuming the first matching file is the desired one
        data = download_json_file(service,file_id)
    return data

def close_task():
    try:
        path = os.getcwd().split("\\")

        path.pop()
        data = "\\".join(path)
        os.chdir(data)
        shutil.rmtree("testing")
    except:pass
    else:pass

    sys.exit()

class main:
    def __init__(self):
        self.key = ""
        self.root = Tk()
        self.root.title("Password encryption")
        self.root.geometry("580x530")
        self.mainframe = Frame(self.root)
        self.mainframe.grid_rowconfigure(0,minsize=100)  # Empty row of height 100
        self.root.protocol("WM_DELETE_WINDOW", close_task)

        """# Create Style object"""
        S = ttk.Style()
        S.configure("Red.TLabel",background="red",font=("Arial",13))
        S.configure("blued.TLabel",background="blue",font=("Arial",13))

        """password lable  """
        ttk.Label(self.mainframe,text="Password",style="blued.TLabel",width=15,anchor="center",).grid(row=2,column=0,)
        """
        In this code snippet, anchor='center' ensures that the text “Password” is centered within the label. 
        If you’re using the pack geometry manager, the text will be centered by default. However,
         since you’re using grid, you need to specify the anchor attribute to align the text.
        """  # imp information

        self.mainframe.grid_rowconfigure(3,minsize=20)  # Space before password field

        """Password Field"""
        self.p_val = StringVar()
        self.p_show = "*"
        S.configure("enter.TEntry",font="arial 8")
        pasword_entry = ttk.Entry(self.mainframe,textvariable=self.p_val,style="enter.TEntry",show=self.p_show,
            width=35,).grid(row=4,column=0,sticky="w"

        )  # Align entry to the left

        self.root.bind('<Return>',self.bindfuntion)

        """Subframe for buttons"""
        self.subframe = Frame(self.mainframe,width=35)
        self.subframe.grid(row=5,column=0,sticky="ew",pady=5)  # Align subframe to the left

        """Enter button"""
        S.configure("enter.TButton",font="arial 8")
        enter_button = ttk.Button(self.subframe,text="Enter",style="enter.TButton",width=12,command=self.Validate_password,)
        enter_button.pack(side="left")  # Align button to the left with padding

        """Change Password button"""
        change_button = ttk.Button(self.subframe,text="Change Password",style="enter.TButton",width=18,command=self.change_password,)
        change_button.pack(side="right")  # Place next to the enter button

        self.mainframe.pack()
        self.root.mainloop()

    def bindfuntion(self,event=None):
        if self.mainframe.winfo_exists():
            self.Validate_password()


    def Validate_password(self,event=None):
        password = self.p_val.get()
        if password == "king":
            self.main_body()
        else:
            self.p_val.set("")
            messagebox.showwarning("Warning","Incorrect Password")

#Trial main hai
    def change_password(self):
        pass
        messagebox.showinfo("info","Testing")
        # """another sub frame for bottoms"""
        # self.subframe1 = Frame(self.mainframe,width=40)
        # self.subframe1.grid(row=6,column=0,sticky="ew",pady=5)
        # """OTP field"""
        # ttk.Entry(self.subframe1,textvariable=self.p_val,style="enter.TEntry",show=self.p_show,width=15,).pack(
        #     side="left")

        # """Verifybutton"""
        # verify_button = ttk.Button(self.subframe1,text="Verify",style="enter.TButton",width=8,
        #     command=self.Validate_password,)
        # verify_button.pack(side="left")  # Stack below the "Change Password" button

        # """" send button"""
        # send_button = ttk.Button(self.subframe1,text="Send",style="enter.TButton",width=8,command=self.change_password,)
        # send_button.pack(side="left")  # Stack below the "Verify" button

    # main frame
    def main_body(self):

        
        

        self.mainframe.destroy()
        self.bodyframe = Frame(self.root)
        self.bodyframe.grid_rowconfigure(0,minsize=20)

        """button for action"""

        # Configure the columns to distribute space evenly
        self.bodyframe.grid_columnconfigure(0,weight=2)
        self.bodyframe.grid_columnconfigure(1,weight=2)

        # Create buttons with equal
        S = ttk.Style()
        S.configure("size.TButton",font=("Arial",15))
        ttk.Button(self.bodyframe,text="Encryption",style="size.TButton",command=self.encryption).grid(row=1,column=0,sticky="n",)
        ttk.Button(self.bodyframe,text="Show",style="size.TButton",command=self.show).grid(row=1,column=1,sticky="n",padx=10)
        self.bodyframe.pack()
        self.root.mainloop()

    # encrytion part
    def encryption(self):
        filenames = get_filenames(service,folder_id)
        self.filenameslist= [os.path.splitext(i)[0] for i in filenames]
        try:
            self.bodyframe1.destroy()
        except:
            pass
        self.bodyframe1 = Frame(self.root,width=380)
        self.bodyframe1.grid_columnconfigure(0,minsize=100)
        self.bodyframe1.grid_rowconfigure(0,minsize=100)
        # get filename
        self.filename = StringVar()
        Label(self.bodyframe1,text="Filename ",font=" arial 10").grid(row=0,pady=(50,0),padx=(3,0),columnspan=4)
        self.filenametext = Entry(self.bodyframe1,textvariable=self.filename,font="arial 10",width=30).grid(row=1,pady=2,padx=(5,0),columnspan=4)

        #  get username
        self.username = StringVar()
        Label(self.bodyframe1,text="Enter  Username ",font=" arial 10").grid(row=2,pady=3,padx=(5,0),columnspan=4)
        self.usernametext = Entry(self.bodyframe1,textvariable=self.username,font="arial 10",width=30).grid(row=3,pady=3,padx=(5,0),columnspan=4)

        # get password
        self.password = StringVar()
        Label(self.bodyframe1,text="Enter  Password ",font=" arial 10").grid(row=4,pady=3,padx=(5,0),columnspan=4)
        self.passwordtext = Entry(self.bodyframe1,textvariable=self.password,font="arial 10",show="*",width=30).grid(row=5,pady=3,padx=(5,0),columnspan=4)

        # buttons
        self.show_pasword = Button(self.bodyframe1,text="show",font="arial 10",command=self.showpassword,bg="forest green",fg="white").grid(row=6,column=0,pady=1)
        self.submit = Button(self.bodyframe1,text="enter",font="arial 10",command=self.save,bg="royal blue",fg="white").grid(row=6,column=1,pady=1)
        self.clear = self.submit = Button(self.bodyframe1,text="clear",font="arial 10",command=self.clearfield,bg="#2ecc71",fg="white").grid(row=6,column=2,pady=1,padx=20)

        self.bodyframe1.pack(side='left',anchor=NW)

    def save(self):
        if self.filename.get() == "":
            messagebox.showwarning("ALERT",'FILE IS EMPTY')
            return
        elif self.filename.get() in self.filenameslist:
            messagebox.showwarning("alert","file exist")
            return

        # Generate a key for username
        key_username = Fernet.generate_key()
        fernet = Fernet(key_username)
        username = fernet.encrypt(self.username.get().encode())
        username = username.decode()
        key_username = key_username.decode()

        # generate a key for Password
        key_password = Fernet.generate_key()
        fernet = Fernet(key_password)
        password = fernet.encrypt(self.password.get().encode())
        password = password.decode()
        key_password = key_password.decode()

        #encode the keys
        fernet = Fernet(self.key)
        key_password = fernet.encrypt(key_password.encode())
        key_password = key_password.decode()
        key_username = (fernet.encrypt(key_username.encode()))
        key_username = key_username.decode()

        data = {

            f'username':{'key':f'{key_username}','value':f'{username}'},

            f'password':{'key':f'{key_password}','value':f'{password}'}}
        with open(f'{self.filename.get()}.json','w') as file:
            json.dump(data,file,indent=4)
        upload(service,self.filename.get(),folder_id)

    def showpassword(self):
        messagebox.showinfo("password",self.password.get())

    def clearfield(self):
        self.filename.set("")
        self.username.set("")
        self.password.set("")

    # decryption part
    def decryption(self,name):
        try:
            self.bodyframe1.destroy()
        except:
            pass

        self.bodyframe1 = Frame(self.root,width=380)
        self.bodyframe1.grid_columnconfigure(0,minsize=100)
        self.bodyframe1.grid_rowconfigure(0,minsize=100)
        # get filename
        self.filename = StringVar()
        Label(self.bodyframe1,text="Filename ",font=" arial 10").grid(row=0,pady=(50,0),padx=(3,0),columnspan=2)
        self.filenametext = Entry(self.bodyframe1,textvariable=self.filename,font="arial 10",width=30).grid(row=1,pady=2,padx=(5,0),columnspan=2)

        #  get username
        self.username = StringVar()
        Label(self.bodyframe1,text="Enter  Username ",font=" arial 10").grid(row=2,pady=3,padx=(5,0),columnspan=2)
        self.usernametext = Entry(self.bodyframe1,textvariable=self.username,font="arial 10",width=30).grid(row=3,pady=3,padx=(5,0),columnspan=2)

        # get password
        self.password = StringVar()
        Label(self.bodyframe1,text="Enter  Password ",font=" arial 10").grid(row=4,pady=3,padx=(5,0),columnspan=2)
        self.passwordtext = Entry(self.bodyframe1,textvariable=self.password,font="arial 10",width=30).grid(row=5,pady=3,padx=(5,0),columnspan=2)

        # check if exitst in folder

        load_data = json.loads(downloadfile(service,folder_id,name))

        # show the value in the field
        self.filename.set(name)

        username_key = load_data['username']['key']
        username_value = load_data['username']['value']
        password_key = load_data['password']['key']
        password_value = load_data['password']['value']

        # decrypt the key
        f = Fernet(self.key)
        new_u_key = (f.decrypt(username_key.encode())).decode()
        new_p_key = (f.decrypt(password_key.encode())).decode()

        # username
        f = Fernet(new_u_key)
        decrypted_text = f.decrypt(username_value.encode())
        self.username.set(decrypted_text)

        # password
        f = Fernet(new_p_key)
        decrypted_text = f.decrypt(password_value.encode())
        self.password.set(decrypted_text)

        self.clear = self.submit = Button(self.bodyframe1,text="clear",font="arial 10",command=self.clearfield,bg="#2ecc71",fg="white").grid(row=6,column=1,pady=1)
        self.change_p = self.submit = Button(self.bodyframe1,text="Change",font="arial 10",command=self.change_password_data,bg="#ecf0f1",fg="black").grid(row=6,column=0,pady=1)

        self.bodyframe1.pack(side='left',anchor=NW)

    # show the list of files that you have saved
    def show(self):
        try:
            self.bodyframe2.destroy()
        except:
            pass
        self.bodyframe2 = Frame(self.root)

        filenames = get_filenames(service,folder_id)

        filenames_without_extension = [os.path.splitext(i)[0] for i in filenames]  # split file with name and extension

        """BUTTONS"""
        self.refreshbtn = Button(self.bodyframe2,text="refresh",font=" arial 8",bg="royal blue",fg="white",command=self.show).pack(side=TOP,padx=30,pady=3)
        self.closebtn = Button(self.bodyframe2,text="close",font=" arial 8",bg="royal blue",fg="white",command=self.bodyframe2.destroy).pack(side=TOP,padx=10,pady=3)

        """" canavs"""
        canvas = Canvas(self.bodyframe2,height=400,bg='grey',width=280,)

        """Scrollbar"""
        scrollbar = Scrollbar(self.bodyframe2)
        scrollbar.pack(side=RIGHT,fill=Y)
        canvas.pack(side=TOP,pady=(10,0))

        """config"""
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.yview)

        def on_scroll(event):
            canvas.yview_scroll(1 * int(event.delta / 120),"units")

        # Bind the mouse scroll event to the canvas
        canvas.bind("<MouseWheel>",on_scroll)
        # Add buttons to the canvas

        """When you place a button directly on a canvas in Tkinter, it is simply positioned over the canvas 
        but not actually part of the canvas’s drawable area. This means that if you scroll the canvas, 
        the button will not move because it’s not a canvas object; it’s just placed above the canvas in the window.
    On the other hand, when you create a window in the canvas using canvas.create_window, 
    you’re embedding the button into the canvas as an object. This makes the button part of the canvas’s drawable area, 
    and it will scroll along with the rest of the canvas content. This method is useful when you want the button 
    to be part of the scrollable area.
    """  # imp
        if len(filenames_without_extension) == 0:
            pass
        else:
            lebell = Label(canvas,bg='grey')
            canvas.create_window(5,5,window=lebell,width=250)
            max_filename_length = max(len(filename) for filename in filenames_without_extension)
            button_width = max_filename_length * 10
            for i in range(len(filenames_without_extension)):  # Example list of 20 buttons

                def printname(name=filenames_without_extension[i]):
                    self.decryption(name)

                def deletebutton(name=filenames_without_extension[i]):
                    pass
                    self.deletebuttons(name)

                self.button = Button(canvas,text=f'{filenames_without_extension[i]}',command=printname)
                self.delete = Button(canvas,text=f'D',command=deletebutton,bg='red',fg='white')
                canvas.create_window(10,(i * 40) + 20,window=self.button,width=button_width)
                canvas.create_window(button_width + 12,(i * 40) + 20,window=self.delete,width=25)

            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox('all'))
        self.bodyframe2.pack(side='right',anchor=NW)

    # delete the file
    def deletebuttons(self,name):
        answer = messagebox.askyesno("Confirm Delete",f"Are you sure you want to delete '{name}'?")
        if answer:
            try:self.clearfield()
            except:pass
            else:pass
            deletefile(service,folder_id,name)
            self.show()



        else:
            return

    # change password for data
    def change_password_data(self):  # for changing userdatapassword
        # messagebox.showwarning("alert","THis is in testing stage")
        password = self.password.get()
        name = self.filename.get()
        data = json.loads(downloadfile(service,folder_id,name))

        key = Fernet.generate_key()
        f = Fernet(key)
        password = f.encrypt(password.encode())
        password = password.decode()
        key = key.decode()
        f = Fernet(self.key)
        key_new = f.encrypt(key.encode())
        key = key_new.decode()

        data['password']['key'] = key
        data['password']['value'] = password
        with open(f'{name}.json','w') as file:
            json.dump(data,file,indent=4)
        updatedata(service,name,folder_id)
        self.clearfield()
        messagebox.showinfo("success",'password changed sucessfully')


if __name__ == "__main__":
    if os.path.isdir(""):
        pass
    else:
        os.makedirs("testing")
    os.chdir("")
    main()

