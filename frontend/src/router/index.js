import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects',
    name: 'AdminSubjects',
    component: () => import('../views/admin/Subjects.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters/:subjectId?',
    name: 'AdminChapters',
    component: () => import('../views/admin/Chapters.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    props: true
  },
  {
    path: '/admin/quizzes/:chapterId?',
    name: 'AdminQuizzes',
    component: () => import('../views/admin/Quizzes.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    props: true
  },
  {
    path: '/admin/questions/:quizId?',
    name: 'AdminQuestions',
    component: () => import('../views/admin/Questions.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    props: true
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/statistics',
    name: 'AdminStatistics',
    component: () => import('../views/admin/Statistics.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: () => import('../views/user/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('../views/user/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/subjects',
    name: 'UserSubjects',
    component: () => import('../views/user/Subjects.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/chapters/:subjectId',
    name: 'UserChapters',
    component: () => import('../views/user/Chapters.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/user/quizzes/:chapterId',
    name: 'UserQuizzes',
    component: () => import('../views/user/Quizzes.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/user/take-quiz/:quizId',
    name: 'TakeQuiz',
    component: () => import('../views/user/TakeQuiz.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/user/results/:quizId',
    name: 'QuizResults',
    component: () => import('../views/user/QuizResults.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/user/scores',
    name: 'UserScores',
    component: () => import('../views/user/Scores.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard - proper implementation for Vue 3
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token');
  let isAdmin = false;
  
  try {
    const userData = localStorage.getItem('user');
    isAdmin = userData ? JSON.parse(userData).is_admin : false;
  } catch (e) {
    console.error('Error parsing user data:', e);
  }
  
  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // User is not authenticated, redirect to login
      next({ name: 'Login' });
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      // Route requires admin privileges but user is not admin
      next({ name: 'UserDashboard' });
    } else {
      // User is authenticated (and is admin if required)
      next();
    }
  } else {
    // Route does not require authentication
    if (isAuthenticated && (to.name === 'Login' || to.name === 'Register' || to.name === 'Home')) {
      // User is already authenticated, redirect to appropriate dashboard
      next({ name: isAdmin ? 'AdminDashboard' : 'UserDashboard' });
    } else {
      // Continue as normal
      next();
    }
  }
})

export default router
