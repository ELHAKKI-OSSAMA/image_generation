<template>
  <div>
    <div class="min-h-screen bg-gray-50 p-6">
      <!-- Quick Create Modal -->
      <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        v-if="showQuickCreateModal"
      >
        <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
          <div class="p-6 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-gray-900">Create New {{ quickCreateType }}</h3>
            <button @click="showQuickCreateModal = false" class="text-gray-400 hover:text-gray-500">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <form @submit.prevent="submitQuickCreate" class="p-6 space-y-6">
            <div class="form-group">
              <label class="form-label">Name</label>
              <input
                v-model="quickCreateName"
                type="text"
                class="form-input"
                required
                autofocus
              />
            </div>
            <div class="flex justify-end space-x-3">
              <button 
                type="button" 
                @click="showQuickCreateModal = false" 
                class="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" class="btn-primary">
                Create
              </button>
            </div>
          </form>
        </div>
      </div>
      <!-- Header -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-gray-900">Model Management</h2>
        <p class="mt-2 text-gray-600">
          Manage and configure your AI models and components
        </p>
      </div>
  
      <!-- Section Navigation -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px space-x-8">
            <button
              v-for="section in sections"
              :key="section.id"
              @click="currentSection = section.id"
              :class="[
                currentSection === section.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              ]"
            >
              {{ section.name }}
            </button>
          </nav>
        </div>
      </div>
  
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
        ></div>
      </div>
  
      <!-- Content Sections -->
      <div v-else class="space-y-6">
        <!-- Section Content -->
        <div
          v-show="currentSection === 'sdModelVersion'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">SD Model Versions</h3>
            <button @click="openModal('sdModelVersion')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Version
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Version Name</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="version in sdModelVersions" :key="version.id">
                  <td class="td-cell">{{ version.version_name }}</td>
                  <td class="td-cell">
                    {{ formatDate(version.created_at) }}
                  </td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('sdModelVersion', version)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('sdModelVersion', version.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <!-- Similar sections for other types -->
        <div
          v-show="currentSection === 'sdModel'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">SD Models</h3>
            <button @click="openModal('sdModel')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add SD Model
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">SD Model Version</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="model in sdModels" :key="model.id">
                  <td class="td-cell">{{ model.name }}</td>
                  <td class="td-cell">{{ model.description }}</td>
                  <td class="td-cell">{{ model.sdmodel_version.version_name }}</td>
                  <td class="td-cell">{{ formatDate(model.created_at) }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('sdModel', model)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('sdModel', model.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'typeControl'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Type Controls</h3>
            <button @click="openModal('typeControl')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Type Control
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Type Name</th>
                  <th class="th-cell">Preview URL</th>
                  <th class="th-cell">Associated Versions</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="type in typeControls" :key="type.id">
                  <td class="td-cell">{{ type.type_name }}</td>
                  <td class="td-cell">
                    <img
                      :src="isBase64(type.preview_url) ? type.preview_url : type.preview_url"
                      :alt="type.type_name"
                      class="h-16 w-16 object-cover"
                    />
                  </td>
                  <td class="td-cell">
                    <ul>
                      <li v-for="version in type.associated_versions" :key="version.id">
                        {{ version.version_name }}
                      </li>
                    </ul>
                  </td>
                  <td class="td-cell">{{ type.description }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('typeControl', type)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('typeControl', type.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'controlModel'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Control Models</h3>
            <button @click="openModal('controlModel')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Control Model
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">Type Control</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="model in controlModels" :key="model.id">
                  <td class="td-cell">{{ model.name }}</td>
                  <td class="td-cell">{{ model.description }}</td>
                  <td class="td-cell">
                    {{ model.type_control?.type_name || "N/A" }}
                  </td>
                  <td class="td-cell">{{ formatDate(model.created_at) }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('controlModel', model)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('controlModel', model.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'controlModule'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Control Modules</h3>
            <button @click="openModal('controlModule')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Control Module
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">Type Control</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="module in controlModules" :key="module.id">
                  <td class="td-cell">{{ module.name }}</td>
                  <td class="td-cell">{{ module.description }}</td>
                  <td class="td-cell">
                    {{ module.type_control?.type_name || "N/A" }}
                  </td>
                  <td class="td-cell">{{ formatDate(module.created_at) }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('controlModule', module)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('controlModule', module.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'samplerType'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Sampler Types</h3>
            <button @click="openModal('samplerType')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Sampler Type
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="type in samplerTypes" :key="type.id">
                  <td class="td-cell">{{ type.name }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('samplerType', type)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('samplerType', type.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'samplerMode'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Sampler Modes</h3>
            <button @click="openModal('samplerMode')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Sampler Mode
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="mode in samplerModes" :key="mode.id">
                  <td class="td-cell">{{ mode.name }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('samplerMode', mode)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('samplerMode', mode.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'controlNet'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">ControlNet</h3>
            <button @click="openModal('controlNet')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add ControlNet
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Control Model</th>
                  <th class="th-cell">Control Module</th>
                  <th class="th-cell">Guidance Start</th>
                  <th class="th-cell">Guidance End</th>
                  <th class="th-cell">Control Mode</th>
                  <th class="th-cell">Resize Mode</th>
                  <th class="th-cell">Enabled</th>
                  <th class="th-cell">Weight</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="net in controlNets" :key="net.id">
                  <td class="td-cell">{{ net.name || "N/A" }}</td>
                  <td class="td-cell">{{ net.control_model.name || "N/A" }}</td>
                  <td class="td-cell">{{ net.control_module.name || "N/A" }}</td>
                  <td class="td-cell">{{ net.guidance_start }}</td>
                  <td class="td-cell">{{ net.guidance_end }}</td>
                  <td class="td-cell">{{ net.control_mode }}</td>
                  <td class="td-cell">{{ net.resize_mode }}</td>
                  <td class="td-cell">{{ net.enabled }}</td>
                  <td class="td-cell">{{ net.weight }}</td>
                  <td class="td-cell">{{ net.description || "N/A" }}</td>
                  <td class="td-cell">{{ formatDate(net.created_at) }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('controlNet', net)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('controlNet', net.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div
          v-show="currentSection === 'category'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Categories</h3>
            <button @click="openModal('category')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Category
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="category in categories" :key="category.id">
                  <td class="td-cell">{{ category.name }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button
                        @click="editItem('category', category)"
                        class="btn-edit"
                      >
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('category', category.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
  
        <div
          v-show="currentSection === 'model'"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">Models</h3>
            <button @click="openModal('model')" class="btn-primary">
              <i class="fas fa-plus mr-2"></i> Add Model
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="th-cell">Name</th>
                  <th class="th-cell">Image</th>
                  <th class="th-cell">Description</th>
                  <th class="th-cell">Type</th>
                  <th class="th-cell">Prompt</th>
                  <th class="th-cell">Negative Prompt</th>
                  <th class="th-cell">Active</th>
                  <th class="th-cell">SD Model</th>
                  <th class="th-cell">Gendre</th>
                  <th class="th-cell">Category</th> 
                  <th class="th-cell">Sampler Mode</th>
                  <th class="th-cell">Sampler Type</th>
                  <th class="th-cell">Resize Mode</th>
                  <th class="th-cell">Steps</th>
                  <th class="th-cell">Save Images</th>
                  <th class="th-cell">Seed</th>
                  <th class="th-cell">Width</th>
                  <th class="th-cell">Height</th>
                  <th class="th-cell">Cfg Scale</th>
                  <th class="th-cell">ControlNet</th>
                  <th class="th-cell">Created At</th>
                  <th class="th-cell">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="model in models" :key="model.id">
                  <td class="td-cell">{{ model.name }}</td>
                  <td class="td-cell">
                    <img
                      :src="isBase64(model.preview_url) ? model.preview_url : model.preview_url"
                      :alt="model.name"
                      class="h-16 w-16 object-cover"
                    />
                  </td>
                  <td class="td-cell">{{ model.description }}</td>
                  <td class="td-cell">{{ model.type }}</td>
                  <td class="td-cell">{{ model.prompt }}</td>
                  <td class="td-cell">{{ model.negative_prompt }}</td>
                  <td class="td-cell">{{ model.active ? "Yes" : "No" }}</td>
                  <td class="td-cell">{{ model.sdmodel?.name || "N/A" }}</td>
                  <td class="td-cell">{{ model.gendre }}</td>
                  <td class="td-cell">{{ model.category?.name || "N/A" }}</td>
                  <td class="td-cell">{{ model.sampler_mode?.name || "N/A" }}</td>
                  <td class="td-cell">{{ model.sampler_type?.name || "N/A" }}</td>
                  <td class="td-cell">{{ model.resize_mode_name }}</td>
                  <td class="td-cell">{{ model.steps }}</td>
                  <td class="td-cell">{{ model.save_images ? "Yes" : "No" }}</td>
                  <td class="td-cell">{{ model.seed }}</td>
                  <td class="td-cell">{{ model.width }}</td>
                  <td class="td-cell">{{ model.height }}</td>
                  <td class="td-cell">{{ model.cfg_scale }}</td>
                  <td class="td-cell">
                    <ul>
                      <li v-for="controlnet in model.controlnets" :key="controlnet.id">
                        {{ controlnet.name }}
                      </li>
                    </ul>
                  </td>
                  <td class="td-cell">{{ formatDate(model.created_at) }}</td>
                  <td class="td-cell">
                    <div class="flex space-x-2">
                      <button @click="editItem('model', model)" class="btn-edit">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        @click="deleteItem('model', model.id)"
                        class="btn-delete"
                      >
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
      <!-- Generic Modal -->
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      >
        <div
          class="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col"
        >
          <div
            class="p-6 border-b border-gray-200 flex justify-between items-center"
          >
            <h3 class="text-xl font-semibold text-gray-900">{{ modalTitle }}</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="p-6 overflow-y-auto">
            <form @submit.prevent="saveItem" class="space-y-6">
              <!-- SD Model Version Form -->
              <div v-if="currentSection === 'sdModelVersion'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Version Name</label>
                  <input
                    v-model="formData.version_name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
              </div>
  
              <!-- SD Model Form -->
              <div v-if="currentSection === 'sdModel'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-group">
                  <label class="form-label">Sd Model Version</label>
                  <div class="flex gap-2">
                    <select
                      v-model="formData.sdmodel_version_id"
                      class="form-select bg-white text-gray-900 flex-1"
                      required
                    >
                      <option value="" selected disabled>
                        Select Sd Model Version
                      </option>
                      <option
                        v-for="version in getVersionFormOptions('sdModelVersion')"
                        :key="version.id"
                        :value="version.id"
                      >
                        {{ version.version_name }}
                      </option>
                    </select>
                    <button 
                      type="button"
                      class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                      @click="openModal('sdModelVersion')"
                    >
                      <span class="text-lg font-bold">+</span>
                      Create new
                    </button>
                  </div>
                </div>
              </div>
  
              <!-- Type Control Form -->
              <div v-if="currentSection === 'typeControl'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Type Name</label>
                  <input
                    v-model="formData.type_name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div>
                  <Multiselect
                    v-model="formData.selectedTags"
                    :options="tagOptions"
                    :multiple="true"
                    :close-on-select="false"
                    placeholder="Select type controls"
                    label="version_name"     
                    track-by="id"     
                    :searchable="true"
                  />
                </div>
                
                <div class="form-group">
                  <label class="form-label">Image</label>
                  <div class="flex flex-col gap-4">
                    <input
                      type="file"
                      @change="handleImageSelect"
                      accept="image/*"
                      class="form-input"
                      required
                    />
                    <div v-if="formData.preview_image" class="relative w-full max-w-xs">
                      <img
                        :src="formData.preview_image"
                        alt="Preview"
                        class="w-full h-auto rounded-lg shadow"
                      />
                      <button
                        @click="removeImage"
                        type="button"
                        class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>

              </div>
  
              <!-- Control Model Form -->
              <div v-if="currentSection === 'controlModel'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-group">
                  <label class="form-label">Type Control</label>
                  <div class="flex gap-2">
                    <select
                      v-model="formData.typecontrol_id"
                      class="form-select bg-white text-gray-900 flex-1"
                      required
                    >
                      <option value="" selected disabled>
                        Select Type Control
                      </option>
                      <option
                        v-for="type in getVersionFormOptions('typeControl')"
                        :key="type.id"
                        :value="type.id"
                      >
                        {{ type.type_name }}
                      </option>
                    </select>
                    <button 
                      type="button"
                      class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                      @click="openModal('typeControl')"
                    >
                      <span class="text-lg font-bold">+</span>
                      Create new
                    </button>
                  </div>
                </div>
              </div>
  
              <!-- Control Module Form -->
              <div v-if="currentSection === 'controlModule'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Type Control</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.typecontrol_id"
                        class="form-select bg-white text-gray-900 flex-1"
                        required
                      >
                        <option value="" selected disabled>
                          Select Type Control
                        </option>
                        <option
                          v-for="module in getVersionFormOptions('typeControl')"
                          :key="module.id"
                          :value="module.id"
                        >
                          {{ module.type_name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="openModal('typeControl')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                </div>
              </div>
  
              <!-- Model Form -->
              <div v-if="currentSection === 'model'" class="space-y-6">
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Name</label>
                    <input
                      v-model="formData.name"
                      type="text"
                      class="form-input"
                      required
                    />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Type</label>
                    <input
                      v-model="formData.type"
                      type="text"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">SD Model</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.sdmodel_id"
                        class="form-select bg-white text-gray-900"
                        required
                      >
                        <option value="" selected disabled>Select SD Model</option>
                        <option
                          v-for="model in sdModels"
                          :key="model.id"
                          :value="model.id"
                        >
                          {{ model.name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="handleCreateNew('sdModel', 'name')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                  <div>
                    <div class="form-group">
                      <label class="form-label">Category</label>
                      <div class="flex gap-2">
                        <select
                          v-model="formData.categorie_id"
                          class="form-select bg-white text-gray-900 flex-1"
                          required
                        >
                          <option value="" selected disabled>
                            Select Categorie
                          </option>
                          <option
                            v-for="mode in categories"
                            :key="mode.id"
                            :value="mode.id"
                          >
                            {{ mode.name }}
                          </option>
                        </select>
                        <button 
                          type="button"
                          class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                          @click="handleCreateNew('samplerMode', 'name')"
                        >
                          <span class="text-lg font-bold">+</span>
                          Create new
                        </button>
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Active</label>
                      <select v-model="formData.active" class="form-select">
                        <option value="" selected disabled>Select Status</option>
                        <option :value="true">Yes</option>
                        <option :value="false">No</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div>
                  <Multiselect
                    v-model="formData.selectedcontrolnets"
                    :options="controlnetOptions"
                    :multiple="true"
                    :close-on-select="false"
                    placeholder="Select controlnets"
                    label="name"     
                    track-by="id"     
                    :searchable="true"
                    :disabled="!formData.sdmodel_id"
                  />
                </div>
                
                
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Width</label>
                    <input
                      v-model.number="formData.width"
                      type="number"
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Height</label>
                    <input
                      v-model.number="formData.height"
                      type="number"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Steps</label>
                    <input
                      v-model.number="formData.steps"
                      type="number"
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Cfg Scale</label>
                    <input
                      v-model.number="formData.cfg_scale"
                      type="range"
                      min="0"
                      max="7"
                      step="0.1"
                      class="form-input"
                    />
                    <div class="mt-1 text-gray-700">
                      Current value: {{ formData.cfg_scale }}
                    </div>
                  </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">seed</label>
                    <input
                      v-model.number="formData.seed"
                      type="number"
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                  <label class="form-label">Save image</label>
                  <select
                    v-model="formData.save_images"
                    class="form-select bg-white text-gray-900"
                    required
                  >
                    <option value="" selected disabled>Select Status</option>
                    <option :value="true">Yes</option>
                    <option :value="false">No</option>
                  </select>
                </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Resize Mode</label>
                    <select
                      v-model="formData.resize_mode"
                      class="form-select bg-white text-gray-900"
                      required
                    >
                      <option value="" selected disabled>
                        Select Resize Mode
                      </option>
                      <option value=0>Just Resize</option>
                      <option value=1>Crop and Resize</option>
                      <option value=2>Resize and Fill</option>

                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Gendre</label>
                    <select
                      v-model="formData.gendre"
                      class="form-select bg-white text-gray-900"
                      required
                    >
                      <option value="" selected disabled>
                        Select Gendre
                      </option>
                      <option value="men">men</option>
                      <option value="women">women</option>
                      <option value="both">both</option>

                    </select>
                  </div>
                </div>
                
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Sampler Mode</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.sampler_mode_id"
                        class="form-select bg-white text-gray-900 flex-1"
                        required
                      >
                        <option value="" selected disabled>
                          Select Sampler Mode
                        </option>
                        <option
                          v-for="mode in samplerModes"
                          :key="mode.id"
                          :value="mode.id"
                        >
                          {{ mode.name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="handleCreateNew('samplerMode', 'name')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Sampler Type</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.sampler_type_id"
                        class="form-select bg-white text-gray-900 flex-1"
                        required
                      >
                        <option value="" selected disabled>
                          Select Sampler Type
                        </option>
                        <option
                          v-for="type in samplerTypes"
                          :key="type.id"
                          :value="type.id"
                        >
                          {{ type.name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="handleCreateNew('samplerType', 'name')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                </div>
                <div class="form-group">
                  <label class="form-label">Prompt</label>
                  <textarea
                    v-model="formData.prompt"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-group">
                  <label class="form-label">Negative Prompt</label>
                  <textarea
                    v-model="formData.negative_prompt"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-group">
                  <label class="form-label">Image</label>
                  <div class="flex flex-col gap-4">
                    <input
                      type="file"
                      @change="handleImageSelect"
                      accept="image/*"
                      class="form-input"
                      required
                    />
                    <div v-if="formData.preview_image" class="relative w-full max-w-xs">
                      <img
                        :src="formData.preview_image"
                        alt="Preview"
                        class="w-full h-auto rounded-lg shadow"
                      />
                      <button
                        @click="removeImage"
                        type="button"
                        class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
                
              
              
  
              <!-- Sampler Type Form -->
              <div v-if="currentSection === 'samplerType'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                
              </div>

              <!-- Category Form -->
              <div v-if="currentSection === 'category'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                
              </div>
  
              <!-- Sampler Mode Form -->
              <div v-if="currentSection === 'samplerMode'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                
              </div>
              
  
              <!-- ControlNet Form -->
              <div v-if="currentSection === 'controlNet'" class="space-y-6">
                <div class="form-group">
                  <label class="form-label">Name</label>
                  <input
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Description</label>
                  <textarea
                    v-model="formData.description"
                    class="form-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-group">
                  <label class="form-label">Enabled</label>
                  <select
                    v-model="formData.enabled"
                    class="form-select bg-white text-gray-900"
                    required
                  >
                    <option value="" selected disabled>Select Status</option>
                    <option :value="true">Yes</option>
                    <option :value="false">No</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Type Control</label>
                  <select
                    v-model="formData.typecontrol_id"
                    class="form-select bg-white text-gray-900"
                    required
                  >
                    <option value="" selected disabled>Select Type Control</option>
                    <option :value="typecontrol.id" v-for="typecontrol in typeControls" :key="typecontrol.id">{{ typecontrol.type_name }}</option>
                  </select>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Control Model</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.control_model_id"
                        class="form-select bg-white text-gray-900 flex-1"
                        :disabled="!formData.typecontrol_id"
                        required
                      >
                        <option value="" selected disabled>
                          Select Control Model
                        </option>
                        <option
                          v-for="model in getVersionFormOptions('controlModel/typecontrol_id/' + formData.typecontrol_id)"
                          :key="model.id"
                          :value="model.id"
                        >
                          {{ model.name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="openModal('controlModel')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Control Module</label>
                    <div class="flex gap-2">
                      <select
                        v-model="formData.control_module_id"
                        class="form-select bg-white text-gray-900 flex-1"
                        required
                        :disabled="!formData.typecontrol_id"
                      >
                        <option value="" selected disabled>
                          Select Control Module
                        </option>
                        <option
                          v-for="module in getVersionFormOptions('controlModule/typecontrol_id/' + formData.typecontrol_id)"
                          :key="module.id"
                          :value="module.id"
                        >
                          {{ module.name }}
                        </option>
                      </select>
                      <button 
                        type="button"
                        class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded flex items-center gap-1"
                        @click="openModal('controlModule')"
                      >
                        <span class="text-lg font-bold">+</span>
                        Create new
                      </button>
                    </div>
                  </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Guidance Start</label>
                    <input
                      v-model.number="formData.guidance_start"
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      class="form-input"
                      required
                    />
                    <div class="mt-1 text-gray-700">
                      Current value: {{ formData.guidance_start }}
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Guidance End</label>
                    <input
                      v-model.number="formData.guidance_end"
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      class="form-input"
                      required
                    />
                    <div class="mt-1 text-gray-700">
                      Current value: {{ formData.guidance_end }}
                    </div>
                  </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Weight</label>
                    <input
                      v-model.number="formData.weight"
                      type="range"
                      min="0"
                      max="2"
                      step="0.05"
                      class="form-input"
                      required
                    />
                    <div class="mt-1 text-gray-700">
                      Current value: {{ formData.weight }}
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Control Mode</label>
                    <select
                      v-model="formData.control_mode"
                      class="form-select bg-white text-gray-900"
                      required
                    >
                      <option value="" selected disabled>
                        Select Control Mode
                      </option>
                      <option value="Balanced">Balanced</option>
                      <option value="My prompt is more important">My prompt is more important</option>
                      <option value="ControlNet is more important">ControlNet is more important</option>
                    </select>
                  </div>
                </div>
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="form-group">
                    <label class="form-label">Resize Mode</label>
                    <select
                      v-model="formData.resize_mode"
                      class="form-select bg-white text-gray-900"
                      required
                    >
                      <option value="" selected disabled>
                        Select Resize Mode
                      </option>
                      <option value="Just Resize">Just Resize</option>
                      <option value="Crop and Resize">Crop and Resize</option>
                      <option value="Resize and Fill">Resize and Fill</option>

                    </select>
                  </div>
                </div>
              </div>
  
              <div
                class="flex justify-end space-x-3 pt-6 border-t border-gray-200"
              >
                <button type="button" @click="closeModal" class="btn-secondary">
                  Cancel
                </button>
                <button type="submit" class="btn-primary">
                  {{ editingId ? "Update" : "Create" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  
    <!-- Quick Create Modal -->
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      v-if="showQuickCreateModal"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-xl font-semibold text-gray-900">Create New {{ quickCreateType }}</h3>
          <button @click="showQuickCreateModal = false" class="text-gray-400 hover:text-gray-500">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="submitQuickCreate" class="p-6 space-y-6">
          <div class="form-group">
            <label class="form-label">Name</label>
            <input
              v-model="quickCreateName"
              type="text"
              class="form-input"
              required
              autofocus
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button 
              type="button" 
              @click="showQuickCreateModal = false" 
              class="btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
  </template>
  
  <script>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useModelManagementService } from '@/services/api/modelManagementService.js';
  import { useToast } from 'vue-toast-notification'
  import Multiselect from "vue-multiselect";
  
  export default {
    components: { Multiselect },
    setup() {
      const modelManagementApi = useModelManagementService();
      const $toast = useToast()
      const loading = ref(false)
      const showModal = ref(false)
      const currentSection = ref('model')
      const formData = ref({
        // Default values for all form fields
        name: '',
        preview_image: null,
        description: '',
        selectedTags: [],
        selectedcontrolnets: [],
        associated_versions: [],

        listcontrolnets:[],
        version_name: '',
        type_name: '',
        preview_url: '',
        sdmodel_id: '',
        typecontrol_id: '',
        control_model_id: '',
        sdmodel_version_id: '',
        control_module_id: '',
        sampler_mode_id: '',
        sampler_type_id: '',
        active: '',
        enabled: '',
        control_mode: '',
        resize_mode: '',
        guidance_start: 0.0,
        guidance_end: 1.0,
        weight: 1.0,
        type: '',
        width: null,
        height: null,
        steps: null,
        cfg_scale: 1.0,
        prompt: '',
        negative_prompt: ''
      });
     
      const editingId = ref(null)

      const showQuickCreateModal = ref(false)
      const quickCreateType = ref('')
      const quickCreateNameField = ref('')
      const quickCreateName = ref('')

      const versionFormItems = ref({
        sdModels: [],
        typeControls: [],
        controlModels: [],
        controlModules: [],
        sdModelVersions: []
      })

      const getVersionFormOptions = (type) => {
        if (type.startsWith('controlModel/typecontrol_id/')) {
          const typecontrolId = parseInt(type.split('/').pop(), 10);
          const baseControlModels = controlModels.value.filter(
            model => model.typecontrol_id === typecontrolId
          );
          const versionControlModels = versionFormItems.value.controlModels.filter(
            model => model.typecontrol_id === typecontrolId
          );
          return [...baseControlModels, ...versionControlModels];
        }
        else if (type.startsWith('controlModule/typecontrol_id/')) {
          const typecontrolId = parseInt(type.split('/').pop(), 10);
          const baseControlModules = controlModules.value.filter(
            module => module.typecontrol_id === typecontrolId
          );
          const versionControlModules = versionFormItems.value.controlModules.filter(
            module => module.typecontrol_id === typecontrolId
          );
          return [...baseControlModules, ...versionControlModules];
        
        } else if (type === 'sdModel') {
          return [...sdModels.value, ...versionFormItems.value.sdModels]
        } else if (type === 'typeControl') {
          return [...typeControls.value, ...versionFormItems.value.typeControls]
        } else if (type === 'controlModel') {
          return [...controlModels.value, ...versionFormItems.value.controlModels]
        } else if (type === 'controlModule') {
          return [...controlModules.value, ...versionFormItems.value.controlModules]
        } else if (type === 'sdModelVersion') {
          return [...sdModelVersions.value, ...versionFormItems.value.sdModelVersions]
        }
        return []
      }
      const isBase64 = (str) => {
        const base64Regex = /^(data:image\/[a-zA-Z]+;base64,)[^\s]+$/;
        return base64Regex.test(str);
      };


      const handleCreateNew = (type, nameField) => {
        quickCreateType.value = type
        quickCreateNameField.value = nameField
        quickCreateName.value = ''
        showQuickCreateModal.value = true
      }

      const handleImageSelect = (event) => {
        const file = event.target.files[0]
        if (file) {
          const reader = new FileReader()
          reader.onload = (e) => {
            formData.value.preview_image = e.target.result
          }
          reader.readAsDataURL(file)
        }
      }

      const removeImage = () => {
        formData.value.preview_image = null
      }
      const submitQuickCreate = async () => {
        if (!quickCreateName.value.trim()) {
          $toast.error('Name cannot be empty');
          return;
        }
        try {
          let sectionKey = '';
          let payload = { name: quickCreateName.value.trim() };

          if (quickCreateType.value === 'SD Model Version') {
            sectionKey = 'sdModelVersion';
            payload = { version_name: quickCreateName.value.trim() };
          } else if (quickCreateType.value === 'Category') {
            sectionKey = 'category';
            // payload is already { name: ... }
          } else if (quickCreateType.value === 'Tag') {
            sectionKey = 'tagOptions';
            // payload is already { name: ... }
          } else {
            $toast.error('Invalid type for quick create');
            return;
          }

          await modelManagementApi.createDataItem(sectionKey, payload);
          $toast.success(`${quickCreateType.value} created successfully`);
          showQuickCreateModal.value = false;
          await loadData(); 
        } catch (error) {
          console.error(`Error creating ${quickCreateType.value}:`, error);
          $toast.error(error.message || `Failed to create ${quickCreateType.value}`);
        }
      };

      const resetForm = () => {
        formData.value = {
          preview_image: null,
          name: '',
          categorie_id: '',
          description: '',
          selectedTags: [],
          selectedcontrolnets: [],
          associated_versions: [],
          version_name: '',
          type_name: '',
          preview_url: '',
          sdmodel_id: '',
          sdmodel_version_id: '',
          typecontrol_id: '',
          control_model_id: '',
          control_module_id: '',
          sampler_mode_id: '',
          sampler_type_id: '',
          active: '',
          enabled: '',
          listcontrolnets:[],
          control_mode: '',
          resize_mode: '',
          guidance_start: 0.0,
          guidance_end: 1.0,
          weight: 1.0,
          type: '',
          width: null,
          height: null,
          steps: null,
          cfg_scale: 1.0,
          prompt: '',
          negative_prompt: ''
        };
      };

      // Format date helper function
      const formatDate = (dateString) => {
        if (!dateString) return '-'
        try {
          const date = new Date(dateString)
          return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        } catch (error) {
          console.error('Error formatting date:', error)
          return 'Invalid Date'
        }
      }

      // Data refs for each section
      const sdModelVersions = ref([])
      const sdModels = ref([])
      const typeControls = ref([])
      const controlModels = ref([])
      const controlModules = ref([])
      const samplerTypes = ref([])
      const samplerModes = ref([])
      const controlNets = ref([])
      const models = ref([])
      const categories = ref([])
      
      // Options fetched from the API
      const tagOptions = ref([])
      const controlnetOptions = ref([])

      watch(() => formData.value.sdmodel_id, async (newId) => {
        if (newId) {
          try {
            const data = await modelManagementApi.getFilteredControlNets(newId);
            controlnetOptions.value = data;
          } catch (error) {
            console.error('Error fetching controlnets:', error);
            controlnetOptions.value = [];
            // $toast.error(error.message || 'Failed to load controlnet options for selected model');
          }
        } else {
          controlnetOptions.value = [];
        }
      });

      const sections = [
        { id: 'model', name: 'Models' },
        { id: 'controlNet', name: 'ControlNet' },
        { id: 'sdModel', name: 'SD Models' },
        { id: 'controlModel', name: 'Control Models' },
        { id: 'controlModule', name: 'Control Modules' },
        { id: 'typeControl', name: 'Type Controls' },
        { id: 'sdModelVersion', name: 'SD Model Versions' },
        { id: 'samplerType', name: 'Sampler Types' },
        { id: 'samplerMode', name: 'Sampler Modes' },
        { id: 'category', name: 'Category' },
        
      ]

      const modalTitle = computed(() => {
        const action = editingId.value ? 'Edit' : 'Add'
        const section = sections.find(s => s.id === currentSection.value)
        return `${action} ${section?.name || ''}`
      })

      const saveItem = async () => {
        try {
          // Map UI section keys to service endpoint keys
          const sectionKeyMap = {
            model: 'model',
            type: 'samplerType',
            version: 'sdModelVersion',
            typeControl: 'typeControl',
            controlModel: 'controlModel',
            controlModule: 'controlModule',
            samplerMode: 'samplerMode',
            samplerType: 'samplerType',
            category: 'category',
            controlNet: 'controlNet',
            sdModelVersion: 'sdModelVersion',
            sdModel: 'sdModel'
          };
          
          const sectionKey = sectionKeyMap[currentSection.value];
          if (!sectionKey) {
            throw new Error(`No endpoint mapping found for section: ${currentSection.value}`);
          }

          // Prepare the data
          if (currentSection.value === 'typeControl') {
            formData.value.associated_versions = formData.value.selectedTags?.map(tag => tag.id) || [];
          }
          
          if (currentSection.value === 'model') {
            formData.value.listcontrolnets = formData.value.selectedcontrolnets?.map(tag => tag.id) || [];
          }

          console.log('Saving:', formData.value);
          
          // Use the appropriate service method based on whether we're creating or updating
          if (editingId.value) {
            await modelManagementApi.updateDataItem(sectionKey, editingId.value, formData.value);
          } else {
            await modelManagementApi.createDataItem(sectionKey, formData.value);
          }
          
          await loadData();
          closeModal();
          $toast.success(`${editingId.value ? 'Updated' : 'Created'} successfully`);
        } catch (error) {
          console.error('Error saving item:', error);
          $toast.error(`Operation failed: ${error.message || 'Unknown error'}`);
        }
      };

      const deleteItem = async (section, id) => {
        if (!confirm('Are you sure you want to delete this item?')) return

        try {
          await modelManagementApi.deleteDataItem(section, id);
          await loadData();
          $toast.success('Deleted successfully')
        } catch (error) {
          $toast.error('Delete operation failed')
          console.error('Error deleting item:', error)
        }
      }

      const openModal = (section, item = null) => {
        currentSection.value = section
        editingId.value = item?.id || null
        resetForm()
        if (item) {
          // Copy all properties from item to formData
          Object.keys(item).forEach(key => {
            if (key in formData.value) {
              formData.value[key] = item[key]
            }
          })
        }
        showModal.value = true
      }

      const closeModal = () => {
        showModal.value = false
        resetForm()
        editingId.value = null
      }

      const loadData = async () => {
        loading.value = true;
        try {
          const result = await modelManagementApi.loadAllDataSeparately();
          sdModelVersions.value = result.sdModelVersions;
          sdModels.value = result.sdModels;
          typeControls.value = result.typeControls;
          controlModels.value = result.controlModels;
          controlModules.value = result.controlModules;
          samplerTypes.value = result.samplerTypes;
          samplerModes.value = result.samplerModes;
          controlNets.value = result.controlNets;
          models.value = result.models;
          categories.value = result.categories;
          tagOptions.value = result.tagOptions;
        } catch (error) {
          console.error('Error loading data in component:', error);
          $toast.error(error.message || 'Failed to load data');
        } finally {
          loading.value = false;
        }
      };

      onMounted(() => {
        loadData()
      })

      return {
        loading,
        showModal,
        categories,
        currentSection,
        sections,
        formData,
        modalTitle,
        sdModelVersions,
        sdModels,
        tagOptions,
        controlnetOptions,
        typeControls,
        controlModels,
        controlModules,
        samplerTypes,
        samplerModes,
        controlNets,
        models,
        categories,
        isBase64,
        openModal,
        closeModal,
        saveItem,
        deleteItem,
        formatDate,
        resetForm,
        editingId,
        handleCreateNew,
        showQuickCreateModal,
        quickCreateType,
        quickCreateName,
        submitQuickCreate,
        getVersionFormOptions,
        versionFormItems,
        handleImageSelect,
        removeImage
      }
    }
  }
  </script>
  
  <style scoped>
  
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-sm transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg shadow-sm transition-colors duration-200;
  }
  
  .btn-edit {
    @apply text-blue-600 hover:text-blue-700;
  }
  
  .btn-delete {
    @apply text-red-600 hover:text-red-700;
  }
  
  .th-cell {
    @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
  }
  
  .td-cell {
    @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
  }
  
  .form-input {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }
  
  .form-select {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }
  
  .form-select option {
    @apply text-gray-900;
  }
  
  .form-select option[value=""][disabled] {
    @apply text-gray-500;
  }
  
  .form-textarea {
    @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }
  
  .form-label {
    @apply block text-sm font-medium text-gray-700;
  }
  
  .form-group {
    @apply mb-6;
  }
  </style>
  