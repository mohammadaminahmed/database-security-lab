document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const profileForm = document.getElementById('profile-form');
    const logoutBtn = document.getElementById('logout-btn');
    
    const loginContainer = document.getElementById('login-container');
    const dashboardContainer = document.getElementById('dashboard-container');
    const adminPanel = document.getElementById('admin-panel');
    const resetDbBtn = document.getElementById('reset-db-btn');
    
    let currentUser = null;

    if (resetDbBtn) {
        resetDbBtn.addEventListener('click', async () => {
            if (confirm('هل أنت متأكد أنك تريد إعادة ضبط قاعدة البيانات وحذف جميع الاختراقات؟')) {
                try {
                    const res = await fetch('/api/reset_db', { method: 'POST' });
                    if (res.ok) {
                        alert('✅ تم إعادة ضبط قاعدة البيانات بنجاح!');
                        window.location.reload();
                    }
                } catch (e) {
                    alert('خطأ في الاتصال بالخادم');
                }
            }
        });
    }

    // --- Login Logic ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (res.ok) {
                currentUser = await res.json();
                showDashboard();
            } else {
                alert('خطأ في اسم المستخدم أو كلمة المرور');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('حدث خطأ أثناء الاتصال بالخادم');
        }
    });

    // --- Dashboard Setup ---
    function showDashboard() {
        loginContainer.classList.add('hidden');
        dashboardContainer.classList.remove('hidden');
        
        document.getElementById('display-name').textContent = currentUser.name;
        const roleBadge = document.getElementById('display-role');
        roleBadge.textContent = currentUser.role;
        document.getElementById('edit-name').value = currentUser.name;
        
        // Reset toggles
        document.getElementById('attack-toggle').checked = false;
        document.getElementById('defense-toggle').checked = false;
        document.getElementById('update-msg').textContent = '';

        if (currentUser.role === 'admin') {
            roleBadge.classList.add('admin');
            adminPanel.classList.remove('hidden');
            loadAdminData();
        } else {
            roleBadge.classList.remove('admin');
            adminPanel.classList.add('hidden');
        }
    }

    // --- Logout ---
    logoutBtn.addEventListener('click', () => {
        currentUser = null;
        dashboardContainer.classList.add('hidden');
        loginContainer.classList.remove('hidden');
    });

    // --- Profile Update (The Vulnerability Demo) ---
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const newName = document.getElementById('edit-name').value;
        const isAttackActive = document.getElementById('attack-toggle').checked;
        const isDefenseActive = document.getElementById('defense-toggle').checked;
        const msgEl = document.getElementById('update-msg');

        // Base payload
        const payload = {
            id: currentUser.id,
            name: newName,
            secure_mode: isDefenseActive
        };

        // If attack is active, malicious user injects 'role: admin'
        if (isAttackActive) {
            payload.role = 'admin';
        }

        try {
            const res = await fetch('/api/update_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const updatedUser = await res.json();
                
                if (updatedUser.role === 'admin' && currentUser.role !== 'admin') {
                    msgEl.textContent = '🔥 تم اختراق النظام وتصعيد الصلاحيات بنجاح! يتم الآن الانتقال للوحة الإدارة...';
                    msgEl.className = 'msg error';
                    currentUser = updatedUser;
                    setTimeout(() => { showDashboard(); }, 1500); // Transition directly
                } else if (isDefenseActive) {
                    msgEl.textContent = '🛡️ تم تفعيل الحماية! الخادم تجاهل الصلاحية وقام بتحديث الاسم فقط (Whitelisting).';
                    msgEl.className = 'msg success';
                    currentUser = updatedUser;
                } else {
                    msgEl.textContent = '✅ تم تحديث البيانات بنجاح.';
                    msgEl.className = 'msg success';
                    currentUser = updatedUser;
                }
            }
        } catch (error) {
            console.error('Update error:', error);
            msgEl.textContent = 'حدث خطأ أثناء التحديث';
            msgEl.className = 'msg error';
        }
    });

    // --- Fetch Admin Data ---
    async function loadAdminData() {
        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = '<tr><td colspan="5">جاري جلب البيانات...</td></tr>';
        
        try {
            // In demo, we send role in header. (In real app, backend checks session/token)
            const res = await fetch('/api/users', {
                headers: { 'X-User-Role': currentUser.role }
            });
            
            if (res.ok) {
                const users = await res.json();
                tbody.innerHTML = '';
                users.forEach(u => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${u.id}</td>
                            <td>${u.name}</td>
                            <td><span class="badge ${u.role === 'admin' ? 'admin' : ''}">${u.role}</span></td>
                            <td>${u.salary}</td>
                            <td>${u.performance}</td>
                        </tr>
                    `;
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5">غير مصرح لك برؤية هذه البيانات</td></tr>';
            }
        } catch (error) {
            console.error('Error fetching admin data:', error);
        }
    }
});
