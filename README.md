# 🔄 SkillSwap — Student Freelance Marketplace

A full-stack student-powered freelance marketplace built with **Streamlit** and **Supabase**. Students can trade skills, post jobs, place bids, and transact using an **escrow-based wallet system** — all with admin moderation.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---


### 👤 User Features
- **Registration & Login** — Sign up as Buyer, Seller, or Both
- **Browse Skills** — Search and filter approved skill listings by category
- **Order from Listings** — One-click ordering with instant wallet deduction
- **Job Postings** — Buyers post jobs, sellers place bids with proposals
- **Bid System** — Accept/reject bids with automatic order creation
- **My Orders** — Track buying and selling orders in real-time
- **Reviews & Ratings** — Leave reviews after order completion; seller `avgrating` auto-updates
- **Wallet Dashboard** — View balance, transaction history, and cumulative balance chart
- **Dispute System** — Raise disputes on active orders

### 🛡️ Admin Features
- **Dashboard** — Overview stats: users, orders, listings, disputes
- **Listing Moderation** — Approve/reject/delete skill listings
- **Job Moderation** — Approve/reject/delete job postings
- **Dispute Resolution** — Favor seller (release payment) or refund buyer
- **User Management** — Suspend/unsuspend/delete users
- **Order Tracking** — View all orders with buyer/seller details
- **Live Analytics** — Charts for orders, revenue, user roles, bids, top sellers, categories

### 💰 Escrow Payment System
- **Buyer places order** → Wallet deducted → Funds held in escrow
- **Buyer accepts bid** → Wallet deducted → Order auto-created → Escrow hold
- **Buyer marks complete** → Seller receives payment
- **Dispute raised** → Admin resolves → Refund buyer OR release to seller
- **All transactions logged** in `wallet_transactions` table

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (Python) |
| Backend | Python |
| Database | Supabase (PostgreSQL) |
| Data | Pandas |
| Auth | Custom (email + password via Supabase table) |

---

## 🗄️ Database Schema (ERD)

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│    users      │     │  skill_listing   │     │   category   │
├──────────────┤     ├──────────────────┤     ├──────────────┤
│ studentid PK │◄────│ providerid FK    │     │ categoryid PK│
│ fullname     │     │ listing_id PK    │────►│ categoryname │
│ email        │     │ title            │     └──────────────┘
│ passwordhash │     │ description      │
│ role         │     │ price            │
│ walletbalance│     │ categoryid FK    │
│ avgrating    │     │ skilltags        │
│ issuspended  │     │ approvalstatus   │
└──────┬───────┘     │ createdat        │
       │             └──────────────────┘
       │
       │     ┌──────────────────┐     ┌──────────────┐
       │     │  ordersescrow    │     │   reviews    │
       │     ├──────────────────┤     ├──────────────┤
       ├────►│ buyerid FK       │     │ reviewid PK  │
       ├────►│ sellerid FK      │     │ orderid FK   │
       │     │ orderid PK       │◄────│ reviewerid FK│
       │     │ listingid FK     │     │ revieweeid FK│
       │     │ amount           │     │ ratingscore  │
       │     │ escrowstatus     │     │ comment      │
       │     │ createdat        │     │ createdat    │
       │     └──────────────────┘     └──────────────┘
       │
       │     ┌──────────────────┐     ┌──────────────┐
       │     │  jobpostings     │     │    bids      │
       │     ├──────────────────┤     ├──────────────┤
       ├────►│ requesterid FK   │     │ bidid PK     │
       │     │ postingid PK     │◄────│ jobid FK     │
       │     │ title            │     │ providerid FK│
       │     │ description      │     │ bidamount    │
       │     │ budget           │     │ proposalnote │
       │     │ categoryid FK    │     │ bidstatus    │
       │     │ isurgent         │     │ createdat    │
       │     │ status           │     └──────────────┘
       │     │ approvalstatus   │
       │     │ createdat        │
       │     └──────────────────┘
       │
       │     ┌─────────────────────┐   ┌──────────────┐
       │     │ wallet_transactions │   │  disputes    │
       │     ├─────────────────────┤   ├──────────────┤
       ├────►│ studentid FK        │   │ disputeid PK │
       │     │ transactionid PK    │   │ orderid FK   │
       │     │ amount              │   │ initiatorid  │
       │     │ transactiontype     │   │ reason       │
       │     │ createdat           │   │ status       │
       │     └─────────────────────┘   │ resolution   │
       │                               │ adminid FK   │
       │     ┌──────────────────┐      └──────────────┘
       │     │ buyer_subclass   │
       │     ├──────────────────┤      ┌──────────────┐
       ├────►│ studentid FK/PK  │      │    admin     │
       │     │ totalorders      │      ├──────────────┤
       │     └──────────────────┘      │ adminid PK   │
       │                               │ username     │
       │     ┌──────────────────┐      │ email        │
       │     │ seller_subclass  │      │ passwordhash │
       │     ├──────────────────┤      └──────────────┘
       └────►│ studentid FK/PK  │
             └──────────────────┘
```

---

## 📁 Project Structure

```
skillswap_streamlit/
├── .streamlit/
│   └── secrets.toml        # Supabase URL & API key (DO NOT COMMIT)
├── app.py                   # Main Streamlit application (all pages & UI)
├── database.py              # Supabase database helper functions
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A [Supabase](https://supabase.com/) account (free tier works)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/skillswap_streamlit.git
cd skillswap_streamlit
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Supabase Secrets

Create the file `.streamlit/secrets.toml`:
## 🗄️ Supabase Database Setup

Run the following SQL in Supabase **SQL Editor** to create all tables:

```sql
-- 1. Users Table
CREATE TABLE users (
    studentid SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    passwordhash VARCHAR(255) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('buyer', 'seller', 'both')) NOT NULL,
    walletbalance NUMERIC DEFAULT 100,
    avgrating NUMERIC DEFAULT 0,
    issuspended INTEGER DEFAULT 0,
    createdat TIMESTAMP DEFAULT NOW()
);

-- 2. Admin Table
CREATE TABLE admin (
    adminid SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    passwordhash VARCHAR(255) NOT NULL
);

-- 3. Category Table
CREATE TABLE category (
    categoryid SERIAL PRIMARY KEY,
    categoryname VARCHAR(100) NOT NULL
);

-- 4. Skill Listings
CREATE TABLE skill_listing (
    listing_id SERIAL PRIMARY KEY,
    providerid INTEGER REFERENCES users(studentid) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC NOT NULL,
    categoryid INTEGER REFERENCES category(categoryid),
    skilltags TEXT[],
    approvalstatus VARCHAR(20) DEFAULT 'pending',
    createdat TIMESTAMP DEFAULT NOW()
);

-- 5. Job Postings
CREATE TABLE jobpostings (
    postingid SERIAL PRIMARY KEY,
    requesterid INTEGER REFERENCES users(studentid) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    budget NUMERIC NOT NULL,
    categoryid INTEGER REFERENCES category(categoryid),
    isurgent VARCHAR(5) DEFAULT 'no',
    status VARCHAR(20) DEFAULT 'open',
    approvalstatus VARCHAR(20) DEFAULT 'pending',
    createdat TIMESTAMP DEFAULT NOW()
);

-- 6. Bids
CREATE TABLE bids (
    bidid SERIAL PRIMARY KEY,
    jobid INTEGER REFERENCES jobpostings(postingid) ON DELETE CASCADE,
    providerid INTEGER REFERENCES users(studentid) ON DELETE CASCADE,
    bidamount NUMERIC NOT NULL,
    proposalnote TEXT,
    bidstatus VARCHAR(20) DEFAULT 'pending',
    createdat TIMESTAMP DEFAULT NOW()
);

-- 7. Orders / Escrow
CREATE TABLE ordersescrow (
    orderid SERIAL PRIMARY KEY,
    buyerid INTEGER REFERENCES users(studentid),
    sellerid INTEGER REFERENCES users(studentid),
    listingid INTEGER REFERENCES skill_listing(listing_id),
    amount NUMERIC NOT NULL,
    escrowstatus VARCHAR(20) DEFAULT 'active',
    createdat TIMESTAMP DEFAULT NOW()
);

-- 8. Reviews
CREATE TABLE reviews (
    reviewid SERIAL PRIMARY KEY,
    orderid INTEGER REFERENCES ordersescrow(orderid),
    reviewerid INTEGER REFERENCES users(studentid),
    revieweeid INTEGER REFERENCES users(studentid),
    ratingscore INTEGER CHECK (ratingscore BETWEEN 1 AND 5),
    comment TEXT,
    createdat TIMESTAMP DEFAULT NOW()
);

-- 9. Disputes
CREATE TABLE disputes (
    disputeid SERIAL PRIMARY KEY,
    orderid INTEGER REFERENCES ordersescrow(orderid),
    initiatorid INTEGER REFERENCES users(studentid),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'open',
    resolution TEXT,
    adminid INTEGER REFERENCES admin(adminid),
    createdat TIMESTAMP DEFAULT NOW()
);

-- 10. Wallet Transactions
CREATE TABLE wallet_transactions (
    transactionid SERIAL PRIMARY KEY,
    studentid INTEGER REFERENCES users(studentid) ON DELETE CASCADE,
    amount NUMERIC NOT NULL,
    transactiontype VARCHAR(50) NOT NULL,
    createdat TIMESTAMP DEFAULT NOW()
);

-- 11. Buyer Subclass
CREATE TABLE buyer_subclass (
    studentid INTEGER PRIMARY KEY REFERENCES users(studentid) ON DELETE CASCADE,
    totalorders INTEGER DEFAULT 0
);

-- 12. Seller Subclass
CREATE TABLE seller_subclass (
    studentid INTEGER PRIMARY KEY REFERENCES users(studentid) ON DELETE CASCADE
);

-- ─── Insert Default Categories ───
INSERT INTO category (categoryname) VALUES
    ('Web Development'),
    ('Mobile App Development'),
    ('Graphic Design'),
    ('Video Editing'),
    ('Content Writing'),
    ('Data Entry'),
    ('SEO & Marketing'),
    ('Tutoring'),
    ('Translation'),
    ('Other');

-- ─── Insert Default Admin ───
INSERT INTO admin (username, email, passwordhash) VALUES
    ('Admin', 'admin@skillswap.com', 'admin123');
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8...`

## 👥 User Roles & Flows

### 🛒 Buyer Flow
1. Register as **Buyer** (gets 100 pts wallet)
2. **Browse Skills** → Order a listing → Wallet deducted → Order created
3. **Post a Job** → Admin approves → Sellers bid → Accept best bid → Order + escrow
4. **Mark Complete** → Seller gets paid
5. **Leave Review** → Seller rating updates

### 💼 Seller Flow
1. Register as **Seller** (gets 100 pts wallet)
2. **Create Listing** → Admin approves → Appears in Browse Skills
3. **Browse Jobs** → Place bid with proposal → Wait for buyer acceptance
4. **Receive Orders** → Complete work → Get paid when buyer marks complete

### 🛡️ Admin Flow
1. Login via **Admin Login**
2. **Approve/Reject** listings and job postings
3. **Resolve Disputes** — Favor seller or refund buyer
4. **Manage Users** — Suspend/delete accounts
5. **View Analytics** — Orders, revenue, bids, categories

---

## 💰 Escrow Payment Flow

```
┌─────────┐    Order/Bid Accept     ┌──────────────┐
│  Buyer  │ ──────────────────────► │   Escrow     │
│ Wallet  │    -amount (deducted)   │   (active)   │
└─────────┘                         └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                         Mark Complete   Dispute    Dispute
                              │         (open)     (resolved)
                              ▼            │            │
                     ┌──────────────┐      │     ┌──────┴──────┐
                     │   Seller     │      │     │ Favor Seller│
                     │   Wallet     │      │     │ +amount     │
                     │   +amount    │      │     └─────────────┘
                     └──────────────┘      │
                                           │     ┌─────────────┐
                                           └────►│ Refund Buyer│
                                                 │ +amount     │
                                                 └─────────────┘
```

### Transaction Types in Database
| Type | Description |
|------|------------|
| `order_payment` | Buyer wallet deducted (listing order) |
| `escrow_hold` | Buyer wallet deducted (bid accepted) |
| `order_received` | Seller wallet credited (order completed) |
| `dispute_refund` | Buyer wallet refunded (dispute resolved) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

**Made with ❤️ by SkillSwap Team**
