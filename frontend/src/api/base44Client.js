// Mock base44 client for demonstration
// This would normally be a real API client

const mockStorage = {
  messages: [],
  settings: null,
  user: { email: "demo@user.com", name: "Demo User" }
};

export const base44 = {
  auth: {
    me: async () => {
      return mockStorage.user;
    }
  },
  entities: {
    ChatMessage: {
      filter: async (criteria, sort) => {
        return mockStorage.messages.filter(msg => 
          !criteria.created_by || msg.created_by === criteria.created_by
        ).sort((a, b) => new Date(a.created_date) - new Date(b.created_date));
      },
      create: async (data) => {
        const message = {
          ...data,
          id: Date.now().toString(),
          created_by: mockStorage.user.email,
          created_date: new Date().toISOString()
        };
        mockStorage.messages.push(message);
        return message;
      }
    },
    AppSettings: {
      filter: async (criteria) => {
        if (!mockStorage.settings) return [];
        if (criteria.user_email && mockStorage.settings.user_email === criteria.user_email) {
          return [mockStorage.settings];
        }
        return [];
      },
      create: async (data) => {
        const settings = {
          ...data,
          id: Date.now().toString()
        };
        mockStorage.settings = settings;
        return settings;
      },
      update: async (id, data) => {
        mockStorage.settings = { ...mockStorage.settings, ...data };
        return mockStorage.settings;
      }
    }
  }
};

