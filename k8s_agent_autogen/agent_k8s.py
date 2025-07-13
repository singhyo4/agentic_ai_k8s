import asyncio
from kubernetes import client, config
from autogen_core.models import UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os


load_dotenv()

# Load Kubernetes config (assumes running locally with kubeconfig)
config.load_kube_config()

def get_failed_pods():
    v1 = client.CoreV1Api()
    failed_pods = []
    pods = v1.list_pod_for_all_namespaces(watch=False)
    for pod in pods.items:
        for cs in pod.status.container_statuses or []:
            waiting = getattr(cs.state, "waiting", None)
            if waiting and waiting.reason in ["CrashLoopBackOff", "Error"]:
                failed_pods.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "reason": waiting.reason,
                    "message": waiting.message
                })
    return failed_pods

async def main():
    failed_pods = get_failed_pods()
    if not failed_pods:
        print("✅ All pods are healthy.")
        return

    # Prepare prompt for troubleshooting
    pod_descriptions = "\n".join(
        [f"- {p['name']} in {p['namespace']}: {p['reason']} ({p['message']})" for p in failed_pods]
    )
    prompt = (
        "You are a Kubernetes SRE. Analyze these failed pods and provide troubleshooting steps:\n"
        f"{pod_descriptions}\n"
        "Respond with clear, actionable steps."
    )

    # Set your Azure OpenAI credentials (use environment variables for security)
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment="gpt-4o-mini",
        model="gpt-4o-mini",
        api_version="2024-12-01-preview",
        azure_endpoint="https://yogeshtestaiopen.openai.azure.com/",
        # azure_ad_token_provider=token_provider,  # Optional if you choose key-based authentication.
        api_key="", # For key-based authentication.
    )
    result = await az_model_client.create([UserMessage(content=prompt, source="user")])
    print("\n🧠 Troubleshooting Steps:\n", result)
    await az_model_client.close()

if __name__ == "__main__":
    asyncio.run(main())