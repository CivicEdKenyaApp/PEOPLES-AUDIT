# monitor.py - Pipeline Monitoring System
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import humanize

class PipelineMonitor:
    def __init__(self, pipeline_root: Path):
        self.root = pipeline_root
        self.logs_dir = pipeline_root / 'logs'
        self.monitor_dir = pipeline_root / 'monitoring'
        self.monitor_dir.mkdir(exist_ok=True)
        
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Setup monitoring system"""
        self.metrics_file = self.monitor_dir / 'metrics.json'
        self.alert_file = self.monitor_dir / 'alerts.json'
        
        # Initialize metrics if not exists
        if not self.metrics_file.exists():
            self.initialize_metrics()
    
    def initialize_metrics(self):
        """Initialize metrics storage"""
        initial_metrics = {
            'start_time': datetime.now().isoformat(),
            'runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'total_processing_time': 0,
            'average_processing_time': 0,
            'documents_generated': 0,
            'data_points_extracted': 0,
            'last_run': None,
            'system_metrics': {}
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(initial_metrics, f, indent=2)
    
    def log_run_start(self):
        """Log pipeline run start"""
        metrics = self.load_metrics()
        metrics['current_run'] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        metrics['runs'] += 1
        self.save_metrics(metrics)
    
    def log_run_complete(self, success: bool, stats: dict):
        """Log pipeline run completion"""
        metrics = self.load_metrics()
        
        if 'current_run' in metrics:
            run_data = metrics['current_run']
            run_data['end_time'] = datetime.now().isoformat()
            run_data['status'] = 'completed' if success else 'failed'
            
            # Calculate duration
            start_time = datetime.fromisoformat(run_data['start_time'])
            end_time = datetime.fromisoformat(run_data['end_time'])
            duration = (end_time - start_time).total_seconds()
            
            run_data['duration_seconds'] = duration
            
            # Update overall metrics
            if success:
                metrics['successful_runs'] += 1
                metrics['documents_generated'] += stats.get('documents_generated', 0)
                metrics['data_points_extracted'] += stats.get('data_points_extracted', 0)
            else:
                metrics['failed_runs'] += 1
            
            metrics['total_processing_time'] += duration
            metrics['average_processing_time'] = (
                metrics['total_processing_time'] / metrics['runs']
            )
            
            metrics['last_run'] = run_data
            
            # Add system metrics
            metrics['system_metrics'] = self.collect_system_metrics()
            
            del metrics['current_run']
        
        self.save_metrics(metrics)
        
        # Check for alerts
        self.check_alerts(metrics, success, stats)
    
    def collect_system_metrics(self) -> dict:
        """Collect system performance metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'available_memory': humanize.naturalsize(psutil.virtual_memory().available),
            'process_count': len(psutil.pids())
        }
    
    def check_alerts(self, metrics: dict, success: bool, stats: dict):
        """Check for conditions that require alerts"""
        alerts = []
        
        # Check for failed run
        if not success:
            alerts.append({
                'level': 'ERROR',
                'message': 'Pipeline run failed',
                'timestamp': datetime.now().isoformat(),
                'run_stats': stats
            })
        
        # Check for performance degradation
        avg_time = metrics.get('average_processing_time', 0)
        if avg_time > 3600:  # More than 1 hour
            alerts.append({
                'level': 'WARNING',
                'message': f'Average processing time high: {avg_time:.0f} seconds',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check system resources
        sys_metrics = metrics.get('system_metrics', {})
        if sys_metrics.get('memory_percent', 0) > 90:
            alerts.append({
                'level': 'WARNING',
                'message': f'High memory usage: {sys_metrics["memory_percent"]}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # Save alerts if any
        if alerts:
            self.save_alerts(alerts)
    
    def save_alerts(self, alerts: list):
        """Save alerts to file"""
        existing_alerts = self.load_alerts()
        existing_alerts.extend(alerts)
        
        # Keep only last 100 alerts
        if len(existing_alerts) > 100:
            existing_alerts = existing_alerts[-100:]
        
        with open(self.alert_file, 'w') as f:
            json.dump(existing_alerts, f, indent=2)
    
    def load_metrics(self) -> dict:
        """Load metrics from file"""
        try:
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.initialize_metrics()
            return self.load_metrics()
    
    def load_alerts(self) -> list:
        """Load alerts from file"""
        try:
            with open(self.alert_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_metrics(self, metrics: dict):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def generate_report(self) -> str:
        """Generate monitoring report"""
        metrics = self.load_metrics()
        alerts = self.load_alerts()
        
        report = f"""
        People's Audit Pipeline Monitoring Report
        =========================================
        
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        SUMMARY
        -------
        Total Runs: {metrics.get('runs', 0)}
        Successful: {metrics.get('successful_runs', 0)}
        Failed: {metrics.get('failed_runs', 0)}
        Success Rate: {(metrics.get('successful_runs', 0) / metrics.get('runs', 1) * 100):.1f}%
        
        PERFORMANCE
        -----------
        Average Processing Time: {metrics.get('average_processing_time', 0):.0f} seconds
        Total Processing Time: {humanize.naturaldelta(timedelta(seconds=metrics.get('total_processing_time', 0)))}
        
        OUTPUTS
        -------
        Documents Generated: {metrics.get('documents_generated', 0)}
        Data Points Extracted: {metrics.get('data_points_extracted', 0)}
        
        SYSTEM METRICS
        --------------
        CPU Usage: {metrics.get('system_metrics', {}).get('cpu_percent', 'N/A')}%
        Memory Usage: {metrics.get('system_metrics', {}).get('memory_percent', 'N/A')}%
        Available Memory: {metrics.get('system_metrics', {}).get('available_memory', 'N/A')}
        
        RECENT ALERTS ({len(alerts)} total)
        --------------------------
        """
        
        for alert in alerts[-10:]:  # Last 10 alerts
            report += f"\n[{alert.get('level')}] {alert.get('timestamp')}: {alert.get('message')}"
        
        report += f"""
        
        RECOMMENDATIONS
        ---------------
        """
        
        # Add recommendations based on metrics
        if metrics.get('failed_runs', 0) > 0:
            report += "- Review failed runs in logs directory\n"
        
        if metrics.get('system_metrics', {}).get('memory_percent', 0) > 80:
            report += "- Consider increasing system memory\n"
        
        avg_time = metrics.get('average_processing_time', 0)
        if avg_time > 1800:
            report += f"- Optimize pipeline (current avg: {avg_time:.0f}s)\n"
        
        report += "\n--- End of Report ---"
        
        return report