import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Función para calcular los impuestos
def calculate_taxes(filing_status, income, deductions):
    brackets = {
        "Soltero": [(0, 9950, 0.1), (9951, 40525, 0.12), (40526, 86375, 0.22), (86376, 164925, 0.24)],
        "Casado en conjunto": [(0, 19900, 0.1), (19901, 81050, 0.12), (81051, 172750, 0.22), (172751, 329850, 0.24)],
        "Casado por separado": [(0, 9950, 0.1), (9951, 40525, 0.12), (40526, 86375, 0.22), (86376, 164925, 0.24)],
        "Jefe de familia": [(0, 14200, 0.1), (14201, 54200, 0.12), (54201, 86350, 0.22), (86351, 164900, 0.24)]
    }
    taxable_income = max(0, income - deductions)
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
    return tax, details

# Título de la aplicación
st.title("Calculadora Avanzada de Impuestos")

# Entradas de usuario
st.header("Información Básica")
filing_status = st.selectbox("Estado de Declaración", ["Soltero", "Casado en conjunto", "Casado por separado", "Jefe de familia"])
income = st.number_input("Ingreso Anual (USD)", min_value=0)
deductions = st.number_input("Deducciones (USD)", min_value=0)

# Calcular y mostrar resultados
if st.button("Calcular"):
    tax, details = calculate_taxes(filing_status, income, deductions)
    st.subheader(f"Impuesto Estimado: ${tax:,.2f}")
    
    # Mostrar desglose de tasas impositivas
    st.header("Desglose de Tasas Impositivas")
    breakdown_df = pd.DataFrame(details, columns=["Tramo Imponible (USD)", "Impuesto (USD)"])
    st.table(breakdown_df)
    
    # Visualización de resultados
    fig, ax = plt.subplots()
    brackets = [d[0] for d in details]
    taxes = [d[1] for d in details]
    ax.pie(taxes, labels=brackets, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    
    # Consejos fiscales personalizados
    st.header("Consejos Fiscales")
    if deductions < 12550:
        st.markdown("- Considera incrementar tus deducciones a través de donaciones caritativas, gastos médicos, o contribuciones a cuentas de retiro.")
    if income > 200000:
        st.markdown("- Es posible que debas pagar un impuesto adicional sobre ingresos netos de inversión. Asegúrate de consultarlo con un asesor fiscal.")

# Ejecutar la aplicación
if __name__ == "__main__":
    st.run()
