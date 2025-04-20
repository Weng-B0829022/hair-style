'use client';

import { useState } from 'react';
import Image from 'next/image';

interface Article {
  title: string;
  subtitle: string;
  content: string;
  image_url: string;
  category: string;
  subcategory: string;
  source_articles: Array<{
    url: string;
    title: string;
    snippet: string;
    content: string;
    raw_data: any;
  }>;
}

interface SearchResult {
  keyword: string;
  articles: Article[];
}

interface ArticleModalProps {
  article: Article;
  onClose: () => void;
}

function ArticleModal({ article, onClose }: ArticleModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="relative h-64">
          <Image
            src={article.image_url}
            alt={article.title}
            fill
            className="object-cover rounded-t-lg"
          />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-6">
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
              {article.category}
            </span>
            <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm ml-2">
              {article.subcategory}
            </span>
          </div>
          <h2 className="text-2xl font-bold mb-2">{article.title}</h2>
          <h3 className="text-xl text-gray-600 mb-4">{article.subtitle}</h3>
          <div className="prose max-w-none mb-8">
            {article.content.split('\n').map((paragraph, index) => (
              <p key={index} className="mb-4">{paragraph}</p>
            ))}
          </div>
          
          {/* 來源文章資訊 */}
          <div className="border-t pt-6">
            <h4 className="text-lg font-semibold mb-3">參考來源</h4>
            <div className="space-y-4">
              {article.source_articles.map((source, index) => (
                <a 
                  key={index}
                  href={source.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <h5 className="text-blue-600 font-medium mb-2">{source.title}</h5>
                  <p className="text-gray-600 text-sm mb-2">{source.snippet}</p>
                  {source.raw_data?.hashtags && source.raw_data.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {source.raw_data.hashtags.map((tag: string, tagIndex: number) => (
                        <span key={tagIndex} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [keyword, setKeyword] = useState('');
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/qa/beauty/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword }),
      });
      
      if (!response.ok) {
        throw new Error('搜尋失敗');
      }
      
      const data: SearchResult = await response.json();
      setArticles(data.articles);
    } catch (err) {
      setError('搜尋過程中發生錯誤');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">美容美髮靈感生成器</h1>
        
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-4 justify-center">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="輸入髮型或美容相關關鍵字"
              className="w-full max-w-xl px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '生成中...' : '生成文章'}
            </button>
          </div>
        </form>

        {error && (
          <div className="text-red-600 text-center mb-8">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article, index) => (
            <div
              key={index}
              onClick={() => setSelectedArticle(article)}
              className="bg-white rounded-lg shadow-lg overflow-hidden transform rotate-1 hover:rotate-0 transition-transform duration-300 cursor-pointer"
              style={{
                backgroundColor: ['#fef3c7', '#fce7f3', '#dbeafe', '#ecfccb', '#f3e8ff'][index % 5]
              }}
            >
              <div className="relative h-48">
                <Image
                  src={article.image_url}
                  alt={article.title}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-6">
                <div className="mb-2">
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    {article.category}
                  </span>
                </div>
                <h2 className="text-xl font-bold mb-2">{article.title}</h2>
                <h3 className="text-sm text-gray-600 mb-2">{article.subtitle}</h3>
                <p className="text-gray-700 text-sm line-clamp-6">
                  {article.content}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedArticle && (
        <ArticleModal
          article={selectedArticle}
          onClose={() => setSelectedArticle(null)}
        />
      )}
    </main>
  );
}
