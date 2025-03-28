<template>
  <div class="admin-quizzes">
    <h1 class="mb-4">Manage Quizzes</h1>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Chapter: {{ chapterName }}</h3>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="fas fa-plus me-2"></i> Add Quiz
      </button>
    </div>
    
    <!-- Alerts -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error!</strong> {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>
    
    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
      <strong>Success!</strong> {{ successMessage }}
      <button type="button" class="btn-close" @click="successMessage = null"></button>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading quizzes...</p>
    </div>
    
    <!-- No quizzes available -->
    <div v-else-if="quizzes.length === 0" class="text-center py-5">
      <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
      <h3>No Quizzes Available</h3>
      <p class="text-muted">Click the "Add Quiz" button to create your first quiz for this chapter.</p>
    </div>
    
    <!-- Quizzes list -->
    <div v-else class="card shadow">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Duration</th>
                <th>Questions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in quizzes" :key="quiz.id">
                <td>{{ quiz.id }}</td>
                <td>{{ quiz.title }}</td>
                <td>{{ quiz.description }}</td>
                <td>{{ quiz.duration }} mins</td>
                <td>{{ quiz.question_count || quiz.questionCount || 0 }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link :to="{name: 'AdminQuestions', params: {quizId: quiz.id}}" class="btn btn-info text-white">
                      <i class="fas fa-list"></i> Questions
                    </router-link>
                    <button class="btn btn-warning" @click="editQuiz(quiz)">
                      <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger" @click="confirmDelete(quiz)">
                      <i class="fas fa-trash-alt"></i> Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Add Quiz Modal -->
    <div class="modal fade" id="addQuizModal" tabindex="-1" ref="addModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Quiz' : 'Add New Quiz' }}</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuiz">
              <div class="mb-3">
                <label for="quizTitle" class="form-label">Quiz Title</label>
                <input type="text" class="form-control" id="quizTitle" v-model="form.title" required>
              </div>
              <div class="mb-3">
                <label for="quizDescription" class="form-label">Description</label>
                <textarea class="form-control" id="quizDescription" rows="3" v-model="form.description"></textarea>
              </div>
              <div class="mb-3">
                <label for="quizDuration" class="form-label">Duration (minutes)</label>
                <input type="number" class="form-control" id="quizDuration" v-model="form.duration" min="1" required>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
                  <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ editMode ? 'Update Quiz' : 'Add Quiz' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Chapters button -->
    <div class="mt-4">
      <router-link :to="{name: 'AdminChapters', params: {subjectId: subjectId}}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Chapters
      </router-link>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'AdminQuizzes',
  props: {
    chapterId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      chapterName: 'Loading...',
      subjectId: null,
      quizzes: [],
      loading: true,
      error: null,
      successMessage: null,
      showAddModal: false,
      editMode: false,
      selectedQuiz: null,
      form: {
        title: '',
        description: '',
        duration: 30
      },
      formSubmitting: false,
      addModal: null
    }
  },
  watch: {
    showAddModal(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          // Bootstrap 5 modal initialization
          this.addModal = new bootstrap.Modal(this.$refs.addModal)
          this.addModal.show()
        })
      }
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        // If chapterId is missing, redirect to subjects page
        if (!this.chapterId) {
          console.log('Missing chapterId, redirecting to subjects page');
          this.$router.replace({ name: 'AdminSubjects' });
          return;
        }

        console.log('Fetching chapter details and quizzes...');
        
        // First, get the chapter details to display the name and get the subject ID
        const chapterResponse = await ApiService.get(API_CONFIG.ENDPOINTS.CHAPTER_BY_ID(this.chapterId));
        this.chapterName = chapterResponse.name;
        this.subjectId = chapterResponse.subject_id;
        
        // Then, get the quizzes for this chapter
        const quizzesResponse = await ApiService.get(API_CONFIG.ENDPOINTS.QUIZZES(this.chapterId));
        this.quizzes = Array.isArray(quizzesResponse) ? quizzesResponse : (quizzesResponse.quizzes || []);
        
        console.log('Fetched quizzes:', this.quizzes);
      } catch (error) {
        console.error('Error loading quizzes:', error);
        this.error = error.message || 'Failed to load quizzes';
      } finally {
        this.loading = false;
      }
    },
    
    editQuiz(quiz) {
      this.editMode = true;
      this.selectedQuiz = quiz;
      this.form = {
        title: quiz.title,
        description: quiz.description,
        duration: quiz.duration
      };
      this.showAddModal = true;
    },
    
    confirmDelete(quiz) {
      if (confirm(`Are you sure you want to delete the quiz "${quiz.title}"?`)) {
        this.deleteQuiz(quiz);
      }
    },
    
    async deleteQuiz(quiz) {
      this.error = null;
      
      try {
        console.log('Deleting quiz:', quiz.id);
        await ApiService.delete(API_CONFIG.ENDPOINTS.QUIZ_BY_ID(quiz.id));
        
        this.successMessage = 'Quiz deleted successfully';
        
        // Refresh the quizzes list
        await this.fetchData();
      } catch (error) {
        console.error('Error deleting quiz:', error);
        this.error = error.message || 'Failed to delete quiz';
      }
    },
    
    async saveQuiz() {
      this.formSubmitting = true;
      this.error = null;
      
      try {
        if (this.editMode) {
          console.log('Updating quiz:', this.selectedQuiz.id);
          // Update existing quiz
          await ApiService.put(API_CONFIG.ENDPOINTS.QUIZ_BY_ID(this.selectedQuiz.id), {
            title: this.form.title,
            description: this.form.description,
            duration: parseInt(this.form.duration)
          });
          
          this.successMessage = 'Quiz updated successfully';
        } else {
          console.log('Creating new quiz for chapter:', this.chapterId);
          // Create new quiz
          await ApiService.post(API_CONFIG.ENDPOINTS.QUIZZES(this.chapterId), {
            title: this.form.title,
            description: this.form.description,
            duration: parseInt(this.form.duration)
          });
          
          this.successMessage = 'Quiz created successfully';
        }
        
        // Refresh the quizzes list
        await this.fetchData();
        
        // Close the modal
        this.closeAddModal();
      } catch (error) {
        console.error('Error saving quiz:', error);
        this.error = error.message || 'Failed to save quiz';
      } finally {
        this.formSubmitting = false;
      }
    },
    
    closeAddModal() {
      if (this.addModal) {
        this.addModal.hide();
      }
      this.editMode = false;
      this.selectedQuiz = null;
      this.form = {
        title: '',
        description: '',
        duration: 30
      };
      this.showAddModal = false;
    }
  }
}
</script> 