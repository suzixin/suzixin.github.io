# 计算月供
# 计算提前还款后的月供和节省的利息

total_price = 5210000  # Total house price
down_payment_rate = 0.3  # 30% down payment
loan_public = 1080000  # public accumulation fund loan
annual_rate_public = 0.031  # annual interest rate for public accumulation fund loan

loan_commercial = 2560000  # commercial loan
annual_rate_commercial = 0.046  # annual interest rate for commercial loan


def equal_interest_monthly_interest(principal, monthly_rate, months):
    """Calculate monthly repayment details using equal interest method."""
    fixed_monthly_payment = monthly_payment(principal, monthly_rate * 12)  # using the earlier defined function
    remaining_principal = principal
    monthly_interests = []
    
    for month in range(months):
        monthly_interest = remaining_principal * monthly_rate
        monthly_principal = fixed_monthly_payment - monthly_interest
        monthly_interests.append(monthly_interest)
        remaining_principal -= monthly_principal
        
    return monthly_interests

def equal_interest_monthly_principal(principal, monthly_rate, months):
    """Calculate monthly repayment details using equal interest method."""
    fixed_monthly_payment = monthly_payment(principal, monthly_rate * 12)  # using the earlier defined function
    remaining_principal = principal
    monthly_principals = []
    
    for month in range(months):
        monthly_interest = remaining_principal * monthly_rate
        monthly_principal = fixed_monthly_payment - monthly_interest
        monthly_principals.append(monthly_principal)
        remaining_principal -= monthly_principal
        
    return monthly_principals

def monthly_payment(principal, annual_rate, years=30):
    """Calculate monthly payment using equal principal and interest method."""
    months = years * 12
    monthly_rate = annual_rate / 12
    
    # Formula for equal principal and interest monthly payment
    payment = (principal * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    return payment

def early_repayment(init_principal, remain_principal, annual_rate, early_period, early_repayment_amount, years=30):
    """Calculate monthly payment and saved interest after early repayment."""
    original_total_interest = monthly_payment(init_principal, annual_rate, years) * years * 12 - init_principal
    
    # Deduct early repayment amount from principal
    new_principal = remain_principal - early_repayment_amount
    new_monthly_payment = monthly_payment(new_principal, annual_rate, years - early_period/12)
    
    new_total_interest = new_monthly_payment * (years * 12 - early_period) - new_principal
    monthly_principals_interest = equal_interest_monthly_interest(init_principal, annual_rate / 12, 30 * 12)

    saved_interest = original_total_interest - new_total_interest - sum(monthly_principals_interest[0:early_period])
    
    return new_monthly_payment, saved_interest


# Calculate monthly payments for both loans
def cal_monthly_payment_total(loan_public, annual_rate_public, loan_commercial, annual_rate_commercial):
    """Calculate monthly payment"""
    monthly_payment_public = monthly_payment(loan_public, annual_rate_public)
    monthly_payment_commercial = monthly_payment(loan_commercial, annual_rate_commercial)

    # Total monthly payment
    total_monthly_payment = monthly_payment_public + monthly_payment_commercial

    return total_monthly_payment


def early_repayment_total_updated_v3(principal_public, annual_rate_public, principal_commercial, annual_rate_commercial, early_period, early_repayment_amount):
    """Calculate monthly payment and saved interest after early repayment for combined loans."""
    
    # Calculate remaining principal for commercial loan after early_period using equal interest method
    monthly_principals_commercial = equal_interest_monthly_principal(principal_commercial, annual_rate_commercial / 12, 30 * 12)
    remaining_principal_commercial = principal_commercial - sum(monthly_principals_commercial[:early_period])
    
    # Determine which loan the early repayment is applied to
    if early_repayment_amount <= remaining_principal_commercial:
        new_monthly_payment_commercial, saved_interest_commercial = early_repayment(principal_commercial, remaining_principal_commercial, annual_rate_commercial, early_period, early_repayment_amount)
        new_monthly_payment_public = monthly_payment(principal_public, annual_rate_public)
        saved_interest_public = 0
    else:
        # 暂时不考虑提前还公积金的贷款
        pass
    
    new_total_monthly_payment = new_monthly_payment_public + new_monthly_payment_commercial
    total_saved_interest = saved_interest_public + saved_interest_commercial
    
    return new_total_monthly_payment, total_saved_interest

# Test the function with an example
print(cal_monthly_payment_total(loan_public, annual_rate_public, loan_commercial, annual_rate_commercial))
print (early_repayment_total_updated_v3(loan_public, annual_rate_public, loan_commercial, annual_rate_commercial, 36, 1272000))
