# task

LastYearOrders: Captures the total amount spent by each customer on each product in the last year.
CustomerTotalSpent: Calculates the total amount spent by each customer.
CustomerCategorySpent: Computes the amount spent by each customer in each category.
CustomerMostPurchasedCategory: Identifies the most purchased category for each customer.
The final query combines these to find the top 5 customers along with their most purchased category.


2 
## Database Connection:

sqlalchemy is used to connect to an SQLite database and define the tables (Product and User).
Data Upload:

The load_data function loads data from a CSV file into a pandas DataFrame, handles missing values, and uploads the data to the database.
## Login and Sign-Up System using JWT:

The /signup endpoint hashes the password and stores the user in the database.
The /login endpoint verifies the credentials and returns a JWT token if successful. The token includes the user ID and expiration time.

## Data Cleaning:

Missing values for price and quantity_sold are replaced with their median values.
Missing values for rating are replaced with the average rating of the respective category.

## Summary Report:

The /summary endpoint generates a summary report of total revenue and the top-selling product by category and returns the result as a JSON response. The report is also saved as a CSV file.
