import cv2
import numpy as np
import winsound
import keyboard
import threading
import requests

def alert_sound():
    frequency = 2500  # Set frequency to 2500 Hertz
    duration = 10  # Set duration to 10 milliseconds
    winsound.Beep(frequency, duration)

def alert_image_Line(file):
    global access_token
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + access_token
    }
    data = ({
        'message':'Someone crossing the fence'
    })
    r=requests.post(url, headers=headers, files=file, data=data)

access_token = "-" #My token 

# Open the video file
cap = cv2.VideoCapture('-\\fence7.mp4')

# Variables to keep track of the previous frame's fence lines
prev_lines = []
prev_num_lines = 0

# Variables to keep alert status
alert_status = False

alert_count = 0

while cap.isOpened():
    # Read a frame from the video
    ret, frame = cap.read()

    if ret:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply Hough Transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, 390)

        # Count the number of lines and detect if any line is missing
        num_lines = 0
        missing_line = False
        if lines is not None:
            num_lines = len(lines)
            if num_lines < prev_num_lines:
                missing_line = True
        else:
            missing_line = True

        # Draw the lines on the frame and display the count
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                alert_count = 0
        else:
            #Save when alert
            cv2.imwrite("-\\alert_{}.jpg".format(cap.get(cv2.CAP_PROP_POS_FRAMES)), frame)
            alert_status = True
            if alert_status and alert_count == 0:
                alert_count = 1


        cv2.putText(frame, "Number of lines: {}".format(num_lines), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Generate an alert if a line is missing
        if missing_line:
            cv2.putText(frame, "ALERT: Missing fence line", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Update the previous frame's fence lines
        prev_lines = lines
        prev_num_lines = num_lines

        # Display the frame
        cv2.imshow('Fence Detection', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if alert_status:
            t1 = threading.Thread(target=alert_sound())
            t1.start()
            
        if alert_count == 1:
            file = {'imageFile':open("-\\alert\\alert_{}.jpg".format(cap.get(cv2.CAP_PROP_POS_FRAMES)),'rb')}
            t2 = threading.Thread(target=alert_image_Line(file))
            t2.start()
            alert_count = 3


        # Stop sound if 's' is pressed
        if keyboard.is_pressed("s"):
            alert_status = False

    else:
        break

cap.release()
cv2.destroyAllWindows()