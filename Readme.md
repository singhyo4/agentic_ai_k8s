# Agentic AI for Kubernetes

## Prerequisites

Before running this project, ensure you have the following:

- **Azure Kubernetes Service (AKS) Cluster**  
  You must have access to an AKS cluster and `kubectl` configured to interact with it.

- **Azure OpenAI Resource**  
  - An Azure OpenAI resource deployed in your Azure subscription.
  - A deployed model (deployment name, e.g., `gpt-4o` or similar).
  - Your Azure OpenAI endpoint URL.
  - Your Azure OpenAI API key.

- **Python 3.12+**  
  Ensure Python and `pip` are installed.

## Setup Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/singhyo4/agentic_ai_k8s.git
   cd k8sagentic_ai
   ```

2. **Create and Activate a Virtual Environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**  
   Create a `.env` file in the project root with the following content:
   ```
   AZURE_OPENAI_API_KEY=your-azure-openai-key
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

5. **Ensure AKS Access**  
   Make sure your `kubectl` context is set to your AKS cluster:
   ```sh
   kubectl config use-context <your-aks-context>
   ```

6. **Run the Agentic AI Script**
   ```sh
   python3 devops_boot.py
   ```

## Notes

- The `.env` file is ignored by git for security.
- Make sure your Azure OpenAI deployment name matches the one you set up in Azure.
- The script will analyze failed pods in your AKS cluster and provide recommendations using Azure OpenAI.
