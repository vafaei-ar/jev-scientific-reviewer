from jev_reviewer.review.integrity import style_signals


def test_style_signals_detects_formulaic_patterns():
    text = (
        "This is not just a technical problem, but a major scientific challenge. "
        "In recent years, this topic has garnered increasing attention. "
        "This finding underscores the importance of careful evaluation."
    )
    out = style_signals(text)
    assert out["pattern_counts"]["contrastive_negation"] >= 1
    assert out["pattern_counts"]["generic_gap"] >= 1
    assert out["pattern_counts"]["generic_significance"] >= 1
