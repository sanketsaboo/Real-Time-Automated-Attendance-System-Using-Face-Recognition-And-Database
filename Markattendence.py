import os
import cv2
import numpy as np
import face_recognition
import datetime
from datetime import datetime
from datetime import date
import mysql.connector
import pymysql


detected=[]

try:
   mydb = pymysql.connect(host="127.0.0.1", user="root", password="", db="Face_recog")
except:
    print("Can't connect to database")

mycursor = mydb.cursor()


path = 'Images'
images = []
studentNames = []
studentList = os.listdir(path)
print(studentList)

for student in studentList:
    currentImage = cv2.imread(f'{path}/{student}')
    images.append(currentImage)
    studentNames.append(os.path.splitext(student)[0])
print(studentNames)


def findEncoding(images):
    encodedList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_recognition.face_encodings(img)[0]
        encodedList.append(encodeimg)
    return encodedList


def addToCSV(name):

    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        dateList = []
        for line in myDataList:
            entry = line.split(',')
            # print(entry)
            nameList.append(entry[0])
            today = date.today()
            dateString = today.strftime("%m/%d/%Y")
            # dateList.append(entry[2])
            dates_1 = dateString
            # print(nameList)


        # print(dateString)
        if name not in nameList:
            now = datetime.now()
            today = date.today()
            timeeString = now.strftime('%H:%M:%S')
            dateString = today.strftime("%d/%m/%Y")
            # dateList.append(dateString)
            # print(dateList)
            f.writelines(f'\n{name},{timeeString},{dateString}')
            sqlFormula = "INSERT INTO attendance (Name,Date,Time) VALUES (%s,%s,%s)"
        
            attendance = [name, dateString,timeeString]
            mycursor.execute(sqlFormula, attendance)
            mydb.commit()

        elif dates_1 not in dateList:
            # print(dates_1)
            dateList.append(date)
            now = datetime.now()
            today = date.today()
            timeeString = now.strftime('%H:%M:%S')
            dateString = today.strftime("%d/%m/%Y")
            f.writelines(f'\n{name},{timeeString},{dateString}')
            sqlFormula = "INSERT INTO attendance (Name,Date,Time) VALUES (%s,%s,%s)"
            attendance = [name, dateString,timeeString]
            mycursor.execute(sqlFormula,attendance)
            mydb.commit()


encodeListRecognised = findEncoding(images)
print("encoding finished")

# use image to compare to from web cam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imageResized = cv2.resize(img, (0, 0), None, 0.25, 0.25) #reducing the img size to 1/4 to make sure
    imageResized = cv2.cvtColor(imageResized, cv2.COLOR_BGR2RGB)

    facesintheFrame = face_recognition.face_locations(imageResized) #find locations of all faces and send to the next line(encodingFaces)
    encodeintheFrame = face_recognition.face_encodings(imageResized, facesintheFrame)

    # To find matches
    for encodedface, faceLoc in zip(encodeintheFrame, facesintheFrame):
        matches = face_recognition.compare_faces(encodeListRecognised, encodedface) #compare faces
        faceDistance = face_recognition.face_distance(encodeListRecognised, encodedface) #few time faces can have similarities so to find the best match we use distance Also lower the best better the match
        # print(faceDis)
        matchingIndex = np.argmin(faceDistance)
        # print(matchingIndex)

        if matches[matchingIndex]:
            name = studentNames[matchingIndex]
            if name not in detected:
                detected.append(name) #to add name only once in the file and database
                print(name)
                addToCSV(name)
            y1, x2, y2, x1 = faceLoc #storing the values of face location returned by face_recognition.face_locations(imageResized)
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2) #the inner rectangle around face 
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED) #the outer rectangle around face and fills it 
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2) #Just to put text near the rectangle

            
            
        else:
            print("else reached")
            name = "Unknown"
            y1, x2, y2, x1 = faceLoc        #Repeated comments from the above section
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  #inorder to revive back the original image to put name around it
    
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            addToCSV("Unknown")

        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

    cv2.imshow('WebCam', img)
    cv2.waitKey(1)