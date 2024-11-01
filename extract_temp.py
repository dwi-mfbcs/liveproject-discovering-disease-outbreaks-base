import re
from collections import Counter
from geonamescache import GeonamesCache

def get_city_names():
    gc = GeonamesCache()
    cities = gc.get_cities()
    countries = gc.get_countries()
    return {city['name'].lower(): (city['name'], countries[city['countrycode']]['name']) 
            for city in cities.values()}

def clean_word(word):
    # Remove possessive 's and any non-alphabetic characters except spaces
    return re.sub(r"'s|[^a-zA-Z\s]", '', word).strip().lower()

# List of words to exclude from city detection (all lowercase)
stop_words = {'of', 'man', 'the', 'in', 'on', 'at', 'by', 'for', 'with', 'to', 'from'}

def extract_cities(filename, city_names):
    cities = []
    with open(filename, 'r') as f:
        for line in f:
            words = line.strip().split()
            i = 0
            while i < len(words):
                # Check for multi-word cities (up to 4 words)
                for j in range(4, 0, -1):
                    if i + j <= len(words):
                        potential_city = ' '.join(words[i:i+j])
                        cleaned_city = clean_word(potential_city)
                        if cleaned_city in city_names and cleaned_city not in stop_words:
                            cities.append(city_names[cleaned_city])
                            i += j
                            break
                else:
                    i += 1
    return cities

# Get the dictionary of city names
city_names = get_city_names()

# Add some common compound names that might not be in geonamescache
compound_names = {
    'tampa bay': ('Tampa Bay', 'United States'),
    'rio grande valley': ('Rio Grande Valley', 'United States'),
    # Add more as needed
}
city_names.update(compound_names)

# Extract cities
cities = extract_cities('./data/headlines.txt', city_names)

# Count occurrences
city_counts = Counter(cities)

# Print the top 20 most mentioned cities
print("Top 20 most mentioned cities:")
for (city, country), count in city_counts.most_common(700):
    print(f"{city}, {country}: {count}")