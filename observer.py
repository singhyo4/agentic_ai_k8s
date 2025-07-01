# observer.py
from k8s_client import get_k8s_client

def get_failed_pods():
    api = get_k8s_client()
    pods = api.list_pod_for_all_namespaces()
    failed = []
    for pod in pods.items:
        if pod.status.phase != "Running":
            failed.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "reason": pod.status.reason or "Unknown"
            })
    return failed
