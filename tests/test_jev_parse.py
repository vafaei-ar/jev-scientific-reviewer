from jev_reviewer.providers.jev import JevClient


def test_parse_nested_answers():
    body = {
        "answers": {
            "rigor": {
                "choice": "4",
                "probabilities": {"1": 0.01, "2": 0.04, "3": 0.20, "4": 0.60, "5": 0.15},
                "confidence": 0.78,
            }
        }
    }
    parsed = JevClient._parse(body)
    assert parsed["rigor"].choice == "4"
    assert parsed["rigor"].probabilities["4"] == 0.60
    assert parsed["rigor"].confidence == 0.78


def test_parse_current_flat_reply():
    body = {
        "rigor": "4",
        "novelty": "3",
        "confidence": {"rigor": 0.78, "novelty": 0.61},
        "probabilities": {
            "rigor": {"1": 0.01, "2": 0.04, "3": 0.20, "4": 0.60, "5": 0.15},
            "novelty": {"1": 0.02, "2": 0.18, "3": 0.55, "4": 0.20, "5": 0.05},
        },
        "usage": {"input_tokens": 500, "output_tokens": 0},
        "model": "jev-latest",
    }
    parsed = JevClient._parse(body)
    assert parsed["rigor"].choice == "4"
    assert parsed["novelty"].choice == "3"
    assert parsed["rigor"].confidence == 0.78
    assert parsed["novelty"].probabilities["3"] == 0.55
