FROM node:20-alpine

# Install pnpm globally
RUN npm install -g pnpm

WORKDIR /app

# Copy ONLY the dependency files first
COPY package.json pnpm-lock.yaml* ./

# Install dependencies inside the container
RUN pnpm install

# Now copy the rest of the code (the .dockerignore will skip node_modules)
COPY . .

# We don't need RUN pnpm build for dev mode!
EXPOSE 3000

# Start the dev server
CMD ["pnpm", "dev"]