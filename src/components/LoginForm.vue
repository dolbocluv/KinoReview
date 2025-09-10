<template>
    <div class="form-container">
        <h2 class="text-center mb-4">Вход</h2>
        <form @submit.prevent="login">
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
                       required />
                <p v-if="errors.password" class="form-error">{{ errors.password }}</p>
            </div>
            <button type="submit" class="form-button">Войти</button>
            <p class="link"><router-link to="/register">Нет аккаунта? Зарегистрироваться</router-link></p>
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
            async login() {
                this.errors = {};
                if (!this.username.trim()) this.errors.username = "Логин не может быть пустым";
                if (!this.password) this.errors.password = "Пароль не может быть пустым";
                if (Object.keys(this.errors).length > 0) return;

                try {
                    const formData = new FormData();
                    formData.append("username", this.username);
                    formData.append("password", this.password);

                    const res = await this.$axios.post("http://localhost:8000/login/", formData, {
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded"
                        }
                    });

                    localStorage.setItem("token", res.data.access_token);
                    this.$router.push("/");
                } catch (err) {
                    this.errors = { general: "Неверный логин или пароль" };
                }
            }
        }
    };
</script>