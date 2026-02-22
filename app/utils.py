from .models import SynthesisReport, VerdictStatus

def generate_markdown(report: SynthesisReport) -> str:
    """
    Converts the SynthesisReport into a high-scannability Markdown string.
    """
    md_output = f"# {report.header}\n\n"
    
    # Article Cards
    md_output += "## Key Publications\n\n"
    for idx, article in enumerate(report.articles, 1):
        md_output += f"### {idx}. {article.title}\n"
        md_output += f"**Source:** {article.journal} ({article.date}) | **Authors:** {article.authors}\n\n"
        md_output += f"**The Why:** {article.why}\n\n"
        md_output += f"**The How:** {article.how}\n\n"
        md_output += f"**The Stats:** {article.stats}\n\n"
        if article.url:
            md_output += f"[Read Full Paper]({article.url})\n\n"
        md_output += "---\n\n"

    # Resident's Verdict Table
    md_output += "## The Resident's Verdict\n\n"
    md_output += "| Topic | What's In | What's Out/Evolving |\n"
    md_output += "| :--- | :--- | :--- |\n"
    
    for verdict in report.verdicts:
        topic_cell = verdict.topic
        in_cell = ""
        out_cell = ""
        
        if verdict.verdict == VerdictStatus.IN:
            in_cell = "✅ **YES**<br>" + (verdict.reasoning or "")
        elif verdict.verdict == VerdictStatus.OUT:
            out_cell = "❌ **NO**<br>" + (verdict.reasoning or "")
        else:
            out_cell = "⚠️ **WATCH**<br>" + (verdict.reasoning or "")

        md_output += f"| {topic_cell} | {in_cell} | {out_cell} |\n"
    
    return md_output
