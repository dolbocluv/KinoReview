import { createRouter, createWebHistory } from 'vue-router'
import FilmList from './/components/FilmList.vue'
import FilmDetail from './/components/FilmDetail.vue'
import LoginForm from './/components/LoginForm.vue'
import RegisterForm from './/components/RegisterForm.vue'

const routes = [
    { path: '/', component: FilmList },
    { path: '/films/:id', component: FilmDetail },
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router


