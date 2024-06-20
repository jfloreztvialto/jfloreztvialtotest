import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Function to calculate federal taxes
def calculate_taxes(filing_status, state, visa_type, income_details, deductions_details, personal_details, foreign_credits):
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
    if personal_details['age'] >= 65:
        additional_deduction = 1850 if filing_status == "Single" or filing_status == "Head of Household" else 1350

    # Adjustment for visa type
    visa_adjustment = 1.0
    if visa_type == "Non-resident (F, J, M, Q)":
        visa_adjustment = 0.7  # Example: 30% less deductions

    total_income = income_details['google_salary'] + income_details['google_bonus'] + income_details['other_income'] + income_details['interests'] + income_details['dividends']
    total_deductions = (deductions_details['deductions'] + deductions_details['education_expenses'] + deductions_details['donations'] + deductions_details['retirement_contributions'] + (deductions_details['rent_paid'] if not deductions_details['home_ownership'] else 0) + foreign_credits) * visa_adjustment
    taxable_income = max(0, total_income - total_deductions - (standard_deductions[filing_status] + additional_deduction))
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

    child_tax_credit = 2000 * personal_details['dependents']
    tax -= child_tax_credit
    tax = max(0, tax)  # Ensure tax is not negative
    return tax, details, taxable_income, total_deductions, standard_deductions

# Function to calculate state taxes
def calculate_state_taxes(state, filing_status, income_details):
    no_income_tax_states = ["Alaska", "Florida", "Nevada", "South Dakota", "Tennessee", "Texas", "Wyoming"]
    flat_rate_states = {
        "Arizona": {"rate": 0.03, "standard_deduction": {"Single": 14600, "Couple": 29200}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 100}},
        "Colorado": {"rate": 0.04, "standard_deduction": {"Single": 14600, "Couple": 29200}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 0}},
        "Georgia": {"rate": 0.05, "standard_deduction": {"Single": 12000, "Couple": 24000}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 3000}},
        "Idaho": {"rate": 0.058, "standard_deduction": {"Single": 14600, "Couple": 29200}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 0}},
        "Illinois": {"rate": 0.05, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 2775, "Couple": 5550, "Dependent": 2775}},
        "Indiana": {"rate": 0.03, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 1000, "Couple": 2000, "Dependent": 1000}},
        "Kentucky": {"rate": 0.04, "standard_deduction": {"Single": 3160, "Couple": 6320}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 0}},
        "Michigan": {"rate": 0.04, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 5600, "Couple": 11200, "Dependent": 5600}},
        "Mississippi": {"rate": 0.05, "standard_deduction": {"Single": 2300, "Couple": 4600}, "personal_exemption": {"Single": 6000, "Couple": 12000, "Dependent": 1500}},
        "New Hampshire": {"rate": 0.03, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 2400, "Couple": 4800, "Dependent": 0}},
        "North Carolina": {"rate": 0.05, "standard_deduction": {"Single": 12750, "Couple": 25500}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 0}},
        "Pennsylvania": {"rate": 0.03, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 0, "Couple": 0, "Dependent": 0}},
        "Utah": {"rate": 0.05, "standard_deduction": {"Single": 0, "Couple": 0}, "personal_exemption": {"Single": 876, "Couple": 1752, "Dependent": 1941}},
    }

    if state in no_income_tax_states:
        return 0, "State with no Income Tax", 0, 0, 0, 0

    if state in flat_rate_states:
        state_info = flat_rate_states[state]
        rate = state_info["rate"]
        standard_deduction = state_info["standard_deduction"]["Single"]
        personal_exemption = state_info["personal_exemption"]["Single"]
        if filing_status == "Married Filing Jointly":
            standard_deduction = state_info["standard_deduction"]["Couple"]
            personal_exemption = state_info["personal_exemption"]["Couple"]
        if filing_status == "Married Filing Separately":
            standard_deduction = state_info["standard_deduction"]["Single"]
            personal_exemption = state_info["personal_exemption"]["Single"]
        total_income = income_details['google_salary'] + income_details['google_bonus'] + income_details['other_income'] + income_details['interests'] + income_details['dividends']
        taxable_income = max(0, total_income - standard_deduction - personal_exemption)
        state_tax = taxable_income * rate
        return state_tax, f"Flat rate of {rate * 100}% applies", total_income, taxable_income, standard_deduction, personal_exemption
    
    return 0, "State tax not calculated for selected state.", 0, 0, 0, 0

# App title
st.title("Google Tax Tool 2023")
st.write("This calculator helps you estimate your taxes for 2023 with a detailed breakdown and personalized tax tips.")

# Mandatory information
st.header("Mandatory Information")
filing_status = st.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"], help="Select your filing status for tax purposes.", index=0)
state = st.selectbox("State", ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"], help="Select the state you live in.")
age = st.number_input("Age as of December 31, 2023", min_value=0, help="Enter your age as of December 31, 2023.")
dependents = st.number_input("Number of Dependents", min_value=0, step=1, help="Enter the number of dependents you have.")
country = st.selectbox("Country", ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo, Democratic Republic of the", "Congo, Republic of the", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"], help="Select the country you live in.")
assignment_start_date = st.date_input("Assignment Start Date", help="Select the start date of the assignment.")
assignment_end_date = st.date_input("Assignment End Date", help="Select the end date of the assignment.")

foreign_credits = 0
if country != "United States":
    foreign_credits = st.number_input("Foreign Credits (USD)", min_value=0, help="Enter the total foreign credits for tax deduction.")

state_tax_message = ""
state_tax = 0
no_income_tax_states = ["Alaska", "Florida", "Nevada", "South Dakota", "Tennessee", "Texas", "Wyoming"]

if state:
    state_tax, state_tax_message, state_total_income, state_taxable_income, state_standard_deduction, state_personal_exemption = calculate_state_taxes(state, filing_status, {
        'google_salary': st.session_state.get('google_salary', 0),
        'google_bonus': st.session_state.get('google_bonus', 0),
        'other_income': st.session_state.get('other_income', 0),
        'interests': st.session_state.get('interests', 0),
        'dividends': st.session_state.get('dividends', 0)
    })
    st.write(state_tax_message)

if not filing_status or age is None or dependents is None or not state:
    st.error("Please fill out all the mandatory information.")
else:
    # Additional information
    st.header("Additional Information")
    visa_type = st.selectbox("Visa Type", ["Resident", "Non-resident (F, J, M, Q)"], help="Select your visa type.")
    
    income_details = {
        'google_salary': st.number_input("Total Annual Google Salary (USD)", min_value=0, help="Enter your total annual Google salary."),
        'google_bonus': st.number_input("Total Google Bonus (USD)", min_value=0, help="Enter your total Google bonus."),
        'other_income': st.number_input("Other Annual Income (USD)", min_value=0, help="Enter any additional income from other sources."),
        'interests': st.number_input("Interests (USD)", min_value=0, help="Enter the total interest income."),
        'dividends': st.number_input("Dividends (USD)", min_value=0, help="Enter the total dividend income.")
    }
    
    home_ownership = st.checkbox("Own a Home?", key="home_ownership", value=False, help="Check this box if you own a home.")
    deductions_details = {
        'deductions': st.number_input("Annual Deductions (USD)", min_value=0, help="Enter your total annual deductions."),
        'education_expenses': st.number_input("Annual Education Expenses (USD)", min_value=0, help="Enter your total annual education expenses."),
        'home_ownership': home_ownership,
        'rent_paid': st.number_input("Monthly Rent Paid (USD)", min_value=0, help="Enter your total monthly rent paid.", key="rent_paid") if not home_ownership else 0,
        'donations': st.number_input("Annual Charitable Donations (USD)", min_value=0, help="Enter your total annual charitable donations."),
        'retirement_contributions': st.number_input("Annual Retirement Contributions (USD)", min_value=0, help="Enter your total annual contributions to retirement accounts.")
    }

    personal_details = {
        'age': age,
        'dependents': dependents
    }

    # Calculate and display results
    if st.button("Calculate"):
        # Update session state with current income details
        st.session_state['google_salary'] = income_details['google_salary']
        st.session_state['google_bonus'] = income_details['google_bonus']
        st.session_state['other_income'] = income_details['other_income']
        st.session_state['interests'] = income_details['interests']
        st.session_state['dividends'] = income_details['dividends']

        tax, details, taxable_income, total_deductions, standard_deductions = calculate_taxes(filing_status, state, visa_type, income_details, deductions_details, personal_details, foreign_credits)
        
        st.header("Tax Summary")
        st.subheader(f"Estimated Federal Tax: ${tax:,.2f}")
        st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
        st.write(f"**Total Deductions:** ${total_deductions:,.2f}")
        st.write(f"**Total Income:** ${income_details['google_salary'] + income_details['google_bonus'] + income_details['other_income'] + income_details['interests'] + income_details['dividends']:,.2f}")

        if state not in no_income_tax_states:
            st.subheader(f"Estimated State Tax: ${state_tax:,.2f}")
            st.write(f"**State Total Income:** ${state_total_income:,.2f}")
            st.write(f"**State Taxable Income:** ${state_taxable_income:,.2f}")
            st.write(f"**State Standard Deduction:** ${state_standard_deduction:,.2f}")
            st.write(f"**State Personal Exemption:** ${state_personal_exemption:,.2f}")

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
        if total_deductions < standard_deductions[filing_status]:
            st.markdown("- **Increase Deductions:** Consider increasing your deductions through charitable donations, medical expenses, or retirement contributions.")
        if income_details['google_salary'] + income_details['google_bonus'] > 200000:
            st.markdown("- **Investment Income Tax:** You may be subject to an additional tax on net investment income. Consult with a tax advisor.")
        if personal_details['dependents'] > 0:
            st.markdown("- **Child Tax Credit:** Make sure to claim the Child Tax Credit, which is $2000 per dependent child.")
        if deductions_details['education_expenses'] > 0:
            st.markdown("- **Education Tax Credits:** Explore available tax credits for education expenses, such as the American Opportunity Credit.")
        if deductions_details['retirement_contributions'] > 0:
            st.markdown("- **Retirement Contributions:** Maximize your contributions to retirement accounts to take advantage of tax benefits.")
        if not deductions_details['home_ownership'] and deductions_details['rent_paid'] > 0:
            st.markdown("- **Rent Deductions:** Check if there are state deductions available for rent paid.")
