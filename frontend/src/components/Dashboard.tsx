import React, { useState, useEffect, useCallback } from 'react';
import { TaskFilters } from '../types/task';
import TaskForm from './TaskForm';
import TaskList from './TaskList';
import BulkOperationsBar from './BulkOperationsBar';
import useBulkSelection from '../hooks/useBulkSelection';
import { taskApi } from '../services/task_api';
import ChatPanel from './chat/ChatPanel'; 

const Dashboard: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState<TaskFilters>({});
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [allTaskIds, setAllTaskIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const {
    selectedIds,
    toggleSelection,
    deselectAll,
    toggleSelectAll,
    selectionCount
  } = useBulkSelection();

  /**
   * REFACTORED: Single source of truth for dashboard data.
   */
  const refreshDashboardData = useCallback(async () => {
    try {
      setError(null);
      const response = await taskApi.getTasks(filters);
      const tasks = response.tasks;
      
      const completed = tasks.filter(t => t.is_completed).length;
      const ids = tasks.map(task => task.id);

      setStats({
        total: tasks.length,
        completed: completed,
        pending: tasks.length - completed
      });
      setAllTaskIds(ids);
    } catch (error: any) {
      console.error('T014: Dashboard fetch error:', error);
      if (error.response?.status === 401) {
        setError("Session expired. Please log in again.");
      } else {
        setError("Failed to load tasks. Please try again later.");
      }
    }
  }, [filters]);

  /**
   * T016: SILENT REFRESH LISTENER
   * Listens for the 'refresh-dashboard' event from ChatPanel.
   * This updates the UI without window.location.reload().
   */
  useEffect(() => {
    const handleSilentRefresh = () => {
      console.log("Dashboard: Received silent refresh event from AI.");
      refreshDashboardData();
    };

    window.addEventListener('refresh-dashboard', handleSilentRefresh);
    return () => window.removeEventListener('refresh-dashboard', handleSilentRefresh);
  }, [refreshDashboardData]);

  // Initial load and filter-based updates
  useEffect(() => {
    refreshDashboardData();
  }, [refreshDashboardData]);

  const handleApplyFilters = () => {
    setFilters({ ...filters });
  };

  const handleResetFilters = () => {
    setFilters({});
  };

  const handleTaskUpdate = () => {
    refreshDashboardData();
  };

  return (
    <div className="container relative px-4 py-8 mx-auto">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">Task Dashboard</h1>
        <p className="text-gray-600">Manage your tasks efficiently</p>
      </div>

      {/* Stats Panel */}
      <div className="grid grid-cols-1 gap-6 mb-8 md:grid-cols-3">
        <div className="p-6 bg-white rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full"><span className="text-blue-600">📊</span></div>
            <div className="ml-4">
              <h2 className="text-lg font-semibold text-gray-900">Total Tasks</h2>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="p-6 bg-white rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full"><span className="text-green-600">✅</span></div>
            <div className="ml-4">
              <h2 className="text-lg font-semibold text-gray-900">Completed</h2>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
            </div>
          </div>
        </div>

        <div className="p-6 bg-white rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full"><span className="text-yellow-600">⏳</span></div>
            <div className="ml-4">
              <h2 className="text-lg font-semibold text-gray-900">Pending</h2>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Controls and Filters */}
      <div className="p-6 mb-8 bg-white rounded-lg shadow">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
          >
            {showForm ? 'Cancel' : 'Create Task'}
          </button>
          
          <div className="flex space-x-2">
            <button onClick={handleApplyFilters} className="px-3 py-2 border rounded-md hover:bg-gray-50">Apply</button>
            <button onClick={handleResetFilters} className="px-3 py-2 border rounded-md hover:bg-gray-50">Reset</button>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="mb-8">
          <TaskForm onSubmit={() => { setShowForm(false); handleTaskUpdate(); }} />
        </div>
      )}

      {/* Task List Section */}
      <div className="p-6 mb-20 bg-white rounded-lg shadow">
        {error ? (
          <div className="p-4 mb-4 text-red-700 bg-red-100 border border-red-400 rounded">
            {error}
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Tasks</h2>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectionCount > 0 && selectionCount === allTaskIds.length}
                  onChange={() => toggleSelectAll(allTaskIds)}
                  className="w-4 h-4 cursor-pointer"
                />
                <span className="ml-2 text-sm text-gray-600">Select all</span>
              </div>
            </div>
            <TaskList
              filters={filters}
              onTaskUpdate={handleTaskUpdate}
              onTaskDelete={handleTaskUpdate}
              selectedTaskIds={selectedIds}
              onSelectionChange={toggleSelection}
            />
          </>
        )}
      </div>

      <BulkOperationsBar
        selectedTaskIds={selectedIds}
        onBulkOperationComplete={() => { handleTaskUpdate(); deselectAll(); }}
        onCancelSelection={deselectAll}
      />

      <ChatPanel />
    </div>
  );
};

export default Dashboard;