<template>
    <div id="app">
        <header class="nh-topbar">
            <div class="nh-topbar__inner">
                <h1 class="nh-topbar__title"><b>К</b>ино<b>О</b>тзыв</h1>

                <nav class="nh-topbar__nav">
                    <!-- Главная -->
                    <router-link to="/" class="nh-topbar-link">Главная</router-link>

                    <!-- Если не авторизован -->
                    <div v-if="!isLoggedIn" class="nh-topbar__nav">
                        <router-link to="/login" class="nh-topbar-link">Вход</router-link>
                        <router-link to="/register" class="nh-topbar-link">Регистрация</router-link>
                    </div>

                    <!-- Если авторизован -->
                    <div v-else class="nh-topbar__nav">
                        <router-link to="/profile" class="nh-topbar-link">Профиль</router-link>
                        <button @click="logout" class="nh-topbar-link nh-topbar-link--button">
                            <img src="../public/images/logout.png" alt="Выйти" class="exit-png">
                        </button>
                    </div>
                </nav>
            </div>
        </header>
        <main>
            <router-view />
        </main>
        <footer class="nh-footer">
            <div class="nh-footer-columns__inner">
                <div class="nh-footer-columns__column">
                    <div class="nh-footer-columns__section-title">О сайте</div>
                    <ul>
                        <li><a href="/" class="nh-footer-columns__link">Фильмы</a></li>
                    </ul>
                </div>
                <div class="nh-footer-columns__column">
                    <div class="nh-footer-columns__section-title">Контакты</div>
                    <ul>
                        <li><a href="https://mail.google.com/mail/u/0/#inbox?compose=CllgCJvqrzKPbvmDGCwQZBLWVCNkRktkrzKHHmQjDBTzLFFbPbjcLXfRpxvHFLpvDmZfTCZfQRg" class="nh-footer-columns__link">Email</a></li>
                    </ul>
                </div>
            </div>
        </footer>
    </div>
</template>

<script>
    import { onMounted, ref, watch } from 'vue';
    import { useRouter } from 'vue-router';

    export default {
        setup() {
            const router = useRouter();
            const isLoggedIn = ref(false);

            const checkAuth = () => {
                const token = localStorage.getItem("token");
                isLoggedIn.value = !!token;
            };

            const logout = () => {
                localStorage.removeItem("token");
                checkAuth();
                router.push("/");
            };

            watch(() => router.currentRoute.value.path, () => {
                checkAuth();
            });

            onMounted(() => {
                checkAuth();
            });

            return {
                isLoggedIn,
                logout
            };
        }
    };
</script>

<style scoped>
    .nh-topbar__nav {
        display: flex;
        gap: 20px;
    }

    .nh-topbar-link {
        height: 20px;
        padding: 10px 15px;
        border-radius: 8px;
        background-color: #2176FF;
        color: white;
        text-decoration: none;
        font-weight: 500;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }

    .nh-topbar-link:hover {
        background-color: #106CFF;
    }

    /* Стили для кнопки "Выйти" */
    .nh-topbar-link--button {
        
        height: 40px;
        background-color: #808080;
        border: none;
        cursor: pointer;
    }
        .nh-topbar-link--button:hover {
            background-color: white;
        }


    .nh-topbar {
        background-color: #11151C;
        padding: 15px 20px;
        color: white;
        border-radius: 5px
    }

    .nh-topbar__inner {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .nh-topbar__title {
        font-family: 'FontHeader', sans-serif;
        font-size: 25px;
    }

    .nh-topbar__nav {
        display: flex;
        gap: 20px;
    }
    b {
        color: #106CFF
    }

    .nh-footer {
        background-color: #11151C;
        color: white;
        padding: 40px 20px;
    }

    .nh-footer-columns__inner {
        display: flex;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        flex-wrap: wrap;
    }

    .nh-footer-columns__section-title {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .exit-png {
        width: auto;
        height: auto;
        max-height: 20px;
        transition: transform 0.3s ease;
    }

    .exit-png:hover {
        transform: scale(1.1);
    }
</style>