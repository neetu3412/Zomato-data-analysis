import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

st.set_page_config(page_title="Zomato Data Dashboard", layout="wide")
st.title("📊 Zomato Restaurant Data Dashboard")

# Sidebar: Zoom controls
st.sidebar.header("🔍 Zoom Controls") 
zoom_level = st.sidebar.radio("Select Zoom Level", ["Very Small", "Small", "Medium", "Large"], index=1)
zoom_map = {
    "Very Small": (3, 2),
    "Small": (5, 3),
    "Medium": (8, 5),
    "Large": (12, 7)
}
figsize = zoom_map[zoom_level]

# File uploader
uploaded_file = st.file_uploader("Upload your Zomato dataset (CSV)", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        st.success("✅ File uploaded and read successfully!")
    except Exception as e:
        st.error(f"❌ Error reading CSV file: {e}")
        st.stop()

    st.subheader("Preview of Dataset")
    if 'link' in df.columns:
        preview_df = df.head(10).copy()
        preview_df['Menu Link'] = preview_df['link'].apply(
            lambda x: f'<a href="{x.rstrip("/")}/menu" target="_blank">📄 View Menu</a>' if pd.notnull(x) else 'N/A'
        )
        st.write(preview_df[['rest_name', 'loc', 'dine_rating', 'Cost (RS)', 'Menu Link']].to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(df.head(10), use_container_width=True)

    st.markdown("---")
    st.subheader("📌 Basic Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Restaurants", len(df))
        st.metric("Unique Locations", df['loc'].nunique() if 'loc' in df else 0)
    with col2:
        st.metric("Unique Cuisines", df['cuisine'].nunique() if 'cuisine' in df else 0)
        st.metric("Max Cost", f"Rs. {df['Cost (RS)'].max():,.0f}" if 'Cost (RS)' in df else "N/A")
    with col3:
        st.metric("City", "Pune")

    st.markdown("---")
    st.subheader("⭐ Dine & Delivery Ratings Distribution")
    col3, col4 = st.columns(2)
    with col3:
        if 'dine_rating' in df:
            fig2, ax2 = plt.subplots(figsize=figsize)
            sns.histplot(df['dine_rating'].dropna(), bins=10, kde=True, ax=ax2, color='skyblue')
            ax2.set_title("Dine Rating Distribution")
            st.pyplot(fig2)
            avg_dine = df['dine_rating'].mean()
            st.markdown(f"🎯 Insight: The average diner gives a solid {avg_dine:.2f} stars. Not bad, Pune! 🍽️")
    with col4:
        if 'delivery_rating' in df:
            fig3, ax3 = plt.subplots(figsize=figsize)
            sns.histplot(df['delivery_rating'].dropna(), bins=10, kde=True, ax=ax3, color='salmon')
            ax3.set_title("Delivery Rating Distribution")
            st.pyplot(fig3)
            avg_del = df['delivery_rating'].mean()
            st.markdown(f"📦 Insight: Delivery ratings hover around {avg_del:.2f}. Quick bites, happy hearts! 🛵")

    if 'Cost (RS)' in df and 'rest_type' in df:
        st.markdown("---")
        st.subheader("💰 Average Cost by Restaurant Type (Exploded)")
        rest_df = df[['rest_type', 'Cost (RS)']].dropna()
        rest_df['rest_type'] = rest_df['rest_type'].astype(str).str.split(",")
        rest_df = rest_df.explode('rest_type')
        rest_df['rest_type'] = rest_df['rest_type'].str.strip()
        avg_cost = rest_df.groupby('rest_type')['Cost (RS)'].mean().sort_values(ascending=False).head(10)
        fig4, ax4 = plt.subplots(figsize=figsize)
        sns.barplot(x=avg_cost.values, y=avg_cost.index, ax=ax4, palette="Spectral")
        ax4.set_title("Avg. Cost by Individual Restaurant Type")
        st.pyplot(fig4)
        st.markdown(f"💸 Observation: Fancy a luxurious meal? Try *{avg_cost.idxmax()}*, averaging ₹{int(avg_cost.max())}! 👑")

    if 'loc' in df:
        st.markdown("---")
        st.subheader("📍 Top Locations by Outlet Count")
        loc_count = df['loc'].value_counts().head(10)
        fig5, ax5 = plt.subplots(figsize=figsize)
        sns.barplot(x=loc_count.values, y=loc_count.index, ax=ax5, palette="magma")
        ax5.set_title("Top 10 Locations")
        st.pyplot(fig5)
        top_loc = loc_count.index[0]
        st.markdown(f"📍 Observation: *{top_loc}* is Pune’s food central with *{loc_count.iloc[0]}* joints lighting up the map!")

    if 'cuisine' in df and 'name' in df:
        st.markdown("---")
        st.subheader("🍛 Top Restaurants by Selected Cuisine")
        all_cuisines = df['cuisine'].dropna().str.split(",").explode().str.strip().unique()
        selected_cuisine = st.selectbox("Select a Cuisine", sorted(all_cuisines))
        mask = df['cuisine'].str.contains(selected_cuisine, case=False, na=False)
        top_cuisine_df = df[mask].sort_values(by='dine_rating', ascending=False).head(10)
        st.dataframe(top_cuisine_df[['name', 'loc', 'dine_rating', 'Cost (RS)']], use_container_width=True)

    st.markdown("---")
    st.subheader("🎛️ Filter Restaurants by Cost and Rating")
    min_cost, max_cost = int(df['Cost (RS)'].min()), int(df['Cost (RS)'].max())
    cost_range = st.slider("Select Cost Range (Rs)", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
    rating_range = st.slider("Select Rating Range", 0.0, 5.0, (0.0, 5.0), step=0.1)
    filtered_df = df[(df['Cost (RS)'] >= cost_range[0]) & (df['Cost (RS)'] <= cost_range[1]) & 
                     (df['dine_rating'].fillna(0) >= rating_range[0]) & (df['dine_rating'].fillna(0) <= rating_range[1])]
    st.write(f"Filtered Restaurants: {len(filtered_df)}")
    st.dataframe(filtered_df[['rest_name', 'loc', 'dine_rating', 'Cost (RS)']].head(10), use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Correlation Heatmap (Rating, Cost, Votes)")
    corr_cols = ['dine_rating', 'delivery_rating', 'Cost (RS)', 'votes']
    corr_cols = [col for col in corr_cols if col in df.columns]
    corr_df = df[corr_cols].dropna()
    if not corr_df.empty:
        corr = corr_df.corr()
        fig_corr, ax_corr = plt.subplots(figsize=figsize)
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax_corr)
        st.pyplot(fig_corr)
        st.markdown("🧠 Observation: Cost, votes, and ratings are in a tasty tango! Track the heatmap for foodie patterns.")
    else:
        st.info("Not enough data to show correlation heatmap.")

    st.markdown("---")
    st.subheader("🍛 Cuisine Frequency (Top 15)")
    if 'cuisine' in df:
        cuisines_cleaned = df['cuisine'].dropna().str.lower().str.split(",").explode().str.strip()
        cuisines_cleaned = cuisines_cleaned[cuisines_cleaned != ""]
        cuisine_freq = cuisines_cleaned.value_counts().head(15)
        fig_cuisine, ax_cuisine = plt.subplots(figsize=figsize)
        sns.barplot(x=cuisine_freq.values, y=cuisine_freq.index.str.title(), ax=ax_cuisine, palette="Set3")
        ax_cuisine.set_title("Top 15 Cuisines Frequency")
        ax_cuisine.set_xlabel("Count")
        ax_cuisine.set_ylabel("Cuisine")
        st.pyplot(fig_cuisine)
        if not cuisine_freq.empty:
            top_cuisine = cuisine_freq.idxmax().title()
            st.markdown(f"🍽️ Observation: Craving what Pune loves most? It's *{top_cuisine}*, hands down! 😋")
        else:
            st.markdown("*Observation:* No cuisine data available.")

    if 'votes' in df and 'Cost (RS)' in df:
        st.markdown("---")
        st.subheader("📊 Votes vs Cost (Popularity vs Expense)")
        fig_scatter, ax_scatter = plt.subplots(figsize=figsize)
        sns.scatterplot(data=df, x='Cost (RS)', y='votes', hue='dine_rating', palette='cool', ax=ax_scatter)
        ax_scatter.set_title("Votes vs Cost")
        st.pyplot(fig_scatter)
        st.markdown("🔎 Observation: Some pricey picks do pull the crowd—explore the scatter and find your vibe!")

    st.markdown("---")
    st.markdown("## 🚀 Wrapping Up: Your Foodie Footprint in Pune!")
    st.balloons()
    st.markdown("### 🍽️ Your Dashboard Digest")
    st.markdown(f"""
- City Explored: Pune 🏙️  
- Restaurant Universe: {len(df)} total restaurants  
- Top Cuisine Trend: 🍛 {top_cuisine if 'top_cuisine' in locals() else "Surprise Yourself!"}  
- Hotspot Location: 📍 {top_loc if 'top_loc' in locals() else "Somewhere Delicious"}  
- Spendy Spot: 💸 {avg_cost.idxmax() if 'avg_cost' in locals() else "TBD"} restaurants at Rs. {int(avg_cost.max()) if 'avg_cost' in locals() else "?"} on average  
""")

    vibe = st.radio("What's your foodie vibe today?", ["Budget Explorer", "Luxury Feaster", "Hidden Gem Hunter", "Café Hopper"])
    recommend = {
        "Budget Explorer": "Check out spots under ₹300 with 4.0+ rating. 🤑",
        "Luxury Feaster": "Explore fine-dines with 4.5+ rating and exotic cuisines. 👑",
        "Hidden Gem Hunter": "Sort by rating-to-cost ratio and uncover underrated stars. 🔍",
        "Café Hopper": "Filter for 'Café' types, low cost, cozy locations. ☕"
    }
    st.success(f"💡 Tip for {vibe}: {recommend[vibe]}")

    if st.button("🎁 Reveal a Secret Pune Food Tip"):
        tips = [
            "Try late-night shawarmas in Viman Nagar – surprisingly awesome.",
            "Baner has the quirkiest Asian fusion bistros – hidden in plain sight.",
            "Local thalis in Sadashiv Peth beat any fine-dine on authenticity!",
            "Bakeries in Koregaon Park are a morning delight – try one before 9 AM!"
        ]
        st.info(random.choice(tips))

    st.markdown("""
---  
<h3 style='text-align: center; font-size:1.2em;'>Thank you for being a data-savvy foodie! 💡🍕</h3>
<p style='text-align: center; font-size:1em;'>May your ratings be high, your bills be low, and your plates always full.</p>
<h1 style='text-align: center; font-size:1.5em;'>🥳 Bon Appétit, Pune! 🥳</h1>
""", unsafe_allow_html=True)

    st.markdown("Made with 🧠 + ❤️ using Streamlit, Seaborn & a pinch of curiosity.")

else:
    st.warning("📂 Please upload a Zomato-style CSV file to get started.")
