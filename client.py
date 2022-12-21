import cv2
import socket
import os
import numpy as np

# Serve 資訊
HOST = '127.0.0.1'
PORT = 12000

MAX_LENGTH = 60000

#建立client socket
def initClientSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return s

#套用灰階
def applyGrayScale(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

def printConnectInfo():
    print("Connecting to server...")
    print("Server IP: " + HOST)
    print("Server Port: " + str(PORT))
    print("====================================")

if __name__ == "__main__":
    os.system("clear")

    try:
        #取得client socket
        client_socket = initClientSocket()

        #印出連線資訊
        printConnectInfo()
        
        #通知server端開始傳送影片
        client_socket.sendto("OK".encode("utf-8"), (HOST, PORT))


        while True:
            #接收server端傳送的影片pack數量
            data, address = client_socket.recvfrom(MAX_LENGTH)
            #如果影片data size小於100，代表是 nums_of_packs
            if len(data) < 100:
                nums_of_packs = int(data.decode("utf-8"))
                print(nums_of_packs)

                #接收server端傳送的影片
                for i in range(nums_of_packs):
                    data, address = client_socket.recvfrom(MAX_LENGTH)

                    #如果是第一個pack
                    if i == 0:
                        buffer = data
                    else:
                        buffer += data

                #將buffer轉成np array
                frame = np.frombuffer(buffer, dtype=np.uint8)
                #從np array轉成cv2的frame
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                #如果frame不是空的，且frame的型態是np array
                if frame is not None and type(frame) == np.ndarray:
                    #顯示frame
                    cv2.imshow("Client video with filter", applyGrayScale(frame))
                    keyboard_input = cv2.waitKey(25)
                    
                    #離開程式
                    if keyboard_input == ord('q'):
                        print("Exit")
                        cv2.destroyAllWindows()
                        client_socket.close()
                        exit()
                    #存當前frame    
                    elif keyboard_input == ord('p'):
                        print("Save frame.jpg")
                        cv2.imwrite("Screenshot_client.jpg", applyGrayScale(frame))

                        cv2.imshow("Screenshot_client", cv2.imread("Screenshot_client.jpg"))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        cv2.destroyAllWindows()
        exit()