# actioner.py
from k8s_client import get_k8s_client

def restart_pod(namespace, pod_name):
    api = get_k8s_client()
    api.delete_namespaced_pod(name=pod_name, namespace=namespace)
