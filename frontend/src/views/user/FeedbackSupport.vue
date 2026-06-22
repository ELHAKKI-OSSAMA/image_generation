<template>
	<div class="container mx-auto px-4 py-8">
		<header class="page-header mb-8">
			<h1 class="text-3xl font-bold text-gray-800">Feedback & Support</h1>
		</header>

		<main class="page-content">
			<div class="grid gap-8 md:grid-cols-2">
				<!-- Feedback Form Section -->
				<section class="bg-white rounded-lg shadow-md p-6">
					<h2 class="text-2xl font-semibold mb-6">Share Your Feedback</h2>
					<form @submit.prevent="submitFeedback" class="space-y-4">
						<div>
							<label for="category" class="block text-sm font-medium text-gray-700 mb-1">
								Category
							</label>
							<select
								id="category"
								v-model="feedbackForm.category"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								<option value="suggestion">Suggestion</option>
								<option value="bug">Bug Report</option>
								<option value="feature">Feature Request</option>
								<option value="other">Other</option>
							</select>
						</div>

						<div>
							<label for="subject" class="block text-sm font-medium text-gray-700 mb-1">
								Subject <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								id="subject"
								v-model="feedbackForm.subject"
								:class="{'border-red-500': formErrors.subject}"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
								placeholder="Brief description of your feedback"
							/>
							<p v-if="formErrors.subject" class="mt-1 text-sm text-red-500">
								{{ formErrors.subject }}
							</p>
						</div>

						<div>
							<label for="message" class="block text-sm font-medium text-gray-700 mb-1">
								Message <span class="text-red-500">*</span>
							</label>
							<textarea
								id="message"
								v-model="feedbackForm.message"
								:class="{'border-red-500': formErrors.message}"
								rows="6"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
								placeholder="Please provide detailed feedback..."
							></textarea>
							<p v-if="formErrors.message" class="mt-1 text-sm text-red-500">
								{{ formErrors.message }}
							</p>
						</div>

						<button
							type="submit"
							:disabled="isSubmitting"
							class="w-full bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{{ isSubmitting ? 'Submitting...' : 'Submit Feedback' }}
						</button>
					</form>
				</section>

				<!-- Support Info Section -->
				<section class="bg-white rounded-lg shadow-md p-6">
					<h2 class="text-2xl font-semibold mb-6">Support Information</h2>
					
					<div class="space-y-6">
						<!-- Quick Support -->
						<div>
							<h3 class="text-lg font-semibold mb-3">Quick Support</h3>
							<div class="bg-blue-50 p-4 rounded-lg">
								<p class="text-gray-700">
									Need immediate assistance? Check our comprehensive 
									<a 
										href="#" 
										@click.prevent="contactSupport('help')"
										class="text-blue-600 hover:underline"
									>
										Help Center
									</a>
									for quick answers to common questions.
								</p>
							</div>
						</div>

						<!-- Contact Methods -->
						<div>
							<h3 class="text-lg font-semibold mb-3">Contact Us</h3>
							<div class="space-y-3">
								<div class="flex items-center gap-3">
									<font-awesome-icon icon="envelope" class="text-gray-600" />
									<a 
										href="#" 
										@click.prevent="contactSupport('email')"
										class="text-blue-600 hover:underline"
									>
										support@example.com
									</a>
								</div>
								<div class="flex items-center gap-3">
									<font-awesome-icon icon="clock" class="text-gray-600" />
									<span>Response time: Within 24 hours</span>
								</div>
							</div>
						</div>

						<!-- Support Hours -->
						<div>
							<h3 class="text-lg font-semibold mb-3">Support Hours</h3>
							<p class="text-gray-700">
								Monday - Friday: 9:00 AM - 6:00 PM (EST)<br>
								Weekend: Limited support for urgent issues
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
	name: 'FeedbackSupport',
	data() {
		return {
			feedbackForm: {
				category: 'suggestion',
				subject: '',
				message: ''
			},
			isSubmitting: false,
			formErrors: {
				subject: '',
				message: ''
			}
		}
	},
	methods: {
		validateForm() {
			let isValid = true;
			this.formErrors = {
				subject: '',
				message: ''
			};

			// Validate subject
			if (!this.feedbackForm.subject.trim()) {
				this.formErrors.subject = 'Subject is required';
				isValid = false;
			} else if (this.feedbackForm.subject.length > 100) {
				this.formErrors.subject = 'Subject must be less than 100 characters';
				isValid = false;
			}

			// Validate message
			if (!this.feedbackForm.message.trim()) {
				this.formErrors.message = 'Message is required';
				isValid = false;
			} else if (this.feedbackForm.message.length < 10) {
				this.formErrors.message = 'Message must be at least 10 characters';
				isValid = false;
			} else if (this.feedbackForm.message.length > 1000) {
				this.formErrors.message = 'Message must be less than 1000 characters';
				isValid = false;
			}

			if (!isValid) {
				throw new Error('Please fix the form errors');
			}
		},

		async submitFeedback() {
			if (this.isSubmitting) return;

			try {
				this.isSubmitting = true;
				this.validateForm();

				// Prepare feedback data
				const feedbackData = {
					...this.feedbackForm,
					timestamp: new Date().toISOString(),
					userAgent: navigator.userAgent
				};

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 1500));

				// Simulated error for testing (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Network error occurred');
				}

				// Clear form on success
				this.feedbackForm.subject = '';
				this.feedbackForm.message = '';
				this.feedbackForm.category = 'suggestion';

				this.$toast.success('Thank you for your feedback!');
			} catch (error) {
				if (error.message === 'Please fix the form errors') {
					// Form validation errors
					this.$toast.error('Please fix the form errors before submitting');
				} else {
					// Other errors
					handleError(error, 'Submit Feedback', {
						message: 'Failed to submit feedback. Please try again.'
					});
				}
			} finally {
				this.isSubmitting = false;
			}
		},

		async contactSupport(method) {
			try {
				switch (method) {
					case 'email':
						window.location.href = 'mailto:support@example.com';
						break;
					case 'help':
						// Validate help center URL before navigation
						const helpCenterUrl = new URL('#', window.location.href);
						window.open(helpCenterUrl.toString(), '_blank');
						break;
					default:
						throw new Error('Invalid contact method');
				}
			} catch (error) {
				handleError(error, 'Contact Support', {
					message: 'Failed to open contact method. Please try again.'
				});
			}
		}
	}
}
</script>
