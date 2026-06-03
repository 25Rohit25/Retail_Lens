FROM node:18-slim

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Start development server configured to accept external connections
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
