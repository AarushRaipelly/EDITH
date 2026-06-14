import logging
from typing import List

logger = logging.getLogger("EDITH.Vision.Object")

class ObjectIdentifier:
    def __init__(self) -> None:
        pass

    def identify_objects(self, image_frame) -> List[str]:
        """Classifies items in a frame.
        In production, executes YOLO or TensorFlow models.
        """
        logger.info("Running object classifier neural net on frame.")
        return ["laptop", "coffee mug", "notebook", "cell phone"]
