import cv2
import mediapipe as mp
import pyautogui as p
import time
import math
import pyautogui as p


def check_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    wrist=hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    ring_pip=hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

    ring_mcp=hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]




    # for play and pause
    distances = [
        abs(wrist.y - index_tip.y),
        abs(wrist.y - middle_tip.y),
        abs(wrist.y - ring_tip.y),
        abs(wrist.y - pinky_tip.y),
        ]
    if all(i > 0.3 for i in distances) :
        p.hotkey('k')
        time.sleep(1.5)

    # for volume control
    v_distance=math.hypot(thumb_tip.x-ring_mcp.x,thumb_tip.y-ring_mcp.y)
    if abs(thumb_tip.y- index_tip.y) > 0.2  and middle_tip.y > index_tip.y and v_distance > 0.12:
        p.press('volumeup')
    if 0.01< abs(thumb_tip.y- index_tip.y) < 0.2   and middle_tip.y > index_tip.y and thumb_tip.y > index_tip.y and  v_distance > 0.12:
        p.press('volumedown')
        
    # mouse_cursur and click
    screen_width, screen_height = p.size()
    cur_disantace=math.hypot(index_tip.x-middle_tip.x,index_tip.y-middle_tip.y)
    if ring_tip.y>ring_pip.y and pinky_tip.y > pinky_pip.y and  index_pip.y > index_tip.y and middle_pip.y > middle_tip.y:
        if cur_disantace>0.1:
            x=middle_tip.x*screen_width*2
            y=middle_tip.y*screen_height*2
            p.moveTo(x, y)
         
        if cur_disantace >0.03 and cur_disantace < 0.06:
            p.click(clicks=2, interval=0.25)
            print("click")

    
        

   



if __name__=="__main__":
    mp_hands=mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    cap = cv2.VideoCapture(0)
    while True:
        ok,frame=cap.read()
        if not ok:
            break
        
        # convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label =='Left':
                    check_gesture(hand_landmarks)
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

   
        cv2.imshow("Hand Gesture Control", frame)   # Display the frame
        if cv2.waitKey(1) & 0xFF == ord('q'):    # Break the loop on 'q' key press
            break
        

