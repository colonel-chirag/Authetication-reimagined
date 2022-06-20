from tkinter import *
from tkinter import filedialog
import hashlib
import base64
import json
import tempfile
import zipfile
from xml.dom import minidom
from cryptography.fernet import Fernet
from signxml import XMLVerifier
from PIL import Image, ImageTk

def browse(canvas,filep):
	global kycPath
	kycPath = filedialog.askopenfilename()
	if len(kycPath) < 40:
		canvas.itemconfigure(filep,text = kycPath)
	else:
		canvas.itemconfigure(filep,text = kycPath[-39:])

def delentry(name,dob,gender):
	name.config(state = "normal")
	name.delete(0,END)
	name.config(state = "disabled")
	
	gender.config(state = "normal")
	gender.delete(0,END)
	gender.config(state = "disabled")
	
	dob.config(state = "normal")
	dob.delete(0,END)
	dob.config(state = "disabled")
	
	
def verify(canvas,name,status,dob,gender,face,code):
	
	delentry(name,dob,gender)
	
	global kycPath
	global face_img
	
	try:
		key = hashlib.md5(code.encode()).hexdigest()
		key = base64.urlsafe_b64encode(key.encode())
		decKyc = Fernet(key).decrypt(open(kycPath,'rb').read())
	except Exception as e:
		canvas.itemconfigure(status,text = "WRONG CODE",fill="#d32828")

	decKyc = json.loads(decKyc)

	kycZip = decKyc['kycZip']
	temp = tempfile.TemporaryFile()
	temp.write(base64.b64decode(kycZip))
	with zipfile.ZipFile(temp) as file:
		kyc = file.open(name = file.namelist()[-1], mode = 'r',pwd=code.encode())
	
	kycXml = minidom.parse(kyc)
	kyc = kycXml.toxml()
	cer = kycXml.getElementsByTagName('X509Certificate')[0].firstChild.nodeValue

	try:
		verify_result = XMLVerifier().verify(kyc, x509_cert=cer)
		certVer = True
	except Exception as e:
		verify_result = None
		certVer = False
    
	poi = kycXml.getElementsByTagName('Poi')
	pht = kycXml.getElementsByTagName('Pht')[0].firstChild.nodeValue

	for poi in poi:
		Name = poi.getAttribute('name').lower()
		Gender = poi.getAttribute('gender')
		DOB = poi.getAttribute('dob')
		mobile = poi.getAttribute('m')

	if Name == decKyc['name'] and mobile == decKyc['mobile']:
		dataVer = True
	else:
		dataVer = False

	if dataVer == False:
		canvas.itemconfigure(status,text = "DATA NOT VERIFIED",fill="#d32828")
	elif certVer == False:
		canvas.itemconfigure(status,text = "SIGNATURE NOT VERIFIED",fill="#d32828")
	else:
		name.config(state = "normal")
		name.insert(0,Name.upper())
		name.config(state = "readonly")
		if Gender == 'M':
			gender.config(state = "normal")
			gender.insert(0,"MALE")
			gender.config(state = "readonly")
		elif Gender == 'F':
			gender.config(state = "normal")
			gender.insert(0,"FEMALE")
			gender.config(state = "readonly")
		else:
			gender.config(state = "normal")
			gender.insert(0,"TRANSGENDER")
			gender.config(state = "readonly")
		dob.config(state = "normal")
		dob.insert(0,DOB)
		dob.config(state = "readonly")
		canvas.itemconfigure(status,text = "USER VERIFIED",fill ="#257f29")
		
		temp = tempfile.TemporaryFile()
		temp.write(base64.b64decode(pht))
		img = Image.open(temp)
		img = img.resize((160,200))
		face_img = ImageTk.PhotoImage(img)
		canvas.itemconfigure(face,image = face_img)

kycPath = None
face_img = None

window = Tk()
window.title('Verifier App')
window.geometry("547x634")
window.configure(bg = "#ffffff")
ico = PhotoImage(file = f"res/ico.png")
window.iconphoto(False,ico)

canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 634,
    width = 547,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

background_img = PhotoImage(file = f"res/background.png")
background = canvas.create_image(
    275.0, 329.5,
    image=background_img)

entry0 = Entry(
    bd = 1,
    bg = "#decccc",
    highlightthickness = 0)

entry0.place(
    x = 268, y = 186,
    width = 170,
    height = 19)

name = Entry(
    bd = 1,
    bg = "#000000",
    state='disabled',
    highlightthickness = 0)

name.place(
    x = 183, y = 396,
    width = 190,
    height = 15)

gender = Entry(
    bd = 1,
    bg = "#decccc",
    state='disabled',
    highlightthickness = 0)

gender.place(
    x = 183, y = 440,
    width = 190,
    height = 13)

dob = Entry(
    bd = 1,
    bg = "#decccc",
    state='disabled',
    highlightthickness = 0)

dob.place(
    x = 183, y = 482,
    width = 190,
    height = 15)

face = canvas.create_image(
    463.0, 448.0,
    image = face_img)

filep = canvas.create_text(
    154.0, 225.0,
    text = "",
    fill = "#827878",
    font = ("Roboto", int(10.0)))

status = canvas.create_text(
    265, 610,
    text = "Verification Status",
    fill = "#827878",
    font = ("Roboto", int(20.0)))
    
img0 = PhotoImage(file = f"res/img0.png")
b0 = Button(
    image = img0,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda : browse(canvas,filep),
    relief = "flat")

b0.place(
    x = 334, y = 217,
    width = 106,
    height = 16)

img1 = PhotoImage(file = f"res/img1.png")
b1 = Button(
    image = img1,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda: verify(canvas,name,status,dob,gender,face,entry0.get()),
    relief = "flat")

b1.place(
    x = 173, y = 293,
    width = 190,
    height = 26)

window.resizable(False, False)
window.mainloop()
