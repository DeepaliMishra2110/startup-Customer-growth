import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# input field 
if 'k_val' not in st.session_state:
    st.session_state.k_val = None
if 'r_val' not in st.session_state:
    st.session_state.r_val = None
if 'churn_val' not in st.session_state:
    st.session_state.churn_val = None
if 'steps_val' not in st.session_state:
    st.session_state.steps_val = None
if 'initial_val' not in st.session_state:
    st.session_state.initial_val = None
if 'observed_val' not in st.session_state:
    st.session_state.observed_val = None

# Reset function 
def reset_all():
    st.session_state.k_val = None
    st.session_state.r_val = None
    st.session_state.churn_val = None
    st.session_state.steps_val = None
    st.session_state.initial_val = None
    st.session_state.observed_val = None
    st.rerun()

st.set_page_config(page_title="Startup Customer Growth with Churn", layout="wide")

st.title("📈 Startup Customer Growth with Churn")
st.markdown("""
This project simulates startup customer growth using a **logistic growth model with churn**.

### Model Components
- **New Customers**: customers acquired at each time step
- **Active Customers**: currently retained customers
- **Churned Customers**: customers leaving the startup

### Included Features
- Customer acquisition and dropout simulation
- Logistic growth + parameter estimation
- Retention analysis
- Growth visualization
""")

st.subheader("Simulation Inputs")

col1, col2, col3 = st.columns(3)

with col1:
    k = st.number_input("Carrying Capacity (Maximum Customers)", min_value=100, max_value=1000000, key="k_val")
    churn_rate = st.number_input("Churn Rate", min_value=0.0, max_value=1.0, key="churn_val")

with col2:
    r = st.number_input("Growth Rate (r)", min_value=0.01, max_value=5.0, key="r_val")

    t1, t2 = st.columns([2,1])

    with t1:
        time_steps = st.number_input("Number of Time Steps", min_value=1, max_value=300, key="steps_val")

    with t2:
        time_unit = st.selectbox("Unit", ["Day", "Month", "Year"])

with col3:
    initial_active = st.number_input("Initial Active Customers", min_value=1.0, key="initial_val")
    observed_final_active = st.number_input(
        "Observed Final Active Customers (optional)",
        min_value=0.0,
        key="observed_val",
        help="Enter a real observed final customer count to estimate growth rate r"
    )

# --- BUTTONS SECTION ---
b_col1, b_col2 = st.columns([1, 8])
with b_col1:
    run_button = st.button("🚀 Run Simulation", type="primary")
with b_col2:
    # Reset Button
    st.button("🔄 Reset All Fields", on_click=reset_all)

def simulate_growth(r, k, churn_rate, time_steps, initial_active):
    active = initial_active

    active_list = []
    new_list = []
    churn_list = []
    retention_list = []

    for t in range(int(time_steps)):
        new_customers = r * active * (1 - active / k)
        churned = churn_rate * active
        active = active + new_customers - churned

        if active < 0:
            active = 0

        denom = (active - new_customers + churned)
        retention_rate = ((active - new_customers) / denom) if denom > 0 else 0

        active_list.append(active)
        new_list.append(new_customers)
        churn_list.append(churned)
        retention_list.append(retention_rate)

    peak_active = max(active_list)
    peak_time = active_list.index(peak_active) + 1

    return active_list, new_list, churn_list, retention_list, peak_active, peak_time

def estimate_growth_rate(observed_final, k, churn_rate, time_steps, initial_active):
    best_r = None
    best_error = float("inf")

    candidate_rs = np.linspace(0.01, 2.0, 1000)

    for candidate_r in candidate_rs:
        active_list, _, _, _, _, _ = simulate_growth(candidate_r, k, churn_rate, time_steps, initial_active)
        predicted_final = active_list[-1]
        error = abs(predicted_final - observed_final)

        if error < best_error:
            best_error = error
            best_r = candidate_r

    return best_r, best_error

if run_button:

    if k is None or r is None or churn_rate is None or time_steps is None or initial_active is None:
        st.error("⚠️ Please fill all required inputs!")
    else:

        estimated_r = None
        estimation_error = None

        if observed_final_active and observed_final_active > 0:
            estimated_r, estimation_error = estimate_growth_rate(
                observed_final_active, k, churn_rate, time_steps, initial_active
            )
            r_to_use = estimated_r
        else:
            r_to_use = r

        active_list, new_list, churn_list, retention_list, peak_active, peak_time = simulate_growth(
            r_to_use, k, churn_rate, time_steps, initial_active
        )

        final_active = active_list[-1]
        final_churned = sum(churn_list)
        avg_retention = np.mean(retention_list) * 100 if len(retention_list) > 0 else 0

        st.subheader("Key Results")
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Peak Active Customers", f"{peak_active:.2f}")
        c2.metric("Peak Time Step", f"{peak_time}")
        c3.metric("Final Active Customers", f"{final_active:.2f}")
        c4.metric("Average Retention (%)", f"{avg_retention:.2f}")

        st.subheader("Growth Visualization")

        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots()
            ax1.plot(active_list)
            ax1.set_title("Active Customers")
            ax1.set_xlabel(time_unit + "s")
            ax1.grid(True)
            st.pyplot(fig1)

            st.write("Active customers show the total number of users currently using the service.")
            st.write("This graph reflects overall business growth and stability.")
            st.write("A steady increase indicates successful retention and acquisition.")

        with col2:
            fig2, ax2 = plt.subplots()
            ax2.plot(new_list)
            ax2.set_title("New Customers")
            ax2.set_xlabel(time_unit + "s")
            ax2.grid(True)
            st.pyplot(fig2)

            st.write("New customers represent users joining the platform over time.")
            st.write("This graph shows how fast the startup is acquiring new users.")
            st.write("Higher values indicate strong marketing or growth strategies.")

        col3, col4 = st.columns(2)

        with col3:
            fig3, ax3 = plt.subplots()
            ax3.plot(churn_list)
            ax3.set_title("Churned Customers")
            ax3.set_xlabel(time_unit + "s")
            ax3.grid(True)
            st.pyplot(fig3)

            st.write("Churned customers represent users leaving the platform.")
            st.write("This graph helps identify customer loss trends.")
            st.write("Lower churn indicates better customer satisfaction.")

        with col4:
            fig4, ax4 = plt.subplots()
            ax4.plot([x * 100 for x in retention_list])
            ax4.set_title("Retention Rate (%)")
            ax4.set_xlabel(time_unit + "s")
            ax4.grid(True)
            st.pyplot(fig4)

            st.write("Retention rate shows the percentage of customers staying.")
            st.write("It reflects customer loyalty and product satisfaction.")
            st.write("Higher retention means a healthier business model.")

        # Combined Graph
        st.subheader("Combined Customer Growth (All in One)")

        fig_combined, ax_combined = plt.subplots()
        ax_combined.plot(active_list, label="Active Customers", linewidth=3)
        ax_combined.plot(new_list, label="New Customers", linewidth=3)
        ax_combined.plot(churn_list, label="Churned Customers", linewidth=3)

        ax_combined.set_xlabel(time_unit + "s")
        ax_combined.legend()
        ax_combined.grid(True)

        st.pyplot(fig_combined)

        st.write("This graph combines all customer metrics in one view.")
        st.write("It helps compare growth, acquisition, and churn together.")
        st.write("Useful for overall performance analysis of the startup.")

        # Table
        st.subheader("Simulation Data Table")

        data = pd.DataFrame({
            time_unit: list(range(1, len(active_list) + 1)),
            "New Customers": [int(round(x)) for x in new_list],
            "Churned Customers": [int(round(x)) for x in churn_list],
            "Active Customers": [int(round(x)) for x in active_list]
        })
        st.dataframe(data)

        st.subheader("Model Interpretation")
        st.write(f"""
The maximum number of active customers reached is {peak_active:.2f}, which occurs at {time_unit.lower()} {peak_time}.
The final active customer count is {final_active:.2f}.
The total churn across the simulation is {final_churned:.2f}.
The average retention during the simulation is {avg_retention:.2f}%.
""")
        st.subheader("Conclusion")
        st.write("""
This project helps analyze startup growth by combining customer acquisition, churn, retention, and parameter estimation.
""")