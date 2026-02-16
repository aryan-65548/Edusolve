class AuthService {
    static login(username, password) {
        // Mock credentials - Hardcoded for demo
        if (username === 'student' && password === '123') {
            const user = { username: 'Student', role: 'student' };
            localStorage.setItem('edusolve_user', JSON.stringify(user));
            return { success: true };
        }
        return { success: false, message: 'Invalid username or password' };
    }

    static logout() {
        localStorage.removeItem('edusolve_user');
        window.location.href = 'login.html';
    }

    static getUser() {
        const userStr = localStorage.getItem('edusolve_user');
        return userStr ? JSON.parse(userStr) : null;
    }

    static isAuthenticated() {
        return !!this.getUser();
    }

    static requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
        }
    }

    static redirectIfAuthenticated() {
        if (this.isAuthenticated()) {
            window.location.href = 'index.html';
        }
    }
}
