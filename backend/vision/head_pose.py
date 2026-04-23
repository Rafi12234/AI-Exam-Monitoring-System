import cv2
import mediapipe as mp
import numpy as np

class HeadPoseEstimator:
    """MediaPipe-based head pose estimator."""
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=10,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def estimate(self, frame, bbox=None):
        """
        Estimate head pose from frame.
        Args:
            frame: Input frame
            bbox: Optional bounding box [x1, y1, x2, y2]
        Returns:
            String pose classification ('forward', 'left', 'right', 'back')
        """
        try:
            if bbox is not None:
                x1, y1, x2, y2 = [int(x) for x in bbox]
                # Ensure coordinates are valid
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)
                
                if x2 > x1 and y2 > y1:
                    face_region = frame[y1:y2, x1:x2]
                else:
                    return 'forward'
            else:
                face_region = frame
            
            rgb_frame = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return 'forward'
            
            # Use first face detected
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Calculate head pose
            pose = self._calculate_head_pose(landmarks)
            
            return pose
        except Exception as e:
            print(f"Head pose estimation error: {e}")
            return 'forward'
    
    def _calculate_head_pose(self, landmarks):
        """
        Calculate head pose from landmarks.
        Args:
            landmarks: MediaPipe face landmarks
        Returns:
            Pose classification string
        """
        # Use eye and nose positions to estimate pose
        left_eye = np.array([landmarks[33].x, landmarks[33].y])  # Left eye
        right_eye = np.array([landmarks[263].x, landmarks[263].y])  # Right eye
        nose = np.array([landmarks[1].x, landmarks[1].y])  # Nose tip
        
        # Calculate vectors
        eye_center = (left_eye + right_eye) / 2
        nose_to_eye = eye_center - nose
        
        # Estimate head pose angle
        angle_x = np.arctan2(nose_to_eye[1], nose_to_eye[0]) * 180 / np.pi
        
        # Estimate left-right turn (based on eye width changes)
        left_right_diff = (left_eye[0] - right_eye[0])
        horizontal_angle = abs(left_right_diff)
        
        # Classify pose with more lenient thresholds for better detection
        # Left/Right detection
        if horizontal_angle > 0.08:
            if left_eye[0] > right_eye[0] + 0.02:
                return 'left'
            elif right_eye[0] > left_eye[0] + 0.02:
                return 'right'
        
        # Back detection (looking downward/backward)
        if angle_x > 20 or nose_to_eye[1] < -0.1:
            return 'back'
        
        # Forward/neutral
        return 'forward'
    
    def is_unethical_behavior(self, pose_result):
        """
        Check if head pose indicates unethical behavior.
        Args:
            pose_result: Result from estimate()
        Returns:
            Boolean indicating unethical behavior
        """
        unethical_poses = ['back', 'left', 'right']
        return pose_result['pose'] in unethical_poses
    
    def draw_landmarks(self, frame, bbox=None):
        """
        Draw face landmarks on frame.
        Args:
            frame: Input frame
            bbox: Optional bounding box
        Returns:
            Annotated frame
        """
        if bbox:
            x1, y1, x2, y2 = [int(x) for x in bbox]
            face_region = frame[y1:y2, x1:x2]
        else:
            face_region = frame
            x1, y1 = 0, 0
        
        rgb_frame = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    face_region,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_TESSELATION
                )
        
        if bbox:
            frame[y1:y2, x1:x2] = face_region
        else:
            frame = face_region
        
        return frame
