/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  experimental: {
    workerThreads: false,
    cpus: 1,
  },
};

export default nextConfig;
