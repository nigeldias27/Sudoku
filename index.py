from urllib import request
from flask import Flask, render_template,request,redirect
import cv2
import numpy
from tensorflow import keras
app = Flask(__name__)
def dl_predict(filename):
    img = cv2.imread('./images/'+filename)
    img = cv2.resize(img,(256,256))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 199, 5)
    def corner(a,b,c,d):
        s=False
        for x in range(0,256):
            if s==False:
                for l in range(2*x+1):
                    if int(d[abs(x-a),abs(l-b)])==c:
                        return (abs(x-a),abs(l-b))
                        s=True
                        break
            else:
                break
    x,y=corner(0,0,0,thresh)
    x1,_=corner(255,0,0,thresh)
    _,y1=corner(0,255,0,thresh)
    corner(255,255,0,thresh)
    cropped_thresh=thresh[x:x1,y:y1]
    cropped_thresh=cv2.resize(cropped_thresh,(256,256))
    x,y=corner(0,0,255,cropped_thresh)
    x1,_=corner(255,0,255,cropped_thresh)
    _,y1=corner(0,255,255,cropped_thresh)
    corner(255,255,255,cropped_thresh)
    cropped=cropped_thresh[x:x1,y:y1]
    cropped=cv2.resize(cropped,(256,256))
    #cv2.imshow('',cropped)
    l=[0,87,172]
    #cv2.imshow("fufhfhu",255-cropped)
    sudoku=[]
    for q in l:
        for a in range(3):
            row=[]
            for w in l:
                for b in range(3):
                    img=cv2.resize(cropped[q+(84//3*a):q+(84//3*(a+1)),w+(84//3*b):w+(84//3*(b+1))],(28,28))
                    empty=img[8:20,8:20]
                    boolempty=False
                    for emptya in range(12):
                            for emptyb in range(12):
                                if empty[emptya,emptyb]<=128:
                                    boolempty=True
                                    break
                    if boolempty==False:
                        row.append(0)
                    else:
                        img = 255 - img
     #                   cv2.imshow('',img)
                        x=numpy.expand_dims(img/255, axis=-1).reshape(1,28,28,1)
                        model=keras.models.load_model('MNIST (1).h5')

                        prediction=model.predict(x)
                        row.append(numpy.argmax(prediction[0]))
            sudoku.append(row)
    print(sudoku)
    def possible(y,x,n):
        nonlocal sudoku
        for i in range(9):
            if sudoku[y][i]==n:
                return False
        for i in range(9):
            if sudoku[i][x]==n:
                return False
        x0=x//3*3
        y0=y//3*3
        for  i in range(3):
            for j in range(3):
                if sudoku[y0+i][x0+j]==n:
                    return False
        return True
    def solve():
        nonlocal sudoku
        for y in range(9):
            for x in range(9):
                if sudoku[y][x]==0:
                    for n in range(1,10):
                        if possible(y,x,n):
                            sudoku[y][x]=n
                            solve()
                            sudoku[y][x]=0
                    return
        solved_sudoku=cv2.imread("sudo.png")
        for x in range(9):
            for y in range(9):
                solved_sudoku = cv2.rectangle(solved_sudoku, (57*x, 57*y), ((57*x) + (57*(x+1)), (57*y) + (57*(y+1))), (255,255,255), 1)
                cv2.putText(solved_sudoku, str(sudoku[y][x]), (57*x+20, 57*y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
      #  cv2.imshow('',solved_sudoku)
        cv2.imwrite('./static/sudoku.png',solved_sudoku)
    solve()
@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')
@app.route('/',methods=['POST'])
def predict():
    imagefile = request.files['imagefile']
    print(imagefile.filename)
    imagefile.save('./images/'+imagefile.filename)
    dl_predict(imagefile.filename)
    return render_template('index.html',finished="all done")
if __name__=='__main__':
    app.run()
