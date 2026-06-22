<template>
	<div class="container mx-auto px-4 py-8">
		<header class="page-header mb-8">
			<h1 class="text-3xl font-bold text-gray-800">Events Overview</h1>
		</header>

		<main class="page-content">
			<!-- Event Banner/CTA -->
			<div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 mb-8 text-white">
				<h2 class="text-2xl font-bold mb-2">Join Our Next Event!</h2>
				<p class="mb-4">Be part of our growing community and participate in exciting AI image generation events.</p>
				<button class="bg-white text-purple-600 px-6 py-2 rounded-full font-semibold hover:bg-opacity-90 transition-all">
					Learn More
				</button>
			</div>

			<!-- Events List -->
			<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				<!-- Event Card 1 -->
				<div class="bg-white rounded-lg shadow-md p-6">
					<h3 class="text-xl font-semibold mb-2">AI Art Challenge</h3>
					<p class="text-gray-600 mb-4">Create stunning AI-generated artwork based on weekly themes.</p>
					<button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-all">
						Participate
					</button>
				</div>

				<!-- Event Card 2 -->
				<div class="bg-white rounded-lg shadow-md p-6">
					<h3 class="text-xl font-semibold mb-2">Community Showcase</h3>
					<p class="text-gray-600 mb-4">Share and showcase your best AI-generated images with the community.</p>
					<button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-all">
						Participate
					</button>
				</div>

				<!-- Event Card 3 -->
				<div class="bg-white rounded-lg shadow-md p-6">
					<h3 class="text-xl font-semibold mb-2">Workshop Series</h3>
					<p class="text-gray-600 mb-4">Learn advanced techniques from experts in AI image generation.</p>
					<button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-all">
						Participate
					</button>
				</div>
			</div>
		</main>
	</div>
</template>

<script>
export default {
	name: 'EventsOverview',
	data() {
		return {
			// Add reactive data here when needed
		}
	},
	methods: {
		// Add methods here when needed
	}
}
</script>
