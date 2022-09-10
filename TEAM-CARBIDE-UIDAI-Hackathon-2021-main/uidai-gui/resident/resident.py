from tkinter import *
from tkinter import simpledialog
import requests
import json
import uuid
import base64
import tempfile
import hashlib
from PIL import Image,ImageTk
from cryptography.fernet import Fernet

def genCap(canvas,status,capt):
	global ret
	global cap
	
	url = 'https://stage1.uidai.gov.in/unifiedAppAuthService/api/v2/get/captcha'
	headers = { 
		'Content-Type': 'application/json'
	}
	data = {
		'langCode':'en',
		'captchaLength':'3',
		'captchaType':'2'
	}
	response = requests.post(url=url,data=json.dumps(data),headers=headers)
	jsonData = json.loads(response.text)
	
	if jsonData and jsonData['status'] == 'Success':
		temp = tempfile.TemporaryFile()
		temp.write(base64.b64decode(jsonData['captchaBase64String']))
		img = Image.open(temp)
		img = img.resize((180,50))
		cap = ImageTk.PhotoImage(img)
		canvas.itemconfigure(capt,image = cap)
		
		ret = [True,jsonData['captchaTxnId']]
		
	else:
		ret = [False]
		canvas.itemconfigure(status,text = "Captcha Generation Error",fill="#d32828")

def fetchKyc(canvas,otp,scode,uid,fn,ln,m):
	url = 'https://stage1.uidai.gov.in/eAadhaarService/api/downloadOfflineEkyc'
	if ret[0]==True:
		txNum = ret[1]
	else:
		txNum = ""
	
	headers = { 
		'Content-Type': 'application/json'
	}
	data={
		"txnNumber": txNum,
		"otp":otp,
		"shareCode": scode,
		"uid": uid
	}
	response = requests.post(url=url,data=json.dumps(data),headers=headers)
	jsonData = json.loads(response.text)
	
	if jsonData['status'] == 'Success':
		kycZip = jsonData['eKycXML']
		mobileenc = m+scode
		for i in range(int(uid[-1])):
			mobileenc = (hashlib.sha256(mobileenc.encode()).hexdigest())
		kycDetails = {
				'name' : fn.lower()+' '+ln.lower(),
				'mobile' : mobileenc,
				'kycZip' : kycZip
			}
		key = hashlib.md5(scode.encode()).hexdigest()
		key = base64.urlsafe_b64encode(key.encode())
		encAuth = Fernet(key).encrypt(str.encode(json.dumps(kycDetails)))
		
		with open('kycVerify','wb') as file:
			file.write(encAuth)
		canvas.itemconfigure(status,text = '"kycVerify" generated',fill="#257f29")
	else:
		canvas.itemconfigure(status,text = "Failed Try Again",fill="#d32828")
		
def getOtp(canvas,status,captcha,aadhaar,firstname,lastname,contactno,secretcode):
	global ret
	global window 
	
	url = 'https://stage1.uidai.gov.in/unifiedAppAuthService/api/v2/generate/aadhaar/otp'
	if ret[0] == True:
		capId = ret[1]
	else:
		capId = ""
		
	reqId= str(uuid.uuid4())
	txId = 'MYAADHAAR:'+str(uuid.uuid4())
	headers = {
		'x-request-id':reqId,
		'appid':'MYAADHAAR',
		'Accept-Language':'en_in',
		'Content-Type': 'application/json'
	}
	data={
		"uidNumber": aadhaar.get(),
		"captchaTxnId": capId,
		"captchaValue": captcha.get(),
		"transactionId": txId
	}
	response = requests.post(url=url,data=json.dumps(data),headers=headers)
	jsonData = json.loads(response.text)
	if jsonData['status'] == 'Success':
		ret = [True,jsonData['txnId']]
		otp = simpledialog.askinteger("Input", "OTP",parent=window,minvalue=0, maxvalue=999999)
		fetchKyc(canvas,otp,secretcode.get(),aadhaar.get(),firstname.get(),lastname.get(),contactno.get())
	elif jsonData['message'] == 'Invalid Captcha':
		canvas.itemconfigure(status,text = "Invalid Captch",fill="#d32828")
	else:
		ret = [False]
		canvas.itemconfigure(status,text = "Error Generating Otp",fill="#d32828")
	
	



ret = [False]
cap = None 

window = Tk()
window.title('Resident App')
window.geometry("530x654")
window.configure(bg = "#ffffff")
ico = PhotoImage(file = f"res/ico.png")
window.iconphoto(False,ico)

canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 654,
    width = 530,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

background_img = PhotoImage(file = f"res/background.png")
background = canvas.create_image(
    265.5, 355.5,
    image=background_img)

firstname = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

firstname.place(
    x = 220, y = 238,
    width = 127,
    height = 17)

lastname = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

lastname.place(
    x = 220, y = 275,
    width = 127,
    height = 17)

aadhaar = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

aadhaar.place(
    x = 220, y = 315,
    width = 127,
    height = 17)

contactno = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

contactno.place(
    x = 220, y = 351,
    width = 127,
    height = 17)

secretcode = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

secretcode.place(
    x = 220, y = 392,
    width = 127,
    height = 17)

captcha = Entry(
    bd = 1,
    bg = "#eae0e0",
    highlightthickness = 0)

captcha.place(
    x = 220, y = 504,
    width = 127,
    height = 17)

status = canvas.create_text(
    265, 635,
    text = "Enter Data As Per Your Aadhar",
    fill = "#827878",
    font = ("Roboto", int(20.0)))

capt = canvas.create_image(
    280.0, 465.0,
    image = cap)
    
img0 = PhotoImage(file = f"res/img0.png")
b0 = Button(
    image = img0,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda: getOtp(canvas,status,captcha,aadhaar,firstname,lastname,contactno,secretcode),
    relief = "flat")

b0.place(
    x = 215, y = 560,
    width = 131,
    height = 38)

window.resizable(False, False)


genCap(canvas,status,capt)
window.mainloop()

