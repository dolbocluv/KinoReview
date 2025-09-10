import { createRouter, createWebHistory } from 'vue-router'
import FilmList from '../components/FilmList.vue'
import FilmDetail from '../components/FilmDetail.vue'
import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'
import axios from "axios";


const routes = [
    { path: '/', component: FilmList },
    { path: '/films/:id', component: FilmDetail },
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
    { path: '/profile', name: 'UserProfile', component: () => import('../views/UserProfile.vue') },
    { path: "/add-film", name: "AddFilm", component: () => import("../views/AddFilm.vue") },
    {
        path: "/add-film",
        name: "AddFilm",
        component: () => import("../views/AddFilm.vue"),
        meta: { requiresAdmin: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    if (to.meta.requiresAdmin) {
        axios.get('/users/me', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            }
        }).then(response => {
            if (response.data.is_admin) {
                next();
            } else {
                next('/');
            }
        }).catch(() => {
            next('/login');
        });
    } else {
        next();
    }
});

export default router