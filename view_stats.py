import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add this line at the start to ensure plots display
plt.switch_backend('TkAgg')

def view_mall_stats():
    # Read the CSV file
    df = pd.read_csv('mall_stats.csv')
    
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
    ax2.plot(df['Day'], df['Daily Customers'], label='Customers', color='blue')
    ax2.plot(df['Day'], df['Failed Parking Attempts'], label='Failed Parkings', color='orange')
    ax2.plot(df['Day'], df['Daily Incidents'], label='Incidents', color='red', linestyle='--')
    ax2.set_title('Daily Activity Metrics')
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Count')
    ax2.legend()
    ax2.grid(True)

    # 3. Movie Popularity
    ax3 = plt.subplot(2, 2, 3)
    movie_counts = df['Most Popular Movie'].value_counts()
    movie_counts.plot(kind='bar', ax=ax3)
    ax3.set_title('Most Shown Movies')
    ax3.set_xlabel('Movie')
    ax3.set_ylabel('Frequency')
    plt.xticks(rotation=45)

    # 4. Restaurant Performance
    ax4 = plt.subplot(2, 2, 4)
    # Extract restaurant names and revenues from the 'Top Restaurant' column
    restaurant_data = df['Top Restaurant'].str.split(':', expand=True)
    restaurant_data[1] = restaurant_data[1].str.replace('$', '').str.replace(' ', '').astype(float)
    restaurant_performance = restaurant_data.groupby(0)[1].mean()
    restaurant_performance.plot(kind='bar', ax=ax4)
    ax4.set_title('Average Daily Revenue by Restaurant')
    ax4.set_xlabel('Restaurant')
    ax4.set_ylabel('Average Revenue ($)')
    plt.xticks(rotation=45)

    # Adjust layout and display
    plt.tight_layout()
    plt.savefig('mall_stats.png')

    # Print summary statistics
    print("\n=== Mall Performance Summary ===")
    print(f"Average Daily Revenue: ${df['Daily Revenue'].mean():.2f}")
    print(f"Average Daily Expenses: ${df['Daily Expenses'].mean():.2f}")
    print(f"Average Daily Profit: ${(df['Daily Revenue'] - df['Daily Expenses']).mean():.2f}")
    print(f"Average Daily Customers: {df['Daily Customers'].mean():.1f}")
    print(f"Average Failed Parking Attempts: {df['Failed Parking Attempts'].mean():.1f}")
    print(f"Total Incidents: {df['Daily Incidents'].sum()}")
    print("\nMost Popular Movie:", df['Most Popular Movie'].mode().iloc[0])
    print("Most Profitable Restaurant:", df['Top Restaurant'].mode().iloc[0])

# Add this line at the end of the file to actually call the function
if __name__ == "__main__":
    view_mall_stats()
