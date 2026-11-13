
import os
import requests
import streamlit as st

API_URL = os.getenv("FREAKNSSENTIAL_API", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Freaknssential | Security Console",
    page_icon="🛡️",
    layout="wide",
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: #080d18;
    color: #e5e7eb;
}
[data-testid="stSidebar"] {
    background: #0d1422;
}
.metric-card {
    background: #111c2e;
    border: 1px solid #24334a;
    padding: 20px;
    border-radius: 12px;
}
.metric-label { color: #94a3b8; font-size: 14px; }
.metric-value { color: #ffffff; font-size: 28px; font-weight: 700; }
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ---------- Session ----------
if "token" not in st.session_state:
    st.session_state.token = None

if "admin" not in st.session_state:
    st.session_state.admin = None


def api_request(method, endpoint, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            headers=headers,
            timeout=10,
            **kwargs,
        )
        return response
    except requests.RequestException as error:
        st.error(f"API connection failed: {error}")
        return None


# ---------- Login ----------
if not st.session_state.token:
    st.title("🛡️ Freaknssential")
    st.caption("AI Agent Security Gateway")
    st.divider()

    with st.form("login_form"):
        st.subheader("Admin Authentication")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        response = api_request(
            "POST",
            "/auth/login",
            data={"username": username, "password": password},
        )

        if response is not None:
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.session_state.admin = username
                st.rerun()
            else:
                st.error("Invalid credentials.")

    st.stop()


# ---------- Header ----------
header_col, logout_col = st.columns([5, 1])

with header_col:
    st.title("🛡️ Freaknssential")
    st.caption(f"Security Console  •  Administrator: {st.session_state.admin}")

with logout_col:
    if st.button("Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.admin = None
        st.rerun()

st.divider()


# ---------- Sidebar ----------
page = st.sidebar.radio(
    "NAVIGATION",
   ["Overview", "Agents", "Approvals", "Audit Logs"],
)

st.sidebar.caption("FREAKNSSENTIAL SECURITY SYSTEM")
st.sidebar.success("Admin session active")


# ---------- Overview ----------
if page == "Overview":
    st.subheader("Security Overview")

    pending_response = api_request("GET", "/approvals/pending")
    logs_response = api_request("GET", "/logs/")
    verify_response = api_request("GET", "/logs/verify")

    pending = pending_response.json() if (
        pending_response is not None and pending_response.ok
    ) else []

    logs = logs_response.json() if (
        logs_response is not None and logs_response.ok
    ) else {"total_events": 0, "events": []}

    verified = verify_response.json() if (
        verify_response is not None and verify_response.ok
    ) else {"valid": False}

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'PENDING APPROVALS</div><div class="metric-value">'
            f'{len(pending)}</div></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'AUDIT EVENTS</div><div class="metric-value">'
            f'{logs.get("total_events", 0)}</div></div>',
            unsafe_allow_html=True,
        )

    with col3:
        integrity = "VALID" if verified.get("valid") else "CHECK"
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">'
            f'AUDIT INTEGRITY</div><div class="metric-value">'
            f'{integrity}</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("System Status")

    if verified.get("valid"):
        st.success("Audit log integrity verified.")
    else:
        st.error("Audit log integrity check failed.")

    st.info("Agent listing is not available yet. The backend currently has no GET /agents endpoint.")


# ---------- Approvals ----------
elif page == "Approvals":
    st.subheader("Pending Action Approvals")

    response = api_request("GET", "/approvals/pending")

    if response is None:
        st.error("Could not connect to the API.")
    elif response.status_code == 401:
        st.error("Session expired. Please log in again.")
        st.session_state.token = None
        st.rerun()
    elif not response.ok:
        st.error(response.text)
    else:
        approvals = response.json()

        if not approvals:
            st.success("No pending approvals.")
        else:
            st.write(f"{len(approvals)} action(s) awaiting review.")

            for item in approvals:
                action_id = item["action_id"]
                action_data = item.get("action_data", {})

                with st.container(border=True):
                    st.write(f"**Action:** {action_data.get('action', 'Unknown')}")
                    st.write(f"**Agent:** {item.get('agent_id', 'Unknown')}")
                    st.write(f"**Resource:** {action_data.get('resource', 'Unknown')}")
                    st.caption(f"Action ID: {action_id}")
                    st.json(action_data)

                    approve_col, reject_col = st.columns(2)

                    with approve_col:
                        if st.button("Approve", key=f"approve_{action_id}", type="primary"):
                            result = api_request(
                                "POST",
                                f"/approvals/{action_id}/approve",
                            )
                            if result is not None and result.ok:
                                st.success("Action approved and processed.")
                                st.rerun()
                            elif result is not None:
                                st.error(result.text)

                    with reject_col:
                        if st.button("Reject", key=f"reject_{action_id}"):
                            result = api_request(
                                "POST",
                                f"/approvals/{action_id}/reject",
                            )
                            if result is not None and result.ok:
                                st.success("Action rejected.")
                                st.rerun()
                            elif result is not None:
                                st.error(result.text)


# ---------- Audit Logs ----------
elif page == "Audit Logs":
    st.subheader("Audit Trail")

    verify_col, refresh_col = st.columns(2)

    with verify_col:
        if st.button("Verify Audit Integrity"):
            result = api_request("GET", "/logs/verify")
            if result is not None and result.ok:
                data = result.json()
                if data.get("valid"):
                    st.success(data.get("message", "Integrity verified"))
                else:
                    st.error(data.get("message", "Integrity verification failed"))

    with refresh_col:
        refresh = st.button("Refresh Logs")

    response = api_request("GET", "/logs/")

    if response is not None and response.ok:
        data = response.json()
        events = data.get("events", [])

        st.metric("Total Audit Events", data.get("total_events", len(events)))

        if events:
            st.dataframe(events, use_container_width=True, hide_index=True)
        else:
            st.info("No audit events recorded.")
    elif response is not None:
        st.error(response.text)


elif page == "Agents":
    st.subheader("Registered AI Agents")

    response = api_request("GET", "/agents/")

    if response is not None and response.ok:
        agents = response.json()

        st.metric("Total Registered Agents", len(agents))

        if agents:
            st.dataframe(
                agents,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No agents registered.")