"""
Automatic Error Reporting System for Brain Buddy
Captures, logs, and reports both client-side and server-side errors
"""

import os
import json
import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from flask import request, session
from firebase_config import get_firestore_client

class ErrorReporter:
    """Comprehensive error reporting and tracking system"""
    
    def __init__(self):
        self.firestore_client = None
        self.setup_logging()
        self.initialize_firebase()
    
    def setup_logging(self):
        """Configure enhanced logging for error tracking"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure error-specific logger
        self.error_logger = logging.getLogger('brain_buddy_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # File handler for persistent error logs
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.error_logger.addHandler(error_handler)
        self.error_logger.addHandler(console_handler)
    
    def initialize_firebase(self):
        """Initialize Firebase connection for cloud error storage"""
        try:
            self.firestore_client = get_firestore_client()
            print("Error reporting: Firebase initialized successfully")
        except Exception as e:
            print(f"Error reporting: Firebase initialization failed - {e}")
            self.firestore_client = None
    
    def capture_server_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Capture and report server-side Python errors
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Error ID for tracking
        """
        error_id = self._generate_error_id()
        
        error_data = {
            'error_id': error_id,
            'type': 'server_error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'url': request.url if request else 'N/A',
            'method': request.method if request else 'N/A',
            'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
            'ip_address': self._get_client_ip(),
            'session_data': self._get_safe_session_data(),
            'context': context if context is not None else {}
        }
        
        # Log to file
        self.error_logger.error(f"Server Error {error_id}: {error_data}")
        
        # Store in Firebase if available
        self._store_error_in_firebase(error_data)
        
        return error_id
    
    def capture_client_error(self, error_data: Dict[str, Any]) -> str:
        """
        Capture and report client-side JavaScript errors
        
        Args:
            error_data: Error information from client
            
        Returns:
            Error ID for tracking
        """
        error_id = self._generate_error_id()
        
        enhanced_error_data = {
            'error_id': error_id,
            'type': 'client_error',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'url': request.url if request else error_data.get('url', 'N/A'),
            'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
            'ip_address': self._get_client_ip(),
            'session_data': self._get_safe_session_data(),
            **error_data
        }
        
        # Log to file
        self.error_logger.error(f"Client Error {error_id}: {enhanced_error_data}")
        
        # Store in Firebase if available
        self._store_error_in_firebase(enhanced_error_data)
        
        return error_id
    
    def get_error_statistics(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get error statistics for the specified time period
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Dictionary containing error statistics
        """
        if not self.firestore_client:
            return self._get_local_error_stats(days_back)
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            errors_ref = self.firestore_client.collection('error_reports')
            query = errors_ref.where('timestamp', '>=', cutoff_date.isoformat())
            
            errors = list(query.stream())
            
            stats = {
                'total_errors': len(errors),
                'server_errors': 0,
                'client_errors': 0,
                'error_types': {},
                'most_common_errors': [],
                'recent_errors': []
            }
            
            for error_doc in errors:
                error_data = error_doc.to_dict()
                
                if error_data.get('type') == 'server_error':
                    stats['server_errors'] += 1
                elif error_data.get('type') == 'client_error':
                    stats['client_errors'] += 1
                
                error_type = error_data.get('error_type', 'Unknown')
                stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1
                
                # Add to recent errors (limit to 10)
                if len(stats['recent_errors']) < 10:
                    stats['recent_errors'].append({
                        'error_id': error_data.get('error_id'),
                        'type': error_data.get('type'),
                        'message': error_data.get('error_message', error_data.get('message')),
                        'timestamp': error_data.get('timestamp')
                    })
            
            # Sort error types by frequency
            stats['most_common_errors'] = sorted(
                stats['error_types'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return stats
            
        except Exception as e:
            self.error_logger.error(f"Failed to get error statistics: {e}")
            return self._get_local_error_stats(days_back)
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def _get_client_ip(self) -> str:
        """Get client IP address safely"""
        if not request:
            return 'N/A'
        
        # Check for forwarded IP first
        forwarded_ip = request.headers.get('X-Forwarded-For')
        if forwarded_ip:
            return forwarded_ip.split(',')[0].strip()
        
        return request.remote_addr or 'N/A'
    
    def _get_safe_session_data(self) -> Dict[str, Any]:
        """Get safe session data (excluding sensitive information)"""
        if not session:
            return {}
        
        safe_data = {}
        safe_keys = ['student_id', 'current_subject', 'learning_style', 'lesson_progress']
        
        for key in safe_keys:
            if key in session:
                safe_data[key] = session[key]
        
        return safe_data
    
    def _store_error_in_firebase(self, error_data: Dict[str, Any]):
        """Store error data in Firebase"""
        if not self.firestore_client:
            return
        
        try:
            doc_ref = self.firestore_client.collection('error_reports').document(error_data['error_id'])
            doc_ref.set(error_data)
        except Exception as e:
            # Don't let Firebase errors break the application
            print(f"Failed to store error in Firebase: {e}")
    
    def _get_local_error_stats(self, days_back: int) -> Dict[str, Any]:
        """Fallback method to get error stats from local logs"""
        try:
            stats = {
                'total_errors': 0,
                'server_errors': 0,
                'client_errors': 0,
                'error_types': {},
                'most_common_errors': [],
                'recent_errors': []
            }
            
            log_file = 'logs/errors.log'
            if not os.path.exists(log_file):
                return stats
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Simple parsing of recent log entries
            for line in lines[-100:]:  # Check last 100 lines
                if 'Error' in line:
                    stats['total_errors'] += 1
                    if 'Server Error' in line:
                        stats['server_errors'] += 1
                    elif 'Client Error' in line:
                        stats['client_errors'] += 1
            
            return stats
            
        except Exception as e:
            print(f"Failed to get local error stats: {e}")
            return {
                'total_errors': 0,
                'server_errors': 0,
                'client_errors': 0,
                'error_types': {},
                'most_common_errors': [],
                'recent_errors': []
            }

# Global error reporter instance
error_reporter = ErrorReporter()

def handle_server_error(error: Exception, context: Dict[str, Any] = None) -> str:
    """Convenience function to handle server errors"""
    return error_reporter.capture_server_error(error, context)

def handle_client_error(error_data: Dict[str, Any]) -> str:
    """Convenience function to handle client errors"""
    return error_reporter.capture_client_error(error_data)