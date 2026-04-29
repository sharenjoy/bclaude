import google.generativeai as genai
import os
import json

# Setup API Key
# Assuming user has GOOGLE_API_KEY env var set, or we can prompt/configure.
# For now, let's assume it's set or rely on default credentials if available.
if "GOOGLE_API_KEY" not in os.environ:
    # Placeholder warning or default to empty
    pass

def generate_strategic_insight(brand_name, dept_name, card_data, api_key=None, reference_context=""):
    """
    Generate a strategic insight for a specific department issue using LLM.
    
    Args:
        brand_name (str): Name of the brand/product.
        dept_name (str): Department name (e.g. Supply Chain).
        card_data (dict): Dictionary containing 'issue', 'factors', 'examples', 'status'.
        api_key (str): Google API Key for Gemini.
        reference_context (str): Content of methodology documents to guide AI thinking.
        
    Returns:
        dict: {
            'analysis': 'Deep analysis text...',
            'action': 'Strategic action text...'
        }
    """
    
    # 1. Configure API if key provided
    if api_key:
        genai.configure(api_key=api_key)
    elif "GOOGLE_API_KEY" in os.environ:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    else:
        # Halt if no key found anywhere
        return {
            "analysis": "⚠️ API Key Missing",
            "action": "Please configure GOOGLE_API_KEY or provide input key."
        }

    # 2. Construct Prompt (Enhanced with References)
    prompt = f"""
    Role: Chief Strategy Officer (CSO) for {brand_name}.
    Task: Analyze the following market feedback issue for the "{dept_name}" department.
    
    [Methodology & Thinking Framework]
    You MUST apply the following analytical principles in your reasoning:
    {reference_context[:2000]}... (truncated for efficiency)
    
    [Issue Context]
    - Issue: {card_data.get('issue')}
    - Severity: {card_data.get('status')}
    - Key Factors: {', '.join([str(f) for f in card_data.get('factors', [])])}
    - Consumer Voice (Evidence):
      {chr(10).join(['- ' + str(e) for e in card_data.get('examples', [])])}
      
    [Requirements]
    1. Analysis: Apply the methodology to explain the root cause and potential business impact (max 60 words).
    2. Action: Propose ONE specific, high-level strategic action. Avoid generic advice. (max 40 words).
    
    [Output Format]
    Return ONLY a valid JSON object:
    {{
        "analysis": "...",
        "action": "..."
    }}
    """
    
    try:
        # Reverting to gemini-pro (stable) as 1.5-flash caused 404 in this env
        model = genai.GenerativeModel('gemini-pro')
        
        # Set generation config for JSON
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json"
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        text = response.text
        
        # Parse JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        return json.loads(text)
        
    except Exception as e:
        # Return error object instead of simulation
        return {
            "analysis": f"❌ Analysis Failed: {str(e)}",
            "action": "Check API Key or Model Service Status."
        }

