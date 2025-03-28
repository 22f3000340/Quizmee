<template>
  <div class="admin-subjects">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Manage Subjects</h1>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="fas fa-plus me-2"></i> Add Subject
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
    
    <!-- Subjects List -->
    <div class="card shadow">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading subjects...</p>
        </div>
        
        <div v-else-if="subjects.length === 0" class="text-center py-5">
          <i class="fas fa-book fa-3x text-muted mb-3"></i>
          <h5>No Subjects Found</h5>
          <p class="text-muted">Click the "Add Subject" button to create your first subject.</p>
        </div>
        
        <div v-else class="table-responsive">
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
              <tr v-for="subject in subjects" :key="subject.id">
                <td>{{ subject.id }}</td>
                <td>{{ subject.name }}</td>
                <td>{{ subject.description }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link :to="{name: 'AdminChapters', params: {subjectId: subject.id}}" class="btn btn-info text-white">
                      <i class="fas fa-list"></i> Chapters
                    </router-link>
                    <button class="btn btn-warning" @click="editSubject(subject)">
                      <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger" @click="confirmDelete(subject)">
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
    
    <!-- Add Subject Modal -->
    <div class="modal fade" id="addSubjectModal" tabindex="-1" ref="addModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Subject' : 'Add New Subject' }}</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSubject">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name</label>
                <input type="text" class="form-control" id="subjectName" v-model="form.name" required>
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea class="form-control" id="subjectDescription" rows="3" v-model="form.description"></textarea>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
                  <span v-if="formSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ editMode ? 'Update Subject' : 'Add Subject' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the subject "<strong>{{ selectedSubject ? selectedSubject.name : '' }}</strong>"?</p>
            <p class="text-danger">This action cannot be undone and will delete all chapters and quizzes associated with this subject.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteSubject" :disabled="deleteSubmitting">
              <span v-if="deleteSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Delete
            </button>
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
  name: 'AdminSubjects',
  data() {
    return {
      subjects: [],
      loading: true,
      error: null,
      successMessage: null,
      showAddModal: false,
      editMode: false,
      selectedSubject: null,
      form: {
        name: '',
        description: ''
      },
      formSubmitting: false,
      deleteSubmitting: false,
      addModal: null,
      deleteModal: null
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
    this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Fetching subjects from API...');
        const response = await ApiService.get(API_CONFIG.ENDPOINTS.SUBJECTS);
        console.log('Subjects response:', response);
        
        // The API might return an array directly or an object with a subjects property
        this.subjects = Array.isArray(response) ? response : (response.subjects || []);
        
      } catch (error) {
        console.error('Error loading subjects:', error);
        this.error = error.message || 'Failed to load subjects';
      } finally {
        this.loading = false;
      }
    },
    
    editSubject(subject) {
      this.editMode = true
      this.selectedSubject = subject
      this.form = {
        name: subject.name,
        description: subject.description
      }
      this.showAddModal = true
    },
    
    confirmDelete(subject) {
      this.selectedSubject = subject
      this.$nextTick(() => {
        // Bootstrap 5 modal initialization
        this.deleteModal = new bootstrap.Modal(this.$refs.deleteModal)
        this.deleteModal.show()
      })
    },
    
    async saveSubject() {
      this.formSubmitting = true;
      this.error = null;
      
      try {
        if (this.editMode) {
          console.log('Updating subject:', this.selectedSubject.id);
          // Update existing subject
          await ApiService.put(API_CONFIG.ENDPOINTS.SUBJECT_BY_ID(this.selectedSubject.id), {
            name: this.form.name,
            description: this.form.description
          });
          
          this.successMessage = 'Subject updated successfully';
        } else {
          console.log('Creating new subject');
          // Create new subject
          await ApiService.post(API_CONFIG.ENDPOINTS.SUBJECTS, {
            name: this.form.name,
            description: this.form.description
          });
          
          this.successMessage = 'Subject created successfully';
        }
        
        // Refresh the subjects list
        await this.fetchSubjects();
        
        // Close the modal
        this.closeAddModal();
      } catch (error) {
        console.error('Error saving subject:', error);
        this.error = error.message || 'Failed to save subject';
      } finally {
        this.formSubmitting = false;
      }
    },
    
    async deleteSubject() {
      if (!this.selectedSubject) return;
      
      this.deleteSubmitting = true;
      this.error = null;
      
      try {
        console.log('Deleting subject:', this.selectedSubject.id);
        // Delete subject
        await ApiService.delete(API_CONFIG.ENDPOINTS.SUBJECT_BY_ID(this.selectedSubject.id));
        
        this.successMessage = 'Subject deleted successfully';
        
        // Refresh the subjects list
        await this.fetchSubjects();
        
        // Close the modal
        this.closeDeleteModal();
      } catch (error) {
        console.error('Error deleting subject:', error);
        this.error = error.message || 'Failed to delete subject';
      } finally {
        this.deleteSubmitting = false;
      }
    },
    
    closeAddModal() {
      if (this.addModal) {
        this.addModal.hide()
      }
      this.editMode = false
      this.selectedSubject = null
      this.form = {
        name: '',
        description: ''
      }
      this.showAddModal = false
    },
    
    closeDeleteModal() {
      if (this.deleteModal) {
        this.deleteModal.hide()
      }
      this.selectedSubject = null
    }
  }
}
</script> 