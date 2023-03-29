FROM node:19-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Install app dependencies
RUN npm install

RUN npm install -g @angular/cli@latest

# Copy the rest of the application code to the container
COPY . .

# Build the Angular app
# Add --prod
RUN npm run build 

# Expose port 80 for the container
EXPOSE 4200

# Define the command to run when the container starts
CMD ["ng", "serve", "--host", "0.0.0.0", "--disable-host-check"]
