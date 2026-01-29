import { apiClient } from './auth'; 
import { getTokenPayload } from '../utils/auth';
import {
  Task,
  TaskCreateData,
  TaskUpdateData,
  TaskApiResponse,
  TaskFilters,
  BulkOperationResponse,
  TrashApiResponse,
} from '../types/task';

export const taskApi = {
  // Get all tasks
  getTasks: async (filters?: TaskFilters): Promise<TaskApiResponse> => {
    const response = await apiClient.get('/tasks/', { params: filters });
    return response.data;
  },

  // Create a new task
  createTask: async (taskData: TaskCreateData): Promise<Task> => {
    const payload = getTokenPayload();
    
    // Add user_id to satisfy the backend schema (prevents 422 error)
    const taskWithUser = {
      ...taskData,
      user_id: payload?.sub 
    };

    const response = await apiClient.post('/tasks/', taskWithUser);
    return response.data;
  },

  // Get a specific task
  getTask: async (taskId: string): Promise<Task> => {
    const response = await apiClient.get(`/tasks/${taskId}/`);
    return response.data;
  },

  // Update a task
  updateTask: async (taskId: string, taskData: TaskUpdateData): Promise<Task> => {
    const response = await apiClient.put(`/tasks/${taskId}/`, taskData);
    return response.data;
  },

  // Toggle completion
  toggleTaskCompletion: async (taskId: string): Promise<Task> => {
    const response = await apiClient.patch(`/tasks/${taskId}/toggle/`);
    return response.data;
  },

  // Delete a task
  deleteTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}/`);
  },

  // Bulk update
  bulkUpdateTasks: async (taskIds: string[], updateType: string, params: any): Promise<BulkOperationResponse> => {
    const response = await apiClient.post('/tasks/bulk/update/', {
      task_ids: taskIds,
      update_type: updateType,
      params
    });
    return response.data;
  },

  // Bulk delete
  bulkDeleteTasks: async (taskIds: string[]): Promise<BulkOperationResponse> => {
    const response = await apiClient.post('/tasks/bulk/delete/', {
      task_ids: taskIds
    });
    return response.data;
  },

  // Get trash
  getTrashItems: async (limit: number = 20, offset: number = 0): Promise<TrashApiResponse> => {
    const response = await apiClient.get('/trash/', { params: { limit, offset } });
    return response.data;
  },

  // Restore from trash
  restoreFromTrash: async (taskIds: string[]): Promise<BulkOperationResponse> => {
    const response = await apiClient.post('/trash/restore/', {
      task_ids: taskIds
    });
    return response.data;
  },

  // Cleanup trash
  cleanupTrash: async (olderThanDays: number = 30): Promise<BulkOperationResponse> => {
    const response = await apiClient.delete('/trash/cleanup/', { 
      params: { older_than_days: olderThanDays } 
    });
    return response.data;
  },
};