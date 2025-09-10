<template>
    <div class="profile-container">
        <!-- Отладочные сообщения -->
        <p v-if="isLoading" class="loading-message">Загрузка данных профиля...</p>
        <p v-if="error" class="error-message">{{ error }}</p>

        <!-- Основной макет профиля -->
        <div class="profile-wrapper" v-if="!isLoading && !error">
            <!-- Левая часть: аватарка -->
            <div class="avatar-section">
                <img :src="avatarUrl || defaultAvatar" alt="Аватар" class="avatar-preview" />
                <br />
                <button @click="showAvatarModal = true" class="change-avatar-btn">Сменить аватар</button>
            </div>

            <!-- Правая часть: данные профиля -->
            <div class="user-info">
                <!-- Никнейм -->
                <!-- Форма редактирования никнейма -->
                <div class="username-section">
                    <!-- Режим просмотра -->
                    <h1 style="font-size:30px;color:black" v-if="!isEditingPublicName" class="bio-display">
                        {{ publicName || "Никнейм не задан" }}
                        <button @click="toggleEditPublicName" class="edit-bio-btn">✎</button>
                    </h1>

                    <!-- Режим редактирования -->
                    <div v-else class="bio-edit">
                        <input v-model="newPublicName"
                               @keyup.enter="savePublicName"
                               class="bio-textarea"
                               placeholder="Введите новый никнейм" />
                        <button @click="savePublicName" class="save-bio-btn">Сохранить</button>
                        <p v-if="errors.publicName" class="form-error">{{ errors.publicName }}</p>
                    </div>
                </div>

                <!-- Описание -->
                <div class="bio-section">
                    <p v-if="!isEditingBio" class="bio-display">
                        {{ bio || "Описание отсутствует" }}
                        <button @click="toggleEditBio" class="edit-bio-btn">✎</button>
                    </p>
                    <div v-else class="bio-edit">
                        <textarea v-model="newBio"
                                  @keyup.enter="saveBio"
                                  class="bio-textarea" />
                        <button @click="saveBio" class="save-bio-btn">Сохранить описание</button>
                        <p v-if="errors.bio" class="form-error">{{ errors.bio }}</p>
                    </div>
                </div>

                <!-- Кнопка сменить пароль -->
                <button @click="showPasswordModal = true" class="change-password-btn">Сменить пароль</button>
                
                <div v-if="isAdmin" class="admin-actions">
                    <router-link to="/add-film" class="admin-btn">
                        Добавить фильм
                    </router-link>
                </div>
            </div>

            <!-- Модальное окно: смена аватарки -->
            <div v-if="showAvatarModal" class="modal-overlay" @click.self="closeAvatarModal">
                <div class="modal-content">
                    <span class="modal-close" @click="closeAvatarModal">&times;</span>
                    <h3>Загрузить аватар</h3>
                    <input type="file" @change="handleFileChange" accept="image/*" class="form-input" />
                    <button @click="submitAvatar" class="form-button">Обновить аватар</button>
                    <p v-if="errors.avatar" class="form-error">{{ errors.avatar }}</p>
                </div>
            </div>

            <!-- Модальное окно: смена пароля -->
            <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
                <div class="modal-content">
                    <span class="modal-close" @click="closePasswordModal">&times;</span>
                    <h3>Смена пароля</h3>
                    <form @submit.prevent="submitPassword">
                        <label for="old-password">Старый пароль</label>
                        <input v-model="oldPassword"
                               type="password"
                               id="old-password"
                               class="form-input"
                               required />
                        <p v-if="errors.oldPassword" class="form-error">{{ errors.oldPassword }}</p>

                        <label for="new-password">Новый пароль</label>
                        <input v-model="newPassword"
                               type="password"
                               id="new-password"
                               class="form-input"
                               required />
                        <p v-if="errors.newPassword" class="form-error">{{ errors.newPassword }}</p>

                        <button type="submit" class="form-button">Изменить пароль</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        computed: {
            isAdmin() {
                return this.userData?.is_admin || false;
            }
        },
        data() {
            return {
                userData: {
                    is_admin: false,
                    public_name: "",
                    bio: "",
                    avatar_url: ""
                },
                defaultAvatar: `${this.$axios.defaults.baseURL}/static/default.png`,
                oldPassword: "",
                newPassword: "",
                errors: {},
                isLoading: true,
                error: null,

                // Режимы редактирования
                isEditingPublicName: false,
                isEditingBio: false,
                newPublicName: "",
                newBio: "",

                // Модальные окна
                showAvatarModal: false,
                showPasswordModal: false,
                avatarFile: null
            };
        },
        mounted() {
            this.loadProfile();
        },
        methods: {
            async loadProfile() {
                try {
                    const res = await this.$axios.get("/users/me", {
                        headers: {
                            Authorization: `Bearer ${localStorage.getItem("token")}`
                        }
                    });
                    this.userData = res.data;
                    this.publicName = res.data.public_name || "Никнейм не задан";
                    this.bio = res.data.bio || "Описание отсутствует";
                    this.avatarUrl = res.data.avatar_url || this.defaultAvatar;
                    this.isAdmin = res.data.is_admin; // Теперь должно правильно приходить с бэкенда
                } 
                
                catch (err) {
                    console.error("Ошибка загрузки профиля:", err);
                    this.error = "Не удалось загрузить данные профиля";
                } 
                
                finally {
                    this.isLoading = false;
                }
            },

            // Редактирование никнейма
            toggleEditPublicName() {
                this.isEditingPublicName = !this.isEditingPublicName;
                if (this.isEditingPublicName) {
                    this.newPublicName = this.publicName === "Никнейм не задан" ? "" : this.publicName;
                } else {
                    this.newPublicName = "";
                }
            },

            // Сохранение никнейма
            async savePublicName() {
                if (!this.newPublicName.trim()) {
                    this.errors.publicName = "Никнейм не может быть пустым";
                    return;
                }

                if (this.newPublicName === this.publicName) {
                    this.isEditingPublicName = false;
                    return;
                }

                try {
                    const res = await this.$axios.patch(
                        "/users/me",
                        { public_name: this.newPublicName },
                        {
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            }
                        }
                    );
                    this.publicName = res.data.public_name;
                    this.isEditingPublicName = false;
                    this.errors.publicName = "";
                    alert("Никнейм обновлён");
                } catch (err) {
                    this.errors.publicName = "Не удалось обновить никнейм";
                    this.isEditingPublicName = false;
                }
            },

            // Редактирование описания
            toggleEditBio() {
                this.isEditingBio = !this.isEditingBio;
                if (this.isEditingBio) {
                    this.newBio = this.bio === "Описание отсутствует" ? "" : this.bio;
                }
            },

            async saveBio() {
                try {
                    await this.$axios.patch(
                        "/users/me",
                        { bio: this.newBio },
                        {
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            }
                        }
                    );
                    this.bio = this.newBio || "Описание отсутствует";
                    this.isEditingBio = false;
                    this.errors.bio = "";
                    alert("Описание обновлено");
                } catch (err) {
                    this.errors.bio = "Не удалось обновить описание";
                }
            },

            // Загрузка аватарки
            handleFileChange(e) {
                const file = e.target.files[0];
                if (!file) return;

                // Проверка типа файла
                if (!['image/jpeg', 'image/png'].includes(file.type)) {
                    this.errors.avatar = "Только JPG/PNG изображения";
                    return;
                }

                this.avatarFile = file;
                this.previewImage = URL.createObjectURL(file);
            },

            async submitAvatar() {
                if (!this.avatarFile) {
                    this.errors.avatar = "Выберите файл";
                    return;
                }

                const formData = new FormData();
                formData.append("avatar", this.avatarFile);

                try {
                    const response = await this.$axios.post(
                        "/users/me/avatar",
                        formData,
                        {
                            headers: {
                                "Content-Type": "multipart/form-data",
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            }
                        }
                    );
        
                    this.avatarUrl = response.data.avatar_url;
                    this.showAvatarModal = false;
                    this.$toast.success("Аватар обновлён");
                } catch (error) {
                    this.errors.avatar = error.response?.data?.detail || "Ошибка загрузки";
                    console.error(error);
                }
            },

            // Смена пароля
            async submitPassword() {
                if (!this.newPassword || this.newPassword.length < 8) {
                    this.errors.newPassword = "Пароль должен быть не короче 8 символов";
                    return;
                }

                try {
                    await this.$axios.post(
                        "/users/me/password",
                        {
                            old_password: this.oldPassword,
                            new_password: this.newPassword
                        },
                        {
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            }
                        }
                    );
                    this.oldPassword = "";
                    this.newPassword = "";
                    this.showPasswordModal = false;
                    alert("Пароль изменён");
                } catch (err) {
                    this.errors.oldPassword = "Неверный текущий пароль";
                }
            },

            // Управление модальными окнами
            closeAvatarModal() {
                this.showAvatarModal = false;
                this.avatarFile = null;
                this.errors.avatar = "";
            },
            closePasswordModal() {
                this.showPasswordModal = false;
                this.oldPassword = "";
                this.newPassword = "";
                this.errors.oldPassword = "";
                this.errors.newPassword = "";
            }
        }
    };
</script>


<style scoped>
    img {
        max-height: 95%;
        max-width: 95%
    }
    .avatar-section {
        border-radius: 5%
    }
    .admin-btn {
        display: inline-block;
        margin-top: 20px;
        padding: 10px 15px;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 5px;
    }
    .profile-container {
        padding: 40px 20px;
        background-color: #f9f9f9;
    }

    .profile-wrapper {
        display: flex;
        gap: 40px;
        flex-wrap: wrap;
    }

    .avatar-section {
        flex: 1 1 200px;
        text-align: center;
    }

    .avatar-preview {
        width: 300px;
        height: 300px;
        border-radius: 5%;
        object-fit: cover;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

        .avatar-preview:hover {
            transform: scale(1.05);
        }

    .change-avatar-btn {
        margin-top: 20px;
        padding: 10px 20px;
        background-color: var(--button-default-bg-color, #2176FF);
        color: var(--button-default-color, #fff);
        border: none;
        border-radius: var(--button-radius-medium, 0.375em);
        cursor: pointer;
        transition: background-color 0.3s;
    }

        .change-avatar-btn:hover {
            background-color: var(--button-default-bg-color-hover, #106CFF);
        }

    .user-info {
        flex: 1 1 500px;
        padding: 20px;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }


    .username-section {
        margin-bottom: 20px;
    }

    .username-display {
        font-size: 1.5rem;
        font-weight: bold;
        color: #343E45;
    }

    .edit-username-btn {
        background: transparent;
        border: none;
        font-size: 1.2rem;
        margin-left: 10px;
        cursor: pointer;
        transition: color 0.3s ease;
    }

        .edit-username-btn:hover {
            color: #2176FF;
        }

    .username-edit {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .edit-input {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: var(--button-radius-small, 0.25em);
        font-size: 16px;
    }

    .save-username-btn {
        align-self: flex-start;
        background-color: var(--button-default-bg-color, #2176FF);
        color: var(--button-default-color, #fff);
        border: none;
        padding: 10px 20px;
        border-radius: var(--button-radius-medium, 0.375em);
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .save-username-btn:hover {
        background-color: var(--button-default-bg-color-hover, #106CFF);
    }

    .edit-bio-btn {
        background: transparent;
        border: none;
        font-size: 1.2rem;
        margin-left: 10px;
        cursor: pointer;
        transition: color 0.3s;
    }

    .edit-bio-btn:hover {
            color: var(--button-default-bg-color, #2176FF);
        }

    .bio-edit {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .bio-textarea {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: var(--button-radius-small, 0.25em);
        font-size: 16px;
    }

    .save-bio-btn {
        align-self: flex-start;
        background-color: var(--button-default-bg-color, #2176FF);
        color: var(--button-default-color, #fff);
        border: none;
        padding: 10px 20px;
        border-radius: var(--button-radius-medium, 0.375em);
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .save-bio-btn:hover {
        background-color: var(--button-default-bg-color-hover, #106CFF);
    }

    .bio-display {
        font-size: 1rem;
        color: #666;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .bio-textarea {
        width: 100%;
        height: 100px;
        resize: none;
        font-size: 16px;
    }

    .change-password-btn {
        margin-top: 20px;
        padding: 10px 20px;
        background-color: var(--button-default-bg-color, #2176FF);
        color: var(--button-default-color, #fff);
        border: none;
        border-radius: var(--button-radius-medium, 0.375em);
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

        .change-password-btn:hover {
            background-color: var(--button-default-bg-color-hover, #106CFF);
        }

    /* Модальное окно */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background-color: #fff;
        padding: 30px;
        border-radius: 10px;
        width: 400px;
        position: relative;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .modal-close {
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 1.5rem;
        cursor: pointer;
        color: #000;
    }

    .form-input {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ccc;
        border-radius: var(--button-radius-small, 0.25em);
        font-size: 16px;
    }

    .form-button {
        background-color: var(--button-default-bg-color, #2176FF);
        color: var(--button-default-color, #fff);
        border: none;
        padding: 10px 20px;
        border-radius: var(--button-radius-medium, 0.375em);
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

        .form-button:hover {
            background-color: var(--button-default-bg-color-hover, #106CFF);
        }

    .form-error {
        color: red;
        font-size: 0.9rem;
    }

    .loading-message {
        text-align: center;
        font-size: 1.2rem;
        margin-top: 30px;
    }

    .error-message {
        text-align: center;
        color: red;
        font-size: 1.1rem;
        margin-top: 30px;
    }
</style>