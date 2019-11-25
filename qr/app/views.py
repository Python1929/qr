from django.shortcuts import render,redirect,get_object_or_404
from .models import User,Staff,Contractor,Visitor,EntryExit
from app.forms import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
import qrcode
import time
from PIL import Image
# from Crypto.Cipher import AES
from cryptography.fernet import Fernet
# Create your views here.
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from django.http import StreamingHttpResponse
import json
import sys
from twilio.rest import Client

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        print("ssss")
        if user_form.is_valid() :
            user = user_form.save()
            user.set_password(user.password)
            # registered_user = User.objects.values_list('id',flat=True).latest('id')
            user.save()
            print("Registered successfully")
            registered = True
            messages.success(request, 'Account created successfully')
            return redirect('/userlogin')
        else:
            messages.success(request,'Already Registered')
            print("iiiiiiiiiii",user_form.errors)

    else:
        user_form = UserForm()
        # profile_form = UserProfileInfoForm()
    return render(request,'register.html',{'user_form':user_form,'registered':registered})


def userlogin(request):
  
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print(User.objects.filter(email=username))
        name = User.objects.get(username = username)
        print("username:",name)
        
        
        user = authenticate(username=name, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect('/dashboard')
            else:
                return HttpResponse("Your account was inactive.")

        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            messages.success(request, 'Invalid Password')

            return redirect('/userlogin')        
        
    # else:
    #     u_list = User.objects.values_list("email",flat=True)
    #     print(u_list)
    #     # for u in userlist:
    #     #     u_list = u.email
    #     #     print(u_list,">>>>>>>>>>>")
        
    return render(request,'login.html')     
        


def dashboard(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    return render(request,'index.html',{'loginusername':loginusername,'loginemail':loginemail})

def staff(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    
    return render(request,'staffs.html',{'loginusername':loginusername,'loginemail':loginemail})

def contractor(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    if request.method == 'POST':
        contractorname = request.POST.get('contractorname')
        contractorid = request.POST.get('contractorid')
        companyname = request.POST.get('companyname')
        mailid = request.POST.get('mailid')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        # contractor = Contractor.objects.create(contractorname=contractorname,contractorid=contractorid,companyname=companyname,mailid=mailid,phone=phone,address=address)
        # contractor = Contractor(contractorname=contractorname,contractorid=contractorid,companyname=companyname,mailid=mailid,phone=phone,address=address)
        # contractor.save()
        # Create qr code instance
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
        )
        
        # The data that you want to store
        data =('Name:'+ contractorname,'id:'+contractorid,'Company:'+ companyname,'Phone:'+ phone,'Email:'+ mailid,'Address:'+ address)
        print(data,"rfsdfs")
        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image()

        # Save it somewhere, change the extension as needed:
        img.save("app/static/qrdata/Contractor/"+ contractorname+".png")
        qrcodeimage = "app/static/qrdata/Contractor/"+ contractorname +".png"
        contractor = Contractor(contractorname=contractorname,contractorid=contractorid,companyname=companyname,mailid=mailid,phone=phone,address=address,qrimage=qrcodeimage)
        contractor.save()
        print("Image Saved Sucessfully")
        #img.show(title="Qr")
        # img.save("image.bmp")
        # img.save("image.jpeg")
        #img.save("image.jpg")
        account_sid = 'AC127ce20676faa219890e8cb944102c18'
        auth_token = '8086a7cee88d1996c995d01e49233d15'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                #body='This is Your Qr Code For Entry And Exit',
                body='Welcome to our Company This is the code for entry and exit',
                media_url=['http://127.0.0.1:8000/static/qrdata/Contractor/'+contractorname+".png"],
                #media_url=["qrdata/smsimage.png"],
                from_='+15186926536',
                to='+918148350120'
            )
        print(message.sid)
        print ("Sms Sent Sucessfully")

        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(b"A really secret message. Not for prying eyes.")
        plain_text = cipher_suite.decrypt(cipher_text)
        print(plain_text)
    c = Contractor.objects.all()
    # print(c)
    return render(request,'contractors.html',{'loginusername':loginusername,'loginemail':loginemail,"contractor":c})
    # return render(request,'contractors.html',{'loginusername':loginusername,'loginemail':loginemail})

def visitor(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    if request.method == 'POST':
        visitorname = request.POST.get('visitorname')
        mailid = request.POST.get('mailid')
        phone = request.POST.get('phone')
        purpose = request.POST.get('purpose')
        # contractor = Contractor.objects.create(contractorname=contractorname,contractorid=contractorid,companyname=companyname,mailid=mailid,phone=phone,address=address)
        # visitor = Visitor(visitorname=visitorname,mailid=mailid,phone=phone,purpose=purpose) 
        # visitor.save()
        # Create qr code instance
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
        )

        # The data that you want to store
        data =('Name:'+ visitorname,'Phone:'+ phone,'Email:'+ mailid,'Purpose:'+ purpose)
        print(data,"rfsdfs")
        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image()

        # Save it somewhere, change the extension as needed:
        img.save("app/static/qrdata/Visitor/"+ visitorname +".png")
        # http://127.0.0.1:8000/static/qrdata/Visitor/revathi.png
        qrcodeimage = "app/static/qrdata/Visitor/"+ visitorname +".png"
        visitor = Visitor(visitorname=visitorname,mailid=mailid,phone=phone,purpose=purpose,qrimage=qrcodeimage) 
        visitor.save()
        print("Image Saved Sucessfully")
        #img.show(title="Qr")
        # img.save("image.bmp")
        # img.save("image.jpeg")
        #img.save("image.jpg")
        account_sid = 'ACd9655ed09cbdb45c5ac2181ceaca308d'
        auth_token = 'b1cab5063ede8ebd41a12a29da06809c'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                #body='This is Your Qr Code For Entry And Exit',
                body='Welcome to our Company This is the code for entry and exit',
                media_url=['http://127.0.0.1:8000/static/qrdata/Visitor/'+visitorname+".png"],
                #media_url=["qrdata/smsimage.png"],
                from_='+12052939343',
                to='+918680854271'
            )
        print(message.sid)
        print ("Sms Sent Sucessfully")
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(b"A really secret message. Not for prying eyes.")
        plain_text = cipher_suite.decrypt(cipher_text)
        print(plain_text)
    v = Visitor.objects.all()
    print(v)
    return render(request,'visitor.html',{'loginusername':loginusername,'loginemail':loginemail,"visitor":v})


def entryexit(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    entryexit = EntryExit.objects.all()
    return render(request,'entryexit.html',{'loginusername':loginusername,'loginemail':loginemail,'entryexit':entryexit})

def contractordelete(request,contractordelete_id =None):
    object = Contractor.objects.get(id=contractordelete_id)
    object.delete()
    return redirect('/contractor/')
def visitordelete(request,visitordelete_id =None):
    object = Visitor.objects.get(id=visitordelete_id)
    object.delete()
    return redirect('/visitor/')
# def visitordelete(request,visitordelete_id =None):
#     object = Visitor.objects.get(id=contractodelete_id)
#     object.delete()
#     return redirect('/visitor/')

def visitoredit(request,visitoredit_id=None):
    visitor = Visitor.objects.get(id=visitoredit_id)
    id = visitor.id
    v_name = visitor.visitorname
    v_mailid = visitor.mailid
    v_phone = visitor.phone
    v_purpose = visitor.purpose
    if request.method == "POST":
        vnew_name = request.POST.get('visitorname')
        vnew_mailid = request.POST.get('mailid')
        vnew_phone = request.POST.get('phone')
        vnew_purpose = request.POST.get('purpose')
        # contractor.save()
        # Create qr code instance
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
        )

        # The data that you want to store
        data =('Name:'+ vnew_name,'Phone:'+ vnew_phone,'Email:'+ vnew_mailid,'Purpose:'+ vnew_purpose)
        print(data,"rfsdfs")
        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image()

        # Save it somewhere, change the extension as needed:
        img.save("app/static/qrdata/Visitor/"+ vnew_name +".png")
        # http://127.0.0.1:8000/static/qrdata/Visitor/revathi.png
        qrcodeimage = "app/static/qrdata/Visitor/"+ vnew_name +".png"
        visitor = Visitor.objects.filter(id=id).update(visitorname=vnew_name,mailid=vnew_mailid,phone=vnew_phone,purpose=vnew_purpose,qrimage=qrcodeimage)

        # img.save("image.bmp")
        # img.save("image.jpeg")
        #img.save("image.jpg")

        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(b"A really secret message. Not for prying eyes.")
        plain_text = cipher_suite.decrypt(cipher_text)
        print(plain_text)
        return redirect('/visitor')
    
    print("Name:",v_name)
    return render(request,'visitoredit.html',{'id':id,'visitorname':v_name,'mailid':v_mailid,'phone':v_phone,'purpose':v_purpose})


def contractoredit(request,contractoredit_id=None):
    contractor = Contractor.objects.get(id=contractoredit_id)
    id = contractor.id
    c_name = contractor.contractorname
    c_id = contractor.contractorid
    c_company = contractor.companyname
    c_mailid = contractor.mailid
    c_phone = contractor.phone
    c_address = contractor.address
    if request.method == "POST":
        cnew_name = request.POST.get('contractorname')
        cnew_id = request.POST.get('contractorid')
        cnew_company = request.POST.get('companyname')
        cnew_mailid = request.POST.get('mailid')
        cnew_phone = request.POST.get('phone')
        cnew_address = request.POST.get('address')
        contractor = Contractor.objects.filter(id=id).update(contractorname=cnew_name,contractorid=cnew_id,companyname=cnew_company,mailid=cnew_mailid,phone=cnew_phone,address=cnew_address)
        # contractor.save()
        # Create qr code instance
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 4,
        )

        # The data that you want to store
        data =('Name:'+ cnew_name,'Company:'+ cnew_company,'Phone:'+cnew_phone,'Email:'+cnew_mailid,'Address:'+ cnew_address)
        print(data,"rfsdfs")
        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image()

        # Save it somewhere, change the extension as needed:
        img.save("app/static/qrdata/image.png"+str(time.strftime(" %Y_%m_%d_%H_%M")))
        print("Image Saved Sucessfully")
        img.show()
        # img.save("image.bmp")
        # img.save("image.jpeg")
        #img.save("image.jpg")

        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(b"A really secret message. Not for prying eyes.")
        plain_text = cipher_suite.decrypt(cipher_text)
        print(plain_text)
        return redirect('/contractor')
    
    print("Name:",c_name)
    return render(request,'contractoredit.html',{'id':id,'contractorname':c_name,'contractorid':c_id,'companyname':c_company,'mailid':c_mailid,'phone':c_phone,'address':c_address})

def qrscanner(request):
    loginusername = request.user.username
    # print("............",loginusername)
    loginid = request.user.id
    loginemail = request.user.email
    return render(request,'qrscanner.html',{'loginusername':loginusername,'loginemail':loginemail})    

def stream_video(request):
	#data=StreamingHttpResponse(stream_response_generator(),content_type="multipart/x-mixed-replace;boundary=frame")
	return StreamingHttpResponse(media(request),content_type="multipart/x-mixed-replace;boundary=frame")

# def media():
#     cap = cv2.VideoCapture(0)
#     font = cv2.FONT_HERSHEY_PLAIN

#     while True:
#         _, frame = cap.read()

#         decodedObjects = pyzbar.decode(frame)
#         for obj in decodedObjects:
#             name = "janani"
#             contract = Contractor.objects.all()
#             for c in contract:
#                 cname = c.contractorname
#                 if name in cname:
#                     print(cname)
#                 else:
#                     print("not matched")
#                 return 

#         imgencode=cv2.imencode('.jpg',frame)[1]
#         stringData=imgencode.tostring()
#         yield (b'--frame\r\n'
# 			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
#     del(camera)
def media(request):
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    hasOpened = False

    while True:
        _, frame = cap.read()

        decodedObjects = pyzbar.decode(frame)
        for obj in decodedObjects:
            #print(obj.data)
            datac=obj.data
            name=datac.decode("utf-8")
            # n = json.dumps(name)
            # res = json.loads(n)
            # print("res:<<<<",res)
            print('*****',name)
            
            res = dict(item.split(":") for item in name.split(", "))
            print('......>>>>>>',res)
            len_name = len(res)
            print(len_name)
         
            if obj.data and not hasOpened:
                print("data here")
                hasOpened = True
                print("retrive data:",name)
                if len_name == 4:
                    a,b,c,d = name.split(",")
                    s=a
                    v = (s.split(':')[1])
                    qr_name = v.strip("'")
                    print(qr_name)
                    # qr_name = v["Name"]
                    # print(qr_name)
                    vname = qr_name
                    visitor = Visitor.objects.all()
                    print("Visitors:",visitor)

                    if (Visitor.objects.filter(visitorname=vname).exists()):
                        # visitorname = vname
                        print("......",vname)
                        print("matched")
                        EntryExit.objects.create(name=vname,category="Visitor")
                        
                        return render(request,'qrscanner.html',{'name':vname})
                    else:
                        print("not matched")
                        
                        return render(request,'qrscanner.html',{'name':vname})
                else:
                    a,b,c,d,e,f = name.split(",")
                    s=a
                    v = (s.split(':')[1])
                    qr_name = v.strip("'")
                    print(qr_name)
            
                    vname = qr_name
                    contractor = Contractor.objects.all()
                    print("Contractors:",contractor)
                    
                   
                    if (Contractor.objects.filter(contractorname=vname).exists()):
                        # visitorname = vname
                        print("......",vname)
                        print("matched")
                        EntryExit.objects.create(name=vname,category="Contractor")

                        return render(request,'qrscanner.html',{'name':vname})
                    else:
                        print("not matched")
                        return render(request,'qrscanner.html',{'name':vname})

        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
    del(camera)
                    