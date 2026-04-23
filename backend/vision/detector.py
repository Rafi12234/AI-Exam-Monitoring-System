import cv2
import torch
import numpy as np

class PersonDetector:
    """YOLO-based person detector for CCTV footage."""
    
    def __init__(self, model_path='yolov5s'):
        """
        Initialize YOLO detector.
        Args:
            model_path: Path to YOLOv5 model
        """
        try:
            self.model = torch.hub.load('ultralytics/yolov5', model_path, pretrained=True)
            self.model.conf = 0.45  # Confidence threshold
            self.model.iou = 0.45   # IOU threshold
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            print(f"PersonDetector loaded on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def detect(self, frame):
        """
        Detect persons in a frame.
        Args:
            frame: Input image frame
        Returns:
            List of detections with bounding boxes and confidence scores
        """
        if self.model is None:
            return []
        
        try:
            results = self.model(frame)
            detections = []
            
            # Filter for person class (class 0 in COCO)
            for *box, conf, cls in results.xyxy[0]:
                if int(cls) == 0:  # Person class
                    detection = {
                        'bbox': [float(x) for x in box],  # [x1, y1, x2, y2]
                        'confidence': float(conf),
                        'class': int(cls)
                    }
                    detections.append(detection)
            
            return detections
        except Exception as e:
            print(f"Error during detection: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes on frame.
        Args:
            frame: Input frame
            detections: List of detections
        Returns:
            Annotated frame
        """
        for detection in detections:
            x1, y1, x2, y2 = [int(x) for x in detection['bbox']]
            conf = detection['confidence']
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'Person {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
