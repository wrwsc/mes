const title = document.getElementById('title');
const authForm = document.getElementById('authForm');
const toggleAuth = document.getElementById('toggleAuth');
const emailInput = document.getElementById('email');
const confirmPasswordInput = document.getElementById('confirmPassword');
let isRegistration = true;

toggleAuth.addEventListener('click', () => {
    isRegistration = !isRegistration;
    if (isRegistration) {
        title.textContent = 'Регистрация';
        toggleAuth.textContent = 'Уже есть аккаунт? Войти';
        emailInput.style.display = 'block';
        confirmPasswordInput.style.display = 'block';
    } else {
        title.textContent = 'Вход';
        toggleAuth.textContent = 'Нет аккаунта? Зарегистрироваться';
        emailInput.style.display = 'none';
        confirmPasswordInput.style.display = 'none';
    }
});

authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (isRegistration) {
        if (password !== confirmPassword) {
            alert('Пароли не совпадают');
            return;
        }
        // Здесь должен быть код для отправки данных регистрации на сервер
        console.log('Регистрация:', { username, email, password });
    } else {
        // Здесь должен быть код для отправки данных авторизации на сервер
        console.log('Вход:', { username, password });
    }
});

// OAuth2 авторизация
document.querySelector('.google').addEventListener('click', () => {
    window.location.href = 'https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=openid%20profile%20email';
});

document.querySelector('.facebook').addEventListener('click', () => {
    window.location.href = 'https://www.facebook.com/v11.0/dialog/oauth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=email,public_profile';
});