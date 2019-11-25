# -*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponse
from collections import Counter
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.template.loader import render_to_string, get_template
from ip_config import local_ip,port
from datetime import datetime
import time
import face_recognition
import os
import glob
import cv2
import csv
import sys
import numpy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render
import pandas as pd
import shutil
import json
face_cascade=cv2.CascadeClassifier('sample/static/opencv/haarcascade_frontalface_default.xml')
ip = "192.168.10.13"

accepted_face_data = []
accepted_name_list = []
waiting_face_data = []
waiting_name_list = []
rejected_face_data = []
rejected_name_list = []
#
print(accepted_face_data)
with open('sample/static/trained_data/accepted_list.csv', 'r') as readFile:
    reader = csv.reader(readFile)
    lines = list(reader)
for i in range(1,len(lines)):
    data=lines[i]
    accepted_name_list.append(data[0])
    en=data[1:]
    data=[]
    for k in en:
        data.append(float(k))
    accepted_face_data.append(data)
    # print(accepted_face_data)

red=[]
for img in glob.glob("sample/static/img_data/wait_list/*.jpg"):
    # Load a sample picture and learn how to recognize it.
    image = face_recognition.load_image_file(img)
    data = face_recognition.face_encodings(image)[0]
    waiting_face_data.append(data)
    name=img.split('/')
    
    user_name, ext = os.path.splitext(name[4])
    r=user_name
    
    waiting_name_list.append(user_name)
    red=waiting_name_list

with open('sample/static/trained_data/rejected_list.csv', 'r') as readFile:
    reader = csv.reader(readFile)
    lines = list(reader)
for i in range(1,len(lines)):
    data=lines[i]
    rejected_name_list.append(data[0])
    en=data[1:]
    data=[]
    for k in en:
        data.append(float(k))
    rejected_face_data.append(data)

face_locations = []
face_encodings = []
face_names = []
frame_number = 0
current_path = os.getcwd()
counter = 0
counter1 = 0


def base(request):
    return render(request, 'base.html')

#stream process of video capture:
def stream_video(request):
	return StreamingHttpResponse(stream_response_generator(),content_type="multipart/x-mixed-replace;boundary=frame")
#video capture:
def stream_response_generator():
    i=1
    video_capture=cv2.VideoCapture(0)
    while True:
        ret, frame = video_capture.read()
        
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        strs=[]
        face_names = []
        #check accetp list data:
        for face_encoding in face_encodings:
            match = face_recognition.compare_faces(accepted_face_data, face_encoding, tolerance=0.60)
            name = None
            if True in match:
                first_match_index = match.index(True)
                name = accepted_name_list[first_match_index]
        #end      
                
            else:
                #check rejectlist data:
                for face_encoding in face_encodings:
                    match = face_recognition.compare_faces(rejected_face_data, face_encoding, tolerance=0.60)
                    name = None
                    if True in match:
                        first_match_index = match.index(True)
                        name = rejected_name_list[first_match_index]
                    #end

                    else:
                        #check waiting list data:
                        for face_encoding in face_encodings:
                            match = face_recognition.compare_faces(waiting_face_data, face_encoding, tolerance=0.60)
                            name = None
                            if True in match:
                                first_match_index = match.index(True)
                                name = waiting_name_list[first_match_index]
                        #end        
                            
                            #new person take picture and encode his face data:    
                            else:
                                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                                faces=face_cascade.detectMultiScale(gray,1.3,5)
                                for (top, right, bottom, left) in faces:
                                    fram=frame[right-50:right+left+50,top-50:top+bottom+100]
                                    filename="sample/static/temp.jpg"
                                    out = cv2.imwrite(filename, fram)
                                    face_locations = face_recognition.face_locations(fram)
                                    face_encodings = face_recognition.face_encodings(fram, face_locations)
                            #end..        
 
                                    #check waiting list data:
                                    for face_encoding in face_encodings:
                                        match = face_recognition.compare_faces(waiting_face_data, face_encoding, tolerance=0.40)
                                        name = None
                                        if True in match:
                                            first_match_index = match.index(True)
                                            name = waiting_name_list[first_match_index]
                                    #end...
                                            
                                        #if not match of all take new picture and assigin new id process:    
                                        else:
                                            current_time=datetime.now()
                                            ts = int(time.time())
                                            id ="wid_"+str(ts)
                                            filename='sample/static/img_data/wait_list/'+id+'.jpg'
                                            out = cv2.imwrite(filename, fram)
                                            image = face_recognition.load_image_file(filename)
                                            data = face_recognition.face_encodings(image)[0]
                                            waiting_face_data.append(data)
                                            waiting_name_list.append(id)
                                            row = [id]
                                            for i in data:
                                                row.append(float(i))
                                            with open('sample/static/trained_data/waiting_list.csv', 'a') as csvFile:
                                                writer = csv.writer(csvFile)
                                                writer.writerow(row)
                                            csvFile.close()
                                        #end    
     
            #count process of wait,accept and reject in frame:                                
            strs.append(name)                
            d=[]    
            for x in strs:
                if not x:
                    x='bc'
                    print(x)
                q=x[0]                
                d.append(q)
                daaa=Counter(d)
                col = ['a','r','w'] 
                for color in col: 
                    s=color,daaa[color]
                
                    if 'a' in s:
                        row = []
                        sa=s
                        row.append(sa)
                        
                        with open('sample/static/trained_data/sample.csv', 'r') as readFile:
                            reader = csv.reader(readFile)
                            lines = list(reader)
                            lines = row
                        with open('sample/static/trained_data/sample.csv', 'w') as writeFile:
                            writer = csv.writer(writeFile)
                            writer.writerows(lines)

                        readFile.close()
                        writeFile.close()
                    elif 'w' in s:
                        row = []
                        sa=s 
                        row .append(sa)           
                        with open('sample/static/trained_data/test.csv', 'r') as readFile:
                            reader = csv.reader(readFile)
                            lines = list(reader)
                            lines = row
                        with open('sample/static/trained_data/test.csv', 'w') as writeFile:
                            writer = csv.writer(writeFile)
                            writer.writerows(lines)

                        readFile.close()
                        writeFile.close()
                    elif 'r' in s:     
                        row = []
                        sa=s
                        row.append(sa)          
                        with open('sample/static/trained_data/review.csv', 'r') as readFile:
                            reader = csv.reader(readFile)
                            lines = list(reader)
                            lines = row
                        with open('sample/static/trained_data/review.csv', 'w') as writeFile:
                            writer = csv.writer(writeFile)
                            writer.writerows(lines)

                        readFile.close()
                        writeFile.close()  
                    #end    

            #collection of frame list array;
            face_names.append(name)
            #end
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                #colour check in process:
                if not name:
                    continue
                if('wid_'in name):
                    c=(0,165,255)
                elif('rjd_'in name):
                    c=(0, 0, 255)
                else:
                    c= (34,139,34)
                #end    

                #rectangle frame and text will appear:
                cv2.rectangle(frame, (left, top), (right, bottom),c, 2)
                crop_img = frame[top:bottom, left:right]
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), c, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                #end
        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        #frame is empty count process is assign zero:
        if not face_encodings:
            sample =("a",0)
            row=[sample]
            with open('sample/static/trained_data/sample.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                lines = list(reader)
                lines = row
            with open('sample/static/trained_data/sample.csv', 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)

            readFile.close()
            writeFile.close()
            # print("******************")
            q=('w',0)
            test=[q]
            with open('sample/static/trained_data/test.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                lines = list(reader)
                lines = test

            with open('sample/static/trained_data/test.csv', 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)

            readFile.close()
            writeFile.close()
            w=('r',0)
            ded=[w]
            with open('sample/static/trained_data/review.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                lines = list(reader)
                lines = ded
            with open('sample/static/trained_data/review.csv', 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)

            readFile.close()
            writeFile.close()
        #end    
        else:
            pass
    del(camera)
#end of video capture:

#accept id function:
def accept(request,user_id):   
    s=user_id
    user_id=user_id[4:]
# wait list csv file has been moved
    df = pd.read_csv("sample/static/trained_data/waiting_list.csv")
    df.loc[df["user_id"]==s, "user_id"] = 'file-moved'
    df.to_csv("sample/static/trained_data/waiting_list.csv", index=False)    
    #waiting image file move to accept folder:
    old_file='sample/static/img_data/wait_list/'+"wid_"+str(user_id)+'.jpg'
    ts = int(time.time())
    id ="aid"+str(ts)
    #copy old file and move to new file process: 
    new_file='sample/static/img_data/accept_list/'+id+'.jpg'
    shutil.copy2(old_file, new_file)
    name=new_file.split('/')
    user_name, ext = os.path.splitext(name[4])
    #delete file process:
    os.remove(old_file)
    for i in range(0,len(waiting_name_list)):
        if(waiting_name_list[i]==s):
            waiting_name_list[i]=user_name
            data=waiting_face_data[i]
    accepted_face_data.append(data)
    accepted_name_list.append(user_name)
    row = [user_name]
    for i in data:
        row.append(float(i))
    with open('sample/static/trained_data/accepted_list.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()
    data=[{'message':user_id+" is Accepted Successfully"}]
    return HttpResponse(json.dumps(data), content_type="application/json")
#end
    
#waiting list data show in web :
def waiting_list(request):
    waiting_list=[] 
    with open('sample/static/trained_data/waiting_list.csv') as f: 
        data=[line.split(",")[0] for line in f]
         
    if(data):
        data=reversed(data)
        for i in data:
            a={'id':i}
            waiting_list.append(a)
        return render(request,'alert.html',{'data':waiting_list,'ip':local_ip,'port':port})
    else:
        return 0
#end

#reject id function:
def reject(request,user_id):
    s=user_id
    user_id=user_id[4:]
    #file move in waiting csv file:
    df = pd.read_csv("sample/static/trained_data/waiting_list.csv")
    df.loc[df["user_id"]==s, "user_id"] = 'file-moved'
    df.to_csv("sample/static/trained_data/waiting_list.csv", index=False)
    #waiting image file move to accept folder:
    old_file='sample/static/img_data/wait_list/'+"wid_"+str(user_id)+'.jpg'
    ts = int(time.time())
    id ="rjd_"+str(ts)
    new_file='sample/static/img_data/reject_list/'+id+'.jpg'
    #copy old file and move to new file process: 
    shutil.copy2(old_file, new_file)
    name=new_file.split('/')
    user_name, ext = os.path.splitext(name[4])
    # print(user_name)
    #delete file process:
    os.remove(old_file)
    
    for i in range(0,len(waiting_name_list)):
        if(waiting_name_list[i]==s):
            waiting_name_list[i]=user_name
            data=waiting_face_data[i]
    rejected_face_data.append(data)
    rejected_name_list.append(user_name)
    row = [user_name]
    for i in data:
        row.append(float(i))
    with open('sample/static/trained_data/rejected_list.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()
    data=[{'message':user_id+" is Rejected Successfully"}]
    return HttpResponse(json.dumps(data), content_type="application/json") 
#end

#waitinglist data send to app:
def notifi_data(request):
    waiting_list=[]
    with open('sample/static/trained_data/waiting_list.csv') as f:
        data=[line.split(",")[0] for line in f]
    data=reversed(data)
    for i in data:
        if (i !="sample" and i !="file-moved" and i !="user_id" ):
            a={'id':i,'image':'http://'+ip+':8000/static/img_data/wait_list/'+str(i)+'.jpg'}
            waiting_list.append(a)
    return HttpResponse(json.dumps(waiting_list), content_type="application/json")
  


#acceptlist data send to app:
def accept_api(request):
    accept_list=[]
    with open('sample/static/trained_data/accepted_list.csv') as f:
        data=[line.split(",")[0] for line in f]
        data=reversed(data)
        for i in data:
            if (i !="user_id" ):
                a={'id':i,'image':'http://'+ip+':8000/static/img_data/accept_list/'+str(i)+'.jpg'}
                accept_list.append(a)
        return HttpResponse(json.dumps(accept_list), content_type="application/json")

# rejectlist data send to app:
def rej_api(request):
    reject_list=[]
    with open('sample/static/trained_data/rejected_list.csv') as f:
        data=[line.split(",")[0] for line in f]
        data=reversed(data)
        for i in data:
            if (i !="user_id" ):
                a={'id':i,'image':'http://'+ip+':8000/static/img_data/reject_list/'+str(i)+'.jpg'}
                reject_list.append(a)
        return HttpResponse(json.dumps(reject_list), content_type="application/json")

#count acceptlist in frame:
def sam(request):
    with open('sample/static/trained_data/sample.csv') as f:
        data=[line for line in f]
        return HttpResponse(json.dumps(data), content_type="application/json")

#count waitinglist in frame:
def test(request):
    with open('sample/static/trained_data/test.csv') as f:
        data=[line for line in f]
        return HttpResponse(json.dumps(data), content_type="application/json")

#count rejectlist in frame:
def rev(request):
    with open('sample/static/trained_data/review.csv') as f:
        data=[line for line in f]
        return HttpResponse(json.dumps(data), content_type="application/json")

#Waitlist data clear and create new csv file in dashboard:
def delete(request):
    d=[]
    os.remove('sample/static/trained_data/waiting_list.csv')


    directory='sample/static/img_data/wait_list/'
    for i in glob.glob(os.path.join(directory,"*.jpg")):
        os.remove(i)
    return HttpResponse(json.dumps(d), content_type="application/json")
def create(request):
    da=[]
  
    s=[['user_id', ' 1',' 2',' 3',' 4',' 5',' 6',' 7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31',' 32',  '33',  '34',  '35',  '36',  '37',  '38', '39','40',  '41',  '42', ' 43', ' 44' ,' 45' , '46',  '47',  '48',  '49',  '50',  '51',  '52',  '53',  '54',  '55',  '56', ' 57',  '58' , '59',  '60',  '61',  '62',  '63',  '64',  '65',  '66' , '67' , '68' , '69',  '70' , '71',  '72',  '73' , '74',  '75' , '76',  '77',  '78',  '79',  '80',  '81',  '82',  '83',  '84', ' 85',  '86',  '87',  '88',  '89',  '90', ' 91',  '92',  '93',  '94'  ,'95',  '96' , '97',  '98',  '99' , '100', '101', '102', '103', '104', '105', '106' ,'107' ,'108 ','109' ,'110', '111', '112', '113' ,'114', '115', '116', '117', '118','119', '120', '121', '122', '123', '124', '125', '126', '127', '128']]
    with open('sample/static/trained_data/waiting_list.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(s)
        da=[{'message':" is create_waiting_list_csv Successfully"}]
    return HttpResponse(json.dumps(da), content_type="application/json")
#end

#reject data clear and create new csv file in dashboard: 
def clear(request):
    ata=[]
   
    os.remove('sample/static/trained_data/rejected_list.csv')

    directory='sample/static/img_data/reject_list/'
    for i in glob.glob(os.path.join(directory,"*.jpg")):
        os.remove(i)
    return HttpResponse(json.dumps(ata), content_type="application/json")
def add(request):
    ta=[]
   
    s=[['user_id', ' 1',' 2',' 3',' 4',' 5',' 6',' 7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31',' 32',  '33',  '34',  '35',  '36',  '37',  '38', '39','40',  '41',  '42', ' 43', ' 44' ,' 45' , '46',  '47',  '48',  '49',  '50',  '51',  '52',  '53',  '54',  '55',  '56', ' 57',  '58' , '59',  '60',  '61',  '62',  '63',  '64',  '65',  '66' , '67' , '68' , '69',  '70' , '71',  '72',  '73' , '74',  '75' , '76',  '77',  '78',  '79',  '80',  '81',  '82',  '83',  '84', ' 85',  '86',  '87',  '88',  '89',  '90', ' 91',  '92',  '93',  '94'  ,'95',  '96' , '97',  '98',  '99' , '100', '101', '102', '103', '104', '105', '106' ,'107' ,'108 ','109' ,'110', '111', '112', '113' ,'114', '115', '116', '117', '118','119', '120', '121', '122', '123', '124', '125', '126', '127', '128']]
    with open('sample/static/trained_data/rejected_list.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(s)
        ta=[{'message':" is create_rejected_list_csv Successfully"}]
    return HttpResponse(json.dumps(ta), content_type="application/json")
#end 


#start accept data clear and create new csv file in dashboard:
def cut(request):
    dt=[]
    os.remove('sample/static/trained_data/accepted_list.csv')

    directory='sample/static/img_data/accept_list/'
    for i in glob.glob(os.path.join(directory,"*.jpg")):
        os.remove(i)
    return HttpResponse(json.dumps(dt), content_type="application/json")
def generate(request):
    qw=[]
    s=[['user_id', ' 1',' 2',' 3',' 4',' 5',' 6',' 7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31',' 32',  '33',  '34',  '35',  '36',  '37',  '38', '39','40',  '41',  '42', ' 43', ' 44' ,' 45' , '46',  '47',  '48',  '49',  '50',  '51',  '52',  '53',  '54',  '55',  '56', ' 57',  '58' , '59',  '60',  '61',  '62',  '63',  '64',  '65',  '66' , '67' , '68' , '69',  '70' , '71',  '72',  '73' , '74',  '75' , '76',  '77',  '78',  '79',  '80',  '81',  '82',  '83',  '84', ' 85',  '86',  '87',  '88',  '89',  '90', ' 91',  '92',  '93',  '94'  ,'95',  '96' , '97',  '98',  '99' , '100', '101', '102', '103', '104', '105', '106' ,'107' ,'108 ','109' ,'110', '111', '112', '113' ,'114', '115', '116', '117', '118','119', '120', '121', '122', '123', '124', '125', '126', '127', '128']]
    with open('sample/static/trained_data/accepted_list.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(s)
        qw=[{'message':" is create_accepted_list_csv Successfully"}]
    return HttpResponse(json.dumps(qw), content_type="application/json")       
#end

#Photo menu in dashboard:
def gallery(request):   
    return render(request,'gallery.html')

#accept_image show in dashboard:
def Accept(request):
    e=[]
    with open('sample/static/trained_data/accepted_list.csv') as f: 
        data=[line.split(",")[0] for line in f]
         
    if(data):
        data=reversed(data)
        for i in data:
            a={'id':i}
            e.append(a)
        return render(request,'accept_list.html',{'data':e,'ip':local_ip,'port':port})
    
#reject_image show in dashboard:
def Reject(request):
    w=[]
    with open('sample/static/trained_data/rejected_list.csv') as f: 
        data=[line.split(",")[0] for line in f]
         
    if(data):
        data=reversed(data)
        for i in data:
            a={'id':i}
            w.append(a)
        return render(request,'reject_list.html',{'data':w,'ip':local_ip,'port':port})
    
#waithing_image show in dashboard:
def Waiting(request):
    df=[]
   
    with open('sample/static/trained_data/waiting_list.csv') as f: 
        data=[line.split(",")[0] for line in f]
         
    if(data):
        data=reversed(data)
        for i in data:
            a={'id':i}
            df.append(a)
        return render(request,'waiting_list.html',{'data':df,'ip':local_ip,'port':port})

#ignore data process:
def cans(request,user_id):
    sa=user_id
    print(sa)
    user_id=user_id[4:]
    df = pd.read_csv("sample/static/trained_data/waiting_list.csv")
    df.loc[df["user_id"]==sa, "user_id"] = 'file-moved'
    df.to_csv("sample/static/trained_data/waiting_list.csv", index=False)
    old_file='sample/static/img_data/wait_list/'+"wid_"+str(user_id)+'.jpg'
    os.remove(old_file)
    a=[{'message':user_id+" is Delete Successfully"}]
    return HttpResponse(json.dumps(a), content_type="application/json") 

def video(request):   
    qqq=[]
    return render(request,'video1111.html',{'data':qqq,'ip':local_ip,'port':port})

