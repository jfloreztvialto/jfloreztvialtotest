import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Function to calculate taxes
def calculate_taxes(filing_status, state, visa_type, income, deductions, age, dependents, other_income, education_expenses, home_ownership, rent_paid, donations, retirement_contributions):
    brackets = {
        "Single": [(0, 11000, 0.1), (11001, 44725, 0.12), (44726, 95375, 0.22), (95376, 182100, 0.24), (182101, 231250, 0.32), (231251, 578125, 0.35), (578126, float('inf'), 0.37)],
        "Married Filing Jointly": [(0, 22000, 0.1), (22001, 89450, 0.12), (89451, 190750, 0.22), (190751, 364200, 0.24), (364201, 462500, 0.32), (462501, 693750, 0.35), (693751, float('inf'), 0.37)],
        "Married Filing Separately": [(0, 11000, 0.1), (11001, 44725, 0.12), (44726, 95375, 0.22), (95376, 182100, 0.24), (182101, 231250, 0.32), (231251, 346875, 0.35), (346875, float('inf'), 0.37)],
        "Head of Household": [(0, 15700, 0.1), (15701, 59850, 0.12), (59851, 95350, 0.22), (95351, 182100, 0.24), (182101, 231250, 0.32), (231251, 578100, 0.35), (578101, float('inf'), 0.37)],
    }

    standard_deductions = {
        "Single": 13850,
        "Married Filing Jointly": 27700,
        "Married Filing Separately": 13850,
        "Head of Household": 20800
    }

    additional_deduction = 0
    if age >= 65:
        additional_deduction = 1850 if filing_status == "Single" or filing_status == "Head of Household" else 1350

    #additional_deduction = 0
    #if age >= 65: additional_deduction == 1850 if filing_status == "Single" or filing_status == "Head of Household" else  additional_deduction = 1350

    # Adjustment for visa type
    visa_adjustment = 1.0
    if visa_type == "Non-resident (F, J, M, Q)":
        visa_adjustment = 0.7  # Example: 30% less deductions

    total_income = income + other_income
    total_deductions = (deductions + education_expenses + donations + retirement_contributions + (rent_paid if not home_ownership else 0)) * visa_adjustment
    taxable_income = max(0, total_income - total_deductions - (standard_deductions[filing_status] + additional_deduction) * visa_adjustment)
    tax = 0
    details = []
    for lower, upper, rate in brackets[filing_status]:
        if taxable_income > upper:
            tax += (upper - lower) * rate
            details.append((upper - lower, (upper - lower) * rate))
        else:
            tax += (taxable_income - lower) * rate
            details.append((taxable_income - lower, (taxable_income - lower) * rate))
            break

    child_tax_credit = 2000 * dependents
    tax -= child_tax_credit
    tax = max(0, tax)  # Ensure tax is not negative
    return tax, details, taxable_income, total_deductions

# App title
st.title("Advanced Tax Calculator 2023")
st.write("This calculator helps you estimate your taxes for 2023 with a detailed breakdown and personalized tax tips.")

# Mandatory information
st.header("Mandatory Information")
filing_status = st.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"], help="Select your filing status for tax purposes.", index=0)
state = st.selectbox("State", ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"], help="Select the state you live in.")
age = st.number_input("Age as of December 31, 2023", min_value=0, help="Enter your age as of December 31, 2023.")
dependents = st.number_input("Number of Dependents", min_value=0, step=1, help="Enter the number of dependents you have.")

if not filing_status or age is None or dependents is None or not state:
    st.error("Please fill out all the mandatory information.")
else:
    # Additional information
    st.header("Additional Information")
    visa_type = st.selectbox("Visa Type", ["Resident", "Non-resident (F, J, M, Q)"], help="Select your visa type.")
    income = st.number_input("Annual Income (USD)", min_value=0, help="Enter your total annual income.")
    other_income = st.number_input("Other Annual Income (USD)", min_value=0, help="Enter any additional income from other sources.")
    deductions = st.number_input("Annual Deductions (USD)", min_value=0, help="Enter your total annual deductions.")
    education_expenses = st.number_input("Annual Education Expenses (USD)", min_value=0, help="Enter your total annual education expenses.")
    home_ownership = st.checkbox("Own a Home?", value=False, help="Check this box if you own a home.")
    rent_paid = st.number_input("Monthly Rent Paid (USD)", min_value=0, help="Enter your total monthly rent paid.") if not home_ownership else 0
    donations = st.number_input("Annual Charitable Donations (USD)", min_value=0, help="Enter your total annual charitable donations.")
    retirement_contributions = st.number_input("Annual Retirement Contributions (USD)", min_value=0, help="Enter your total annual contributions to retirement accounts.")

    # Calculate and display results
    if st.button("Calculate"):
        tax, details, taxable_income, total_deductions = calculate_taxes(filing_status, state, visa_type, income, deductions, age, dependents, other_income, education_expenses, home_ownership, rent_paid * 12, donations, retirement_contributions)
        
        st.header("Tax Summary")
        st.subheader(f"Estimated Tax: ${tax:,.2f}")
        st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
        st.write(f"**Total Deductions:** ${total_deductions:,.2f}")
        st.write(f"**Total Income:** ${income + other_income:,.2f}")

        st.header("Detailed Tax Breakdown")
        st.write("Below is a breakdown of how your income is taxed at each bracket.")
        breakdown_df = pd.DataFrame(details, columns=["Taxable Amount (USD)", "Tax (USD)"])
        st.table(breakdown_df)

        st.markdown("### Detailed Tax Breakdown")
        st.markdown("This table shows how your income is taxed in each bracket:")
        st.markdown("- **Taxable Amount (USD):** The amount of income taxed at that bracket.")
        st.markdown("- **Tax (USD):** The tax calculated for that amount of income.")

        # Improved results visualization
        st.header("Tax Breakdown Visualization")
        fig, ax = plt.subplots()
        brackets = [f"${amt:,.2f}" for amt in breakdown_df["Taxable Amount (USD)"]]
        taxes = breakdown_df["Tax (USD)"]
        ax.bar(brackets, taxes, color='skyblue')
        ax.set_xlabel("Tax Brackets")
        ax.set_ylabel("Tax Amount (USD)")
        ax.set_title("Tax Breakdown by Bracket")
        st.pyplot(fig)

        st.header("Personalized Tax Tips")
        standard_deductions = {
            "Single": 12550,
            "Married Filing Jointly": 25100,
            "Married Filing Separately": 12550,
            "Head of Household": 18800
        }
        if total_deductions < standard_deductions[filing_status]:
            st.markdown("- **Increase Deductions:** Consider increasing your deductions through charitable donations, medical expenses, or retirement contributions.")
        if income > 200000:
            st.markdown("- **Investment Income Tax:** You may be subject to an additional tax on net investment income. Consult with a tax advisor.")
        if dependents > 0:
            st.markdown("- **Child Tax Credit:** Make sure to claim the Child Tax Credit, which is $2000 per dependent child.")
        if education_expenses > 0:
            st.markdown("- **Education Tax Credits:** Explore available tax credits for education expenses, such as the American Opportunity Credit.")
        if retirement_contributions > 0:
            st.markdown("- **Retirement Contributions:** Maximize your contributions to retirement accounts to take advantage of tax benefits.")
        if not home_ownership and rent_paid > 0:
            st.markdown("- **Rent Deductions:** Check if there are state deductions available for rent paid.")
