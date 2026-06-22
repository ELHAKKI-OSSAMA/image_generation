<template>
  <div class="min-h-screen">
    <!-- Header -->
    <header class="fixed top-0 left-0 right-0 bg-white shadow z-50">
      <nav class="container py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-8">
            <img class="h-8 w-auto" src="../assets/brand.png" alt="Logo">
            <a href="#features" class="text-gray-900 hover:text-primary font-medium" @click="scrollToFeatures">Features</a>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/login" class="text-gray-700 hover:text-primary font-medium">Login</router-link>
            <router-link to="/login" class="btn-primary">Get Started</router-link>
          </div>
        </div>
      </nav>
    </header>

    <!-- Hero Section -->
    <section class="pt-32 pb-20 relative">
      <!-- Background with overlay -->
      <div class="absolute inset-0 bg-gradient-to-br from-primary via-primary-light to-primary opacity-90"></div>
      <!-- Dark overlay for better contrast -->
      <div class="absolute inset-0 bg-black opacity-20"></div>
      <div class="container relative z-10">
        <div class="text-center max-w-4xl mx-auto text-white">
          <h1 class="text-5xl sm:text-6xl font-bold mb-8">
            Create Amazing<br/>
            <span class="text-white">AI Generated Art</span>
          </h1>
          <p class="text-xl text-white mb-12 max-w-2xl mx-auto">
            Transform your ideas into stunning visuals with our state-of-the-art AI image generation suite. 
            Unleash your creativity with advanced models and intuitive tools.
          </p>
          <div class="flex justify-center space-x-4">
            <router-link to="/login" class="btn-primary">Get Started</router-link>
            <a href="#features" class="btn-secondary" @click="scrollToFeatures">Learn More</a>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section bg-gray-50">
      <div class="container">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">Powerful Features</h2>
          <p class="text-xl text-gray-600">
            Everything you need to create stunning AI-generated artwork
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="card">
            <div class="h-12 w-12 bg-primary rounded-lg text-white flex items-center justify-center mb-4">
              <font-awesome-icon icon="magic" size="lg" />
            </div>
            <h3 class="text-xl font-semibold mb-2">Advanced AI Models</h3>
            <p class="text-gray-600">Access state-of-the-art AI models for image generation</p>
          </div>

          <!-- Feature 2 -->
          <div class="card">
            <div class="h-12 w-12 bg-primary rounded-lg text-white flex items-center justify-center mb-4">
              <font-awesome-icon icon="images" size="lg" />
            </div>
            <h3 class="text-xl font-semibold mb-2">Batch Processing</h3>
            <p class="text-gray-600">Generate multiple images at once with variations</p>
          </div>

          <!-- Feature 3 -->
          <div class="card">
            <div class="h-12 w-12 bg-primary rounded-lg text-white flex items-center justify-center mb-4">
              <font-awesome-icon icon="download" size="lg" />
            </div>
            <h3 class="text-xl font-semibold mb-2">Easy Export</h3>
            <p class="text-gray-600">Download your creations in multiple formats</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="section bg-white">
      <div class="container">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p class="text-xl text-gray-600">
            Create stunning AI art in three simple steps
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">1</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Describe Your Vision</h3>
            <p class="text-gray-600">Enter a detailed description of the image you want to create</p>
          </div>

          <div class="text-center">
            <div class="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">2</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Choose Your Style</h3>
            <p class="text-gray-600">Select from various AI models and customize settings</p>
          </div>

          <div class="text-center">
            <div class="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl font-bold text-primary">3</span>
            </div>
            <h3 class="text-xl font-semibold mb-2">Generate & Download</h3>
            <p class="text-gray-600">Get your AI-generated artwork in seconds</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white">
      <div class="container py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Company Info -->
          <div>
            <h3 class="text-lg font-semibold mb-4">About</h3>
            <p class="text-gray-400">Creating the future of AI-powered digital art generation.</p>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
            <ul class="space-y-2">
              <li><a href="#features" class="text-gray-400 hover:text-white" @click="scrollToFeatures">Features</a></li>
              <li><router-link to="/login" class="text-gray-400 hover:text-white">Login</router-link></li>
              <li><router-link to="/register" class="text-gray-400 hover:text-white">Sign Up</router-link></li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Legal</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white">Privacy Policy</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white">Terms of Service</a></li>
            </ul>
          </div>

          <!-- Contact -->
          <div>
            <h3 class="text-lg font-semibold mb-4">Contact</h3>
            <ul class="space-y-2">
              <li class="text-gray-400">Email: support@aiart.com</li>
              <li class="flex space-x-4 mt-4">
                <a href="#" class="text-gray-400 hover:text-white">
                  <font-awesome-icon icon="fa-brands fa-twitter" size="lg" />
                </a>
                <a href="#" class="text-gray-400 hover:text-white">
                  <font-awesome-icon icon="fa-brands fa-github" size="lg" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div class="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
          <p>&copy; {{ currentYear }} AI Art Generator. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      currentYear: new Date().getFullYear()
    }
  },
  methods: {
    scrollToFeatures() {
      const featuresSection = document.getElementById('features')
      if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }
}
</script>

<style scoped>
.btn {
  @apply transition-all duration-200 ease-in-out;
}

.section {
  @apply scroll-mt-20;
}
</style>
