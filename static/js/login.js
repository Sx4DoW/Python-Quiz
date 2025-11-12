document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const csrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(csrf ? {'X-CSRF-Token': csrf} : {})
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Login successful!');
                window.location.href = '/';
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            alert('An error occurred. Please try again.');
        }
    });
});