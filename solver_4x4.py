import time
import cv2
import numpy as np
import sys
while True:
    GRID_SIZE = 4
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

            cv2.imshow("Calibration Window", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 32:
                frame_captured = frame.copy()
                break
            if key == ord('q'):
                frame_captured = None
                break

        cap.release()
        cv2.destroyAllWindows()
        return frame_captured


    def avg_center_hsv(frame, size=80):
        h, w = frame.shape[:2]
        x1 = w//2 - size//2
        y1 = h//2 - size//2
        box = frame[y1:y1+size, x1:x1+size]
        hsv = cv2.cvtColor(box, cv2.COLOR_BGR2HSV)
        return np.mean(hsv.reshape(-1,3), axis=0)


    def hue_distance(a, b):
        d = abs(a-b)
        return min(d, 180-d)


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


    def calibrate_all_colors():
        order = ["W","Y","O","R","G","B"]
        order1 = {"W":"White","R":"Red","B":"Blue","Y":"Yellow","O":"Orange","G":"Green"}
        centers = {}

        print("\n=== 4x4 CUBE COLOR CALIBRATION ===")
        print("Show ANY sticker of the given color inside the box.\n")

        for cname in order:
            frame = capture_frame_once(f"Show {order1[cname]} sticker and press SPACE")
            if frame is None:
                sys.exit()

            centers[cname] = avg_center_hsv(frame, 120)
            print(f"{cname} calibrated:", centers[cname].astype(int))

        return centers



    def scan_face_live(face_name, centers):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            sys.exit()

        size = 320
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
                                (x1+c*step+8, y1+r*step+30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

            cv2.putText(frame, f"Face: {face_name}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
            cv2.putText(frame, "Y=Confirm  N=Rescan  Q=Quit", (10,h-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)

            cv2.imshow("4x4 Cube Scanner", frame)
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
                r, c = map(int, input("Row Col (1-4): ").split())
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
        centers = calibrate_all_colors()

        face_order = ["TOP","FRONT","RIGHT","LEFT","BEHIND","BOTTOM"]
        cube = {}

        for face in face_order:
            grid = scan_face_live(face, centers)
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
            for j in range(4):
                i[j] = i[j][::-1]
        print("FACET ",facet)
        print("FACEF ",facef)
        print("FACER ",facer)
        print("FACEL ",facel)
        print("FACEB ",faceb)
        print("FACED ",faced)
    if __name__ == "__main__":
        main()
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
    check = {'W':0, 'B':0,'R':0, 'G':0, 'Y':0, 'O':0}
    valid = 1
    for i in [facer,facel,faceb,faced,facet,facef]:
        for j in i:
            for k in j:
                check[k] += 1
    for i in check:
        if check[i] != 16:
            print("You have entered " + str(check[i])+" pieces of " + i + " instead of 16.")
            print()
            valid = 0
            continue
    if valid == 0:
        continue
    all_edges = [[facet[0][1],faceb[0][2]],[facet[0][2],faceb[0][1]],[facet[1][3],facer[0][2]],[facet[2][3],facer[0][1]],[facet[3][1],facef[0][1]],[facet[3][2],facef[0][2]],[facet[1][0],facel[0][1]],[facet[2][0],facel[0][2]],
    [faced[0][1],facef[3][1]],[faced[0][2],facef[3][2]],[faced[1][3],facer[3][1]],[faced[2][3],facer[3][2]],[faced[3][1],faceb[3][2]],[faced[3][2],faceb[3][1]],[faced[1][0],facel[3][2]],[faced[2][0],facel[3][1]],
    [facef[1][0],facel[1][3]],[facef[2][0],facel[2][3]],[facef[1][3],facer[1][0]],[facef[2][3],facer[2][0]],[faceb[1][0],facer[1][3]],[faceb[2][0],facer[2][3]],[faceb[1][3],facel[1][0]],[faceb[2][3],facel[2][0]]]
    all_corners = [[facet[0][0],facel[0][0],faceb[0][3]],[facet[0][3],facer[0][3],faceb[0][0]],[facet[3][0],facef[0][0],facel[0][3]],[facet[3][3],facef[0][3],facer[0][0]],[faced[0][0],facef[3][0],facel[3][3]],[faced[0][3],facef[3][3],facer[3][0]],[faced[3][0],facel[3][0],faceb[3][3]],[faced[3][3],facer[3][3],faceb[3][0]]]
    valid = 1
    for i in [all_edges,all_corners]:
        for j in i:
            for k in j:
                if opposite(k) in j or j.count(k) > 1:
                    print("jk",j,k)
                    valid = 0
    if valid == 0:
        print("You made a mistake in entering the colours")
        continue

    elist = []
    cycled_lets = []
    ecycles = 0
    cycle = 0
    ccycles = 0
    cecycles = 0
    cycle = {}
    d1 = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B']}
    d2 = {'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}

    mappings_corner = {'A':['W','O','B'],'B':['W','R','B'],'C':['W','R','G'],'D':['W','O','G'],'E':['O','W','B'],'F':['O','W','G'],'G':['O','Y','G'],'H':['O','Y','B'],'I':['G','W','O'],'J':['G','W','R'],'K':['G','Y','R'],'L':['G','Y','O'],'M':['R','W','G'],'N':['R','W','B'],'O':['R','Y','B'],'P':['R','Y','G'],'Q':['B','W','R'],'R':['B','W','O'],'S':['B','Y','O'],'T':['B','Y','R'],'U':['Y','O','G'],'V':['Y','R','G'],'W':['Y','R','B'],'X':['Y','O','B'],
    'A':['W','B','O'],'B':['W','B','R'],'C':['W','G','R'],'D':['W','G','O'],'E':['O','B','W'],'F':['O','G','W'],'G':['O','G','Y'],'H':['O','B','Y'],'I':['G','O','W'],'J':['G','R','W'],'K':['G','R','Y'],'L':['G','O','Y'],'M':['R','G','W'],'N':['R','B','W'],'O':['R','B','Y'],'P':['R','G','Y'],'Q':['B','R','W'],'R':['B','O','W'],'S':['B','O','Y'],'T':['B','R','Y'],'U':['Y','G','O'],'V':['Y','G','R'],'W':['Y','B','R'],'X':['Y','B','O']}
    mappings_edge = {'A':['W','B'],'B':['W','R'],'C':['W','G'],'D':['W','O'],'E':['O','W'],'F':['O','G'],'G':['O','Y'],'H':['O','B'],'I':['G','W'],'J':['G','R'],'K':['G','Y'],'L':['G','O'],'M':['R','W'],'N':['R','B'],'O':['R','Y'],'P':['R','G'],'Q':['B','W'],'R':['B','O'],'S':['B','Y'],'T':['B','R'],'U':['Y','G'],'V':['Y','R'],'W':['Y','B'],'X':['Y','O']}
    mappings_centre = {'A':['W'],'B':['W'],'C':['W'],'D':['W'],'E':['O'],'F':['O'],'G':['O'],'H':['O'],'I':['G'],'J':['G'],'K':['G'],'L':['G'],'M':['R'],'N':['R'],'O':['R'],'P':['R'],'Q':['B'],'R':['B'],'S':['B'],'T':['B'],'U':['Y'],'V':['Y'],'W':['Y'],'X':['Y'],}
    for i in mappings_centre:
        cycle[i] = 0
    def edge(l1,l2):
        for i in mappings_edge:
            if mappings_edge[i] == [l1,l2]:
                return i

    def centre(l1):
        print("CYCCCC ",cycle,cecycles)
        order = centres[::-1]
        for i in mappings_centre:
            if i not in order:
                order.append(i)
        for i in order:
            print("iiii ",i,l1)
            if ((i != 'A') and (mappings_centre[i] == [l1]) and [l1] != cefind(i)) and ((cycle[i] == 1 and centres.count(i) < 2) or (cycle[i] == 0 and i not in centres)):
                return i

    def move(letter):
        global facer,facel,facef,faceb,facet,faced
        if letter == 'R':
            facer[0][0],facer[0][3],facer[3][0],facer[3][3] = facer[3][0],facer[0][0],facer[3][3],facer[0][3]
            facer[0][1],facer[1][3],facer[3][2],facer[2][0] = facer[2][0],facer[0][1],facer[1][3],facer[3][2]
            facer[0][2],facer[2][3],facer[3][1],facer[1][0] = facer[1][0],facer[0][2],facer[2][3],facer[3][1]
            facet[0][3],facet[3][3],facef[0][3],facef[3][3],faced[0][3],faced[3][3],faceb[0][0],faceb[3][0] = facef[0][3],facef[3][3],faced[0][3],faced[3][3],faceb[3][0],faceb[0][0],facet[3][3],facet[0][3]            
            facet[1][3],facet[2][3],facef[1][3],facef[2][3],faced[1][3],faced[2][3],faceb[1][0],faceb[2][0] = facef[1][3],facef[2][3],faced[1][3],faced[2][3],faceb[2][0],faceb[1][0],facet[2][3],facet[1][3]
            facer[1][1],facer[1][2],facer[2][1],facer[2][2] = facer[2][1],facer[1][1],facer[2][2],facer[1][2]
        elif letter == "R'":
            facer[0][0],facer[0][3],facer[3][0],facer[3][3] = facer[0][3],facer[3][3],facer[0][0],facer[3][0]
            facer[0][1],facer[1][3],facer[3][2],facer[2][0] = facer[1][3],facer[3][2],facer[2][0],facer[0][1]
            facer[0][2],facer[2][3],facer[3][1],facer[1][0] = facer[2][3],facer[3][1],facer[1][0],facer[0][2]
            facet[0][3],facet[3][3],facef[0][3],facef[3][3],faced[0][3],faced[3][3],faceb[0][0],faceb[3][0] = faceb[3][0],faceb[0][0],facet[0][3],facet[3][3],facef[0][3],facef[3][3],faced[3][3],faced[0][3]            
            facet[1][3],facet[2][3],facef[1][3],facef[2][3],faced[1][3],faced[2][3],faceb[1][0],faceb[2][0] = faceb[2][0],faceb[1][0],facet[1][3],facet[2][3],facef[1][3],facef[2][3],faced[2][3],faced[1][3]
            facer[1][1],facer[1][2],facer[2][1],facer[2][2] = facer[1][2],facer[2][2],facer[1][1],facer[2][1]
            
        elif letter == 'L':
            facel[0][0],facel[0][3],facel[3][0],facel[3][3] = facel[3][0],facel[0][0],facel[3][3],facel[0][3]
            facel[0][1],facel[1][3],facel[3][2],facel[2][0] = facel[2][0],facel[0][1],facel[1][3],facel[3][2]
            facel[0][2],facel[2][3],facel[3][1],facel[1][0] = facel[1][0],facel[0][2],facel[2][3],facel[3][1]
            facet[0][0],facet[3][0],facef[0][0],facef[3][0],faced[0][0],faced[3][0],faceb[0][3],faceb[3][3] = faceb[3][3],faceb[0][3],facet[0][0],facet[3][0],facef[0][0],facef[3][0],faced[3][0],faced[0][0]            
            facet[1][0],facet[2][0],facef[1][0],facef[2][0],faced[1][0],faced[2][0],faceb[1][3],faceb[2][3] = faceb[2][3],faceb[1][3],facet[1][0],facet[2][0],facef[1][0],facef[2][0],faced[2][0],faced[1][0]
            facel[1][1],facel[1][2],facel[2][1],facel[2][2] = facel[2][1],facel[1][1],facel[2][2],facel[1][2]

        elif letter == "L'":
            facel[0][0],facel[0][3],facel[3][0],facel[3][3] = facel[0][3],facel[3][3],facel[0][0],facel[3][0]
            facel[0][1],facel[1][3],facel[3][2],facel[2][0] = facel[1][3],facel[3][2],facel[2][0],facel[0][1]
            facel[0][2],facel[2][3],facel[3][1],facel[1][0] = facel[2][3],facel[3][1],facel[1][0],facel[0][2]
            facet[0][0],facet[3][0],facef[0][0],facef[3][0],faced[0][0],faced[3][0],faceb[0][3],faceb[3][3] = facef[0][0],facef[3][0],faced[0][0],faced[3][0],faceb[3][3],faceb[0][3],facet[3][0],facet[0][0]            
            facet[1][0],facet[2][0],facef[1][0],facef[2][0],faced[1][0],faced[2][0],faceb[1][3],faceb[2][3] = facef[1][0],facef[2][0],faced[1][0],faced[2][0],faceb[2][3],faceb[1][3],facet[2][0],facet[1][0]
            facel[1][1],facel[1][2],facel[2][1],facel[2][2] = facel[1][2],facel[2][2],facel[1][1],facel[2][1]

        elif letter == 'U':
            facet[0][0],facet[0][3],facet[3][0],facet[3][3] = facet[3][0],facet[0][0],facet[3][3],facet[0][3]
            facet[0][1],facet[1][3],facet[3][2],facet[2][0] = facet[2][0],facet[0][1],facet[1][3],facet[3][2]
            facet[0][2],facet[2][3],facet[3][1],facet[1][0] = facet[1][0],facet[0][2],facet[2][3],facet[3][1]
            facef[0][1],facel[0][1],faceb[0][1],facer[0][1] = facer[0][1],facef[0][1],facel[0][1],faceb[0][1]
            facef[0][2],facel[0][2],faceb[0][2],facer[0][2] = facer[0][2],facef[0][2],facel[0][2],faceb[0][2]
            facef[0][0],facef[0][3],facer[0][0],facer[0][3],faceb[0][0],faceb[0][3],facel[0][0],facel[0][3] = facer[0][0],facer[0][3],faceb[0][0],faceb[0][3],facel[0][0],facel[0][3],facef[0][0],facef[0][3]
            facet[1][1],facet[1][2],facet[2][1],facet[2][2] = facet[2][1],facet[1][1],facet[2][2],facet[1][2]

        elif letter == "U'":
            facet[0][0],facet[0][3],facet[3][0],facet[3][3] = facet[0][3],facet[3][3],facet[0][0],facet[3][0]
            facet[0][1],facet[1][3],facet[3][2],facet[2][0] = facet[1][3],facet[3][2],facet[2][0],facet[0][1]
            facet[0][2],facet[2][3],facet[3][1],facet[1][0] = facet[2][3],facet[3][1],facet[1][0],facet[0][2]
            facef[0][1],facel[0][1],faceb[0][1],facer[0][1] = facel[0][1],faceb[0][1],facer[0][1],facef[0][1]
            facef[0][2],facel[0][2],faceb[0][2],facer[0][2] = facel[0][2],faceb[0][2],facer[0][2],facef[0][2]
            facef[0][0],facef[0][3],facer[0][0],facer[0][3],faceb[0][0],faceb[0][3],facel[0][0],facel[0][3] = facel[0][0],facel[0][3],facef[0][0],facef[0][3],facer[0][0],facer[0][3],faceb[0][0],faceb[0][3]
            facet[1][1],facet[1][2],facet[2][1],facet[2][2] = facet[1][2],facet[2][2],facet[1][1],facet[2][1]

        elif letter == "D":
            faced[0][0],faced[0][3],faced[3][0],faced[3][3] = faced[3][0],faced[0][0],faced[3][3],faced[0][3]
            faced[0][1],faced[1][3],faced[3][2],faced[2][0] = faced[2][0],faced[0][1],faced[1][3],faced[3][2]
            faced[0][2],faced[2][3],faced[3][1],faced[1][0] = faced[1][0],faced[0][2],faced[2][3],faced[3][1]
            facef[3][1],facel[3][1],faceb[3][1],facer[3][1] = facel[3][1],faceb[3][1],facer[3][1],facef[3][1]
            facef[3][2],facel[3][2],faceb[3][2],facer[3][2] = facel[3][2],faceb[3][2],facer[3][2],facef[3][2]
            facef[3][0],facef[3][3],facer[3][0],facer[3][3],faceb[3][0],faceb[3][3],facel[3][0],facel[3][3] = facel[3][0],facel[3][3],facef[3][0],facef[3][3],facer[3][0],facer[3][3],faceb[3][0],faceb[3][3]
            faced[1][1],faced[1][2],faced[2][1],faced[2][2] = faced[2][1],faced[1][1],faced[2][2],faced[1][2]

        elif letter == "D'":
            faced[0][0],faced[0][3],faced[3][0],faced[3][3] = faced[0][3],faced[3][3],faced[0][0],faced[3][0]
            faced[0][1],faced[1][3],faced[3][2],faced[2][0] = faced[1][3],faced[3][2],faced[2][0],faced[0][1]
            faced[0][2],faced[2][3],faced[3][1],faced[1][0] = faced[2][3],faced[3][1],faced[1][0],faced[0][2]
            facef[3][1],facel[3][1],faceb[3][1],facer[3][1] = facer[3][1],facef[3][1],facel[3][1],faceb[3][1]
            facef[3][2],facel[3][2],faceb[3][2],facer[3][2] = facer[3][2],facef[3][2],facel[3][2],faceb[3][2]
            facef[3][0],facef[3][3],facer[3][0],facer[3][3],faceb[3][0],faceb[3][3],facel[3][0],facel[3][3] = facer[3][0],facer[3][3],faceb[3][0],faceb[3][3],facel[3][0],facel[3][3],facef[3][0],facef[3][3]
            faced[1][1],faced[1][2],faced[2][1],faced[2][2] = faced[1][2],faced[2][2],faced[1][1],faced[2][1]

        elif letter == 'F':
            facef[0][0],facef[0][3],facef[3][0],facef[3][3] = facef[3][0],facef[0][0],facef[3][3],facef[0][3]
            facef[0][1],facef[1][3],facef[3][2],facef[2][0] = facef[2][0],facef[0][1],facef[1][3],facef[3][2]
            facef[0][2],facef[2][3],facef[3][1],facef[1][0] = facef[1][0],facef[0][2],facef[2][3],facef[3][1]
            facet[3][1],facer[1][0],faced[0][2],facel[2][3] = facel[2][3],facet[3][1],facer[1][0],faced[0][2]
            facet[3][2],facer[2][0],faced[0][1],facel[1][3] = facel[1][3],facet[3][2],facer[2][0],faced[0][1]
            facet[3][0],facet[3][3],facer[0][0],facer[3][0],faced[0][0],faced[0][3],facel[0][3],facel[3][3] = facel[3][3],facel[0][3],facet[3][0],facet[3][3],facer[3][0],facer[0][0],faced[0][0],faced[0][3]
            facef[1][1],facef[1][2],facef[2][1],facef[2][2] = facef[2][1],facef[1][1],facef[2][2],facef[1][2]
        elif letter == "F'":
            facef[0][0],facef[0][3],facef[3][0],facef[3][3] = facef[0][3],facef[3][3],facef[0][0],facef[3][0]
            facef[0][1],facef[1][3],facef[3][2],facef[2][0] = facef[1][3],facef[3][2],facef[2][0],facef[0][1]
            facef[0][2],facef[2][3],facef[3][1],facef[1][0] = facef[2][3],facef[3][1],facef[1][0],facef[0][2]
            facet[3][1],facer[1][0],faced[0][2],facel[2][3] = facer[1][0],faced[0][2],facel[2][3],facet[3][1]
            facet[3][2],facer[2][0],faced[0][1],facel[1][3] = facer[2][0],faced[0][1],facel[1][3],facet[3][2]
            facet[3][0],facet[3][3],facer[0][0],facer[3][0],faced[0][0],faced[0][3],facel[0][3],facel[3][3] = facer[0][0],facer[3][0],faced[0][3],faced[0][0],facel[0][3],facel[3][3],facet[3][3],facet[3][0]
            facef[1][1],facef[1][2],facef[2][1],facef[2][2] = facef[1][2],facef[2][2],facef[1][1],facef[2][1]

        elif letter == 'B':
            faceb[0][0],faceb[0][3],faceb[3][0],faceb[3][3] = faceb[3][0],faceb[0][0],faceb[3][3],faceb[0][3]
            faceb[0][1],faceb[1][3],faceb[3][2],faceb[2][0] = faceb[2][0],faceb[0][1],faceb[1][3],faceb[3][2]
            faceb[0][2],faceb[2][3],faceb[3][1],faceb[1][0] = faceb[1][0],faceb[0][2],faceb[2][3],faceb[3][1]
            facet[0][1],facer[1][3],faced[3][2],facel[2][0] = facer[1][3],faced[3][2],facel[2][0],facet[0][1]
            facet[0][2],facer[2][3],faced[3][1],facel[1][0] = facer[2][3],faced[3][1],facel[1][0],facet[0][2]
            facet[0][0],facet[0][3],facer[0][3],facer[3][3],faced[3][0],faced[3][3],facel[0][0],facel[3][0] = facer[0][3],facer[3][3],faced[3][3],faced[3][0],facel[0][0],facel[3][0],facet[0][3],facet[0][0]
            faceb[1][1],faceb[1][2],faceb[2][1],faceb[2][2] = faceb[2][1],faceb[1][1],faceb[2][2],faceb[1][2]

        elif letter == "B'":
            faceb[0][0],faceb[0][3],faceb[3][0],faceb[3][3] = faceb[0][3],faceb[3][3],faceb[0][0],faceb[3][0]
            faceb[0][1],faceb[1][3],faceb[3][2],faceb[2][0] = faceb[1][3],faceb[3][2],faceb[2][0],faceb[0][1]
            faceb[0][2],faceb[2][3],faceb[3][1],faceb[1][0] = faceb[2][3],faceb[3][1],faceb[1][0],faceb[0][2]
            facet[0][1],facer[1][3],faced[3][2],facel[2][0] = facel[2][0],facet[0][1],facer[1][3],faced[3][2]
            facet[0][2],facer[2][3],faced[3][1],facel[1][0] = facel[1][0],facet[0][2],facer[2][3],faced[3][1]
            facet[0][0],facet[0][3],facer[0][3],facer[3][3],faced[3][0],faced[3][3],facel[0][0],facel[3][0] = facel[3][0],facel[0][0],facet[0][0],facet[0][3],facer[3][3],facer[0][3],faced[3][0],faced[3][3]
            faceb[1][1],faceb[1][2],faceb[2][1],faceb[2][2] = faceb[1][2],faceb[2][2],faceb[1][1],faceb[2][1]

        elif letter == 'r':
            facet[0][2],facet[1][2],facet[2][2],facet[3][2],facef[0][2],facef[1][2],facef[2][2],facef[3][2],faced[0][2],faced[1][2],faced[2][2],faced[3][2],faceb[0][1],faceb[1][1],faceb[2][1],faceb[3][1] = facef[0][2],facef[1][2],facef[2][2],facef[3][2],faced[0][2],faced[1][2],faced[2][2],faced[3][2],faceb[3][1],faceb[2][1],faceb[1][1],faceb[0][1],facet[3][2],facet[2][2],facet[1][2],facet[0][2]
        elif letter == "r'":
            facet[0][2],facet[1][2],facet[2][2],facet[3][2],facef[0][2],facef[1][2],facef[2][2],facef[3][2],faced[0][2],faced[1][2],faced[2][2],faced[3][2],faceb[0][1],faceb[1][1],faceb[2][1],faceb[3][1] = faceb[3][1],faceb[2][1],faceb[1][1],faceb[0][1],facet[0][2],facet[1][2],facet[2][2],facet[3][2],facef[0][2],facef[1][2],facef[2][2],facef[3][2],faced[3][2],faced[2][2],faced[1][2],faced[0][2]
        elif letter == "l'":
            facet[0][1],facet[1][1],facet[2][1],facet[3][1],facef[0][1],facef[1][1],facef[2][1],facef[3][1],faced[0][1],faced[1][1],faced[2][1],faced[3][1],faceb[0][2],faceb[1][2],faceb[2][2],faceb[3][2] = facef[0][1],facef[1][1],facef[2][1],facef[3][1],faced[0][1],faced[1][1],faced[2][1],faced[3][1],faceb[3][2],faceb[2][2],faceb[1][2],faceb[0][2],facet[3][1],facet[2][1],facet[1][1],facet[0][1]
        elif letter == "l":
            facet[0][1],facet[1][1],facet[2][1],facet[3][1],facef[0][1],facef[1][1],facef[2][1],facef[3][1],faced[0][1],faced[1][1],faced[2][1],faced[3][1],faceb[0][2],faceb[1][2],faceb[2][2],faceb[3][2] = faceb[3][2],faceb[2][2],faceb[1][2],faceb[0][2],facet[0][1],facet[1][1],facet[2][1],facet[3][1],facef[0][1],facef[1][1],facef[2][1],facef[3][1],faced[3][1],faced[2][1],faced[1][1],faced[0][1]
        elif letter == 'u':
            facef[1][0],facef[1][1],facef[1][2],facef[1][3],facer[1][0],facer[1][1],facer[1][2],facer[1][3],faceb[1][0],faceb[1][1],faceb[1][2],faceb[1][3],facel[1][0],facel[1][1],facel[1][2],facel[1][3] = facer[1][0],facer[1][1],facer[1][2],facer[1][3],faceb[1][0],faceb[1][1],faceb[1][2],faceb[1][3],facel[1][0],facel[1][1],facel[1][2],facel[1][3],facef[1][0],facef[1][1],facef[1][2],facef[1][3]
        
        elif letter == "f'":
            facet[2][0],facet[2][1],facet[2][2],facet[2][3],facer[0][1],facer[1][1],facer[2][1],facer[3][1],faced[1][0],faced[1][1],faced[1][2],faced[1][3],facel[0][2],facel[1][2],facel[2][2],facel[3][2] = facer[0][1],facer[1][1],facer[2][1],facer[3][1],faced[1][3],faced[1][2],faced[1][1],faced[1][0],facel[0][2],facel[1][2],facel[2][2],facel[3][2],facet[2][3],facet[2][2],facet[2][1],facet[2][0]
        elif letter == 'f':
            facet[2][0],facet[2][1],facet[2][2],facet[2][3],facer[0][1],facer[1][1],facer[2][1],facer[3][1],faced[1][0],faced[1][1],faced[1][2],faced[1][3],facel[0][2],facel[1][2],facel[2][2],facel[3][2] = facel[3][2],facel[2][2],facel[1][2],facel[0][2],facet[2][0],facet[2][1],facet[2][2],facet[2][3],facer[3][1],facer[2][1],facer[1][1],facer[0][1],faced[1][0],faced[1][1],faced[1][2],faced[1][3]

        elif letter == "b":
            facet[1][0],facet[1][1],facet[1][2],facet[1][3],facer[0][2],facer[1][2],facer[2][2],facer[3][2],faced[2][0],faced[2][1],faced[2][2],faced[2][3],facel[0][1],facel[1][1],facel[2][1],facel[3][1] = facer[0][2],facer[1][2],facer[2][2],facer[3][2],faced[2][3],faced[2][2],faced[2][1],faced[2][0],facel[0][1],facel[1][1],facel[2][1],facel[3][1],facet[1][3],facet[1][2],facet[1][1],facet[1][0]
        elif letter == "b'":
            facet[1][0],facet[1][1],facet[1][2],facet[1][3],facer[0][2],facer[1][2],facer[2][2],facer[3][2],faced[2][0],faced[2][1],faced[2][2],faced[2][3],facel[0][1],facel[1][1],facel[2][1],facel[3][1] = facel[3][1],facel[2][1],facel[1][1],facel[0][1],facet[1][0],facet[1][1],facet[1][2],facet[1][3],facer[3][2],facer[2][2],facer[1][2],facer[0][2],faced[2][0],faced[2][1],faced[2][2],faced[2][3]


        elif letter == "u'":
            facef[1][0],facef[1][1],facef[1][2],facef[1][3],facer[1][0],facer[1][1],facer[1][2],facer[1][3],faceb[1][0],faceb[1][1],faceb[1][2],faceb[1][3],facel[1][0],facel[1][1],facel[1][2],facel[1][3] = facel[1][0],facel[1][1],facel[1][2],facel[1][3],facef[1][0],facef[1][1],facef[1][2],facef[1][3],facer[1][0],facer[1][1],facer[1][2],facer[1][3],faceb[1][0],faceb[1][1],faceb[1][2],faceb[1][3]
        
        elif letter == "d'":
            facef[2][0],facef[2][1],facef[2][2],facef[2][3],facer[2][0],facer[2][1],facer[2][2],facer[2][3],faceb[2][0],faceb[2][1],faceb[2][2],faceb[2][3],facel[2][0],facel[2][1],facel[2][2],facel[2][3] = facer[2][0],facer[2][1],facer[2][2],facer[2][3],faceb[2][0],faceb[2][1],faceb[2][2],faceb[2][3],facel[2][0],facel[2][1],facel[2][2],facel[2][3],facef[2][0],facef[2][1],facef[2][2],facef[2][3]
        
        elif letter == "d":
            facef[2][0],facef[2][1],facef[2][2],facef[2][3],facer[2][0],facer[2][1],facer[2][2],facer[2][3],faceb[2][0],faceb[2][1],faceb[2][2],faceb[2][3],facel[2][0],facel[2][1],facel[2][2],facel[2][3] = facel[2][0],facel[2][1],facel[2][2],facel[2][3],facef[2][0],facef[2][1],facef[2][2],facef[2][3],facer[2][0],facer[2][1],facer[2][2],facer[2][3],faceb[2][0],faceb[2][1],faceb[2][2],faceb[2][3]

        elif letter == 'x':
            facet,facef,faced,faceb = facef,faced,faceb,facet
            for i in range(4):
                faceb[i] = faceb[i][::-1]
                faced[i] = faced[i][::-1]
            faceb[0],faceb[1],faceb[2],faceb[3] = faceb[3],faceb[2],faceb[1],faceb[0]
            faced[0],faced[1],faced[2],faced[3] = faced[3],faced[2],faced[1],faced[0]
            facel[1][1],facel[1][2],facel[2][1],facel[2][2] = facel[1][2],facel[2][2],facel[1][1],facel[2][1]
            facel[0][0],facel[0][3],facel[3][0],facel[3][3] = facel[0][3],facel[3][3],facel[0][0],facel[3][0]
            facel[0][1],facel[1][3],facel[3][2],facel[2][0] = facel[1][3],facel[3][2],facel[2][0],facel[0][1]
            facel[0][2],facel[2][3],facel[3][1],facel[1][0] = facel[2][3],facel[3][1],facel[1][0],facel[0][2]
            facer[0][0],facer[0][3],facer[3][0],facer[3][3] = facer[3][0],facer[0][0],facer[3][3],facer[0][3]
            facer[0][1],facer[1][3],facer[3][2],facer[2][0] = facer[2][0],facer[0][1],facer[1][3],facer[3][2]
            facer[0][2],facer[2][3],facer[3][1],facer[1][0] = facer[1][0],facer[0][2],facer[2][3],facer[3][1]
            facer[1][1],facer[1][2],facer[2][1],facer[2][2] = facer[2][1],facer[1][1],facer[2][2],facer[1][2]

        elif letter == "x'":
            facet,facef,faced,faceb = faceb,facet,facef,faced
            for i in range(4):
                faceb[i] = faceb[i][::-1]
                facet[i] = facet[i][::-1]
            faceb[0],faceb[1],faceb[2],faceb[3] = faceb[3],faceb[2],faceb[1],faceb[0]
            facet[0],facet[1],facet[2],facet[3] = facet[3],facet[2],facet[1],facet[0]
            facel[0][0],facel[0][3],facel[3][0],facel[3][3] = facel[3][0],facel[0][0],facel[3][3],facel[0][3]
            facel[0][1],facel[1][3],facel[3][2],facel[2][0] = facel[2][0],facel[0][1],facel[1][3],facel[3][2]
            facel[0][2],facel[2][3],facel[3][1],facel[1][0] = facel[1][0],facel[0][2],facel[2][3],facel[3][1]
            facel[1][1],facel[1][2],facel[2][1],facel[2][2] = facel[2][1],facel[1][1],facel[2][2],facel[1][2]
            facer[0][0],facer[0][3],facer[3][0],facer[3][3] = facer[0][3],facer[3][3],facer[0][0],facer[3][0]
            facer[0][1],facer[1][3],facer[3][2],facer[2][0] = facer[1][3],facer[3][2],facer[2][0],facer[0][1]
            facer[0][2],facer[2][3],facer[3][1],facer[1][0] = facer[2][3],facer[3][1],facer[1][0],facer[0][2]
            facer[1][1],facer[1][2],facer[2][1],facer[2][2] = facer[1][2],facer[2][2],facer[1][1],facer[2][1]

        elif letter == 'y':
            facef,facel,faceb,facer = facer,facef,facel,faceb
            facet[0][0],facet[0][3],facet[3][0],facet[3][3] = facet[3][0],facet[0][0],facet[3][3],facet[0][3]
            facet[0][1],facet[1][3],facet[3][2],facet[2][0] = facet[2][0],facet[0][1],facet[1][3],facet[3][2]
            facet[0][2],facet[2][3],facet[3][1],facet[1][0] = facet[1][0],facet[0][2],facet[2][3],facet[3][1]
            facet[1][1],facet[1][2],facet[2][1],facet[2][2] = facet[2][1],facet[1][1],facet[2][2],facet[1][2]
            faced[0][0],faced[0][3],faced[3][0],faced[3][3] = faced[0][3],faced[3][3],faced[0][0],faced[3][0]
            faced[0][1],faced[1][3],faced[3][2],faced[2][0] = faced[1][3],faced[3][2],faced[2][0],faced[0][1]
            faced[0][2],faced[2][3],faced[3][1],faced[1][0] = faced[2][3],faced[3][1],faced[1][0],faced[0][2]
            faced[1][1],faced[1][2],faced[2][1],faced[2][2] = faced[1][2],faced[2][2],faced[1][1],faced[2][1]
        
        elif letter == "y'":
            facef,facel,faceb,facer = facel,faceb,facer,facef
            facet[0][0],facet[0][3],facet[3][0],facet[3][3] = facet[0][3],facet[3][3],facet[0][0],facet[3][0]
            facet[0][1],facet[1][3],facet[3][2],facet[2][0] = facet[1][3],facet[3][2],facet[2][0],facet[0][1]
            facet[0][2],facet[2][3],facet[3][1],facet[1][0] = facet[2][3],facet[3][1],facet[1][0],facet[0][2]
            facet[1][1],facet[1][2],facet[2][1],facet[2][2] = facet[1][2],facet[2][2],facet[1][1],facet[2][1]
            faced[0][0],faced[0][3],faced[3][0],faced[3][3] = faced[3][0],faced[0][0],faced[3][3],faced[0][3]
            faced[0][1],faced[1][3],faced[3][2],faced[2][0] = faced[2][0],faced[0][1],faced[1][3],faced[3][2]
            faced[0][2],faced[2][3],faced[3][1],faced[1][0] = faced[1][0],faced[0][2],faced[2][3],faced[3][1]
            faced[1][1],faced[1][2],faced[2][1],faced[2][2] = faced[2][1],faced[1][1],faced[2][2],faced[1][2]
    def find(letter):
        if letter == 'A':
            return [facet[0][2],faceb[0][1]]
        if letter == 'B':
            return [facet[2][3],facer[0][1]]
        if letter == 'C':
            return [facet[3][1],facef[0][1]]
        if letter == 'D':
            return [facet[1][0],facel[0][1]]
        if letter == 'E':
            return [facel[0][2],facet[2][0]]
        if letter == 'F':
            return [facel[2][3],facef[2][0]]
        if letter == 'G':
            return [facel[3][1],faced[2][0]]
        if letter == 'H':
            return [facel[1][0],faceb[1][3]]
        if letter == 'I':
            return [facef[0][2],facet[3][2]]
        if letter == 'J':
            return [facef[2][3],facer[2][0]]
        if letter == 'K':
            return [facef[3][1],faced[0][1]]
        if letter == 'L':
            return [facef[1][0],facel[1][3]]
        if letter == 'M':
            return [facer[0][2],facet[1][3]]
        if letter == 'N':
            return [facer[2][3],faceb[2][0]]
        if letter == 'O':
            return [facer[3][1],faced[1][3]]
        if letter == 'P':
            return [facer[1][0],facef[1][3]]
        if letter == 'Q':
            return [faceb[0][2],facet[0][1]]
        if letter == 'R':
            return [faceb[2][3],facel[2][0]]
        if letter == 'S':
            return [faceb[3][1],faced[3][2]]
        if letter == 'T':
            return [faceb[1][0],facer[1][3]]
        if letter == 'U':
            return [faced[0][2],facef[3][2]]
        if letter == 'V':
            return [faced[2][3],facer[3][2]]
        if letter == 'W':
            return [faced[3][1],faceb[3][2]]
        if letter == 'X':
            return [faced[1][0],facel[3][2]]
        return [0,0]

    def cefind(letter):
        if letter == 'A':
            return [facet[1][1]]
        if letter == 'B':
            return [facet[1][2]]
        if letter == 'C':
            return [facet[2][2]]
        if letter == 'D':
            print('lollllll')
            return [facet[2][1]]
        if letter == 'E':
            return [facel[1][1]]
        if letter == 'F':
            return [facel[1][2]]
        if letter == 'G':
            return [facel[2][2]]
        if letter == 'H':
            return [facel[2][1]]
        if letter == 'I':
            return [facef[1][1]]
        if letter == 'J':
            return [facef[1][2]]
        if letter == 'K':
            return [facef[2][2]]
        if letter == 'L':
            return [facef[2][1]]
        if letter == 'M':
            return [facer[1][1]]
        if letter == 'N':
            return [facer[1][2]]
        if letter == 'O':
            return [facer[2][2]]
        if letter == 'P':
            return [facer[2][1]]
        if letter == 'Q':
            return [faceb[1][1]]
        if letter == 'R':
            return [faceb[1][2]]
        if letter == 'S':
            return [faceb[2][2]]
        if letter == 'T':
            return [faceb[2][1]]
        if letter == 'U':
            return [faced[1][1]]
        if letter == 'V':
            return [faced[1][2]]
        if letter == 'W':
            return [faced[2][2]]
        if letter == 'X':
            return [faced[2][1]]
        return 0
    def cesolved():
        s = 0
        cso = []
        for i in mappings_edge:
            if i != 'A':
                cso.append(i)
        for i in cso:
            if cefind(i) == mappings_centre[i]:
                s+=1
        return s

    def cenewcycle():
        print("FUNC ",centres)
        edgelist = []
        elist = []
        for i in mappings_centre:
            if i not in ['A']:
                edgelist.append(i)
        print("ed ",edgelist)
        edgelist1 = edgelist.copy()
        for i in edgelist1:
            if i in centres:
                if i in edgelist:
                    edgelist.remove(i)
        edgelist1 = edgelist.copy()
        print("edgelist",edgelist)
        print("edgelist1",edgelist1)
        print("elist",elist)
        for i in edgelist1:
            t = cefind(i)
            if t == mappings_centre[i]:
                edgelist.remove(i)
        print("Edgelist",edgelist)
        print("Edgelist1",edgelist1)
        print("Elist",elist)
        if edgelist == []:
            return 0
        else:
            for i in edgelist:
                t = cefind(i)
                elist.append(t)
            print("edgelisT",edgelist)
            print("edgelisT1",edgelist1)
            print("elisT",elist)
            return edgelist[0]
    def solved():
        s = 0
        edgelist = []
        for i in mappings_edge:
            if i != 'U':
                edgelist.append(i)
        for i in edgelist:
            if find(i) == mappings_edge[i]:
                s += 1
        print("solved ",s)
        print("cycle",ecycles)
        return s

    def newcycle():
        print("FUNC ",edges)
        edgelist = []
        elist = []
        for i in mappings_edge:
            if i not in ['K','U']:
                edgelist.append(i)
        print("ed ",edgelist)
        edgelist1 = edgelist.copy()
        for i in edgelist1:
            if i in edges:
                print(i)
                if i in edgelist:
                    edgelist.remove(i)
        edgelist1 = edgelist.copy()
        print("edgelist",edgelist)
        print("edgelist1",edgelist1)
        print("elist",elist)
        for i in edgelist1:
            t = find(i)
            if t == mappings_edge[i]:
                edgelist.remove(i)
        print("Edgelist",edgelist)
        print("Edgelist1",edgelist1)
        print("Elist",elist)
        if edgelist == []:
            return 0
        else:
            for i in edgelist:
                t = find(i)
                elist.append(t)
            print("edgelisT",edgelist)
            print("edgelisT1",edgelist1)
            print("elisT",elist)
            return edgelist[0]

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
            return [facet[0][0],facel[0][0],faceb[0][3]]
        if letter == 'B':
            return [facet[0][3],facer[0][3],faceb[0][0]]
        if letter == 'C':
            return [facet[3][3],facer[0][0],facef[0][3]]
        if letter == 'D':
            return [facet[3][0],facel[0][3],facef[0][0]]
        if letter == 'E':
            return [facel[0][0],facet[0][0],faceb[0][3]]
        if letter == 'F':
            return [facel[0][3],facet[3][0],facef[0][0]]
        if letter == 'G':
            return [facel[3][3],faced[0][0],facef[3][0]]
        if letter == 'H':
            return [facel[3][0],faced[3][0],faceb[3][3]]
        if letter == 'I':
            return [facef[0][0],facet[3][0],facel[0][3]]
        if letter == 'J':
            return [facef[0][3],facet[3][3],facer[0][0]]
        if letter == 'K':
            return [facef[3][3],faced[0][3],facer[3][0]]
        if letter == 'L':
            return [facef[3][0],faced[0][0],facel[3][3]]
        if letter == 'M':
            return [facer[0][0],facet[3][3],facef[0][3]]
        if letter == 'N':
            return [facer[0][3],facet[0][3],faceb[0][0]]
        if letter == 'O':
            return [facer[3][3],faced[3][3],faceb[3][0]]
        if letter == 'P':
            return [facer[3][0],faced[0][3],facef[3][3]]
        if letter == 'Q':
            return [faceb[0][0],facet[0][3],facer[0][3]]
        if letter == 'R':
            return [faceb[0][3],facet[0][0],facel[0][0]]
        if letter == 'S':
            return [faceb[3][3],faced[3][0],facel[3][0]]
        if letter == 'T':
            return [faceb[3][0],faced[3][3],facer[3][3]]
        if letter == 'U':
            return [faced[0][0],facel[3][3],facef[3][0]]
        if letter == 'V':
            return [faced[0][3],facer[3][0],facef[3][3]]
        if letter == 'W':
            return [faced[3][3],facer[3][3],faceb[3][0]]
        if letter == 'X':
            return [faced[3][0],facel[3][0],faceb[3][3]]
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
        print("SOLVED ",edgelist)
        for i in edgelist:
            if findc(i) == d1[i] or findc(i) == d2[i]:
                s += 1
        print("solved ",s)
        print("cycle",ccycles)
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
        print("FUNC ",corners)
        edgelist = []
        elist = []
        for i in mappings_corner:
            if i not in ['E','A','R']:
                edgelist.append(i)
        print("ed ",edgelist)
        edgelist1 = edgelist.copy()
        for i in edgelist1:
            if i in corners:
                print(i)
                t = samec(i)
                if i in edgelist:
                    edgelist.remove(i)
                if t[0] in edgelist:
                    edgelist.remove(t[0])
                if t[1] in edgelist:
                    edgelist.remove(t[1])
        edgelist1 = edgelist.copy()
        print("edgelist",edgelist)
        print("edgelist1",edgelist1)
        print("elist",elist)
        for i in edgelist1:
            t = findc(i)
            if t == d1[i] or t == d2[i]:
                edgelist.remove(i)
        print("Edgelist",edgelist)
        print("Edgelist1",edgelist1)
        print("Elist",elist)
        if edgelist == []:
            return 0
        else:
            for i in edgelist:
                t = findc(i)
                elist.append(t)
            print("edgelisT",edgelist)
            print("edgelisT1",edgelist1)
            print("elisT",elist)
            return edgelist[0]

    def edgealg(letter):
        if letter == 'A':
            return ""
        if letter == 'B':
            return "R U R' U'"
        if letter == 'D':
            return "L' U' L U"
        if letter == 'E':
            return "B L' B'"
        if letter == 'F':
            return "B L2 B'"
        if letter == 'G':
            return "B L B'"
        if letter == 'H':
            return "L B L' B'"
        if letter == 'J':
            return "U R U'"
        if letter == 'L':
            return "U' L' U"
        if letter == 'M':
            return "B' R B"
        if letter == 'N':
            return "R' B' R B"
        if letter == 'O':
            return "B' R' B"
        if letter == 'P':
            return "B' R2 B"
        if letter == 'Q':
            return "U B' R U' B"
        if letter == 'R':
            return "U' L U"
        if letter == 'T':
            return "U R' U'"
        if letter == 'V':
            return "U R2 U'"
        if letter == 'X':
            return "U' L2 U"
        return [0,0]
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
    def reversedgealg(letter):
        if letter == 'A':
            return ""
        if letter == 'B':
            return "U R U' R'"
        if letter == 'D':
            return "U' L' U L"
        if letter == 'E':
            return "B L B'"
        if letter == 'F':
            return "B L2 B'"
        if letter == 'G':
            return "B L' B'"
        if letter == 'H':
            return "B L B' L'"
        if letter == 'J':
            return "U R' U'"
        if letter == 'L':
            return "U' L U"
        if letter == 'M':
            return "B' R' B"
        if letter == 'N':
            return "B' R' B R"
        if letter == 'O':
            return "B' R B"
        if letter == 'P':
            return "B' R2 B"
        if letter == 'Q':
            return "B' U R' B U'"
        if letter == 'R':
            return "U' L' U"
        if letter == 'T':
            return "U R U'"
        if letter == 'V':
            return "U R2 U'"
        if letter == 'X':
            return "U' L2 U"
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

    def centrealg(letter):
        if letter == 'E':
            return "r u r'"
        if letter == 'F':
            return "y' u r' u' r"
        if letter == 'G':
            return "r' d r"
        if letter == 'H':
            return "y' r d2 r'"
        if letter == 'I':
            return "r u2 r'"
        if letter == 'J':
            return "y' r' u r"
        if letter == 'K':
            return "d' r' d r"
        if letter == 'L':
            return "y' r d r'"
        if letter == 'M':
            return "r u' r'"
        if letter == 'N':
            return "y' r' u2 r"
        if letter == 'O':
            return "r' d' r"
        if letter == 'P':
            return "y' d' r d r'"
        if letter == 'Q':
            return "u r u' r'"
        if letter == 'R':
            return "y' r' u' r"
        if letter == 'S':
            return "r' d2 r"
        if letter == 'T':
            return "y' r d' r'"
    def reversecentrealg(letter):
        if letter == 'E':
            return "r u' r'"
        if letter == 'F':
            return "r' u r u' y"
        if letter == 'G':
            return "r' d' r"
        if letter == 'H':
            return "r d2 r' y"
        if letter == 'I':
            return "r u2 r'"
        if letter == 'J':
            return "r' u' r y"
        if letter == 'K':
            return "r' d' r d"
        if letter == 'L':
            return "r d' r' y"
        if letter == 'M':
            return "r u r'"
        if letter == 'N':
            return "r' u2 r y"
        if letter == 'O':
            return "r' d r"
        if letter == 'P':
            return "r d' r' d y"
        if letter == 'Q':
            return "r u r' u'"
        if letter == 'R':
            return "r' u r y"
        if letter == 'S':
            return "r' d2 r"
        if letter == 'T':
            return "r d r' y"
    centres=[]
    edges = []
    corners = []

    print("SSSSS ",cesolved())
    while True:
        buffer1 = facet[1][1]
        print("BBBBB ",buffer1)
        if buffer1 == 0 or (buffer1 == 'W' and (('B' in centres and 'C' in centres and 'D' in centres) or ('B' in centres and 'C' in centres and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and facet[2][1] == 'W') or (facet[1][2] == 'W' and facet[2][1] == 'W' and facet[2][2] == 'W') or (facet[1][2] == 'W' and facet[2][2] == 'W' and 'D' in centres))):
            cecycles += 1
            let = cenewcycle()
            print("let",let)
            t = cefind(let)
            print("t",t)
            if t == 0:
                break
            print('HFOE ',centre(t[0]))
            #centres.append(centre(t[0]))
            cycle[centre(t[0])] = 1
            buffer1 = t[0]
            if buffer1 == 0:
                break
        while (buffer1 != 'W') or (len(centres) != 23 - cesolved() + cecycles):
            if len(centres) == 23 - cesolved() + cecycles:
                print("lol")
                print("edges ",centres)
                break
            print('edges = ',centres, 'letters = ',buffer1)
            dict = {}
            for i in centres:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 2:
                    cycle[i] = 0
                    if centres[-1] == i:
                        buffer1 = 0
            if buffer1 == 'W':
                if ('B' in centres and 'C' in centres and 'D' in centres) or ('B' in centres and 'C' in centres and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and facet[2][1] == 'W') or (facet[1][2] == 'W' and facet[2][1] == 'W' and facet[2][2] == 'W') or (facet[1][2] == 'W' and facet[2][2] == 'W' and 'D' in centres):
                    buffer1 = 0

            if buffer1 == 0:
                print("fehifehi")
                cecycles += 1
                let = cenewcycle()
                print("let",let)
                t = cefind(let)
                if t == 0:
                    break
                print("t",t,centre(t[0]))
                print('HFOEF ',centre(t[0]))
                centres.append(centre(t[0]))
                cycle[centres[-1]] = 1
                buffer1 = cefind(centres[-1])[0]
                if buffer1 == 0:
                    break
                else:
                    continue
            if centre(buffer1) != 'A':
                centres.append(centre(buffer1))
            dict = {}
            for i in centres:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 2:
                    cycle[i] = 0
                    if centres[-1] == i:
                        buffer1 = 0
            if buffer1 != 0:
                print('CENTERRRRR ',centres[-1])
                t = cefind(centres[-1])
                print("ttttt ",t)
                buffer1 = t[0]
            if buffer1 == 'W' or buffer1 == 0 and ('B' in centres and 'C' in centres and 'D' in centres) or ('B' in centres and 'C' in centres and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and facet[2][1] == 'W') or ('B' in centres and facet[2][2] == 'W' and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and 'D' in centres) or (facet[1][2] == 'W' and 'C' in centres and facet[2][1] == 'W') or (facet[1][2] == 'W' and facet[2][1] == 'W' and facet[2][2] == 'W') or (facet[1][2] == 'W' and facet[2][2] == 'W' and 'D' in centres):

                dict = {}
                for i in centres:
                    if i in dict:
                        dict[i] += 1
                    else:
                        dict[i] = 1
                for i in dict:
                    if dict[i] == 2:
                        cycle[i] = 0
                        if centres[-1] == i:
                            buffer1 = 0
                if buffer1 == 0:
                    cecycles += 1
                    print('aiya')
                    let = cenewcycle()
                    print("let",let)
                    t = cefind(let)
                    if t == 0:
                        break
                    print("t",t)
                    print('HFOEFHW ',centre(t[0]))
                    centres.append(centre(t[0]))
                    buffer1 = cefind(centres[-1])[0]
                    cycle[centres[-1]] = 1
                    if buffer1 == 0:
                        break
                    else:
                        continue
        break

    for i in range(1,len(centres),2):
            if centres[i] == 'B':
                centres[i] = 'D'
                continue
            elif centres[i] == 'D':
                centres[i] = 'B'
                continue

    print("FINAL ",centres,len(centres))

    while True:
        buffer2 = facef[3][2]
        buffer1 = faced[0][2]
        if buffer1 == 'Y' and buffer2 == 'G':
            ecycles += 1
            let = newcycle()
            #print("let",let)
            t = find(let)
            #print("t",t)
            buffer1,buffer2 = t[0],t[1]
            if buffer1 == 0:
                break
        while  (buffer1 != 'Y' or buffer2 != 'G') or (len(edges) != 23 - solved() + ecycles):
            if len(edges) == 23 - solved() + ecycles:
                #print("lol")
                #print("edges ",edges)
                break
            print('edges = ',edges, 'letters = ',buffer1,buffer2)
            dict = {}
            for i in edges:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 2:
                    if edge(buffer1,buffer2) == i:
                        buffer1 = 0
            if (buffer1 == 'Y' and buffer2 == 'G'):
                buffer1 = 0
            if buffer1 == 0:
                #print("fehifehi")
                ecycles += 1
                let = newcycle()
                #print("let",let)
                t = find(let)
                #print("t",t)
                buffer1,buffer2 = t[0],t[1]
                if buffer1 == 0:
                    break
                else:
                    continue
            if edge(buffer1,buffer2) != 'U': 
                edges.append(edge(buffer1,buffer2))
            dict = {}
            for i in edges:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            for i in dict:
                if dict[i] == 2:
                    if edge(buffer1,buffer2) == i:
                        buffer1 = 0
            if buffer1 != 0:
                t = find(edge(buffer1,buffer2))
                buffer1,buffer2 = t[0], t[1]
            if (buffer1 == 'Y' and buffer2 == 'G') or buffer1 == 0:
                dict = {}
                for i in edges:
                    if i in dict:
                        dict[i] += 1
                    else:
                        dict[i] = 1
                for i in dict:
                    if dict[i] == 2:
                        if edge(buffer1,buffer2) == i:
                            buffer1 = 0
                if buffer1 == 0:
                    ecycles += 1
                    let = newcycle()
                    #print("let",let)
                    t = find(let)
                    #print("t",t)
                    buffer1,buffer2 = t[0],t[1]
                    if buffer1 == 0:
                        break
                    else:
                        continue
        break

    for i in range(1,len(edges),2):
        if edges[i] == 'I':
            edges[i] = 'S'
            continue
        elif edges[i] == 'S':
            edges[i] = 'I'
            continue
    print("FINAL EDGES ",edges)

    while True:
        buffer1 = facel[0][0]
        buffer2 = facet[0][0]
        buffer3 = faceb[0][3]
        if buffer1 in ['W','B','O'] and buffer2 in ['W','B','O'] and buffer3 in ['W','B','O']:
            ccycles += 1
            let = newccycle()
            print("let",let)
            t = findc(let)
            print("t",t)
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
    print("FINAL CORNERS ",corners)

    string = ""
    for i in centres:
        if i not in ['B','D','U','V','W','X','C']:
            string += centrealg(i) + " U2 " + reversecentrealg(i) + " "
        else:
            if i == 'B':
                string += "Rw' F' U r U' l' U r' U' l F Rw U2 "
            elif i == 'C':
                string += "U2 "
            elif i == 'D':
                string += "Lw F' r U l' U' r' U l U' F Lw' U2 "
            elif i == 'U':
                string += "D Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D' "
            elif i == 'V':
                string += "Lw' U' r2 U' l U r2 U' l' U2 Lw U2 "
            elif i == 'W':
                string += "D' Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D "
            elif i == 'X':
                string += "D2 Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D2 "
    if len(centres) % 2 == 1:
        string += 'U2 '
    for i in edges:
        if i not in ['I','C','W','K','S','A']: 
            string += edgealg(i) + " r2 " + reversedgealg(i) + " "
        else:
            if i == 'I':
                string += "D r U R2 U' r' U R2 U' D' r2 "
            elif i == 'S':
                string += "r2 D U R2 U' r U R2 U' r' D' "
            elif i == 'A':
                string += "r2 "
            elif i == 'C':
                string += "l' U B' R U' B r2 B' U R' B U' l "
            elif i == 'W':
                string += "l U B' R U' B r2 B' U R' B U' l' "
            elif i == 'K':
                string += "l2 U B' R U' B r2 B' U R' B U' l2 "
    if len(edges) % 2 == 1:
        string += "r' U2 r U2 r' U2 x r U2 r U2 r U2 r2 U2 x' r' U2 "
    for i in corners:
        if i != 'V':
            string += corneralg(i) + " R U' R' U' R U R' F' R U R' U' R' F R " + reversecorneralg(i) + " "
        else:
            string += "R U' R' U' R U R' F' R U R' U' R' F R "
    if len(corners) % 2 == 1:
        string += "U2 R U R' U' r2 U2 r2 Uw2 r2 Uw2 U' R U' R' U2 "
    i = 0
    print(string)
    while True:
        if i >= len(string) - 1:
            break
        print(string[i]+string[i+1])
        if string[i] == 'R' and string[i + 1] in ['2',' ']:
            move('R')
            if string[i + 1] == '2':
                move('R')
                i += 1
            i += 2
        elif string[i] == 'R' and string[i + 1] == "'":
            move("R'")
            i += 3
        elif string[i] == 'L' and string[i + 1] in ['2',' ']:
            move('L')
            if string[i + 1] == '2':
                move('L')
                i += 1
            i += 2
        elif string[i] == 'L' and string[i + 1] == "'":
            move("L'")
            i += 3
        elif string[i] == 'U' and string[i + 1] in ['2',' ']:
            move('U')
            if string[i + 1] == '2':
                move('U')
                i += 1
            i += 2
        elif string[i] == 'U' and string[i + 1] == "'":
            move("U'")
            i += 3
        elif string[i] == 'D' and string[i + 1] in ['2',' ']:
            move('D')
            if string[i + 1] == '2':
                move('D')
                i += 1
            i += 2
        elif string[i] == 'D' and string[i + 1] == "'":
            move("D'")
            i += 3
        elif string[i] == 'F' and string[i + 1] in ['2',' ']:
            move('F')
            if string[i + 1] == '2':
                move('F')
                i += 1
            i += 2
        elif string[i] == 'F' and string[i + 1] == "'":
            move("F'")
            i += 3
        elif string[i] == 'B' and string[i + 1] in ['2',' ']:
            move('B')
            if string[i + 1] == '2':
                move('B')
                i += 1
            i += 2
        elif string[i] == 'B' and string[i + 1] == "'":
            move("B'")
            i += 3
        elif string[i] == 'r' and string[i + 1] != "'":
            move('r')
            if string[i + 1] == '2':
                move('r')
                i += 1
            i += 2
        elif string[i] == 'r' and string[i + 1] == "'":
            move("r'")
            i += 3
        elif string[i] == 'l' and string[i + 1] != "'":
            move('l')
            if string[i + 1] == '2':
                move('l')
                i += 1
            i += 2
        elif string[i] == 'l' and string[i + 1] == "'":
            move("l'")
            i += 3
        elif string[i] == 'u' and string[i + 1] != "'":
            move('u')
            if string[i + 1] == '2':
                move('u')
                i += 1
            i += 2
        elif string[i] == 'u' and string[i + 1] == "'":
            move("u'")
            i += 3
        elif string[i] == 'd' and string[i + 1] != "'":
            move('d')
            if string[i + 1] == '2':
                move('d')
                i += 1
            i += 2
        elif string[i] == 'd' and string[i + 1] == "'":
            move("d'")
            i += 3
        elif string[i] == 'x' and string[i + 1] != "'":
            move('x')
            if string[i + 1] == '2':
                move('x')
                i += 1
            i += 2
        elif string[i] == 'x' and string[i + 1] == "'":
            move("x'")
            i += 3
        elif string[i] == 'y' and string[i + 1] != "'":
            move('y')
            if string[i + 1] == '2':
                move('y')
                i += 1
            i += 2
        elif string[i] == 'y' and string[i + 1] == "'":
            move("y'")
            i += 3
        elif string[i] == 'R' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('R')
            move('r')
            if string[i + 2] == '2':
                move('R')
                move('r')
                i += 1
            i += 3
        elif string[i] == 'R' and string[i + 1] == "w" and string[i + 2] == "'":
            move("R'")
            move("r'")
            i += 4
        elif string[i] == 'L' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('L')
            move('l')
            if string[i + 2] == '2':
                move('L')
                move('l')
                i += 1
            i += 3
        elif string[i] == 'L' and string[i + 1] == "w" and string[i + 2] == "'":
            move("L'")
            move("l'")
            i += 4
        elif string[i] == 'U' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('U')
            move('u')
            if string[i + 2] == '2':
                move('U')
                move('u')
                i += 1
            i += 3
        elif string[i] == 'U' and string[i + 1] == "w" and string[i + 2] == "'":
            move("U'")
            move("u'")
            i += 4
        elif string[i] == 'D' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('D')
            move('d')
            if string[i + 2] == '2':
                move('D')
                move('d')
                i += 1
            i += 3
        elif string[i] == 'D' and string[i + 1] == "w" and string[i + 2] == "'":
            move("D'")
            move("d'")
            i += 4
        elif string[i] == 'F' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('F')
            move('f')
            if string[i + 2] == '2':
                move('F')
                move('f')
                i += 1
            i += 3
        elif string[i] == 'F' and string[i + 1] == "w" and string[i + 2] == "'":
            move("F'")
            move("f'")
            i += 4
        elif string[i] == 'B' and string[i + 1] == 'w' and string[i + 2] != "'":
            move('B')
            move('b')
            if string[i + 2] == '2':
                move('B')
                move('b')
                i += 1
            i += 3
        elif string[i] == 'B' and string[i + 1] == "w" and string[i + 2] == "'":
            move("B'")
            move("b'")
            i += 4
        print("FACET ",facet)
        print("FACEF ",facef)
        print("FACED ",faced)
        print("FACER ",facer)
        print("FACEL ",facel)
        print("FACEB ",faceb)
        print()

    if facet == [['W','W','W','W'],['W','W','W','W'],['W','W','W','W'],['W','W','W','W']] and facef == [['G','G','G','G'],['G','G','G','G'],['G','G','G','G'],['G','G','G','G']] and facer == [['R','R','R','R'],['R','R','R','R'],['R','R','R','R'],['R','R','R','R']] and facel == [['O','O','O','O'],['O','O','O','O'],['O','O','O','O'],['O','O','O','O']] and faceb == [['B','B','B','B'],['B','B','B','B'],['B','B','B','B'],['B','B','B','B']] and faced == [['Y','Y','Y','Y'],['Y','Y','Y','Y'],['Y','Y','Y','Y'],['Y','Y','Y','Y']]:
        break
    else:
        print("You made a mistake in entering the colours")
        ans = input("Are you sure you want to get the moves to find out if you have a twisted piece, type no to enter choices if you have entered incorrectly?: ")
        if ans.lower() == 'yes':
            break
        continue

    break

print()
stri = "Note: Hold your 4x4 cube such that center of side facing you is Green and center of side above is White [Sometimes the piece mentioned as solved may not be necessarily solved immediately but would be solved within the next few moves]"
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

for i in centres:
    if i not in ['B','D','U','V','W','X','C']:
        t = mappings_edge[i]
        stri = i+": "+ centrealg(i) + " (U2) " + reversecentrealg(i)+ " [" + decode(t[0]) +" centre solved]"
        for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    else:
        if i == 'B':
            stri = "B: Rw' F' U r U' l' U r' U' l F Rw U2 [Green centre #2 solved]"
        elif i == 'D':
            stri = "D: Lw F' r U l' U' r' U l U' F Lw' U2 [Green centre #4 solved]"
        elif i == 'W':
            stri = "W: D' Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D [Yellow centre #3 solved]"
        elif i == 'C':
            stri = "C: U2 [White centre #3 solved]"
        elif i == 'U':
            stri = "U: D Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D' [Yellow centre #1 solved]"
        elif i == 'V':
            stri = "V: Lw' U' r2 U' l U r2 U' l' U2 Lw U2 [Yellow centre #2 solved]"
        elif i == 'X':
            stri = "X: D2 Lw' U' r2 U' l U r2 U' l' U2 Lw U2 D2 [Yellow centre #4 solved]"
        for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
print()
if len(centres) % 2 == 1:
    stri = "U2 [Parity Algorithm]"
    for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
    print()
for i in edges:
    if i not in ['I','C','W','S','K','A']:
        t = mappings_edge[i]
        stri = i+": "+ edgealg(i) + " (r2) " + reversedgealg(i)+ " [" + decode(t[0])+" - "+decode(t[1])+" edge solved]"
        for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    else:
        if i == 'I':
            stri = "I: D r U R2 U' r' U R2 U' D' r2 [Green - White edge solved]"
        elif i == 'S':
            stri = "S: r2 D U R2 U' r U R2 U' r' D' [Blue - Yellow edge solved]"
        elif i == 'W':
            stri = "W: l U B' R U' B r2 B' U R' B U' l' [Yellow - Blue edge solved]"
        elif i == 'C':
            stri = "C: l' U B' R U' B r2 B' U R' B U' l [White - Green edge solved]"
        elif i == 'K':
            stri = "K: l2 U B' R U' B r2 B' U R' B U' l2 [Green - Yellow edge solved]"
        elif i == 'A':
            stri = "A: r2 [White - Blue edge solved]"
        for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
print()
if len(edges) % 2 == 1:
    stri = "r' U2 r U2 r' U2 x r U2 r U2 r U2 r2 U2 x' r' U2 [Parity Algorithm]"
    for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
    print()
for i in corners:
    stri = i+": "+corneralg(i) + " (R U' R' U' R U R' F' R U R' U' R' F R) "+ reversecorneralg(i)+ " [" + decode(mappings_corner[i][0])+ " - "+decode(mappings_corner[i][1])+" - "+decode(mappings_corner[i][2])+" corner solved]"
    for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
print()
if len(corners) % 2 == 1:
    stri = "U2 R U R' U' (r2 U2 r2 Uw2 r2 Uw2) U' R U' R' U2 [Parity Algorithm]"
    for i in stri:
            time.sleep(0.035)
            print(i, end = '', flush = True)
    print()
    print()
length = 0
for i in string:
    if i in ['M','L','R','U','D','F','B','r','l','d','u']:
        length += 1
stri = "Blindfold centres sequence: "
for i in centres:
    stri += i + " "
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
if len(centres) % 2 == 1:
    stri = "Parity Algorithm [After Centres]: U2"
    for i in stri:
        time.sleep(0.035)
        print(i, end = '', flush = True)
    print()
stri = "Blindfold edges sequence: "
for i in edges:
    stri += i + " "
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
if len(edges) % 2 == 1:
    stri = "Parity Algorithm [After Edges]: r' U2 r U2 r' U2 x r U2 r U2 r U2 r2 U2 x' r' U2"
    for i in stri:
        time.sleep(0.035)
        print(i, end = '', flush = True)
    print()
stri = "Blindfold corners sequence: "
for i in corners:
    stri += i + " "
for i in stri:
    time.sleep(0.035)
    print(i, end = '', flush = True)
print()
if len(corners) % 2 == 1:
    stri = "Parity Algorithm [After Corners]: U2 R U R' U' (r2 U2 r2 Uw2 r2 Uw2) U' R U' R' U2"
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

