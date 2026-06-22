<template>
	<div class="container mx-auto px-4 py-8">
		<header class="page-header mb-8">
			<h1 class="text-3xl font-bold text-gray-800">Notifications</h1>
			<div class="mt-4 flex justify-between items-center">
				<div class="flex items-center space-x-4">
					<button
						@click="toggleNotifications"
						class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center"
						:disabled="loading"
					>
						<i class="fas" :class="notificationsEnabled ? 'fa-bell' : 'fa-bell-slash'"></i>
						<span class="ml-2">{{ notificationsEnabled ? 'Disable' : 'Enable' }} Notifications</span>
					</button>
					<button
						@click="markAllAsRead"
						class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 flex items-center"
						:disabled="loading || !unreadCount"
					>
						<i class="fas fa-check-double mr-2"></i>
						Mark All as Read
					</button>
				</div>
				<div class="text-gray-600">
					{{ unreadCount }} unread
				</div>
			</div>
		</header>

		<main class="page-content">
			<!-- Loading State -->
			<div v-if="loading" class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
				<span class="ml-3 text-gray-600">Loading notifications...</span>
			</div>

			<!-- Error State -->
			<div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-8">
				<strong class="font-bold">Error!</strong>
				<span class="block sm:inline"> {{ error }}</span>
				<button
					@click="loadNotifications"
					class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
				>
					Try Again
				</button>
			</div>

			<!-- Empty State -->
			<div v-else-if="!notifications.length" class="text-center py-12">
				<i class="fas fa-bell-slash text-4xl text-gray-400 mb-4"></i>
				<p class="text-gray-600">No notifications yet</p>
			</div>

			<!-- Notifications List -->
			<div v-else class="space-y-4">
				<div 
					v-for="notification in notifications" 
					:key="notification.id"
					class="bg-white rounded-lg shadow-md p-4"
					:class="{ 'border-l-4 border-blue-500': !notification.read }"
				>
					<div class="flex justify-between items-start">
						<div class="flex-1">
							<div class="flex items-center mb-2">
								<i 
									class="fas mr-3" 
									:class="getNotificationIcon(notification.type)"
								></i>
								<h3 class="font-semibold">{{ notification.title }}</h3>
							</div>
							<p class="text-gray-600">{{ notification.message }}</p>
							<div class="mt-2 text-sm text-gray-500">
								{{ formatDate(notification.timestamp) }}
							</div>
						</div>
						<div class="flex items-center space-x-2">
							<button
								v-if="!notification.read"
								@click="markAsRead(notification.id)"
								class="text-blue-500 hover:text-blue-600"
								:disabled="markingRead === notification.id"
							>
								<i class="fas" :class="markingRead === notification.id ? 'fa-spinner fa-spin' : 'fa-check'"></i>
							</button>
							<button
								@click="deleteNotification(notification.id)"
								class="text-red-500 hover:text-red-600"
								:disabled="deleting === notification.id"
							>
								<i class="fas" :class="deleting === notification.id ? 'fa-spinner fa-spin' : 'fa-trash'"></i>
							</button>
						</div>
					</div>
				</div>
			</div>
		</main>
	</div>
</template>

<script>
import { handleError } from '@/utils/errorHandler'

export default {
	name: 'Notifications',
	data() {
		return {
			loading: true,
			error: null,
			notifications: [],
			notificationsEnabled: true,
			markingRead: null,
			deleting: null,
			// Sample notifications data
			sampleNotifications: [
				{
					id: 1,
					type: 'success',
					title: 'Image Generated Successfully',
					message: 'Your image "Sunset Portrait" has been generated successfully.',
					timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
					read: false
				},
				{
					id: 2,
					type: 'info',
					title: 'New Tutorial Available',
					message: 'Check out our new tutorial on advanced image composition techniques.',
					timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
					read: true
				},
				{
					id: 3,
					type: 'warning',
					title: 'Storage Space Running Low',
					message: 'You have used 80% of your storage space. Consider upgrading your plan.',
					timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
					read: false
				}
			]
		}
	},
	computed: {
		unreadCount() {
			return this.notifications.filter(n => !n.read).length
		}
	},
	methods: {
		async loadNotifications() {
			if (this.loading) return;

			try {
				this.loading = true;
				this.error = null;

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 1000));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to load notifications');
				}

				// In a real implementation, this would be an API call
				// const response = await api.getNotifications();
				// this.notifications = response.notifications;
				this.notifications = [...this.sampleNotifications];
			} catch (error) {
				this.error = 'Failed to load notifications';
				handleError(error, 'Load Notifications', {
					message: 'Unable to load notifications. Please try again.'
				});
			} finally {
				this.loading = false;
			}
		},

		async toggleNotifications() {
			try {
				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 500));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to toggle notifications');
				}

				this.notificationsEnabled = !this.notificationsEnabled;
				this.$toast.success(`Notifications ${this.notificationsEnabled ? 'enabled' : 'disabled'}`);
			} catch (error) {
				handleError(error, 'Toggle Notifications', {
					message: 'Unable to toggle notifications. Please try again.'
				});
			}
		},

		async markAsRead(notificationId) {
			if (this.markingRead) return;

			try {
				this.markingRead = notificationId;

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 500));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to mark notification as read');
				}

				const notification = this.notifications.find(n => n.id === notificationId);
				if (notification) {
					notification.read = true;
				}
			} catch (error) {
				handleError(error, 'Mark Notification as Read', {
					message: 'Unable to mark notification as read. Please try again.'
				});
			} finally {
				this.markingRead = null;
			}
		},

		async markAllAsRead() {
			try {
				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 800));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to mark all notifications as read');
				}

				this.notifications.forEach(notification => {
					notification.read = true;
				});

				this.$toast.success('All notifications marked as read');
			} catch (error) {
				handleError(error, 'Mark All as Read', {
					message: 'Unable to mark all notifications as read. Please try again.'
				});
			}
		},

		async deleteNotification(notificationId) {
			if (this.deleting) return;

			try {
				this.deleting = notificationId;

				// Simulate API call
				await new Promise(resolve => setTimeout(resolve, 500));

				// Simulated error (10% chance)
				if (Math.random() < 0.1) {
					throw new Error('Failed to delete notification');
				}

				this.notifications = this.notifications.filter(n => n.id !== notificationId);
				this.$toast.success('Notification deleted');
			} catch (error) {
				handleError(error, 'Delete Notification', {
					message: 'Unable to delete notification. Please try again.'
				});
			} finally {
				this.deleting = null;
			}
		},

		getNotificationIcon(type) {
			const icons = {
				success: 'fa-check-circle text-green-500',
				warning: 'fa-exclamation-triangle text-yellow-500',
				error: 'fa-times-circle text-red-500',
				info: 'fa-info-circle text-blue-500'
			};
			return icons[type] || icons.info;
		},

		formatDate(date) {
			const now = new Date();
			const diff = now - date;
			const minutes = Math.floor(diff / (1000 * 60));
			const hours = Math.floor(diff / (1000 * 60 * 60));
			const days = Math.floor(diff / (1000 * 60 * 60 * 24));

			if (minutes < 60) {
				return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
			} else if (hours < 24) {
				return `${hours} hour${hours === 1 ? '' : 's'} ago`;
			} else {
				return `${days} day${days === 1 ? '' : 's'} ago`;
			}
		}
	},
	async created() {
		await this.loadNotifications();
	}
}
</script>
