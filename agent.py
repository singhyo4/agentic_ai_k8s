# agent.py
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Read Azure OpenAI settings from environment variables
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Your deployment name
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")  # Default version

client = AzureOpenAI(
    api_version=azure_api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_api_key,
)

def analyze_issues(pods):
    prompt = "You are a Kubernetes SRE. Analyze these failed pods and suggest actions:\n"
    for pod in pods:
        prompt += f"- {pod['name']} in {pod['namespace']}: {pod['status']} ({pod['reason']})\n"
    prompt += "Respond with recommendations in bullet points."

    completion = client.chat.completions.create(
        model=azure_deployment,  # Use your Azure deployment name here
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
