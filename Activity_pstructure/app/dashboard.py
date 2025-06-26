import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from Activity_pstructure.utils.inference_utils import (
    load_csv, load_model, 
    load_transformer, transform_data,
    make_predictions, calculate_custom_metrics
)

# Title
st.title("Health Monitoring Dashboard")


# Fallback to default path if no file uploaded
input_path = r"D:\ActivityP\Activity_pstructure\notebook\testdata2.csv"
df = load_csv(input_path)

# Step 2: Load transformer and transform data
transformer = load_transformer(r"D:\ActivityP\model\transformer.pkl")
X = transform_data(df, transformer)

# Step 3: Load model and predict
model = load_model(r"D:\ActivityP\model\model.pkl")
preds = make_predictions(X, model)

# Step 4: Add predictions
df["prediction"] = preds

# Step 5: Compute custom metrics
df = calculate_custom_metrics(df)

# Add custom spacing columns
spacer1, col1, spacer2, col2, spacer3, col3, spacer4 = st.columns([0.2, 2, 0.2, 2, 0.2, 2, 0.2])

# 🟢 Activity Score Gauge
with col1:
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        number={"suffix": "%"},
        value=df["ActivityScore"].mean(),
        title={"text": "<b>Activity Score</b>"},
        gauge={
            "axis": {"range": [1, 100]},
            "bar": {"color": "#073b4c"},
            "steps": [
                {"range": [1, 40], "color": "#0096c7"},
                {"range": [40, 70], "color": "#023e8a"},
                {"range": [70, 100], "color": "#03045e"}
            ]
        }
    ))
    fig1.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig1, use_container_width=True)

# 🥗 Diet Completion Donut
with col2:
    avg_completion = df["diet_completion"].mean()

    fig2 = go.Figure(go.Pie(
        values=[avg_completion, 100 - avg_completion],
        labels=["Completed", "Recommended"],
        hole=0.4,
        marker_colors=["#0096c7", "#FF4136"],
        textinfo="label",       # Show only labels, not percentages
        hoverinfo="label+percent",  # Optional: show info on hover
        showlegend=False
    ))

    fig2.update_layout(
        title={
        'text': "<b>Average Diet Completion</b>",
        'x': 0.1,          # Move horizontally: 0 = left, 0.5 = center, 1 = right
        'y': 0.75,         # Move vertically: 0 = bottom, 1 = top
        'xanchor': 'left', # Align the title to the left of the x position
        'yanchor': 'top'   # Align the title to the top of the y position
    },
    height=400,
    margin=dict(t=50, b=20, l=20, r=20),
    showlegend=False
    )

    st.plotly_chart(fig2, use_container_width=True)

# 😴 Sleep Quality Gauge
with col3:
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df["sleep_quality_rating"].mean(),
        title={"text": "<b>Sleep Quality</b>"},
        gauge={
            "axis": {"range": [1, 10]},
            "bar": {"color": "#073b4c"},
            "steps": [
                {"range": [1, 4], "color": "#0077b6"},
                {"range": [4, 7], "color": "#023e8a"},
                {"range": [7, 10], "color": "#03045e"}
            ]
        }
    ))
    fig3.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig3, use_container_width=True)

