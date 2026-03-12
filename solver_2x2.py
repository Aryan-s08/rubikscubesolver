import time
import cv2
import numpy as np
import sys
elist = []
ecycles = 0
ccycles = 0
d1 = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B']}
d2 = {'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}

mappings_corner = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B'],
'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}

def move(letter):
    if letter == 'R':
        facer[0][0],facer[0][1],facer[1][0],facer[1][1] = facer[1][0],facer[0][0],facer[1][1],facer[0][1]
        facet[0][1],facet[1][1],facef[0][1],facef[1][1],faced[0][1],faced[1][1],faceb[0][0],faceb[1][0] = facef[0][1],facef[1][1],faced[0][1],faced[1][1],faceb[1][0],faceb[0][0],facet[1][1],facet[0][1]
    if letter == "R'":
        facer[0][0],facer[0][1],facer[1][0],facer[1][1] = facer[0][1],facer[1][1],facer[0][0],facer[1][0]
        facet[0][1],facet[1][1],facef[0][1],facef[1][1],faced[0][1],faced[1][1],faceb[0][0],faceb[1][0] = faceb[1][0],faceb[0][0],facet[0][1],facet[1][1],facef[0][1],facef[1][1],faced[1][1],faced[0][1]
    if letter == 'L':
        facel[0][0],facel[0][1],facel[1][0],facel[1][1] = facel[1][0],facel[0][0],facel[1][1],facel[0][1]
        facet[0][0],facet[1][0],facef[0][0],facef[1][0],faced[0][0],faced[1][0],faceb[0][1],faceb[1][1] = faceb[1][1],faceb[0][1],facet[0][0],facet[1][0],facef[0][0],facef[1][0],faced[1][0],faced[0][0]
    if letter == "L'":
        facel[0][0],facel[0][1],facel[1][0],facel[1][1] = facel[0][1],facel[1][1],facel[0][0],facel[1][0]
        facet[0][0],facet[1][0],facef[0][0],facef[1][0],faced[0][0],faced[1][0],faceb[0][1],faceb[1][1] = facef[0][0],facef[1][0],faced[0][0],faced[1][0],faceb[1][1],faceb[0][1],facet[1][0],facet[0][0]
    if letter == 'D':
        faced[0][0],faced[0][1],faced[1][0],faced[1][1] = faced[1][0],faced[0][0],faced[1][1],faced[0][1]
        facef[1][0],facef[1][1],facer[1][0],facer[1][1],faceb[1][0],faceb[1][1],facel[1][0],facel[1][1] = facel[1][0],facel[1][1],facef[1][0],facef[1][1],facer[1][0],facer[1][1],faceb[1][0],faceb[1][1]
    if letter == "D'":
        faced[0][0],faced[0][1],faced[1][0],faced[1][1] = faced[0][1],faced[1][1],faced[0][0],faced[1][0]
        facef[1][0],facef[1][1],facer[1][0],facer[1][1],faceb[1][0],faceb[1][1],facel[1][0],facel[1][1] = facer[1][0],facer[1][1],faceb[1][0],faceb[1][1],facel[1][0],facel[1][1],facef[1][0],facef[1][1]
    if letter == "F":
        facef[0][0],facef[0][1],facef[1][0],facef[1][1] = facef[1][0],facef[0][0],facef[1][1],facef[0][1]
        facet[1][0],facet[1][1],facer[0][0],facer[1][0],faced[0][0],faced[0][1],facel[0][1],facel[1][1] = facel[1][1],facel[0][1],facet[1][0],facet[1][1],facer[1][0],facer[0][0],faced[0][0],faced[0][1]
    if letter == "F'":
        facef[0][0],facef[0][1],facef[1][0],facef[1][1] = facef[0][1],facef[1][1],facef[0][0],facef[1][0]
        facet[1][0],facet[1][1],facer[0][0],facer[1][0],faced[0][0],faced[0][1],facel[0][1],facel[1][1] = facer[0][0],facer[1][0],faced[0][1],faced[0][0],facel[0][1],facel[1][1],facet[1][1],facet[1][0]
    if letter == "U":
        facet[0][0],facet[0][1],facet[1][0],facet[1][1] = facet[1][0],facet[0][0],facet[1][1],facet[0][1]
        facef[0][0],facef[0][1],facer[0][0],facer[0][1],faceb[0][0],faceb[0][1],facel[0][0],facel[0][1] = facer[0][0],facer[0][1],faceb[0][0],faceb[0][1],facel[0][0],facel[0][1],facef[0][0],facef[0][1]
    if letter == "U'":
        facet[0][0],facet[0][1],facet[1][0],facet[1][1] = facet[0][1],facet[1][1],facet[0][0],facet[1][0]
        facef[0][0],facef[0][1],facer[0][0],facer[0][1],faceb[0][0],faceb[0][1],facel[0][0],facel[0][1] = facel[0][0],facel[0][1],facef[0][0],facef[0][1],facer[0][0],facer[0][1],faceb[0][0],faceb[0][1]


def opposite(colour):
    if colour == 'W':
        return 'Y'
    elif colour == 'B':
        return 'G'
    elif colour == 'Y':
        return 'W'
    elif colour == 'G':
        return 'B'
    elif colour == 'O':
        return 'R'
    elif colour == 'R':
        return 'O'
def corner(l1,l2,l3):
    d1 = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B']}
    d2 = {'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}
    for i in d1:
        if [l1,l2,l3] == d1[i]:
            return i
    for i in d2:
        if [l1,l2,l3] == d2[i]:
            return i
def findc(letter):
    if letter == 'A':
        return [facet[0][0],facel[0][0],faceb[0][1]]
    if letter == 'B':
        return [facet[0][1],facer[0][1],faceb[0][0]]
    if letter == 'C':
        return [facet[1][1],facer[0][0],facef[0][1]]
    if letter == 'D':
        return [facet[1][0],facel[0][1],facef[0][0]]
    if letter == 'E':
        return [facel[0][0],facet[0][0],faceb[0][1]]
    if letter == 'F':
        return [facel[0][1],facet[1][0],facef[0][0]]
    if letter == 'G':
        return [facel[1][1],faced[0][0],facef[1][0]]
    if letter == 'H':
        return [facel[1][0],faced[1][0],faceb[1][1]]
    if letter == 'I':
        return [facef[0][0],facet[1][0],facel[0][1]]
    if letter == 'J':
        return [facef[0][1],facet[1][1],facer[0][0]]
    if letter == 'K':
        return [facef[1][1],faced[0][1],facer[1][0]]
    if letter == 'L':
        return [facef[1][0],faced[0][0],facel[1][1]]
    if letter == 'M':
        return [facer[0][0],facet[1][1],facef[0][1]]
    if letter == 'N':
        return [facer[0][1],facet[0][1],faceb[0][0]]
    if letter == 'O':
        return [facer[1][1],faced[1][1],faceb[1][0]]
    if letter == 'P':
        return [facer[1][0],faced[0][1],facef[1][1]]
    if letter == 'Q':
        return [faceb[0][0],facet[0][1],facer[0][1]]
    if letter == 'R':
        return [faceb[0][1],facet[0][0],facel[0][0]]
    if letter == 'S':
        return [faceb[1][1],faced[1][0],facel[1][0]]
    if letter == 'T':
        return [faceb[1][0],faced[1][1],facer[1][1]]
    if letter == 'U':
        return [faced[0][0],facel[1][1],facef[1][0]]
    if letter == 'V':
        return [faced[0][1],facer[1][0],facef[1][1]]
    if letter == 'W':
        return [faced[1][1],facer[1][1],faceb[1][0]]
    if letter == 'X':
        return [faced[1][0],facel[1][0],faceb[1][1]]
    return [0,0,0]

def csolved():
    s = 0
    edgelist = []
    d1 = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B']}
    d2 = {'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}
    for i in d1:
        t = samec(i)
        if t[0] not in edgelist and t[1] not in edgelist and i != 'R' and i != 'E' and i != 'A':
            edgelist.append(i)
    for i in d2:
        t = samec(i)
        if i not in edgelist and t[0] not in edgelist and t[1] not in edgelist and i != 'R' and i != 'E' and i != 'A':
            edgelist.append(i)
    #print("SOLVED ",edgelist)
    for i in edgelist:
        if findc(i) == d1[i] or findc(i) == d2[i]:
            s += 1
    #print("solved ",s)
    #print("cycle",ccycles)
    return s
def samec(letter):
    if letter == 'A':
        return ['R','E']
    if letter == 'B':
        return ['N','Q']
    if letter == 'C':
        return ['J','M']
    if letter == 'D':
        return ['I','F']
    if letter == 'E':
        return ['A','R']
    if letter == 'F':
        return ['D','I']
    if letter == 'G':
        return ['U','L']
    if letter == 'H':
        return ['S','X']
    if letter == 'I':
        return ['D','F']
    if letter == 'J':
        return ['C','M']
    if letter == 'K':
        return ['V','P']
    if letter == 'U':
        return ['G','L']
    if letter == 'L':
        return ['U','G']
    if letter == 'M':
        return ['C','J']
    if letter == 'N':
        return ['Q','B']
    if letter == 'O':
        return ['W','T']
    if letter == 'P':
        return ['V','K']
    if letter == 'Q':
        return ['N','B']
    if letter == 'R':
        return ['A','E']
    if letter == 'S':
        return ['X','H']
    if letter == 'T':
        return ['W','O']
    if letter == 'V':
        return ['K','P']
    if letter == 'W':
        return ['T','O']
    if letter == 'X':
        return ['S','H']
def newccycle():
    #print("FUNC ",corners)
    edgelist = []
    elist = []
    for i in mappings_corner:
        if i not in ['E','A','R']:
            edgelist.append(i)
    #print("ed ",edgelist)
    edgelist1 = edgelist.copy()
    for i in edgelist1:
        if i in corners:
            #print(i,same(i))
            t = samec(i)
            if i in edgelist:
                edgelist.remove(i)
            if t[0] in edgelist:
                edgelist.remove(t[0])
            if t[1] in edgelist:
                edgelist.remove(t[1])
    edgelist1 = edgelist.copy()
    #print("edgelist",edgelist)
    #print("edgelist1",edgelist1)
    #print("elist",elist)
    for i in edgelist1:
        t = findc(i)
        if t == d1[i] or t == d2[i]:
            edgelist.remove(i)
    #print("Edgelist",edgelist)
    #print("Edgelist1",edgelist1)
    #print("Elist",elist)
    if edgelist == []:
        return 0
    else:
        for i in edgelist:
            t = findc(i)
            elist.append(t)
        #print("edgelisT",edgelist)
        #print("edgelisT1",edgelist1)
        #print("elisT",elist)
        return edgelist[0]

def corneralg(letter):
    if letter == 'B':
        return "R2"
    if letter == 'U':
        return "D"
    if letter == 'C':
        return "F2 D"
    if letter == 'I':
        return "F R'"
    if letter == "W":
        return "D'"
    if letter == 'S':
        return "D F'"
    if letter == 'D':
        return "F2"
    if letter == 'F':
        return "F' D"
    if letter == 'G':
        return "F'"
    if letter == 'H':
        return "D' R"
    if letter == 'J':
        return "R'"
    if letter == 'K':
        return "F' R'"
    if letter == 'L':
        return "F2 R'"
    if letter == 'M':
        return "F"
    if letter == 'N':
        return "R' F"
    if letter == 'O':
        return "R2 F"
    if letter == 'P':
        return "R F"
    if letter == 'Q':
        return "R D'"
    if letter == 'T':
        return "R"
    if letter == 'V':
        return ""
    if letter == 'X':
        return "D2"
    return [0,0]
def reversecorneralg(letter):
    if letter == 'B':
        return "R2"
    if letter == 'U':
        return "D'"
    if letter == 'C':
        return "D' F2"
    if letter == 'I':
        return "R F'"
    if letter == "W":
        return "D"
    if letter == 'S':
        return "F D'"
    if letter == 'D':
        return "F2"
    if letter == 'F':
        return "D' F"
    if letter == 'G':
        return "F"
    if letter == 'H':
        return "R' D"
    if letter == 'J':
        return "R"
    if letter == 'K':
        return "R F"
    if letter == 'L':
        return "R F2"
    if letter == 'M':
        return "F'"
    if letter == 'N':
        return "F' R"
    if letter == 'O':
        return "F' R2"
    if letter == 'P':
        return "F' R'"
    if letter == 'Q':
        return "D R'"
    if letter == 'T':
        return "R'"
    if letter == 'V':
        return ""
    if letter == 'X':
        return "D2"
def decode(letter):
    if letter == 'W':
        return 'White'
    elif letter == 'B':
        return 'Blue'
    elif letter == 'G':
        return 'Green'
    elif letter == 'Y':
        return 'Yellow'
    elif letter == 'O':
        return 'Orange'
    elif letter == 'R':
        return 'Red'

corners = []

while True:

    GRID_SIZE = 2

    def capture_frame_once(prompt_text):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return None

        print(prompt_text)
        frame_captured = None

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            box = 160
            x1 = w//2 - box//2
            y1 = h//2 - box//2
            x2 = x1 + box
            y2 = y1 + box
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,255), 2)

            cv2.putText(frame, prompt_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            cv2.imshow("Calibration", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 32:  # SPACE
                frame_captured = frame.copy()
                break
            if key == ord('q'):
                frame_captured = None
                break

        cap.release()
        cv2.destroyAllWindows()
        return frame_captured


    def avg_center_hsv(frame, size=100):
        h, w = frame.shape[:2]
        x1 = w//2 - size//2
        y1 = h//2 - size//2
        roi = frame[y1:y1+size, x1:x1+size]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        return np.mean(hsv.reshape(-1,3), axis=0)


    def hue_distance(a, b):
        d = abs(a - b)
        return min(d, 180 - d)


    def hsv_distance(a, b):
        dh = hue_distance(a[0], b[0]) / 10
        ds = (a[1] - b[1]) / 50
        dv = (a[2] - b[2]) / 50
        return np.sqrt(dh*dh + ds*ds + dv*dv)


    def match_color(hsv_value, centers):
        best = None
        best_dist = 999
        for cname, center in centers.items():
            d = hsv_distance(hsv_value, center)
            if d < best_dist:
                best_dist = d
                best = cname
        return best


    def calibrate_colors():
        order = ["W","Y","O","R","G","B"]
        names = {"W":"White","Y":"Yellow","O":"Orange",
                "R":"Red","G":"Green","B":"Blue"}

        centers = {}

        print("\n=== 2x2 CUBE COLOR CALIBRATION ===")
        print("Show ANY sticker of the given color.\n")

        for c in order:
            frame = capture_frame_once(f"Show {names[c]} sticker and press SPACE")
            if frame is None:
                sys.exit()

            centers[c] = avg_center_hsv(frame)
            print(f"{c} calibrated:", centers[c].astype(int))

        return centers

    def scan_face(face_name, centers):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            sys.exit()

        size = 300
        grid = None

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            x1 = w//2 - size//2
            y1 = h//2 - size//2
            x2 = x1 + size
            y2 = y1 + size

            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

            face = frame[y1:y2, x1:x2]
            hsv_face = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)

            step = size // GRID_SIZE
            grid = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    yA = r*step + step//4
                    yB = r*step + 3*step//4
                    xA = c*step + step//4
                    xB = c*step + 3*step//4

                    region = hsv_face[yA:yB, xA:xB]
                    avg = np.mean(region.reshape(-1,3), axis=0)
                    col = match_color(avg, centers)
                    grid[r][c] = col

                    cv2.rectangle(frame,
                                (x1+c*step, y1+r*step),
                                (x1+(c+1)*step, y1+(r+1)*step),
                                (255,0,0), 1)

                    cv2.putText(frame, col,
                                (x1+c*step+20, y1+r*step+40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

            cv2.putText(frame, f"Face: {face_name}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
            cv2.putText(frame, "Y=Confirm  N=Rescan  Q=Quit", (10,h-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)

            cv2.imshow("2x2 Cube Scanner", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('y'):
                break
            if key == ord('n'):
                continue
            if key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()

        cap.release()
        cv2.destroyAllWindows()
        return grid


    def manual_edit(grid, centers):
        while True:
            print("\nDetected grid:")
            for row in grid:
                print(row)

            ch = input("Edit any sticker? (y/n): ").lower()
            if ch == 'n':
                return grid

            try:
                r, c = map(int, input("Row Col (1-2): ").split())
                r -= 1; c -= 1

                if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
                    print("Invalid position")
                    continue

                print("Available colors:", list(centers.keys()))
                newc = input("Enter color: ").upper()
                if newc not in centers:
                    print("Invalid color")
                    continue

                grid[r][c] = newc
            except:
                print("Invalid input")

    facef = [[],[],[]]
    facet = [[],[],[]]
    facer = [[],[],[]]
    facel = [[],[],[]]
    faceb = [[],[],[]]
    faced = [[],[],[]]
    def main():
        global facet,facer,facel,facef,faceb,faced
        centers = calibrate_colors()

        face_order = ["TOP","FRONT","RIGHT","LEFT","BEHIND","BOTTOM"]
        cube = {}

        for face in face_order:
            grid = scan_face(face, centers)
            print(f"\nDetected {face}:")
            for row in grid:
                print(row)

            grid = manual_edit(grid, centers)
            cube[face] = grid
            print(f"✔ Saved {face}")

        print("\n=== FINAL CUBE ===")
        for f in face_order:
            if f == "TOP":
                facet = cube[f]
            if f == "RIGHT":
                facer = cube[f]
            if f == "LEFT":
                facel = cube[f]
            if f == "BOTTOM":
                faced = cube[f]
            if f == "BEHIND":
                faceb = cube[f]
            if f == "FRONT":
                facef = cube[f]
        for i in [facet,facer,facel,facef,faced,faceb]:
            for j in range(2):
                i[j] = i[j][::-1]
    if __name__ == "__main__":
        main()

    ccycles = 0

    check = {'W':0, 'B':0,'R':0, 'G':0, 'Y':0, 'O':0}
    valid = 1
    for i in [facer,facel,faceb,faced,facet,facef]:
        for j in i:
            for k in j:
                check[k] += 1
    for i in check:
        if check[i] != 4:
            print("You have entered " + str(check[i])+" pieces of " + i + " instead of 4.")
            print()
            valid = 0
            continue
    if valid == 0:
        continue
    all_corners = [[facet[0][0],facel[0][0],faceb[0][1]],[facet[0][1],facer[0][1],faceb[0][0]],[facet[1][0],facef[0][0],facel[0][1]],[facet[1][1],facef[0][1],facer[0][0]],[faced[0][0],facef[1][0],facel[1][1]],[faced[0][1],facef[1][1],facer[1][0]],[faced[1][0],facel[1][0],faceb[1][1]],[faced[1][1],facer[1][1],faceb[1][0]]]
    valid = 1
    for j in all_corners:
        for k in j:
            if opposite(k) in j or j.count(k) > 1:
                print("jk",j,k)
                valid = 0
    if valid == 0:
        print("You made a mistake in entering the colours")
        continue

    while True:
        buffer1 = facel[0][0]
        buffer2 = facet[0][0]
        buffer3 = faceb[0][1]
        if buffer1 in ['W','B','O'] and buffer2 in ['W','B','O'] and buffer3 in ['W','B','O']:
            ccycles += 1
            let = newccycle()
            #print("let",let)
            t = findc(let)
            #print("t",t)
            buffer1,buffer2,buffer3 = t[0],t[1],t[2]
            if buffer1 == 0:
                break
        while (buffer1 not in ['W','B','O'] or buffer2 not in ['W','B','O'] or buffer3 not in ['W','B','O']) or (len(corners) != 7 - csolved() + ccycles):
            if len(corners) == 7 - csolved() + ccycles:
                #print("lol")
                #print("corners ",corners)
                break
            print('corners = ',corners, 'letters = ',buffer1,buffer2,buffer3)
            dict = {}
            for i in corners:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 1:
                    t = samec(i)
                    if t[0] not in dict and t[1] not in dict:
                        continue
                    else:
                        if corner(buffer1,buffer2,buffer3) == i:
                            buffer1 = 0
                if dict[i] == 2:
                    if corner(buffer1,buffer2,buffer3) == i:
                        buffer1 = 0
            if buffer1 in ['W','B','O'] and buffer2 in ['W','B','O'] and buffer3 in ['W','B','O']:
                buffer1 = 0
            if buffer1 == 0:
                #print("fehifehi")
                ccycles += 1
                let = newccycle()
                #print("let",let)
                t = findc(let)
                #print("t",t)
                buffer1,buffer2,buffer3 = t[0],t[1],t[2]
                if buffer1 == 0:
                    break
                else:
                    continue
            if corner(buffer1,buffer2,buffer3) != 'E' and corner(buffer1,buffer2,buffer3) != 'R' and corner(buffer1,buffer2,buffer3) != 'A': 
                corners.append(corner(buffer1,buffer2,buffer3))
                #print(corners)
            dict = {}
            for i in corners:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 1:
                    t = samec(i)
                    if t[0] not in dict and t[1] not in dict:
                        continue
                    else:
                        if corner(buffer1,buffer2,buffer3) == i:
                            buffer1 = 0
                if dict[i] == 2:
                    if corner(buffer1,buffer2,buffer3) == i:
                        buffer1 = 0
            if buffer1 != 0:
                t = findc(corner(buffer1,buffer2,buffer3))
                buffer1,buffer2,buffer3 = t[0], t[1], t[2]
            if (buffer1 in ['W','B','O'] and buffer2 in ['W','B','O'] and buffer3 in ['W','B','O']) or buffer1 == 0:
                dict = {}
                for i in corners:
                    if i in dict:
                        dict[i] += 1
                    else:
                        dict[i] = 1
                for i in dict:
                    if dict[i] == 1:
                        t = samec(i)
                        if t[0] not in dict and t[1] not in dict:
                            continue
                        else:
                            if corner(buffer1,buffer2,buffer3) == i:
                                buffer1 = 0
                    if dict[i] == 2:
                        if corner(buffer1,buffer2,buffer3) == i:
                            buffer1 = 0
                if buffer1 == 0:
                    ccycles += 1
                    let = newccycle()
                    #print("let",let)
                    t = findc(let)
                    #print("t",t)
                    buffer1,buffer2,buffer3 = t[0],t[1],t[2]
                    if buffer1 == 0:
                        break
                    else:
                        continue
        break
    #print("FINAL EDGES ",edges)
    #print("FINAL CORNERS ",corners)
    
    string = ""
    
    for i in corners:
        if i != 'V':
            string += corneralg(i) + " R U' R' U' R U R' F' R U R' U' R' F R " + reversecorneralg(i) + " "
        else:
            string += "R U' R' U' R U R' F' R U R' U' R' F R "
    i = 0
    while True:
        if i >= len(string) - 1:
            break
        print(string[i]+string[i+1])
        if string[i] == 'R' and string[i + 1] != "'":
            move('R')
            if string[i + 1] == '2':
                move('R')
                i += 1
            i += 2
        elif string[i] == 'R' and string[i + 1] == "'":
            move("R'")
            i += 3
        elif string[i] == 'L' and string[i + 1] != "'":
            move('L')
            if string[i + 1] == '2':
                move('L')
                i += 1
            i += 2
        elif string[i] == 'L' and string[i + 1] == "'":
            move("L'")
            i += 3
        elif string[i] == 'U' and string[i + 1] != "'":
            move('U')
            if string[i + 1] == '2':
                move('U')
                i += 1
            i += 2
        elif string[i] == 'U' and string[i + 1] == "'":
            move("U'")
            i += 3
        elif string[i] == 'D' and string[i + 1] != "'":
            move('D')
            if string[i + 1] == '2':
                move('D')
                i += 1
            i += 2
        elif string[i] == 'D' and string[i + 1] == "'":
            move("D'")
            i += 3
        elif string[i] == 'F' and string[i + 1] != "'":
            move('F')
            if string[i + 1] == '2':
                move('F')
                i += 1
            i += 2
        elif string[i] == 'F' and string[i + 1] == "'":
            move("F'")
            i += 3
        elif string[i] == 'B' and string[i + 1] != "'":
            move('B')
            if string[i + 1] == '2':
                move('B')
                i += 1
            i += 2
        elif string[i] == 'B' and string[i + 1] == "'":
            move("B'")
            i += 3
        elif string[i] == 'M' and string[i + 1] != "'":
            move('M')
            if string[i + 1] == '2':
                move('M')
                i += 1
            i += 2
        elif string[i] == 'M' and string[i + 1] == "'":
            move("M'")
            i += 3
        
        print("FACET ",facet)
        print("FACEF ",facef)
        print("FACED ",faced)
        print("FACER ",facer)
        print("FACEL ",facel)
        print("FACEB ",faceb)
        print()
    
    if facet == [['W','W'],['W','W']] and facef == [['G','G'],['G','G']] and facer == [['R','R'],['R','R']] and facel == [['O','O'],['O','O']] and faceb == [['B','B'],['B','B']] and faced == [['Y','Y'],['Y','Y']]:
        break
    else:
        print("You made a mistake in entering the colours")
        ans = input("Are you sure you want to get the moves to find out if you have a twisted piece, type no to enter choices if you have entered incorrectly?: ")
        if ans.lower() == 'yes':
            break
        continue
    break
print()
stri = "Note: Hold your 3x3 cube such that center of side facing you is Green and center of side above is White [Sometimes the piece mentioned as solved may not be necessarily solved immediately but would be solved within the next few moves]"
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
print()
print("Moves Guide:")
print()
print("R: Move the vertical right layer in front, upwards by 1")
print("R': Move the vertical right layer in front, downwards by 1")
print("R2: Move the vertical right layer in front, in any direction by 2")
print("L: Move the vertical left layer in front, downwards by 1")
print("L': Move the vertical left layer in front, upwards by 1")
print("L2: Move the vertical let layer in front, in any direction by 2")
print("U: Move the top horizontal layer in front, from right to left by 1")
print("U': Move the top horizontal layer in front, from left to right by 1")
print("U2: Move the top horizontal layer in front, in any direction by 2")
print("D: Move the bottom horizontal right layer in front, from left to right by 1")
print("D': Move the bottom horizontal layer in front, from right to left by 1")
print("D2: Move the bottom horizontal layer in front, in any direction by 2")
print("F: Move 1 layer of the entire front 3x3 face clockwise (left to right) by 1")
print("F': Move 1 layer of the entire front 3x3 face anti-clockwise (right to left) by 1")
print("F2: Move 1 layer of the entire front 3x3 face in any direction by 2")
print("B: Move 1 layer of the behind 3x3 face from right to left by 1")
print("B': Move 1 layer of the behind 3x3 face from left to right by 1")
print("B2: Move 1 layer of the behind 3x3 face from in any direction by 2")
print("M: Move the vertical middle layer in front, downwards by 1")
print("M': Move the vertical middle layer in front, upwards by 1")
print("M2: Move the vertical middle layer in front, in any direction by 2")
print()
print()


for i in corners:
    stri = i+": "+corneralg(i) + " (R U' R' U' R U R' F' R U R' U' R' F R) "+ reversecorneralg(i)+ " [" + decode(mappings_corner[i][0])+ " - "+decode(mappings_corner[i][1])+" - "+decode(mappings_corner[i][2])+" corner solved]"
    for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
print()
length = 0
for i in string:
    if i in ['M','L','R','U','D','F','B']:
        length += 1

stri = "Blindfold corners sequence: "
for i in corners:
    stri += i + " "
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
stri = "Number of moves required: " + str(length)
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
input("Click Enter to exit program:")

