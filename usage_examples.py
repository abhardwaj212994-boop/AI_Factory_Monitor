"""
Sample Usage Script for Factory Worker AI Monitor
Demonstrates various ways to use the monitoring system
"""

from factory_ai_monitor import FactoryWorkerMonitor
import json

# Example 1: Basic webcam monitoring
print("Example 1: Basic Webcam Monitoring")
print("-" * 50)

def example_webcam_monitoring():
    """Monitor workers using webcam for 30 seconds"""
    monitor = FactoryWorkerMonitor(video_source=0)
    report = monitor.analyze_video_stream(duration_seconds=30, display=True)
    
    if report:
        monitor.print_report(report)
        monitor.save_report(report, 'webcam_report.json')
    
    return report


# Example 2: Video file analysis
print("\nExample 2: Video File Analysis")
print("-" * 50)

def example_video_file_analysis():
    """Analyze a pre-recorded video file"""
    video_path = 'factory_footage.mp4'  # Replace with your video path
    
    monitor = FactoryWorkerMonitor(video_source=video_path)
    report = monitor.analyze_video_stream(duration_seconds=120, display=False)
    
    if report:
        # Extract key insights
        print("\nKey Insights:")
        print(f"Total Workers: {report['session_info']['total_workers']}")
        
        if 'aggregate_statistics' in report:
            avg_score = report['aggregate_statistics']['average_performance_score']
            print(f"Average Performance: {avg_score}/100")
            
            # Identify top performers
            workers = sorted(report['workers'], 
                           key=lambda x: x['performance_score'], 
                           reverse=True)
            print(f"\nTop Performer: {workers[0]['worker_id']} "
                  f"({workers[0]['performance_score']}/100)")
        
        monitor.save_report(report, 'video_analysis_report.json')
    
    return report


# Example 3: Custom configuration
print("\nExample 3: Custom Configuration")
print("-" * 50)

def example_custom_configuration():
    """Use custom thresholds for specific factory conditions"""
    monitor = FactoryWorkerMonitor(video_source=0)
    
    # Adjust sensitivity for specific environment
    monitor.motion_threshold = 15  # More sensitive motion detection
    monitor.idle_threshold = 10    # Longer idle time before flagging
    
    print("Custom Configuration:")
    print(f"  Motion Threshold: {monitor.motion_threshold}")
    print(f"  Idle Threshold: {monitor.idle_threshold}s")
    
    # Run monitoring
    report = monitor.analyze_video_stream(duration_seconds=45, display=True)
    
    return report


# Example 4: Real-time performance alerts
print("\nExample 4: Performance Alerts")
print("-" * 50)

def example_performance_alerts(report):
    """Generate alerts based on performance thresholds"""
    if not report or 'workers' not in report:
        print("No report data available")
        return
    
    print("\nPerformance Alerts:")
    
    alerts = {
        'low_productivity': [],
        'excessive_idle': [],
        'excellent_performance': []
    }
    
    for worker in report['workers']:
        worker_id = worker['worker_id']
        score = worker['performance_score']
        idle_rate = worker['idle_rate']
        
        # Check conditions
        if score < 60:
            alerts['low_productivity'].append(worker_id)
        if idle_rate > 30:
            alerts['excessive_idle'].append(worker_id)
        if score >= 90:
            alerts['excellent_performance'].append(worker_id)
    
    # Print alerts
    if alerts['low_productivity']:
        print(f"⚠️  Low Productivity: {', '.join(alerts['low_productivity'])}")
    
    if alerts['excessive_idle']:
        print(f"⚠️  Excessive Idle Time: {', '.join(alerts['excessive_idle'])}")
    
    if alerts['excellent_performance']:
        print(f"⭐ Excellent Performance: {', '.join(alerts['excellent_performance'])}")
    
    return alerts


# Example 5: Batch processing multiple video files
print("\nExample 5: Batch Processing")
print("-" * 50)

def example_batch_processing():
    """Process multiple video files and generate comparative report"""
    video_files = [
        'shift_morning.mp4',
        'shift_afternoon.mp4',
        'shift_evening.mp4'
    ]
    
    all_reports = []
    
    for video_file in video_files:
        print(f"\nProcessing: {video_file}")
        
        try:
            monitor = FactoryWorkerMonitor(video_source=video_file)
            report = monitor.analyze_video_stream(duration_seconds=300, display=False)
            
            if report:
                report['video_file'] = video_file
                all_reports.append(report)
                print(f"✓ Completed: {video_file}")
        except Exception as e:
            print(f"✗ Error processing {video_file}: {e}")
    
    # Generate comparative analysis
    if all_reports:
        print("\n" + "=" * 50)
        print("COMPARATIVE ANALYSIS")
        print("=" * 50)
        
        for report in all_reports:
            video_name = report.get('video_file', 'Unknown')
            if 'aggregate_statistics' in report:
                avg_score = report['aggregate_statistics']['average_performance_score']
                print(f"{video_name}: {avg_score}/100")
        
        # Save combined report
        with open('batch_analysis_report.json', 'w') as f:
            json.dump(all_reports, f, indent=4)
        print("\nBatch report saved to: batch_analysis_report.json")
    
    return all_reports


# Example 6: Export for data analysis
print("\nExample 6: Data Export")
print("-" * 50)

def example_data_export(report):
    """Export data in various formats for further analysis"""
    if not report:
        print("No report data available")
        return
    
    # Export to CSV
    try:
        import csv
        
        with open('worker_performance.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Worker ID', 'Effective Hours', 'Active Time (min)',
                'Idle Time (min)', 'Productivity Rate', 'Performance Score', 'Rating'
            ])
            
            # Data rows
            for worker in report['workers']:
                writer.writerow([
                    worker['worker_id'],
                    worker['effective_working_hours'],
                    worker['active_time_minutes'],
                    worker['idle_time_minutes'],
                    worker['productivity_rate'],
                    worker['performance_score'],
                    worker['rating']
                ])
        
        print("✓ Data exported to: worker_performance.csv")
    
    except Exception as e:
        print(f"✗ Export error: {e}")


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("FACTORY WORKER AI MONITOR - USAGE EXAMPLES")
    print("=" * 50)
    
    # Run simulation to get sample data
    print("\nGenerating sample data...")
    from factory_ai_monitor import simulate_factory_monitoring
    
    sample_report = simulate_factory_monitoring()
    
    # Run examples with sample data
    print("\n" + "=" * 50)
    example_performance_alerts(sample_report)
    
    print("\n" + "=" * 50)
    example_data_export(sample_report)
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)
    
    # Uncomment to run live examples:
    # example_webcam_monitoring()
    # example_video_file_analysis()
    # example_custom_configuration()
    # example_batch_processing()
