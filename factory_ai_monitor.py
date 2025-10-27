"""
Factory Worker AI Monitor
Analyzes video streams to track working hours and performance metrics
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
import json
from collections import defaultdict
from typing import Dict, List, Tuple
import time

class FactoryWorkerMonitor:
    def __init__(self, video_source=0):
        """
        Initialize the Factory Worker Monitor
        
        Args:
            video_source: Camera index or video file path
        """
        self.video_source = video_source
        self.workers_data = defaultdict(lambda: {
            'total_work_time': 0,
            'idle_time': 0,
            'productive_time': 0,
            'activity_log': [],
            'performance_score': 0
        })
        
        # Activity thresholds
        self.motion_threshold = 25
        self.idle_threshold = 5  # seconds
        self.productivity_threshold = 0.7
        
        # Initialize background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True
        )
        
        # Performance metrics
        self.start_time = None
        self.frame_count = 0
        self.activity_states = {}
        
    def detect_workers(self, frame):
        """
        Detect workers in the frame using background subtraction and contour detection
        
        Args:
            frame: Input video frame
            
        Returns:
            List of worker bounding boxes and activity status
        """
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Remove shadows
        fg_mask[fg_mask == 127] = 0
        
        # Morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        workers = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area (adjust based on camera distance)
            if area > 1000:  # Minimum worker size
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate motion intensity
                roi_mask = fg_mask[y:y+h, x:x+w]
                motion_intensity = np.sum(roi_mask > 0) / (w * h) if (w * h) > 0 else 0
                
                # Determine activity status
                is_active = motion_intensity > (self.motion_threshold / 100)
                
                workers.append({
                    'id': f'worker_{i}',
                    'bbox': (x, y, w, h),
                    'area': area,
                    'motion_intensity': motion_intensity,
                    'is_active': is_active
                })
                
        return workers
    
    def calculate_performance_metrics(self, worker_id: str, active_time: float, 
                                     idle_time: float, total_time: float) -> Dict:
        """
        Calculate performance metrics for a worker
        
        Args:
            worker_id: Worker identifier
            active_time: Time spent actively working (seconds)
            idle_time: Time spent idle (seconds)
            total_time: Total monitoring time (seconds)
            
        Returns:
            Dictionary with performance metrics
        """
        if total_time == 0:
            return {}
            
        productivity_rate = (active_time / total_time) * 100
        idle_rate = (idle_time / total_time) * 100
        
        # Performance score (0-100)
        performance_score = min(100, productivity_rate * 1.2)
        
        # Performance rating
        if performance_score >= 85:
            rating = "Excellent"
        elif performance_score >= 70:
            rating = "Good"
        elif performance_score >= 50:
            rating = "Average"
        else:
            rating = "Needs Improvement"
        
        return {
            'worker_id': worker_id,
            'total_time_minutes': round(total_time / 60, 2),
            'active_time_minutes': round(active_time / 60, 2),
            'idle_time_minutes': round(idle_time / 60, 2),
            'productivity_rate': round(productivity_rate, 2),
            'idle_rate': round(idle_rate, 2),
            'performance_score': round(performance_score, 2),
            'rating': rating,
            'effective_working_hours': round(active_time / 3600, 2)
        }
    
    def analyze_video_stream(self, duration_seconds=60, display=True):
        """
        Analyze video stream for specified duration
        
        Args:
            duration_seconds: Duration to analyze (seconds)
            display: Whether to display video output
            
        Returns:
            Performance report for all workers
        """
        cap = cv2.VideoCapture(self.video_source)
        
        if not cap.isOpened():
            print("Error: Could not open video source")
            return None
        
        self.start_time = time.time()
        end_time = self.start_time + duration_seconds
        
        print(f"Starting analysis for {duration_seconds} seconds...")
        print("Press 'q' to quit early\n")
        
        frame_times = defaultdict(list)
        last_activity_time = defaultdict(lambda: time.time())
        
        while time.time() < end_time:
            ret, frame = cap.read()
            
            if not ret:
                # Loop video if it's a file
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            self.frame_count += 1
            current_time = time.time()
            
            # Detect workers
            workers = self.detect_workers(frame)
            
            # Update worker data
            for worker in workers:
                worker_id = worker['id']
                is_active = worker['is_active']
                
                if is_active:
                    self.workers_data[worker_id]['productive_time'] += 1/30  # Assuming 30 FPS
                    last_activity_time[worker_id] = current_time
                else:
                    # Check if idle for more than threshold
                    idle_duration = current_time - last_activity_time[worker_id]
                    if idle_duration > self.idle_threshold:
                        self.workers_data[worker_id]['idle_time'] += 1/30
                
                self.workers_data[worker_id]['total_work_time'] = (
                    current_time - self.start_time
                )
                
                # Draw bounding box
                if display:
                    x, y, w, h = worker['bbox']
                    color = (0, 255, 0) if is_active else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Add label
                    status = "ACTIVE" if is_active else "IDLE"
                    label = f"{worker_id}: {status}"
                    cv2.putText(frame, label, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Display statistics
            if display:
                elapsed = current_time - self.start_time
                cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Workers: {len(workers)}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Factory Worker Monitor', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cap.release()
        if display:
            cv2.destroyAllWindows()
        
        # Generate final report
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive performance report
        
        Returns:
            Dictionary containing performance metrics for all workers
        """
        total_elapsed = time.time() - self.start_time if self.start_time else 0
        
        report = {
            'session_info': {
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': round(total_elapsed, 2),
                'total_workers': len(self.workers_data),
                'total_frames_processed': self.frame_count
            },
            'workers': []
        }
        
        for worker_id, data in self.workers_data.items():
            metrics = self.calculate_performance_metrics(
                worker_id,
                data['productive_time'],
                data['idle_time'],
                data['total_work_time']
            )
            report['workers'].append(metrics)
        
        # Calculate aggregate statistics
        if report['workers']:
            avg_performance = np.mean([w['performance_score'] for w in report['workers']])
            avg_productivity = np.mean([w['productivity_rate'] for w in report['workers']])
            total_effective_hours = sum([w['effective_working_hours'] for w in report['workers']])
            
            report['aggregate_statistics'] = {
                'average_performance_score': round(avg_performance, 2),
                'average_productivity_rate': round(avg_productivity, 2),
                'total_effective_working_hours': round(total_effective_hours, 2)
            }
        
        return report
    
    def save_report(self, report: Dict, filename='performance_report.json'):
        """Save report to JSON file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"\nReport saved to {filename}")
        
    def print_report(self, report: Dict):
        """Print formatted report to console"""
        print("\n" + "="*60)
        print("FACTORY WORKER PERFORMANCE REPORT")
        print("="*60)
        
        session = report['session_info']
        print(f"\nSession Start: {session['start_time']}")
        print(f"Duration: {session['duration_seconds']:.2f} seconds")
        print(f"Total Workers Detected: {session['total_workers']}")
        print(f"Frames Processed: {session['total_frames_processed']}")
        
        print("\n" + "-"*60)
        print("INDIVIDUAL WORKER PERFORMANCE")
        print("-"*60)
        
        for worker in report['workers']:
            print(f"\n{worker['worker_id'].upper()}")
            print(f"  Effective Working Hours: {worker['effective_working_hours']:.2f} hrs")
            print(f"  Active Time: {worker['active_time_minutes']:.2f} min")
            print(f"  Idle Time: {worker['idle_time_minutes']:.2f} min")
            print(f"  Productivity Rate: {worker['productivity_rate']:.2f}%")
            print(f"  Performance Score: {worker['performance_score']:.2f}/100")
            print(f"  Rating: {worker['rating']}")
        
        if 'aggregate_statistics' in report:
            print("\n" + "-"*60)
            print("AGGREGATE STATISTICS")
            print("-"*60)
            stats = report['aggregate_statistics']
            print(f"  Average Performance Score: {stats['average_performance_score']:.2f}/100")
            print(f"  Average Productivity Rate: {stats['average_productivity_rate']:.2f}%")
            print(f"  Total Effective Working Hours: {stats['total_effective_working_hours']:.2f} hrs")
        
        print("\n" + "="*60 + "\n")


def simulate_factory_monitoring():
    """
    Simulate factory monitoring with synthetic data
    This is useful for testing without video input
    """
    print("Running simulation mode with synthetic data...\n")
    
    # Create synthetic report
    report = {
        'session_info': {
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': 3600,
            'total_workers': 5,
            'total_frames_processed': 108000
        },
        'workers': [
            {
                'worker_id': 'worker_0',
                'total_time_minutes': 60.0,
                'active_time_minutes': 52.5,
                'idle_time_minutes': 7.5,
                'productivity_rate': 87.5,
                'idle_rate': 12.5,
                'performance_score': 95.0,
                'rating': 'Excellent',
                'effective_working_hours': 0.88
            },
            {
                'worker_id': 'worker_1',
                'total_time_minutes': 60.0,
                'active_time_minutes': 48.0,
                'idle_time_minutes': 12.0,
                'productivity_rate': 80.0,
                'idle_rate': 20.0,
                'performance_score': 88.0,
                'rating': 'Excellent',
                'effective_working_hours': 0.80
            },
            {
                'worker_id': 'worker_2',
                'total_time_minutes': 60.0,
                'active_time_minutes': 43.5,
                'idle_time_minutes': 16.5,
                'productivity_rate': 72.5,
                'idle_rate': 27.5,
                'performance_score': 79.0,
                'rating': 'Good',
                'effective_working_hours': 0.73
            },
            {
                'worker_id': 'worker_3',
                'total_time_minutes': 60.0,
                'active_time_minutes': 38.0,
                'idle_time_minutes': 22.0,
                'productivity_rate': 63.3,
                'idle_rate': 36.7,
                'performance_score': 68.0,
                'rating': 'Average',
                'effective_working_hours': 0.63
            },
            {
                'worker_id': 'worker_4',
                'total_time_minutes': 60.0,
                'active_time_minutes': 51.0,
                'idle_time_minutes': 9.0,
                'productivity_rate': 85.0,
                'idle_rate': 15.0,
                'performance_score': 92.0,
                'rating': 'Excellent',
                'effective_working_hours': 0.85
            }
        ],
        'aggregate_statistics': {
            'average_performance_score': 84.4,
            'average_productivity_rate': 77.66,
            'total_effective_working_hours': 3.89
        }
    }
    
    return report


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("FACTORY WORKER AI MONITOR")
    print("="*60)
    print("\nMode Selection:")
    print("1. Live Camera/Video Analysis")
    print("2. Simulation Mode (Synthetic Data)")
    
    mode = input("\nSelect mode (1 or 2): ").strip()
    
    if mode == "1":
        # Real video analysis
        video_source = input("Enter video source (0 for webcam, or path to video file): ").strip()
        if video_source.isdigit():
            video_source = int(video_source)
        
        duration = int(input("Enter analysis duration in seconds (default 60): ") or "60")
        
        monitor = FactoryWorkerMonitor(video_source)
        report = monitor.analyze_video_stream(duration_seconds=duration, display=True)
        
        if report:
            monitor.print_report(report)
            monitor.save_report(report, '/mnt/user-data/outputs/performance_report.json')
    else:
        # Simulation mode
        report = simulate_factory_monitoring()
        monitor = FactoryWorkerMonitor()
        monitor.print_report(report)
        
        # Save simulation report
        with open('/mnt/user-data/outputs/performance_report.json', 'w') as f:
            json.dump(report, f, indent=4)
        print("Report saved to /mnt/user-data/outputs/performance_report.json")
