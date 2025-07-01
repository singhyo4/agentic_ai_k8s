# k8s_client.py
from kubernetes import client, config

def get_k8s_client():
    config.load_kube_config()  # Or use config.load_incluster_config() in a Pod
    return client.CoreV1Api()
