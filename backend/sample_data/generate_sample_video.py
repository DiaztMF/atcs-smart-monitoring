import os
import cv2
import numpy as np

def create_synthetic_traffic_clip(output_path: str = "sample_data/synthetic_traffic.mp4", num_frames: int = 200):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 15.0, (640, 360))
    
    for i in range(num_frames):
        frame = np.full((360, 640, 3), 45, dtype=np.uint8) # Dark asphalt road
        
        # Road markings
        cv2.line(frame, (320, 0), (320, 360), (255, 255, 255), 2)
        cv2.line(frame, (100, 0), (100, 360), (200, 200, 200), 2)
        cv2.line(frame, (540, 0), (540, 360), (200, 200, 200), 2)
        
        # Simulated Inbound Car (top to bottom)
        car_y = int((i * 4) % 360)
        cv2.rectangle(frame, (180, car_y), (250, min(360, car_y + 60)), (180, 50, 50), -1)
        cv2.putText(frame, "SIMULATED VEHICLE (INBOUND)", (130, max(20, car_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Simulated Outbound Motorcycle (bottom to top)
        moto_y = int((360 - (i * 5)) % 360)
        cv2.rectangle(frame, (400, moto_y), (430, min(360, moto_y + 40)), (50, 180, 50), -1)
        cv2.putText(frame, "SIMULATED MOTOR (OUTBOUND)", (360, max(20, moto_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        out.write(frame)
        
    out.release()
    print(f"Synthetic traffic clip created at {output_path}")

if __name__ == "__main__":
    create_synthetic_traffic_clip()
