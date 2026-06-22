<template>
	<div class="container mx-auto px-4 py-8">
		<header class="page-header mb-8">
			<h1 class="text-3xl font-bold text-gray-800">Tutorials & Tips</h1>
		</header>

		<main class="page-content">
			<!-- Loading State -->
			<div v-if="loading" class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
				<span class="ml-3 text-gray-600">Loading tutorials...</span>
			</div>

			<!-- Error State -->
			<div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-8">
				<strong class="font-bold">Error!</strong>
				<span class="block sm:inline"> {{ error }}</span>
				<button
					@click="loadTutorialContent"
					class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
				>
					Try Again
				</button>
			</div>

			<div v-else>
				<!-- Photo Guide Section -->
				<section v-for="tutorial in tutorials" :key="tutorial.id" class="bg-white rounded-lg shadow-md p-6 mb-8">
					<div class="flex justify-between items-center mb-4">
						<h2 class="text-2xl font-semibold">{{ tutorial.title }}</h2>
						<button
							@click="playTutorialVideo(tutorial.id)"
							class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center"
							:disabled="loadingVideo"
						>
							<i class="fas fa-play mr-2"></i>
							{{ loadingVideo && currentTutorialVideo === tutorial.id ? 'Loading...' : 'Watch Video' }}
						</button>
					</div>

					<!-- Video Error -->
					<div 
						v-if="videoError && currentTutorialVideo === tutorial.id" 
						class="bg-red-100 text-red-700 p-3 rounded mb-4"
					>
						{{ videoError }}
					</div>

					<!-- Tutorial Steps -->
					<div class="space-y-4">
						<div 
							v-for="step in tutorial.steps" 
							:key="step.number"
							class="flex items-start gap-4"
						>
							<div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
								{{ step.number }}
							</div>
							<div>
								<h3 class="font-semibold mb-2">{{ step.title }}</h3>
								<p class="text-gray-600">{{ step.description }}</p>
							</div>
						</div>
					</div>

					<!-- Complete Tutorial Button -->
					<div class="mt-6 text-right">
						<button
							@click="markTutorialComplete(tutorial.id)"
							class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
						>
							Mark as Complete
						</button>
					</div>
				</section>

				<!-- FAQ Section -->
				<section class="bg-white rounded-lg shadow-md p-6">
					<h2 class="text-2xl font-semibold mb-4">Frequently Asked Questions</h2>
					<div class="space-y-4">
						<div 
							v-for="faq in faqs" 
							:key="faq.id"
							class="border-b pb-4"
						>
							<button
								@click="toggleFaq(faq.id)"
								class="w-full text-left flex justify-between items-center"
							>
								<h3 class="font-semibold">{{ faq.question }}</h3>
								<i 
									class="fas" 
									:class="expandedFaqs.has(faq.id) ? 'fa-chevron-up' : 'fa-chevron-down'"
								></i>
							</button>
							<p 
								v-show="expandedFaqs.has(faq.id)"
								class="text-gray-600 mt-2"
							>
								{{ faq.answer }}
							</p>
						</div>
					</div>
				</section>
			</div>
		</main>
	</div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'

export default {
	name: 'Tutorials',
	data() {
		return {
			loading: true,
			error: null,
			tutorials: [
				{
					id: 'photo-guide',
					title: 'Taking the Perfect Photo',
					steps: [
						{
							number: 1,
							title: 'Lighting is Key',
							description: 'Ensure your subject is well-lit with natural light when possible. Avoid harsh shadows and overexposed areas.'
						},
						{
							number: 2,
							title: 'Composition',
							description: 'Frame your subject properly and keep the background clean and uncluttered.'
						},
						{
							number: 3,
							title: 'Focus',
							description: 'Ensure your subject is in sharp focus for the best results.'
						}
					]
				},
				{
					id: 'generation-guide',
					title: 'Generating Images',
					steps: [
						{
							number: 1,
							title: 'Upload Your Photo',
							description: 'Select a high-quality photo that meets the guidelines above.'
						},
						{
							number: 2,
							title: 'Choose Your Style',
							description: 'Select from our variety of AI models and style options.'
						},
						{
							number: 3,
							title: 'Generate',
							description: 'Click generate and wait for your AI-enhanced image.'
						}
					]
				}
			],
			faqs: [
				{
					id: 'formats',
					question: 'What file formats are supported?',
					answer: 'We support JPG, PNG, and WEBP formats.'
				},
				{
					id: 'generation-time',
					question: 'How long does generation take?',
					answer: 'Generation typically takes 10-30 seconds depending on the model used.'
				},
				{
					id: 'editing',
					question: 'Can I edit my generated images?',
					answer: 'Yes, you can regenerate or download your images for external editing.'
				}
			],
			expandedFaqs: new Set(),
			videoPlaying: false,
			videoError: null,
			currentTutorialVideo: null,
			loadingVideo: false
		}
	},
	methods: {
		async loadTutorialContent() {
			if (this.loading) return;

			try {
				this.loading = true;
				this.error = null;

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 1000));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to load tutorial content');
				}

				// In a real implementation, this would be an API call
				// const response = await api.getTutorials();
				// this.tutorials = response.tutorials;
				// this.faqs = response.faqs;
			} catch (error) {
				this.error = 'Failed to load tutorial content';
				handleError(error, 'Load Tutorials', {
					message: 'Unable to load tutorials. Please try again.'
				});
			} finally {
				this.loading = false;
			}
		},

		async playTutorialVideo(tutorialId) {
			if (this.loadingVideo) return;

			try {
				this.loadingVideo = true;
				this.videoError = null;
				this.currentTutorialVideo = tutorialId;

				// Simulate video loading
				await new Promise(resolve => setTimeout(resolve, 800));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to load video');
				}

				this.videoPlaying = true;
			} catch (error) {
				this.videoError = 'Failed to load video';
				this.videoPlaying = false;
				handleError(error, 'Play Tutorial Video', {
					message: 'Unable to play tutorial video. Please try again.'
				});
			} finally {
				this.loadingVideo = false;
			}
		},

		toggleFaq(faqId) {
			try {
				if (this.expandedFaqs.has(faqId)) {
					this.expandedFaqs.delete(faqId);
				} else {
					this.expandedFaqs.add(faqId);
				}
			} catch (error) {
				handleError(error, 'Toggle FAQ', {
					message: 'Error toggling FAQ section'
				});
			}
		},

		async markTutorialComplete(tutorialId) {
			try {
				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 500));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to mark tutorial as complete');
				}

				this.$toast.success('Tutorial marked as complete!');
			} catch (error) {
				handleError(error, 'Mark Tutorial Complete', {
					message: 'Unable to mark tutorial as complete. Please try again.'
				});
			}
		}
	},
	async created() {
		await this.loadTutorialContent();
	}
}
</script>
