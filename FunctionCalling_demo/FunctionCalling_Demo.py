import re
import json
from tax_calculator import calculate_individual_income_tax_from_salary

from openai import OpenAI

# Qwen API Key & Endpoint
# 在这里修改你的API key（重要的事情说三遍）
# 在这里修改你的API key（重要的事情说三遍）
# 在这里修改你的API key（重要的事情说三遍）
client = OpenAI(
    api_key="sk-ac968b8245624f3eb154bda6b13c2601",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

function_definitions = [
    {
        "name": "calculate_individual_income_tax_from_salary",
        "description": "Calculate individual income tax in Mainland China based on monthly gross salary.",
        "parameters": {
            "type": "object",
            "properties": {
                "gross_salary": {"type": "number", "description": "Monthly gross salary (RMB)"},
                "social_insurance": {"type": "number", "description": "Monthly social insurance (RMB)", "default": 0},
                "special_deduction": {"type": "number", "description": "Monthly special additional deduction (RMB)", "default": 0},
                "period": {"type": "string", "enum": ["monthly", "yearly"], "description": "Result period"}
            },
            "required": ["gross_salary", "period"]
        }
    }
]

def extract_salary_info(user_input):
    """
    提取中英文输入中的工资、五险一金、专项附加扣除
    """
    text = user_input.lower().replace('，', ',').replace('。', '.').replace('：', ':')
    text = text.replace('元', '').replace('块', '').replace('rmb', '').replace('cny', '').replace('￥', '').replace('dollars', '')

    # 工资/收入
    salary_patterns = [
        r"(工资|月薪|收入|salary|monthly salary|income)[^\d\-]*([\d,\.]+)",
        r"([\d,\.]+)[^\d]*(工资|月薪|收入|salary|monthly salary|income)"
    ]
    gross_salary = None
    for pat in salary_patterns:
        m = re.search(pat, text)
        if m:
            # 取第一个为数字的分组
            for group in m.groups():
                try:
                    gross_salary = float(group.replace(',', '').strip())
                    break
                except:
                    continue
        if gross_salary is not None:
            break
    # 兜底提取（直接找第一个数字作为工资）
    if gross_salary is None:
        m = re.search(r"([\d,\.]+)", text)
        if m:
            gross_salary = float(m.group(1).replace(',', '').strip())

    # 五险一金/社保
    si_patterns = [
        r"(五险一金|社保|公积金|social insurance|insurances)[^\d\-]*([\d,\.]+)",
        r"([\d,\.]+)[^\d]*(五险一金|社保|公积金|social insurance|insurances)"
    ]
    social_insurance = None
    for pat in si_patterns:
        m = re.search(pat, text)
        if m:
            for group in m.groups():
                try:
                    social_insurance = float(group.replace(',', '').strip())
                    break
                except:
                    continue
        if social_insurance is not None:
            break
    if social_insurance is None:
        social_insurance = 0

    # 专项扣除
    sd_patterns = [
        r"(专项附加扣除|专项扣除|special deduction|additional deduction)[^\d\-]*([\d,\.]+)",
        r"([\d,\.]+)[^\d]*(专项附加扣除|专项扣除|special deduction|additional deduction)"
    ]
    special_deduction = None
    for pat in sd_patterns:
        m = re.search(pat, text)
        if m:
            for group in m.groups():
                try:
                    special_deduction = float(group.replace(',', '').strip())
                    break
                except:
                    continue
        if special_deduction is not None:
            break
    if special_deduction is None:
        special_deduction = 0

    return gross_salary, social_insurance, special_deduction

def main():
    print("欢迎使用Qwen工资个税function calling助手！")
    print("请输入您的工资、五险一金、专项附加扣除，例如：")
    print("  - 我工资12000元，五险一金2000，专项附加扣除1000")
    print("  - My salary is 15000, social insurance is 2000, special deduction is 1000")
    print("按Ctrl+C退出。")

    while True:
        try:
            user_input = input("\n>>> ")
            gross_salary, social_insurance, special_deduction = extract_salary_info(user_input)

            if gross_salary is None:
                print("未能识别您的工资金额，请重新输入。")
                continue

            print("\n[本地function_call] calculate_individual_income_tax_from_salary")
            print(f"gross_salary={gross_salary}, social_insurance={social_insurance}, special_deduction={special_deduction}")

            # 本地计算
            monthly_result = calculate_individual_income_tax_from_salary(
                gross_salary, social_insurance, special_deduction, period="monthly"
            )
            yearly_result = calculate_individual_income_tax_from_salary(
                gross_salary, social_insurance, special_deduction, period="yearly"
            )

            print(f"\n[结果]")
            print(f"月工资总额: {gross_salary} 元")
            print(f"五险一金: {social_insurance} 元/月")
            print(f"专项附加扣除: {special_deduction} 元/月")
            print(f"月纳税额: {monthly_result['tax_due']} 元")
            print(f"年纳税额: {yearly_result['tax_due']} 元")

            # Qwen function calling API（新版 openai-python）
            messages = [
                {"role": "system", "content": "你是一个中国个人所得税计算专家，请根据用户输入调用函数并返回纳税信息。"},
                {"role": "user", "content": user_input}
            ]
            try:
                completion = client.chat.completions.create(
                    model="qwen-max",
                    messages=messages,
                    functions=function_definitions,
                    function_call={
                        "name": "calculate_individual_income_tax_from_salary",
                        "arguments": json.dumps({
                            "gross_salary": gross_salary,
                            "social_insurance": social_insurance,
                            "special_deduction": special_deduction,
                            "period": "monthly"
                        })
                    }
                )
                print("\n[Qwen function calling API 返回]:")
                if completion.choices:
                    func_resp = completion.choices[0].message.function_call
                    if func_resp:
                        print("【LLM已调用function】")
                        print("调用参数:", func_resp.arguments)
                    else:
                        print(completion)
                else:
                    print(completion)
            except Exception as e:
                print("\n[Qwen function calling API 调用失败]:", e)
                print("如需关闭API调用，可注释相关代码。")

        except KeyboardInterrupt:
            print("\n感谢使用，已退出。")
            break

if __name__ == "__main__":
    main()
