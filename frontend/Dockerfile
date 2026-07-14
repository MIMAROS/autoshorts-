FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy application code
COPY . .

# Build Next.js app
RUN npm run build

# Start the application
EXPOSE 3000
CMD ["npm", "start"]