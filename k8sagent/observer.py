# observer.py
from k8s_client import get_k8s_client

def get_failed_pods():
    v1 = get_k8s_client()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    failed = []
    for pod in pods.items:
        for cs in pod.status.container_statuses or []:
            waiting = getattr(cs.state, "waiting", None)
            if waiting and waiting.reason == "CrashLoopBackOff":
                failed.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": waiting.reason,
                    "reason": waiting.reason
                })
    return failed
