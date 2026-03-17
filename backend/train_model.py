"""
Fake News Detection - Model Training Script
Trains a TF-IDF + Logistic Regression pipeline on synthetic data.
Run this once to generate the model file (fake_news_model.pkl).
"""

import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Synthetic training corpus
# In production you would swap this for a real dataset (e.g. LIAR, FakeNewsNet)
# ---------------------------------------------------------------------------

real_news = [
    "The Federal Reserve announced a quarter-point interest rate increase today, citing ongoing inflationary pressures in the economy.",
    "Scientists at CERN have confirmed the detection of a new subatomic particle consistent with theoretical predictions.",
    "The World Health Organization reported a 15% decline in global malaria cases over the past five years.",
    "NASA's Perseverance rover has collected its 20th rock sample from the Jezero Crater on Mars.",
    "The European Union passed new legislation requiring tech companies to improve data privacy protections.",
    "A 6.2 magnitude earthquake struck the coast of Chile early Wednesday morning. No tsunami warning was issued.",
    "The United Nations General Assembly voted to expand humanitarian aid to conflict zones in East Africa.",
    "Researchers at MIT developed a new battery technology that could double the range of electric vehicles.",
    "The Bank of England held interest rates steady at 5.25% amid mixed economic signals.",
    "A new study published in The Lancet shows that regular exercise reduces the risk of cardiovascular disease by 30%.",
    "India's space agency ISRO successfully launched its latest communication satellite into geostationary orbit.",
    "The Supreme Court agreed to hear arguments on a landmark case regarding digital privacy rights.",
    "Global carbon dioxide emissions rose by 1.1% in 2024 according to a report by the International Energy Agency.",
    "Apple announced its quarterly earnings exceeded analyst expectations with revenue of $94.8 billion.",
    "The mayor of London unveiled a new public transportation plan aimed at reducing congestion by 20% over five years.",
    "Climate scientists warn that Arctic sea ice is melting at an unprecedented rate, reaching record lows this summer.",
    "A bipartisan group of senators introduced legislation to modernize the country's aging infrastructure.",
    "The International Monetary Fund projected global economic growth at 3.1% for the coming fiscal year.",
    "Doctors Without Borders opened three new clinics in rural areas of South Sudan to address healthcare shortages.",
    "Toyota announced plans to invest $13 billion in battery technology as part of its electric vehicle strategy.",
    "The stock market closed slightly higher today as investors awaited the latest jobs report from the Labor Department.",
    "A team of archaeologists discovered a previously unknown ancient city in the jungles of Guatemala.",
    "The CDC reported that flu hospitalizations have decreased by 22% compared to the same period last year.",
    "Germany's coalition government agreed on a new climate package targeting 65% emissions reduction by 2030.",
    "The Nobel Prize in Chemistry was awarded to three researchers for their work on quantum dot nanocrystals.",
    "Singapore Airlines reported record profits driven by strong demand in premium travel segments.",
    "Heavy rainfall caused flooding in parts of southern France, prompting emergency evacuations in several towns.",
    "The Federal Aviation Administration issued new safety guidelines for commercial drone operations.",
    "Economists at Goldman Sachs predicted a soft landing for the U.S. economy with no recession expected.",
    "The International Space Station crew successfully completed a six-hour spacewalk to repair solar panels.",
    "A government report showed that unemployment fell to 3.7%, the lowest level in over a decade.",
    "Pfizer received regulatory approval for a new treatment targeting rare genetic disorders in children.",
    "The African Union held an emergency summit to discuss peacekeeping efforts in the Sahel region.",
    "Microsoft announced it would acquire a cybersecurity firm for $2.1 billion to strengthen its cloud offerings.",
    "Wildfires in northern California have burned over 50,000 acres, forcing thousands to evacuate.",
    "A peer-reviewed study found that Mediterranean diets are associated with improved cognitive function in older adults.",
    "South Korea's semiconductor exports grew by 18% year-over-year, boosting the country's trade surplus.",
    "The World Bank approved a $500 million loan to support renewable energy projects across Southeast Asia.",
    "New York City's public school system reported a 5% increase in graduation rates for the 2024-2025 academic year.",
    "The Federal Trade Commission launched an investigation into anti-competitive practices in the tech industry.",
]

fake_news = [
    "BREAKING: Scientists discover that drinking bleach cures all known diseases! Hospitals don't want you to know!",
    "SHOCKING: Secret government documents reveal that the moon landing was filmed in a Hollywood studio!",
    "EXCLUSIVE: Bill Gates admits that 5G towers are being used to implant microchips in the global population!",
    "EXPOSED: Major airline caught spraying mind-control chemicals through chemtrails over major cities!",
    "URGENT: Eating five bananas a day has been proven to completely cure cancer, doctors furious!",
    "ALERT: The earth is actually flat — NASA whistleblower leaks classified photos proving the truth!",
    "BOMBSHELL: Government confirms that aliens have been living among us for decades!",
    "REVEALED: Drinking hot water with lemon every morning makes you immune to all viruses forever!",
    "SCANDAL: Famous celebrity caught in underground tunnel network connected to secret society!",
    "CONFIRMED: Wi-Fi signals cause brain tumors — study hidden by tech companies for years!",
    "BREAKING: Thousands of voters exposed in massive election fraud scheme — ballots found in dumpster!",
    "SHOCKING: New world order revealed — global elites plan to replace all currencies with microchips!",
    "EXCLUSIVE: COVID-19 vaccine contains tracking nanobots according to leaked Pfizer documents!",
    "EXPOSED: Solar panels are secretly draining the sun's energy and causing global warming!",
    "URGENT: Fluoride in water supply is a government plot to control population growth!",
    "ALERT: Hollywood celebrities are actually lizard people from another dimension!",
    "BOMBSHELL: Major bank secretly moving all customer money to offshore accounts — millions affected!",
    "REVEALED: Children who eat organic food develop superhuman abilities according to suppressed study!",
    "SCANDAL: Top politician caught with time machine — has been manipulating elections for decades!",
    "CONFIRMED: Your smartphone is recording everything you say and sending it directly to the CIA!",
    "BREAKING: Ancient pyramid discovered under the White House — proof of alien government conspiracy!",
    "SHOCKING: Local man discovers miracle herb that regrows hair overnight — pharma companies in panic!",
    "EXCLUSIVE: Scientists admit evolution is a hoax — humans were created by advanced aliens!",
    "EXPOSED: The sun is actually cold — everything you learned in school is a lie!",
    "URGENT: Wearing masks permanently damages your DNA according to top European scientists!",
    "ALERT: Social media companies confirmed to be run by artificial intelligence that controls your thoughts!",
    "BOMBSHELL: Major fast food chain caught using human meat in their burgers — whistleblower speaks out!",
    "REVEALED: The ocean is actually shrinking and will disappear in 10 years — governments cover it up!",
    "SCANDAL: Top university professors admit that degrees are worthless — entire education system is a scam!",
    "CONFIRMED: Gravity is not real — objects fall because the earth is constantly accelerating upward!",
    "BREAKING: Weather control machine discovered in secret military base — responsible for all hurricanes!",
    "SHOCKING: Millionaire reveals money trick that banks don't want you to know! Make $50,000 overnight!",
    "EXCLUSIVE: Proof that dinosaurs never existed — fossils were planted by the government!",
    "EXPOSED: Tap water turns people into mindless zombies — switch to raw water immediately!",
    "URGENT: New study shows that sleeping is actually harmful — top doctors recommend staying awake 24/7!",
    "ALERT: Secret underground cities discovered where elites plan to survive the manufactured apocalypse!",
    "BOMBSHELL: Airlines have been hiding the truth — planes don't actually fly, they're suspended by invisible cables!",
    "REVEALED: All world leaders are clones — the real ones were replaced decades ago!",
    "SCANDAL: Oxygen levels being deliberately reduced by global organizations to weaken the population!",
    "CONFIRMED: Looking at your phone screen for 8+ hours gives you telepathic powers — tech companies know!",
]

def get_training_data():
    import pandas as pd
    url = "https://raw.githubusercontent.com/joolsa/fake_real_news_dataset/master/fake_or_real_news.csv"
    print("🌐 Downloading fake news dataset from GitHub to train on real-world news...")
    try:
        # Load a large open-source dataset
        df = pd.read_csv(url)
        if 'text' in df.columns and 'label' in df.columns:
            texts = df['text'].fillna("").tolist()
            # FAKE == fake news (1), REAL == real news (0)
            labels = df['label'].apply(lambda x: 1 if str(x).upper() == 'FAKE' else 0).tolist()
            print(f"✅ Successfully downloaded {len(texts)} real-world news articles for training!")
            return texts, labels
    except Exception as e:
        print(f"⚠️ Could not download the external dataset ({e}). Falling back to synthetic data.")
    
    # Fallback to synthetic if network fails
    texts = real_news + fake_news
    labels = [0] * len(real_news) + [1] * len(fake_news)
    return texts, labels

def train_model():
    """Train and save the fake news detection model."""
    print("🔧 Preparing training data...")

    texts, labels = get_training_data()

    # Shuffle
    combined = list(zip(texts, labels))
    np.random.seed(42)
    np.random.shuffle(combined)
    texts, labels = zip(*combined)
    texts, labels = list(texts), list(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples:  {len(X_test)}")

    # Build pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1,
            max_df=0.95,
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42,
        )),
    ])

    print("🏋️ Training model...")
    pipeline.fit(X_train, y_train)

    accuracy = pipeline.score(X_test, y_test)
    print(f"✅ Model accuracy on test set: {accuracy:.2%}")

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "model", "fake_news_model.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"💾 Model saved to {model_path}")

    return pipeline


if __name__ == "__main__":
    train_model()
