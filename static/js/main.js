/**
 * Main JavaScript file for PaperSummarizer AI
 * Handles client-side interactions, form validations, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormHandlers();
    initializeFileUpload();
    initializeTooltips();
    initializeAnimations();
    initializeKeyboardShortcuts();
    initializeThemePreferences();
});

/**
 * Initialize form submission handlers with loading states
 */
function initializeFormHandlers() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                // Store original button content
                const originalContent = submitButton.innerHTML;
                
                // Show loading state
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                submitButton.disabled = true;
                
                // Show loading spinner if it exists
                const loadingSpinner = document.getElementById('loadingSpinner');
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'block';
                    loadingSpinner.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                // Re-enable form on error (in case of client-side validation failure)
                setTimeout(() => {
                    if (submitButton.disabled) {
                        submitButton.innerHTML = originalContent;
                        submitButton.disabled = false;
                        if (loadingSpinner) {
                            loadingSpinner.style.display = 'none';
                        }
                    }
                }, 30000); // Timeout after 30 seconds
            }
        });
    });
}

/**
 * Initialize file upload handlers with drag and drop support
 */
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const container = input.closest('.tab-pane') || input.closest('.card-body');
        
        if (container) {
            // Add drag and drop functionality
            container.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.stopPropagation();
                container.classList.add('drag-over');
            });
            
            container.addEventListener('dragleave', function(e) {
                e.preventDefault();
                e.stopPropagation();
                container.classList.remove('drag-over');
            });
            
            container.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                container.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    // Filter PDF files
                    const pdfFiles = Array.from(files).filter(file => 
                        file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
                    );
                    
                    if (pdfFiles.length > 0) {
                        // Set files to input
                        const dataTransfer = new DataTransfer();
                        pdfFiles.forEach(file => dataTransfer.items.add(file));
                        input.files = dataTransfer.files;
                        
                        // Trigger change event
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Show success message
                        showToast(`${pdfFiles.length} PDF file(s) selected`, 'success');
                    } else {
                        showToast('Please drop only PDF files', 'warning');
                    }
                }
            });
        }
        
        // File change handler
        input.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                let message = '';
                if (files.length === 1) {
                    message = `Selected: ${files[0].name}`;
                } else {
                    message = `Selected ${files.length} files`;
                }
                
                // Show file selection feedback
                const feedback = this.parentElement.querySelector('.file-feedback') || 
                                document.createElement('div');
                feedback.className = 'file-feedback text-success small mt-2';
                feedback.innerHTML = `<i class="fas fa-check-circle me-1"></i>${message}`;
                
                if (!this.parentElement.querySelector('.file-feedback')) {
                    this.parentElement.appendChild(feedback);
                }
                
                // Validate file sizes
                const maxSize = 10 * 1024 * 1024; // 10MB
                const oversizedFiles = Array.from(files).filter(file => file.size > maxSize);
                
                if (oversizedFiles.length > 0) {
                    showToast(`${oversizedFiles.length} file(s) exceed 10MB limit`, 'warning');
                }
            }
        });
    });
}

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initializeTooltips() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize scroll animations and intersection observers
 */
function initializeAnimations() {
    // Fade in animation for cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);
    
    // Observe cards and feature elements
    const animatedElements = document.querySelectorAll('.card, .feature-card, .process-step, .benefit-item');
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(el);
    });
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeElement = document.activeElement;
            const form = activeElement.closest('form');
            
            if (form && activeElement.tagName === 'TEXTAREA') {
                e.preventDefault();
                form.dispatchEvent(new Event('submit', { bubbles: true }));
            }
        }
        
        // Escape to close modals/alerts
        if (e.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            });
        }
    });
}

/**
 * Initialize theme preferences and local storage
 */
function initializeThemePreferences() {
    // Save and restore tab preferences
    const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            localStorage.setItem('activeTab', e.target.id);
        });
    });
    
    // Restore last active tab
    const lastActiveTab = localStorage.getItem('activeTab');
    if (lastActiveTab) {
        const tabElement = document.getElementById(lastActiveTab);
        if (tabElement) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
        }
    }
    
    // Auto-save form data
    const textInputs = document.querySelectorAll('textarea, input[type="text"], input[type="url"]');
    textInputs.forEach(input => {
        // Restore saved content
        const savedValue = localStorage.getItem(`form_${input.name}`);
        if (savedValue && !input.value) {
            input.value = savedValue;
        }
        
        // Save on input
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                localStorage.setItem(`form_${this.name}`, this.value);
            } else {
                localStorage.removeItem(`form_${this.name}`);
            }
        });
    });
}

/**
 * Show toast notifications
 */
function showToast(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast_' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.id = toastId;
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getIconForType(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Get appropriate icon for toast type
 */
function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Text analysis utilities
 */
const TextAnalyzer = {
    countWords: function(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    },
    
    countSentences: function(text) {
        return text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0).length;
    },
    
    estimateReadingTime: function(text) {
        const wordsPerMinute = 200;
        const words = this.countWords(text);
        return Math.ceil(words / wordsPerMinute);
    },
    
    updateStats: function(textarea, statsElement) {
        const text = textarea.value;
        const words = this.countWords(text);
        const sentences = this.countSentences(text);
        const readingTime = this.estimateReadingTime(text);
        
        statsElement.innerHTML = `
            <small class="text-muted">
                ${text.length} characters • ${words} words • ${sentences} sentences • ~${readingTime} min read
            </small>
        `;
    }
};

/**
 * Form validation utilities
 */
const FormValidator = {
    validateText: function(text, minLength = 50, maxLength = 50000) {
        if (!text || text.trim().length === 0) {
            return { valid: false, message: 'Text cannot be empty' };
        }
        
        const length = text.trim().length;
        if (length < minLength) {
            return { valid: false, message: `Text must be at least ${minLength} characters long` };
        }
        
        if (length > maxLength) {
            return { valid: false, message: `Text cannot exceed ${maxLength} characters` };
        }
        
        return { valid: true, message: 'Text is valid' };
    },
    
    validateURL: function(url) {
        if (!url || url.trim().length === 0) {
            return { valid: false, message: 'URL cannot be empty' };
        }
        
        try {
            // Add protocol if missing
            const testUrl = url.startsWith('http') ? url : 'https://' + url;
            new URL(testUrl);
            return { valid: true, message: 'URL is valid' };
        } catch {
            return { valid: false, message: 'Please enter a valid URL' };
        }
    },
    
    validatePDF: function(file) {
        if (!file) {
            return { valid: false, message: 'No file selected' };
        }
        
        if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
            return { valid: false, message: 'Only PDF files are allowed' };
        }
        
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            return { valid: false, message: 'File size cannot exceed 10MB' };
        }
        
        return { valid: true, message: 'PDF file is valid' };
    }
};

/**
 * Initialize real-time validation for forms
 */
function initializeRealTimeValidation() {
    // Text validation
    const textArea = document.getElementById('textContent');
    if (textArea) {
        const helpText = textArea.nextElementSibling;
        
        textArea.addEventListener('input', function() {
            const validation = FormValidator.validateText(this.value);
            const length = this.value.length;
            
            helpText.textContent = `${length} characters - ${validation.message}`;
            helpText.className = `form-text ${validation.valid ? 'text-success' : 'text-warning'}`;
            
            // Add stats if valid
            if (validation.valid) {
                const statsContainer = this.parentElement.querySelector('.text-stats') || 
                                     document.createElement('div');
                statsContainer.className = 'text-stats mt-2';
                TextAnalyzer.updateStats(this, statsContainer);
                
                if (!this.parentElement.querySelector('.text-stats')) {
                    this.parentElement.appendChild(statsContainer);
                }
            }
        });
    }
    
    // URL validation
    const urlInput = document.getElementById('urlContent');
    if (urlInput) {
        const helpText = urlInput.nextElementSibling;
        
        urlInput.addEventListener('input', function() {
            const validation = FormValidator.validateURL(this.value);
            helpText.textContent = validation.message;
            helpText.className = `form-text ${validation.valid ? 'text-success' : 'text-muted'}`;
        });
    }
    
    // PDF validation
    const pdfInputs = document.querySelectorAll('input[type="file"][accept=".pdf"]');
    pdfInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = Array.from(this.files);
            let validFiles = 0;
            let invalidFiles = 0;
            
            files.forEach(file => {
                const validation = FormValidator.validatePDF(file);
                if (validation.valid) {
                    validFiles++;
                } else {
                    invalidFiles++;
                }
            });
            
            if (files.length > 0) {
                const message = invalidFiles === 0 ? 
                    `${validFiles} valid PDF file(s) selected` :
                    `${validFiles} valid, ${invalidFiles} invalid files`;
                
                showToast(message, invalidFiles === 0 ? 'success' : 'warning');
            }
        });
    });
}

/**
 * Initialize copy to clipboard functionality
 */
function initializeClipboard() {
    // Add copy buttons to summary results
    const summaryContents = document.querySelectorAll('.summary-content');
    summaryContents.forEach(content => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i data-feather="copy"></i>';
        copyBtn.title = 'Copy summary to clipboard';
        
        content.style.position = 'relative';
        content.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', function() {
            const text = content.textContent.trim();
            navigator.clipboard.writeText(text).then(() => {
                this.innerHTML = '<i data-feather="check"></i>';
                setTimeout(() => {
                    this.innerHTML = '<i data-feather="copy"></i>';
                    feather.replace();
                }, 2000);
                showToast('Summary copied to clipboard!', 'success');
            }).catch(() => {
                showToast('Failed to copy to clipboard', 'danger');
            });
        });
    });
    
    // Re-initialize feather icons
    feather.replace();
}

/**
 * Initialize progressive enhancement features
 */
function initializeProgressiveEnhancements() {
    // Auto-expand textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const autoResize = () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        };
        
        textarea.addEventListener('input', autoResize);
        autoResize(); // Initial resize
    });
    
    // Smooth scrolling for internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Initialize real-time validation
    initializeRealTimeValidation();
    
    // Initialize clipboard functionality
    initializeClipboard();
}

// Initialize progressive enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', initializeProgressiveEnhancements);

// Export utilities for global access
window.TextAnalyzer = TextAnalyzer;
window.FormValidator = FormValidator;
window.showToast = showToast;

// Add CSS for drag and drop styling
const style = document.createElement('style');
style.textContent = `
    .drag-over {
        border: 2px dashed var(--bs-primary) !important;
        background-color: rgba(var(--bs-primary-rgb), 0.1) !important;
    }
    
    .animated {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .text-stats {
        padding: 0.5rem;
        background-color: rgba(var(--bs-info-rgb), 0.1);
        border-radius: 0.375rem;
        border-left: 3px solid var(--bs-info);
    }
`;
document.head.appendChild(style);
