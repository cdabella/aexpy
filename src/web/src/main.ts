import { createApp } from 'vue'
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { store, key } from './services/store'

import App from './App.vue'
import Home from './pages/Home.vue'
import View from './pages/View.vue'
import DistributionView from './pages/view/Distribution.vue'
import DescriptionView from './pages/view/Description.vue'
import DifferenceView from './pages/view/Difference.vue'
import ReportView from './pages/view/Report.vue'
import ProjectView from './pages/view/Project.vue'
import NotFound from './pages/NotFound.vue'
import { publicModels } from './services/utils'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: Home,
        meta: {
            title: 'Home'
        }
    },
    {
        path: '/view',
        component: View,
        meta: {
            title: 'View'
        }
    },
    {
        path: '/projects',
        redirect: '/'
    },
    {
        path: '/projects/:project',
        component: ProjectView,
        meta: {
            title: 'Projects'
        },
        props: true
    },
    {
        path: '/projects/:project/@:version',
        component: DistributionView,
        meta: {
            title: 'Distributions'
        },
        props: true
    },
    {
        path: '/projects/:project/:version',
        component: DescriptionView,
        meta: {
            title: 'APIs'
        },
        props: true
    },
    {
        path: '/projects/:project/:old..:new',
        component: DifferenceView,
        meta: {
            title: 'Changes'
        },
        props: true
    },
    {
        path: '/projects/:project/:old&:new',
        component: ReportView,
        meta: {
            title: 'Reports'
        },
        props: true
    },
    {
        path: '/:path*',
        component: NotFound,
        meta: {
            title: 'Not Found'
        }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
})

router.beforeEach((to, from) => {
    if (to.path == from.path) {
        return true;
    }
    let params = <{
        id?: string,
    }>to.params;
    let title = (to.meta.title as any).toString() + " - AexPy";
    if (params.id) {
        title = `${params.id} - ${title}`;
    }
    document.title = title;
    return true;
});

const app = createApp(App);
app.use(router).use(store, key);

app.mount('#app')

publicModels();
