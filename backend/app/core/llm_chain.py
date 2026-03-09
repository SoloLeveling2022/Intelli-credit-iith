import os
from app.config import get_settings


async def generate_text(prompt: str, system_prompt: str = "") -> str:
    settings = get_settings()
    providers = settings.llm_priority.split(",")
    errors: list[str] = []

    for provider in providers:
        provider = provider.strip()
        try:
            if provider == "openai":
                if not settings.openai_api_key:
                    errors.append(f"openai: no API key configured")
                    continue
                print(f"Trying LLM provider: openai")
                return await _call_openai(prompt, system_prompt, settings.openai_api_key)
            elif provider == "gemini":
                if not settings.gemini_api_key or settings.gemini_api_key.startswith("your-"):
                    errors.append(f"gemini: no valid API key configured")
                    continue
                print(f"Trying LLM provider: gemini")
                return await _call_gemini(prompt, system_prompt, settings.gemini_api_key)
            elif provider == "ollama":
                if not settings.ollama_url:
                    errors.append(f"ollama: no URL configured")
                    continue
                print(f"Trying LLM provider: ollama")
                return await _call_ollama(prompt, system_prompt, settings.ollama_url)
        except Exception as e:
            errors.append(f"{provider}: {e}")
            print(f"LLM provider {provider} failed: {e}")
            continue

    error_detail = "; ".join(errors) if errors else "no providers configured"
    return f"Unable to generate explanation — all LLM providers failed. ({error_detail})"


async def _call_openai(prompt: str, system_prompt: str, api_key: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content


async def _call_gemini(prompt: str, system_prompt: str, api_key: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    response = model.generate_content(full_prompt)
    return response.text


async def _call_ollama(prompt: str, system_prompt: str, ollama_url: str) -> str:
    import httpx

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{ollama_url}/api/chat",
            json={"model": "qwen2.5-coder:32b", "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


AUDIT_SYSTEM_PROMPT = """You are an expert Corporate Credit Analyst specializing in lending to Indian businesses.
You analyze credit risk indicators in clear, professional language suitable for credit officers and senior management.
Always reference specific company details, financial metrics, and amounts.
Explain why each risk indicator matters for credit decision-making and loan recovery.
Recommend specific risk mitigation measures and credit terms.
Format your response with sections: Summary, Impact on Creditworthiness, Root Cause Analysis, Recommended Action."""


async def generate_cam_explanation(risk_indicator: dict) -> str:
    """Generate Credit Appraisal Memo explanation for a risk indicator"""
    prompt = f"""Analyze this credit risk indicator and provide a detailed assessment:

Risk Indicator: {risk_indicator.get('indicator_type')}
Severity: {risk_indicator.get('severity')}
Company ID: {risk_indicator.get('company_id')}
Document Reference: {risk_indicator.get('document_id', 'N/A')}
Field: {risk_indicator.get('field_name', 'N/A')}
Expected Value: {risk_indicator.get('expected_value', 'N/A')}
Actual Value: {risk_indicator.get('actual_value', 'N/A')}
Amount Impact: INR {risk_indicator.get('amount_impact', 0)}
Description: {risk_indicator.get('description', '')}

Provide a comprehensive credit analysis with risk mitigation recommendations."""

    return await generate_text(prompt, AUDIT_SYSTEM_PROMPT)

# Keep old function for backward compatibility
async def generate_audit_explanation(mismatch: dict) -> str:
    return await generate_cam_explanation(mismatch)


RISK_SYSTEM_PROMPT = """You are a Corporate Credit Risk Analyst for a commercial bank.
Analyze company credit risk factors and provide a concise credit risk assessment.
Reference specific financial metrics, ratios, and explain what each risk indicator means for lending decisions.
Consider the Five C's of Credit: Character, Capacity, Capital, Collateral, Conditions.
Format: Credit Risk Summary, Key Concerns, Lending Recommendation (with suggested terms)."""


async def generate_credit_risk_summary(company: dict) -> str:
    """Generate credit risk summary for a company"""
    prompt = f"""Assess the credit risk for this corporate borrower:

Company ID: {company.get('company_id')}
Legal Name: {company.get('legal_name')}
Credit Risk Score: {company.get('risk_score')}/100
Credit Grade: {company.get('credit_grade')}
Recommended Loan Amount: INR {company.get('loan_amount_recommended', 0):,.2f}
Recommended Interest Rate: {company.get('interest_rate_recommended', 0):.2f}%
Five C's Scores:
  - Character: {company.get('five_cs', {}).get('character_score', 0):.1f}/100
  - Capacity: {company.get('five_cs', {}).get('capacity_score', 0):.1f}/100
  - Capital: {company.get('five_cs', {}).get('capital_score', 0):.1f}/100
  - Collateral: {company.get('five_cs', {}).get('collateral_score', 0):.1f}/100
  - Conditions: {company.get('five_cs', {}).get('conditions_score', 0):.1f}/100
Risk Factors: {', '.join(company.get('risk_factors', []))}
Mitigation Measures: {', '.join(company.get('mitigation_measures', []))}

Provide a comprehensive credit risk assessment with lending recommendations."""

    return await generate_text(prompt, RISK_SYSTEM_PROMPT)

# Keep old function for backward compatibility
async def generate_risk_summary(vendor: dict) -> str:
    return await generate_credit_risk_summary(vendor)
