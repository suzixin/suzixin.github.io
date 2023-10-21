# 三年后开始提前还贷， 计算最快多久可以把商业贷款还完
# 一年后开始提前还贷， 计算最快多久可以把商业贷款还完

# Given data
init_mortgate_monthly = 17735
annual_income = 820000  # Every year's total income
annual_expenses_including_mortgage = 396000  # Every year's expenses including mortgage
annual_expenses_excluding_mortgage = 192000  # Every year's expenses excluding mortgage

# Defining the necessary functions provided earlier

def equal_interest_monthly_interest(principal, monthly_rate, months):
    """Calculate monthly repayment details using equal interest method."""
    fixed_monthly_payment = monthly_payment(principal, monthly_rate * 12, months)
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
    fixed_monthly_payment = monthly_payment(principal, monthly_rate * 12, months)
    remaining_principal = principal
    monthly_principals = []
    
    for month in range(months):
        monthly_interest = remaining_principal * monthly_rate
        monthly_principal = fixed_monthly_payment - monthly_interest
        monthly_principals.append(monthly_principal)
        remaining_principal -= monthly_principal
        
    return monthly_principals

def monthly_payment(principal, annual_rate, months=360):
    """Calculate monthly payment using equal principal and interest method."""
    monthly_rate = annual_rate / 12
    
    # Formula for equal principal and interest monthly payment
    payment = (principal * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    return payment

def early_repayment(init_principal, remain_principal, annual_rate, early_period, early_repayment_amount, months=360):
    """Calculate monthly payment and saved interest after early repayment."""
    # As is : 剩余应付利息
    global remaining_interest
    
    # Deduct early repayment amount from principal
    new_principal = remain_principal - early_repayment_amount
    new_monthly_payment = monthly_payment(new_principal, annual_rate, months - early_period)
    
    # TO BE : 提前还款后的剩余应付利息
    new_total_interest = new_monthly_payment * (months - early_period) - new_principal

    saved_interest = remaining_interest - new_total_interest
    
    return new_monthly_payment, saved_interest

def early_repayment_total_updated_v4(principal_public, annual_rate_public, principal_commercial, annual_rate_commercial, early_period, early_repayment_amount, remaining_principal):
    """Calculate monthly payment and saved interest after early repayment for combined loans."""
    # Determine which loan the early repayment is applied to
    if early_repayment_amount <= remaining_principal:
        new_monthly_payment_commercial, saved_interest_commercial = early_repayment(principal_commercial, remaining_principal, annual_rate_commercial, early_period, early_repayment_amount)
        new_monthly_payment_public = monthly_payment(principal_public, annual_rate_public)
        saved_interest_public = 0
    else:
        # TODO:暂时不考虑提前还公积金的贷款
        pass
    
    new_total_monthly_payment = new_monthly_payment_public + new_monthly_payment_commercial
    total_saved_interest = saved_interest_public + saved_interest_commercial
    
    return new_total_monthly_payment, total_saved_interest

# Constants
loan_public = 1080000  # public accumulation fund loan
annual_rate_public = 0.031  # annual interest rate for public accumulation fund loan

loan_commercial = 2560000  # commercial loan
annual_rate_commercial = 0.046  # annual interest rate for commercial loan
mortgate_monthly = init_mortgate_monthly
# Now, we simulate the early repayment to calculate how long it will take to repay the commercial loan

monthly_principals_commercial = equal_interest_monthly_principal(loan_commercial, annual_rate_commercial / 12, 30 * 12)
remaining_principal_commercial_after_1_years = loan_commercial - sum(monthly_principals_commercial[:12])
remaining_interest_commercial_after_1_years = sum(equal_interest_monthly_interest(loan_commercial, annual_rate_commercial / 12, 30 * 12)[12:])

# status #
# TODO： 前三年内，需要考虑提前还款的手续费 = 还款金额 x 当前贷款利率 ÷ 12 x 3
# 这里暂时考虑三年之后再开始提前还款
months_to_repay = 12
remaining_principal = remaining_principal_commercial_after_1_years
remaining_interest = remaining_interest_commercial_after_1_years

while remaining_principal > 0:
    annual_savings = annual_income - annual_expenses_excluding_mortgage - mortgate_monthly * 12
    print('第' ,int(months_to_repay/12+1), '年初')
    print('储蓄率' ,annual_savings/annual_income)
    if months_to_repay < 36:
        # 前三年内提前还贷需要扣违约金 还款金额 x 当前贷款利率÷12x3
        pay_early_loan = annual_savings / (1+annual_rate_commercial * 3 / 12) * 1
        
        print('提前还款额', pay_early_loan, ' 违约金', annual_savings - pay_early_loan)
    else:
        pay_early_loan = annual_savings
        print('提前还款额', pay_early_loan)
    if pay_early_loan < remaining_principal:
        new_total_monthly_payment, saved_interest = early_repayment_total_updated_v4(
            loan_public, annual_rate_public, loan_commercial, annual_rate_commercial, 
            months_to_repay, pay_early_loan, remaining_principal)
        print('提前还款后月供', new_total_monthly_payment, ' 提前还款节省的利息支出', saved_interest)
        mortgate_monthly = new_total_monthly_payment
        remaining_principal -= pay_early_loan
        remaining_interest -= saved_interest
        monthly_principals_commercial = equal_interest_monthly_principal(remaining_principal, annual_rate_commercial / 12, 30 * 12 - months_to_repay)
        monthly_interest_commercial = equal_interest_monthly_interest(remaining_principal, annual_rate_commercial / 12, 30 * 12 - months_to_repay)
        remaining_principal -= sum(monthly_principals_commercial[:12])
        remaining_interest -= sum(monthly_interest_commercial[:12])
        months_to_repay += 12
    else:
        print('最后剩余本金',remaining_principal)
        break


# 接口设计
# 每次提前还款之后可以得到一个新的月供额。
# 节省的利息， 每次支付之后可以算出来一个值。这个节省的结果是针对上一次而言的。
    # 这样需要计算上一次状态下的总利息支出
# 这样需要保存一个内部状态