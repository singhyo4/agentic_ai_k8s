# devops_bot.py
from observer import get_failed_pods
from agent import analyze_issues
from actioner import restart_pod

def run_bot():
    failed = get_failed_pods()
    if not failed:
        print("All pods healthy.")
        return

    print("⚠️ Issues detected:")
    for p in failed:
        print(f"- {p['name']} in {p['namespace']} - {p['status']}")

    analysis = analyze_issues(failed)
    print("\n🧠 Agent Recommendations:\n", analysis)

    # Optional: auto-restart pods (if CrashLoopBackOff)
    for pod in failed:
        if pod["reason"] == "CrashLoopBackOff":
            print(f"Restarting {pod['name']}...")
            restart_pod(pod["namespace"], pod["name"])

if __name__ == "__main__":
    run_bot()
