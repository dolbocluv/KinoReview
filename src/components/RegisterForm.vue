<template>
    <div class="form-container">
        <h2 class="text-center mb-4">Регистрация</h2>
        <form @submit.prevent="register">
            <div class="form-group">
                <label for="username" class="form-label">Логин</label>
                <input v-model="username"
                       type="text"
                       id="username"
                       class="form-input"
                       required />
                <p v-if="errors.username" class="form-error">{{ errors.username }}</p>
            </div>
            <div class="form-group">
                <label for="password" class="form-label">Пароль</label>
                <input v-model="password"
                       type="password"
                       id="password"
                       class="form-input"
                       required minlength="8" />
                <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
            </div>
            <button type="submit" class="form-button">Зарегистрироваться</button>
            <p class="link"><router-link to="/login">Уже есть аккаунт? Войти</router-link></p>
        </form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                username: "",
                password: "",
                errors: {}
            };
        },
        methods: {
            async register() {
                this.errors = {};
                if (!this.username.trim()) this.errors.username = "Логин не может быть пустым";
                if (this.password.length < 8)
                    this.errors.password = "Пароль должен содержать минимум 8 символов";
                if (Object.keys(this.errors).length > 0) return;

                try {
                    await this.$axios.post("http://localhost:8000/register/", {
                        username: this.username,
                        password: this.password
                    });
                    this.$router.push("/login");
                } catch (err) {
                    this.errors = { general: "Не удалось зарегистрироваться" };
                }
            }
        }
    };
</script>