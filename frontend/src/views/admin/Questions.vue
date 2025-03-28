<template>
  <div class="admin-questions">
    <h1 class="mb-4">Manage Questions</h1>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Quiz: {{ quizTitle }}</h3>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="fas fa-plus me-2"></i> Add Question
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
      <p class="mt-2">Loading questions...</p>
    </div>
    
    <!-- No questions available -->
    <div v-else-if="questions.length === 0" class="text-center py-5">
      <i class="fas fa-question fa-3x text-muted mb-3"></i>
      <h3>No Questions Available</h3>
      <p class="text-muted">Click the "Add Question" button to create your first question for this quiz.</p>
    </div>
    
    <!-- Questions list -->
    <div v-else>
      <div v-for="(question, index) in questions" :key="question.id" class="card shadow mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Question {{ index + 1 }}</h5>
          <div class="btn-group btn-group-sm">
            <button class="btn btn-warning" @click="editQuestion(question)">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-danger" @click="confirmDelete(question)">
              <i class="fas fa-trash-alt"></i> Delete
            </button>
          </div>
        </div>
        <div class="card-body">
          <p class="mb-4 h5">{{ question.question_text }}</p>
          
          <div class="mb-2 d-flex align-items-center">
            <span class="badge" :class="question.correct_option === 1 ? 'bg-success' : 'bg-light text-dark'">
              {{ question.correct_option === 1 ? '✓' : 'A' }}
            </span>
            <span class="ms-2">{{ question.option1 }}</span>
          </div>
          
          <div class="mb-2 d-flex align-items-center">
            <span class="badge" :class="question.correct_option === 2 ? 'bg-success' : 'bg-light text-dark'">
              {{ question.correct_option === 2 ? '✓' : 'B' }}
            </span>
            <span class="ms-2">{{ question.option2 }}</span>
          </div>
          
          <div class="mb-2 d-flex align-items-center">
            <span class="badge" :class="question.correct_option === 3 ? 'bg-success' : 'bg-light text-dark'">
              {{ question.correct_option === 3 ? '✓' : 'C' }}
            </span>
            <span class="ms-2">{{ question.option3 }}</span>
          </div>
          
          <div class="mb-2 d-flex align-items-center">
            <span class="badge" :class="question.correct_option === 4 ? 'bg-success' : 'bg-light text-dark'">
              {{ question.correct_option === 4 ? '✓' : 'D' }}
            </span>
            <span class="ms-2">{{ question.option4 }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Question Modal -->
    <div class="modal fade" id="addQuestionModal" tabindex="-1" ref="addModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Question' : 'Add New Question' }}</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuestion">
              <div class="mb-3">
                <label for="questionText" class="form-label">Question Text</label>
                <textarea class="form-control" id="questionText" rows="2" v-model="form.question_text" required></textarea>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="option1" class="form-label">Option A</label>
                  <input type="text" class="form-control" id="option1" v-model="form.option1" required>
                </div>
                <div class="col-md-6">
                  <label for="option2" class="form-label">Option B</label>
                  <input type="text" class="form-control" id="option2" v-model="form.option2" required>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="option3" class="form-label">Option C</label>
                  <input type="text" class="form-control" id="option3" v-model="form.option3" required>
                </div>
                <div class="col-md-6">
                  <label for="option4" class="form-label">Option D</label>
                  <input type="text" class="form-control" id="option4" v-model="form.option4" required>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Correct Option</label>
                <div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="correctOption" id="correctOption1" value="1" v-model="form.correct_option" required>
                    <label class="form-check-label" for="correctOption1">A</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="correctOption" id="correctOption2" value="2" v-model="form.correct_option" required>
                    <label class="form-check-label" for="correctOption2">B</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="correctOption" id="correctOption3" value="3" v-model="form.correct_option" required>
                    <label class="form-check-label" for="correctOption3">C</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="correctOption" id="correctOption4" value="4" v-model="form.correct_option" required>
                    <label class="form-check-label" for="correctOption4">D</label>
                  </div>
                </div>
              </div>
              
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
                  <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ editMode ? 'Update Question' : 'Add Question' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Quizzes button -->
    <div class="mt-4">
      <router-link :to="{name: 'AdminQuizzes', params: {chapterId: chapterId}}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Quizzes
      </router-link>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'AdminQuestions',
  props: {
    quizId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      quizTitle: 'Loading...',
      chapterId: null,
      questions: [],
      loading: true,
      error: null,
      successMessage: null,
      showAddModal: false,
      editMode: false,
      selectedQuestion: null,
      form: {
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
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
        // If quizId is missing, redirect to subjects page
        if (!this.quizId) {
          console.log('Missing quizId, redirecting to subjects page');
          this.$router.replace({ name: 'AdminSubjects' });
          return;
        }

        console.log('Fetching quiz details and questions...');
        
        // First, get the quiz details to display the title and get the chapter ID
        const quizResponse = await ApiService.get(API_CONFIG.ENDPOINTS.QUIZ_BY_ID(this.quizId));
        this.quizTitle = quizResponse.title;
        this.chapterId = quizResponse.chapter_id;
        
        // Then, get the questions for this quiz
        const questionsResponse = await ApiService.get(API_CONFIG.ENDPOINTS.QUESTIONS(this.quizId));
        this.questions = Array.isArray(questionsResponse) ? questionsResponse : (questionsResponse.questions || []);
        
        console.log('Fetched questions:', this.questions);
      } catch (error) {
        console.error('Error loading questions:', error);
        this.error = error.message || 'Failed to load questions';
      } finally {
        this.loading = false;
      }
    },
    
    editQuestion(question) {
      this.editMode = true;
      this.selectedQuestion = question;
      this.form = {
        question_text: question.question_text,
        option1: question.option1,
        option2: question.option2,
        option3: question.option3,
        option4: question.option4,
        correct_option: question.correct_option
      };
      this.showAddModal = true;
    },
    
    confirmDelete(question) {
      if (confirm(`Are you sure you want to delete this question?`)) {
        this.deleteQuestion(question);
      }
    },
    
    async deleteQuestion(question) {
      this.error = null;
      
      try {
        console.log('Deleting question:', question.id);
        await ApiService.delete(API_CONFIG.ENDPOINTS.QUESTION_BY_ID(question.id));
        
        this.successMessage = 'Question deleted successfully';
        
        // Refresh the questions list
        await this.fetchData();
      } catch (error) {
        console.error('Error deleting question:', error);
        this.error = error.message || 'Failed to delete question';
      }
    },
    
    async saveQuestion() {
      this.formSubmitting = true;
      this.error = null;
      
      try {
        // Make sure correct_option is a number
        const formData = {
          ...this.form,
          correct_option: parseInt(this.form.correct_option)
        };
        
        if (this.editMode) {
          console.log('Updating question:', this.selectedQuestion.id);
          // Update existing question
          await ApiService.put(API_CONFIG.ENDPOINTS.QUESTION_BY_ID(this.selectedQuestion.id), formData);
          
          this.successMessage = 'Question updated successfully';
        } else {
          console.log('Creating new question for quiz:', this.quizId);
          // Create new question
          await ApiService.post(API_CONFIG.ENDPOINTS.QUESTIONS(this.quizId), formData);
          
          this.successMessage = 'Question created successfully';
        }
        
        // Refresh the questions list
        await this.fetchData();
        
        // Close the modal
        this.closeAddModal();
      } catch (error) {
        console.error('Error saving question:', error);
        this.error = error.message || 'Failed to save question';
      } finally {
        this.formSubmitting = false;
      }
    },
    
    closeAddModal() {
      if (this.addModal) {
        this.addModal.hide();
      }
      this.editMode = false;
      this.selectedQuestion = null;
      this.form = {
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      };
      this.showAddModal = false;
    }
  }
}
</script> 