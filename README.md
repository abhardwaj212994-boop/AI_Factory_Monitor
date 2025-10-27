# Factory Worker AI Monitor

An intelligent video monitoring system that analyzes factory worker performance, tracks effective working hours, and generates comprehensive performance reports.

## Features

- **Real-time Video Analysis**: Process live video streams from cameras or video files
- **Worker Detection**: Automatic detection and tracking of workers using computer vision
- **Activity Recognition**: Distinguish between active work and idle time
- **Performance Metrics**: Calculate productivity rates, performance scores, and effective working hours
- **Comprehensive Reports**: Generate detailed JSON reports and visualizations
- **TikZ Visualizations**: Professional LaTeX/TikZ diagrams for system architecture and performance dashboards

## System Architecture

The system uses a multi-stage computer vision pipeline:

1. **Video Input**: Capture frames from IP cameras or video files
2. **Background Subtraction**: MOG2 algorithm to detect moving objects
3. **Worker Detection**: Contour detection to identify workers
4. **Motion Analysis**: Calculate motion intensity to determine activity status
5. **Performance Calculation**: Track time metrics and generate scores
6. **Report Generation**: Output JSON reports and visualizations

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenCV
- NumPy
- LaTeX (for TikZ visualizations)

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# For LaTeX/TikZ support (Ubuntu/Debian)
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-pictures
```

## Usage

### Running the Monitor

```bash
python factory_ai_monitor.py
```

You'll be prompted to select a mode:

1. **Live Camera/Video Analysis**: Process real video streams
2. **Simulation Mode**: Generate sample reports with synthetic data

### Live Video Analysis

```python
from factory_ai_monitor import FactoryWorkerMonitor

# Initialize monitor
monitor = FactoryWorkerMonitor(video_source=0)  # 0 for webcam, or path to video file

# Run analysis for 60 seconds
report = monitor.analyze_video_stream(duration_seconds=60, display=True)

# Print and save report
monitor.print_report(report)
monitor.save_report(report, 'performance_report.json')
```

### Video Source Options

- **Webcam**: `video_source=0` (or 1, 2, etc. for multiple cameras)
- **Video File**: `video_source='path/to/video.mp4'`
- **IP Camera**: `video_source='rtsp://username:password@ip:port/stream'`

## Performance Metrics

The system calculates the following metrics for each worker:

| Metric | Description |
|--------|-------------|
| **Effective Working Hours** | Total time spent actively working |
| **Productivity Rate** | Percentage of time spent working vs. idle |
| **Idle Rate** | Percentage of time spent idle |
| **Performance Score** | Overall score (0-100) based on productivity |
| **Rating** | Qualitative rating (Excellent/Good/Average/Needs Improvement) |

### Performance Rating Scale

- **Excellent**: 85-100 points
- **Good**: 70-84 points
- **Average**: 50-69 points
- **Needs Improvement**: <50 points

## Output Examples

### JSON Report Structure

```json
{
    "session_info": {
        "start_time": "2025-10-27 14:30:00",
        "duration_seconds": 3600,
        "total_workers": 5,
        "total_frames_processed": 108000
    },
    "workers": [
        {
            "worker_id": "worker_0",
            "effective_working_hours": 0.88,
            "active_time_minutes": 52.5,
            "idle_time_minutes": 7.5,
            "productivity_rate": 87.5,
            "performance_score": 95.0,
            "rating": "Excellent"
        }
    ],
    "aggregate_statistics": {
        "average_performance_score": 84.4,
        "average_productivity_rate": 77.66,
        "total_effective_working_hours": 3.89
    }
}
```

### Console Output

```
============================================================
FACTORY WORKER PERFORMANCE REPORT
============================================================

Session Start: 2025-10-27 14:30:00
Duration: 3600.00 seconds
Total Workers Detected: 5
Frames Processed: 108000

------------------------------------------------------------
INDIVIDUAL WORKER PERFORMANCE
------------------------------------------------------------

WORKER_0
  Effective Working Hours: 0.88 hrs
  Active Time: 52.50 min
  Idle Time: 7.50 min
  Productivity Rate: 87.50%
  Performance Score: 95.00/100
  Rating: Excellent

...
```

## TikZ Visualizations

The system includes professional LaTeX/TikZ diagrams:

1. **System Architecture Diagram**: Complete data flow and processing pipeline
2. **Performance Monitoring Workflow**: Real-time monitoring process
3. **Performance Dashboard**: Visual representation of worker metrics
4. **Technical Architecture**: Detailed component breakdown

### Generating TikZ Diagrams

```bash
# Compile LaTeX document
pdflatex factory_monitor_tikz.tex

# View the generated PDF
# Output: factory_monitor_tikz.pdf
```

## Configuration

### Adjustable Parameters

```python
monitor = FactoryWorkerMonitor(video_source=0)

# Adjust detection thresholds
monitor.motion_threshold = 25  # Motion sensitivity (0-100)
monitor.idle_threshold = 5     # Idle detection time (seconds)
monitor.productivity_threshold = 0.7  # Productivity baseline
```

## Technical Details

### Computer Vision Pipeline

- **Background Subtraction**: MOG2 (Mixture of Gaussians 2)
- **Morphological Operations**: Noise reduction and object enhancement
- **Contour Detection**: Worker boundary identification
- **Motion Analysis**: Pixel-based activity measurement

### Performance Calculation

```
Productivity Rate = (Active Time / Total Time) × 100
Performance Score = min(100, Productivity Rate × 1.2)
Effective Working Hours = Active Time / 3600
```

## Use Cases

- **Manufacturing Plants**: Monitor assembly line efficiency
- **Warehouses**: Track loading/unloading operations
- **Construction Sites**: Analyze worker activity patterns
- **Retail**: Measure employee productivity during shifts
- **Quality Control**: Ensure consistent work patterns

## Privacy & Ethics

⚠️ **Important Considerations**:

- Obtain proper consent before monitoring employees
- Comply with local labor laws and privacy regulations
- Use data responsibly and transparently
- Focus on improving processes, not punishing workers
- Provide feedback mechanisms for employees

## Limitations

- Requires clear camera view of workers
- May struggle with heavy occlusions or poor lighting
- Worker identification requires consistent positioning
- Motion-based detection may not capture all work types

## Future Enhancements

- [ ] Deep learning-based person detection (YOLO, Faster R-CNN)
- [ ] Multi-camera support with worker re-identification
- [ ] Pose estimation for detailed activity analysis
- [ ] Integration with time-tracking systems
- [ ] Real-time dashboard with live updates
- [ ] Anomaly detection for safety incidents

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Include docstrings for all functions
- Add unit tests for new features
- Update documentation

## License

This project is provided as-is for educational and commercial purposes.

## Support

For issues, questions, or feature requests, please refer to the documentation or contact support.

---

**Built with**: Python, OpenCV, NumPy, LaTeX/TikZ

**Last Updated**: October 2025
