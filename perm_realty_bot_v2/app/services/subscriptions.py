from app.config import settings

def get_plan(role: str, plan_code: str):
    role = "buyer" if role == "buyer" else "agent"
    return settings.plans[role][plan_code]
