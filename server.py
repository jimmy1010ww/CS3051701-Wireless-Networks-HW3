import cv2
import socket
import math
import os
import numpy as np

# Serve 資訊
HOST = '127.0.0.1'
PORT = 12000

MAX_LENGTH = 60000

#client 
address = None

# 影片檔案名稱
VIDEO_FILE_NAME = 'video.mp4'

# Server 傳送模式
# 0 -> 需要client端回應 “OK”
# 1 -> 不需要client端回應 “OK”
server_mode = 0

#建立server socket
def initServerSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    print("Create server socket...")
    print("Waiting for client...")
    print("Server IP: " + HOST)
    print("Server Port: " + str(PORT))
    return s

#根據server傳送模式檢查client端是否有回應 “OK”
def checkClientOK():
    while True:
        global address
        if server_mode == 0:
            data, address = server_socket.recvfrom(4096)
            decode_data = data.decode("utf-8")
            print("Got connection from:")
            print("Client IP: " + address[0])
            print("Client Port: " + str(address[1]))
            print("====================================")
            print("Start sending video...")

            if decode_data == "OK":
                break
        elif server_mode == 1:
            break

#黑白化
def applyBlackAndWhite(frame):
    #套用灰階
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #套用黑白化

    #first argument  -> source image
    #second argument -> the threshold value which is used to classify the pixel values. 
    #third argument  -> the maximum value which is assigned to pixel values exceeding the threshold
    #fourth argument -> thresholding type

    #cv2.THRESH_BINARY -> If pixel value is greater than a threshold value, it is assigned one value (may be white), else it is assigned another value (may be black).
    ret, blackAndWhiteFrame = cv2.threshold(gray_frame, 115, 280,cv2.THRESH_BINARY)
    return blackAndWhiteFrame

#傳送影片
def sendVideoFrame(_frame, _address):

    #將影片編碼成jpg
    retval, buffer = cv2.imencode(".jpg", _frame)

    #如果編碼成功
    if retval:

        #將編碼後的影片轉成bytes
        frame_send = buffer.tobytes()

        #計算總共要傳送的長度
        buffer_size = len(frame_send)

        num_of_packs = 1
        #如果總共要傳送的長度大於最大長度
        if buffer_size > MAX_LENGTH:
            #計算總共要傳幾個pack   
            num_of_packs = math.ceil(buffer_size/MAX_LENGTH)

        print("Number of packs:", num_of_packs)
        frame_info = str(num_of_packs).encode("utf-8")
        server_socket.sendto(frame_info, _address)
    
        left = 0
        right = MAX_LENGTH

        for i in range(num_of_packs):
            data = frame_send[left:right]
            left = right
            right += MAX_LENGTH

            server_socket.sendto(data, _address)


if __name__ == "__main__":
    os.system("clear")

    #取得 server socket
    server_socket = initServerSocket()

    #檢查client端是否有回應 “OK”
    checkClientOK()


    try:
        #程式重複執行
        while True:
            #打開影片
            video_cap = cv2.VideoCapture(VIDEO_FILE_NAME)
            print("Start capture video.")

            #重複讀取影片
            while video_cap.isOpened():
                
                #ret 是布林值表示有沒有讀取到圖片
                #frame 是當前截取一幀的圖片
                ret, frame = video_cap.read()
                
                #如果沒有讀取到圖片，代表影片結束
                if not ret:
                    print("Video is over.")
                    video_cap.release()
                    break
                
                #傳送影片
                sendVideoFrame(frame, address)

                #接收使用者輸入
                keyboard_input = cv2.waitKey(25)

                #離開程式
                if keyboard_input == ord('q'):
                    print("Exit")
                    video_cap.release()
                    cv2.destroyAllWindows()
                    server_socket.close()
                    exit()
                #存當前frame    
                elif keyboard_input == ord('p'):
                    print("Save frame.jpg")
                    cv2.imwrite("Screenshot_origin.jpg", frame)
                    cv2.imwrite("Screenshot_filter.jpg", applyBlackAndWhite(frame))

                    #cv 讀取照片
                    cv2.imshow("Screenshot_origin", cv2.imread("Screenshot_origin.jpg"))
                    cv2.imshow("Screenshot_filter", cv2.imread("Screenshot_filter.jpg"))
                
                #顯示目前的frame
                cv2.imshow("Server original video", frame)
                cv2.imshow("Server video with filter", applyBlackAndWhite(frame))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        print("Exit")
        video_cap.release()
        cv2.destroyAllWindows()
        server_socket.close()
        exit()