<template>
    <h1 style="text-align:center" class="text-center mb-4"><b>Фильмы</b></h1>
    <div class="container">

        <div class="film-grid">
            <router-link v-for="film in films"
                         :key="film.id"
                         :to="`/films/${film.id}`"
                         class="film-card-link">
                <div class="film-card" style="background-color: #11151C;">
                    <img :src="`http://localhost:8000${film.poster_url}`" alt="Постер" class="film-poster" />
                    <div class="film-card-info">
                        <h3 style="border-radius:50px;text-align:center; color:#106CFF" class="film-card-title">{{ film.title }}</h3>
                        <p style="color:white" class="film-card-desc">{{ film.description }}</p>
                    </div>
                </div>
            </router-link>

        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                films: [],
                defaultPoster: `${this.$axios.defaults.baseURL}/static/default-film.png`
            };
        },
        mounted() {
            this.$axios.get("/films/").then(res => {
                this.films = res.data.map(film => ({
                    ...film,
                    poster_url: film.poster_url || this.defaultPoster
                }));
            });
        }
    };
</script>

<style scoped>
    .film-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }

    @media (min-width: 768px) {
        .film-grid {
            grid-template-columns: repeat(5, minmax(200px, 1fr)); /* Фиксировано до 5 */
        }
    }

    @media (max-width: 768px) {
        .film-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        }
    }
</style>