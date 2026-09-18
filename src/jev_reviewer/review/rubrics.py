from __future__ import annotations


def _scale(low: str, mid: str, high: str) -> dict[str, str]:
    return {
        "1": low,
        "2": "Between 1 and 3. Important weaknesses are present.",
        "3": mid,
        "4": "Between 3 and 5. Strong overall with only limited weaknesses.",
        "5": high,
    }


PAPER_RUBRIC: dict[str, tuple[str, dict[str, str]]] = {
    "research_question": (
        "How clear, specific, and scientifically answerable is the main research question or objective?",
        _scale("Unclear or not answerable as stated.", "Generally clear but has material ambiguity.", "Highly specific, answerable, and well aligned with the study."),
    ),
    "design_alignment": (
        "How well does the study design answer the stated research question? Judge design-question alignment, not writing quality.",
        _scale("Major mismatch between design and question.", "Broadly aligned with notable limitations.", "Design directly and rigorously addresses the question."),
    ),
    "methods_rigor": (
        "How rigorous and reproducible are the methods as described?",
        _scale("Critical methodological weaknesses or insufficient detail.", "Adequate core methods with important weaknesses or missing details.", "Rigorous, reproducible, and well justified."),
    ),
    "statistics": (
        "How appropriate and sufficiently justified are the statistical or computational analyses for the data and outcomes?",
        _scale("Major analytic mismatch or invalid approach.", "Mostly appropriate but with meaningful concerns.", "Strongly aligned, justified, and appropriately interpreted."),
    ),
    "results_support": (
        "How well do the presented results support the manuscript's principal conclusions?",
        _scale("Conclusions substantially exceed the evidence.", "Most conclusions are supported but some overreach remains.", "Principal conclusions closely match the evidence and uncertainty."),
    ),
    "novelty": (
        "How much substantive scientific or methodological novelty is demonstrated in the document itself? Do not reward novelty claims without evidence.",
        _scale("Little or no demonstrated novelty.", "Incremental but potentially useful contribution.", "Clearly demonstrated and consequential novelty."),
    ),
    "limitations": (
        "How adequately does the manuscript recognize limitations that materially affect interpretation?",
        _scale("Major limitations are ignored or minimized.", "Important limitations are discussed but incompletely.", "Material limitations are explicit and appropriately integrated into interpretation."),
    ),
}


PROPOSAL_RUBRIC: dict[str, tuple[str, dict[str, str]]] = {
    "significance": (
        "How strongly does the proposal establish an important problem and a consequential knowledge or practice gap?",
        _scale("Importance or gap is weakly established.", "Important problem but gap or impact case needs strengthening.", "Compelling importance, gap, and potential impact."),
    ),
    "innovation": (
        "How well does the proposal demonstrate substantive innovation rather than simply labeling the work innovative?",
        _scale("Innovation is minimal, unclear, or unsupported.", "Some meaningful innovation, but partly incremental or underdeveloped.", "Clear and consequential conceptual, methodological, or translational innovation."),
    ),
    "aim_coherence": (
        "How coherent are the Specific Aims as a set? Consider logical progression, independence, and whether failure of one aim endangers later aims.",
        _scale("Aims are poorly aligned or dangerously interdependent.", "Overall coherent with notable dependencies or gaps.", "Aims are tightly aligned, logically structured, and resilient to partial failure."),
    ),
    "aim_method_alignment": (
        "How well do the proposed methods directly answer each stated aim and hypothesis?",
        _scale("Major aim-method mismatch.", "Generally aligned but important gaps remain.", "Methods directly and convincingly address the aims."),
    ),
    "feasibility": (
        "How feasible is the proposed work given recruitment/data access, team, timeline, preliminary support, and technical complexity?",
        _scale("Major feasibility threats are unresolved.", "Feasible in principle but with meaningful execution risk.", "Strong evidence that the work can be completed as proposed."),
    ),
    "analysis_plan": (
        "How rigorous and adequately specified is the quantitative, qualitative, or computational analysis plan?",
        _scale("Major analytic weaknesses or insufficient specification.", "Generally reasonable with important missing justification.", "Rigorous, appropriately justified, and operationally specific."),
    ),
    "risk_mitigation": (
        "How well does the proposal anticipate major failure modes and provide credible alternatives?",
        _scale("Important risks are ignored and alternatives are weak.", "Several risks are addressed but key contingencies remain vague.", "Major risks are anticipated with specific and credible alternatives."),
    ),
    "expected_impact": (
        "If the project succeeds as written, how strongly would it advance knowledge, methods, or practice? Judge the proposed work, not promotional language.",
        _scale("Likely limited impact.", "Useful contribution with moderate impact.", "Potentially substantial and well-supported impact."),
    ),
}


INTEGRITY_RUBRIC: dict[str, tuple[str, dict[str, str]]] = {
    "formulaic_rhetoric": (
        "How strong is the burden of formulaic AI-associated rhetorical patterns in this text, such as repetitive contrastive framing, generic signposting, symmetrical phrasing, or repeated stock transitions? This is not an authorship determination.",
        {"low": "Little evidence of formulaic pattern clustering.", "moderate": "Some clustered formulaic patterns that merit editing.", "high": "Dense or repeated formulaic patterns that materially affect natural scientific writing."},
    ),
    "generic_claims": (
        "How strong is the burden of generic, vague, or promotional scientific claims that should be replaced with concrete claims, evidence, quantities, mechanisms, or decisions?",
        {"low": "Mostly concrete and specific.", "moderate": "Several vague or generic passages.", "high": "Frequent vague, promotional, or low-information claims."},
    ),
    "over_symmetry": (
        "How strong is the burden of overly balanced, repetitive, or mechanically parallel sentence and paragraph structures?",
        {"low": "Natural structural variation.", "moderate": "Noticeable repeated structures.", "high": "Strong mechanical symmetry or repeated templates."},
    ),
    "scientific_stance": (
        "How weak is the document's scientific or epistemic stance? Consider whether uncertainty, evidence strength, interpretation, and limitations are stated specifically rather than generically.",
        {"low": "Scientific stance is specific and appropriately calibrated.", "moderate": "Some weak or generic stance language.", "high": "Frequent weak, vague, or poorly calibrated scientific stance."},
    ),
    "clarity_burden": (
        "How strong is the burden of unnecessary complexity that reduces clear scientific English, including long overloaded sentences, nominalization, or abstract wording?",
        {"low": "Mostly direct and clear.", "moderate": "Several passages need simplification.", "high": "Complexity materially harms readability."},
    ),
}


def build_choice_questions(rubric: dict[str, tuple[str, dict[str, str]]]) -> dict[str, dict]:
    return {
        key: {"type": "choice", "instructions": instruction, "criteria": criteria}
        for key, (instruction, criteria) in rubric.items()
    }
