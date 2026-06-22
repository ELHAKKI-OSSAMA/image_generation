<template>
  <div class="admin-page">
    <header class="page-header">
      <h1>Event Management</h1>
    </header>
    
    <main class="page-content">
      <div class="event-form">
        <h2>Create New Event</h2>
        <form @submit.prevent="createEvent">
          <div class="form-group">
            <label for="eventName">Event Name</label>
            <input 
              type="text" 
              id="eventName" 
              v-model="eventForm.name" 
              required
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="eventDescription">Description</label>
            <textarea 
              id="eventDescription" 
              v-model="eventForm.description" 
              required
              class="form-control"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="eventDate">Date</label>
            <input 
              type="datetime-local" 
              id="eventDate" 
              v-model="eventForm.date" 
              required
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="eventModel">Model</label>
            <input 
              type="text" 
              id="eventModel" 
              v-model="eventForm.model" 
              required
              class="form-control"
            />
          </div>
          
          <button type="submit" class="btn btn-primary">Create Event</button>
        </form>
      </div>

      <div class="events-list mt-4">
        <h2>Existing Events</h2>
        <table class="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Date</th>
              <th>Model</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in events" :key="event.id">
              <td>{{ event.name }}</td>
              <td>{{ event.description }}</td>
              <td>{{ formatDate(event.date) }}</td>
              <td>{{ event.model }}</td>
              <td>
                <button @click="editEvent(event)" class="btn btn-sm btn-info me-2">Edit</button>
                <button @click="deleteEvent(event.id)" class="btn btn-sm btn-danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'EventManagement',
  data() {
    return {
      eventForm: {
        name: '',
        description: '',
        date: '',
        model: ''
      },
      events: [] // This would be populated from your API
    }
  },
  methods: {
    createEvent() {
      // TODO: Implement event creation logic
      console.log('Creating event:', this.eventForm)
    },
    editEvent(event) {
      // TODO: Implement event editing logic
      console.log('Editing event:', event)
    },
    deleteEvent(eventId) {
      // TODO: Implement event deletion logic
      console.log('Deleting event:', eventId)
    },
    formatDate(date) {
      return new Date(date).toLocaleString()
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.btn-info {
  background-color: #2196F3;
  color: white;
  border: none;
}

.btn-danger {
  background-color: #f44336;
  color: white;
  border: none;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.table th,
.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

.me-2 {
  margin-right: 0.5rem;
}
</style>
