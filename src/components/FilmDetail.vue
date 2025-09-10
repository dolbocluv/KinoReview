<template>
    <div class="film-detail-container">
        <div class="film-header">
            <img :src="film.poster_url" alt="Постер" class="film-poster" style="height:100%" />
            <div class="film-info" style="max-width:70%">
                <div class="film-header-info">
                    <h2 class="film-title">{{ film.title }}</h2>
                </div>
                <div class="film-description">
                    <p>{{ film.description }}</p>
                </div>
            </div>
        </div>
        <div v-if="userReview" class="user-review">
            <h4>Ваш отзыв</h4>
            <p><strong>{{ userReview.author_name }}</strong> — {{ formatDate(userReview.created_at) }}</p>
            <p>{{ userReview.text }}</p>
            <button @click="deleteReview" class="delete-button">Удалить отзыв</button>
        </div>

        <div v-if="!userReview" class="review-form">
            <form @submit.prevent="addReview">
                <textarea v-model="text"></textarea>
                <button type="submit">Оставить отзыв</button>
            </form>
        </div>
        <div>
            <h3>Отзывы других пользователей</h3>
            <ul class="review-list" v-if="publicReviews.length > 0">
                <li v-for="review in publicReviews" :key="review.id" class="review-item">
                    <p><strong>{{ review.author_name }}</strong> — {{ formatDate(review.created_at) }}</p>
                    <p>{{ review.text }}</p>
                </li>
            </ul>
            <p v-else class="no-reviews">Пока нет отзывов</p>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                defaultPoster: `${this.$axios.defaults.baseURL}/static/default-film.png`,
                film: {
                    poster_url: '' // Добавляем явное определение поля
                },
                userReview: null,
                publicReviews: [],
                text: "",
                errors: {},
                isLoading: true,
                error: null
            };
        },
        methods: {
            async loadFilm() {
                try {
                    const token = localStorage.getItem("token");
                    const filmRes = await this.$axios.get(`http://localhost:8000/films/${this.$route.params.id}`);
                    this.film = {
                        ...filmRes.data,
                        poster_url: filmRes.data.poster_url ? `http://localhost:8000${filmRes.data.poster_url}` : this.defaultPoster
                    };
                    console.log(`http://localhost:8000${filmRes.data.poster_url}`);
                    const reviewsRes = await this.$axios.get(`/films/${this.$route.params.id}/reviews/`, {
                        headers: token ? { Authorization: `Bearer ${token}` } : {}
                    });

                    this.userReview = reviewsRes.data.user_review || null;
                    this.publicReviews = reviewsRes.data.public_reviews || [];
                } catch (err) {
                    console.error("Ошибка загрузки фильма:", err);
                    this.error = "Не удалось загрузить данные фильма";

                    // Устанавливаем дефолтный постер при ошибке
                    this.film = {
                        title: 'Фильм не найден',
                        description: '',
                        poster_url: this.defaultPoster
                    };
                } finally {
                    this.isLoading = false;
                }
            },

            async deleteReview() {
                if (!confirm("Удалить ваш отзыв?")) return;

                try {
                    await this.$axios.delete(`/films/${this.$route.params.id}/reviews/me`, {
                        headers: {
                            Authorization: `Bearer ${localStorage.getItem("token")}`
                        }
                    });

                    this.userReview = null;
                    this.text = "";
                    await this.loadFilm();
                } catch (err) {
                    console.error("Ошибка удаления отзыва:", err);
                    if (err.response?.status === 401) {
                        this.$router.push("/login");
                    }
                }
            },

            async addReview() {
                if (!this.text.trim()) {
                    this.errors.text = "Поле отзыва не может быть пустым";
                    return;
                }

                try {
                    await this.$axios.post(
                        `/films/${this.$route.params.id}/reviews/`,
                        { text: this.text },
                        {
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            }
                        }
                    );
                    this.text = "";
                    await this.loadFilm();
                } catch (err) {
                    console.error("Ошибка добавления отзыва:", err);
                    if (err.response?.status === 401) {
                        this.$router.push("/login");
                    }
                }
            },

            formatDate(dateString) {
                const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
                return new Date(dateString).toLocaleDateString('ru-RU', options);
            }
        },
        mounted() {
            this.loadFilm();
        }
    };
</script>


<style scoped>
    .film-detail-container {
        max-width: 90%;
        margin: 0 auto;
        padding: 20px;
    }

    .film-header {
        display: flex;
        gap: 20px;
        align-items: center;
        margin-bottom: 30px;
    }

    .film-poster {
        width: 400px;
        height: 300px;
        object-fit: cover;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .film-header-info {
        flex: 1;
    }

    .film-title {
        font-size: 32px;
        margin: 0;
    }

    .film-description {
        margin-top: 20px;
        font-size: 18px;
    }

    .film-reviews {
        margin-top: 30px;
    }

    .user-review {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

        .user-review h4 {
            margin-top: 0;
            margin-bottom: 10px;
        }

    .delete-button {
        background-color: #e74c3c;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        margin-top: 10px;
    }

        .delete-button:hover {
            background-color: #c0392b;
        }

    .review-form textarea {
        width: 100%;
        min-height: 80px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        resize: vertical;
    }

    .review-form button {
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #2176FF;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .review-list {
        list-style: none;
        padding: 0;
        margin-top: 20px;
    }

    .review-item {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    .no-reviews {
        color: #666;
        font-style: italic;
    }
</style>
