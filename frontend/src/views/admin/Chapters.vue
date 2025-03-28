<template>
  <div class="admin-chapters">
    <h1 class="mb-4">Manage Chapters</h1>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Subject: {{ subjectName }}</h3>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="fas fa-plus me-2"></i> Add Chapter
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
      <p class="mt-2">Loading chapters...</p>
    </div>
    
    <!-- No chapters available -->
    <div v-else-if="chapters.length === 0" class="text-center py-5">
      <i class="fas fa-book-open fa-3x text-muted mb-3"></i>
      <h3>No Chapters Available</h3>
      <p class="text-muted">Click the "Add Chapter" button to create your first chapter for this subject.</p>
    </div>
    
    <!-- Chapters list -->
    <div v-else class="card shadow">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in chapters" :key="chapter.id">
                <td>{{ chapter.id }}</td>
                <td>{{ chapter.name }}</td>
                <td>{{ chapter.description }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link :to="{name: 'AdminQuizzes', params: {chapterId: chapter.id}}" class="btn btn-info text-white">
                      <i class="fas fa-list"></i> Quizzes
                    </router-link>
                    <button class="btn btn-warning" @click="editChapter(chapter)">
                      <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger" @click="confirmDelete(chapter)">
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
    
    <!-- Add Chapter Modal -->
    <div class="modal fade" id="addChapterModal" tabindex="-1" ref="addModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Chapter' : 'Add New Chapter' }}</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveChapter">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name</label>
                <input type="text" class="form-control" id="chapterName" v-model="form.name" required>
              </div>
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea class="form-control" id="chapterDescription" rows="3" v-model="form.description"></textarea>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
                  <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ editMode ? 'Update Chapter' : 'Add Chapter' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Back to Subjects button -->
    <div class="mt-4">
      <router-link :to="{name: 'AdminSubjects'}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i> Back to Subjects
      </router-link>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/apiService';
import API_CONFIG from '@/config/api';

export default {
  name: 'AdminChapters',
  props: {
    subjectId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      subjectName: 'Loading...',
      chapters: [],
      loading: true,
      error: null,
      successMessage: null,
      showAddModal: false,
      editMode: false,
      selectedChapter: null,
      form: {
        name: '',
        description: ''
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
        // If subjectId is missing, redirect to subjects page
        if (!this.subjectId) {
          console.log('Missing subjectId, redirecting to subjects page');
          this.$router.replace({ name: 'AdminSubjects' });
          return;
        }

        console.log('Fetching subject details and chapters...');
        
        // First, get the subject details to display the name
        const subjectResponse = await ApiService.get(API_CONFIG.ENDPOINTS.SUBJECT_BY_ID(this.subjectId));
        this.subjectName = subjectResponse.name;
        
        // Then, get the chapters for this subject
        const chaptersResponse = await ApiService.get(API_CONFIG.ENDPOINTS.CHAPTERS(this.subjectId));
        this.chapters = Array.isArray(chaptersResponse) ? chaptersResponse : (chaptersResponse.chapters || []);
        
        console.log('Fetched chapters:', this.chapters);
      } catch (error) {
        console.error('Error loading chapters:', error);
        this.error = error.message || 'Failed to load chapters';
      } finally {
        this.loading = false;
      }
    },
    
    editChapter(chapter) {
      this.editMode = true;
      this.selectedChapter = chapter;
      this.form = {
        name: chapter.name,
        description: chapter.description
      };
      this.showAddModal = true;
    },
    
    confirmDelete(chapter) {
      if (confirm(`Are you sure you want to delete the chapter "${chapter.name}"?`)) {
        this.deleteChapter(chapter);
      }
    },
    
    async deleteChapter(chapter) {
      this.error = null;
      
      try {
        console.log('Deleting chapter:', chapter.id);
        await ApiService.delete(API_CONFIG.ENDPOINTS.CHAPTER_BY_ID(chapter.id));
        
        this.successMessage = 'Chapter deleted successfully';
        
        // Refresh the chapters list
        await this.fetchData();
      } catch (error) {
        console.error('Error deleting chapter:', error);
        this.error = error.message || 'Failed to delete chapter';
      }
    },
    
    async saveChapter() {
      this.formSubmitting = true;
      this.error = null;
      
      try {
        if (this.editMode) {
          console.log('Updating chapter:', this.selectedChapter.id);
          // Update existing chapter
          await ApiService.put(API_CONFIG.ENDPOINTS.CHAPTER_BY_ID(this.selectedChapter.id), {
            name: this.form.name,
            description: this.form.description
          });
          
          this.successMessage = 'Chapter updated successfully';
        } else {
          console.log('Creating new chapter for subject:', this.subjectId);
          // Create new chapter
          await ApiService.post(API_CONFIG.ENDPOINTS.CHAPTERS(this.subjectId), {
            name: this.form.name,
            description: this.form.description
          });
          
          this.successMessage = 'Chapter created successfully';
        }
        
        // Refresh the chapters list
        await this.fetchData();
        
        // Close the modal
        this.closeAddModal();
      } catch (error) {
        console.error('Error saving chapter:', error);
        this.error = error.message || 'Failed to save chapter';
      } finally {
        this.formSubmitting = false;
      }
    },
    
    closeAddModal() {
      if (this.addModal) {
        this.addModal.hide();
      }
      this.editMode = false;
      this.selectedChapter = null;
      this.form = {
        name: '',
        description: ''
      };
      this.showAddModal = false;
    }
  }
}
</script> 