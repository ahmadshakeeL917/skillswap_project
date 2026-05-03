import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database as db_helper

st.set_page_config(
    page_title="SkillSwap",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SESSION STATE INIT ──────────────────────────────
for key in ["user", "admin", "page"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "page" not in st.session_state or st.session_state.page is None:
    st.session_state.page = "home"

# ─── CUSTOM CSS ─────────────────────────────────────
st.markdown("""
<style>
    .main-header {font-size:2.2rem; font-weight:800; color:#2563eb; margin-bottom:0;}
    .sub-header {color:#64748b; margin-bottom:1.5rem;}
    .metric-card {background:white; padding:1.2rem; border-radius:12px; border:1px solid #e2e8f0; text-align:center;}
    .metric-val {font-size:2rem; font-weight:800; color:#2563eb;}
    .metric-lbl {color:#64748b; font-size:0.85rem;}
    .badge-green {background:#d1fae5; color:#065f46; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;}
    .badge-yellow {background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;}
    .badge-red {background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;}
    .badge-blue {background:#dbeafe; color:#1d4ed8; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600;}
    .listing-card {background:white; border:1px solid #e2e8f0; border-radius:12px; padding:1rem; margin-bottom:0.75rem;}
    div[data-testid="stSidebarContent"] {background: #0f172a;}
    section[data-testid="stSidebar"] * {color: white !important;}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🔄 SkillSwap")
        st.markdown("---")

        if st.session_state.admin:
            st.markdown(f"**🛡️ Admin:** {st.session_state.admin['username']}")
            st.markdown("---")
            pages = {
                "📊 Dashboard": "admin_dashboard",
                "📋 Listings": "admin_listings",
                "⚠️ Disputes": "admin_disputes",
                "👥 Users": "admin_users",
                "📦 All Orders": "admin_orders",
                "📈 Analytics": "admin_analytics",
            }
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin = None
                st.session_state.page = "home"
                st.rerun()

        elif st.session_state.user:
            u = st.session_state.user
            st.markdown(f"**👤 {u['fullname']}**")
            st.markdown(f"💰 **{u['walletbalance']} pts**")
            st.markdown("---")
            pages = {
                "🏠 Home": "home",
                "🔍 Browse Skills": "listings",
                "📋 Job Posts": "jobs",
                "📦 My Orders": "my_orders",
                "📊 Dashboard": "dashboard",
            }
            if u["role"] in ("seller", "both"):
                pages["🎨 My Listings"] = "my_listings"
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "home"
                st.rerun()

        else:
            pages = {"🏠 Home": "home", "🔍 Browse Skills": "listings", "📋 Job Posts": "jobs"}
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
            st.markdown("---")
            if st.button("🔑 Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
            if st.button("📝 Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
            if st.button("🛡️ Admin Login", use_container_width=True):
                st.session_state.page = "admin_login"
                st.rerun()


# ════════════════════════════════════════════════════
# AUTH PAGES
# ════════════════════════════════════════════════════
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔑 Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = db_helper.login_user(email, password)
                if user:
                    if user.get("issuspended"):
                        st.error("Your account is suspended. Contact admin.")
                    else:
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.rerun()
                else:
                    st.error("Invalid email or password!")
        if st.button("Don't have account? Register"):
            st.session_state.page = "register"
            st.rerun()


def page_register():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 📝 Register")
        with st.form("register_form"):
            fullname = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("I want to join as", ["buyer", "seller", "both"],
                                format_func=lambda x: {"buyer": "🛒 Buyer", "seller": "💼 Seller", "both": "🔄 Both"}[x])
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not fullname or not email or not password:
                    st.error("Please fill all fields!")
                else:
                    try:
                        user = db_helper.register_user(fullname, email, password, role)
                        if user:
                            st.session_state.user = user
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error("Registration failed. Email might already exist.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


def page_admin_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🛡️ Admin Login")
        with st.form("admin_login_form"):
            email = st.text_input("Admin Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login as Admin", use_container_width=True)
            if submitted:
                admin = db_helper.login_admin(email, password)
                if admin:
                    st.session_state.admin = admin
                    st.session_state.page = "admin_dashboard"
                    st.rerun()
                else:
                    st.error("Invalid admin credentials!")


# ════════════════════════════════════════════════════
# HOME PAGE
# ════════════════════════════════════════════════════
def page_home():
    st.markdown('<h1 class="main-header">🔄 SkillSwap</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Trade Skills. Grow Together. Student-powered freelance marketplace.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Browse Skills", use_container_width=True):
            st.session_state.page = "listings"
            st.rerun()
    with col2:
        if st.button("📋 View Jobs", use_container_width=True):
            st.session_state.page = "jobs"
            st.rerun()
    with col3:
        if not st.session_state.user:
            if st.button("📝 Get Started Free", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

    st.markdown("---")
    st.markdown("### How it works")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info("🔍 **Browse Skills**\nFind verified student freelancers")
    with c2: st.info("💬 **Place a Bid**\nPost jobs and receive proposals")
    with c3: st.info("🔒 **Escrow Protection**\nPayment held until work done")
    with c4: st.info("⭐ **Leave Reviews**\nBuild your reputation")


# ════════════════════════════════════════════════════
# CLIENT PAGES
# ════════════════════════════════════════════════════
def page_listings():
    st.markdown("## 🔍 Browse Skills")
    categories = db_helper.get_categories()
    cat_names = ["All"] + [c["categoryname"] for c in categories]
    cat_map = {c["categoryname"]: c["categoryid"] for c in categories}

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search skills...", placeholder="e.g. logo design, web app")
    with col2:
        selected_cat = st.selectbox("Category", cat_names)

    listings = db_helper.get_listings(status="approved")

    if search:
        listings = [l for l in listings if search.lower() in l["title"].lower() or search.lower() in (l.get("description") or "").lower()]
    if selected_cat != "All":
        cid = cat_map.get(selected_cat)
        listings = [l for l in listings if l.get("categoryid") == cid]

    st.markdown(f"**{len(listings)} listings found**")

    if not listings:
        st.info("No listings found. Try different search!")
        return

    for i in range(0, len(listings), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(listings):
                l = listings[i + j]
                with col:
                    with st.container(border=True):
                        cat = l.get("category") or {}
                        st.markdown(f'<span class="badge-blue">{cat.get("categoryname", "General")}</span>', unsafe_allow_html=True)
                        st.markdown(f"**{l['title']}**")
                        st.caption(f"👤 {(l.get('users') or {}).get('fullname', 'Student')} • ⭐ {(l.get('users') or {}).get('avgrating', 0):.1f}")
                        st.markdown(f"💰 **{l['price']} pts**")
                        desc = (l.get("description") or "")[:80]
                        st.caption(f"{desc}...")
                        if st.session_state.user:
                            if st.button("Order Now", key=f"order_{l['listing_id']}", use_container_width=True):
                                u = st.session_state.user
                                if u["walletbalance"] < l["price"]:
                                    st.error("Insufficient balance!")
                                elif u["studentid"] == l["providerid"]:
                                    st.error("Can't order your own listing!")
                                else:
                                    db_helper.create_order(u["studentid"], l["providerid"], l["listing_id"], l["price"])
                                    # Refresh user balance
                                    users = db_helper.db().table("users").select("*").eq("studentid", u["studentid"]).execute().data
                                    if users: st.session_state.user = users[0]
                                    st.success("✅ Order placed!")
                                    st.rerun()
                        else:
                            if st.button("Login to Order", key=f"order_{l['listing_id']}", use_container_width=True):
                                st.session_state.page = "login"
                                st.rerun()


def page_jobs():
    st.markdown("## 📋 Job Postings")
    u = st.session_state.user

    tab1, tab2 = st.tabs(["📋 Browse Jobs", "➕ Post a Job"])

    with tab1:
        jobs = db_helper.get_jobs("open")
        if not jobs:
            st.info("No open jobs right now. Be the first to post!")
        for job in jobs:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    cat = (job.get("category") or {}).get("categoryname", "General")
                    urgent = job.get("isurgent") == "yes"
                    badges = f'<span class="badge-blue">{cat}</span>'
                    if urgent: badges += ' <span class="badge-red">🔥 Urgent</span>'
                    st.markdown(badges, unsafe_allow_html=True)
                    st.markdown(f"**{job['title']}**")
                    st.caption(job.get("description", ""))
                    st.caption(f"👤 {(job.get('users') or {}).get('fullname', '?')} • 📅 {str(job.get('createdat',''))[:10]}")
                with c2:
                    st.markdown(f"### 💰 {job.get('budget', 0)}")

                if u and u.get("role") in ("seller", "both") and u["studentid"] != job.get("requesterid"):
                    with st.expander("📨 Place a Bid"):
                        with st.form(f"bid_{job['postingid']}"):
                            amount = st.number_input("Your Bid (pts)", min_value=1, value=job.get("budget", 100))
                            note = st.text_area("Proposal Note", placeholder="Why should they pick you?")
                            if st.form_submit_button("Submit Bid", use_container_width=True):
                                db_helper.place_bid(job["postingid"], u["studentid"], amount, note)
                                st.success("✅ Bid placed!")
                                st.rerun()

                # Show bids for job owner
                if u and u["studentid"] == job.get("requesterid"):
                    bids = db_helper.get_bids_for_job(job["postingid"])
                    if bids:
                        with st.expander(f"👁️ View {len(bids)} Bids"):
                            for bid in bids:
                                bc1, bc2, bc3 = st.columns([2, 1, 1])
                                with bc1:
                                    st.write(f"**{(bid.get('users') or {}).get('fullname', '?')}** — {bid.get('proposalnote','')[:60]}")
                                with bc2:
                                    st.write(f"💰 {bid['bidamount']} pts")
                                with bc3:
                                    if bid["bidstatus"] == "pending":
                                        if st.button("Accept", key=f"acc_{bid['bidid']}"):
                                            db_helper.accept_bid(bid["bidid"], job["postingid"])
                                            st.success("Bid accepted!")
                                            st.rerun()
                                    else:
                                        st.markdown(f'<span class="badge-green">{bid["bidstatus"]}</span>', unsafe_allow_html=True)

    with tab2:
        if not u:
            st.warning("Please login to post a job!")
            return
        if u["role"] not in ("buyer", "both"):
            st.warning("Only buyers can post jobs!")
            return
        categories = db_helper.get_categories()
        with st.form("post_job"):
            title = st.text_input("Job Title", placeholder="I need a logo designed...")
            description = st.text_area("Description", placeholder="Describe what you need...")
            c1, c2 = st.columns(2)
            with c1:
                budget = st.number_input("Budget (pts)", min_value=1, value=500)
            with c2:
                cat_choice = st.selectbox("Category", ["None"] + [c["categoryname"] for c in categories])
            isurgent = st.checkbox("🔥 Mark as Urgent")
            if st.form_submit_button("Post Job", use_container_width=True):
                cat_id = next((c["categoryid"] for c in categories if c["categoryname"] == cat_choice), None)
                db_helper.create_job(u["studentid"], title, description, budget, cat_id, isurgent)
                st.success("✅ Job posted!")
                st.rerun()


def page_my_orders():
    u = st.session_state.user
    st.markdown("## 📦 My Orders")

    tab1, tab2 = st.tabs(["🛒 Buying", "💼 Selling"])
    STATUS_COLOR = {"pending": "badge-yellow", "active": "badge-blue", "completed": "badge-green", "disputed": "badge-red", "refunded": "badge-gray"}

    with tab1:
        orders = db_helper.get_my_orders(u["studentid"], "buyer")
        if not orders:
            st.info("No orders yet. Browse skills and place your first order!")
        for o in orders:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    status_cls = STATUS_COLOR.get(o["escrowstatus"], "badge-gray")
                    st.markdown(f'<span class="{status_cls}">{o["escrowstatus"]}</span>', unsafe_allow_html=True)
                    title = (o.get("skill_listing") or {}).get("title", "Custom Order")
                    st.markdown(f"**{title}**")
                    seller = (o.get("seller") or {}).get("fullname", "?")
                    st.caption(f"💼 Seller: {seller} • 📅 {str(o.get('createdat',''))[:10]}")
                with c2:
                    st.markdown(f"### {o['amount']} pts")

                if o["escrowstatus"] == "active":
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("✅ Mark Complete", key=f"comp_{o['orderid']}"):
                            db_helper.complete_order(o["orderid"], o["sellerid"], o["amount"])
                            st.success("Order completed! Payment released.")
                            st.rerun()
                    with bc2:
                        if st.button("⚠️ Raise Dispute", key=f"disp_{o['orderid']}"):
                            reason = st.text_input("Reason", key=f"reason_{o['orderid']}")
                            if reason:
                                db_helper.raise_dispute(o["orderid"], u["studentid"], reason)
                                st.warning("Dispute raised!")
                                st.rerun()

                if o["escrowstatus"] == "completed":
                    with st.expander("⭐ Leave Review"):
                        with st.form(f"rev_{o['orderid']}"):
                            rating = st.slider("Rating", 1, 5, 5)
                            comment = st.text_area("Comment")
                            if st.form_submit_button("Submit Review"):
                                db_helper.submit_review(o["orderid"], u["studentid"], o["sellerid"], rating, comment)
                                st.success("Review submitted!")

    with tab2:
        orders = db_helper.get_my_orders(u["studentid"], "seller")
        if not orders:
            st.info("No selling orders yet. Create a listing to start selling!")
        for o in orders:
            with st.container(border=True):
                status_cls = STATUS_COLOR.get(o["escrowstatus"], "badge-gray")
                st.markdown(f'<span class="{status_cls}">{o["escrowstatus"]}</span>', unsafe_allow_html=True)
                title = (o.get("skill_listing") or {}).get("title", "Custom Order")
                buyer = (o.get("buyer") or {}).get("fullname", "?")
                st.markdown(f"**{title}** — 🛒 Buyer: {buyer}")
                st.caption(f"💰 {o['amount']} pts • 📅 {str(o.get('createdat',''))[:10]}")


def page_my_listings():
    u = st.session_state.user
    st.markdown("## 🎨 My Listings")
    categories = db_helper.get_categories()

    tab1, tab2 = st.tabs(["📋 My Listings", "➕ Create New"])

    with tab1:
        listings = db_helper.get_my_listings(u["studentid"])
        STATUS_COLOR = {"pending": "badge-yellow", "approved": "badge-green", "rejected": "badge-red"}
        if not listings:
            st.info("No listings yet. Create your first one!")
        for l in listings:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f'<span class="{STATUS_COLOR.get(l["approvalstatus"], "badge-gray")}">{l["approvalstatus"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**{l['title']}**")
                    st.caption(f"💰 {l['price']} pts • {(l.get('category') or {}).get('categoryname', 'General')}")
                with c2:
                    if st.button("🗑️ Delete", key=f"del_{l['listing_id']}"):
                        db_helper.delete_listing(l["listing_id"])
                        st.success("Deleted!")
                        st.rerun()

    with tab2:
        with st.form("create_listing"):
            title = st.text_input("Title", placeholder="I will design your logo...")
            description = st.text_area("Description", placeholder="Describe your service in detail...")
            c1, c2 = st.columns(2)
            with c1:
                price = st.number_input("Price (pts)", min_value=1, value=500)
            with c2:
                cat_choice = st.selectbox("Category", ["None"] + [c["categoryname"] for c in categories])
            tags = st.text_input("Skill Tags (comma separated)", placeholder="react, python, design")
            if st.form_submit_button("Submit Listing", use_container_width=True):
                cat_id = next((c["categoryid"] for c in categories if c["categoryname"] == cat_choice), None)
                tag_list = [t.strip() for t in tags.split(",")] if tags else []
                db_helper.create_listing(u["studentid"], title, description, price, cat_id, tag_list)
                st.success("✅ Listing submitted for admin approval!")
                st.rerun()


def page_dashboard():
    u = st.session_state.user
    st.markdown(f"## 📊 Dashboard — {u['fullname']}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💰 Wallet", f"{u['walletbalance']} pts")
    with c2:
        st.metric("⭐ Rating", f"{u.get('avgrating', 0):.1f}")
    with c3:
        role_map = {"buyer": "🛒 Buyer", "seller": "💼 Seller", "both": "🔄 Both"}
        st.metric("Role", role_map.get(u["role"], u["role"]))
    with c4:
        status = "🚫 Suspended" if u.get("issuspended") else "✅ Active"
        st.metric("Status", status)

    st.markdown("---")

    # Transactions
    st.markdown("### 💳 Wallet Transactions")
    txns = db_helper.get_transactions(u["studentid"])
    if txns:
        df = pd.DataFrame(txns)
        df["createdat"] = pd.to_datetime(df["createdat"]).dt.strftime("%Y-%m-%d %H:%M")
        df["amount"] = df["amount"].apply(lambda x: f"+{x}" if x > 0 else str(x))
        st.dataframe(df[["createdat", "transactiontype", "amount"]], use_container_width=True, hide_index=True)

        # Chart
        raw = db_helper.get_transactions(u["studentid"])
        if raw:
            df2 = pd.DataFrame(raw)
            df2["createdat"] = pd.to_datetime(df2["createdat"])
            df2 = df2.sort_values("createdat")
            df2["cumulative"] = df2["amount"].cumsum()
            fig = px.line(df2, x="createdat", y="cumulative", title="Wallet Balance Over Time",
                          color_discrete_sequence=["#2563eb"])
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions yet")


# ════════════════════════════════════════════════════
# ADMIN PAGES
# ════════════════════════════════════════════════════
def page_admin_dashboard():
    st.markdown("## 📊 Admin Dashboard")
    stats = db_helper.get_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("👥 Total Users", stats["users"])
    with c2: st.metric("📦 Total Orders", stats["orders"])
    with c3: st.metric("📋 Listings", stats["listings"])
    with c4: st.metric("⚠️ Open Disputes", stats["open_disputes"])
    with c5: st.metric("🕐 Pending Listings", stats["pending_listings"])

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Orders by status
        orders = db_helper.get_all_orders()
        if orders:
            df = pd.DataFrame(orders)
            status_counts = df["escrowstatus"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig = px.pie(status_counts, values="Count", names="Status", title="Orders by Status",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Listings by status
        all_listings = db_helper.get_listings()
        if all_listings:
            df2 = pd.DataFrame(all_listings)
            lstat = df2["approvalstatus"].value_counts().reset_index()
            lstat.columns = ["Status", "Count"]
            fig2 = px.bar(lstat, x="Status", y="Count", title="Listings by Approval Status",
                          color="Status", color_discrete_map={"approved": "#10b981", "pending": "#f59e0b", "rejected": "#ef4444"})
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # Recent orders table
    st.markdown("### 📦 Recent Orders")
    orders = db_helper.get_all_orders()
    if orders:
        df = pd.DataFrame(orders)
        df["buyer"] = df["buyer"].apply(lambda x: (x or {}).get("fullname", "?"))
        df["seller"] = df["seller"].apply(lambda x: (x or {}).get("fullname", "?"))
        df["listing"] = df["skill_listing"].apply(lambda x: (x or {}).get("title", "Custom"))
        df["date"] = pd.to_datetime(df["createdat"]).dt.strftime("%Y-%m-%d")
        st.dataframe(df[["orderid", "buyer", "seller", "listing", "amount", "escrowstatus", "date"]].head(10),
                     use_container_width=True, hide_index=True)


def page_admin_listings():
    st.markdown("## 📋 Manage Listings")
    filter_status = st.selectbox("Filter by Status", ["all", "pending", "approved", "rejected"])
    status = None if filter_status == "all" else filter_status
    listings = db_helper.get_listings(status)

    st.markdown(f"**{len(listings)} listings**")
    STATUS_COLOR = {"pending": "badge-yellow", "approved": "badge-green", "rejected": "badge-red"}

    for l in listings:
        with st.container(border=True):
            c1, c2 = st.columns([5, 2])
            with c1:
                st.markdown(f'<span class="{STATUS_COLOR.get(l["approvalstatus"])}">{l["approvalstatus"]}</span> '
                            f'<span class="badge-blue">{(l.get("category") or {}).get("categoryname","General")}</span>', unsafe_allow_html=True)
                st.markdown(f"**{l['title']}**")
                st.caption(f"👤 {(l.get('users') or {}).get('fullname','?')} • 💰 {l['price']} pts")
                st.caption((l.get("description") or "")[:120])
            with c2:
                if l["approvalstatus"] != "approved":
                    if st.button("✅ Approve", key=f"appr_{l['listing_id']}", use_container_width=True):
                        db_helper.update_listing_status(l["listing_id"], "approved")
                        st.success("Approved!")
                        st.rerun()
                if l["approvalstatus"] != "rejected":
                    if st.button("❌ Reject", key=f"rej_{l['listing_id']}", use_container_width=True):
                        db_helper.update_listing_status(l["listing_id"], "rejected")
                        st.warning("Rejected!")
                        st.rerun()
                if st.button("🗑️ Delete", key=f"del_{l['listing_id']}", use_container_width=True):
                    db_helper.delete_listing(l["listing_id"])
                    st.success("Deleted!")
                    st.rerun()


def page_admin_disputes():
    st.markdown("## ⚠️ Manage Disputes")
    filter_s = st.selectbox("Filter", ["open", "resolved", "all"])
    status = None if filter_s == "all" else filter_s
    disputes = db_helper.get_disputes(status)

    if not disputes:
        st.success("🎉 No disputes found!")
        return

    for d in disputes:
        with st.container(border=True):
            c1, c2 = st.columns([4, 2])
            with c1:
                cls = "badge-red" if d["status"] == "open" else "badge-green"
                st.markdown(f'<span class="{cls}">{d["status"]}</span> Order #{d["orderid"]}', unsafe_allow_html=True)
                initiator = (d.get("initiator") or {}).get("fullname", "?")
                st.markdown(f"**Raised by:** {initiator}")
                st.markdown(f"**Reason:** {d.get('reason','')}")
                order = d.get("ordersescrow") or {}
                st.caption(f"💰 Order Amount: {order.get('amount', '?')} pts")
                if d.get("resolution"):
                    st.success(f"Resolution: {d['resolution']}")
            with c2:
                if d["status"] == "open":
                    order = d.get("ordersescrow") or {}
                    buyerid = order.get("buyerid")
                    sellerid = order.get("sellerid")
                    amount = order.get("amount", 0)
                    if st.button("✅ Favor Seller", key=f"fs_{d['disputeid']}", use_container_width=True):
                        db_helper.resolve_dispute(d["disputeid"], d["orderid"],
                                                  "Seller completed work. Payment released.",
                                                  False, st.session_state.admin["adminid"],
                                                  buyerid, sellerid, amount)
                        st.success("Resolved — Seller favored!")
                        st.rerun()
                    if st.button("💰 Refund Buyer", key=f"rb_{d['disputeid']}", use_container_width=True):
                        db_helper.resolve_dispute(d["disputeid"], d["orderid"],
                                                  "Issue verified. Buyer refunded.",
                                                  True, st.session_state.admin["adminid"],
                                                  buyerid, sellerid, amount)
                        st.success("Resolved — Buyer refunded!")
                        st.rerun()


def page_admin_users():
    st.markdown("## 👥 Manage Users")
    search = st.text_input("Search by name or email...")
    users = db_helper.get_all_users()
    if search:
        users = [u for u in users if search.lower() in u["fullname"].lower() or search.lower() in u["email"].lower()]

    st.markdown(f"**{len(users)} users**")
    for u in users:
        with st.container(border=True):
            c1, c2 = st.columns([4, 2])
            with c1:
                susp = u.get("issuspended")
                cls = "badge-red" if susp else "badge-green"
                status = "Suspended" if susp else "Active"
                st.markdown(f'<span class="{cls}">{status}</span> <span class="badge-blue">{u["role"]}</span>', unsafe_allow_html=True)
                st.markdown(f"**{u['fullname']}** — {u['email']}")
                st.caption(f"💰 {u['walletbalance']} pts • ⭐ {u.get('avgrating',0):.1f} • ID: {u['studentid']}")
            with c2:
                label = "✅ Unsuspend" if susp else "🚫 Suspend"
                if st.button(label, key=f"sus_{u['studentid']}", use_container_width=True):
                    db_helper.toggle_suspend(u["studentid"], susp)
                    st.rerun()
                if st.button("🗑️ Delete", key=f"del_{u['studentid']}", use_container_width=True):
                    if st.session_state.get(f"confirm_del_{u['studentid']}"):
                        db_helper.delete_user(u["studentid"])
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{u['studentid']}"] = True
                        st.warning("Click again to confirm!")


def page_admin_orders():
    st.markdown("## 📦 All Orders")
    orders = db_helper.get_all_orders()
    if not orders:
        st.info("No orders yet!")
        return
    df = pd.DataFrame(orders)
    df["buyer"] = df["buyer"].apply(lambda x: (x or {}).get("fullname", "?"))
    df["seller"] = df["seller"].apply(lambda x: (x or {}).get("fullname", "?"))
    df["listing"] = df["skill_listing"].apply(lambda x: (x or {}).get("title", "Custom"))
    df["date"] = pd.to_datetime(df["createdat"]).dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(df[["orderid", "buyer", "seller", "listing", "amount", "escrowstatus", "date"]],
                 use_container_width=True, hide_index=True)


def page_admin_analytics():
    st.markdown("## 📈 Live Analytics")

    orders = db_helper.get_all_orders()
    users = db_helper.get_all_users()
    listings = db_helper.get_listings()
    bids = db_helper.get_all_bids()

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        # Orders over time
        if orders:
            df = pd.DataFrame(orders)
            df["date"] = pd.to_datetime(df["createdat"]).dt.date
            daily = df.groupby("date").size().reset_index(name="orders")
            fig = px.bar(daily, x="date", y="orders", title="📦 Orders Per Day",
                         color_discrete_sequence=["#2563eb"])
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Revenue by day
        if orders:
            df = pd.DataFrame(orders)
            df["date"] = pd.to_datetime(df["createdat"]).dt.date
            rev = df.groupby("date")["amount"].sum().reset_index()
            fig2 = px.area(rev, x="date", y="amount", title="💰 Revenue (pts) Per Day",
                           color_discrete_sequence=["#10b981"])
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig2, use_container_width=True)

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        # Users by role
        if users:
            df = pd.DataFrame(users)
            role_counts = df["role"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]
            fig3 = px.pie(role_counts, values="Count", names="Role", title="👥 Users by Role",
                          color_discrete_sequence=["#2563eb", "#f59e0b", "#10b981"])
            st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Bids analysis
        if bids:
            df = pd.DataFrame(bids)
            bid_status = df["bidstatus"].value_counts().reset_index()
            bid_status.columns = ["Status", "Count"]
            fig4 = px.bar(bid_status, x="Status", y="Count", title="📨 Bids by Status",
                          color="Status",
                          color_discrete_map={"pending": "#f59e0b", "accepted": "#10b981", "rejected": "#ef4444"})
            fig4.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc", showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

    # Row 3 - Top sellers
    st.markdown("### 🏆 Top Sellers by Wallet Balance")
    if users:
        df = pd.DataFrame(users)
        sellers = df[df["role"].isin(["seller", "both"])].sort_values("walletbalance", ascending=False).head(10)
        if not sellers.empty:
            fig5 = px.bar(sellers, x="fullname", y="walletbalance", title="Top Sellers",
                          color_discrete_sequence=["#7c3aed"])
            fig5.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc", xaxis_title="Seller", yaxis_title="Wallet (pts)")
            st.plotly_chart(fig5, use_container_width=True)

    # Listings category breakdown
    st.markdown("### 📊 Listings by Category")
    if listings:
        df = pd.DataFrame(listings)
        df["category_name"] = df["category"].apply(lambda x: (x or {}).get("categoryname", "General"))
        cat_counts = df["category_name"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig6 = px.bar(cat_counts, x="Category", y="Count", title="Listings per Category",
                      color_discrete_sequence=["#2563eb"])
        fig6.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc")
        st.plotly_chart(fig6, use_container_width=True)


# ════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════
render_sidebar()

page = st.session_state.page

if st.session_state.admin:
    if page == "admin_dashboard": page_admin_dashboard()
    elif page == "admin_listings": page_admin_listings()
    elif page == "admin_disputes": page_admin_disputes()
    elif page == "admin_users": page_admin_users()
    elif page == "admin_orders": page_admin_orders()
    elif page == "admin_analytics": page_admin_analytics()
    else: page_admin_dashboard()
elif st.session_state.user:
    if page == "home": page_home()
    elif page == "listings": page_listings()
    elif page == "jobs": page_jobs()
    elif page == "my_orders": page_my_orders()
    elif page == "my_listings": page_my_listings()
    elif page == "dashboard": page_dashboard()
    else: page_dashboard()
else:
    if page == "login": page_login()
    elif page == "register": page_register()
    elif page == "admin_login": page_admin_login()
    elif page == "listings": page_listings()
    elif page == "jobs": page_jobs()
    else: page_home()
