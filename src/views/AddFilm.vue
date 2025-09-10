<template>
    <div class="add-film-container">
        <h2>Добавить новый фильм</h2>
        <form @submit.prevent="submitFilm" enctype="multipart/form-data">
            <div class="form-group">
                <label>Название фильма</label>
                <input v-model="film.title" required>
            </div>

            <div class="form-group">
                <label>Описание</label>
                <textarea v-model="film.description"></textarea>
            </div>

            <div class="form-group">
                <label>Постер фильма</label>
                <input type="file" @change="handleFileUpload" accept="image/*" required>
                <img v-if="previewImage" :src="previewImage" class="preview-image">
            </div>

            <button type="submit">Добавить фильм</button>
        </form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                film: {
                    title: '',
                    description: ''
                },
                posterFile: null,
                previewImage: null
            }
        },
        methods: {
            handleFileUpload(event) {
                this.posterFile = event.target.files[0];
                this.previewImage = URL.createObjectURL(this.posterFile);
            },
            async submitFilm() {
                const formData = new FormData();
                formData.append('title', this.film.title);
                formData.append('description', this.film.description);
                formData.append('poster', this.posterFile);

                try {
                    await this.$axios.post('/films/with-poster/', formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                            Authorization: `Bearer ${localStorage.getItem('token')}`
                        }
                    });
                    alert('Фильм успешно добавлен');
                    this.$router.push(`/profile`);
                } catch (error) {
                    console.error('Ошибка добавления фильма:', error);
                    alert('Не удалось добавить фильм');
                }
            }
        }
    }
</script>

<style scoped>
    .add-film-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }

    .form-group {
        margin-bottom: 20px;
    }

    input, textarea {
        width: 100%;
        padding: 8px;
        margin-top: 5px;
    }

    .preview-image {
        max-width: 200px;
        max-height: 300px;
        margin-top: 10px;
        display: block;
    }

    button {
        background-color: #2176FF;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
</style>