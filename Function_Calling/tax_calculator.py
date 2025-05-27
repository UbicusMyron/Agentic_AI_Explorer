def calculate_individual_income_tax_from_salary(
    gross_salary: float,
    social_insurance: float = 0,
    special_deduction: float = 0,
    period: str = "monthly"
) -> dict:
    """
    计算中国大陆个人所得税（综合所得），输入为月工资总额，自动扣除起征点、五险一金、专项附加扣除。

    Args:
        gross_salary (float): 月工资总额（未扣除前）
        social_insurance (float): 月五险一金总额（默认为0）
        special_deduction (float): 月专项附加扣除总额（默认为0）
        period (str): "monthly" 或 "yearly"（输出周期，默认"monthly"）

    Returns:
        dict: {
            "tax_due": 应缴税额,
            "effective_rate": 实际税率 (%),
            "marginal_rate": 边际税率 (%),
            "period": 输出周期,
            "gross_salary": 月工资总额,
            "taxable_income": 应纳税所得额（年度）,
            "deductions": {
                "annual_threshold": 年度起征点,
                "annual_social_insurance": 年度五险一金,
                "annual_special_deduction": 年度专项附加扣除
            }
        }
    """

    # 年度累计
    months = 12
    annual_threshold = 5000 * months  # 年度起征点
    annual_gross = gross_salary * months
    annual_social_insurance = social_insurance * months
    annual_special_deduction = special_deduction * months

    # 年度应纳税所得额
    taxable_income = (
        annual_gross
        - annual_threshold
        - annual_social_insurance
        - annual_special_deduction
    )
    taxable_income = max(0, taxable_income)  # 不得为负

    # 税率表
    tax_brackets = [
        {"min": 0, "max": 36000, "rate": 0.03, "deduction": 0},
        {"min": 36000, "max": 144000, "rate": 0.10, "deduction": 2520},
        {"min": 144000, "max": 300000, "rate": 0.20, "deduction": 16920},
        {"min": 300000, "max": 420000, "rate": 0.25, "deduction": 31920},
        {"min": 420000, "max": 660000, "rate": 0.30, "deduction": 52920},
        {"min": 660000, "max": 960000, "rate": 0.35, "deduction": 85920},
        {"min": 960000, "max": float('inf'), "rate": 0.45, "deduction": 181920}
    ]

    # 查找适用税率
    bracket = None
    for b in tax_brackets:
        # 左闭右开区间
        if taxable_income >= b["min"] and taxable_income < b["max"]:
            bracket = b
            break
    # 边界情况
    if bracket is None and taxable_income >= 960000:
        bracket = tax_brackets[-1]

    # 计算税额
    annual_tax = taxable_income * bracket["rate"] - bracket["deduction"]
    annual_tax = max(0, annual_tax)

    effective_rate = (annual_tax / annual_gross * 100) if annual_gross > 0 else 0
    marginal_rate = bracket["rate"] * 100  # %

    # 根据周期返回
    if period == "yearly":
        return {
            "tax_due": round(annual_tax, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": marginal_rate,
            "period": "yearly",
            "gross_salary": gross_salary,
            "taxable_income": taxable_income,
            "deductions": {
                "annual_threshold": annual_threshold,
                "annual_social_insurance": annual_social_insurance,
                "annual_special_deduction": annual_special_deduction
            }
        }
    else:
        monthly_tax = annual_tax / months
        return {
            "tax_due": round(monthly_tax, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": marginal_rate,
            "period": "monthly",
            "gross_salary": gross_salary,
            "taxable_income": taxable_income,
            "deductions": {
                "annual_threshold": annual_threshold,
                "annual_social_insurance": annual_social_insurance,
                "annual_special_deduction": annual_special_deduction
            }
        }


# 示例：function calling风格包装
def calculate_monthly_tax_from_salary(
    gross_salary: float,
    social_insurance: float = 0,
    special_deduction: float = 0
) -> dict:
    return calculate_individual_income_tax_from_salary(
        gross_salary, social_insurance, special_deduction, period="monthly"
    )

def calculate_yearly_tax_from_salary(
    gross_salary: float,
    social_insurance: float = 0,
    special_deduction: float = 0
) -> dict:
    return calculate_individual_income_tax_from_salary(
        gross_salary, social_insurance, special_deduction, period="yearly"
    )


# 测试样例
if __name__ == "__main__":
    test_cases = [
        {"gross_salary": 5000, "social_insurance": 0, "special_deduction": 0},
        {"gross_salary": 10000, "social_insurance": 2000, "special_deduction": 1000},
        {"gross_salary": 20000, "social_insurance": 4000, "special_deduction": 1500},
        {"gross_salary": 40000, "social_insurance": 4000, "special_deduction": 2000},
    ]

    print("中国大陆工资个税计算器（输入工资总额）")
    print("=" * 50)
    for i, case in enumerate(test_cases, 1):
        result = calculate_individual_income_tax_from_salary(**case)
        print(f"\n测试用例 {i}:")
        print(f"月工资总额: ¥{case['gross_salary']:.2f}")
        print(f"月五险一金: ¥{case['social_insurance']:.2f}")
        print(f"月专项附加扣除: ¥{case['special_deduction']:.2f}")
        print(f"月应纳税额: ¥{result['taxable_income'] / 12:.2f}")
        print(f"月个税: ¥{result['tax_due']:.2f}")
        print(f"实际税率: {result['effective_rate']:.2f}%")
        print(f"边际税率: {result['marginal_rate']:.1f}%")