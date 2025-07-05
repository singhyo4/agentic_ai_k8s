# ui_app.py
import streamlit as st
from observer import get_failed_pods
from agent import analyze_issues
from actioner import restart_pod

st.set_page_config(page_title="DevOps AI Bot", page_icon="🤖")

st.title("🤖 Kubernetes AI Troubleshooting Bot")

if st.button("Check Cluster Health"):
    with st.spinner("Scanning for failed pods..."):
        failed = get_failed_pods()

    if not failed:
        st.success("✅ All pods healthy.")
    else:
        st.warning("⚠️ Issues detected:")
        for pod in failed:
            st.markdown(f"- **{pod['name']}** in `{pod['namespace']}` - `{pod['status']}`")
        
        if st.button("Analyze with LLM"):
            with st.spinner("🧠 Analyzing..."):
                insights = analyze_issues(failed)
            st.subheader("🧠 AI Recommendations")
            st.code(insights)

        # Optional fix buttons per pod
        for pod in failed:
            if pod["reason"] == "CrashLoopBackOff":
                if st.button(f"Restart {pod['name']}"):
                    restart_pod(pod["namespace"], pod["name"])
                    st.success(f"🔁 Restarted {pod['name']}")

pods_input = st.text_area("Paste pod info (JSON list):")
if st.button("Analyze"):
    import json
    try:
        pods = json.loads(pods_input)
        result = analyze_issues(pods)
        st.write(result)
    except Exception as e:
        st.error(f"Error: {e}")
