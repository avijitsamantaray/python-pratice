import cv2
import mediapipe as mp
import pyautogui as p
import time


# cont=0
def check_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    wrist=hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # for play and pause
    distances = [
        abs(wrist.y - index_tip.y),
        abs(wrist.y - middle_tip.y),
        abs(wrist.y - ring_tip.y),
        abs(wrist.y - pinky_tip.y),
        ]
    if all(i > 0.3 for i in distances) :
        p.hotkey('space')
        time.sleep(1.5)

    # for volume control
    if abs(thumb_tip.y- index_tip.y) > 0.2  and middle_tip.y > index_tip.y:
        p.press('volumeup')
        
        
    if 0.01< abs(thumb_tip.y- index_tip.y) < 0.2   and middle_tip.y > index_tip.y and thumb_tip.y > index_tip.y:
        p.press('volumedown')
        

   



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
        

