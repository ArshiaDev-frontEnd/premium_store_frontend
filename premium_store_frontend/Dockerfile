FROM node:18-alpine

WORKDIR /app

# Install dependencies first to leverage cache
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3005

# Start the application in development mode
CMD ["npm", "run", "dev"]
