<template>
  <div class="take-quiz">
    <!-- Quiz Header -->
    <div class="card shadow mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h1 class="mb-2">{{ quiz ? quiz.title : 'Loading Quiz...' }}</h1>
            <p class="mb-0 text-muted" v-if="quiz">
              <i class="fas fa-book me-2"></i> {{ chapterName }} | {{ subjectName }}
            </p>
          </div>
          <div class="text-end">
            <div class="card bg-light p-3 text-center" v-if="!quizSubmitted && quizStarted">
              <h5 class="mb-1">Time Remaining</h5>
              <h3 class="mb-0" :class="{'text-danger': timeRemaining <= 60}">
                {{ formatTime(timeRemaining) }}
              </h3>
            </div>
            <div v-else-if="quizSubmitted">
              <span class="badge bg-success p-2">
                <i class="fas fa-check-circle me-1"></i> Completed
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading quiz questions...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
    </div>
    
    <!-- Quiz not started yet -->
    <div v-else-if="!quizStarted && !quizSubmitted" class="card shadow">
      <div class="card-body text-center p-5">
        <i class="fas fa-clipboard-list fa-3x text-primary mb-3"></i>
        <h2 class="mb-3">Ready to start the quiz?</h2>
        <p class="lead mb-4">
          This quiz contains {{ questions.length }} questions and has a time limit of {{ quiz ? quiz.duration : 0 }} minutes.
        </p>
        <div class="d-grid gap-2 col-md-6 mx-auto">
          <button class="btn btn-primary btn-lg" @click="startQuiz">
            <i class="fas fa-play-circle me-2"></i> Start Quiz
          </button>
        </div>
      </div>
    </div>
    
    <!-- Quiz in progress -->
    <div v-else-if="quizStarted && !quizSubmitted">
      <div class="mb-4">
        <div class="progress" style="height: 10px;">
          <div class="progress-bar bg-success" role="progressbar" :style="{width: `${(currentQuestionIndex + 1) * 100 / questions.length}%`}"></div>
        </div>
        <div class="d-flex justify-content-between mt-2">
          <span>Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</span>
          <span>{{ Math.round((currentQuestionIndex + 1) * 100 / questions.length) }}% Complete</span>
        </div>
      </div>
      
      <!-- Current Question -->
      <div class="card shadow mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">Question {{ currentQuestionIndex + 1 }}</h5>
        </div>
        <div class="card-body">
          <h4 class="mb-4">{{ currentQuestion.question_text }}</h4>
          
          <div class="options">
            <div class="form-check mb-3" v-for="i in 4" :key="i">
              <input class="form-check-input" type="radio" :name="`question-${currentQuestion.id}`" :id="`option-${i}`" 
                     :value="i" v-model="answers[currentQuestion.id]" @change="registerAnswer(currentQuestion.id, i)">
              <label class="form-check-label" :for="`option-${i}`">
                {{ currentQuestion[`option${i}`] }}
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Navigation buttons -->
      <div class="d-flex justify-content-between">
        <button class="btn btn-secondary" @click="prevQuestion" :disabled="currentQuestionIndex === 0">
          <i class="fas fa-arrow-left me-2"></i> Previous
        </button>
        
        <div v-if="currentQuestionIndex < questions.length - 1">
          <button class="btn btn-primary" @click="nextQuestion">
            Next <i class="fas fa-arrow-right ms-2"></i>
          </button>
        </div>
        <div v-else>
          <button class="btn btn-success" @click="confirmSubmission">
            Submit Quiz <i class="fas fa-check-circle ms-2"></i>
          </button>
        </div>
      </div>
      
      <!-- Question navigation -->
      <div class="card shadow mt-4">
        <div class="card-header">
          <h5 class="mb-0">Question Navigator</h5>
        </div>
        <div class="card-body">
          <div class="d-flex flex-wrap gap-2">
            <button v-for="(question, index) in questions" :key="question.id" 
                    class="btn" 
                    :class="getQuestionButtonClass(question.id, index)"
                    @click="jumpToQuestion(index)">
              {{ index + 1 }}
            </button>
          </div>
        </div>
        <div class="card-footer">
          <div class="d-flex gap-3">
            <div><span class="badge bg-primary me-1">Blue</span> Current Question</div>
            <div><span class="badge bg-success me-1">Green</span> Answered</div>
            <div><span class="badge bg-light me-1 text-dark border">White</span> Not Answered</div>
          </div>
        </div>
      </div>
      
      <!-- Submission Confirmation Modal -->
      <div class="modal fade" id="submitConfirmationModal" tabindex="-1" ref="submitModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Confirm Submission</h5>
              <button type="button" class="btn-close" @click="closeSubmitModal"></button>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to submit your quiz?</p>
              <div class="alert alert-warning" v-if="unansweredCount > 0">
                <i class="fas fa-exclamation-triangle me-2"></i> You have {{ unansweredCount }} unanswered question(s).
              </div>
              <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i> All your current answers, including the one for the last question, will be saved.
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeSubmitModal">
                Continue Quiz
              </button>
              <button type="button" class="btn btn-success" @click="submitQuiz">
                <i class="fas fa-check-circle me-2"></i> Submit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Results after submission -->
    <div v-else-if="quizSubmitted" class="results">
      <div class="card shadow mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">Quiz Results</h5>
        </div>
        <div class="card-body text-center py-5">
          <div class="mb-4">
            <div class="display-1 mb-3">
              <span :class="getScoreColorClass(quizResult.score)">
                {{ quizResult.score.toFixed(1) }}%
              </span>
            </div>
            <h5 class="mb-0">
              {{ quizResult.correct_answers }} correct out of {{ quizResult.total_questions }} questions
            </h5>
            <p class="text-muted mt-2">
              Time Taken: {{ formatTime(quizResult.time_taken) }}
            </p>
          </div>
          <div class="d-flex justify-content-center gap-3">
            <router-link :to="{name: 'UserScores'}" class="btn btn-primary">
              <i class="fas fa-chart-line me-2"></i> View All Scores
            </router-link>
            <router-link :to="{name: 'UserSubjects'}" class="btn btn-success">
              <i class="fas fa-book me-2"></i> Take Another Quiz
            </router-link>
          </div>
          
          <div class="alert alert-info mt-4">
            <i class="fas fa-info-circle me-2"></i> Your score has been saved. View your scores page to see your updated statistics.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'TakeQuiz',
  props: {
    quizId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      quiz: null,
      subjectName: '',
      chapterName: '',
      questions: [],
      loading: true,
      error: null,
      quizStarted: false,
      quizSubmitted: false,
      currentQuestionIndex: 0,
      answers: {},
      timeRemaining: 0,
      timerInterval: null,
      startTime: null,
      quizResult: null,
      submitModal: null
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {};
    },
    unansweredCount() {
      // Count how many questions don't have an answer in the answers object
      let count = 0;
      this.questions.forEach(question => {
        if (!this.answers[question.id]) {
          count++;
        }
      });
      return count;
    }
  },
  mounted() {
    this.fetchQuizData();
  },
  beforeUnmount() {
    this.clearTimer();
  },
  methods: {
    async fetchQuizData() {
      try {
        // Get quiz details
        const quizData = await ApiService.get(API_CONFIG.ENDPOINTS.QUIZ_BY_ID(this.quizId));
        this.quiz = quizData;
        
        // Get chapter and subject details if available
        if (quizData.chapter_id) {
          try {
            const chapterData = await ApiService.get(API_CONFIG.ENDPOINTS.CHAPTER_BY_ID(quizData.chapter_id));
            this.chapterName = chapterData.name;
            
            if (chapterData.subject_id) {
              const subjectData = await ApiService.get(API_CONFIG.ENDPOINTS.SUBJECT_BY_ID(chapterData.subject_id));
              this.subjectName = subjectData.name;
            }
          } catch (error) {
            console.warn('Error fetching chapter/subject details:', error);
            // Non-critical error, continue loading quiz
          }
        }
        
        // Get questions
        const questionsData = await ApiService.get(API_CONFIG.ENDPOINTS.QUESTIONS(this.quizId));
        this.questions = questionsData.questions || questionsData;
        
        this.loading = false;
      } catch (error) {
        console.error('Error loading quiz:', error);
        this.error = error.message || 'Failed to load quiz';
        this.loading = false;
      }
    },
    
    startQuiz() {
      this.quizStarted = true;
      this.startTime = new Date();
      
      // Set timer based on quiz duration (in minutes)
      if (this.quiz && this.quiz.duration) {
        this.timeRemaining = this.quiz.duration * 60; // convert minutes to seconds
        this.startTimer();
      }
    },
    
    startTimer() {
      this.timerInterval = setInterval(() => {
        this.timeRemaining -= 1;
        
        if (this.timeRemaining <= 0) {
          this.submitQuiz();
        }
      }, 1000);
    },
    
    clearTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },
    
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    },
    
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex -= 1;
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex += 1;
      }
    },
    
    jumpToQuestion(index) {
      this.currentQuestionIndex = index;
    },
    
    getQuestionButtonClass(questionId, index) {
      if (index === this.currentQuestionIndex) {
        return 'btn-primary';
      } else if (this.answers[questionId]) {
        return 'btn-success';
      } else {
        return 'btn-light border';
      }
    },
    
    confirmSubmission() {
      console.log('Confirming submission');
      
      // Get the current question
      const currentQuestion = this.questions[this.currentQuestionIndex];
      
      // Log the current state of the answer for this question
      console.log('Current question ID:', currentQuestion.id);
      console.log('Current answer for this question:', this.answers[currentQuestion.id]);
      
      // Check if we're on the last question and make sure we register the answer
      if (this.currentQuestionIndex === this.questions.length - 1) {
        console.log('On last question, ensuring answer is registered');
        
        // If the last question isn't answered, show a reminder
        if (!this.answers[currentQuestion.id]) {
          if (!confirm('You haven\'t answered the current question. Are you sure you want to submit without answering?')) {
            return; // Stop the submission process if they cancel
          }
        }
      }
      
      // Ensure all answers are saved
      this.ensureAnswersSaved();
      
      console.log('Current answers before submission:', this.answers);
      
      // Bootstrap 5 modal initialization
      try {
        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
          this.$nextTick(() => {
            try {
              this.submitModal = new bootstrap.Modal(this.$refs.submitModal);
              this.submitModal.show();
            } catch (e) {
              console.error('Error showing modal:', e);
              // Fallback if modal fails
              if (confirm('Are you sure you want to submit your quiz?')) {
                this.submitQuiz();
              }
            }
          });
        } else {
          // Fallback if Bootstrap is not available
          if (confirm('Are you sure you want to submit your quiz?')) {
            this.submitQuiz();
          }
        }
      } catch (e) {
        console.error('Error in confirmSubmission:', e);
        // Ultimate fallback
        this.submitQuiz();
      }
    },
    
    closeSubmitModal() {
      if (this.submitModal) {
        this.submitModal.hide();
        // Clean up the modal backdrop manually
        document.querySelector('.modal-backdrop')?.remove();
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
      }
    },
    
    async submitQuiz() {
      this.clearTimer();
      
      // Ensure all answers are saved
      this.ensureAnswersSaved();
      
      // Make one final check of unanswered questions
      const unansweredQuestions = this.questions.filter(q => !this.answers[q.id]);
      console.log(`Submitting quiz. ${unansweredQuestions.length} questions left unanswered.`);
      
      // Close the modal if it's open before setting quizSubmitted
      this.closeSubmitModal();
      
      this.quizSubmitted = true;
      
      // Calculate score
      let correctAnswers = 0;
      const totalQuestions = this.questions.length;
      
      console.log('Answers at submission:', this.answers);
      
      // Copy the answers to ensure we have the final state
      const finalAnswers = {...this.answers};
      
      // Debug each question and answer
      this.questions.forEach(question => {
        const userAnswer = finalAnswers[question.id];
        // Ensure correct_option is treated as a number for comparison
        const correctOption = parseInt(question.correct_option, 10);
        const isCorrect = parseInt(userAnswer, 10) === correctOption;
        console.log(`Question ${question.id}: User answered ${userAnswer} (${typeof userAnswer}), Correct is ${correctOption} (${typeof correctOption}), Is correct: ${isCorrect}`);
        
        if (isCorrect) {
          correctAnswers++;
        }
      });
      
      const score = Math.round((correctAnswers / totalQuestions) * 100);
      const endTime = new Date();
      const timeTaken = Math.round((endTime - this.startTime) / 1000); // in seconds
      
      console.log(`Final score: ${correctAnswers}/${totalQuestions} = ${score}%`);
      
      // Prepare result with clean data
      this.quizResult = {
        quiz_id: parseInt(this.quizId, 10), // Ensure quiz_id is a number
        score: score,
        total_questions: totalQuestions,
        correct_answers: correctAnswers,
        time_taken: timeTaken,
        answers: finalAnswers
      };
      
      console.log('Submitting quiz result:', this.quizResult);
      
      try {
        // Send result to backend
        console.log('Submitting to endpoint:', API_CONFIG.ENDPOINTS.QUIZ_ATTEMPT(this.quizId));
        const response = await ApiService.post(API_CONFIG.ENDPOINTS.QUIZ_ATTEMPT(this.quizId), {
          quiz_id: parseInt(this.quizId, 10),
          answers: finalAnswers,
          time_taken: timeTaken
        });
        console.log('Quiz submission successful:', response);
        
        // If the backend returns score information, use it to update the local result
        if (response && response.score !== undefined) {
          // Update with server-calculated score (more reliable)
          this.quizResult.score = response.score;
          this.quizResult.correct_answers = response.correct_answers || correctAnswers;
          console.log('Updated score from server response:', this.quizResult.score);
        }
      } catch (error) {
        console.error('Error saving quiz result:', error);
        // Handle specific errors
        if (error.message && error.message.includes('CORS')) {
          console.error('CORS error detected. This may be due to server configuration issues.');
        }
        // Still show results even if saving failed
      }
    },
    
    getScoreColorClass(score) {
      if (score >= 90) return 'text-success';
      if (score >= 70) return 'text-info';
      if (score >= 50) return 'text-warning';
      return 'text-danger';
    },
    
    registerAnswer(questionId, option) {
      // Store the answer as a number (not a string)
      this.answers[questionId] = parseInt(option, 10);
      console.log(`Registered answer for question ${questionId}: ${this.answers[questionId]} (${typeof this.answers[questionId]})`);
    },
    
    ensureAnswersSaved() {
      // This method explicitly ensures all answers (especially the last one) are saved correctly
      // Vue's reactivity should handle this automatically via v-model, but we're adding this
      // as an extra safeguard
      
      // Get the current question
      const currentQuestion = this.questions[this.currentQuestionIndex];
      if (currentQuestion && this.answers[currentQuestion.id]) {
        // Explicitly force the answer to be saved by creating a new answers object
        const currentAnswer = this.answers[currentQuestion.id];
        console.log(`Explicitly saving answer for question ${currentQuestion.id}: ${currentAnswer}`);
        
        // Force Vue to register the change by creating a new object
        this.answers = {
          ...this.answers,
          [currentQuestion.id]: currentAnswer
        };
      }
    }
  }
}
</script>

<style scoped>
.options {
  max-width: 600px;
}
.form-check {
  padding: 15px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  margin-bottom: 15px;
  transition: background-color 0.2s;
}
.form-check:hover {
  background-color: #f8f9fa;
}
.form-check-input:checked + .form-check-label {
  font-weight: bold;
}
</style> 