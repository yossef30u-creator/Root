-e # ONBOARDING.md

Welcome to the Root OS development team! This guide will help you understand the overall architecture and the role of each component within our repository, as well as how you'll interact with and contribute to this project.

## Three-Layer Architecture

Root OS employs a Three-Layer Architecture consisting of Memory, Brain, and Bridge:

1. **Memory**: This layer handles both short-term and long-term memory. It utilizes markdown files like ROOT.md for short-term memory and ChromaDB to manage long-term memory storage.
2. **Brain**: The Semantic Engine serves as the "Brain", interpreting architectural changes through diff analysis of the codebase and provides context updates.
3. **Bridge**: This is the MCP (Model Context Protocol) Bridge, which delivers context and actions to external agents or systems, enabling seamless integration and interaction with AI agents.

## Repository Files

Here is a brief explanation of the purpose of each main file in the repository:

- **README_SECURITY.md**: Contains guidelines and configurations regarding the security architecture of the Root OS.
- **ingestor.py**: Houses logic for analyzing Git diffs, querying OpenAI for architectural impacts, and logging updates within the system.
- **ROOT.md**: A project manifest file summarizing project intentions, recent changes, and statuses.
- **config.py**: The central configuration bridge integrating various system settings.

## Self-Correction Mechanisms

The system's self-correction process involves:
- **Git Diff Analysis**: Changes in code are continuously monitored, allowing the system to generate context updates via ingestor.py in case of architectural deviations or enhancements.
- **Error Synthesis**: Errors caught during operations are logged, enabling future corrections and improvements to ensure the evolving architecture aligns with project goals.

Your primary goal as a developer is to contribute to this dynamic, while ensuring your code adheres to existing patterns and integrates smoothly with the components.

