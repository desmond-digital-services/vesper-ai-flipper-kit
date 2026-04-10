/**
 * RedWand Admin Dashboard - JavaScript
 * Handles all frontend interactions
 */

const API_BASE = 'http://localhost:5050/api';
let currentOrder = null;
let ordersData = { orders: [], total: 0 };
let currentPage = 1;
const PAGE_SIZE = 20;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Check connection on load
    checkConnection();
    
    // Load orders
    loadOrders();
    
    // Setup navigation
    setupNavigation();
});

function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            showView(view);
        });
    });
}

function showView(viewName) {
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-view="${viewName}"]`)?.classList.add('active');
    
    // Update view visibility
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`${viewName}-view`)?.classList.add('active');
    
    // Load data for view
    if (viewName === 'orders') loadOrders();
    if (viewName === 'reports') loadReports();
}

// ============================================
// API HELPERS
// ============================================

async function apiGet(endpoint) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        // Check content type for CSV
        const contentType = res.headers.get('content-type');
        if (contentType && contentType.includes('text/csv')) {
            return await res.text();
        }
        
        return await res.json();
    } catch (err) {
        console.error(`API Error: ${endpoint}`, err);
        showToast('Failed to fetch data', 'error');
        return null;
    }
}

async function apiPost(endpoint, data) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error(`API Error: ${endpoint}`, err);
        showToast(err.message, 'error');
        return null;
    }
}

async function apiPut(endpoint, data) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error(`API Error: ${endpoint}`, err);
        showToast(err.message, 'error');
        return null;
    }
}

// ============================================
// CONNECTION CHECK
// ============================================

async function checkConnection() {
    const status = document.getElementById('connection-status');
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            status.textContent = '● Connected';
            status.style.color = '#28a745';
        } else {
            throw new Error('Health check failed');
        }
    } catch {
        status.textContent = '● Disconnected';
        status.style.color = '#dc3545';
    }
}

async function testConnection() {
    showLoading(true);
    const connected = await checkConnection();
    showLoading(false);
    showToast(connected ? 'Connected to backend!' : 'Cannot connect to backend', connected ? 'success' : 'error');
}

// ============================================
// ORDERS - LIST VIEW
// ============================================

async function loadOrders() {
    const status = document.getElementById('filter-status').value;
    const payment = document.getElementById('filter-payment').value;
    const search = document.getElementById('search-input').value;
    
    let endpoint = `/orders?limit=${PAGE_SIZE}&offset=${(currentPage - 1) * PAGE_SIZE}`;
    if (status) endpoint += `&status=${status}`;
    if (payment) endpoint += `&payment_status=${payment}`;
    if (search) endpoint += `&search=${encodeURIComponent(search)}`;
    
    showLoading(true);
    const data = await apiGet(endpoint);
    showLoading(false);
    
    if (data) {
        ordersData = data;
        renderOrders(data.orders);
        renderPagination(data.total);
    }
}

function renderOrders(orders) {
    const tbody = document.getElementById('orders-tbody');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8">
                    <div class="empty-state">
                        <div class="empty-icon">📦</div>
                        <h3>No orders found</h3>
                        <p>Try adjusting your filters or search</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = orders.map(order => `
        <tr onclick="viewOrder('${order.order_id}')" style="cursor:pointer;">
            <td><strong>${order.order_id}</strong></td>
            <td>
                ${order.customer_name}<br>
                <span style="font-size:12px;color:#666;">${order.customer_email}</span>
            </td>
            <td>${formatDate(order.order_date)}</td>
            <td><strong>$${order.order_total.toFixed(2)}</strong></td>
            <td><span class="payment-badge ${order.payment_status}">${order.payment_status}</span></td>
            <td><span class="status-badge ${order.order_status}">${order.order_status}</span></td>
            <td>${order.tracking_number || '—'}</td>
            <td onclick="event.stopPropagation();">
                <button class="action-btn view" onclick="viewOrder('${order.order_id}')">View</button>
            </td>
        </tr>
    `).join('');
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / PAGE_SIZE);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">← Prev</button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<span style="padding:0 8px;">...</span>`;
        }
    }
    
    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next →</button>`;
    
    pagination.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadOrders();
}

function handleSearch(event) {
    if (event.key === 'Enter') {
        currentPage = 1;
        loadOrders();
    }
}

// ============================================
// ORDERS - DETAIL VIEW
// ============================================

async function viewOrder(orderId) {
    showLoading(true);
    const order = await apiGet(`/orders/${orderId}`);
    showLoading(false);
    
    if (!order) return;
    
    currentOrder = order;
    document.getElementById('detail-order-id').textContent = order.order_id;
    
    // Customer Info
    document.getElementById('customer-info').innerHTML = `
        <div class="info-item">
            <label>Name</label>
            <span>${order.customer_name}</span>
        </div>
        <div class="info-item">
            <label>Email</label>
            <span>${order.customer_email}</span>
        </div>
        <div class="info-item">
            <label>Phone</label>
            <span>${order.customer_phone || '—'}</span>
        </div>
    `;
    
    // Shipping Address
    let address = order.shipping_address;
    if (typeof address === 'string') {
        try { address = JSON.parse(address); } catch {}
    }
    if (typeof address === 'object' && address) {
        document.getElementById('shipping-info').innerHTML = `
            ${address.street || ''}<br>
            ${address.city || ''}, ${address.state || ''} ${address.zip || ''}<br>
            ${address.country || ''}
        `;
    } else {
        document.getElementById('shipping-info').innerHTML = '—';
    }
    
    // Payment Info
    document.getElementById('payment-info').innerHTML = `
        <div class="info-item">
            <label>Total</label>
            <span>$${order.order_total.toFixed(2)}</span>
        </div>
        <div class="info-item">
            <label>Payment Status</label>
            <span class="payment-badge ${order.payment_status}">${order.payment_status}</span>
        </div>
        <div class="info-item">
            <label>Stripe ID</label>
            <span style="font-size:12px;">${order.stripe_payment_intent_id || '—'}</span>
        </div>
    `;
    
    // Current Status
    document.getElementById('current-status').className = `status-badge ${order.order_status}`;
    document.getElementById('current-status').textContent = order.order_status;
    
    // Status Timeline
    renderStatusTimeline(order.order_status);
    
    // Set status dropdown to current
    document.getElementById('new-status').value = order.order_status;
    
    // Shipping Details
    document.getElementById('shipping-details').innerHTML = `
        <div class="info-item">
            <label>Carrier</label>
            <span>${order.carrier || 'USPS'}</span>
        </div>
        <div class="info-item">
            <label>Tracking</label>
            <span>${order.tracking_number || '—'}</span>
        </div>
        <div class="info-item">
            <label>Ship Date</label>
            <span>${order.ship_date ? formatDate(order.ship_date) : '—'}</span>
        </div>
        <div class="info-item">
            <label>Est. Delivery</label>
            <span>${order.estimated_delivery_date ? formatDate(order.estimated_delivery_date) : '—'}</span>
        </div>
    `;
    
    // Pre-fill tracking fields
    document.getElementById('tracking-input').value = order.tracking_number || '';
    document.getElementById('carrier-input').value = order.carrier || 'USPS';
    
    // Email Log
    renderEmailLog(order.emails || []);
    
    // Procurement
    renderProcurement(order.procurement || []);
    
    // Notes
    renderNotes(order.notes_history || []);
    
    // Show detail view
    showView('detail');
}

function renderStatusTimeline(currentStatus) {
    const statuses = ['pending', 'building', 'testing', 'shipped', 'delivered'];
    const timeline = document.getElementById('status-timeline');
    
    const currentIndex = statuses.indexOf(currentStatus);
    
    timeline.innerHTML = statuses.map((status, index) => {
        let cls = '';
        if (index < currentIndex) cls = 'completed';
        else if (index === currentIndex) cls = 'active';
        
        return `
            <div class="status-step ${cls}">
                <div class="step-icon">${index < currentIndex ? '✓' : index + 1}</div>
                <span class="step-label">${status}</span>
            </div>
        `;
    }).join('');
}

function renderEmailLog(emails) {
    const container = document.getElementById('email-log');
    
    if (!emails.length) {
        container.innerHTML = '<div class="empty-state"><p>No emails sent yet</p></div>';
        return;
    }
    
    container.innerHTML = emails.map(email => `
        <div class="log-item">
            <div>
                <span class="email-type">${email.email_type}</span>
                <div class="email-subject">${email.subject || ''}</div>
            </div>
            <div>
                <span class="email-status ${email.status}">${email.status}</span>
                <div class="email-date">${formatDate(email.sent_date)}</div>
            </div>
        </div>
    `).join('');
}

function renderProcurement(procurement) {
    const container = document.getElementById('procurement-list');
    
    if (!procurement.length) {
        container.innerHTML = '<div class="empty-state"><p>No hardware procurement records</p></div>';
        return;
    }
    
    container.innerHTML = procurement.map(p => `
        <div class="procurement-card">
            <div class="supplier">${p.supplier}</div>
            <div class="item"><strong>${p.item}</strong> × ${p.quantity}</div>
            <div class="cost">$${p.cost.toFixed(2)}</div>
            <div class="tracking">${p.tracking_number || 'No tracking'}</div>
            <span class="status ${p.status}">${p.status}</span>
        </div>
    `).join('');
}

function renderNotes(notes) {
    const container = document.getElementById('notes-list');
    
    if (!notes.length) {
        container.innerHTML = '<div class="empty-state"><p>No notes yet</p></div>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-item">
            <span class="note-type">${note.note_type}</span>
            <div class="note-content">${note.note}</div>
            <div class="note-date">${formatDate(note.created_at)}</div>
        </div>
    `).join('');
}

function showDetailTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = content.id === `tab-${tabName}` ? 'block' : 'none';
    });
}

// ============================================
// ORDER ACTIONS
// ============================================

async function updateStatus() {
    if (!currentOrder) return;
    
    const newStatus = document.getElementById('new-status').value;
    
    showLoading(true);
    const result = await apiPut(`/orders/${currentOrder.order_id}/status`, { order_status: newStatus });
    showLoading(false);
    
    if (result?.success) {
        showToast(`Status updated to ${newStatus}`, 'success');
        viewOrder(currentOrder.order_id);
    }
}

async function addTracking() {
    if (!currentOrder) return;
    
    const tracking = document.getElementById('tracking-input').value.trim();
    const carrier = document.getElementById('carrier-input').value.trim();
    
    if (!tracking) {
        showToast('Tracking number required', 'error');
        return;
    }
    
    showLoading(true);
    const result = await apiPost(`/orders/${currentOrder.order_id}/tracking`, {
        tracking_number: tracking,
        carrier: carrier || 'USPS'
    });
    showLoading(false);
    
    if (result?.success) {
        showToast('Tracking added!', 'success');
        viewOrder(currentOrder.order_id);
    }
}

async function addNote() {
    if (!currentOrder) return;
    
    const noteText = document.getElementById('note-input').value.trim();
    
    if (!noteText) {
        showToast('Note content required', 'error');
        return;
    }
    
    showLoading(true);
    const result = await apiPost(`/orders/${currentOrder.order_id}/notes`, {
        note: noteText,
        note_type: 'manual'
    });
    showLoading(false);
    
    if (result?.success) {
        showToast('Note added!', 'success');
        document.getElementById('note-input').value = '';
        viewOrder(currentOrder.order_id);
    }
}

function showAddProcurement() {
    document.getElementById('procurement-modal').style.display = 'flex';
}

function closeProcurementModal() {
    document.getElementById('procurement-modal').style.display = 'none';
}

async function saveProcurement() {
    if (!currentOrder) return;
    
    const data = {
        order_id: currentOrder.order_id,
        supplier: document.getElementById('proc-supplier').value,
        item: document.getElementById('proc-item').value,
        cost: parseFloat(document.getElementById('proc-cost').value) || 0,
        tracking_number: document.getElementById('proc-tracking').value.trim() || null
    };
    
    showLoading(true);
    const result = await apiPost('/procurement', data);
    showLoading(false);
    
    if (result?.success) {
        showToast('Hardware added!', 'success');
        closeProcurementModal();
        viewOrder(currentOrder.order_id);
    }
}

// ============================================
// EXPORT
// ============================================

async function exportOrders() {
    showLoading(true);
    const csv = await apiGet('/orders/export');
    showLoading(false);
    
    if (csv) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `redwand-orders-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Export downloaded!', 'success');
    }
}

// ============================================
// REPORTS
// ============================================

async function loadReports() {
    showLoading(true);
    
    const [revenue, buildTimes, shipping] = await Promise.all([
        apiGet('/reports/revenue'),
        apiGet('/reports/build-times'),
        apiGet('/reports/shipping')
    ]);
    
    showLoading(false);
    
    if (!revenue) return;
    
    // Summary metrics
    document.getElementById('metric-total').textContent = `$${revenue.total_revenue.toFixed(2)}`;
    document.getElementById('metric-collected').textContent = `$${revenue.collected_revenue.toFixed(2)}`;
    document.getElementById('metric-pending').textContent = `$${revenue.pending_revenue.toFixed(2)}`;
    
    const avgBuildDays = buildTimes?.average_build_days || 0;
    document.getElementById('metric-build-time').textContent = `${avgBuildDays} days`;
    
    // Monthly comparison
    document.getElementById('this-month-rev').textContent = `$${revenue.this_month.toFixed(2)}`;
    document.getElementById('last-month-rev').textContent = `$${revenue.last_month.toFixed(2)}`;
    
    const change = revenue.month_over_month_change;
    const changeEl = document.getElementById('month-change');
    changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
    changeEl.style.color = change >= 0 ? '#28a745' : '#dc3545';
    
    // Shipping stats
    if (shipping) {
        renderShippingStats(shipping);
    }
    
    // Status distribution
    if (buildTimes?.status_distribution) {
        renderStatusChart(buildTimes.status_distribution);
    }
    
    // Default sales chart
    loadSalesChart('day');
}

async function loadSalesChart(period) {
    // Update active button
    document.querySelectorAll('.btn-period').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.period === period);
    });
    
    const salesData = await apiGet(`/reports/sales?period=${period}`);
    
    if (salesData) {
        renderSalesChart(salesData.data, period);
    }
}

function renderSalesChart(data, period) {
    const canvas = document.getElementById('sales-chart');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!data || data.length === 0) {
        ctx.font = '14px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No sales data available', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    const padding = { top: 20, right: 20, bottom: 40, left: 60 };
    const chartWidth = canvas.width - padding.left - padding.right;
    const chartHeight = canvas.height - padding.top - padding.bottom;
    
    // Find max value for scaling
    const maxRevenue = Math.max(...data.map(d => d.revenue || 0), 1);
    
    // Draw bars
    const barWidth = chartWidth / data.length * 0.7;
    const gap = chartWidth / data.length * 0.3;
    
    data.forEach((item, index) => {
        const x = padding.left + (index * (barWidth + gap)) + gap / 2;
        const barHeight = (item.revenue / maxRevenue) * chartHeight;
        const y = padding.top + chartHeight - barHeight;
        
        ctx.fillStyle = '#0066ff';
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Date label
        ctx.save();
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.translate(x + barWidth / 2, padding.top + chartHeight + 15);
        ctx.rotate(-45);
        ctx.fillText(item.date || item.week || item.month, 0, 0);
        ctx.restore();
        
        // Value label
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.fillText(`$${(item.revenue / 1000).toFixed(0)}k`, x + barWidth / 2, y - 5);
    });
    
    // Y-axis
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartHeight / 4) * i;
        const value = Math.round(maxRevenue * (1 - i / 4));
        
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(padding.left + chartWidth, y);
        ctx.stroke();
        
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'right';
        ctx.fillText(`$${(value / 1000).toFixed(0)}k`, padding.left - 5, y + 3);
    }
}

function renderStatusChart(statusDist) {
    const canvas = document.getElementById('status-chart');
    const ctx = canvas.getContext('2d');
    
    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!statusDist || statusDist.length === 0) {
        ctx.font = '14px sans-serif';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No status data', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;
    
    const total = statusDist.reduce((sum, s) => sum + s.count, 0);
    
    let startAngle = -Math.PI / 2;
    
    const colors = {
        'pending': '#6c757d',
        'building': '#17a2b8',
        'testing': '#6610f2',
        'shipped': '#0066ff',
        'delivered': '#28a745'
    };
    
    statusDist.forEach(status => {
        const sliceAngle = (status.count / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[status.order_status] || '#999';
        ctx.fill();
        
        startAngle += sliceAngle;
    });
    
    // Legend
    const legendX = canvas.width - 80;
    let legendY = 20;
    
    statusDist.forEach(status => {
        ctx.fillStyle = colors[status.order_status] || '#999';
        ctx.fillRect(legendX, legendY, 12, 12);
        
        ctx.font = '11px sans-serif';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'left';
        ctx.fillText(`${status.order_status}: ${status.count}`, legendX + 18, legendY + 10);
        
        legendY += 18;
    });
}

function renderShippingStats(shipping) {
    const container = document.getElementById('shipping-stats');
    
    if (!shipping || shipping.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#666;">No shipping data</p>';
        return;
    }
    
    container.innerHTML = shipping.map(s => `
        <div class="stat-item">
            <span class="stat-label">${s.carrier || 'USPS'}</span>
            <span class="stat-value">${s.total_shipped} shipped</span>
        </div>
        <div style="font-size:12px;color:#666;margin-left:12px;">
            ${s.delivered} delivered<br>
            Avg: ${s.avg_delivery_days?.toFixed(1) || '?'} days
        </div>
    `).join('');
}

// ============================================
// UI HELPERS
// ============================================

function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

// ============================================
// CANVAS SETUP (called on load)
// ============================================

window.addEventListener('resize', () => {
    // Re-render charts on resize
    if (document.getElementById('reports-view').classList.contains('active')) {
        loadReports();
    }
});

// Set canvas sizes
document.querySelectorAll('canvas').forEach(canvas => {
    const container = canvas.parentElement;
    if (container) {
        canvas.width = container.clientWidth || 400;
        canvas.height = container.clientHeight || 250;
    }
});