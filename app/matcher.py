import re
from email.utils import parseaddr

# Words that appear in lots of organization names and say nothing about
# WHICH organization it is. Matching on "foundation" would hit everything.
STOPWORDS = {
    "the", "of", "for", "and", "inc", "foundation", "scholarship",
    "scholarships", "fund", "association", "society", "national",
}

AWARD_KEYWORDS = [
    "congratulations", "pleased to award", "pleased to inform you",
    "you have been selected", "you've been selected", "has been awarded",
]
REJECT_KEYWORDS = [
    "regret to inform", "unable to offer", "not selected", "unfortunately",
    "were not chosen", "other candidates", "not been selected",
]

MIN_MATCH_SCORE = 3  # below this, we say "no match" instead of guessing


def normalize(text):
    """Lowercase and strip punctuation so comparisons are forgiving."""
    return re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())


def significant_words(name):
    """The distinctive words in a name, e.g. 'Gates Foundation' -> ['gates']."""
    return [w for w in normalize(name).split() if w not in STOPWORDS and len(w) >= 4]


def sender_domain_text(sender):
    """'Jo <jo@mail.gatesfoundation.org>' -> 'mailgatesfoundation'."""
    address = parseaddr(sender or "")[1].lower()
    if "@" not in address:
        return ""
    domain = address.split("@", 1)[1]
    domain = domain.rsplit(".", 1)[0]  # drop the .org / .com part
    return domain.replace(".", "").replace("-", "")


def score_scholarship(scholarship, sender, subject, body):
    """Return (score, reasons) for how well one email fits one scholarship."""
    score = 0
    reasons = []

    domain = sender_domain_text(sender)
    if any(word in domain for word in significant_words(scholarship.organization)):
        score += 3
        reasons.append("sender domain matches organization")

    subject_n, body_n = normalize(subject), normalize(body)
    name_n = normalize(scholarship.name).strip()
    org_n = normalize(scholarship.organization).strip()

    if name_n and name_n in subject_n:
        score += 4
        reasons.append("scholarship name in subject")
    elif name_n and name_n in body_n:
        score += 2
        reasons.append("scholarship name in body")

    if org_n and (org_n in subject_n or org_n in body_n):
        score += 2
        reasons.append("organization name in text")

    return score, reasons


def guess_outcome(subject, body):
    """Naive keyword vote: 'awarded', 'rejected', or 'unknown'."""
    text = normalize(f"{subject} {body}")
    award_hits = sum(1 for k in AWARD_KEYWORDS if normalize(k) in text)
    reject_hits = sum(1 for k in REJECT_KEYWORDS if normalize(k) in text)

    if award_hits > reject_hits:
        return "awarded"
    if reject_hits > award_hits:
        return "rejected"
    return "unknown"  # a tie or no signal: leave it for a human


def match_email(scholarships, sender, subject, body):
    """Find the best-fitting scholarship for an email, or None."""
    best, best_score, best_reasons = None, 0, []

    for s in scholarships:
        score, reasons = score_scholarship(s, sender, subject, body)
        if score > best_score:
            best, best_score, best_reasons = s, score, reasons

    if best is None or best_score < MIN_MATCH_SCORE:
        return {"scholarship": None, "score": best_score, "reasons": [], "outcome": "unknown"}

    return {
        "scholarship": best,
        "score": best_score,
        "reasons": best_reasons,
        "outcome": guess_outcome(subject, body),
    }