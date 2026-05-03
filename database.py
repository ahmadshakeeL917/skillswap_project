import streamlit as st
from supabase import create_client

def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def db():
    return get_supabase()
# ─── AUTH ───────────────────────────────────────────
def login_user(email, password):
    res = db().table("users").select("*").eq("email", email).eq("passwordhash", password).execute()
    return res.data[0] if res.data else None

def register_user(fullname, email, password, role):
    res = db().table("users").insert({
        "fullname": fullname, "email": email,
        "passwordhash": password, "role": role,
        "walletbalance": 100, "issuspended": 0, "avgrating": 0
    }).execute()
    if res.data:
        user = res.data[0]
        if role in ("buyer", "both"):
            db().table("buyer_subclass").insert({"studentid": user["studentid"], "totalorders": 0}).execute()
        if role in ("seller", "both"):
            db().table("seller_subclass").insert({"studentid": user["studentid"]}).execute()
        return user
    return None

def login_admin(email, password):
    res = db().table("admin").select("*").eq("email", email).eq("passwordhash", password).execute()
    return res.data[0] if res.data else None

# ─── LISTINGS ───────────────────────────────────────
def get_listings(status=None):
    q = db().table("skill_listing").select("*, users(fullname, avgrating), category(categoryname)")
    if status:
        q = q.eq("approvalstatus", status)
    return q.order("createdat", desc=True).execute().data or []

def create_listing(providerid, title, description, price, categoryid, tags):
    db().table("skill_listing").insert({
        "providerid": providerid, "title": title,
        "description": description, "price": price,
        "categoryid": categoryid if categoryid else None,
        "skilltags": tags, "approvalstatus": "pending"
    }).execute()

def update_listing_status(listing_id, status):
    db().table("skill_listing").update({"approvalstatus": status}).eq("listing_id", listing_id).execute()

def delete_listing(listing_id):
    db().table("skill_listing").delete().eq("listing_id", listing_id).execute()

def get_my_listings(providerid):
    return db().table("skill_listing").select("*, category(categoryname)").eq("providerid", providerid).order("createdat", desc=True).execute().data or []

# ─── CATEGORIES ─────────────────────────────────────
def get_categories():
    return db().table("category").select("*").execute().data or []

# ─── JOBS ───────────────────────────────────────────
def get_jobs(status="open"):
    return db().table("jobpostings").select("*, users(fullname), category(categoryname)").eq("status", status).order("createdat", desc=True).execute().data or []

def create_job(requesterid, title, description, budget, categoryid, isurgent):
    db().table("jobpostings").insert({
        "requesterid": requesterid, "title": title,
        "description": description, "budget": budget,
        "categoryid": categoryid if categoryid else None,
        "isurgent": "yes" if isurgent else "no", "status": "open"
    }).execute()

# ─── BIDS ───────────────────────────────────────────
def get_bids_for_job(jobid):
    return db().table("bids").select("*, users(fullname)").eq("jobid", jobid).execute().data or []

def place_bid(jobid, providerid, amount, note):
    db().table("bids").insert({
        "jobid": jobid, "providerid": providerid,
        "bidamount": amount, "proposalnote": note, "bidstatus": "pending"
    }).execute()

def accept_bid(bidid, jobid):
    db().table("bids").update({"bidstatus": "accepted"}).eq("bidid", bidid).execute()
    db().table("bids").update({"bidstatus": "rejected"}).eq("jobid", jobid).neq("bidid", bidid).execute()
    db().table("jobpostings").update({"status": "in_progress"}).eq("postingid", jobid).execute()

def get_all_bids():
    return db().table("bids").select("*, users(fullname), jobpostings(title)").order("createdat", desc=True).execute().data or []

# ─── ORDERS ─────────────────────────────────────────
def create_order(buyerid, sellerid, listingid, amount):
    res = db().table("ordersescrow").insert({
        "buyerid": buyerid, "sellerid": sellerid,
        "listingid": listingid, "amount": amount, "escrowstatus": "pending"
    }).execute()
    if res.data:
        # Deduct from buyer
        buyer = db().table("users").select("walletbalance").eq("studentid", buyerid).execute().data[0]
        db().table("users").update({"walletbalance": buyer["walletbalance"] - amount}).eq("studentid", buyerid).execute()
        db().table("wallet_transactions").insert({"studentid": buyerid, "amount": -amount, "transactiontype": "order_payment"}).execute()
    return res.data[0] if res.data else None

def get_my_orders(userid, role="buyer"):
    field = "buyerid" if role == "buyer" else "sellerid"
    return db().table("ordersescrow").select("*, skill_listing(title), buyer:users!ordersescrow_buyerid_fkey(fullname), seller:users!ordersescrow_sellerid_fkey(fullname)").eq(field, userid).order("createdat", desc=True).execute().data or []

def complete_order(orderid, sellerid, amount):
    db().table("ordersescrow").update({"escrowstatus": "completed"}).eq("orderid", orderid).execute()
    seller = db().table("users").select("walletbalance").eq("studentid", sellerid).execute().data[0]
    db().table("users").update({"walletbalance": seller["walletbalance"] + amount}).eq("studentid", sellerid).execute()
    db().table("wallet_transactions").insert({"studentid": sellerid, "amount": amount, "transactiontype": "order_received"}).execute()

def get_all_orders():
    return db().table("ordersescrow").select("*, skill_listing(title), buyer:users!ordersescrow_buyerid_fkey(fullname), seller:users!ordersescrow_sellerid_fkey(fullname)").order("createdat", desc=True).execute().data or []

# ─── REVIEWS ────────────────────────────────────────
def submit_review(orderid, reviewerid, revieweeid, rating, comment):
    db().table("reviews").insert({
        "orderid": orderid, "reviewerid": reviewerid,
        "revieweeid": revieweeid, "ratingscore": rating, "comment": comment
    }).execute()

# ─── DISPUTES ───────────────────────────────────────
def raise_dispute(orderid, initiatorid, reason):
    db().table("disputes").insert({"orderid": orderid, "initiatorid": initiatorid, "reason": reason, "status": "open"}).execute()
    db().table("ordersescrow").update({"escrowstatus": "disputed"}).eq("orderid", orderid).execute()

def get_disputes(status=None):
    q = db().table("disputes").select("*, ordersescrow(amount, escrowstatus, buyerid, sellerid), initiator:users!disputes_initiatorid_fkey(fullname, email)")
    if status:
        q = q.eq("status", status)
    return q.order("disputeid", desc=True).execute().data or []

def resolve_dispute(disputeid, orderid, resolution, refund_buyer, adminid, buyerid, sellerid, amount):
    db().table("disputes").update({"status": "resolved", "resolution": resolution, "adminid": adminid}).eq("disputeid", disputeid).execute()
    if refund_buyer:
        db().table("ordersescrow").update({"escrowstatus": "refunded"}).eq("orderid", orderid).execute()
        buyer = db().table("users").select("walletbalance").eq("studentid", buyerid).execute().data[0]
        db().table("users").update({"walletbalance": buyer["walletbalance"] + amount}).eq("studentid", buyerid).execute()
        db().table("wallet_transactions").insert({"studentid": buyerid, "amount": amount, "transactiontype": "dispute_refund"}).execute()
    else:
        db().table("ordersescrow").update({"escrowstatus": "completed"}).eq("orderid", orderid).execute()
        seller = db().table("users").select("walletbalance").eq("studentid", sellerid).execute().data[0]
        db().table("users").update({"walletbalance": seller["walletbalance"] + amount}).eq("studentid", sellerid).execute()
        db().table("wallet_transactions").insert({"studentid": sellerid, "amount": amount, "transactiontype": "order_received"}).execute()

# ─── USERS (admin) ───────────────────────────────────
def get_all_users():
    return db().table("users").select("*").order("studentid", desc=True).execute().data or []

def toggle_suspend(studentid, current):
    db().table("users").update({"issuspended": 0 if current else 1}).eq("studentid", studentid).execute()

def delete_user(studentid):
    db().table("users").delete().eq("studentid", studentid).execute()

# ─── WALLET ─────────────────────────────────────────
def get_transactions(studentid):
    return db().table("wallet_transactions").select("*").eq("studentid", studentid).order("createdat", desc=True).limit(20).execute().data or []

# ─── STATS ──────────────────────────────────────────
def get_stats():
    users     = db().table("users").select("*", count="exact").execute().count or 0
    orders    = db().table("ordersescrow").select("*", count="exact").execute().count or 0
    listings  = db().table("skill_listing").select("*", count="exact").execute().count or 0
    disputes  = db().table("disputes").select("*", count="exact").eq("status","open").execute().count or 0
    pending   = db().table("skill_listing").select("*", count="exact").eq("approvalstatus","pending").execute().count or 0
    return {"users": users, "orders": orders, "listings": listings, "open_disputes": disputes, "pending_listings": pending}
