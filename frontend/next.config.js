/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: ['147.93.97.15'],
  images: {
    domains: [
      'via.placeholder.com',
      // ... 其他已存在的域名 ...
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'oaidalleapiprodscus.blob.core.windows.net',
      },
    ],
  },
}

module.exports = nextConfig 