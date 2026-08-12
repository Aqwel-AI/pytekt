"""Built-in text datasets for NLP prototyping — no downloads required.

Provides curated samples for sentiment analysis, topic classification, and
named-entity recognition.  Every function returns a :class:`Dataset` whose
``data`` column holds raw text strings (object array) and ``target`` holds
integer class labels or, for NER, BIO-tagged sequences.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from ._base import Dataset


# ===================================================================
# Sentiment analysis (binary: positive / negative)
# ===================================================================

_SENTIMENT_DATA: List[Tuple[str, int]] = [
    # ---- positive (1) ----
    ("This product exceeded all my expectations. Absolutely brilliant!", 1),
    ("I love the clean design and intuitive interface. Five stars.", 1),
    ("The customer support team was incredibly helpful and responsive.", 1),
    ("Best purchase I've made this year. Highly recommended.", 1),
    ("A masterpiece of engineering. Works flawlessly every time.", 1),
    ("The quality is outstanding for the price. Great value.", 1),
    ("I'm genuinely impressed by the attention to detail.", 1),
    ("Smooth performance, beautiful finish, and reliable results.", 1),
    ("This has completely transformed my workflow for the better.", 1),
    ("Simple, elegant, and powerful. Exactly what I needed.", 1),
    ("Wonderful experience from start to finish. Will buy again.", 1),
    ("The team has done a fantastic job with this update.", 1),
    ("Easy setup, great documentation, and everything just works.", 1),
    ("I can't imagine going back to the old way of doing things.", 1),
    ("This is the gold standard in its category. Top notch.", 1),
    ("Delivers on every promise. Truly a game changer.", 1),
    ("The build quality is exceptional. Feels premium in every way.", 1),
    ("Fast shipping, perfect packaging, and the product is superb.", 1),
    ("My productivity has doubled since I started using this.", 1),
    ("Elegant solution to a complex problem. Beautifully executed.", 1),
    ("Incredible performance and reliability. Worth every penny.", 1),
    ("I recommend this to everyone I know. It's that good.", 1),
    ("The user experience is seamless and delightful throughout.", 1),
    ("Exceeded the benchmarks we set. Outstanding results.", 1),
    ("Everything about this product feels thoughtfully designed.", 1),
    # ---- negative (0) ----
    ("Terrible quality. Broke after two days of normal use.", 0),
    ("The worst customer service experience I've ever had.", 0),
    ("Does not work as advertised. Complete waste of money.", 0),
    ("Buggy, slow, and crashes constantly. Very disappointed.", 0),
    ("The instructions are confusing and the product is defective.", 0),
    ("Arrived damaged and the return process was a nightmare.", 0),
    ("Feels cheap and poorly constructed. Not worth the price.", 0),
    ("I regret this purchase. Nothing about it works properly.", 0),
    ("Unreliable and frustrating to use. Avoid at all costs.", 0),
    ("The update broke everything. Went from bad to worse.", 0),
    ("Overpriced for what you get. There are much better options.", 0),
    ("Support never responded to my emails. Completely ignored.", 0),
    ("Misleading product description. Not what I expected at all.", 0),
    ("Constant errors and no documentation to help troubleshoot.", 0),
    ("Falls apart easily. Clearly cut corners on manufacturing.", 0),
    ("Terrible performance. Lags even with the simplest tasks.", 0),
    ("The design is clunky and outdated. Very hard to navigate.", 0),
    ("Would give zero stars if I could. Total disappointment.", 0),
    ("Incomplete features and full of bugs. Not ready for release.", 0),
    ("I returned it immediately. Save your money and look elsewhere.", 0),
    ("The packaging was fine but the product itself is useless.", 0),
    ("Had high hopes but it completely failed to deliver.", 0),
    ("Extremely frustrating experience. Will not be buying again.", 0),
    ("It overheats and shuts down randomly. Safety concern.", 0),
    ("Absolutely the worst product in this category I've tried.", 0),
]


def load_sentiment(*, shuffle: bool = True, seed: Optional[int] = 42) -> Dataset:
    """50-sample binary sentiment analysis dataset (25 positive, 25 negative).

    Returns
    -------
    Dataset
        ``data`` is an object array of review strings.
        ``target`` is 0 (negative) or 1 (positive).
    """
    texts, labels = zip(*_SENTIMENT_DATA)
    data = np.array(texts, dtype=object)
    target = np.array(labels, dtype=np.int64)

    if shuffle:
        rng = np.random.RandomState(seed)
        idx = np.arange(len(data))
        rng.shuffle(idx)
        data, target = data[idx], target[idx]

    return Dataset(
        data=data.reshape(-1, 1),
        target=target,
        feature_names=["text"],
        target_names=["negative", "positive"],
        description="Binary sentiment analysis dataset. 50 product review samples.",
        name="sentiment",
        metadata={"n_classes": 2, "task": "sentiment_analysis"},
    )


# ===================================================================
# Topic classification (multi-class)
# ===================================================================

_TOPIC_DATA: List[Tuple[str, int]] = [
    # 0 = technology
    ("Apple announced a new MacBook Pro with the M4 Ultra processor.", 0),
    ("The latest version of Python introduces structural pattern matching.", 0),
    ("Quantum computing startups raised over $2 billion in funding this year.", 0),
    ("NVIDIA released a new GPU architecture targeting AI workloads.", 0),
    ("Open-source large language models are now competitive with proprietary ones.", 0),
    ("5G networks are expanding coverage to rural areas across the country.", 0),
    ("The cybersecurity industry faces a shortage of skilled professionals.", 0),
    ("Cloud computing revenue grew by 30 percent in the last quarter.", 0),
    ("Researchers developed a new algorithm that speeds up database queries.", 0),
    ("The browser wars continue as Firefox introduces AI-powered features.", 0),
    # 1 = sports
    ("The Lakers secured a spot in the playoffs with a decisive victory.", 1),
    ("Lionel Messi scored a hat trick in the championship final.", 1),
    ("The Olympic Committee announced new sports for the 2028 Games.", 1),
    ("Tennis rankings shifted after a surprise upset at the Grand Slam.", 1),
    ("The marathon world record was broken by two seconds in Berlin.", 1),
    ("The football team announced a major trade deal before the deadline.", 1),
    ("Swimming champion set three new national records at the trials.", 1),
    ("The baseball season opens with several rookies making their debut.", 1),
    ("Injuries plagued the team throughout the playoffs this season.", 1),
    ("The boxing match drew over a million pay-per-view purchases.", 1),
    # 2 = science
    ("Astronomers discovered a potentially habitable exoplanet 40 light years away.", 2),
    ("CRISPR gene editing shows promise in treating sickle cell disease.", 2),
    ("The James Webb Space Telescope captured stunning images of distant galaxies.", 2),
    ("A new study links gut microbiome diversity to mental health outcomes.", 2),
    ("Physicists confirmed the existence of a new subatomic particle.", 2),
    ("Climate models predict accelerated ice sheet melting over the next decade.", 2),
    ("Marine biologists discovered three new species in deep-sea trenches.", 2),
    ("A breakthrough in nuclear fusion achieved net energy gain.", 2),
    ("Paleontologists unearthed a remarkably preserved dinosaur fossil.", 2),
    ("New materials research led to more efficient solar panel designs.", 2),
    # 3 = business
    ("The Federal Reserve raised interest rates by a quarter point.", 3),
    ("Startup valuations declined as venture capital funding tightened.", 3),
    ("The merger between the two tech giants was approved by regulators.", 3),
    ("Retail sales exceeded expectations during the holiday shopping season.", 3),
    ("Supply chain disruptions continue to impact global manufacturing.", 3),
    ("The stock market reached an all-time high driven by tech earnings.", 3),
    ("A major airline filed for bankruptcy amid rising fuel costs.", 3),
    ("Remote work policies are reshaping commercial real estate markets.", 3),
    ("Consumer confidence index dropped to its lowest point in two years.", 3),
    ("The cryptocurrency market experienced significant volatility this week.", 3),
    # 4 = health
    ("A new vaccine showed 95 percent efficacy in clinical trials.", 4),
    ("Studies suggest that regular exercise reduces risk of dementia.", 4),
    ("The WHO declared the end of the global health emergency.", 4),
    ("Mental health awareness campaigns led to increased funding.", 4),
    ("Telemedicine adoption doubled since the start of the pandemic.", 4),
    ("Researchers found a link between sleep quality and heart disease.", 4),
    ("A new treatment for antibiotic-resistant infections was approved.", 4),
    ("Childhood obesity rates continue to rise in developed nations.", 4),
    ("Advances in prosthetics now allow mind-controlled artificial limbs.", 4),
    ("The hospital implemented an AI system to predict patient outcomes.", 4),
]


def load_topics(*, shuffle: bool = True, seed: Optional[int] = 42) -> Dataset:
    """50-sample topic classification dataset (5 classes, 10 samples each).

    Categories: technology, sports, science, business, health.
    """
    texts, labels = zip(*_TOPIC_DATA)
    data = np.array(texts, dtype=object)
    target = np.array(labels, dtype=np.int64)

    if shuffle:
        rng = np.random.RandomState(seed)
        idx = np.arange(len(data))
        rng.shuffle(idx)
        data, target = data[idx], target[idx]

    return Dataset(
        data=data.reshape(-1, 1),
        target=target,
        feature_names=["text"],
        target_names=["technology", "sports", "science", "business", "health"],
        description="Topic classification dataset. 50 news-like samples across 5 categories.",
        name="topics",
        metadata={"n_classes": 5, "task": "text_classification"},
    )


# ===================================================================
# Named Entity Recognition (NER) — BIO tagging
# ===================================================================

_NER_SAMPLES: List[Dict] = [
    {"tokens": ["Barack", "Obama", "was", "born", "in", "Honolulu", ",", "Hawaii", "."],
     "tags":   ["B-PER", "I-PER", "O",   "O",    "O",  "B-LOC",    "O", "B-LOC",  "O"]},
    {"tokens": ["Google", "was", "founded", "by", "Larry", "Page", "and", "Sergey", "Brin", "."],
     "tags":   ["B-ORG", "O",   "O",       "O",  "B-PER", "I-PER","O",   "B-PER",  "I-PER","O"]},
    {"tokens": ["The", "Eiffel", "Tower", "is", "located", "in", "Paris", ",", "France", "."],
     "tags":   ["O",   "B-LOC",  "I-LOC", "O",  "O",       "O",  "B-LOC","O", "B-LOC",  "O"]},
    {"tokens": ["Apple", "Inc", ".", "released", "the", "iPhone", "in", "January", "2007", "."],
     "tags":   ["B-ORG","I-ORG","I-ORG","O",     "O",   "B-MISC","O",  "B-DATE", "I-DATE","O"]},
    {"tokens": ["Microsoft", "CEO", "Satya", "Nadella", "spoke", "at", "the", "conference", "."],
     "tags":   ["B-ORG",    "O",   "B-PER", "I-PER",   "O",     "O",  "O",   "O",          "O"]},
    {"tokens": ["The", "United", "Nations", "headquarters", "is", "in", "New", "York", "City", "."],
     "tags":   ["O",   "B-ORG",  "I-ORG",  "O",            "O",  "O",  "B-LOC","I-LOC","I-LOC","O"]},
    {"tokens": ["Amazon", "reported", "record", "revenue", "of", "$", "386", "billion", "in", "2020", "."],
     "tags":   ["B-ORG", "O",        "O",      "O",       "O",  "O", "O",   "O",       "O",  "B-DATE","O"]},
    {"tokens": ["Dr", ".", "Jane", "Smith", "works", "at", "Stanford", "University", "."],
     "tags":   ["O",  "O", "B-PER","I-PER", "O",     "O",  "B-ORG",   "I-ORG",      "O"]},
    {"tokens": ["Tesla", "will", "open", "a", "factory", "in", "Berlin", ",", "Germany", "."],
     "tags":   ["B-ORG","O",    "O",    "O", "O",       "O",  "B-LOC", "O", "B-LOC",   "O"]},
    {"tokens": ["The", "World", "Health", "Organization", "declared", "a", "pandemic", "in", "March", "2020", "."],
     "tags":   ["O",   "B-ORG","I-ORG",  "I-ORG",        "O",        "O", "O",        "O",  "B-DATE","I-DATE","O"]},
    {"tokens": ["Elon", "Musk", "founded", "SpaceX", "in", "2002", "."],
     "tags":   ["B-PER","I-PER","O",       "B-ORG",  "O",  "B-DATE","O"]},
    {"tokens": ["The", "European", "Union", "approved", "new", "regulations", "on", "AI", "."],
     "tags":   ["O",   "B-ORG",    "I-ORG", "O",        "O",   "O",           "O",  "O",  "O"]},
    {"tokens": ["Marie", "Curie", "was", "born", "in", "Warsaw", ",", "Poland", "."],
     "tags":   ["B-PER","I-PER", "O",   "O",    "O",  "B-LOC", "O", "B-LOC",  "O"]},
    {"tokens": ["IBM", "partnered", "with", "NASA", "to", "build", "a", "weather", "model", "."],
     "tags":   ["B-ORG","O",        "O",    "B-ORG","O",  "O",    "O", "O",       "O",     "O"]},
    {"tokens": ["Tokyo", "hosted", "the", "2021", "Summer", "Olympics", "."],
     "tags":   ["B-LOC","O",      "O",   "B-DATE","B-MISC","I-MISC",  "O"]},
    {"tokens": ["Mark", "Zuckerberg", "announced", "Meta", "Platforms", "in", "October", "2021", "."],
     "tags":   ["B-PER","I-PER",      "O",         "B-ORG","I-ORG",    "O",  "B-DATE",  "I-DATE","O"]},
    {"tokens": ["The", "Nile", "River", "flows", "through", "Egypt", "and", "Sudan", "."],
     "tags":   ["O",   "B-LOC","I-LOC", "O",     "O",       "B-LOC","O",   "B-LOC", "O"]},
    {"tokens": ["Oxford", "University", "was", "founded", "in", "1096", "."],
     "tags":   ["B-ORG", "I-ORG",      "O",   "O",       "O",  "B-DATE","O"]},
    {"tokens": ["Jeff", "Bezos", "stepped", "down", "as", "CEO", "of", "Amazon", "."],
     "tags":   ["B-PER","I-PER","O",       "O",    "O",  "O",   "O",  "B-ORG", "O"]},
    {"tokens": ["The", "Great", "Wall", "of", "China", "stretches", "over", "13000", "miles", "."],
     "tags":   ["O",   "B-LOC","I-LOC","I-LOC","I-LOC","O",         "O",    "O",     "O",    "O"]},
]


def load_ner(*, shuffle: bool = True, seed: Optional[int] = 42) -> Dataset:
    """20-sample Named Entity Recognition dataset with BIO tags.

    Entity types: ``PER`` (person), ``ORG`` (organization), ``LOC``
    (location), ``DATE``, ``MISC``.

    Returns
    -------
    Dataset
        ``data`` is an object array of token lists.
        ``target`` is an object array of corresponding BIO-tag lists.
        ``metadata["tag_set"]`` lists all unique tags.
    """
    rng = np.random.RandomState(seed)
    samples = list(_NER_SAMPLES)
    if shuffle:
        rng.shuffle(samples)

    data = np.array([s["tokens"] for s in samples], dtype=object)
    target = np.array([s["tags"] for s in samples], dtype=object)

    all_tags = sorted({t for s in samples for t in s["tags"]})

    return Dataset(
        data=data.reshape(-1, 1),
        target=target,
        feature_names=["tokens"],
        target_names=all_tags,
        description="Named entity recognition dataset. 20 samples with BIO-tagged entities (PER, ORG, LOC, DATE, MISC).",
        name="ner",
        metadata={"tag_set": all_tags, "task": "ner", "n_samples": len(samples)},
    )


# ===================================================================
# Spam detection (binary)
# ===================================================================

_SPAM_DATA: List[Tuple[str, int]] = [
    # 0 = ham (not spam)
    ("Hey, are we still meeting for lunch tomorrow at noon?", 0),
    ("Just wanted to let you know the project deadline is Friday.", 0),
    ("Can you pick up some groceries on your way home?", 0),
    ("The meeting has been rescheduled to 3 PM. Please confirm.", 0),
    ("Thanks for sending over the report. I'll review it today.", 0),
    ("Happy birthday! Hope you have an amazing day.", 0),
    ("Reminder: dentist appointment at 2 PM on Wednesday.", 0),
    ("Could you share the presentation slides from yesterday?", 0),
    ("I'll be arriving at the airport at 6 PM. See you then.", 0),
    ("The weather looks great this weekend. Want to go hiking?", 0),
    ("Your order has been shipped and will arrive by Thursday.", 0),
    ("Let's schedule a call to discuss the quarterly review.", 0),
    ("I found a great restaurant we should try next week.", 0),
    ("Please review the attached contract and send feedback.", 0),
    ("Good news — the server migration completed successfully.", 0),
    # 1 = spam
    ("CONGRATULATIONS! You've won a $1,000,000 prize! Click here NOW!", 1),
    ("Free iPhone 15 Pro! Claim yours by entering your credit card.", 1),
    ("URGENT: Your account will be suspended unless you verify now.", 1),
    ("Buy cheap medications online! No prescription needed!", 1),
    ("Make $5000 per day working from home! Limited spots available!", 1),
    ("You have been selected for an exclusive luxury vacation deal!", 1),
    ("WARNING: Your computer is infected! Download our antivirus now!", 1),
    ("Get rich quick with this one weird trick banks hate!", 1),
    ("Double your investment in 24 hours! Guaranteed returns!", 1),
    ("FREE GIFT CARD! Complete this survey to claim your reward!", 1),
    ("Your loan has been pre-approved! No credit check required!", 1),
    ("Act now! This limited time offer expires in 2 hours!", 1),
    ("Congratulations, you are the 1,000,000th visitor! Claim prize!", 1),
    ("Lose 30 pounds in 30 days with this miracle supplement!", 1),
    ("ALERT: Unusual activity detected. Enter password to secure.", 1),
]


def load_spam(*, shuffle: bool = True, seed: Optional[int] = 42) -> Dataset:
    """30-sample binary spam detection dataset (15 ham, 15 spam).

    Returns
    -------
    Dataset
        ``data`` is an object array of message strings.
        ``target`` is 0 (ham) or 1 (spam).
    """
    texts, labels = zip(*_SPAM_DATA)
    data = np.array(texts, dtype=object)
    target = np.array(labels, dtype=np.int64)

    if shuffle:
        rng = np.random.RandomState(seed)
        idx = np.arange(len(data))
        rng.shuffle(idx)
        data, target = data[idx], target[idx]

    return Dataset(
        data=data.reshape(-1, 1),
        target=target,
        feature_names=["text"],
        target_names=["ham", "spam"],
        description="Binary spam detection dataset. 30 message samples (15 ham, 15 spam).",
        name="spam",
        metadata={"n_classes": 2, "task": "spam_detection"},
    )


# ===================================================================
# Question Answering pairs (for RAG / retrieval evaluation)
# ===================================================================

_QA_DATA: List[Dict] = [
    {"question": "What is the capital of France?", "answer": "Paris", "context": "Paris is the capital and largest city of France.", "category": "geography"},
    {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare", "context": "Romeo and Juliet is a tragedy written by William Shakespeare early in his career.", "category": "literature"},
    {"question": "What is the speed of light?", "answer": "299,792,458 meters per second", "context": "The speed of light in vacuum is exactly 299,792,458 metres per second.", "category": "physics"},
    {"question": "What year did World War II end?", "answer": "1945", "context": "World War II ended in 1945 with the surrender of both Germany and Japan.", "category": "history"},
    {"question": "What is the largest planet in our solar system?", "answer": "Jupiter", "context": "Jupiter is the largest planet in the Solar System with a mass more than twice that of all other planets combined.", "category": "astronomy"},
    {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci", "context": "The Mona Lisa is a half-length portrait painting by Italian artist Leonardo da Vinci.", "category": "art"},
    {"question": "What is the chemical formula for water?", "answer": "H2O", "context": "Water is a chemical substance with the formula H2O, consisting of two hydrogen atoms and one oxygen atom.", "category": "chemistry"},
    {"question": "What programming language was created by Guido van Rossum?", "answer": "Python", "context": "Python is a high-level programming language created by Guido van Rossum, first released in 1991.", "category": "technology"},
    {"question": "How many chromosomes do humans have?", "answer": "46", "context": "Humans typically have 46 chromosomes, arranged in 23 pairs, in each cell.", "category": "biology"},
    {"question": "What is the tallest mountain in the world?", "answer": "Mount Everest", "context": "Mount Everest, at 8,849 metres above sea level, is the tallest mountain on Earth.", "category": "geography"},
    {"question": "Who developed the theory of relativity?", "answer": "Albert Einstein", "context": "Albert Einstein developed the theory of relativity, one of the two pillars of modern physics.", "category": "physics"},
    {"question": "What is the largest organ in the human body?", "answer": "Skin", "context": "The skin is the largest organ of the human body, covering approximately 1.5 to 2 square meters.", "category": "biology"},
    {"question": "In what year was the internet invented?", "answer": "1969", "context": "The internet originated from ARPANET in 1969, connecting four university computers.", "category": "technology"},
    {"question": "What is the boiling point of water in Celsius?", "answer": "100 degrees Celsius", "context": "Pure water boils at 100 degrees Celsius at standard atmospheric pressure.", "category": "chemistry"},
    {"question": "Who was the first person to walk on the Moon?", "answer": "Neil Armstrong", "context": "Neil Armstrong became the first person to walk on the Moon on July 20, 1969.", "category": "history"},
]


def load_qa(*, shuffle: bool = True, seed: Optional[int] = 42) -> Dataset:
    """15-sample question-answering dataset with context passages.

    Useful for testing RAG retrieval and answer extraction.

    Returns
    -------
    Dataset
        ``data`` is an object array of question strings.
        ``target`` is an object array of answer strings.
        ``metadata["contexts"]`` and ``metadata["categories"]`` provide
        additional information per sample.
    """
    rng = np.random.RandomState(seed)
    samples = list(_QA_DATA)
    if shuffle:
        rng.shuffle(samples)

    questions = np.array([s["question"] for s in samples], dtype=object)
    answers = np.array([s["answer"] for s in samples], dtype=object)
    contexts = [s["context"] for s in samples]
    categories = [s["category"] for s in samples]

    return Dataset(
        data=questions.reshape(-1, 1),
        target=answers,
        feature_names=["question"],
        target_names=["answer"],
        description="Question-answering dataset with context passages. 15 samples across multiple domains.",
        name="qa",
        metadata={
            "task": "question_answering",
            "contexts": contexts,
            "categories": categories,
        },
    )
