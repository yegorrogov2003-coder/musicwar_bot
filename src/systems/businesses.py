# [SRC-SYSTEMS-BUSINESS] Логика бизнесов: покупка, прокачка, расчет дохода.
# Не трогает банды или донат.
from ..config import BUSINESSES

def get_business_info(biz_id):
    for biz in BUSINESSES:
        if biz["id"] == biz_id:
            return biz
    return None

def calculate_income(user_businesses):
    # Пример простой логики: сумма доходов от всех бизнесов
    total = 0
    for biz_id, level in user_businesses.items():
        info = get_business_info(biz_id)
        if info:
            # Доход растет с уровнем
            total += info["base_income"] * level
    return total
  
