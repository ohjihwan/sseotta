// API 기본 URL (개발 환경)
const API_BASE_URL = 'http://localhost:8000/api';

// 전역 인스턴스 생성
const authManager = new AuthManager();
const apiClient = new APIClient(API_BASE_URL, authManager);

// 전역 상태 (애플리케이션 상태 관리)
class AppState {
    constructor() {
        this.currentTab = 'input';
        this.currentInputType = 'text';
        this.transactions = [];
        this.categories = [
            '식비', '교통비', '쇼핑', '문화/여가', '의료/건강', '주거/통신', '교육', '기타'
        ];
        this.currentMonth = new Date().toISOString().slice(0, 7);
        this.selectedTransaction = null;
        this.isAuthenticated = false;
        this.user = null;
        this.token = null;
    }

    setAuthenticated(user, token) {
        this.isAuthenticated = true;
        this.user = user;
        this.token = token;
    }

    clearAuth() {
        this.isAuthenticated = false;
        this.user = null;
        this.token = null;
        this.transactions = [];
    }
}

const state = new AppState();

// 하위 호환성을 위한 전역 함수들
const formatCurrency = Formatter.formatCurrency;
const formatDate = Formatter.formatDate;
const formatDateInput = Formatter.formatDateInput;
const showLoading = UIManager.showLoading;
const hideLoading = UIManager.hideLoading;
const showResult = UIManager.showResult;
const getToken = () => authManager.getToken();
const setToken = (token, rememberMe) => authManager.setToken(token, rememberMe);
const removeToken = () => authManager.removeToken();
const getUser = () => authManager.getUser();
const setUser = (user, rememberMe) => authManager.setUser(user, rememberMe);
const apiCall = (endpoint, options) => apiClient.call(endpoint, options);

// 탭 전환
const initTabs = () => {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // 활성 탭 업데이트
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 컨텐츠 표시
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tab}-section`).classList.add('active');
            
            state.currentTab = tab;
            
            // 탭별 초기화
            if (tab === 'transactions') {
                loadTransactions();
            } else if (tab === 'report') {
                initReportMonthSelect();
            }
        });
    });
};

// 입력 방식 탭 전환
const initInputTabs = () => {
    const inputTabButtons = document.querySelectorAll('.input-tab-btn');
    const inputForms = document.querySelectorAll('.input-form');

    inputTabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const inputType = btn.dataset.inputType;
            
            inputTabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            inputForms.forEach(form => form.classList.remove('active'));
            document.getElementById(`${inputType}-input-form`).classList.add('active');
            
            state.currentInputType = inputType;
        });
    });
};

// 텍스트 입력 처리
const initTextInput = () => {
    const textInput = document.getElementById('text-input');
    const submitBtn = document.getElementById('submit-text-btn');

    submitBtn.addEventListener('click', async () => {
        if (!state.isAuthenticated) {
            showResult('로그인이 필요한 기능입니다.', 'error');
            openLoginModal();
            return;
        }

        const text = textInput.value.trim();
        
        if (!text) {
            showResult('소비 내역을 입력해주세요.', 'error');
            return;
        }

        try {
            showLoading();
            submitBtn.disabled = true;
            submitBtn.querySelector('.btn-text').style.display = 'none';
            submitBtn.querySelector('.btn-loader').style.display = 'inline';

            const data = await apiCall('/transactions/text', {
                method: 'POST',
                body: JSON.stringify({ text })
            });

            showResult('소비 내역이 성공적으로 추가되었습니다!', 'success');
            textInput.value = '';
            
            // 거래내역 탭으로 이동
            document.querySelector('.nav-btn[data-tab="transactions"]').click();
        } catch (error) {
            showResult(error.message || '처리 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });

    // Enter 키로 제출 (Shift+Enter는 줄바꿈)
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitBtn.click();
        }
    });
};

// 이미지 업로드 처리
const initImageUpload = () => {
    const imageInput = document.getElementById('image-input');
    const uploadArea = document.getElementById('image-upload-area');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-image-btn');
    const submitBtn = document.getElementById('submit-image-btn');
    const placeholder = uploadArea.querySelector('.upload-placeholder');
    const preview = uploadArea.querySelector('.upload-preview');

    // 클릭으로 파일 선택
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    // 드래그 앤 드롭
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-color)';
        uploadArea.style.background = 'rgba(99, 102, 241, 0.1)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--gray-300)';
        uploadArea.style.background = 'var(--gray-50)';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--gray-300)';
        uploadArea.style.background = 'var(--gray-50)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageFile(files[0]);
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageFile(e.target.files[0]);
        }
    });

    const handleImageFile = (file) => {
        if (!file.type.startsWith('image/')) {
            showResult('이미지 파일만 업로드 가능합니다.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            placeholder.style.display = 'none';
            preview.style.display = 'block';
            submitBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    };

    removeBtn.addEventListener('click', () => {
        imageInput.value = '';
        placeholder.style.display = 'flex';
        preview.style.display = 'none';
        submitBtn.disabled = true;
    });

    submitBtn.addEventListener('click', async () => {
        if (!state.isAuthenticated) {
            showResult('로그인이 필요한 기능입니다.', 'error');
            openLoginModal();
            return;
        }

        if (!imageInput.files || imageInput.files.length === 0) {
            showResult('이미지를 선택해주세요.', 'error');
            return;
        }

        try {
            showLoading();
            submitBtn.disabled = true;
            submitBtn.querySelector('.btn-text').style.display = 'none';
            submitBtn.querySelector('.btn-loader').style.display = 'inline';

            const formData = new FormData();
            formData.append('image', imageInput.files[0]);

            const data = await fetch(`${API_BASE_URL}/transactions/image`, {
                method: 'POST',
                body: formData
            }).then(res => {
                if (!res.ok) throw new Error('업로드 실패');
                return res.json();
            });

            showResult('영수증이 성공적으로 분석되었습니다!', 'success');
            imageInput.value = '';
            placeholder.style.display = 'flex';
            preview.style.display = 'none';
            submitBtn.disabled = true;
            
            document.querySelector('.nav-btn[data-tab="transactions"]').click();
        } catch (error) {
            showResult(error.message || '이미지 분석 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });
};

// 파일 업로드 처리
const initFileUpload = () => {
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('file-upload-area');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const removeBtn = document.getElementById('remove-file-btn');
    const submitBtn = document.getElementById('submit-file-btn');
    const placeholder = uploadArea.querySelector('.upload-placeholder');
    const preview = uploadArea.querySelector('.upload-preview');

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-color)';
        uploadArea.style.background = 'rgba(99, 102, 241, 0.1)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--gray-300)';
        uploadArea.style.background = 'var(--gray-50)';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--gray-300)';
        uploadArea.style.background = 'var(--gray-50)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    const handleFile = (file) => {
        const validExtensions = ['.csv', '.xlsx', '.xls'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validExtensions.includes(fileExt)) {
            showResult('CSV, XLSX, XLS 파일만 업로드 가능합니다.', 'error');
            return;
        }

        fileName.textContent = file.name;
        fileSize.textContent = Formatter.formatFileSize(file.size);
        placeholder.style.display = 'none';
        preview.style.display = 'flex';
        submitBtn.disabled = false;
    };

    removeBtn.addEventListener('click', () => {
        fileInput.value = '';
        placeholder.style.display = 'flex';
        preview.style.display = 'none';
        submitBtn.disabled = true;
    });

    submitBtn.addEventListener('click', async () => {
        if (!state.isAuthenticated) {
            showResult('로그인이 필요한 기능입니다.', 'error');
            openLoginModal();
            return;
        }

        if (!fileInput.files || fileInput.files.length === 0) {
            showResult('파일을 선택해주세요.', 'error');
            return;
        }

        try {
            showLoading();
            submitBtn.disabled = true;
            submitBtn.querySelector('.btn-text').style.display = 'none';
            submitBtn.querySelector('.btn-loader').style.display = 'inline';

            const data = await apiClient.uploadFile(
                '/transactions/file',
                fileInput.files[0],
                { fieldName: 'file' }
            );

            showResult(`${data.count || 0}건의 거래가 성공적으로 추가되었습니다!`, 'success');
            fileInput.value = '';
            placeholder.style.display = 'flex';
            preview.style.display = 'none';
            submitBtn.disabled = true;
            
            document.querySelector('.nav-btn[data-tab="transactions"]').click();
        } catch (error) {
            showResult(error.message || '파일 처리 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });
};

// 거래내역 로드
const loadTransactions = async () => {
    if (!state.isAuthenticated) {
        const tbody = document.getElementById('transactions-tbody');
        tbody.innerHTML = '<tr class="empty-row"><td colspan="6">로그인이 필요한 기능입니다. 로그인해주세요.</td></tr>';
        return;
    }

    try {
        showLoading();
        const month = document.getElementById('month-filter').value;
        const category = document.getElementById('category-filter').value;
        
        let url = '/transactions';
        const params = new URLSearchParams();
        if (month) params.append('month', month);
        if (category) params.append('category', category);
        if (params.toString()) url += '?' + params.toString();

        const data = await apiCall(url);
        state.transactions = data.transactions || [];
        
        renderTransactions();
        updateStatistics();
    } catch (error) {
        console.error('거래내역 로드 오류:', error);
        showResult('거래내역을 불러오는 중 오류가 발생했습니다.', 'error');
    } finally {
        hideLoading();
    }
};

// 거래내역 렌더링
const renderTransactions = () => {
    const tbody = document.getElementById('transactions-tbody');
    
    if (state.transactions.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="6">거래 내역이 없습니다. 소비 내역을 입력해주세요.</td></tr>';
        return;
    }

    tbody.innerHTML = state.transactions.map(transaction => `
        <tr>
            <td>${formatDate(transaction.date)}</td>
            <td class="amount">${formatCurrency(transaction.amount)}</td>
            <td><span class="category-badge ${transaction.category}">${transaction.category}</span></td>
            <td>${transaction.description || '-'}</td>
            <td>${transaction.merchant || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon" onclick="editTransaction('${transaction._id}')" title="수정">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
};

// 통계 업데이트
const updateStatistics = () => {
    const currentMonth = new Date().toISOString().slice(0, 7);
    const monthTransactions = state.transactions.filter(t => 
        new Date(t.date).toISOString().slice(0, 7) === currentMonth
    );
    
    const total = monthTransactions.reduce((sum, t) => sum + t.amount, 0);
    const count = monthTransactions.length;
    const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate();
    const dailyAverage = count > 0 ? Math.round(total / daysInMonth) : 0;

    document.getElementById('total-spending').textContent = formatCurrency(total);
    document.getElementById('transaction-count').textContent = `${count}건`;
    document.getElementById('daily-average').textContent = formatCurrency(dailyAverage);
};

// 필터 초기화
const initFilters = () => {
    const monthFilter = document.getElementById('month-filter');
    const categoryFilter = document.getElementById('category-filter');

    // 월 필터 옵션 생성 (최근 12개월)
    const months = [];
    for (let i = 0; i < 12; i++) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        const monthStr = date.toISOString().slice(0, 7);
        const monthLabel = date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
        months.push({ value: monthStr, label: monthLabel });
    }

    months.forEach(month => {
        const option = document.createElement('option');
        option.value = month.value;
        option.textContent = month.label;
        monthFilter.appendChild(option);
    });

    // 카테고리 필터 옵션 생성
    state.categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });

    monthFilter.addEventListener('change', loadTransactions);
    categoryFilter.addEventListener('change', loadTransactions);
};

// 거래 수정
const editTransaction = async (id) => {
    const transaction = state.transactions.find(t => t._id === id);
    if (!transaction) return;

    state.selectedTransaction = transaction;

    // 모달 폼 채우기
    document.getElementById('edit-date').value = formatDateInput(transaction.date);
    document.getElementById('edit-amount').value = transaction.amount;
    document.getElementById('edit-description').value = transaction.description || '';
    document.getElementById('edit-merchant').value = transaction.merchant || '';

    // 카테고리 옵션 채우기
    const categorySelect = document.getElementById('edit-category');
    categorySelect.innerHTML = state.categories.map(cat => 
        `<option value="${cat}" ${cat === transaction.category ? 'selected' : ''}>${cat}</option>`
    ).join('');

    // 모달 표시
    document.getElementById('transaction-modal').style.display = 'flex';
};

// 모달 닫기
const closeModal = () => {
    document.getElementById('transaction-modal').style.display = 'none';
    state.selectedTransaction = null;
};

// 거래 수정/삭제 처리
const initTransactionModal = () => {
    const modal = document.getElementById('transaction-modal');
    const closeBtn = document.getElementById('close-modal-btn');
    const form = document.getElementById('edit-transaction-form');
    const deleteBtn = document.getElementById('delete-transaction-btn');

    closeBtn.addEventListener('click', closeModal);
    modal.querySelector('.modal-overlay').addEventListener('click', closeModal);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!state.selectedTransaction) return;

        try {
            showLoading();
            const formData = {
                date: document.getElementById('edit-date').value,
                amount: parseFloat(document.getElementById('edit-amount').value),
                category: document.getElementById('edit-category').value,
                description: document.getElementById('edit-description').value,
                merchant: document.getElementById('edit-merchant').value
            };

            await apiCall(`/transactions/${state.selectedTransaction._id}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });

            showResult('거래가 성공적으로 수정되었습니다.', 'success');
            closeModal();
            loadTransactions();
        } catch (error) {
            showResult(error.message || '수정 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
        }
    });

    deleteBtn.addEventListener('click', async () => {
        if (!state.selectedTransaction) return;
        if (!confirm('정말 이 거래를 삭제하시겠습니까?')) return;

        try {
            showLoading();
            await apiCall(`/transactions/${state.selectedTransaction._id}`, {
                method: 'DELETE'
            });

            showResult('거래가 성공적으로 삭제되었습니다.', 'success');
            closeModal();
            loadTransactions();
        } catch (error) {
            showResult(error.message || '삭제 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
        }
    });
};

// 리포트 월 선택 초기화
const initReportMonthSelect = () => {
    const select = document.getElementById('report-month-select');
    select.innerHTML = '';

    // 최근 12개월
    for (let i = 0; i < 12; i++) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        const monthStr = date.toISOString().slice(0, 7);
        const monthLabel = date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
        
        const option = document.createElement('option');
        option.value = monthStr;
        option.textContent = monthLabel;
        if (i === 0) option.selected = true;
        select.appendChild(option);
    }
};

// 리포트 생성
const initReport = () => {
    const generateBtn = document.getElementById('generate-report-btn');
    
    generateBtn.addEventListener('click', async () => {
        if (!state.isAuthenticated) {
            showResult('로그인이 필요한 기능입니다.', 'error');
            openLoginModal();
            return;
        }

        const month = document.getElementById('report-month-select').value;
        if (!month) {
            showResult('월을 선택해주세요.', 'error');
            return;
        }

        try {
            showLoading();
            const data = await apiCall(`/reports/generate?month=${month}`);
            renderReport(data);
        } catch (error) {
            showResult(error.message || '리포트 생성 중 오류가 발생했습니다.', 'error');
        } finally {
            hideLoading();
        }
    });
};

// 리포트 렌더링
const renderReport = (report) => {
    const content = document.getElementById('report-content');
    
    if (!report) {
        content.innerHTML = '<div class="empty-state"><p>리포트 데이터가 없습니다.</p></div>';
        return;
    }

    const categoryBreakdown = Object.entries(report.category_breakdown || {})
        .map(([category, data]) => `
            <div class="summary-card">
                <h4>${category}</h4>
                <div class="value">${formatCurrency(data.amount)}</div>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--gray-600);">
                    ${data.percentage.toFixed(1)}% (${data.count}건)
                </div>
            </div>
        `).join('');

    const insights = (report.insights || []).map(insight => `
        <div class="insight-item ${insight.type}">
            ${insight.message}
        </div>
    `).join('');

    const comparison = report.comparison || {};
    const changePercent = comparison.change_percentage || 0;
    const changeClass = changePercent > 0 ? 'warning' : changePercent < 0 ? 'success' : 'info';
    const changeIcon = changePercent > 0 ? '↑' : changePercent < 0 ? '↓' : '→';

    content.innerHTML = `
        <div class="report-summary">
            <h3>${new Date(report.month + '-01').toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })} 리포트</h3>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h4>총 소비 금액</h4>
                    <div class="value">${formatCurrency(report.total_spending)}</div>
                </div>
                <div class="summary-card">
                    <h4>전월 대비</h4>
                    <div class="value" style="color: ${changePercent > 0 ? 'var(--warning-color)' : changePercent < 0 ? 'var(--success-color)' : 'var(--info-color)'};">
                        ${changeIcon} ${Math.abs(changePercent).toFixed(1)}%
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--gray-600);">
                        전월: ${formatCurrency(comparison.previous_month_total || 0)}
                    </div>
                </div>
            </div>

            <div class="summary-grid" style="margin-top: 1rem;">
                ${categoryBreakdown}
            </div>
        </div>

        ${insights ? `
            <div class="insights-list">
                <h3 style="margin-bottom: 1rem;">AI 인사이트</h3>
                ${insights}
            </div>
        ` : ''}
    `;
};

// 인증 관련 함수
const checkAuth = () => {
    const token = authManager.getToken();
    const user = authManager.getUser();
    
    if (token && user) {
        state.setAuthenticated(user, token);
        updateAuthUI();
        return true;
    }
    return false;
};

const updateAuthUI = () => {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const userName = document.getElementById('user-name');
    
    if (state.isAuthenticated && state.user) {
        authButtons.style.display = 'none';
        userMenu.style.display = 'flex';
        userName.textContent = state.user.name || state.user.email;
    } else {
        authButtons.style.display = 'flex';
        userMenu.style.display = 'none';
    }
};

const handleLogin = async (email, password, rememberMe) => {
    try {
        showLoading();
        const data = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (data.token && data.user) {
            authManager.setToken(data.token, rememberMe);
            authManager.setUser(data.user, rememberMe);
            state.setAuthenticated(data.user, data.token);
            
            updateAuthUI();
            closeLoginModal();
            showResult('로그인에 성공했습니다!', 'success');
            
            // 데이터 새로고침
            if (state.currentTab === 'transactions') {
                loadTransactions();
            }
        }
    } catch (error) {
        const resultEl = document.getElementById('login-result');
        resultEl.textContent = error.message || '로그인에 실패했습니다.';
        resultEl.className = 'result-message error';
        resultEl.style.display = 'block';
        throw error;
    } finally {
        hideLoading();
    }
};

const handleSignup = async (name, email, password) => {
    try {
        showLoading();
        const data = await apiCall('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });

        showResult('회원가입에 성공했습니다! 로그인해주세요.', 'success');
        closeSignupModal();
        
        // 로그인 모달로 전환
        setTimeout(() => {
            document.getElementById('login-btn').click();
            document.getElementById('login-email').value = email;
        }, 1000);
    } catch (error) {
        const resultEl = document.getElementById('signup-result');
        resultEl.textContent = error.message || '회원가입에 실패했습니다.';
        resultEl.className = 'result-message error';
        resultEl.style.display = 'block';
        throw error;
    } finally {
        hideLoading();
    }
};

const handleLogout = () => {
    authManager.removeToken();
    state.clearAuth();
    
    updateAuthUI();
    
    // 메인 탭으로 이동
    document.querySelector('.nav-btn[data-tab="input"]').click();
    
    // 거래내역 초기화
    const tbody = document.getElementById('transactions-tbody');
    tbody.innerHTML = '<tr class="empty-row"><td colspan="6">거래 내역이 없습니다. 소비 내역을 입력해주세요.</td></tr>';
    
    showResult('로그아웃되었습니다.', 'info');
};

const openLoginModal = () => {
    document.getElementById('login-modal').style.display = 'flex';
    document.getElementById('login-email').focus();
};

const closeLoginModal = () => {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('login-form').reset();
    document.getElementById('login-result').style.display = 'none';
};

const openSignupModal = () => {
    document.getElementById('signup-modal').style.display = 'flex';
    document.getElementById('signup-name').focus();
};

const closeSignupModal = () => {
    document.getElementById('signup-modal').style.display = 'none';
    document.getElementById('signup-form').reset();
    document.getElementById('signup-result').style.display = 'none';
};

// 인증 모달 초기화
const initAuth = () => {
    // 로그인 버튼
    document.getElementById('login-btn').addEventListener('click', openLoginModal);
    document.getElementById('close-login-modal-btn').addEventListener('click', closeLoginModal);
    document.querySelector('#login-modal .modal-overlay').addEventListener('click', closeLoginModal);

    // 회원가입 버튼
    document.getElementById('signup-btn').addEventListener('click', openSignupModal);
    document.getElementById('close-signup-modal-btn').addEventListener('click', closeSignupModal);
    document.querySelector('#signup-modal .modal-overlay').addEventListener('click', closeSignupModal);

    // 모달 간 전환
    document.getElementById('switch-to-signup').addEventListener('click', (e) => {
        e.preventDefault();
        closeLoginModal();
        setTimeout(openSignupModal, 200);
    });

    document.getElementById('switch-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        closeSignupModal();
        setTimeout(openLoginModal, 200);
    });

    // 로그인 폼 제출
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        if (!email || !password) {
            const resultEl = document.getElementById('login-result');
            resultEl.textContent = '이메일과 비밀번호를 입력해주세요.';
            resultEl.className = 'result-message error';
            resultEl.style.display = 'block';
            return;
        }

        try {
            await handleLogin(email, password, rememberMe);
        } catch (error) {
            // 에러는 handleLogin에서 처리됨
        }
    });

    // 회원가입 폼 제출
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value;
        const passwordConfirm = document.getElementById('signup-password-confirm').value;

        if (!name || !email || !password || !passwordConfirm) {
            const resultEl = document.getElementById('signup-result');
            resultEl.textContent = '모든 필드를 입력해주세요.';
            resultEl.className = 'result-message error';
            resultEl.style.display = 'block';
            return;
        }

        if (password.length < 8) {
            const resultEl = document.getElementById('signup-result');
            resultEl.textContent = '비밀번호는 8자 이상이어야 합니다.';
            resultEl.className = 'result-message error';
            resultEl.style.display = 'block';
            return;
        }

        if (password !== passwordConfirm) {
            const resultEl = document.getElementById('signup-result');
            resultEl.textContent = '비밀번호가 일치하지 않습니다.';
            resultEl.className = 'result-message error';
            resultEl.style.display = 'block';
            return;
        }

        try {
            await handleSignup(name, email, password);
        } catch (error) {
            // 에러는 handleSignup에서 처리됨
        }
    });

    // 로그아웃 버튼
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
};

// 전역 함수로 내보내기 (HTML에서 호출하기 위해)
window.editTransaction = editTransaction;

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 인증 초기화 (먼저 실행)
    initAuth();
    checkAuth();
    updateAuthUI();

    initTabs();
    initInputTabs();
    initTextInput();
    initImageUpload();
    initFileUpload();
    initFilters();
    initTransactionModal();
    initReport();
    
    // 인증된 경우에만 데이터 로드
    if (state.isAuthenticated) {
        loadTransactions();
    }
});

