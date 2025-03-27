Property Finder in NY - Django Web Application
Overview
This is a web-based application built with the Django rest framework that allows users to find properties in New York City. The application integrates a Language Learning Model (LLM) and a query agent to facilitate intelligent property searches using natural language queries. It leverages an open-source real estate dataset from Kaggle to provide users with a comprehensive and up-to-date list of properties.

Key Features:
Property Search: Users can search for properties in New York based on various filters like location, price range, number of bedrooms, etc.

Natural Language Query: The LLM-based query agent interprets user queries in natural language, allowing users to ask questions like "Find me apartments under $2,000 near Central Park."

Real Estate Dataset: The application uses an open-source property dataset sourced from Kaggle to display available listings.

Ranking: The app accepts users rattings and corrections for better future performance

Example of queries:
1. Price-related Queries
"Show me properties under $500,000."
"List houses that are priced over $1,000,000."
"Find all properties with a price range between $300,000 and $700,000."
"What properties are for sale with a price less than $200,000?"
"Give me all properties that cost more than $2,500,000."
2. Location-related Queries
"Show me condos in New York City."
"Find properties in California near the beach."
"List homes for sale in Brooklyn, NY."
"Show properties in Manhattan with prices under $1,000,000."
"Find houses in Los Angeles with more than 3 bedrooms."
3. Property Type-related Queries
"Find me all the condos in the city."
"Show only houses for sale."
"List townhouses in San Francisco."
"I want to see duplexes in Brooklyn."
"Give me apartments in New York under $400,000."
4. Size and Bedroom-related Queries
"Find homes with more than 5 bedrooms."
"What properties have at least 3 bathrooms?"
"Show me apartments with 2 or more bedrooms."
"List homes that are over 2,000 sq ft."
5. Advanced Queries
"Show me properties that have 4 bedrooms and 3 bathrooms"
"List homes with more than 2,500 sq ft, in the $500,000 to $750,000 price range."
"Give me all properties in Brooklyn with 3+ bedrooms and 2+ bathrooms."
"Find houses in California with at least 3 bedrooms, with a price between $600,000 and $1,000,000."
6. Combination Queries
"Show me all condos in New York with 2+ bedrooms and a price under $300,000."
"What properties have more than 3 bedrooms and are priced under $1,000,000?"
"Give me all properties in San Francisco with at least 3 bathrooms and more than 1,500 sq ft."
"Find apartments with a balcony and priced below $500,000 in Manhattan."
7. Other Queries
"Give me houses for sale in California with no more than 3 bedrooms."
"Find houses near the beach with a view of the ocean."
"What are the cheapest houses in the city?"

