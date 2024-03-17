"""File for camera calibration"""
import glob
from datetime import datetime
import cv2
import numpy as np


class CameraCalibration:
    """Class for calibration of the camera"""

    def __init__(self, chessboard=(9,6)) -> None:
        # self.resolution = resolution
        self.chess_board_size = chessboard
        self.images = []
        self.criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001,
        )  # termination criteria
        self.calibration_values = {
            "mtx": np.array([]),  # camera matrix
            "dst": np.array([]),  # distortion
            "newmtx": np.array([]),  # new camera matrix
            "roi": np.array([]),  # ROI (region of interest) --- NOT np.array
        }

    def calibrate(self):
        """Calibrate the camera"""

        if not self.images:
            print("No images exist for calibration")
            return

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros(
            (self.chess_board_size[0] * self.chess_board_size[1], 3), np.float32
        )
        objp[:, :2] = np.mgrid[
            0 : self.chess_board_size[0], 0 : self.chess_board_size[1]
        ].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        gray = cv2.cvtColor(self.images[0], cv2.COLOR_BGR2GRAY)
        for fname in self.images:
            gray = cv2.cvtColor(fname, cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(
                gray, (self.chess_board_size), None
            )
            # If found, add object points, image points (after refining them)
            if ret is True:
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1), self.criteria
                )
                imgpoints.append(corners2)

                # Draw and display the corners
                # draw_corners = fname.copy()
                # self.draw_and_display_corners(
                #    image=draw_corners, corners=corners2, ret=ret
                # )

        # =================== Calibration =================== #
        print ("Start calibration")
        (
            ret,
            self.calibration_values["mtx"],
            self.calibration_values["dst"],
            _,
            _,
        ) = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )  # ignore rvecs and tvecs
        print ("End calibration")

        # =================== Undistortion =================== #
        height, width = gray.shape[:2]
        (
            self.calibration_values["newmtx"],
            self.calibration_values["roi"],
        ) = cv2.getOptimalNewCameraMatrix(
            self.calibration_values["mtx"],
            self.calibration_values["dst"],
            (width, height),
            1,
            (width, height),
        )

        print ("End of calibration")
        return self.calibration_values

    def add_pictures(self, images: list) -> None:
        """Add list of pictures for calibration"""
        for image in images:
            self.images.append(image)

    def replace_pictures(self, images: list) -> None:
        """Add list of pictures for calibration"""
        self.images = images

    def draw_and_display_corners(self, image, corners, ret) -> None:
        """Draw and display an image with found chessboard corners with opencv"""
        draw_corners = image.copy()
        cv2.drawChessboardCorners(draw_corners, (self.chess_board_size), corners, ret)
        cv2.imshow("img", draw_corners)
        cv2.waitKey(500)
        cv2.destroyAllWindows()

    def get_image_with_corners(self, image):
        """Return image with drawn corners"""

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (self.chess_board_size), None)
        # If found, add object points, image points (after refining them)
        if ret is True:
            corners2 = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), self.criteria
            )
            draw_corners = image.copy()
            cv2.drawChessboardCorners(
                draw_corners, (self.chess_board_size), corners2, ret
            )
            return draw_corners
        return None

    def get_current_calibration(self):
        """Returns calibration values, if a calibration exists"""
        if (
            self.calibration_values["mtx"].size == 0
            or self.calibration_values["dst"].size == 0
        ):
            return None
        else:
            return self.calibration_values

    def load_calibration(self, file_name) -> None:
        """Load calibration parameters out of a file"""
        data = np.load(file_name)
        self.calibration_values["mtx"] = data["mtx"]
        self.calibration_values["dst"] = data["dst"]
        self.calibration_values["newmtx"] = data["newmtx"]
        self.calibration_values["roi"] = data["roi"]

    def get_saved_calibrations(self):
        """Get all saved calibration files"""
        files = glob.glob("*_cal.npz")
        list_of_files = []
        for _, one_file in enumerate(files):
            list_of_files.append(one_file)
        if not list_of_files:
            print("Keine Datei vorhanden")
            return [""]
        return list_of_files

    def save_parameter(self, file_name) -> bool:
        """Save parameters in extra file"""
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        new_file = (
            file_name + dt_string + "_cal.npz"
        )  # "calibration_parameter/" + # ToDO: Save in Folder
        np.savez(
            new_file,
            mtx=self.calibration_values["mtx"],
            dst=self.calibration_values["dst"],
            newmtx=self.calibration_values["newmtx"],
            roi=self.calibration_values["roi"],
        )
        return True

    def get_images(self):
        """Get list of current images"""
        return self.images

    def get_number_of_images(self):
        """Get number of current images"""
        return len(self.images)

    def delete_all_images(self) -> None:
        """Delete all images"""
        self.images = []


def set_images(video_path):
    cap = cv2.VideoCapture(video_path)

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
        return

    list_images = []
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            list_images.append(frame)
        else:
            break
    # print(list_images)
    return list_images
    cali_class.add_pictures(list_images)

if __name__ == '__main__':
    # 1. record video

    # record_video(width=1280, height=720, fps=30)
    # 2. split video into frames e.g. `ffmpeg -i 2021-10-15_10:30:00.mp4 -f image2 frames/video_01-%07d.png` and delete blurry images
    # 3. run calibration on images
    # calibration('./frames', 30, debug=True)

    # vid_path = record_video_2(width=1280, height=720, fps=30, vid_time=30)
    cali = CameraCalibration()
    vid_path = '2023-07-26_09:10:54.mp4'
    imgs = set_images(vid_path)
    cali.add_pictures(imgs)
    cali.calibrate()