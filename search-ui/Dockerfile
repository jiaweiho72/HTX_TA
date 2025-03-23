# Step 1: Use an official Node.js image as the base
FROM node:18-alpine AS build

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

# Step 4: Copy the rest of the app and build it
COPY . .
RUN npm run build

# Step 5: Use a smaller Node.js image for production
FROM node:18-alpine AS runner

WORKDIR /app

# Step 6: Copy only necessary files
COPY --from=build /app/.next .next
COPY --from=build /app/public public
COPY --from=build /app/package.json .
COPY --from=build /app/node_modules node_modules

# Step 7: Expose port 3000 for Next.js
EXPOSE 3000

# Step 8: Start the Next.js server
CMD ["npm", "run", "start"]
