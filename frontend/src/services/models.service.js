import { ModelsGateway } from './models.gateway';

export const ModelsService = {
  async getModels() {
    try {
      return await ModelsGateway.fetchModels();
    } catch (error) {
      console.error('ModelsService - Error fetching models:', error);
      throw error;
    }
  },

  async getModelPayload(modelId, imageBase64) {
    try {
      return await ModelsGateway.getModelPayload(modelId, imageBase64);
    } catch (error) {
      console.error('ModelsService - Error getting model payload:', error);
      throw error;
    }
  }
};
