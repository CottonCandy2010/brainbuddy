/**
 * Client-Side Automatic Error Reporting System for Brain Buddy
 * Captures JavaScript errors, network failures, and user experience issues
 */

class ErrorReportingSystem {
    constructor() {
        this.errorQueue = [];
        this.isReporting = false;
        this.maxRetries = 3;
        this.reportingEndpoint = '/api/report-error';
        
        this.initializeErrorHandlers();
        this.startErrorQueueProcessor();
    }
    
    /**
     * Initialize all error capture mechanisms
     */
    initializeErrorHandlers() {
        // Capture uncaught JavaScript errors
        window.addEventListener('error', (event) => {
            this.captureJavaScriptError({
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error ? event.error.stack : null,
                type: 'javascript_error'
            });
        });
        
        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.captureJavaScriptError({
                message: event.reason ? event.reason.toString() : 'Unhandled promise rejection',
                stack: event.reason && event.reason.stack ? event.reason.stack : null,
                type: 'promise_rejection'
            });
        });
        
        // Capture network errors
        this.interceptFetch();
        this.interceptXHR();
        
        // Capture performance issues
        this.monitorPerformance();
        
        console.log('Error reporting system initialized');
    }
    
    /**
     * Capture and queue JavaScript errors
     */
    captureJavaScriptError(errorData) {
        const enhancedError = {
            ...errorData,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            student_context: this.getStudentContext(),
            lesson_context: this.getLessonContext()
        };
        
        this.queueError(enhancedError);
        console.error('JavaScript error captured:', enhancedError);
    }
    
    /**
     * Intercept fetch requests to capture network errors
     */
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async function(...args) {
            try {
                const response = await originalFetch.apply(this, args);
                
                // Report failed HTTP responses
                if (!response.ok) {
                    errorReporter.captureNetworkError({
                        url: args[0],
                        status: response.status,
                        statusText: response.statusText,
                        type: 'fetch_error'
                    });
                }
                
                return response;
            } catch (error) {
                // Report network failures
                errorReporter.captureNetworkError({
                    url: args[0],
                    message: error.message,
                    type: 'network_failure'
                });
                throw error;
            }
        };
    }
    
    /**
     * Intercept XMLHttpRequest to capture network errors
     */
    interceptXHR() {
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._errorReporting = { method, url };
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            this.addEventListener('error', () => {
                if (this._errorReporting) {
                    errorReporter.captureNetworkError({
                        url: this._errorReporting.url,
                        method: this._errorReporting.method,
                        status: this.status,
                        type: 'xhr_error'
                    });
                }
            });
            
            this.addEventListener('load', () => {
                if (this.status >= 400 && this._errorReporting) {
                    errorReporter.captureNetworkError({
                        url: this._errorReporting.url,
                        method: this._errorReporting.method,
                        status: this.status,
                        statusText: this.statusText,
                        type: 'xhr_http_error'
                    });
                }
            });
            
            return originalSend.apply(this, args);
        };
    }
    
    /**
     * Capture network-related errors
     */
    captureNetworkError(errorData) {
        const enhancedError = {
            ...errorData,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            student_context: this.getStudentContext(),
            lesson_context: this.getLessonContext()
        };
        
        this.queueError(enhancedError);
        console.error('Network error captured:', enhancedError);
    }
    
    /**
     * Monitor performance issues
     */
    monitorPerformance() {
        // Monitor slow page loads
        window.addEventListener('load', () => {
            setTimeout(() => {
                const timing = performance.timing;
                const loadTime = timing.loadEventEnd - timing.navigationStart;
                
                if (loadTime > 10000) { // 10 seconds
                    this.capturePerformanceIssue({
                        type: 'slow_page_load',
                        load_time: loadTime,
                        timing: timing
                    });
                }
            }, 1000);
        });
        
        // Monitor memory usage if available
        if (performance.memory) {
            setInterval(() => {
                const memory = performance.memory;
                const memoryUsage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
                
                if (memoryUsage > 0.9) { // 90% memory usage
                    this.capturePerformanceIssue({
                        type: 'high_memory_usage',
                        memory_usage: memoryUsage,
                        used_heap: memory.usedJSHeapSize,
                        total_heap: memory.totalJSHeapSize,
                        heap_limit: memory.jsHeapSizeLimit
                    });
                }
            }, 30000); // Check every 30 seconds
        }
    }
    
    /**
     * Capture performance-related issues
     */
    capturePerformanceIssue(errorData) {
        const enhancedError = {
            ...errorData,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            student_context: this.getStudentContext(),
            lesson_context: this.getLessonContext()
        };
        
        this.queueError(enhancedError);
        console.warn('Performance issue captured:', enhancedError);
    }
    
    /**
     * Get current student context
     */
    getStudentContext() {
        try {
            return {
                student_id: window.currentStudentId || localStorage.getItem('current_student_id') || 'unknown',
                family_id: localStorage.getItem('family_id'),
                selected_avatar: localStorage.getItem('selected_avatar')
            };
        } catch (e) {
            return { student_id: 'unknown' };
        }
    }
    
    /**
     * Get current lesson context
     */
    getLessonContext() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            return {
                subject: urlParams.get('subject'),
                learning_style: urlParams.get('style'),
                topic: urlParams.get('topic'),
                lesson_progress: window.lessonProgress || null
            };
        } catch (e) {
            return {};
        }
    }
    
    /**
     * Add error to processing queue
     */
    queueError(errorData) {
        this.errorQueue.push({
            ...errorData,
            id: this.generateErrorId(),
            retries: 0
        });
        
        // Limit queue size to prevent memory issues
        if (this.errorQueue.length > 50) {
            this.errorQueue.shift(); // Remove oldest error
        }
    }
    
    /**
     * Process error queue and send to server
     */
    startErrorQueueProcessor() {
        setInterval(() => {
            this.processErrorQueue();
        }, 5000); // Process every 5 seconds
    }
    
    /**
     * Process queued errors and send to server
     */
    async processErrorQueue() {
        if (this.isReporting || this.errorQueue.length === 0) {
            return;
        }
        
        this.isReporting = true;
        
        while (this.errorQueue.length > 0) {
            const error = this.errorQueue.shift();
            
            try {
                await this.sendErrorToServer(error);
                console.log(`Error ${error.id} reported successfully`);
            } catch (e) {
                error.retries++;
                
                if (error.retries < this.maxRetries) {
                    // Re-queue for retry
                    this.errorQueue.push(error);
                    console.warn(`Failed to report error ${error.id}, retrying...`);
                } else {
                    console.error(`Failed to report error ${error.id} after ${this.maxRetries} attempts`);
                    this.storeErrorLocally(error);
                }
            }
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        this.isReporting = false;
    }
    
    /**
     * Send error data to server
     */
    async sendErrorToServer(errorData) {
        const response = await fetch(this.reportingEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(errorData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    /**
     * Store error locally when server reporting fails
     */
    storeErrorLocally(errorData) {
        try {
            const storedErrors = JSON.parse(localStorage.getItem('brain_buddy_errors') || '[]');
            storedErrors.push(errorData);
            
            // Limit stored errors
            if (storedErrors.length > 20) {
                storedErrors.shift();
            }
            
            localStorage.setItem('brain_buddy_errors', JSON.stringify(storedErrors));
        } catch (e) {
            console.error('Failed to store error locally:', e);
        }
    }
    
    /**
     * Generate unique error ID
     */
    generateErrorId() {
        return `CLIENT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Manual error reporting for custom errors
     */
    reportCustomError(message, context = {}) {
        this.captureJavaScriptError({
            message: message,
            type: 'custom_error',
            context: context
        });
    }
    
    /**
     * Get locally stored errors
     */
    getStoredErrors() {
        try {
            return JSON.parse(localStorage.getItem('brain_buddy_errors') || '[]');
        } catch (e) {
            return [];
        }
    }
    
    /**
     * Clear locally stored errors
     */
    clearStoredErrors() {
        localStorage.removeItem('brain_buddy_errors');
    }
}

// Initialize global error reporter
const errorReporter = new ErrorReportingSystem();

// Export for use in other scripts
window.errorReporter = errorReporter;