import glob
from datetime import datetime
import time
# import os

import cv2
# os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
import numpy as np
import yaml

from webcam import WebcamSource


def record_video(width: int, height: int, fps: int) -> None:
    """
    Create a mp4 video file with `width`x`height` and `fps` frames per second.
    Shows a preview of the recording every 5 frames.

    :param width: width of the video
    :param height: height of the video
    :param fps: frames per second
    :return: None
    """

    source = WebcamSource(width=width, height=height, fps=fps, buffer_size=10)
    video_writer = cv2.VideoWriter(f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.mp4', cv2.VideoWriter_fourcc(*'MP4V'), fps, (width, height))
    t_end = time.time() + 5 * 1
    # while time.time() < t_end:
    # do whatever you do
    for idx, frame in enumerate(source):
        if time.time() >= t_end:
            break
        video_writer.write(frame)
        source.show(frame, only_print=idx % 5 != 0)


def calibration(image_path, every_nth: int = 1, debug: bool = False, chessboard_grid_size=(9, 6)):
    """
    Perform camera calibration on the previously collected images.
    Creates `calibration_matrix.yaml` with the camera intrinsic matrix and the distortion coefficients.

    :param image_path: path to all png images
    :param every_nth: only use every n_th image
    :param debug: preview the matched chess patterns
    :param chessboard_grid_size: size of chess pattern
    :return:
    """

    x, y = chessboard_grid_size

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((y * x, 3), np.float32)
    objp[:, :2] = np.mgrid[0:x, 0:y].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    
    images = glob.glob(f'{image_path}/*.png')[::every_nth]

    found = 0
    for fname in images:
        print("Image")
        img = cv2.imread(fname)  # Capture frame-by-frame
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (x, y), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)  # Certainly, every loop objp is the same, in 3D.
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            found += 1

            if debug:
                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, chessboard_grid_size, corners2, ret)
                cv2.imshow('img', img)
                cv2.waitKey(100)

    print("Number of images used for calibration: ", found)

    # When everything done, release the capture
    cv2.destroyAllWindows()

    # calibration
    rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    print('rms', rms)

    # transform the matrix and distortion coefficients to writable lists
    data = {
        'rms': np.asarray(rms).tolist(),
        'camera_matrix': np.asarray(mtx).tolist(),
        'dist_coeff': np.asarray(dist).tolist()
    }

    # and save it to a file
    with open("calibration_matrix.yaml", "w") as f:
        yaml.dump(data, f)

    print(data)

def record_video_2(width: int, height: int, fps: int, vid_time: int) -> None:
    """
    Create a mp4 video file with `width`x`height` and `fps` frames per second.
    Shows a preview of the recording every 5 frames.

    :param width: width of the video
    :param height: height of the video
    :param fps: frames per second
    :return: None
    """

    source = WebcamSource(width=width, height=height, fps=fps, buffer_size=10)
    file_name = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.mp4'
    video_writer = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc(*'MP4V'), fps, (width, height))
    t_end = time.time() + vid_time
    # while time.time() < t_end:
    # do whatever you do
    for idx, frame in enumerate(source):
        if time.time() >= t_end:
            break
        video_writer.write(frame)
        source.show(frame, only_print=idx % 5 != 0)
    
    return file_name

def calibration_2(video_path, every_nth: int = 1, debug: bool = False, chessboard_grid_size=(9, 6)):
    """
    Perform camera calibration on the previously collected images.
    Creates `calibration_matrix.yaml` with the camera intrinsic matrix and the distortion coefficients.

    :param image_path: path to all png images
    :param every_nth: only use every n_th image
    :param debug: preview the matched chess patterns
    :param chessboard_grid_size: size of chess pattern
    :return:
    """

    print (video_path)
    x, y = chessboard_grid_size

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((y * x, 3), np.float32)
    objp[:, :2] = np.mgrid[0:x, 0:y].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    
    # images = glob.glob(f'{image_path}/*.png')[::every_nth]

    cap = cv2.VideoCapture(video_path)

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
        return

    found = 0    
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            
            # img = cv2.imread(fname)  # Capture frame-by-frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (x, y), None)

            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)  # Certainly, every loop objp is the same, in 3D.
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)

                found += 1

                if debug:
                    # Draw and display the corners
                    img = cv2.drawChessboardCorners(frame, chessboard_grid_size, corners2, ret)
                    cv2.imshow('img', img)
                    cv2.waitKey(100)
        else:
            break

    print("Number of images used for calibration: ", found)

    # When everything done, release the capture
    # cv2.destroyAllWindows()

    print ("start calibration")
    # calibration
    rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    print('rms', rms)

    print ("Transform data")
    # transform the matrix and distortion coefficients to writable lists
    data = {
        'rms': np.asarray(rms).tolist(),
        'camera_matrix': np.asarray(mtx).tolist(),
        'dist_coeff': np.asarray(dist).tolist()
    }

    print ("Save to file")
    # and save it to a file
    with open("calibration_matrix.yaml", "w") as f:
        yaml.dump(data, f)

    print ("End")
    print(data)


if __name__ == '__main__':
    # 1. record video

    # record_video(width=1280, height=720, fps=30)
    # 2. split video into frames e.g. `ffmpeg -i 2021-10-15_10:30:00.mp4 -f image2 frames/video_01-%07d.png` and delete blurry images
    # 3. run calibration on images
    # calibration('./frames', 30, debug=True)

    vid_path = record_video_2(width=1280, height=720, fps=30, vid_time=5)
    # vid_path = '2023-07-26_09:10:54.mp4'
    calibration_2(vid_path, 30, debug=False)
