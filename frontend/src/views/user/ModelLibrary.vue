<template>
	<div class="container mx-auto px-4 py-8">
		<header class="page-header mb-8">
			<h1 class="text-3xl font-bold text-gray-800">Model Library</h1>
		</header>

		<main class="page-content">
			<!-- Search and Filter Bar -->
			<div class="mb-8">
				<div class="flex gap-4 flex-wrap">
					<div class="flex-1 min-w-[200px]">
						<input
							type="text"
							placeholder="Search models..."
							@input="handleSearch"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>
					<div class="w-40">
						<select 
							v-model="selectedCategory"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">All Categories</option>
							<option value="portrait">Portrait</option>
							<option value="landscape">Landscape</option>
							<option value="abstract">Abstract</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Loading State -->
			<div v-if="isLoading" class="text-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-4 text-gray-600">Loading models...</p>
			</div>

			<!-- Error State -->
			<div v-else-if="loadError" class="text-center py-12">
				<div class="text-red-500 mb-4">
					<i class="fas fa-exclamation-circle text-4xl"></i>
				</div>
				<p class="text-gray-800 mb-4">{{ loadError }}</p>
				<button 
					@click="fetchModels"
					class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
				>
					Try Again
				</button>
			</div>

			<!-- Model Grid -->
			<div v-else class="space-y-8">
				<!-- Featured Models Grid -->
				<div class="space-y-4">
					<h2 class="text-xl font-semibold text-gray-800">Featured Models</h2>
					<div class="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
						<div 
							v-for="model in featuredModels" 
							:key="model.id"
							class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
						>
							<div class="relative h-48">
								<img 
									:src="model.previewImage" 
									:alt="model.name"
									class="w-full h-full object-cover"
								/>
								<div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
							</div>
							<div class="p-4">
								<div class="flex items-center justify-between mb-2">
									<h3 class="text-lg font-semibold">{{ model.name }}</h3>
									<span class="px-2 py-1 text-xs rounded-full" 
										:class="model.type === 'new' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'">
										{{ model.type === 'new' ? 'New' : 'Featured' }}
									</span>
								</div>
								<p class="text-gray-600 text-sm mb-4">{{ model.description }}</p>
								<button 
									@click="selectModel(model.id)"
									class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-all"
								>
									Select Model
								</button>
							</div>
						</div>
					</div>
				</div>

				<!-- All Models Grid -->
				<div class="space-y-4">
					<h2 class="text-xl font-semibold text-gray-800">All Models</h2>
					<div class="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
						<div 
							v-for="model in filteredModels" 
							:key="model.id"
							class="bg-white rounded-lg shadow-md overflow-hidden"
						>
							<div class="h-48 bg-gray-200">
								<div v-if="model.thumbnail" class="w-full h-full">
									<img 
										:src="model.thumbnail" 
										:alt="model.name"
										class="w-full h-full object-cover"
									/>
								</div>
								<div v-else class="w-full h-full flex items-center justify-center text-gray-400">
									<span>Model Preview</span>
								</div>
							</div>
							<div class="p-4">
								<h3 class="text-lg font-semibold mb-2">{{ model.name }}</h3>
								<p class="text-gray-600 text-sm mb-4">{{ model.description }}</p>
								<button 
									@click="selectModel(model.id)"
									:disabled="model.status !== 'available'"
									class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed"
								>
									{{ model.status === 'available' ? 'Select Model' : 'Unavailable' }}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- No Results -->
			<div v-if="!isLoading && !loadError && filteredModels.length === 0" class="text-center py-12">
				<p class="text-gray-600">No models found matching your criteria</p>
			</div>
		</main>
	</div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'

export default {
	name: 'ModelLibrary',
	data() {
		return {
			models: [
				{
					id: 1,
					name: 'Portrait Pro V1',
					description: 'Specialized in creating realistic portrait images with enhanced details.',
					category: 'portrait',
					thumbnail: null,
					status: 'available'
				},
				{
					id: 2,
					name: 'Landscape Master',
					description: 'Perfect for generating stunning landscape and nature scenes.',
					category: 'landscape',
					thumbnail: null,
					status: 'available'
				},
				{
					id: 3,
					name: 'Abstract Art Gen',
					description: 'Specialized in creating unique abstract art and patterns.',
					category: 'abstract',
					thumbnail: null,
					status: 'available'
				}
			],
			featuredModels: [
				{
					id: 1,
					name: 'Portrait Pro V1',
					description: 'Specialized in creating realistic portrait images with enhanced details.',
					previewImage: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=688&auto=format&fit=crop',
					type: 'new'
				},
				{
					id: 2,
					name: 'Landscape Master',
					description: 'Perfect for generating stunning landscape and nature scenes.',
					previewImage: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1470&auto=format&fit=crop',
					type: 'featured'
				},
				{
					id: 3,
					name: 'Abstract Art Gen',
					description: 'Specialized in creating unique abstract art and patterns.',
					previewImage: 'https://images.unsplash.com/photo-1541701494587-cb58502866ab?q=80&w=1470&auto=format&fit=crop',
					type: 'new'
				}
			],
			searchQuery: '',
			selectedCategory: '',
			isLoading: false,
			loadError: null,
			searchTimeout: null
		}
	},
	computed: {
		filteredModels() {
			try {
				let result = [...this.models];

				// Apply category filter
				if (this.selectedCategory) {
					result = result.filter(model => model.category === this.selectedCategory);
				}

				// Apply search filter
				if (this.searchQuery.trim()) {
					const query = this.searchQuery.toLowerCase().trim();
					result = result.filter(model => 
						model.name.toLowerCase().includes(query) ||
						model.description.toLowerCase().includes(query)
					);
				}

				return result;
			} catch (error) {
				handleError(error, 'Filter Models', {
					message: 'Error filtering models'
				});
				return [];
			}
		}
	},
	methods: {
		async fetchModels() {
			if (this.isLoading) return;

			try {
				this.isLoading = true;
				this.loadError = null;

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 1000));

				// Simulated error for testing (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to fetch models');
				}

				// In a real implementation, this would be an API call
				// this.models = await api.getModels();
			} catch (error) {
				this.loadError = error.message;
				handleError(error, 'Fetch Models', {
					message: 'Failed to load models. Please try again.'
				});
			} finally {
				this.isLoading = false;
			}
		},

		async selectModel(modelId) {
			try {
				const model = this.models.find(m => m.id === modelId);
				if (!model) {
					throw new Error('Model not found');
				}

				if (model.status !== 'available') {
					throw new Error('Model is currently unavailable');
				}

				// Simulate API call to select model
				await new Promise(resolve => setTimeout(resolve, 500));

				// Simulated error for testing (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to select model');
				}

				this.$toast.success(`Model "${model.name}" selected successfully`);
				this.$router.push('/image-generation');
			} catch (error) {
				handleError(error, 'Select Model', {
					message: error.message || 'Failed to select model. Please try again.'
				});
			}
		},

		handleSearch(event) {
			try {
				// Debounce search input
				if (this.searchTimeout) {
					clearTimeout(this.searchTimeout);
				}

				this.searchTimeout = setTimeout(() => {
					this.searchQuery = event.target.value;
				}, 300);
			} catch (error) {
				handleError(error, 'Search Models', {
					message: 'Error occurred while searching'
				});
			}
		},

		async loadThumbnails() {
			try {
				const loadPromises = this.models.map(async (model) => {
					try {
						// Simulate thumbnail loading
						await new Promise(resolve => setTimeout(resolve, 500));
						
						// Simulated error for testing (5% chance per thumbnail)
						if (Math.random() < 0.05) {
							throw new Error(`Failed to load thumbnail for ${model.name}`);
						}

						// In a real implementation, this would load the actual thumbnail
						model.thumbnail = 'path/to/thumbnail.jpg';
					} catch (error) {
						// Set a fallback thumbnail
						model.thumbnail = null;
						console.warn(`Failed to load thumbnail for model ${model.name}:`, error);
					}
				});

				await Promise.all(loadPromises);
			} catch (error) {
				handleError(error, 'Load Thumbnails', {
					message: 'Some thumbnails failed to load'
				});
			}
		}
	},
	async mounted() {
		await this.fetchModels();
		await this.loadThumbnails();
	}
}
</script>
