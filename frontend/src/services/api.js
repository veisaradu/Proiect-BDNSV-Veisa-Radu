import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchAPI = {
  search: async (query, k = 5, strategy = 'semantic') => {
    const response = await api.post('/api/search/', {
      query,
      k,
      strategy,
    });
    return response.data;
  },

  compare: async (query, k = 5) => {
    const response = await api.post('/api/search/compare', null, {
      params: { query, k },
    });
    return response.data;
  },
};

export const documentsAPI = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get('/api/documents/list');
    return response.data;
  },

  stats: async () => {
    const response = await api.get('/api/documents/stats');
    return response.data;
  },

  reindex: async () => {
    const response = await api.post('/api/documents/reindex');
    return response.data;
  },

  delete: async (filename) => {
    const response = await api.delete(`/api/documents/${filename}`);
    return response.data;
  },
};

export const healthAPI = {
  check: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};
export const llmAPI = {
  summarize: async (texts, maxLength = 500) => {
    const response = await api.post('/api/llm/summarize', {
      texts,
      max_length: maxLength,
    });
    return response.data;
  },

  answer: async (query, useRetrieval = true, k = 5) => {
    const response = await api.post('/api/llm/answer', {
      query,
      use_retrieval: useRetrieval,
      k,
    });
    return response.data;
  },

  compareRag: async (query) => {
    const response = await api.post('/api/llm/rag-compare', null, {
      params: { query, k: 5 },
    });
    return response.data;
  }
};

export const evaluationAPI = {
  benchmark: async (queries) => {
    const response = await api.post('/api/evaluation/benchmark', {
      queries,
      k: 10,
      iterations: 5
    });
    return response.data;
  },

  compareAnnVsExact: async (query) => {
    const response = await api.post('/api/evaluation/ann-vs-exact', null, {
      params: { query, k: 10 },
    });
    return response.data;
  },
  
  compareRangeVsTopK: async (query, threshold = 0.7) => {
    const response = await api.post('/api/evaluation/range-vs-topk', null, {
      params: { query, threshold, k: 10 },
    });
    return response.data;
  }
};
export default api;
