import logging
from typing import Optional, Any

logger = logging.getLogger("EDITH.Vision.Camera")

try:
    import cv2
except ImportError:
    cv2 = None
    logger.warning("opencv-python not found. Camera frames will be simulated.")

class EdithCameraManager:
    def __init__(self, brain) -> None:
        self.brain = brain

    def capture_single_frame(self) -> Optional[Any]:
        """ALWAYS asks Boss for permission before activating camera. Captures image frame via OpenCV."""
        # 1. Ask Permission
        if not self.brain.request_permission("Activate system camera to capture a photo"):
            logger.warning("Camera activation rejected by Boss.")
            return None

        # 2. Capture Frame
        if not cv2:
            logger.info("OpenCV missing. Simulating successful picture capture.")
            return b"MOCK_CAMERA_FRAME_DATA"

        logger.info("Initializing OpenCV Camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Could not access camera device.")
            return None
            
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            logger.info("Successfully captured frame.")
            return frame
        else:
            logger.error("Failed to read image frame from camera.")
            return None
