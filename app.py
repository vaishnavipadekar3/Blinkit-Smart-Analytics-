import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection
import queries


# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(page_title="Blinkit Smart Analytics", layout="wide" ,page_icon="🛒")



# -------------------------
# DB CONNECTION
# -------------------------

conn = get_connection()



# -------------------------
# AUTH FUNCTIONS
# -------------------------

def register_user(conn, username, password):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False


def login_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    return cursor.fetchone()


def auth_page(conn):
    st.title("🔐 Blinkit Login System")

    choice = st.radio("Select Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Create Account"):
            if username == "" or password == "":
                st.warning("⚠️ Enter username & password")
            else:
                if register_user(conn, username, password):
                    st.success("✅ Account created successfully!")
                else:
                    st.error("⚠️ Username already exists")

    elif choice == "Login":
        if st.button("Login"):
            if username == "" or password == "":
                st.warning("⚠️ Enter username & password")
            else:
                user = login_user(conn, username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = username
                    st.success("✅ Login successful")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")


# -------------------------
# SESSION CONTROL
# -------------------------

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    auth_page(conn)
    st.stop()


# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("📌 Navigation")
st.sidebar.success(f"👤 {st.session_state.get('user', 'Guest')}")

# 👤 USER INFO 

st.sidebar.markdown("👤 Welcome, Vaishnavi")


menu = st.sidebar.radio("Select Module", [
    "📊 Overview",
    "📈 Sales Analytics",
    "🌍 Area-wise Customer Distribution",
    "🏆 Top Revenue Products",
    "📅 Daily Revenue",
    "🔁 Repeat vs New Customers",
    "🧾 Avg Order Value per Customer",
    "💎 Most Expensive Products",
    "🙅 Customers with No Orders",
    "👑 Top Customers by Spending",
    "🤖 AI Insights",
    "📊 Reports",
    "SQL Runner"
])




# Logout Button

if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# -------------------------
# TITLE
# -------------------------

st.title("🛒 Blinkit Smart Analytics")

if menu == "📊 Overview":
    st.subheader("📊 Overview")

 # 🔥 FILTERS 

    col1, col2 = st.columns(2)

    start_date = col1.date_input("Start Date")
    end_date = col2.date_input("End Date")


    st.markdown("### 📌 Key Business Metrics")



    # 🔥 KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    # ✅ FILTERED REVENUE

    query = f"""
    SELECT SUM(order_total) AS revenue
    FROM blinkit_orders
    WHERE order_date BETWEEN '{start_date}' AND '{end_date}'
    """
    revenue = pd.read_sql(query, conn)

    revenue = pd.read_sql(queries.total_revenue_query, conn)
    orders = pd.read_sql("SELECT COUNT(*) FROM blinkit_orders", conn)
    customers = pd.read_sql("SELECT COUNT(*) FROM blinkit_customers", conn)
    avg_order = pd.read_sql("SELECT AVG(order_total) FROM blinkit_orders", conn)

    col1.metric("💰 Revenue", f"₹ {int(revenue.iloc[0,0])}")
    col2.metric("📦 Orders", int(orders.iloc[0,0]))
    col3.metric("👥 Customers", int(customers.iloc[0,0]))
    col4.metric("🧾 Avg Order", f"₹ {int(avg_order.iloc[0,0])}")


# =========================
# 🧠 SMART INSIGHTS 
# =========================

    st.subheader("🧠 Smart Insights")

    revenue_val = revenue.iloc[0,0]
    orders_val = orders.iloc[0,0]

    if revenue_val > 500000:
        st.success("🚀 Revenue is performing very well!")
    elif revenue_val > 200000:
        st.info("📈 Revenue is stable with growth potential.")
    else:
        st.warning("⚠️ Revenue is low. Focus on marketing & retention.")

    if orders_val < 100:
        st.warning("📉 Low order volume detected")
    else:
        st.success("📦 Healthy order volume")


# =========================
# 📈 REVENUE TREND CHART 
# =========================

    st.subheader("📈 Revenue Trend")

    df = pd.read_sql(queries.daily_revenue_query, conn)

    st.line_chart(df.set_index("order_date"))

    # Insight
    if df['revenue'].iloc[-1] > df['revenue'].mean():
        st.success("📈 Latest revenue is above average")
    else:
        st.warning("📉 Revenue below average")


# =========================
# 📦 INVENTORY ALERT 
# =========================

    st.subheader("📦 Inventory Alerts")

    df = pd.read_sql(query, conn)

    if len(df) > 0:
        st.error("⚠️ Urgent: High demand but low stock!")
        st.dataframe(df)
    else:
        st.success("✅ Inventory levels are safe")


# ADD LOADING SPINNER

    with st.spinner("Loading data..."):
        df = pd.read_sql(query, conn)

# =========================
# 🚚 DELIVERY INSIGHTS 
# =========================

    st.subheader("🚚 Delivery Insights")

    df = pd.read_sql(queries.delivery_performance_query, conn)

    st.bar_chart(df.set_index("delivery_status"))
    
    delayed = df[df['delivery_status'].str.contains("delayed", case=False)]

    if len(delayed) > 0:
        st.warning("⚠️ Delivery delays detected")
    else:
        st.success("✅ Deliveries are on time")

   
    st.subheader("🧠 Smart Insights")

    revenue_val = revenue.iloc[0,0]
    orders_val = orders.iloc[0,0]

    if revenue_val > 500000:
        st.success("🚀 Revenue is performing very well!")
    elif revenue_val > 200000:
        st.info("📈 Revenue is stable with growth potential.")
    else:
        st.warning("⚠️ Revenue is low. Focus on marketing & retention.")

    if orders_val < 100:
        st.warning("📉 Low order volume detected")
    else:
        st.success("📦 Healthy order volume")    


# -------------------------
# FOOTER
#  -------------------------

    st.markdown("---")
    st.caption("🚀 Blinkit Analytics System | Built by Vaishnavi") 
                    

# -------------------------
# SALES
# -------------------------

if menu == "📈 Sales Analytics":
    st.subheader("Sales Analytics")

    df = pd.read_sql(queries.top_products_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['product_name'], df['total_sold'], color='blue') 
    plt.xlabel("Product")
    plt.ylabel("Total Sold")
    plt.title("Top Products")
    st.pyplot(plt)

# -------------------------
# FOOTER
#  -------------------------

    st.markdown("---")
    st.caption("🚀 Blinkit Analytics System | Built by Vaishnavi")

# Area-wise Customer Distribution :

elif menu == "🌍 Area-wise Customer Distribution":
    st.subheader("📍 Area-wise Customer Distribution")

    df = pd.read_sql(queries.area_distribution_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['area'], df['total_customers'], color='orange')
    plt.xlabel("Area")
    plt.ylabel("total_customers")
    plt.title("Area-wise Customer Distribution")
    st.pyplot(plt)

# Top Revenue Products

elif menu == "🏆 Top Revenue Products":
    st.subheader("Top Revenue Products")

    df = pd.read_sql(queries.top_revenue_products_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['product_name'], df['revenue'], color='green')
    plt.xlabel("Product")
    plt.ylabel("Revenue")
    plt.title("Top Revenue Products")
    st.pyplot(plt)


# daily revenue :

elif menu == "📅 Daily Revenue":
    st.subheader("Daily Revenue")

    df = pd.read_sql(queries.daily_revenue_query, conn)
    st.dataframe(df)

    fig, ax = plt.subplots()
    ax.plot(df['order_date'], df['revenue'], marker='o')
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue")
    ax.set_title("Daily Revenue Trend")
    plt.xticks(rotation=45)
    st.pyplot(fig)

#  Repeat vs New Customers :
elif menu == "🔁 Repeat vs New Customers":
    st.subheader("Repeat vs New Customers")

    df = pd.read_sql(queries.repeat_customers_query, conn)
    st.dataframe(df)

    fig, ax = plt.subplots()
    ax.bar(df['customer_type'], df['total'], color=['blue', 'orange'])
    ax.set_xlabel("Customer Type")
    ax.set_ylabel("Total Customers")
    ax.set_title("Repeat vs New Customers")
    st.pyplot(fig)
    

# avg order value per customer :

elif menu == "🧾 Avg Order Value per Customer":
    st.subheader("Average Order Value per Customer")

    df = pd.read_sql(queries.avg_order_value_query, conn)
    st.dataframe(df)    

    plt.figure(figsize=(10,5))
    plt.bar(df['customer_name'], df['avg_value'], color='orange')
    plt.xlabel("Customer")
    plt.ylabel("Average Order Value")
    plt.title("Average Order Value per Customer")
    plt.xticks(rotation=45)
    st.pyplot(plt)


# Most Expensive Products :

elif menu == "💎 Most Expensive Products":
    st.subheader("Most Expensive Products")

    df = pd.read_sql(queries.expensive_products_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['product_name'], df['price'], color='red')
    plt.xlabel("Product")
    plt.ylabel("Price")
    plt.title("Most Expensive Products")
    plt.xticks(rotation=45)
    st.pyplot(plt)


# Cheapest Products :

elif menu == "💰 Cheapest Products":
    st.subheader("Cheapest Products")

    df = pd.read_sql(queries.cheap_products_query, conn)
    st.dataframe(df)
    
    plt.figure(figsize=(10,5))
    plt.bar(df['product_name'], df['price'], color='green') 
    plt.xlabel("Product")
    plt.ylabel("Price")
    plt.title("Cheapest Products")
    plt.xticks(rotation=45)
    st.pyplot(plt)


# customers with no orders :

        
elif menu == "🙅 Customers with No Orders":
    st.subheader("Customers with No Orders")

    df = pd.read_sql(queries.inactive_customers_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['customer_name'], [1]*len(df), color='red')
    plt.xlabel("Customer")
    plt.ylabel("No Orders")
    plt.title("Customers with No Orders")
    plt.xticks(rotation=45)
    st.pyplot(plt)


# top customers by spending using ntile :

elif menu == "👑 Top Customers by Spending":
    st.subheader("Top Customers by Spending (NTILE)")

    df = pd.read_sql(queries.top_customers_ntile_query, conn)
    st.dataframe(df)

    plt.figure(figsize=(10,5))
    plt.bar(df['customer_name'], df['total_spent'], color='blue')
    plt.xlabel("Customer")
    plt.ylabel("Total Spent")
    plt.title("Top Customers by Spending (NTILE)")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# AI Insights

elif menu == "🤖 AI Insights":

    menu = st.sidebar.selectbox("Smart Insights", [
        "📈 Sales Prediction",
        "📊 Demand Forecast",
        "🧠 Customer Segmentation",
    ])

    # -------------------------
    # 📈 SALES PREDICTION
    # -------------------------

    if menu == "📈 Sales Prediction":
        st.subheader("📈 Sales Prediction")

        df = pd.read_sql(queries.daily_revenue_query, conn)

        # Simple prediction (moving average)
        df['prediction'] = df['revenue'].rolling(3).mean()

        st.line_chart(df.set_index("order_date")[["revenue", "prediction"]])

        st.info("Prediction based on moving average (basic ML logic)")

    # -------------------------
    # 📊 DEMAND FORECAST
    # -------------------------

    elif menu == "📊 Demand Forecast":
        st.subheader("📊 Demand Forecast")

        df = pd.read_sql(queries.top_products_query, conn)

        df['forecast'] = df['total_sold'] * 1.1  # simple future demand logic

        st.dataframe(df)

        st.bar_chart(df.set_index("product_name")[["total_sold", "forecast"]])

    # -------------------------
    # 🧠 CUSTOMER SEGMENTATION
    # -------------------------

    elif menu == "🧠 Customer Segmentation":
        st.subheader("🧠 Customer Segmentation")

        df = pd.read_sql(queries.rfm_analysis_query, conn)

        # Simple segmentation rule
        df['segment'] = df['monetary_value'].apply(
            lambda x: "High Value" if x > 5000 else "Low Value"
        )

        st.dataframe(df)

        st.bar_chart(df['segment'].value_counts())



#  REPORTS

elif menu == "📊 Reports":

    menu = st.sidebar.selectbox("Reports", [
        "📅 Daily Report",
        "📆 Monthly Report"
    ])

    # -------------------------
    # 📅 DAILY REPORT
    # -------------------------

    if menu == "📅 Daily Report":
        st.subheader("📅 Daily Report")

        df = pd.read_sql(queries.daily_report_query, conn)
        st.dataframe(df)

        st.line_chart(df.set_index("order_date")["revenue"])

    # -------------------------
    # 📆 MONTHLY REPORT
    # -------------------------

    elif menu == "📆 Monthly Report":
        st.subheader("📆 Monthly Report")

        df = pd.read_sql(queries.monthly_report_query, conn)
        st.dataframe(df)

        st.bar_chart(df.set_index("month")["revenue"])

  
# SQL Runner

elif menu == "SQL Runner":
    st.subheader("💻 SQL Runner")

    query = st.text_area("Write SQL Query")

    if st.button("Run Query"):
        if not query.strip():
            st.warning("Please enter a SQL query")
        else:
            try:
                df = pd.read_sql(query, conn)
                if df.empty:
                    st.info("No data returned")
                else:
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------
# FOOTER
#  -------------------------

    st.markdown("---")
    st.caption("🚀 Blinkit Analytics System | Built by Vaishnavi")

