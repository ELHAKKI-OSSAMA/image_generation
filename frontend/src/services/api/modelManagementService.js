import { useApi } from '@/composables/useApi';

export const useModelManagementService = () => {
  const api = useApi();

  const sectionEndpoints = {
    sdModelVersion: '/api/v1/models/sd/versions',
    sdModel: '/api/v1/models/sd',
    typeControl: '/api/v1/models/type-controls',
    controlModel: '/api/v1/models/control-models',
    controlModule: '/api/v1/models/control-modules',
    samplerType: '/api/v1/models/sampler-types',
    samplerMode: '/api/v1/models/sampler-modes',
    controlNet: '/api/v1/models/controlnet',
    model: '/api/v1/models/', // This one was confirmed working
    category: '/api/v1/models/category',
    tagOptions: '/api/v1/models/type-controls/tags',
  };

  const loadAllDataSeparately = async () => {
    try {
      const [ 
        sdModelVersionsRes, sdModelsRes, typeControlsRes, controlModelsRes,
        controlModulesRes, samplerTypesRes, samplerModesRes, controlNetsRes,
        modelsRes, categoriesRes, tagOptionsRes,
      ] = await Promise.all([
        api.get(sectionEndpoints.sdModelVersion),
        api.get(sectionEndpoints.sdModel),
        api.get(sectionEndpoints.typeControl),
        api.get(sectionEndpoints.controlModel),
        api.get(sectionEndpoints.controlModule),
        api.get(sectionEndpoints.samplerType),
        api.get(sectionEndpoints.samplerMode),
        api.get(sectionEndpoints.controlNet),
        api.get(sectionEndpoints.model),
        api.get(sectionEndpoints.category),
        api.get(sectionEndpoints.tagOptions),
      ]);
      return {
        sdModelVersions: sdModelVersionsRes.data,
        sdModels: sdModelsRes.data,
        typeControls: typeControlsRes.data,
        controlModels: controlModelsRes.data,
        controlModules: controlModulesRes.data,
        samplerTypes: samplerTypesRes.data,
        samplerModes: samplerModesRes.data,
        controlNets: controlNetsRes.data,
        models: modelsRes.data,
        categories: categoriesRes.data,
        tagOptions: tagOptionsRes.data,
      };
    } catch (error) {
      console.error('Error loading all model management data:', error);
      throw error;
    }
  };

  const createDataItem = async (sectionKey, data) => {
    const endpoint = sectionEndpoints[sectionKey];
    if (!endpoint) throw new Error(`Invalid section key for create: ${sectionKey}`);
    try {
      const response = await api.post(endpoint, data);
      return response.data;
    } catch (error) {
      console.error(`Error creating item for section ${sectionKey}:`, error);
      throw error;
    }
  };

  const updateDataItem = async (sectionKey, id, data) => {
    const endpoint = sectionEndpoints[sectionKey];
    if (!endpoint) throw new Error(`Invalid section key for update: ${sectionKey}`);
    try {
      const response = await api.put(`${endpoint}/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating item ${id} for section ${sectionKey}:`, error);
      throw error;
    }
  };

  const deleteDataItem = async (sectionKey, id) => {
    const endpoint = sectionEndpoints[sectionKey];
    if (!endpoint) throw new Error(`Invalid section key for delete: ${sectionKey}`);
    try {
      const response = await api.delete(`${endpoint}/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting item ${id} for section ${sectionKey}:`, error);
      throw error;
    }
  };

  const getFilteredControlNets = async (modelId) => {
    try {
      // Path based on original full URL: http://localhost:8000/api/v1/models/filteredControlnet/${modelId}
      const response = await api.get(`/api/v1/models/filteredControlnet/${modelId}`);
      console.log("response",response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching filtered control nets for model ${modelId}:`, error);
      throw error;
    }
  };

  return {
    loadAllDataSeparately,
    createDataItem,
    updateDataItem,
    deleteDataItem,
    getFilteredControlNets,
  };
};
