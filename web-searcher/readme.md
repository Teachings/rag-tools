# Running SearXNG with Custom Settings in Docker

## Overview

This guide walks you through the steps to run a SearXNG instance in Docker using a custom `settings.yml` configuration file. This setup is ideal for users who want to customize their SearXNG instance without needing to rebuild the Docker image every time they make a change.

## Prerequisites

- **Docker**: Ensure Docker is installed on your machine. Verify the installation by running `docker --version`.
- **Git**: For cloning the SearXNG repository, make sure Git is installed.

## Steps

### 1. Use the Official Image or Clone the SearXNG Repository

You have two options for setting up SearXNG:

#### Option 1: Use the Official Image

You can pull the official image directly from Docker Hub:

```bash
docker pull docker.io/searxng/searxng:latest
```

#### Option 2: Clone the SearXNG Repository and Build Your Own Image

If you prefer to customize the build, first clone the SearXNG repository from GitHub:

```bash
git clone https://github.com/searxng/searxng.git
cd searxng
```

### 2. Build the Docker Image (If Using Custom Build)

Build the Docker image using the following command, tagging it with your Docker Hub username:

```bash
docker build -t mukultripathi/searxng .
```

### 3. Push the Docker Image to Docker Hub (Optional)

After building the image, you can push it to your Docker Hub repository:

```bash
docker push mukultripathi/searxng
```

This allows you to reuse the image on any machine by pulling it from Docker Hub.

### 4. Customize `settings.yml`

Place your custom `settings.yml` file in the directory of your choice. Ensure that this file is configured according to your needs, including enabling JSON responses if required.

### 5. Run the SearXNG Docker Container

Run the Docker container using your custom `settings.yml` file. Choose the appropriate command based on whether you are using the official image or a custom build.

#### For the Official Image:

```bash
docker run -d -p 4000:8080 -v ./settings.yml:/etc/searxng/settings.yml searxng/searxng:latest
```

#### For the Custom Build:

```bash
docker run -d -p 4000:8080 -v ./settings.yml:/etc/searxng/settings.yml mukultripathi/searxng
```

#### Command Breakdown:
- `-d`: Runs the container in detached mode.
- `-p 4000:8080`: Maps port 8080 in the container to port 4000 on your host machine.
- `-v ./settings.yml:/etc/searxng/settings.yml`: Mounts the custom `settings.yml` file into the container.
- `searxng/searxng:latest` or `mukultripathi/searxng`: The Docker image being used.

### 6. Pull the Docker Image (Optional)

If you’re setting this up on another machine or after pushing to Docker Hub, you can pull the image using:

```bash
docker pull mukultripathi/searxng
```

### 7. Access SearXNG

Once the container is running, you can access your SearXNG instance by navigating to `http://localhost:4000` in your web browser.

### 8. Testing JSON Output

To verify that the JSON output is correctly configured, you can use `curl` or a similar tool:

```bash
curl http://localhost:4000/search?q=python&format=json
```

This should return search results in JSON format.

## Conclusion

By following these steps, you have successfully set up a SearXNG instance running in Docker with a customized configuration. This setup allows you to easily modify settings without rebuilding the Docker image, offering flexibility and ease of use.
