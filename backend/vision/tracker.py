import numpy as np
from collections import defaultdict

class PersonTracker:
    """DeepSORT-based person tracker for maintaining identity across frames."""
    
    def __init__(self, max_age=30):
        """
        Initialize tracker.
        Args:
            max_age: Maximum frames to keep track without detection
        """
        self.max_age = max_age
        self.tracks = {}  # {track_id: track_info}
        self.next_id = 1
        self.frame_count = 0
        
    def update(self, detections):
        """
        Update tracker with new detections.
        Args:
            detections: List of detection dicts with 'bbox' and 'confidence'
        Returns:
            List of active tracks with track_id and bbox
        """
        self.frame_count += 1
        
        # Update existing tracks
        matched_tracks = set()
        
        for detection in detections:
            bbox = detection['bbox']
            best_track_id = None
            best_distance = float('inf')
            
            # Find best matching track
            for track_id, track_info in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                
                distance = self._calculate_iou_distance(bbox, track_info['bbox'])
                if distance < best_distance and distance < 0.5:  # IOU threshold
                    best_distance = distance
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                self.tracks[best_track_id]['bbox'] = bbox
                self.tracks[best_track_id]['age'] = 0
                self.tracks[best_track_id]['confidence'] = detection['confidence']
                matched_tracks.add(best_track_id)
            else:
                # Create new track
                self.tracks[self.next_id] = {
                    'bbox': bbox,
                    'age': 0,
                    'confidence': detection['confidence'],
                    'created_at': self.frame_count
                }
                self.next_id += 1
        
        # Age out unmatched tracks
        unmatched_ids = []
        for track_id in self.tracks.keys():
            if track_id not in matched_tracks:
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    unmatched_ids.append(track_id)
        
        for track_id in unmatched_ids:
            del self.tracks[track_id]
        
        # Return active tracks
        active_tracks = []
        for track_id, track_info in self.tracks.items():
            active_tracks.append({
                'track_id': track_id,
                'bbox': track_info['bbox'],
                'confidence': track_info['confidence']
            })
        
        return active_tracks
    
    def _calculate_iou_distance(self, box1, box2):
        """
        Calculate IoU distance between two bounding boxes.
        Args:
            box1, box2: Bounding boxes [x1, y1, x2, y2]
        Returns:
            IoU distance (1 - IoU)
        """
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Calculate intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 1.0  # No intersection
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Calculate union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        if union_area == 0:
            return 1.0
        
        iou = inter_area / union_area
        return 1 - iou
    
    def draw_tracks(self, frame, tracks):
        """
        Draw tracked persons on frame.
        Args:
            frame: Input frame
            tracks: List of tracks
        Returns:
            Annotated frame
        """
        import cv2
        for track in tracks:
            track_id = track['track_id']
            x1, y1, x2, y2 = [int(x) for x in track['bbox']]
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame
