// main.js - Complete integration with Flask backend

class NTVisionDashboard {
    constructor() {
        this.cameras = {
            "Front Gate Camera": "Front Gate Camera",
            "Main Entrance": "Main Entrance", 
            "Parking Area": "Parking Area",
            "Lobby Camera": "Lobby Camera"
        };
        
        this.currentCamera = 'Front Gate Camera';
        this.isAutoRefresh = true;
        this.refreshInterval = 5000;
        this.charts = {};
        this.notifications = [];
        this.lastUpdateTime = 0;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing NT Vision Dashboard...');
        
        this.initializeEventListeners();
        this.initializeTheme();
        this.initializeNavigation();
        this.initializeClock();
        this.initializeCharts();
        this.setupCameraGrid();
        this.loadInitialData();
        this.startAutoRefresh();
        
        console.log('✅ Dashboard initialized successfully');
    }

    initializeEventListeners() {
        // Toggle Sidebar
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Navigation Links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('href').substring(1);
                this.navigateToPage(target);
            });
        });

        // Export Data
        const exportBtn = document.getElementById('export-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        // Notifications Button
        const notificationsBtn = document.getElementById('notifications');
        if (notificationsBtn) {
            notificationsBtn.addEventListener('click', () => {
                // Reset badge
                const badge = document.getElementById('notification-count');
                if (badge) badge.textContent = '0';

                // Show toast message
                this.showNotification('Notifications panel (coming soon)', 'info');
            });
        }

        // Chart Period Selector Buttons
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = e.target.dataset.period;
                this.updateChartPeriod(period);
            });
        });

        // Modal Close Buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });

        // Detection Search Input
        const searchInput = document.getElementById('detection-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterDetections(e.target.value);
            });
        }

        // Date Filter Input
        const dateFilter = document.getElementById('date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.filterByDate(e.target.value);
            });
        }

        // Video Quality Selector
        const qualitySelector = document.querySelector('.quality-selector');
        if (qualitySelector) {
            qualitySelector.addEventListener('change', (e) => {
                this.changeVideoQuality(e.target.value);
            });
        }

        document.querySelectorAll('.panel-btn').forEach(btn => {
            btn.addEventListener('click', () => this.refreshPanelData());
        });
    }

    setupCameraGrid() {
        const cameraGrid = document.getElementById('camera-grid');
        if (!cameraGrid) return;

        cameraGrid.style.display = 'flex';
        cameraGrid.style.flexDirection = 'row';
        cameraGrid.style.gap = '16px';
        cameraGrid.style.overflowX = 'auto';
        cameraGrid.style.padding = '16px';
        cameraGrid.style.scrollSnapType = 'x mandatory';

        cameraGrid.innerHTML = '';

        Object.keys(this.cameras).forEach((cameraName, index) => {
            const cameraCard = document.createElement('div');
            cameraCard.className = `camera-card ${index === 0 ? 'active' : ''}`;
            cameraCard.dataset.cameraId = cameraName;
            cameraCard.style.minWidth = '220px';
            cameraCard.style.flexShrink = '0';
            cameraCard.style.scrollSnapAlign = 'start';

            cameraCard.innerHTML = `
                <div class="camera-header">
                    <h4>${this.formatCameraName(cameraName)}</h4>
                    <span class="camera-status online">
                        <i class="fas fa-circle"></i>
                        LIVE
                    </span>
                </div>
                <div class="camera-preview">
                    <img src="/video_feed?camera_id=${encodeURIComponent(cameraName)}" 
                        alt="${cameraName}" 
                        onerror="this.src='/api/placeholder/300/200'">
                </div>
            `;

            cameraCard.addEventListener('click', () => {
                this.switchCamera(cameraName);
            });

            cameraGrid.appendChild(cameraCard);
        });

        this.updateMainVideoFeed();
    }

    formatCameraName(cameraName) {
        const nameMap = {
            "Front Gate Camera": "Front Gate",
            "Main Entrance": "Main Entrance",
            "Parking Area": "Parking Lot", 
            "Lobby Camera": "Lobby Area"
        };
        return nameMap[cameraName] || cameraName;
    }

    updateMainVideoFeed() {
        const videoFeed = document.getElementById('main-video-feed');
        if (videoFeed) {
            videoFeed.src = `/video_feed?camera_id=${encodeURIComponent(this.currentCamera)}&t=${Date.now()}`;
            videoFeed.onerror = () => {
                console.warn(`Failed to load video feed for ${this.currentCamera}`);
                videoFeed.src = '/api/placeholder/1280/720';
            };
        }
    }

    initializeTheme() {
        // บังคับธีมมืดเท่านั้น
        document.body.setAttribute('data-theme', 'dark');
    }

    initializeNavigation() {
        this.navigateToPage('dashboard');
    }

    initializeClock() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    }

    initializeCharts() {
        // Initialize analytics chart
        this.initializeAnalyticsChart();
        this.initializeTrendsChart();
        this.initializePerformanceChart();
    }

    initializeAnalyticsChart() {
        const analyticsCanvas = document.getElementById('analytics-chart');
        if (analyticsCanvas) {
            this.charts.analytics = new Chart(analyticsCanvas, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Detections',
                        data: [],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#2563eb',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0, 0, 0, 0.1)' },
                            ticks: { stepSize: 1 }
                        },
                        x: {
                            grid: { color: 'rgba(0, 0, 0, 0.1)' }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
        }
    }

    initializeTrendsChart() {
        const trendsCanvas = document.getElementById('trends-chart');
        if (trendsCanvas) {
            this.charts.trends = new Chart(trendsCanvas, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Daily Detections',
                        data: [0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: '#2563eb',
                        borderRadius: 4,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }
    }

    initializePerformanceChart() {
        const performanceCanvas = document.getElementById('performance-chart');
        if (performanceCanvas) {
            this.charts.performance = new Chart(performanceCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Front Gate', 'Main Entrance', 'Parking Area', 'Lobby'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#2563eb', '#f59e0b', '#10b981', '#06b6d4'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '60%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 20 }
                        }
                    }
                }
            });
        }
    }

    async loadInitialData() {
        try {
            this.showLoadingState(true);
            
            // Load data in parallel
            await Promise.all([
                this.updateSystemStats(),
                this.updateDetections(),
                this.updateCameraStatus(),
                this.updateActivityStream()
            ]);
            
            this.showLoadingState(false);
            this.retryCount = 0; // Reset retry count on success
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.handleDataLoadError(error);
        }
    }

    showLoadingState(isLoading) {
        const loadingElements = document.querySelectorAll('.loading-spinner');
        loadingElements.forEach(el => {
            el.style.display = isLoading ? 'flex' : 'none';
        });
    }

    handleDataLoadError(error) {
        this.retryCount++;
        
        if (this.retryCount < this.maxRetries) {
            console.log(`Retrying data load... (${this.retryCount}/${this.maxRetries})`);
            setTimeout(() => this.loadInitialData(), 2000);
        } else {
            this.showNotification('Unable to load dashboard data. Check your connection.', 'error');
            this.showErrorState(true);
        }
    }

    showErrorState(show) {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(el => {
            el.style.display = show ? 'flex' : 'none';
        });
    }

    async updateSystemStats() {
        try {
            const response = await fetch('/get_system_stats');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const stats = await response.json();
            
            this.updateMetric('cpu', stats.cpu_percent);
            this.updateMetric('memory', stats.memory_percent);
            this.updateMetric('storage', stats.disk_percent);
            
            // Update active cameras
            const activeCameras = document.getElementById('active-cameras');
            if (activeCameras) {
                activeCameras.textContent = `${stats.active_cameras}/${stats.total_cameras}`;
            }
            
            // Update system uptime
            if (stats.uptime) {
                const uptimeElement = document.getElementById('system-uptime');
                if (uptimeElement) {
                    uptimeElement.textContent = this.formatUptime(stats.uptime);
                }
            }
            
        } catch (error) {
            console.error('Error updating system stats:', error);
            this.setDefaultSystemStats();
        }
    }

    updateMetric(type, value) {
        const metricIndex = { cpu: 1, memory: 2, storage: 3 }[type];
        if (!metricIndex) return;

        const fill = document.querySelector(`.metric-item:nth-child(${metricIndex}) .metric-fill`);
        const valueEl = document.querySelector(`.metric-item:nth-child(${metricIndex}) .metric-value`);
        
        if (fill && valueEl) {
            const percentage = Math.round(value);
            fill.style.width = `${percentage}%`;
            valueEl.textContent = `${percentage}%`;
            
            // Update color based on usage
            if (percentage > 80) {
                fill.style.background = 'var(--danger)';
            } else if (percentage > 60) {
                fill.style.background = 'var(--warning)';
            } else {
                fill.style.background = 'var(--success)';
            }
        }
    }

    setDefaultSystemStats() {
        // Set default values when API fails
        this.updateMetric('cpu', 0);
        this.updateMetric('memory', 0);
        this.updateMetric('storage', 0);
        
        const activeCameras = document.getElementById('active-cameras');
        if (activeCameras) activeCameras.textContent = '0/4';
    }

    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `Running ${days}d ${hours}h`;
        if (hours > 0) return `Running ${hours}h ${minutes}m`;
        return `Running ${minutes}m`;
    }

    async updateDetections() {
        try {
            const response = await fetch('/get_all_detections');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Update detection counters
            this.updateDetectionCounters(data.total_counts);
            
            // Update detections table
            this.updateDetectionsTable(data.recent_detections || []);
            
            // Update analytics chart
            this.updateAnalyticsChart(data.recent_detections || []);
            
            // Update performance chart with camera-specific data
            this.updatePerformanceChart(data.total_counts);
            
            this.lastUpdateTime = Date.now();
            
        } catch (error) {
            console.error('Error updating detections:', error);
            this.setDefaultDetectionData();
        }
    }

    updateDetectionCounters(totalCounts) {
        // Update total detections
        const totalDetections = document.getElementById('total-detections');
        if (totalDetections) {
            const total = totalCounts.total || 0;
            this.animateCounter(totalDetections, total);
        }
        
        // Calculate today's detections
        const today = new Date().toISOString().split('T')[0];
        let todayCount = 0;
        
        // You can enhance this by adding a separate API endpoint for today's count
        const todayDetections = document.getElementById('today-detections');
        if (todayDetections) {
            this.animateCounter(todayDetections, todayCount);
        }
    }

    animateCounter(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil((targetValue - currentValue) / 20);
        
        if (currentValue < targetValue) {
            element.textContent = Math.min(currentValue + increment, targetValue);
            setTimeout(() => this.animateCounter(element, targetValue), 50);
        }
    }

    setDefaultDetectionData() {
        const totalDetections = document.getElementById('total-detections');
        const todayDetections = document.getElementById('today-detections');
        
        if (totalDetections) totalDetections.textContent = '0';
        if (todayDetections) todayDetections.textContent = '0';
    }

    updateDetectionsTable(detections) {
        const tbody = document.getElementById('detections-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (detections.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="no-data">
                        <i class="fas fa-search"></i>
                        <p>No detections found</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        detections.forEach(detection => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDateTime(detection.timestamp)}</td>
                <td>${this.formatCameraName(detection.camera_id)}</td>
                <td>
                    <span class="confidence-badge confidence-${this.getConfidenceLevel(detection.confidence)}">
                        ${Math.round(detection.confidence)}%
                    </span>
                </td>
                <td>
                    ${detection.image_path ? 
                        `<img src="/image/${detection.image_path}" class="thumbnail" alt="Detection" onclick="window.ntDashboard.showDetectionModal('${detection.image_path}', '${detection.camera_id}', '${detection.timestamp}', ${detection.confidence})">` : 
                        '<span class="no-data">No image</span>'
                    }
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" title="View Details" onclick="window.ntDashboard.showDetectionModal('${detection.image_path}', '${detection.camera_id}', '${detection.timestamp}', ${detection.confidence})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${detection.image_path ? 
                            `<button class="action-btn download" title="Download" onclick="window.ntDashboard.downloadDetection('${detection.image_path}')">
                                <i class="fas fa-download"></i>
                            </button>` : ''
                        }
                        <button class="action-btn delete" title="Delete" onclick="window.ntDashboard.deleteDetection(${detection.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async updateActivityStream() {
        try {
            const response = await fetch('/get_all_detections');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            const activityStream = document.getElementById('activity-stream');
            if (!activityStream) return;
            
            const recentDetections = data.recent_detections?.slice(0, 5) || [];
            
            if (recentDetections.length === 0) {
                activityStream.innerHTML = `
                    <div class="activity-placeholder">
                        <i class="fas fa-search"></i>
                        <p>Monitoring for activity...</p>
                    </div>
                `;
                return;
            }
            
            activityStream.innerHTML = '';
            
            recentDetections.forEach(detection => {
                const activityItem = document.createElement('div');
                activityItem.className = 'activity-item';
                activityItem.innerHTML = `
                    <div class="activity-icon">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="activity-details">
                        <h4>Person Detected</h4>
                        <p>${this.formatCameraName(detection.camera_id)} - Confidence: ${Math.round(detection.confidence)}%</p>
                        <span class="activity-time">${this.getTimeAgo(detection.timestamp)}</span>
                    </div>
                `;
                activityStream.appendChild(activityItem);
            });
            
        } catch (error) {
            console.error('Error updating activity stream:', error);
            this.setDefaultActivityStream();
        }
    }

    setDefaultActivityStream() {
        const activityStream = document.getElementById('activity-stream');
        if (activityStream) {
            activityStream.innerHTML = `
                <div class="activity-placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load activity data</p>
                </div>
            `;
        }
    }

    updateAnalyticsChart(detections) {
        if (!this.charts.analytics || !detections) return;
        
        const hourlyData = this.groupDetectionsByHour(detections);
        
        this.charts.analytics.data.labels = hourlyData.labels;
        this.charts.analytics.data.datasets[0].data = hourlyData.data;
        this.charts.analytics.update('none'); // No animation for real-time updates
    }

    updatePerformanceChart(totalCounts) {
        if (!this.charts.performance || !totalCounts) return;
        
        const cameraData = [
            totalCounts['Front Gate Camera'] || 0,
            totalCounts['Main Entrance'] || 0,
            totalCounts['Parking Area'] || 0,
            totalCounts['Lobby Camera'] || 0
        ];
        
        this.charts.performance.data.datasets[0].data = cameraData;
        this.charts.performance.update('none');
    }

    groupDetectionsByHour(detections) {
        const hours = [];
        const data = [];
        const now = new Date();
        
        // Generate last 24 hours
        for (let i = 23; i >= 0; i--) {
            const hour = new Date(now.getTime() - (i * 60 * 60 * 1000));
            hours.push(hour.getHours().toString().padStart(2, '0') + ':00');
            data.push(0);
        }
        
        // Count detections for each hour
        detections.forEach(detection => {
            const detectionTime = new Date(detection.timestamp);
            const hoursDiff = Math.floor((now - detectionTime) / (1000 * 60 * 60));
            
            if (hoursDiff >= 0 && hoursDiff < 24) {
                const index = 23 - hoursDiff;
                if (index >= 0 && index < data.length) {
                    data[index]++;
                }
            }
        });
        
        return { labels: hours, data: data };
    }

    async updateCameraStatus() {
        // Update camera grid with live status
        const cameraCards = document.querySelectorAll('.camera-card');
        
        cameraCards.forEach((card) => {
            const statusElement = card.querySelector('.camera-status');
            if (statusElement) {
                statusElement.innerHTML = '<i class="fas fa-circle"></i> LIVE';
                statusElement.className = 'camera-status online';
            }
        });
    }

    switchCamera(cameraName) {
        if (!this.cameras[cameraName]) {
            console.warn(`Camera ${cameraName} not found`);
            return;
        }

        this.currentCamera = cameraName;
        
        // Update active camera indicator
        document.querySelectorAll('.camera-card').forEach(card => {
            card.classList.remove('active');
            if (card.dataset.cameraId === cameraName) {
                card.classList.add('active');
            }
        });
        
        // Update camera name in video overlay
        const cameraNameElement = document.getElementById('active-camera-name');
        if (cameraNameElement) {
            cameraNameElement.textContent = this.formatCameraName(cameraName);
        }
        
        // Update main video feed
        this.updateMainVideoFeed();
        
        // Call backend to switch camera
        fetch(`/switch_camera/${encodeURIComponent(cameraName)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.showNotification(`Switched to ${this.formatCameraName(cameraName)}`, 'success');
                } else {
                    throw new Error(data.message || 'Failed to switch camera');
                }
            })
            .catch(error => {
                console.error('Error switching camera:', error);
                this.showNotification('Error switching camera', 'error');
            });
    }

    // Modal Functions
    showDetectionModal(imagePath, cameraId, timestamp, confidence) {
        const modal = document.getElementById('detection-modal');
        const modalImage = document.getElementById('modal-image');
        const modalTitle = document.getElementById('modal-title');
        const modalDetails = document.getElementById('modal-details');
        
        if (modal && modalImage && modalTitle && modalDetails) {
            modalTitle.textContent = 'Detection Details';
            modalImage.src = imagePath ? `/image/${imagePath}` : '/api/placeholder/400/300';
            
            modalDetails.innerHTML = `
                <div class="detection-details">
                    <h4>Detection Information</h4>
                    <p><strong>Camera:</strong> ${this.formatCameraName(cameraId)}</p>
                    <p><strong>Time:</strong> ${this.formatDateTime(timestamp)}</p>
                    <p><strong>Confidence:</strong> ${Math.round(confidence)}%</p>
                    <p><strong>Status:</strong> <span class="confidence-badge confidence-${this.getConfidenceLevel(confidence)}">${this.getConfidenceText(confidence)}</span></p>
                </div>
            `;
            
            modal.classList.add('active');
        }
    }

    downloadDetection(imagePath) {
        if (imagePath) {
            const link = document.createElement('a');
            link.href = `/image/${imagePath}`;
            link.download = imagePath.split('/').pop();
            link.click();
        }
    }

    async deleteDetection(detectionId) {
        if (!confirm('Are you sure you want to delete this detection?')) return;

        try {
            const response = await fetch(`/delete_detection?id=${detectionId}`, { method: 'DELETE' });
            const result = await response.json();
            if (result.status === 'success') {
                this.showNotification('Detection deleted successfully', 'success');
                this.updateDetections(); // รีเฟรชตาราง
            } else {
                throw new Error(result.message || 'Delete failed');
            }
        } catch (error) {
            console.error('Error deleting detection:', error);
            this.showNotification('Error deleting detection', 'error');
        }
    }


    // UI Control Functions
    toggleSidebar() {
        const sidebar = document.querySelector('.premium-sidebar');
        const mainContent = document.querySelector('.premium-main');
        
        if (sidebar && mainContent) {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Resize charts after sidebar toggle
            setTimeout(() => {
                Object.values(this.charts).forEach(chart => {
                    if (chart && typeof chart.resize === 'function') {
                        chart.resize();
                    }
                });
            }, 300);
        }
    }

    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('nt-vision-theme', newTheme);
        
        this.showNotification(`Switched to ${newTheme} mode`, 'info');
    }

    navigateToPage(pageName) {
        // Hide all content areas
        document.querySelectorAll('.content-area').forEach(area => {
            area.classList.remove('active');
        });
        
        // Show selected content area
        const targetArea = document.getElementById(`${pageName}-content`);
        if (targetArea) {
            targetArea.classList.add('active');
        }
        
        // Update navigation active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[href="#${pageName}"]`)?.closest('.nav-item');
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
        
        // Update page title and breadcrumb
        const pageTitle = document.getElementById('page-title');
        const currentPage = document.getElementById('current-page');
        
        const pageTitles = {
            'dashboard': 'Intelligence Dashboard',
            'surveillance': 'Live Surveillance',
            'detections': 'Detection History',
            'reports': 'Analytics & Reports'
        };
        
        if (pageTitle) pageTitle.textContent = pageTitles[pageName] || pageName;
        if (currentPage) currentPage.textContent = pageTitles[pageName] || pageName;
        
        // Load page-specific data
        this.loadPageData(pageName);
    }

    loadPageData(pageName) {
        switch(pageName) {
            case 'surveillance':
                setTimeout(() => this.setupCameraGrid(), 100);
                this.loadSurveillanceData(); 
                break;
            case 'detections':
                this.loadDetectionHistory();
                break;
            case 'reports':
                this.loadReportsData();
                break;
        }
    }


    loadSurveillanceData() {
        const surveillanceGrid = document.getElementById('surveillance-grid');
        if (!surveillanceGrid) return;

        surveillanceGrid.innerHTML = '';
        
        Object.keys(this.cameras).forEach(cameraName => {
            const cameraCard = document.createElement('div');
            cameraCard.className = 'surveillance-camera-card';
            
            cameraCard.innerHTML = `
                <div class="surveillance-camera-header">
                    <h3>
                        <i class="fas fa-video"></i>
                        ${this.formatCameraName(cameraName)}
                    </h3>
                    <span class="camera-status online">
                        <i class="fas fa-circle"></i>
                        LIVE
                    </span>
                </div>
                <div class="surveillance-camera-feed">
                    <img src="/video_feed?camera_id=${encodeURIComponent(cameraName)}" 
                         alt="${cameraName}"
                         onerror="this.src='/api/placeholder/640/360'">
                </div>
                <div class="surveillance-camera-footer">
                    <div class="camera-stats">
                        <div class="stat-item">
                            <i class="fas fa-users"></i>
                            <span class="stat-value">0</span>
                            <span>Detections</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-clock"></i>
                            <span class="stat-value">24/7</span>
                            <span>Active</span>
                        </div>
                    </div>
                </div>
            `;
            
            surveillanceGrid.appendChild(cameraCard);
        });
    }

    loadDetectionHistory() {
        // Refresh detection data when navigating to detections page
        this.updateDetections();
    }

    loadReportsData() {
        // Initialize or update trends chart with weekly data
        if (this.charts.trends) {
            // Generate sample weekly data (replace with actual API call)
            const weeklyData = this.generateWeeklyData();
            this.charts.trends.data.datasets[0].data = weeklyData;
            this.charts.trends.update();
        }
    }

    generateWeeklyData() {
        // Generate sample data for the week (replace with actual API call)
        return Array.from({length: 7}, () => Math.floor(Math.random() * 50));
    }

    updateClock() {
        const now = new Date();
        
        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('en-US', { hour12: false });
        }
        
        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('en-US', { 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric' 
            });
        }
    }

    updateChartPeriod(period) {
        // Update period button active state
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-period="${period}"]`);
        if (activeBtn) activeBtn.classList.add('active');
        
        // Update chart data based on period
        this.loadChartDataForPeriod(period);
    }

    async loadChartDataForPeriod(period) {
        try {
            // You can implement different API endpoints for different periods
            // For now, we'll use the same endpoint
            const response = await fetch('/get_all_detections');
            const data = await response.json();
            
            let chartData;
            switch(period) {
                case '24h':
                    chartData = this.groupDetectionsByHour(data.recent_detections || []);
                    break;
                case '7d':
                    chartData = this.groupDetectionsByDay(data.recent_detections || [], 7);
                    break;
                case '30d':
                    chartData = this.groupDetectionsByDay(data.recent_detections || [], 30);
                    break;
                default:
                    chartData = this.groupDetectionsByHour(data.recent_detections || []);
            }
            
            if (this.charts.analytics) {
                this.charts.analytics.data.labels = chartData.labels;
                this.charts.analytics.data.datasets[0].data = chartData.data;
                this.charts.analytics.update();
            }
            
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    groupDetectionsByDay(detections, days) {
        const labels = [];
        const data = [];
        const now = new Date();
        
        // Generate labels for the specified number of days
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            data.push(0);
        }
        
        // Count detections for each day
        detections.forEach(detection => {
            const detectionTime = new Date(detection.timestamp);
            const daysDiff = Math.floor((now - detectionTime) / (1000 * 60 * 60 * 24));
            
            if (daysDiff >= 0 && daysDiff < days) {
                const index = days - 1 - daysDiff;
                if (index >= 0 && index < data.length) {
                    data[index]++;
                }
            }
        });
        
        return { labels, data };
    }

    changeVideoQuality(quality) {
        // Update video quality (placeholder - implement based on your streaming setup)
        console.log(`Changing video quality to: ${quality}`);
        this.showNotification(`Video quality changed to ${quality.toUpperCase()}`, 'info');
    }

    refreshPanelData() {
        // Refresh all panel data
        this.updateSystemStats();
        this.updateDetections();
        this.updateActivityStream();
        this.showNotification('Panel data refreshed', 'success');
    }

    async exportData() {
        try {
            this.showNotification('Preparing export...', 'info');
            
            const response = await fetch('/export_csv');
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `nt_telecom_detections_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showNotification('Data exported successfully', 'success');
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Error exporting data', 'error');
        }
    }

    toggleNotifications() {
        // Update notification count
        const notificationBadge = document.getElementById('notification-count');
        if (notificationBadge) {
            const currentCount = parseInt(notificationBadge.textContent) || 0;
            notificationBadge.textContent = currentCount > 0 ? '0' : '3';
        }
        
        this.showNotification('Notifications panel (coming soon)', 'info');
    }

    filterDetections(searchTerm) {
        const rows = document.querySelectorAll('#detections-tbody tr');
        
        rows.forEach(row => {
            if (row.querySelector('.no-data')) return; // Skip "no data" row
            
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    async filterByDate(dateValue) {
        if (!dateValue) {
            this.updateDetections(); // Reset to all detections
            return;
        }
        
        try {
            // You can implement a date-specific endpoint
            const response = await fetch(`/get_detections_by_date?date=${dateValue}`);
            if (response.ok) {
                const data = await response.json();
                this.updateDetectionsTable(data.detections || []);
            }
        } catch (error) {
            console.error('Error filtering by date:', error);
            this.showNotification('Error filtering detections', 'error');
        }
    }



    closeModal() {
        const modals = document.querySelectorAll('.premium-modal.active');
        modals.forEach(modal => modal.classList.remove('active'));
    }

    showNotification(message, type = 'info') {
        // Create notification container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icons[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add close functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
        
        // Limit number of toasts
        const toasts = container.querySelectorAll('.toast');
        if (toasts.length > 5) {
            toasts[0].remove();
        }
    }

    startAutoRefresh() {
        if (this.isAutoRefresh) {
            setInterval(() => {
                // Only refresh if page is visible and not too frequent
                if (document.visibilityState === 'visible' && 
                    Date.now() - this.lastUpdateTime > this.refreshInterval) {
                    
                    this.updateSystemStats();
                    this.updateDetections();
                    this.updateActivityStream();
                }
            }, this.refreshInterval);
        }
    }

    // Utility functions
    formatDateTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`;
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }

    getConfidenceLevel(confidence) {
        if (confidence >= 80) return 'high';
        if (confidence >= 60) return 'medium';
        return 'low';
    }

    getConfidenceText(confidence) {
        if (confidence >= 80) return 'High Confidence';
        if (confidence >= 60) return 'Medium Confidence';
        return 'Low Confidence';
    }

    // Debug and maintenance functions
    debugInfo() {
        return {
            currentCamera: this.currentCamera,
            cameras: this.cameras,
            lastUpdateTime: new Date(this.lastUpdateTime).toLocaleString(),
            chartsInitialized: Object.keys(this.charts).length,
            autoRefresh: this.isAutoRefresh,
            retryCount: this.retryCount
        };
    }

    resetDashboard() {
        // Reset dashboard to initial state
        this.retryCount = 0;
        this.lastUpdateTime = 0;
        this.loadInitialData();
        this.showNotification('Dashboard reset', 'info');
    }

    // Performance monitoring
    measurePerformance(fn, name) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${name} took ${(end - start).toFixed(2)} milliseconds`);
        return result;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ntDashboard = new NTVisionDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && window.ntDashboard) {
        // Refresh data when page becomes visible after being hidden
        setTimeout(() => {
            window.ntDashboard.updateSystemStats();
            window.ntDashboard.updateDetections();
        }, 1000);
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    // Debounce chart resize
    clearTimeout(window.resizeTimeout);
    window.resizeTimeout = setTimeout(() => {
        if (window.ntDashboard && window.ntDashboard.charts) {
            Object.values(window.ntDashboard.charts).forEach(chart => {
                if (chart && typeof chart.resize === 'function') {
                    chart.resize();
                }
            });
        }
    }, 250);
});

// Handle connection errors
window.addEventListener('online', () => {
    if (window.ntDashboard) {
        window.ntDashboard.showNotification('Connection restored', 'success');
        window.ntDashboard.loadInitialData();
    }
});

window.addEventListener('offline', () => {
    if (window.ntDashboard) {
        window.ntDashboard.showNotification('Connection lost', 'warning');
    }
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.ntDashboard) {
        window.ntDashboard.showNotification('An error occurred. Please refresh the page.', 'error');
    }
});

// Export dashboard class for external use
window.NTVisionDashboard = NTVisionDashboard;

// Console helper functions
window.debugDashboard = () => {
    return window.ntDashboard ? window.ntDashboard.debugInfo() : 'Dashboard not initialized';
};

window.resetDashboard = () => {
    if (window.ntDashboard) {
        window.ntDashboard.resetDashboard();
    }
};