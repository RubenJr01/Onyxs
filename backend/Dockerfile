# Use Node.js 18 on Alpine Linux (small, fast)
FROM node:18-alpine

# Set working directory inside container
WORKDIR /app

# Copy package files first (for layer caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 (documentation, not enforced)
EXPOSE 3000

# Command to run when container starts
CMD ["npm", "start"]
