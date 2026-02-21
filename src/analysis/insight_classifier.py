def analyze_statement(statement_text):
    """
    Evaluates transcript segments to distinguish between surface Needs and deeper Insights.
    This logic forms the basis for the Gap Analysis requested in Study 1.
    """
    
    # Theoretical Definitions grounded in the Knowledge Base:
    definitions = {
        "need": "Explicit statements of what users want or require. Users often articulate them directly and represent surface-level desires or requirements. Focuses on 'what' users want.", # [cite: 1166, 1167, 1176]
        "insight": "Deeper understandings that explain the motivations behind behaviors or needs. They reveal hidden truths and underlying reasons. Focuses on 'why' users behave or feel a certain way." # [cite: 1169, 1170, 1176]
    }
    
    prompt = f"""
    Analyze the following patient statement based on these strict definitions:
    Need: {definitions['need']}
    Insight: {definitions['insight']}
    
    Statement: "{statement_text}"
    
    Task: Classify as 'Need' or 'Insight' and explain the latent variables (e.g., power dynamics, identity, structural barriers) present.
    """
    
    # Note: Pass this prompt to the Perplexity Agent API or Claude for synthesis.
    print("Classification prompt generated for AI analysis pipeline.")
    return prompt

if __name__ == "__main__":
    sample_text = "I need a more flexible appointment schedule because I cannot afford to lose my part-time barista job if the bus is late."
    print(analyze_statement(sample_text))