import logging

logger = logging.getLogger("EDITH.Vision.Face")

class FaceRecognizer:
    def __init__(self, memory_db) -> None:
        self.memory_db = memory_db

    def recognize_face_from_frame(self, frame_data) -> str:
        """Compares captured facial layout with stored face embeddings.
        Returns: Name of identified contact, or 'Unknown'.
        """
        logger.info("Running face biometric matching on frame.")
        
        # In production, uses `face_recognition` library:
        # matches = face_recognition.compare_faces(known_faces, current_face)
        
        # Mock logic matching registered profile
        has_face = self.memory_db.get_memory("security", "face_profile_registered")
        if has_face == "True":
            return "Boss"
            
        return "Unknown"

    def handle_unrecognized_face(self) -> str:
        """Standard alert returned when a stranger is detected."""
        return "Unknown — Boss, someone I don't recognize is here."
