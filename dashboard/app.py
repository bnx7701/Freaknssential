
import os
import requests
import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Freaknssential | Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv(
    "FREAKNSSENTIAL_API",
    "http://127.0.0.1:8000"
).rstrip("/")


# =========================================================
# PREMIUM UI
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, rgba(110,40,180,.16), transparent 35%),
        radial-gradient(ellipse at 90% 80%, rgba(70,30,140,.13), transparent 35%),
        #09090f;
    color: #f5f3ff;
}

header[data-testid="stHeader"] {
    background: rgba(9,9,15,.7);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #100d1c, #09090f);
    border-right: 1px solid rgba(168,85,247,.2);
}

[data-testid="stSidebar"] * {
    color: #e9ddff;
}

h1, h2, h3 {
    color: #f5edff !important;
    letter-spacing: -0.7px;
}

p, label {
    color: #c4b5d9;
}

.glass-card {
    background: linear-gradient(
        135deg,
        rgba(125,70,190,.17),
        rgba(25,20,40,.72)
    );
    border: 1px solid rgba(168,85,247,.25);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(0,0,0,.22);
    transition: .25s ease;
    animation: appear .55s ease both;
}

.glass-card:hover {
    border-color: rgba(192,132,252,.65);
    box-shadow: 0 0 25px rgba(139,92,246,.16);
    transform: translateY(-3px);
}

.metric-label {
    color: #b9a6d4;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: #ffffff;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.hero {
    padding: 30px;
    border-radius: 22px;
    border: 1px solid rgba(168,85,247,.35);
    background: linear-gradient(
        115deg,
        rgba(91,33,182,.35),
        rgba(30,20,50,.75),
        rgba(76,29,149,.22)
    );
    background-size: 200% 200%;
    animation: gradientMove 8s ease infinite;
    box-shadow: 0 0 35px rgba(139,92,246,.12);
}

.hero h1 {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero p {
    color: #d8c8ee;
}

.stButton > button {
    background: linear-gradient(110deg, #7c3aed, #a855f7);
    color: white !important;
    border: 1px solid rgba(216,180,254,.4);
    border-radius: 10px;
    font-weight: 700;
    transition: .25s ease;
}

.stButton > button:hover {
    box-shadow: 0 0 20px rgba(168,85,247,.55);
    transform: translateY(-2px);
    border-color: #d8b4fe;
}

input, textarea, [data-baseweb="select"] {
    background-color: rgba(30,25,45,.8) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(168,85,247,.2);
    border-radius: 12px;
}

hr {
    border-color: rgba(168,85,247,.2);
}

@keyframes appear {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "admin" not in st.session_state:
    st.session_state.admin = None

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "audit_integrity" not in st.session_state:
    st.session_state.audit_integrity = None


# =========================================================
# API HELPERS
# =========================================================

def api_request(method, endpoint, **kwargs):
    headers = kwargs.pop("headers", {})

    if st.session_state.token:
        headers["Authorization"] = (
            f"Bearer {st.session_state.token}"
        )

    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            headers=headers,
            timeout=10,
            **kwargs,
        )

        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text}

        return response.status_code, data

    except requests.RequestException as error:
        return 0, {"detail": str(error)}


def get_json(endpoint, default=None):
    status, data = api_request("GET", endpoint)

    if status == 200:
        return data

    return default if default is not None else []


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_api_error(status, data):
    message = data.get("detail", "Request failed.")

    if status == 0:
        st.error(f"Backend connection failed: {message}")
    else:
        st.error(f"API error ({status}): {message}")


# =========================================================
# LOGIN
# =========================================================

if not st.session_state.token:

    st.markdown("""
    <div class="hero">
        <h1>🛡️ Freaknssential</h1>
        <p>AI Agent Security & Trust Management</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    _, login_col, _ = st.columns([1, 1.2, 1])

    with login_col:
        st.markdown("### Admin Authentication")
        st.caption("Sign in to access your security dashboard.")

        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter admin username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter admin password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

        if submitted:
            status, data = api_request(
                "POST",
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )

            if status == 200 and data.get("access_token"):
                st.session_state.token = data["access_token"]
                st.session_state.admin = username
                st.success("Authentication successful.")
                st.rerun()
            else:
                show_api_error(status, data)

    st.stop()


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown("# 🛡️ Freaknssential")
    st.caption("AI SECURITY COMMAND CENTER")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Agents",
            "Approvals",
            "Audit Center",
        ],
        key="page",
    )

    st.markdown("---")

    st.markdown("### ◈ Admin Session")
    st.success("● Authenticated")

    if st.session_state.admin:
        st.caption(f"Logged in as {st.session_state.admin}")

    if st.button("↪ Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.admin = None
        st.session_state.audit_integrity = None
        st.rerun()


# =========================================================
# MAIN HERO
# =========================================================

st.markdown("""
<div class="hero">
    <h1>Freaknssential</h1>
    <p>Autonomous AI Agent Security & Trust Layer</p>
</div>
""", unsafe_allow_html=True)

st.write("")


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    agents = get_json("/agents/", [])
    approvals = get_json("/approvals/pending", [])
    logs = get_json(
        "/logs/",
        {"total_events": 0, "events": []},
    )
    integrity = get_json(
        "/logs/verify",
        {"valid": False},
    )

    if isinstance(logs, list):
        events = logs
        total_events = len(logs)
    else:
        events = logs.get("events", [])
        total_events = logs.get("total_events", len(events))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Registered Agents", len(agents))

    with col2:
        metric_card("Pending Approvals", len(approvals))

    with col3:
        metric_card("Audit Events", total_events)

    with col4:
        metric_card(
            "System Security",
            "ACTIVE" if integrity.get("valid") else "CHECK",
        )

    st.markdown("## ✦ Security Intelligence")

    if integrity.get("valid"):
        st.success("✓ Audit Log Integrity — Verified")
    else:
        st.error("Audit integrity verification failed.")

    df = pd.DataFrame(events)

    if not df.empty and "status" in df.columns:

        status_counts = (
            df["status"]
            .fillna("unknown")
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Events")
        )

        left, right = st.columns([1.5, 1])

        with left:
            st.markdown("### ⚡ Security Activity Timeline")

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(
                    df["timestamp"],
                    errors="coerce",
                    utc=True,
                )

                timeline = df.dropna(
                    subset=["timestamp"]
                ).copy()

                if not timeline.empty:
                    timeline["Time"] = (
                        timeline["timestamp"].dt.floor("h")
                    )

                    activity = (
                        timeline.groupby(["Time", "status"])
                        .size()
                        .unstack(fill_value=0)
                        .sort_index()
                    )

                    st.area_chart(
                        activity,
                        height=300,
                    )
                else:
                    st.info("No valid timestamps available.")

        with right:
            st.markdown("### ◈ Action Distribution")

            st.bar_chart(
                status_counts.set_index("Status"),
                horizontal=True,
                height=300,
            )

        # Blocked action alerts
        blocked_df = pd.DataFrame()

        if "status" in df.columns:
            blocked_df = df[
                df["status"].astype(str).str.lower() == "blocked"
            ]

        blocked_count = len(blocked_df)

        st.markdown("### 🛡️ Threat Detection & Security Alerts")

        if blocked_count > 0:
            st.error(
                f"🚨 {blocked_count} suspicious or unauthorized "
                "action(s) blocked by Freaknssential!"
            )

            st.markdown("#### Recent Blocked Attempts")

            st.dataframe(
                blocked_df.head(5),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("✓ No blocked actions detected.")

        st.markdown("### ◉ Recent Security Events")

        display_df = df.copy()

        if "timestamp" in display_df.columns:
            display_df = display_df.sort_values(
                "timestamp",
                ascending=False,
            )

        st.dataframe(
            display_df.head(10),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No security activity recorded yet.")


# =========================================================
# AGENTS
# =========================================================

elif page == "Agents":

    st.markdown("## ✦ Agent Intelligence")
    st.caption(
        "Monitor registered AI agents and their security permissions."
    )

    agents = get_json("/agents/", [])

    if not isinstance(agents, list):
        agents = []

    total_agents = len(agents)

    permission_types = {
        action
        for agent in agents
        for action in agent.get("allowed_actions", [])
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Registered Agents", total_agents)

    with col2:
        metric_card("Permission Types", len(permission_types))

    with col3:
        metric_card(
            "Total Permissions",
            sum(
                len(agent.get("allowed_actions", []))
                for agent in agents
            ),
        )

    # Overall risk summary
    st.markdown("---")
    st.markdown("### 🛡️ Global Agent Risk Intelligence")

    risk_counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    for item in agents:
        level = str(item.get("risk_level", "LOW")).upper()

        if level in risk_counts:
            risk_counts[level] += 1

    risk_cols = st.columns(4)

    risk_colors = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴",
    }

    for index, level in enumerate(
        ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    ):
        with risk_cols[index]:
            metric_card(
                f"{risk_colors[level]} {level} RISK",
                risk_counts[level],
            )

    st.markdown("---")
    st.markdown("### ◈ Agent Directory")

    search = st.text_input(
        "⌕ Search agents",
        placeholder="Search by agent ID...",
    )

    filtered = [
        agent
        for agent in agents
        if search.lower() in agent.get("agent_id", "").lower()
    ]

    if filtered:

        st.caption(
            f"Showing {len(filtered)} of {total_agents} agents"
        )

        selected = st.selectbox(
            "Select an agent to inspect",
            [agent["agent_id"] for agent in filtered],
        )

        agent = next(
            item
            for item in filtered
            if item["agent_id"] == selected
        )

        actions = agent.get("allowed_actions", [])

        # Agent Risk Intelligence
        risk_score = max(
            0,
            min(100, int(agent.get("risk_score", 0) or 0))
        )

        risk_level = str(
            agent.get("risk_level", "LOW")
        ).upper()

        security_events = agent.get("security_events", {}) or {}

        st.markdown("### 🛡️ Agent Risk Intelligence")

        risk_colors = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴",
        }

        risk_col1, risk_col2 = st.columns(2)

        with risk_col1:
            st.metric(
                "Risk Score",
                f"{risk_score}/100",
            )

        with risk_col2:
            st.metric(
                "Risk Classification",
                f"{risk_colors.get(risk_level, '⚪')} {risk_level}",
            )

        st.progress(risk_score / 100)

        st.markdown("#### Security Event Breakdown")

        event_col1, event_col2, event_col3 = st.columns(3)

        with event_col1:
            st.metric(
                "Permission Violations",
                security_events.get("permission_violations", 0),
            )

        with event_col2:
            st.metric(
                "Invalid Signatures",
                security_events.get("invalid_signatures", 0),
            )

        with event_col3:
            st.metric(
                "Replay Attacks",
                security_events.get("replay_attacks", 0),
            )

        st.markdown("---")

        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">AGENT PROFILE</div>
                <h2>◈ {agent["agent_id"]}</h2>
                <p>Registered AI Agent</p>
                <span style="
                    color:#4ade80;
                    background:rgba(34,197,94,.12);
                    border:1px solid rgba(34,197,94,.3);
                    padding:6px 12px;
                    border-radius:20px;
                    font-size:12px;
                ">● REGISTERED</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔐 Permission Matrix")

        if actions:
            badges = "".join(
                f"""
                <span style="
                    display:inline-block;
                    margin:5px;
                    padding:9px 15px;
                    border-radius:10px;
                    color:#d8b4fe;
                    background:rgba(139,92,246,.13);
                    border:1px solid rgba(168,85,247,.35);
                ">✦ {action}</span>
                """
                for action in actions
            )

            st.markdown(
                f"<div>{badges}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("This agent has no allowed actions.")

        with st.expander("View raw agent data"):
            st.json(agent)

        st.markdown("---")
        st.markdown("### All Registered Agents")

        for item in filtered:
            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**◈ {item['agent_id']}**")
                    st.caption(
                        f"{len(item.get('allowed_actions', []))} "
                        "permission(s) assigned"
                    )

                with right:
                    st.markdown(
                        '<span style="color:#4ade80;">● Registered</span>',
                        unsafe_allow_html=True,
                    )

    else:
        st.info("No matching agents found.")


# =========================================================
# APPROVALS
# =========================================================

elif page == "Approvals":

    st.markdown("## ✦ Human Approval Center")
    st.caption(
        "Review and control sensitive actions requested by AI agents."
    )

    approvals = get_json("/approvals/pending", [])

    if not isinstance(approvals, list):
        approvals = []

    metric_card("Pending Actions", len(approvals))

    st.markdown("### ◈ Pending Approval Queue")

    if approvals:

        for approval in approvals:

            action_id = approval.get("action_id")
            if action_id is None:
                action_id = approval.get("id")

            agent_id = approval.get("agent_id", "Unknown agent")
            action_name = approval.get(
                "action",
                approval.get("action_type", "Unknown action"),
            )

            with st.container(border=True):

                st.markdown(f"### ⚡ {action_name}")

                st.markdown(f"**Agent:** `{agent_id}`")
                st.markdown(f"**Action ID:** `{action_id}`")

                if approval.get("created_at"):
                    st.caption(
                        f"Requested: {approval['created_at']}"
                    )

                if approval.get("details") is not None:
                    with st.expander("View action details"):
                        st.json(approval["details"])

                if approval.get("payload") is not None:
                    with st.expander("View action payload"):
                        st.json(approval["payload"])

                approve_col, reject_col = st.columns(2)

                with approve_col:
                    if st.button(
                        "✓ Approve Action",
                        key=f"approve_{action_id}",
                        use_container_width=True,
                    ):

                        if action_id is None:
                            st.error(
                                "This approval has no action ID."
                            )
                        else:
                            status, data = api_request(
                                "POST",
                                f"/approvals/{action_id}/approve",
                            )

                            if status in (200, 201):
                                st.success(
                                    "Action approved successfully."
                                )
                                st.rerun()
                            else:
                                show_api_error(status, data)

                with reject_col:
                    if st.button(
                        "✕ Reject Action",
                        key=f"reject_{action_id}",
                        use_container_width=True,
                    ):

                        if action_id is None:
                            st.error(
                                "This approval has no action ID."
                            )
                        else:
                            status, data = api_request(
                                "POST",
                                f"/approvals/{action_id}/reject",
                            )

                            if status in (200, 201):
                                st.success(
                                    "Action rejected successfully."
                                )
                                st.rerun()
                            else:
                                show_api_error(status, data)

    else:
        st.success("✓ No pending approvals. Your queue is clear.")


# =========================================================
# AUDIT CENTER
# =========================================================

elif page == "Audit Center":

    st.markdown("## ✦ Audit & Integrity Center")
    st.caption(
        "Inspect security events and verify tamper-evident audit logs."
    )

    logs = get_json(
        "/logs/",
        {"total_events": 0, "events": []},
    )

    if isinstance(logs, list):
        events = logs
        total_events = len(logs)
    else:
        events = logs.get("events", [])
        total_events = logs.get("total_events", len(events))

    # Manual integrity verification
    if st.button(
        "🔍 Verify Integrity",
        key="audit_verify_btn",
        use_container_width=True,
    ):
        with st.spinner("Verifying cryptographic audit chain..."):
            status, data = api_request(
                "GET",
                "/logs/verify",
            )

        if status == 200:
            st.session_state.audit_integrity = data
            st.success("Integrity verification completed!")
        else:
            show_api_error(status, data)

    # Initial verification
    if st.session_state.audit_integrity is None:
        integrity = get_json(
            "/logs/verify",
            {"valid": False},
        )
        st.session_state.audit_integrity = integrity

    integrity = st.session_state.audit_integrity or {
        "valid": False
    }

    col1, col2 = st.columns(2)

    with col1:
        metric_card("Total Audit Events", total_events)

    with col2:
        metric_card(
            "Integrity Status",
            "VERIFIED" if integrity.get("valid") else "FAILED",
        )

    st.markdown("### ◈ Cryptographic Integrity")

    if integrity.get("valid"):
        st.success("✓ Audit log integrity verified.")
    else:
        st.error("✕ Audit log integrity verification failed.")

    st.json(integrity)

    st.markdown("---")
    st.markdown("### ⚡ Security Event History")

    df = pd.DataFrame(events)

    if not df.empty:

        # Blocked Action Detection
        if "status" in df.columns:

            blocked_df = df[
                df["status"].astype(str).str.lower() == "blocked"
            ]

            blocked_count = len(blocked_df)

            st.markdown("### 🛡️ Threat Detection & Security Alerts")

            if blocked_count > 0:
                st.error(
                    f"🚨 {blocked_count} suspicious or unauthorized "
                    "action(s) blocked by Freaknssential!"
                )

                st.markdown("#### Recent Blocked Attempts")

                st.dataframe(
                    blocked_df.head(5),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("✓ No blocked actions detected.")

        # Replay Attack Detection
        replay_mask = pd.Series(False, index=df.index)

        if "reason" in df.columns:
            replay_mask = (
                df["reason"]
                .fillna("")
                .astype(str)
                .str.contains("Replay detected", case=False)
            )

        replay_count = int(replay_mask.sum())

        st.markdown("### 🚨 Replay Attack Detection")

        if replay_count > 0:
            st.error(
                f"🚨 {replay_count} replay attack(s) detected and blocked!"
            )
        else:
            st.success("✓ No replay attacks detected.")

        st.metric(
            "Total Replay Attacks Blocked",
            replay_count,
        )

        # Event filters
        if "status" in df.columns:

            statuses = sorted(
                df["status"].dropna().astype(str).unique().tolist()
            )

            selected_statuses = st.multiselect(
                "Filter by status",
                statuses,
                default=statuses,
            )

            df = df[
                df["status"].astype(str).isin(selected_statuses)
            ]

        if "timestamp" in df.columns:
            df = df.sort_values(
                "timestamp",
                ascending=False,
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "↓ Download Audit Events",
            data=df.to_csv(index=False),
            file_name="freaknssential_audit_events.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info("No audit events available yet.")


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8b7a9f;
        font-size:12px;
        padding:10px;
    ">
        FREAKNSSENTIAL · AI AGENT SECURITY SYSTEM
        <br>
        Cryptographic Trust · Permission Control · Human Approval
        <br>
        Intelligent Agent Risk Scoring · Replay Protection
    </div>
    """,
    unsafe_allow_html=True,
)
