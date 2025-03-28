<template>
  <div class="home">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-body text-center">
            <h1 class="display-4 my-4">Welcome to Quiz Master V2</h1>
            <p class="lead">
              An interactive quiz platform for educational purposes. Take quizzes, track your progress, and improve your knowledge!
            </p>
            <hr class="my-4">
            <div class="d-flex justify-content-center">
              <router-link :to="{name: 'Login'}" class="btn btn-primary btn-lg me-3">
                <i class="fas fa-sign-in-alt me-2"></i> Login
              </router-link>
              <router-link :to="{name: 'Register'}" class="btn btn-outline-secondary btn-lg">
                <i class="fas fa-user-plus me-2"></i> Register
              </router-link>
            </div>
          </div>
        </div>
        
        <div class="row mt-5">
          <div class="col-md-4">
            <div class="card mb-4">
              <div class="card-body text-center">
                <i class="fas fa-book fa-3x text-primary mb-3"></i>
                <h5 class="card-title">Multiple Subjects</h5>
                <p class="card-text">Access quizzes from various subjects and topics.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card mb-4">
              <div class="card-body text-center">
                <i class="fas fa-tasks fa-3x text-primary mb-3"></i>
                <h5 class="card-title">Track Progress</h5>
                <p class="card-text">Monitor your scores and see your improvement over time.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card mb-4">
              <div class="card-body text-center">
                <i class="fas fa-user-graduate fa-3x text-primary mb-3"></i>
                <h5 class="card-title">Learn & Improve</h5>
                <p class="card-text">Enhance your knowledge through interactive quizzes.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script> 