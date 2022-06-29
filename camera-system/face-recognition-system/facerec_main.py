import face_recognition
import cv2
import numpy as np
import pickle
import os
from time import sleep, time
from organization.employer.employer_main import Employer
from organization.organization_main import Organization
from imutils import paths
 

def createEncodings(path, start, existedData = None):
    # в директории Images хранятся папки со всеми изображениями
    imagePaths = list(paths.list_images('Images'))
    knownEncodings = []
    knownIds = []
    # перебираем все папки с изображениями
    for (i, imagePath) in enumerate(imagePaths, start=start):
        # извлекаем имя человека из названия папки
        id = imagePath.split(os.path.sep)[-2]
        # загружаем изображение и конвертируем его из BGR (OpenCV ordering)
        # в dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #используем библиотеку Face_recognition для обнаружения лиц
        boxes = face_recognition.face_locations(rgb,model='hog')
        # вычисляем эмбеддинги для каждого лица
        encodings = face_recognition.face_encodings(rgb, boxes)
        # loop over the encodings
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownIds.append(id)
    # сохраним эмбеддинги вместе с их именами в формате словаря
    data = {"encodings": knownEncodings, "ids": knownIds}
    if existedData is not None:
        unitedData = {**data, **existedData}
        data = unitedData
    # для сохранения данных в файл используем метод pickle
    f = open(path, "wb")
    f.write(pickle.dumps(data))
    f.close()


class FaceRecognition(object):
    # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
    # other example, but it includes some basic performance tweaks to make things run a lot faster:
    #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
    #   2. Only detect faces in every other frame of video.

    # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
    # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
    # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

    def __init__(self):
        self.main_employer = Employer()
        self.main_organization = Organization()
        path = 'C:\Users\svsergeev\Organization-Control-System\camera-system\face-recognition-system\face_enc'
        if not os.path.exists(path):
            print('File not exist! Creating encodings...')
            try:
                createEncodings(path = path, start = 1)
            except Exception as e:
                print(e)
        else:
            self.data = pickle.loads(open(path, "rb").read())
            self.organization_unit = self.main_organization.get_organization_state()
            if len(self.data) < len(self.organization_unit):
                createEncodings(path = path, start = (len(self.data) + 1), existedData = self.data)

    def connect_to_camera(self, cameraId):
        # Get a reference to webcam (the default one)
        video_capture = cv2.VideoCapture(cameraId)
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_ids = []
        whoIs = ''
        name = None
        process_this_frame = True

        timeout = 10 # [seconds]
        timeout_start = time.time()

        while time.time() < timeout_start + timeout:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            if face_locations == []:
                isOnCam = False
                whoIs = ''
            else:
                if face_ids == []:
                    pass
                else: 
                    whoIs = face_ids[0]
                    isOnCam = True
            # Only process every other frame of video to save time
            if process_this_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                cv2.putText(frame, str(isOnCam) + ' ' + whoIs, (100, 100), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_ids = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.data["encodings"], face_encoding)
                    user_id = "Unknown"
                    
                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(self.data["encodings"], face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        user_id = self.data["ids"][best_match_index]

                    face_ids.append(user_id)

            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), user_id in zip(face_locations, face_ids):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                employer_info = self.main_employer.get_employer_info(user_id)
                name = f'{employer_info["name"]} {employer_info["surname"]}'
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)
            

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if user_id is not None:
                # Если на камере появился человек - делаем скриншот и возвращаем name, camera_img_file
                camera_img_path = "camera-system\Camera Images"
                camera_img_file = f'{camera_img_path}\{name}_{time.ctime()}.jpg'
                cv2.imwrite(camera_img_file, frame)
                sleep(3)
                return user_id, camera_img_file
        
        # Если на камере так никто и не появился - возвращаем user_id = None и camera_img_file = None
        if user_id is None:
            return None, None
                

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()