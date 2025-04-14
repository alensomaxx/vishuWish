import random

def generate_blessing(tone="modern"):
    traditional = [
        "നിനക്ക് സമൃദ്ധിയും സുഖവും പൂർണ്ണമായി കിട്ടില്ലേ!",
        "ഇന്നത്തെ വിഷുവിന് ദൈവത്തിന്റെ അനുഗ്രഹങ്ങൾ!",
        "ഈ വിഷുവിൽ നിനക്ക് വിജയവും സമാധാനവും നേർക്കാം!"
    ]
    modern = [
        "Wishing you gold, growth, and good vibes!",
        "Here’s to fresh starts and fat wallets!",
        "May your Vishu be rich — in vibes and kaineetam!"
    ]
    funny = [
        "This Vishu, don’t ghost me. GPay me!",
        "Blessings are free. Kaineetam isn't!",
        "May your UPI balance be ever in your favor."
    ]

    options = {
        "traditional": traditional,
        "modern": modern,
        "funny": funny
    }

    return random.choice(options.get(tone, modern))
