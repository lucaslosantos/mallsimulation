import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ULTIMATE import Restaurant

# Add this line at the start to ensure plots display
plt.switch_backend('TkAgg')

def view_mall_stats():
    # Read the CSV file
    df = pd.read_csv('mall_stats.csv')
    
    print("Available columns:", df.columns.tolist())
    
    # Process restaurant data
    def extract_restaurant_data(row):
        restaurants = {}
        try:
            # Split by pipe for multiple restaurants
            for restaurant_data in row.split(' | '):
                name, revenue = restaurant_data.split(': $')
                restaurants[name] = float(revenue)
        except Exception as e:
            print(f"Error processing row: {row}")
            return {}
        return restaurants
    
    # Create separate columns for each restaurant
    restaurant_data = df['Restaurant Stats'].apply(extract_restaurant_data)
    for restaurant in Restaurant:
        df[f'{restaurant.value}_Revenue'] = restaurant_data.apply(
            lambda x: x.get(restaurant.value, 0)
        )

    # Create a figure with subplots
    plt.style.use('fivethirtyeight')
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Revenue and Expenses Plot
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(df['Day'], df['Daily Revenue'], label='Revenue', color='green')
    ax1.plot(df['Day'], df['Daily Expenses'], label='Expenses', color='red')
    ax1.fill_between(df['Day'], df['Daily Revenue'], df['Daily Expenses'], 
                    where=(df['Daily Revenue'] >= df['Daily Expenses']),
                    color='lightgreen', alpha=0.3, label='Profit')
    ax1.fill_between(df['Day'], df['Daily Revenue'], df['Daily Expenses'],
                    where=(df['Daily Revenue'] < df['Daily Expenses']),
                    color='lightcoral', alpha=0.3, label='Loss')
    ax1.set_title('Daily Financial Performance')
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Amount ($)')
    ax1.legend()
    ax1.grid(True)

    # 2. Customer and Incidents Plot
    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(df['Day'], df['Customer Count'], label='Customers', color='blue')
    ax2.plot(df['Day'], df['Failed Parking'], label='Failed Parkings', color='orange')
    ax2.plot(df['Day'], df['Incidents'], label='Incidents', color='red', linestyle='--')
    ax2.set_title('Daily Activity Metrics')
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Count')
    ax2.legend()
    ax2.grid(True)

    # 3. Movie Popularity
    ax3 = plt.subplot(2, 2, 3)
    movie_counts = df['Movie'].value_counts()
    movie_counts.plot(kind='bar', ax=ax3)
    ax3.set_title('Most Shown Movies')
    ax3.set_xlabel('Movie')
    ax3.set_ylabel('Frequency')
    plt.xticks(rotation=45)

    # 4. Restaurant Performance
    ax4 = plt.subplot(2, 2, 4)
    for restaurant in Restaurant:
        ax4.plot(df['Day'], 
                df[f'{restaurant.value}_Revenue'],
                label=restaurant.value,
                marker='o')
    
    ax4.set_title('Daily Revenue by Restaurant')
    ax4.set_xlabel('Day')
    ax4.set_ylabel('Revenue ($)')
    ax4.legend()
    ax4.grid(True)

    # Adjust layout and display
    plt.tight_layout()
    plt.savefig('mall_stats.png')

    # Print summary statistics
    print("\n=== Mall Performance Summary ===")
    print(f"Average Daily Revenue: ${df['Daily Revenue'].mean():.2f}")
    print(f"Average Daily Expenses: ${df['Daily Expenses'].mean():.2f}")
    print(f"Average Daily Profit: ${(df['Daily Revenue'] - df['Daily Expenses']).mean():.2f}")
    print(f"Average Daily Customers: {df['Customer Count'].mean():.1f}")
    print(f"Average Failed Parking Attempts: {df['Failed Parking'].mean():.1f}")
    print(f"Total Incidents: {df['Incidents'].sum()}")
    print("\nMost Popular Movie:", df['Movie'].mode().iloc[0])
    print("Restaurant Performance:", df['Restaurant Stats'].mode().iloc[0])

    # Print summary statistics
    print("\n=== Restaurant Performance ===")
    for restaurant in Restaurant:
        avg_revenue = df[f'{restaurant.value}_Revenue'].mean()
        print(f"{restaurant.value} Average Daily Revenue: ${avg_revenue:.2f}")

# Add this line at the end of the file to actually call the function
if __name__ == "__main__":
    view_mall_stats()
