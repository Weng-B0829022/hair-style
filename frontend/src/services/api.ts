// 從環境變量中獲取 API 基礎 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export interface QAResponse {
  question: string;
  answer: string;
  image_url: string;
}

export const askQuestion = async (question: string): Promise<QAResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/ask/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
}; 