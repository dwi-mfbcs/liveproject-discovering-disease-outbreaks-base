import re
from collections import Counter
from geonamescache import GeonamesCache
import pandas as pd

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
    cities_with_headlines = []
    with open(filename, 'r') as f:
        for line in f:
            headline = line.strip()
            words = headline.split()
            headline_cities = []
            i = 0
            while i < len(words):
                # Check for multi-word cities (up to 4 words)
                for j in range(4, 0, -1):
                    if i + j <= len(words):
                        potential_city = ' '.join(words[i:i+j])
                        cleaned_city = clean_word(potential_city)
                        if cleaned_city in city_names and cleaned_city not in stop_words:
                            headline_cities.append(city_names[cleaned_city])
                            i += j
                            break
                else:
                    i += 1
            if headline_cities:
                for city in headline_cities:
                    cities_with_headlines.append((city[0], city[1], headline))
    return cities_with_headlines

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
cities_with_headlines = extract_cities('./data/headlines.txt', city_names)

# Create a DataFrame
df = pd.DataFrame(cities_with_headlines, columns=['City', 'Country', 'Headline'])

# Count occurrences
city_counts = df.groupby(['City', 'Country']).size().reset_index(name='Count')
city_counts = city_counts.sort_values('Count', ascending=False)

# Print the top 20 most mentioned cities
print("Top 20 most mentioned cities:")
print(city_counts.head(20))

# Save the full results to a CSV file
#df.to_csv('city_mentions.csv', index=False)
#print("\nFull results saved to 'city_mentions.csv'")