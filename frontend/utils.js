/**
 * 유틸리티 클래스 - 공통 기능 캡슐화
 */
class Formatter {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('ko-KR', {
            style: 'currency',
            currency: 'KRW'
        }).format(amount);
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatDateInput(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toISOString().slice(0, 10);
    }

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

/**
 * UI 관리 클래스 - UI 상태 및 조작 캡슐화
 */
class UIManager {
    static showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    static hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    static showResult(message, type = 'success') {
        const resultEl = document.getElementById('input-result');
        resultEl.textContent = message;
        resultEl.className = `result-message ${type}`;
        resultEl.style.display = 'block';
        
        setTimeout(() => {
            resultEl.style.display = 'none';
        }, 5000);
    }

    static showResultInElement(elementId, message, type = 'error') {
        const resultEl = document.getElementById(elementId);
        if (resultEl) {
            resultEl.textContent = message;
            resultEl.className = `result-message ${type}`;
            resultEl.style.display = 'block';
        }
    }

    static hideResultInElement(elementId) {
        const resultEl = document.getElementById(elementId);
        if (resultEl) {
            resultEl.style.display = 'none';
        }
    }
}

/**
 * 인증 관리 클래스 - 토큰 및 사용자 정보 캡슐화
 */
class AuthManager {
    constructor() {
        this.TOKEN_KEY = 'sseotta_token';
        this.USER_KEY = 'sseotta_user';
        this.REMEMBER_ME_KEY = 'sseotta_remember';
    }

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY) || sessionStorage.getItem(this.TOKEN_KEY);
    }

    setToken(token, rememberMe = false) {
        if (rememberMe) {
            localStorage.setItem(this.TOKEN_KEY, token);
            localStorage.setItem(this.REMEMBER_ME_KEY, 'true');
        } else {
            sessionStorage.setItem(this.TOKEN_KEY, token);
            sessionStorage.removeItem(this.REMEMBER_ME_KEY);
        }
    }

    removeToken() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        localStorage.removeItem(this.REMEMBER_ME_KEY);
        sessionStorage.removeItem(this.TOKEN_KEY);
        sessionStorage.removeItem(this.USER_KEY);
    }

    getUser() {
        const userStr = localStorage.getItem(this.USER_KEY) || sessionStorage.getItem(this.USER_KEY);
        return userStr ? JSON.parse(userStr) : null;
    }

    setUser(user, rememberMe = false) {
        const userStr = JSON.stringify(user);
        if (rememberMe) {
            localStorage.setItem(this.USER_KEY, userStr);
        } else {
            sessionStorage.setItem(this.USER_KEY, userStr);
        }
    }
}

/**
 * API 클라이언트 클래스 - HTTP 요청 캡슐화
 */
class APIClient {
    constructor(baseURL, authManager) {
        this.baseURL = baseURL;
        this.authManager = authManager;
    }

    async call(endpoint, options = {}) {
        try {
            const token = this.authManager.getToken();
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers
            };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers,
                ...options
            });

            if (!response.ok) {
                if (response.status === 401) {
                    if (window.handleLogout) {
                        window.handleLogout();
                    }
                    throw new Error('로그인이 만료되었습니다. 다시 로그인해주세요.');
                }
                const error = await response.json().catch(() => ({ message: '서버 오류가 발생했습니다.' }));
                throw new Error(error.message || '요청 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('API 호출 오류:', error);
            throw error;
        }
    }

    async uploadFile(endpoint, file, options = {}) {
        try {
            const token = this.authManager.getToken();
            const headers = {
                ...options.headers
            };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const formData = new FormData();
            formData.append(options.fieldName || 'file', file);

            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers,
                body: formData
            });

            if (!response.ok) {
                throw new Error('업로드 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('파일 업로드 오류:', error);
            throw error;
        }
    }
}

