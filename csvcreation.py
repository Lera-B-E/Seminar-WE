import pandas as pd
import random
import os


os.makedirs("datasets", exist_ok=True)

names = ["Alice", "Bob", "Charlie", "Diana", "Eva", "Frank", "Grace", "Helen","alice", "bob", "charlie", "diana", "eva", "frank", "grace", "helen"]
ages = list(range(18, 70))
cities = {
    "New York": ["NYC", "new york", "nyc"],
    "Los Angeles": ["LA", "los angeles"],
    "London": ["London", "london", "UK"],
    "Dubai": ["Dubai", "dubai", "UAE", "uae"],
    "Paris": ["Paris", "paris", "France"],
    "Tokyo": ["Tokyo", "tokyo", "Japan"],
    "Sydney": ["Sydney", "sydney", "Australia"],
}
countries = {
    "United States": ["USA", "usa", "US", "us", "United States", "united states"],
    "United Kingdom": ["UK", "uk", "United Kingdom", "united kingdom"],
    "United Arab Emirates": ["UAE", "uae", "United Arab Emirates", "united arab emirates"],
    "France": ["France", "france"],
    "Japan": ["Japan", "japan"],
    "Australia": ["Australia", "australia"],
}

def get_variant(options):
    return random.choice(options)

data = []
for i in range(10000):
    name = random.choice(names)
    age = random.choice(ages)
    city_full = random.choice(list(cities.keys()))
    country_full = random.choice(list(countries.keys()))

    city_variant = get_variant(cities[city_full])
    country_variant = get_variant(countries[country_full])

    if random.random() < 0.4:
        name = name.lower()

    data.append([name, age, city_variant, country_variant])

df = pd.DataFrame(data, columns=["Name", "Age", "City", "Country"])

output_path = "datasets/synthetic_dataset.csv"
df.to_csv(output_path, index=False)

print(f"✅ Dataset saved to: {output_path}")