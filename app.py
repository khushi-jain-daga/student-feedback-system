"""Student Feedback Management System
A professional, institutional-grade feedback platform with secure authentication,
strict normal-user privacy guarantees, master student directory with registration numbers,
comprehensive analytics, and an advanced administrator control center.
"""
import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import streamlit as st

import database
import auth

# ------------------------------------------------------------------------------
# Page Configuration & Application Initialization
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Feedback Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cached application initialization (executes ONCE per Streamlit server process)
@st.cache_resource
def initialize_application():
    try:
        database.init_db()
        auth.seed_admin()
        print("[INIT] Application initialization complete.")
        return True
    except Exception as e:
        print(f"[INIT ERROR] Application initialization failed: {type(e).__name__}")
        raise

initialize_application()

# ------------------------------------------------------------------------------
# Visual Design System CSS (Modern Institutional Portal)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
}

body {
    background-color: #f8fafc;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 3rem;
    max-width: 1220px;
}

/* Primary and secondary button overrides */
button[kind="primary"] {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    border: 1px solid #0f172a !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08) !important;
    transition: all 0.15s ease !important;
}

button[kind="primary"]:hover {
    background-color: #1e293b !important;
    border-color: #1e293b !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.12) !important;
}

button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    border: 1px solid #cbd5e1 !important;
    transition: all 0.15s ease !important;
}

button[kind="secondary"]:hover {
    border-color: #94a3b8 !important;
    background-color: #f8fafc !important;
}

/* Top Subtle Header Bar for Landing */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0 1.1rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
}

.top-header-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.top-header-logo {
    width: 32px;
    height: 32px;
    background: #0f172a;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.15);
}

.top-header-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}

.top-header-title span {
    color: #64748b;
    font-weight: 500;
    font-size: 0.82rem;
    margin-left: 0.35rem;
}

.top-header-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.28rem 0.75rem;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.pulse-dot {
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

/* Landing Hero Section */
.landing-hero {
    background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
    padding: 2.2rem 2rem;
    border-radius: 16px;
    color: #ffffff;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.08);
    margin-bottom: 1.25rem;
    border: 1px solid #1e293b;
}

.landing-logo-mark {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1rem;
}

.landing-badge {
    display: inline-block;
    padding: 0.28rem 0.72rem;
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.25);
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #38bdf8;
}

.landing-title {
    font-size: 2.05rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.75rem;
    color: #ffffff;
}

.landing-subtitle {
    font-size: 0.95rem;
    color: #cbd5e1;
    font-weight: 400;
    line-height: 1.55;
    max-width: 520px;
}

/* 3 Compact Feature Cards on Landing */
.compact-cards-stack {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.compact-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.95rem 1.1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.compact-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px -2px rgba(15, 23, 42, 0.04);
}

.compact-card-icon {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #f0f9ff;
    border: 1px solid #e0f2fe;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0ea5e9;
    font-size: 0.95rem;
    margin-top: 2px;
}

.compact-card-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.15rem;
    letter-spacing: -0.01em;
}

.compact-card-text {
    font-size: 0.81rem;
    color: #64748b;
    line-height: 1.45;
}

/* Auth Container Card */
.auth-container-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
    margin-bottom: 1.5rem;
}

.auth-header-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.auth-header-caption {
    font-size: 0.84rem;
    color: #64748b;
    margin-bottom: 1.2rem;
    line-height: 1.5;
}

/* Institutional UI Card */
.ui-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03), 0 1px 2px -1px rgba(0, 0, 0, 0.03);
}

.ui-card-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
}

.ui-card-sub {
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 1.2rem;
    line-height: 1.5;
}

/* User Portal Top Navbar */
.nav-brand-container {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.nav-brand-logo {
    width: 36px;
    height: 36px;
    background: #0f172a;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.15);
}

.nav-brand-text {
    font-size: 1.02rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.nav-brand-sub {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
}

/* Segmented Control Styling */
div[data-testid="stSegmentedControl"] {
    display: flex;
    justify-content: center;
}

div[data-testid="stSegmentedControl"] button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.35rem 1rem !important;
    transition: all 0.15s ease !important;
}

/* User Home Dashboard */
.home-greeting-box {
    margin-bottom: 1.85rem;
}

.home-greeting-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.35rem;
}

.home-greeting-sub {
    font-size: 0.96rem;
    color: #64748b;
    line-height: 1.5;
}

.home-action-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.75rem 1.6rem 1.25rem 1.6rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 220px;
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.home-action-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px -2px rgba(15, 23, 42, 0.05);
}

.home-card-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 1rem;
}

.icon-blue { background: #f0f9ff; border: 1px solid #e0f2fe; color: #0284c7; }
.icon-slate { background: #f8fafc; border: 1px solid #e2e8f0; color: #334155; }

.home-card-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.35rem;
    letter-spacing: -0.01em;
}

.home-card-desc {
    font-size: 0.88rem;
    color: #64748b;
    line-height: 1.5;
    margin-bottom: 1.25rem;
}

.home-stats-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 0.5rem;
}

.progress-track {
    background: #f1f5f9;
    height: 8px;
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 1.2rem;
    border: 1px solid #e2e8f0;
}

.progress-fill {
    height: 100%;
    border-radius: 9999px;
    background: linear-gradient(90deg, #0ea5e9, #0284c7);
}

.home-privacy-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    margin-top: 1.75rem;
    color: #475569;
    font-size: 0.84rem;
}

/* Directory Page */
.dir-header-box {
    margin-bottom: 1.4rem;
}

.dir-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.dir-subtitle {
    font-size: 0.92rem;
    color: #64748b;
    margin-bottom: 1rem;
}

/* Directory Person Card */
.pcard-body {
    padding-bottom: 0.75rem;
}

.pcard-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.pcard-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: -0.02em;
}

.pcard-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.35rem;
}

.pcard-reg {
    margin-bottom: 0.35rem;
}

.pcard-dept {
    font-size: 0.78rem;
    color: #64748b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.4;
}

.status-submitted {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
}

.badge-reg {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    background: #f0f9ff;
    color: #0284c7;
    border: 1px solid #bae6fd;
    border-radius: 6px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.22rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-student { background-color: #f0f9ff; color: #0284c7; border: 1px solid #bae6fd; }
.badge-teacher { background-color: #f8fafc; color: #334155; border: 1px solid #e2e8f0; }
.badge-admin   { background-color: #fefce8; color: #854d0e; border: 1px solid #fef08a; }
.badge-user    { background-color: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }
.badge-active  { background-color: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.badge-inactive{ background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* Feedback Detail View */
.feedback-container {
    max-width: 740px;
    margin: 0 auto;
}

.target-profile-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1.1rem;
    margin: 1.25rem 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.target-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.15rem;
    flex-shrink: 0;
}

.target-info {
    flex-grow: 1;
}

.target-name-row {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 0.25rem;
}

.target-name {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
}

.target-sub {
    font-size: 0.85rem;
    color: #64748b;
}

.privacy-notice-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}

.privacy-notice-icon {
    font-size: 1.1rem;
    flex-shrink: 0;
    margin-top: 1px;
}

.privacy-notice-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.2rem;
}

.privacy-notice-desc {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.45;
}

/* Post-submission Success Card */
.submission-success-card {
    background: #ffffff;
    border: 1px solid #bbf7d0;
    border-radius: 18px;
    padding: 2.8rem 2rem;
    text-align: center;
    max-width: 540px;
    margin: 2rem auto;
    box-shadow: 0 4px 16px rgba(22, 163, 74, 0.06);
}

.success-icon-badge {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #f0fdf4;
    border: 1.5px solid #86efac;
    color: #16a34a;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
}

.success-card-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}

.success-card-desc {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1.75rem;
}

/* KPI Cards (Admin) */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.1rem;
    margin-bottom: 1.8rem;
}

.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.35rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: #cbd5e1;
    box-shadow: 0 6px 14px -3px rgba(15, 23, 42, 0.05);
}

.kpi-label {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.kpi-sub {
    font-size: 0.78rem;
    color: #0ea5e9;
    font-weight: 500;
    margin-top: 0.35rem;
}

/* Review Item in Feed/Detail */
.review-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.35rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    transition: border-color 0.15s ease;
}

.review-item:hover {
    border-color: #cbd5e1;
}

.review-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.review-reviewer {
    font-weight: 700;
    font-size: 0.92rem;
    color: #0f172a;
}

.review-date {
    font-size: 0.76rem;
    color: #94a3b8;
}

.review-stars {
    color: #f59e0b;
    font-size: 0.95rem;
    letter-spacing: 1px;
}

.review-text-box {
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.55;
    background: #f8fafc;
    border-left: 3px solid #0ea5e9;
    padding: 0.8rem 0.95rem;
    border-radius: 6px;
    margin-top: 0.5rem;
}

/* Empty State Box */
.empty-state {
    text-align: center;
    padding: 2.8rem 2rem;
    background: #f8fafc;
    border: 1.5px dashed #cbd5e1;
    border-radius: 14px;
    margin: 1.25rem 0;
}

.empty-state-icon {
    font-size: 2.2rem;
    margin-bottom: 0.6rem;
}

.empty-state-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.3rem;
}

.empty-state-text {
    font-size: 0.86rem;
    color: #64748b;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Footer */
.app-footer {
    text-align: center;
    padding: 2.2rem 0 1rem 0;
    margin-top: 3.5rem;
    border-top: 1px solid #e2e8f0;
    font-size: 0.8rem;
    color: #64748b;
    letter-spacing: 0.02em;
}

.app-footer-brand {
    font-weight: 600;
    color: #334155;
    margin-bottom: 0.25rem;
}

.app-footer-security {
    font-size: 0.75rem;
    color: #94a3b8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.5rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .landing-title {
        font-size: 1.6rem;
    }
    .home-greeting-title {
        font-size: 1.6rem;
    }
    .top-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# State Initialization
# ------------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "review_submitted" not in st.session_state:
    st.session_state.review_submitted = False

if "auth_flash_success" not in st.session_state:
    st.session_state.auth_flash_success = None

if "admin_active_tab" not in st.session_state:
    st.session_state.admin_active_tab = "Overview"

if "user_nav" not in st.session_state:
    st.session_state.user_nav = "Home"

if "active_target_person" not in st.session_state:
    st.session_state.active_target_person = None

if "active_target_type" not in st.session_state:
    st.session_state.active_target_type = "student"

if "student_page" not in st.session_state:
    st.session_state.student_page = 1

# Review filter states for Admin Reset button
if "rf_type" not in st.session_state:
    st.session_state.rf_type = "All"
if "rf_rating" not in st.session_state:
    st.session_state.rf_rating = "All"
if "rf_person" not in st.session_state:
    st.session_state.rf_person = "All"
if "rf_date" not in st.session_state:
    st.session_state.rf_date = "All"
if "rf_search" not in st.session_state:
    st.session_state.rf_search = ""


# ------------------------------------------------------------------------------
# Avatar & Formatting Helpers
# ------------------------------------------------------------------------------
AVATAR_PALETTE = [
    ("#e0f2fe", "#0369a1"),  # Light Sky / Dark Sky
    ("#f0fdf4", "#15803d"),  # Light Green / Dark Green
    ("#fef3c7", "#b45309"),  # Light Amber / Dark Amber
    ("#f3e8ff", "#7e22ce"),  # Light Purple / Dark Purple
    ("#fce7f3", "#be185d"),  # Light Pink / Dark Pink
    ("#e0e7ff", "#4338ca"),  # Light Indigo / Dark Indigo
    ("#ccfbf1", "#0f766e"),  # Light Teal / Dark Teal
]

def get_avatar_style(name: str):
    """Return deterministic background and foreground colors for avatar based on name."""
    if not name:
        return ("#f1f5f9", "#475569")
    idx = sum(ord(c) for c in name) % len(AVATAR_PALETTE)
    return AVATAR_PALETTE[idx]

def get_initials(name: str) -> str:
    """Extract 1 or 2 letter initials from a name (e.g. 'AMIT AGARWAL' -> 'AA', 'Dr. Sharma' -> 'S')."""
    if not name:
        return "??"
    parts = [p for p in name.strip().split() if p and not p.lower().rstrip('.').startswith(('dr', 'prof', 'mr', 'ms', 'mrs', 'er'))]
    if not parts:
        parts = [p.rstrip('.') for p in name.strip().split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif parts:
        return parts[0][:2].upper()
    return "??"

def format_datetime(val) -> str:
    """Safely format database timestamp for clean display."""
    if val is None:
        return "—"
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime("%Y-%m-%d %H:%M")
    val_str = str(val)
    if len(val_str) >= 16:
        return val_str[:16].replace("T", " ")
    return val_str

def rating_stars(rating: int) -> str:
    """Render numeric rating as visual star symbols (e.g. ★★★★☆)."""
    r = int(rating or 0)
    return "★" * r + "☆" * (5 - r)

def rating_stars_label(rating: int) -> str:
    """Render star rating with textual academic descriptor."""
    labels = {
        1: "Poor",
        2: "Fair",
        3: "Good",
        4: "Very Good",
        5: "Excellent"
    }
    r = int(rating or 0)
    stars = "★" * r + "☆" * (5 - r)
    return f"{stars} ({r} — {labels.get(r, 'N/A')})"


# ==============================================================================
# VIEW 1: LANDING & AUTHENTICATION PAGE
# ==============================================================================
def render_landing_page():
    # Top Subtle Header
    st.markdown("""
    <div class="top-header">
        <div class="top-header-brand">
            <div class="top-header-logo">🎓</div>
            <div class="top-header-title">Student Feedback Management System <span>• Academic Portal</span></div>
        </div>
        <div class="top-header-badge">
            <span class="pulse-dot"></span> Secure Portal
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Left / Right Responsive Layout (Desktop balanced 47/53 layout)
    col_left, col_right = st.columns([47, 53], gap="large")

    with col_left:
        st.markdown("""
        <div class="landing-hero">
            <div class="landing-logo-mark">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V12C3 17.52 6.84 22.74 12 24C17.16 22.74 21 17.52 21 12V7L12 2Z" fill="rgba(14, 165, 233, 0.18)" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 7L16 9.5V13.5L12 16L8 13.5V9.5L12 7Z" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="landing-badge">Institutional Evaluation Portal</span>
            </div>
            <div class="landing-title">Student Feedback<br>Management System</div>
            <div class="landing-subtitle">
                Secure, structured peer and faculty evaluation for academic institutions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="compact-cards-stack">
            <div class="compact-card">
                <div class="compact-card-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                </div>
                <div>
                    <div class="compact-card-title">Private Reviews</div>
                    <div class="compact-card-text">Reviews are visible only to authorized administrators.</div>
                </div>
            </div>
            <div class="compact-card">
                <div class="compact-card-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                </div>
                <div>
                    <div class="compact-card-title">Verified Directory</div>
                    <div class="compact-card-text">Students are identified using official registration numbers.</div>
                </div>
            </div>
            <div class="compact-card">
                <div class="compact-card-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                </div>
                <div>
                    <div class="compact-card-title">Fair Evaluation</div>
                    <div class="compact-card-text">Self-review and duplicate review protections are enforced.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="auth-container-card">', unsafe_allow_html=True)

        # Persistent authentication flash message after registration
        if st.session_state.get("auth_flash_success"):
            flash_msg = st.session_state.auth_flash_success if isinstance(st.session_state.auth_flash_success, str) else "✓ Account created successfully\n\nYou can now sign in using your username, email, or registration number."
            st.success(flash_msg)
            st.session_state.auth_flash_success = None

        auth_mode = st.radio(
            "Account access",
            ["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode_selector"
        )

        # TAB 1: SIGN IN
        if auth_mode == "Sign In":
            st.markdown('<div class="auth-header-title">Welcome Back</div><div class="auth-header-caption">Sign in with your registered username, email address, or registration number.</div>', unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input(
                    "Username, Email or Registration Number",
                    placeholder="e.g. user@university.edu, username, or 23BCON0028"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your account password"
                )
                submit_login = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

            if submit_login:
                if not login_id.strip() or not login_password:
                    st.error("Please enter both your identifier and password.")
                else:
                    user_data = auth.authenticate(login_id.strip(), login_password)
                    if user_data:
                        st.session_state.user = user_data
                        st.session_state.user_nav = "Home"
                        st.session_state.active_target_person = None
                        st.session_state.review_submitted = False
                        st.rerun()
                    else:
                        st.error("Account not found or password is incorrect.")

        # TAB 2: CREATE ACCOUNT
        else:
            st.markdown('<div class="auth-header-title">Create Account</div><div class="auth-header-caption">Register a new account to participate in academic reviews.</div>', unsafe_allow_html=True)

            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. AMIT AGARWAL")
                reg_user = st.text_input("Username", placeholder="e.g. amitag (minimum 3 characters)")
                reg_email = st.text_input("Email Address", placeholder="e.g. amit.agarwal@university.edu")
                reg_no = st.text_input(
                    "Registration Number (Students only — e.g. 23BCON0028)",
                    placeholder="e.g. 23BCON0028"
                )
                reg_pass = st.text_input("Password (min 8 characters)", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if submit_reg:
                if not reg_name.strip() or not reg_user.strip() or not reg_email.strip():
                    st.error("Please complete your name, username, and email.")
                elif reg_pass != reg_confirm:
                    st.error("Passwords do not match. Please verify both password entries.")
                else:
                    try:
                        user_id = auth.register_user(
                            name=reg_name.strip(),
                            username=reg_user.strip(),
                            email=reg_email.strip(),
                            password=reg_pass,
                            role='user',
                            registration_no=reg_no.strip() if reg_no and reg_no.strip() else None
                        )
                        user_data = auth.authenticate(reg_user.strip(), reg_pass)
                        if user_data:
                            st.session_state.user = user_data
                            st.session_state.new_account_created = True
                            st.session_state.user_nav = "Home"
                            st.session_state.review_submitted = False
                        else:
                            st.session_state.auth_flash_success = "✓ Account created successfully. You can now sign in using your username, email, or registration number."
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))
                    except Exception as err:
                        st.error(f"Registration failed: {err}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Footer
    st.markdown("""
    <div class="app-footer">
        <div class="app-footer-brand">Student Feedback Management System</div>
        <div class="app-footer-security">Secure • Private • Role-Based Access</div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# VIEW 2: NORMAL USER PORTAL (Home → Students → Teachers → My Profile)
# ==============================================================================
def render_user_navbar(user):
    """Clean institutional top navbar with active navigation highlighting and user credentials."""
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_brand, col_nav, col_profile = st.columns([2.8, 4.4, 2.8], vertical_alignment="center")

    with col_brand:
        st.markdown("""
        <div class="nav-brand-container">
            <div class="nav-brand-logo">🎓</div>
            <div>
                <div class="nav-brand-text">Student Feedback System</div>
                <div class="nav-brand-sub">Institutional Portal</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_nav:
        nav_options = ["Home", "Students", "Teachers", "My Profile"]
        cur_nav = st.session_state.get("user_nav", "Home")
        if cur_nav == "Feedback Form":
            highlight = "Students" if st.session_state.get("active_target_type") == "student" else "Teachers"
        else:
            highlight = cur_nav if cur_nav in nav_options else "Home"

        selected = st.segmented_control(
            "User Navigation",
            options=nav_options,
            default=highlight,
            label_visibility="collapsed",
            key="user_top_nav_control"
        )
        if selected and selected != cur_nav and cur_nav != "Feedback Form":
            st.session_state.user_nav = selected
            st.session_state.active_target_person = None
            st.session_state.review_submitted = False
            st.rerun()
        elif selected and selected != highlight and cur_nav == "Feedback Form":
            st.session_state.user_nav = selected
            st.session_state.active_target_person = None
            st.session_state.review_submitted = False
            st.rerun()

    with col_profile:
        col_uinfo, col_ubtn = st.columns([2.5, 1.2], vertical_alignment="center")
        with col_uinfo:
            reg_display = f"<span class='badge-reg'>{user.get('registration_no')}</span>" if user.get('registration_no') else "<span class='badge badge-user'>Standard</span>"
            st.markdown(f"""
            <div style="text-align: right; line-height: 1.25;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">{user['name']}</div>
                <div style="margin-top: 2px;">{reg_display}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ubtn:
            if st.button("Sign Out", key="user_top_signout", help="Sign out of your account"):
                st.session_state.user = None
                st.session_state.user_nav = "Home"
                st.session_state.active_target_person = None
                st.session_state.review_submitted = False
                st.rerun()

    st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin: 0.6rem 0 1.85rem 0;'>", unsafe_allow_html=True)


def render_user_home(user):
    """User Home dashboard with greeting, progress metrics, and direct directory browsing CTAs."""
    first_name = user['name'].split()[0] if user.get('name') else 'Student'

    st.markdown(f"""
    <div class="home-greeting-box">
        <div class="home-greeting-title">Hello, {first_name} 👋</div>
        <div class="home-greeting-sub">Share constructive feedback and help your academic community grow.</div>
    </div>
    """, unsafe_allow_html=True)

    # Compute numbers for Student and Teacher cards
    eligible_students = database.list_people(
        person_type="student",
        active_only=True,
        exclude_user_id=user['id'],
        exclude_name=user['name'],
        exclude_regno=user.get('registration_no')
    )
    total_students = len(eligible_students)

    active_teachers = database.list_people(
        person_type="teacher",
        active_only=True
    )
    total_teachers = len(active_teachers)

    reviews_by_type = database.count_user_reviews_by_type(user['id'])
    reviewed_students = min(reviews_by_type.get('student', 0), total_students)
    reviewed_teachers = min(reviews_by_type.get('teacher', 0), total_teachers)

    st_pct = int((reviewed_students / total_students * 100)) if total_students > 0 else 0
    t_pct = int((reviewed_teachers / total_teachers * 100)) if total_teachers > 0 else 0

    col_c1, col_c2 = st.columns(2, gap="large")

    with col_c1:
        st.markdown(f"""
        <div class="home-action-card">
            <div>
                <div class="home-card-icon-wrap icon-blue">🎓</div>
                <div class="home-card-title">Student Feedback</div>
                <div class="home-card-desc">Review your classmates and share constructive feedback.</div>
                <div class="home-stats-meta">
                    <span>{reviewed_students} of {total_students} reviewed</span>
                    <span>{st_pct}% completed</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {st_pct}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Students →", key="home_browse_students", type="primary", use_container_width=True):
            st.session_state.user_nav = "Students"
            st.session_state.active_target_person = None
            st.session_state.review_submitted = False
            st.rerun()

    with col_c2:
        st.markdown(f"""
        <div class="home-action-card">
            <div>
                <div class="home-card-icon-wrap icon-slate">👨‍🏫</div>
                <div class="home-card-title">Teacher Feedback</div>
                <div class="home-card-desc">Share feedback about faculty members.</div>
                <div class="home-stats-meta">
                    <span>{reviewed_teachers} of {total_teachers} reviewed</span>
                    <span>{t_pct}% completed</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {t_pct}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Teachers →", key="home_browse_teachers", type="primary", use_container_width=True):
            st.session_state.user_nav = "Teachers"
            st.session_state.active_target_person = None
            st.session_state.review_submitted = False
            st.rerun()

    # Small Privacy Notice
    st.markdown("""
    <div class="home-privacy-banner">
        <span style="font-size:1.15rem;">🔒</span>
        <span>Your individual feedback is visible only to authorized administrators.</span>
    </div>
    """, unsafe_allow_html=True)


def render_student_directory(user):
    """Student Directory with search, responsive cards, submitted state, and pagination."""
    st.markdown("""
    <div class="dir-header-box">
        <div class="dir-title">Student Feedback</div>
        <div class="dir-subtitle">Choose a student and share constructive feedback.</div>
    </div>
    """, unsafe_allow_html=True)

    col_search, col_cnt = st.columns([3, 1], vertical_alignment="center")
    with col_search:
        search_query = st.text_input(
            "Search by name or registration number",
            placeholder="Search by name or registration number (e.g. AMIT or 23BCON0028)...",
            label_visibility="collapsed",
            key="st_dir_search_input"
        )

    # Fetch eligible students (strictly excluding logged-in user)
    students = database.list_people(
        person_type="student",
        active_only=True,
        exclude_user_id=user['id'],
        exclude_name=user['name'],
        exclude_regno=user.get('registration_no'),
        search_query=search_query
    )

    with col_cnt:
        st.markdown(f"<div style='text-align:right; font-size:0.85rem; color:#64748b; font-weight:600;'>{len(students)} available</div>", unsafe_allow_html=True)

    if not students:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-title">No Students Found</div>
            <div class="empty-state-text">No active classmates match your search criteria.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    user_reviews = database.get_user_reviewed_person_ids(user['id'])

    # Pagination: 12 cards per page (3 cards x 4 rows)
    PAGE_SIZE = 12
    total_pages = max(1, (len(students) + PAGE_SIZE - 1) // PAGE_SIZE)
    if "student_page" not in st.session_state or st.session_state.student_page > total_pages:
        st.session_state.student_page = 1

    current_page = st.session_state.student_page
    start_idx = (current_page - 1) * PAGE_SIZE
    page_students = students[start_idx : start_idx + PAGE_SIZE]

    for row_start in range(0, len(page_students), 3):
        chunk = page_students[row_start : row_start + 3]
        cols = st.columns(3)
        for i, s in enumerate(chunk):
            with cols[i]:
                with st.container(border=True):
                    has_reviewed = s['id'] in user_reviews
                    bg_color, fg_color = get_avatar_style(s['name'])
                    initials = get_initials(s['name'])
                    reg = s.get('registration_no') or 'N/A'
                    dept = s.get('department') or 'General'

                    status_html = '<span class="status-submitted">✓ Submitted</span>' if has_reviewed else ''
                    card_html = (
                        f'<div class="pcard-body">'
                        f'<div class="pcard-top">'
                        f'<div class="pcard-avatar" style="background-color: {bg_color}; color: {fg_color};">{initials}</div>'
                        f'{status_html}'
                        f'</div>'
                        f'<div class="pcard-name" title="{s["name"]}">{s["name"]}</div>'
                        f'<div class="pcard-reg"><span class="badge-reg">{reg}</span></div>'
                        f'<div class="pcard-dept">{dept}</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    btn_text = "Edit Feedback" if has_reviewed else "Give Feedback"
                    btn_kind = "secondary" if has_reviewed else "primary"
                    if st.button(btn_text, key=f"s_card_btn_{s['id']}", type=btn_kind, use_container_width=True):
                        st.session_state.active_target_person = s
                        st.session_state.active_target_type = "student"
                        st.session_state.user_nav = "Feedback Form"
                        st.session_state.review_submitted = False
                        st.rerun()

    # Pagination controls
    if total_pages > 1:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        col_p_prev, col_p_info, col_p_next = st.columns([1, 2, 1], vertical_alignment="center")
        with col_p_prev:
            if st.button("← Previous", disabled=(current_page <= 1), use_container_width=True, key="s_prev_btn"):
                st.session_state.student_page = current_page - 1
                st.rerun()
        with col_p_info:
            st.markdown(f"<div style='text-align:center; font-size:0.85rem; color:#64748b;'>Page <strong>{current_page}</strong> of <strong>{total_pages}</strong> ({len(students)} total)</div>", unsafe_allow_html=True)
        with col_p_next:
            if st.button("Next →", disabled=(current_page >= total_pages), use_container_width=True, key="s_next_btn"):
                st.session_state.student_page = current_page + 1
                st.rerun()


def render_teacher_directory(user):
    """Teacher Directory with search, cards, and Give/Edit Feedback state."""
    st.markdown("""
    <div class="dir-header-box">
        <div class="dir-title">Teacher Feedback</div>
        <div class="dir-subtitle">Share feedback about faculty members.</div>
    </div>
    """, unsafe_allow_html=True)

    col_search, col_cnt = st.columns([3, 1], vertical_alignment="center")
    with col_search:
        search_query = st.text_input(
            "Search by teacher name or department",
            placeholder="Search by teacher name or department...",
            label_visibility="collapsed",
            key="t_dir_search_input"
        )

    teachers = database.list_people(
        person_type="teacher",
        active_only=True,
        search_query=search_query
    )

    with col_cnt:
        st.markdown(f"<div style='text-align:right; font-size:0.85rem; color:#64748b; font-weight:600;'>{len(teachers)} faculty members</div>", unsafe_allow_html=True)

    if not teachers:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">👨‍🏫</div>
            <div class="empty-state-title">No Teachers Found</div>
            <div class="empty-state-text">No active faculty members match your search criteria.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    user_reviews = database.get_user_reviewed_person_ids(user['id'])

    for row_start in range(0, len(teachers), 3):
        chunk = teachers[row_start : row_start + 3]
        cols = st.columns(3)
        for i, t in enumerate(chunk):
            with cols[i]:
                with st.container(border=True):
                    has_reviewed = t['id'] in user_reviews
                    bg_color, fg_color = get_avatar_style(t['name'])
                    initials = get_initials(t['name'])
                    dept = t.get('department') or 'Faculty'

                    status_html = '<span class="status-submitted">✓ Submitted</span>' if has_reviewed else ''
                    card_html = (
                        f'<div class="pcard-body">'
                        f'<div class="pcard-top">'
                        f'<div class="pcard-avatar" style="background-color: {bg_color}; color: {fg_color};">{initials}</div>'
                        f'{status_html}'
                        f'</div>'
                        f'<div class="pcard-name" title="{t["name"]}">{t["name"]}</div>'
                        f'<div class="pcard-dept">{dept}</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    btn_text = "Edit Feedback" if has_reviewed else "Give Feedback"
                    btn_kind = "secondary" if has_reviewed else "primary"
                    if st.button(btn_text, key=f"t_card_btn_{t['id']}", type=btn_kind, use_container_width=True):
                        st.session_state.active_target_person = t
                        st.session_state.active_target_type = "teacher"
                        st.session_state.user_nav = "Feedback Form"
                        st.session_state.review_submitted = False
                        st.rerun()


def render_feedback_detail(user):
    """Dedicated feedback submission screen with target card, privacy info, rating, and written comment."""
    target = st.session_state.get("active_target_person")
    target_type = st.session_state.get("active_target_type", "student")

    if not target:
        st.session_state.user_nav = "Students" if target_type == "student" else "Teachers"
        st.rerun()
        return

    # Post-submission clean success state
    if st.session_state.get("review_submitted"):
        st.markdown("""
        <div class="submission-success-card">
            <div class="success-icon-badge">✓</div>
            <div class="success-card-title">Feedback submitted successfully</div>
            <div class="success-card-desc">Your feedback has been securely recorded.</div>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            back_dest = "Students" if target_type == "student" else "Teachers"
            if st.button(f"Back to {back_dest}", type="primary", use_container_width=True, key="succ_back_btn"):
                st.session_state.user_nav = back_dest
                st.session_state.active_target_person = None
                st.session_state.review_submitted = False
                st.rerun()
        with col_s2:
            if st.button("Submit Another Feedback", use_container_width=True, key="succ_another_btn"):
                st.session_state.user_nav = "Students"
                st.session_state.active_target_person = None
                st.session_state.review_submitted = False
                st.rerun()
        return

    # Main Feedback Form
    st.markdown('<div class="feedback-container">', unsafe_allow_html=True)

    back_text = "← Back to Students" if target_type == "student" else "← Back to Teachers"
    if st.button(back_text, key="fback_nav_back"):
        st.session_state.user_nav = "Students" if target_type == "student" else "Teachers"
        st.session_state.active_target_person = None
        st.rerun()

    # Target Card
    bg_color, fg_color = get_avatar_style(target['name'])
    initials = get_initials(target['name'])
    type_badge = '<span class="badge-student">Student</span>' if target_type == 'student' else '<span class="badge-teacher">Faculty</span>'
    meta_info = f"Registration Number: <code>{target['registration_no']}</code>" if target.get('registration_no') else f"Department: {target.get('department')}"

    st.markdown(f"""
    <div class="target-profile-card">
        <div class="target-avatar" style="background-color: {bg_color}; color: {fg_color};">{initials}</div>
        <div class="target-info">
            <div class="target-name-row">
                <span class="target-name">{target['name']}</span>
                {type_badge}
            </div>
            <div class="target-sub">{meta_info} • {target.get('department', '')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Privacy Card
    st.markdown("""
    <div class="privacy-notice-card">
        <div class="privacy-notice-icon">🔒</div>
        <div>
            <div class="privacy-notice-title">Private Feedback</div>
            <div class="privacy-notice-desc">Your rating and written feedback are visible only to authorized administrators.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Existing review check (update policy)
    existing_rev = database.get_user_review_for_person(user['id'], target['id'])
    if existing_rev:
        st.info("You have reviewed this person before. Submitting again will update your previous feedback.")
        init_rating = int(existing_rev['rating'])
        init_comment = str(existing_rev['review_text'])
        submit_btn_text = "Update Feedback"
    else:
        init_rating = 5
        init_comment = ""
        submit_btn_text = "Submit Feedback"

    with st.form("feedback_submission_form"):
        st.markdown("**Overall Rating**")
        rating_labels = {
            1: "1 — Poor",
            2: "2 — Fair",
            3: "3 — Good",
            4: "4 — Very Good",
            5: "5 — Excellent"
        }
        rating = st.select_slider(
            "Overall Rating",
            options=[1, 2, 3, 4, 5],
            value=init_rating,
            format_func=lambda x: f"{rating_stars(x)}  {rating_labels[x]}",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown("**Written Feedback**")
        comment = st.text_area(
            "Written Feedback",
            value=init_comment,
            placeholder="Share specific, constructive, and respectful feedback...",
            height=130,
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        col_sub, col_can = st.columns([1.5, 1])
        with col_sub:
            submit_clicked = st.form_submit_button(submit_btn_text, type="primary", use_container_width=True)
        with col_can:
            cancel_clicked = st.form_submit_button("Cancel", use_container_width=True)

    if cancel_clicked:
        st.session_state.user_nav = "Students" if target_type == "student" else "Teachers"
        st.session_state.active_target_person = None
        st.rerun()

    if submit_clicked:
        if not comment.strip():
            st.error("Please provide written feedback before submitting.")
        else:
            try:
                database.submit_or_update_review(
                    reviewer_id=user['id'],
                    person_id=target['id'],
                    rating=int(rating),
                    review_text=comment.strip()
                )
                st.session_state.review_submitted = True
                st.rerun()
            except ValueError as err:
                st.error(str(err))
            except Exception as err:
                st.error(f"Failed to submit feedback: {err}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_my_profile(user):
    """User profile credentials and security password change."""
    st.markdown("""
    <div class="dir-header-box">
        <div class="dir-title">My Profile</div>
        <div class="dir-subtitle">Manage your verified identity and security credentials.</div>
    </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2 = st.columns([1.2, 1], gap="large")

    with col_p1:
        reg_display = user.get('registration_no') or 'Not Linked'
        created_str = format_datetime(user.get('created_at'))

        st.markdown(f"""
        <div class="ui-card">
            <div class="ui-card-header">Account Profile</div>
            <div class="ui-card-sub">Your registered credentials in the institutional feedback directory.</div>
            <div style="font-size:0.92rem; color:#334155; line-height:2;">
                <div><strong>Full Name:</strong> {user['name']}</div>
                <div><strong>Username:</strong> @{user['username']}</div>
                <div><strong>Email:</strong> {user['email']}</div>
                <div><strong>Registration Number:</strong> <code>{reg_display}</code></div>
                <div><strong>Account Type:</strong> <span class="badge badge-user">{user['role'].title()}</span></div>
                <div><strong>Account Created:</strong> {created_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="ui-card">
            <div class="ui-card-header">Change Password</div>
            <div class="ui-card-sub">Update your account login password.</div>
        """, unsafe_allow_html=True)

        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password (min 8 chars)", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            change_btn = st.form_submit_button("Update Password", type="primary", use_container_width=True)

        if change_btn:
            if new_pw != confirm_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters long.")
            else:
                try:
                    auth.change_user_password(user['id'], current_pw, new_pw)
                    st.success("Your password has been updated successfully!")
                except ValueError as err:
                    st.error(str(err))

        st.markdown("</div>", unsafe_allow_html=True)


def render_user_dashboard(user):
    """Main controller for regular user portal."""
    if st.session_state.get("new_account_created"):
        st.success("✓ Account created successfully. You are now signed in.")
        st.session_state.new_account_created = False

    render_user_navbar(user)

    current_nav = st.session_state.get("user_nav", "Home")

    if current_nav == "Home":
        render_user_home(user)
    elif current_nav == "Students":
        render_student_directory(user)
    elif current_nav == "Teachers":
        render_teacher_directory(user)
    elif current_nav == "Feedback Form":
        render_feedback_detail(user)
    elif current_nav == "My Profile":
        render_my_profile(user)
    else:
        render_user_home(user)


# ==============================================================================
# VIEW 3: ADMINISTRATOR DASHBOARD
# ==============================================================================
def render_admin_dashboard(user):
    """Administrator Portal with sidebar navigation."""
    with st.sidebar:
        st.markdown("### 🛡️ Admin Portal")
        st.caption("Institutional Review Administration")
        st.divider()

        admin_options = ["📊 Overview", "📝 Reviews", "🎓 Students", "👨‍🏫 Teachers", "👤 Users", "📥 Export", "🚪 Logout"]

        current_tab = st.session_state.get("admin_active_tab", "Overview")
        if current_tab in ("Dashboard", "Overview"):
            default_idx = 0
        elif current_tab == "Reviews":
            default_idx = 1
        elif current_tab in ("Students", "Manage People"):
            default_idx = 2
        elif current_tab == "Teachers":
            default_idx = 3
        elif current_tab == "Users":
            default_idx = 4
        elif current_tab == "Export":
            default_idx = 5
        else:
            default_idx = 0

        nav_choice = st.radio(
            "Admin Navigation",
            admin_options,
            index=default_idx
        )

        clean_nav = nav_choice.split(" ", 1)[-1]
        if clean_nav == "Logout":
            st.session_state.user = None
            st.session_state.admin_active_tab = "Overview"
            st.rerun()

        st.session_state.admin_active_tab = clean_nav

        st.divider()
        st.markdown("**Administrator:**")
        st.markdown(f"**{user['name']}**")
        st.caption(f"@{user['username']} • System Administrator")

    current_page = st.session_state.admin_active_tab

    # --------------------------------------------------------------------------
    # 1. ADMIN OVERVIEW (KPIs & Visual Analytics)
    # --------------------------------------------------------------------------
    if current_page in ("Overview", "Dashboard"):
        st.markdown("## Admin Dashboard")
        st.caption("Monitor feedback activity and manage institutional evaluation metrics.")
        st.subheader("Administrative Dashboard", divider=False)

        kpis = database.get_kpis()

        # Responsive KPI Row
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-label">📊 Total Reviews</div>
                <div class="kpi-value">{kpis['total_reviews']}</div>
                <div class="kpi-sub">All submissions</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👥 Registered Users</div>
                <div class="kpi-value">{kpis['total_users']}</div>
                <div class="kpi-sub">Active accounts</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🎓 Total Students</div>
                <div class="kpi-value">{kpis['total_students']}</div>
                <div class="kpi-sub">Directory master</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">👨‍🏫 Total Teachers</div>
                <div class="kpi-value">{kpis['total_teachers']}</div>
                <div class="kpi-sub">Faculty members</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">⭐ Average Rating</div>
                <div class="kpi-value">{'%.2f' % kpis['average_rating']}</div>
                <div class="kpi-sub">Out of 5.00</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2, gap="large")

        with col_c1:
            st.markdown("##### 👥 Reviews by Type (Student vs Teacher)")
            type_df = pd.DataFrame([
                {"Target": "Student", "Submissions": kpis['reviews_by_type']['student']},
                {"Target": "Teacher", "Submissions": kpis['reviews_by_type']['teacher']}
            ])
            st.bar_chart(type_df.set_index("Target"), color="#0284c7")

        with col_c2:
            st.markdown("##### ⭐ Rating Distribution (1–5 Stars)")
            dist_df = pd.DataFrame([
                {"Rating": f"{k} Star{'s' if k > 1 else ''}", "Reviews": v}
                for k, v in kpis['rating_distribution'].items()
            ])
            st.bar_chart(dist_df.set_index("Rating"), color="#0f172a")

        st.divider()

        col_act1, col_act2 = st.columns([1.2, 1], gap="large")

        with col_act1:
            st.markdown("##### 🕒 Recent Feedback Activity")
            recent_activity = database.get_recent_feedback_activity(limit=5)
            if recent_activity:
                for act in recent_activity:
                    t_badge = "badge-student" if act['target_type'] == 'student' else "badge-teacher"
                    reg_text = f" ({act['target_regno']})" if act.get('target_regno') else ""
                    st.markdown(f"""
                    <div class="review-item">
                        <div class="review-item-header">
                            <div>
                                <span class="review-reviewer">{act['reviewer_name']}</span>
                                <span style="color:#64748b; font-size:0.85rem;"> evaluated </span>
                                <strong>{act['target_name']}{reg_text}</strong>
                                <span class="badge {t_badge}">{act['target_type'].title()}</span>
                            </div>
                            <span class="review-stars">{rating_stars(act['rating'])}</span>
                        </div>
                        <div class="review-text-box">{act['review_text']}</div>
                        <div class="review-date" style="margin-top:0.4rem;">{format_datetime(act['updated_at'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-title">No Reviews Submitted Yet</div>
                    <div class="empty-state-text">Recent feedback activities will display here once users submit evaluations.</div>
                </div>
                """, unsafe_allow_html=True)

        with col_act2:
            st.markdown("##### 🏆 Top Reviewed People")
            top_people = database.get_top_reviewed_people(limit=5)
            if top_people:
                top_df = pd.DataFrame([{
                    "Name": p['name'],
                    "Type": p['type'].title(),
                    "Identifier": p['registration_no'] or p['department'],
                    "Reviews": p['review_count'],
                    "Avg Rating": f"{p['average_rating']:.2f} ★"
                } for p in top_people])
                st.dataframe(top_df, hide_index=True, use_container_width=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-title">No Rankings Available</div>
                    <div class="empty-state-text">Top reviewed individuals will appear after evaluations are recorded.</div>
                </div>
                """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 2. ADMIN REVIEWS MANAGEMENT
    # --------------------------------------------------------------------------
    elif current_page == "Reviews":
        st.markdown("## Reviews Management")
        st.caption("Inspect, filter, search, read in full, or moderate inappropriate reviews.")

        with st.container():
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1.2, 1.2, 1, 1.1, 0.9])

            with f_col1:
                filter_type = st.selectbox(
                    "Review Type",
                    options=["All", "Student", "Teacher"],
                    index=["All", "Student", "Teacher"].index(st.session_state.rf_type) if st.session_state.rf_type in ["All", "Student", "Teacher"] else 0
                )
                st.session_state.rf_type = filter_type

            with f_col2:
                all_people_names = sorted(list(set([p['name'] for p in database.list_people(active_only=False)])))
                person_opts = ["All"] + all_people_names
                selected_p_name = st.selectbox(
                    "Person Name",
                    options=person_opts,
                    index=person_opts.index(st.session_state.rf_person) if st.session_state.rf_person in person_opts else 0
                )
                st.session_state.rf_person = selected_p_name

            with f_col3:
                rating_opts = ["All", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"]
                selected_rating_label = st.selectbox(
                    "Rating",
                    options=rating_opts,
                    index=rating_opts.index(st.session_state.rf_rating) if st.session_state.rf_rating in rating_opts else 0
                )
                st.session_state.rf_rating = selected_rating_label
                filter_rating = int(selected_rating_label.split()[0]) if selected_rating_label != "All" else None

            with f_col4:
                date_opts = ["All", "Today", "Last 7 Days", "Last 30 Days", "Custom Date"]
                selected_date = st.selectbox(
                    "Date Filter",
                    options=date_opts,
                    index=date_opts.index(st.session_state.rf_date) if st.session_state.rf_date in date_opts else 0
                )
                st.session_state.rf_date = selected_date

            with f_col5:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Reset Filters", use_container_width=True):
                    st.session_state.rf_type = "All"
                    st.session_state.rf_person = "All"
                    st.session_state.rf_rating = "All"
                    st.session_state.rf_date = "All"
                    st.session_state.rf_search = ""
                    st.rerun()

            custom_date_str = None
            if selected_date == "Custom Date":
                picked = st.date_input("Select Date", value=datetime.date.today())
                custom_date_str = picked.strftime("%Y-%m-%d")

            search_text = st.text_input(
                "Search Reviews",
                value=st.session_state.rf_search,
                placeholder="Search name, registration number or reviewer..."
            )
            st.session_state.rf_search = search_text

        type_arg = filter_type.lower() if filter_type != "All" else None
        date_arg = custom_date_str if selected_date == "Custom Date" else selected_date

        reviews = database.fetch_admin_reviews(
            person_type=type_arg,
            person_name=selected_p_name if selected_p_name != "All" else None,
            rating=filter_rating,
            date_filter=date_arg,
            search_query=search_text
        )

        st.markdown(f"**Found {len(reviews)} review{'s' if len(reviews) != 1 else ''}**")

        if not reviews:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-title">No Reviews Found</div>
                <div class="empty-state-text">No reviews match your current search and filter criteria.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            table_records = []
            for r in reviews:
                target_desc = r['reviewed_person']
                if r['reviewed_person_type'] == 'student' and r.get('reviewed_person_regno'):
                    target_desc += f" ({r['reviewed_person_regno']})"

                raw_text = r['review_text'] or ""
                trunc_text = (raw_text[:75] + "...") if len(raw_text) > 75 else raw_text

                table_records.append({
                    "Review ID": r['review_id'],
                    "Reviewer": f"{r['reviewer_name']} (@{r['reviewer_username']})",
                    "Reviewed Person": target_desc,
                    "Type": r['reviewed_person_type'].title(),
                    "Rating": rating_stars(r['rating']),
                    "Review": trunc_text,
                    "Date": format_datetime(r['updated_at'])
                })

            df_reviews = pd.DataFrame(table_records)
            st.dataframe(
                df_reviews.drop(columns=["Review ID"]),
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            col_v1, col_v2 = st.columns([1.3, 1], gap="large")

            review_map = {
                f"#{r['review_id']} — {r['reviewer_name']} on {r['reviewed_person']} ({rating_stars(r['rating'])})": r
                for r in reviews
            }

            with col_v1:
                st.markdown("#### 🔍 View Complete Review")
                sel_rev_key = st.selectbox("Select Review to Inspect:", options=list(review_map.keys()))
                chosen_rev = review_map[sel_rev_key]

                reg_markup = f" • Reg: <code>{chosen_rev['reviewed_person_regno']}</code>" if chosen_rev.get('reviewed_person_regno') else ""
                t_badge = "badge-student" if chosen_rev['reviewed_person_type'] == 'student' else "badge-teacher"

                st.markdown(f"""
                <div class="ui-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                        <span style="font-size:1.15rem; font-weight:700;">{chosen_rev['reviewed_person']}</span>
                        <span class="badge {t_badge}">{chosen_rev['reviewed_person_type'].title()}</span>
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Department / Program:</strong> {chosen_rev['reviewed_person_department']}{reg_markup}
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Reviewer:</strong> {chosen_rev['reviewer_name']} (<code>@{chosen_rev['reviewer_username']}</code> • {chosen_rev['reviewer_email']})
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.4rem;">
                        <strong>Rating:</strong> <span style="color:#f59e0b; font-weight:700;">{rating_stars_label(chosen_rev['rating'])}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.8rem;">
                        Submitted: {format_datetime(chosen_rev['created_at'])} | Updated: {format_datetime(chosen_rev['updated_at'])}
                    </div>
                    <div class="review-text-box">
                        {chosen_rev['review_text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_v2:
                st.markdown("#### 🗑️ Delete Review")
                st.warning("Admins can permanently remove inappropriate or policy-violating reviews.")
                confirm_del = st.checkbox("I confirm I want to permanently delete this review.", key="del_box")

                if st.button("Delete Inappropriate Review", type="primary", use_container_width=True):
                    if not confirm_del:
                        st.error("Please check the confirmation box above before deleting.")
                    else:
                        ok = database.delete_review(chosen_rev['review_id'])
                        if ok:
                            st.success(f"Review #{chosen_rev['review_id']} was deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete review. Please try again.")

    # --------------------------------------------------------------------------
    # 3. ADMIN STUDENTS MANAGEMENT
    # --------------------------------------------------------------------------
    elif current_page in ("Students", "Manage People"):
        st.markdown("## Students Management")
        st.caption("Manage students directory, inspect detailed feedback dossiers, toggle active status, and add new students.")

        tab_st_dir, tab_st_add = st.tabs(["🎓 Student Directory & Dossier", "➕ Add Student"])

        with tab_st_dir:
            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                st_search = st.text_input(
                    "Search student by Name or Registration Number",
                    placeholder="e.g. AMIT or 23BCON0028"
                )
            with col_s2:
                st_filter = st.selectbox("Status Filter", ["All", "Active Only", "Inactive Only"], key="st_stat_filter")

            students_data = database.get_students_summary(search_query=st_search)
            if st_filter == "Active Only":
                students_data = [s for s in students_data if s['active']]
            elif st_filter == "Inactive Only":
                students_data = [s for s in students_data if not s['active']]

            if not students_data:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">🎓</div>
                    <div class="empty-state-title">No Students Match Your Search</div>
                    <div class="empty-state-text">Check your search query or add a new student using the Add Student tab.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st_table = pd.DataFrame([{
                    "Name": s['student_name'],
                    "Registration No.": s['registration_no'] or "—",
                    "Department": s['department'],
                    "Reviews": s['total_reviews'],
                    "Average Rating": f"{s['average_rating']:.2f} ★" if s['average_rating'] else "No reviews",
                    "Status": "Active" if s['active'] else "Inactive"
                } for s in students_data])
                st.dataframe(st_table, hide_index=True, use_container_width=True)

                st.divider()

                st.markdown("### 📋 Student Dossier & Reviews Received")
                st_picker_map = {
                    f"{s['student_name']} — {s['registration_no'] or 'N/A'} ({s['total_reviews']} reviews)": s['student_id']
                    for s in students_data
                }
                chosen_st_label = st.selectbox("Select Student to Inspect:", options=list(st_picker_map.keys()), key="st_dossier_pick")
                chosen_st_id = st_picker_map[chosen_st_label]

                dossier = database.get_person_detail(chosen_st_id)
                if dossier:
                    col_d1, col_d2, col_d3 = st.columns([1.5, 1, 1])
                    with col_d1:
                        st.markdown(f"**Name:** {dossier['name']}")
                        st.markdown(f"**Registration Number:** `{dossier['registration_no'] or 'N/A'}`")
                        st.markdown(f"**Department:** {dossier['department']}")
                        status_badge = "badge-active" if dossier['active'] else "badge-inactive"
                        st.markdown(f"**Status:** <span class='badge {status_badge}'>{'Active' if dossier['active'] else 'Inactive'}</span>", unsafe_allow_html=True)

                    with col_d2:
                        st.metric("Average Rating", f"{dossier['average_rating']:.2f} ★" if dossier['average_rating'] else "No reviews")
                        st.metric("Total Reviews", dossier['total_reviews'])

                    with col_d3:
                        st.markdown("**Rating Breakdown:**")
                        for star_num in [5, 4, 3, 2, 1]:
                            count = dossier['breakdown'].get(star_num, 0)
                            st.write(f"{star_num} ★ : **{count}**")

                    col_btn, col_edit = st.columns([1, 1])
                    with col_btn:
                        btn_txt = "Deactivate Student" if dossier['active'] else "Activate Student"
                        if st.button(btn_txt, key="btn_toggle_st", use_container_width=True):
                            database.set_person_active(dossier['id'], not dossier['active'])
                            st.success(f"{dossier['name']} status updated.")
                            st.rerun()

                    with col_edit:
                        with st.expander("✏️ Edit Student Details"):
                            with st.form("edit_st_form"):
                                new_name = st.text_input("Name", value=dossier['name'])
                                new_reg = st.text_input("Registration No", value=dossier['registration_no'] or "")
                                new_dept = st.text_input("Department", value=dossier['department'])
                                save_st = st.form_submit_button("Save Changes", use_container_width=True)

                            if save_st:
                                try:
                                    database.update_person(
                                        person_id=dossier['id'],
                                        name=new_name,
                                        department=new_dept,
                                        person_type="student",
                                        registration_no=new_reg.strip() if new_reg else None
                                    )
                                    st.success("Student details updated.")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(str(err))

                    st.markdown("##### Reviews Received")
                    if dossier['reviews']:
                        for rev in dossier['reviews']:
                            st.markdown(f"""
                            <div class="review-item">
                                <div class="review-item-header">
                                    <span class="review-reviewer">{rev['reviewer_name']} (@{rev['reviewer_username']})</span>
                                    <span class="review-stars">{rating_stars(rev['rating'])}</span>
                                </div>
                                <div class="review-text-box">{rev['review_text']}</div>
                                <div class="review-date" style="margin-top:0.4rem;">{format_datetime(rev['updated_at'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No reviews have been submitted for this student yet.")

        with tab_st_add:
            st.markdown("##### Add Student to Directory")
            with st.form("add_student_form", clear_on_submit=True):
                new_s_name = st.text_input("Student Name", placeholder="e.g. PRIYANKA SANGWA")
                new_s_reg = st.text_input("Registration Number", placeholder="e.g. 23BCON1710")
                new_s_dept = st.text_input("Department / Program", value="Computer Science & Engineering")
                submit_add_s = st.form_submit_button("Add Student", type="primary", use_container_width=True)

            if submit_add_s:
                try:
                    database.add_person(
                        name=new_s_name,
                        person_type='student',
                        department=new_s_dept,
                        registration_no=new_s_reg.strip() if new_s_reg else None
                    )
                    st.success(f"Student '{new_s_name}' ({new_s_reg}) added successfully!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

    # --------------------------------------------------------------------------
    # 4. ADMIN TEACHERS MANAGEMENT
    # --------------------------------------------------------------------------
    elif current_page == "Teachers":
        st.markdown("## Faculty & Teachers Management")
        st.caption("Manage faculty members, inspect feedback dossiers, toggle active status, and add new teachers.")

        tab_t_dir, tab_t_add = st.tabs(["👨‍🏫 Faculty Directory & Dossier", "➕ Add Teacher"])

        with tab_t_dir:
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                t_search = st.text_input("Search faculty by Name or Department", placeholder="e.g. Computer Science")
            with col_t2:
                t_filter = st.selectbox("Status Filter", ["All", "Active Only", "Inactive Only"], key="t_stat_filter")

            teachers_data = database.get_teachers_summary(search_query=t_search)
            if t_filter == "Active Only":
                teachers_data = [t for t in teachers_data if t['active']]
            elif t_filter == "Inactive Only":
                teachers_data = [t for t in teachers_data if not t['active']]

            if not teachers_data:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">👨‍🏫</div>
                    <div class="empty-state-title">No Faculty Found</div>
                    <div class="empty-state-text">No faculty members match your criteria. Add teachers using the Add Teacher tab.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                t_table = pd.DataFrame([{
                    "Name": t['teacher_name'],
                    "Department": t['department'],
                    "Reviews": t['total_reviews'],
                    "Average Rating": f"{t['average_rating']:.2f} ★" if t['average_rating'] else "No reviews",
                    "Status": "Active" if t['active'] else "Inactive"
                } for t in teachers_data])
                st.dataframe(t_table, hide_index=True, use_container_width=True)

                st.divider()

                st.markdown("### 📋 Faculty Dossier & Reviews Received")
                t_picker_map = {
                    f"{t['teacher_name']} — {t['department']} ({t['total_reviews']} reviews)": t['teacher_id']
                    for t in teachers_data
                }
                chosen_t_label = st.selectbox("Select Faculty Member to Inspect:", options=list(t_picker_map.keys()), key="t_dossier_pick")
                chosen_t_id = t_picker_map[chosen_t_label]

                t_dossier = database.get_person_detail(chosen_t_id)
                if t_dossier:
                    col_td1, col_td2, col_td3 = st.columns([1.5, 1, 1])
                    with col_td1:
                        st.markdown(f"**Name:** {t_dossier['name']}")
                        st.markdown(f"**Department:** {t_dossier['department']}")
                        t_status_badge = "badge-active" if t_dossier['active'] else "badge-inactive"
                        st.markdown(f"**Status:** <span class='badge {t_status_badge}'>{'Active' if t_dossier['active'] else 'Inactive'}</span>", unsafe_allow_html=True)

                    with col_td2:
                        st.metric("Average Rating", f"{t_dossier['average_rating']:.2f} ★" if t_dossier['average_rating'] else "No reviews")
                        st.metric("Total Reviews", t_dossier['total_reviews'])

                    with col_td3:
                        st.markdown("**Rating Breakdown:**")
                        for star_num in [5, 4, 3, 2, 1]:
                            count = t_dossier['breakdown'].get(star_num, 0)
                            st.write(f"{star_num} ★ : **{count}**")

                    col_t_btn, col_t_edit = st.columns([1, 1])
                    with col_t_btn:
                        btn_txt = "Deactivate Teacher" if t_dossier['active'] else "Activate Teacher"
                        if st.button(btn_txt, key="btn_toggle_teacher", use_container_width=True):
                            database.set_person_active(t_dossier['id'], not t_dossier['active'])
                            st.success(f"{t_dossier['name']} status updated.")
                            st.rerun()

                    with col_t_edit:
                        with st.expander("✏️ Edit Teacher Details"):
                            with st.form("edit_t_form"):
                                new_t_name = st.text_input("Name", value=t_dossier['name'])
                                new_t_dept = st.text_input("Department", value=t_dossier['department'])
                                save_t = st.form_submit_button("Save Changes", use_container_width=True)

                            if save_t:
                                try:
                                    database.update_person(
                                        person_id=t_dossier['id'],
                                        name=new_t_name,
                                        department=new_t_dept,
                                        person_type="teacher"
                                    )
                                    st.success("Faculty details updated.")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(str(err))

                    st.markdown("##### Reviews Received")
                    if t_dossier['reviews']:
                        for rev in t_dossier['reviews']:
                            st.markdown(f"""
                            <div class="review-item">
                                <div class="review-item-header">
                                    <span class="review-reviewer">{rev['reviewer_name']} (@{rev['reviewer_username']})</span>
                                    <span class="review-stars">{rating_stars(rev['rating'])}</span>
                                </div>
                                <div class="review-text-box">{rev['review_text']}</div>
                                <div class="review-date" style="margin-top:0.4rem;">{format_datetime(rev['updated_at'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No reviews have been submitted for this teacher yet.")

        with tab_t_add:
            st.markdown("##### Add Faculty / Teacher")
            with st.form("add_teacher_form", clear_on_submit=True):
                new_t_name = st.text_input("Teacher Name", placeholder="e.g. Dr. Robert Miller")
                new_t_dept = st.text_input("Department", placeholder="e.g. Computer Science")
                submit_add_t = st.form_submit_button("Add Teacher", type="primary", use_container_width=True)

            if submit_add_t:
                try:
                    database.add_person(
                        name=new_t_name,
                        person_type='teacher',
                        department=new_t_dept
                    )
                    st.success(f"Teacher '{new_t_name}' added successfully!")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

    # --------------------------------------------------------------------------
    # 5. ADMIN USERS DIRECTORY
    # --------------------------------------------------------------------------
    elif current_page == "Users":
        st.markdown("## Registered Accounts")
        st.caption("Inspect verified user accounts and linked registration credentials.")

        all_users = database.list_users()
        user_search = st.text_input("Search user accounts by name, username, email, or registration number...")
        if user_search.strip():
            kw = user_search.strip().lower()
            all_users = [
                u for u in all_users
                if kw in u['name'].lower() or kw in u['username'].lower() or kw in u['email'].lower() or (u.get('registration_no') and kw in u['registration_no'].lower())
            ]

        if not all_users:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">👤</div>
                <div class="empty-state-title">No User Accounts Found</div>
                <div class="empty-state-text">No user accounts match your search query.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            user_rows = []
            for u in all_users:
                user_rows.append({
                    "Name": u['name'],
                    "Username / Email": f"@{u['username']} • {u['email']}",
                    "Registration Number": u.get('registration_no') or "—",
                    "Role": u['role'].title(),
                    "Created Date": format_datetime(u['created_at']),
                    "Status": "Active"
                })

            st.dataframe(pd.DataFrame(user_rows), hide_index=True, use_container_width=True)

    # --------------------------------------------------------------------------
    # 6. ADMIN EXPORT DATA
    # --------------------------------------------------------------------------
    elif current_page == "Export":
        st.markdown("## Export Data to CSV")
        st.caption("Generate and download structured CSV reports for compliance, archiving, and analysis.")

        col_e1, col_e2 = st.columns(2, gap="large")

        with col_e1:
            st.markdown("""
            <div class="ui-card">
                <div class="ui-card-header">Export Reviews</div>
                <div class="ui-card-sub">Download complete submissions including evaluator details, ratings, and written comments.</div>
            """, unsafe_allow_html=True)

            export_choice = st.radio(
                "Select Export Dataset:",
                ["All Reviews", "Student Reviews", "Teacher Reviews"],
                key="exp_rev_choice"
            )

            filter_type = None
            if export_choice == "Student Reviews":
                filter_type = "student"
            elif export_choice == "Teacher Reviews":
                filter_type = "teacher"

            reviews_to_export = database.fetch_admin_reviews(person_type=filter_type)
            st.write(f"Total matching records: **{len(reviews_to_export)}**")

            if reviews_to_export:
                df_exp_rev = pd.DataFrame([{
                    "Review ID": r['review_id'],
                    "Reviewer Name": r['reviewer_name'],
                    "Reviewer Username": r['reviewer_username'],
                    "Reviewer Email": r['reviewer_email'],
                    "Reviewed Person": r['reviewed_person'],
                    "Registration Number": r['reviewed_person_regno'] or "—",
                    "Reviewed Person Type": r['reviewed_person_type'].title(),
                    "Department": r['reviewed_person_department'],
                    "Rating": r['rating'],
                    "Review Comment": r['review_text'],
                    "Date Submitted": format_datetime(r['created_at']),
                    "Date Updated": format_datetime(r['updated_at'])
                } for r in reviews_to_export])

                csv_rev = df_exp_rev.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"⬇️ Download {export_choice} CSV",
                    data=csv_rev,
                    file_name=f"{export_choice.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("No reviews available to export.")

            st.markdown("</div>", unsafe_allow_html=True)

        with col_e2:
            st.markdown("""
            <div class="ui-card">
                <div class="ui-card-header">Export Master Directory</div>
                <div class="ui-card-sub">Download master student directory with registration numbers and faculty listings.</div>
            """, unsafe_allow_html=True)

            people_to_export = database.list_people(active_only=False)
            st.write(f"Total directory records: **{len(people_to_export)}**")

            if people_to_export:
                df_exp_people = pd.DataFrame([{
                    "Person ID": p['id'],
                    "Name": p['name'],
                    "Registration Number": p.get('registration_no') or "—",
                    "Type": p['type'].title(),
                    "Department": p['department'],
                    "Status": "Active" if p['active'] else "Inactive"
                } for p in people_to_export])

                csv_people = df_exp_people.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download People Directory CSV",
                    data=csv_people,
                    file_name="master_people_directory.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("No people records available.")

            st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# MAIN ROUTING CONTROLLER
# ==============================================================================
def main():
    if st.session_state.user is None:
        render_landing_page()
    else:
        role = st.session_state.user.get('role', 'user')
        if role == 'admin':
            render_admin_dashboard(st.session_state.user)
        else:
            render_user_dashboard(st.session_state.user)


if __name__ == "__main__":
    main()
