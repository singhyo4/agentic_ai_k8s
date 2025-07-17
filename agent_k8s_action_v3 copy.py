import asyncio
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from kubernetes import client, config
from autogen_core.models import UserMessage

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

# Load environment variables from .env
load_dotenv()

# Load local kubeconfig (or use in-cluster config if running in a Kubernetes environment)
config.load_kube_config()

# Azure OpenAI client
az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o-mini",
    model="gpt-4o-mini",
    api_version="2024-12-01-preview",
    azure_endpoint="https://westeurope.api.cognitive.microsoft.com",
)

# Kubernetes helpers
def list_all_pods():
    # Create an instance of the CoreV1Api to interact with Kubernetes
    v1 = client.CoreV1Api()

    # Get all pods in all namespaces
    pods = v1.list_pod_for_all_namespaces(watch=False)

    # List to store pod details for table creation
    pod_details = []

    # Loop through each pod and extract relevant details
    for pod in pods.items:
        pod_info = {
            'Pod Name': pod.metadata.name,
            'Namespace': pod.metadata.namespace,
            'Status': pod.status.phase,
            'Node Name': pod.spec.node_name,
            'Pod IP': pod.status.pod_ip,
            'Containers': ', '.join([container.name for container in pod.spec.containers])
        }
        pod_details.append(pod_info)

    # Convert the list of dictionaries into a pandas DataFrame (table format)
    df = pd.DataFrame(pod_details)

    # Return the DataFrame (table format)
    return df.to_markdown(index=False)

def get_failed_pods():
    v1 = client.CoreV1Api()
    failed_pods = []
    pods = v1.list_pod_for_all_namespaces(watch=False)
    for pod in pods.items:
        for cs in pod.status.container_statuses or []:
            waiting = getattr(cs.state, "waiting", None)
            if waiting and waiting.reason in ["CrashLoopBackOff", "Error", "ImagePullBackOff"]:
                failed_pods.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "reason": waiting.reason,
                    "message": waiting.message,
                })

    df = pd.DataFrame(failed_pods)

    return df.to_markdown(index=False)

def restart_pod(name, namespace="default"):
    v1 = client.CoreV1Api()
    try:
        v1.delete_namespaced_pod(name=name, namespace=namespace)
        return f"✅ Pod '{name}' in namespace '{namespace}' has been deleted to trigger restart."
    except client.exceptions.ApiException as e:
        return f"❌ Error restarting pod: {e}"

def delete_deployment(name, namespace="default"):
    apps_v1 = client.AppsV1Api()
    try:
        apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
        return f"✅ Deployment '{name}' in namespace '{namespace}' deleted."
    except client.exceptions.ApiException as e:
        return f"❌ Error deleting deployment: {e}"

# Handle user input and call appropriate action
async def handle_user_query(user_input):
    prompt = f"""

You are a Kubernetes SRE agent with access to the Kubernetes API.

There are two types of responses:
1. **Actions**: These are commands you should execute. Actions include:
   - `restart_pod(name, namespace)`
   - `get_failed_pods(namespace)`
   - `delete_deployment(name, namespace)`
   - `list_all_pods`
   
   If an action is required, respond with a JSON object, for example:
   {{ "action": "restart_pod", "params": {{ "name": "nginx-crash", "namespace": "default" }} }}

2. **Suggestions**: These are helpful tips or Kubernetes commands that don't require execution. They can be kubectl commands, troubleshooting suggestions, or advice on what to check next.
   
   For suggestions, respond with helpful text like kubectl commands
If the user request is clear, take the appropriate action, but if you're uncertain, offer a **suggestion**.

---

User input: {user_input}
"""
    result = await az_model_client.create([UserMessage(content=prompt, source="user")])

    response = str(result.content)

    try:
        parsed = json.loads(response)
        action = parsed.get("action")
        params = parsed.get("params", {})

        if action == "restart_pod":
            return restart_pod(**params)
        elif action == "get_failed_pods":
            return get_failed_pods()
        elif action == "delete_deployment":
            return delete_deployment(**params)
        elif action == "list_all_pods":
            return list_all_pods()
        else:
            return f"⚠️ Unrecognized action or no action: {response}"

    except json.JSONDecodeError:
        return f"🧠 Suggestion:\n{response}"
    

# Main loop
# async def main():
#     # failed_pods = get_failed_pods()
#     # if failed_pods:
#     #     print("❌ Detected failed pods:")
#     #     for pod in failed_pods:
#     #         print(f"- {pod['name']} in {pod['namespace']}: {pod['reason']} ({pod['message']})")
#     # else:
#     #     print("✅ All pods look healthy.")

#     print("\n💬 Type natural language commands (e.g., 'restart nginx pod', 'get logs from busybox')\nType 'exit' to quit.")
#     while True:
#         user_input = input("🔧 Command> ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         response = await handle_user_query(user_input)
#         print(response)

#     await az_model_client.close()

# if __name__ == "__main__":
#     asyncio.run(main())