import threading
import time
import random
from enum import Enum
import tkinter as tk
from tkinter import ttk
from parking_visualizer import ParkingVisualizer
from concurrent.futures import ThreadPoolExecutor
import csv
import os

# Constantes de tiempo
SIMULATION_HOUR = 2.5  # 2.5 segundos = 1 hora simulada
DISPLAY_INTERVAL = 6 * SIMULATION_HOUR  # 6 horas simuladas

# Lista de marcas de coches
CAR_BRANDS = ["Ford", "Ferrari", "Fiat", "Volkswagen", "Audi", "Maserati", "Lancia",
              "BMW", "Mercedes", "Toyota", "Honda", "Cadillac", "Lexus", "Porsche",
              "Range Rover", "Chevrolet", "Jeep", "Seat", "Cupra", "Peugeot", "Renault"]


class ActivityType(Enum):
    SHOPPING = "shopping"
    DINING = "dining"
    CINEMA = "cinema"


class Movie(Enum):
    STAR_WARS = "Star Wars"
    DUNE = "Dune"
    LORD_OF_THE_RINGS = "Lord of the Rings"
    LALALAND = "LaLaLand"
    FIGHT_CLUB = "Fight Club"


class Shop(Enum):
    CLOTHING = ("Clothing Store", 20, 250)
    TOYS = ("Toys Store", 5, 50)
    VIDEO_GAMES = ("Video Games Store", 20, 80)
    SPORTS = ("Sports Store", 15, 120)
    SUPERMARKET = ("Supermarket", 1, 120)
    
    def __init__(self, display_name, min_spend, max_spend):
        self.display_name = display_name
        self.min_spend = min_spend
        self.max_spend = max_spend


class Restaurant(Enum):
    MCDONALDS = "McDonald's"
    BURGER_KING = "Burger King"
    KFC = "KFC"


class ParkingLot:
    def __init__(self, levels=5, spaces_per_level=10):
        self.levels = levels
        self.spaces_per_level = spaces_per_level
        self.parking_structure = [[None] * spaces_per_level for _ in range(levels)]
        self.lock = threading.Lock()
        self.inaccessible_levels = {}  # Changed from set to dict to store recovery times
        self.blocked_spots = {}  # Dictionary to store blocked spots and their recovery time
        self.incident_costs = {
            'flooding': (1000, 2000),    # Range of cost for flooding cleanup
            'collision': (300, 800),     # Range for collision damage
            'light': (50, 150)           # Range for light repair
        }
        self.had_flooding = False  # New flag to track if flooding has occurred
        
    def get_level_name(self, level):
        """Convert level number to negative floor number (0 -> -5, 1 -> -4, etc.)"""
        return -(self.levels - level)

    def check_for_incidents(self):
        """Comprueba y maneja incidentes en el estacionamiento."""
        incidents = []
        current_time = time.time()
        total_cost = 0

        # Clean up resolved blocked spots
        resolved_spots = [spot for spot, recovery_time in self.blocked_spots.items() 
                        if current_time > recovery_time]
        for spot in resolved_spots:
            del self.blocked_spots[spot]
            incidents.append({
                'type': 'resolved',
                'message': f"Spot {spot[1]} on level {self.get_level_name(spot[0])} is now clear",
                'cost': 0
            })

        # Clean up resolved flooding
        resolved_levels = [level for level, recovery_time in self.inaccessible_levels.items()
                         if current_time > recovery_time]
        for level in resolved_levels:
            del self.inaccessible_levels[level]
            incidents.append({
                'type': 'resolved',
                'message': f"Flooding on level {self.get_level_name(level)} has been cleared",
                'cost': 0
            })

        # Flooding - only if it hasn't happened before
        if not self.had_flooding and random.random() < 0.01:  # 1% probability
            level = 0  # Always floods lowest level
            if level not in self.inaccessible_levels:
                recovery_time = current_time + (12 * SIMULATION_HOUR)  # 12-hour recovery
                self.inaccessible_levels[level] = recovery_time
                cost = random.uniform(*self.incident_costs['flooding'])
                incidents.append({
                    'type': 'flooding',
                    'message': f"Flooding on level -5 (lowest level). Level inaccessible for 12 hours!",
                    'cost': cost
                })
                total_cost += cost
                self.had_flooding = True  # Set flag to prevent future floods

        # Light malfunction
        if random.random() < 0.04:
            level = random.randint(0, self.levels - 1)
            spot = random.randint(0, self.spaces_per_level - 1)
            if (level, spot) not in self.blocked_spots:
                recovery_time = current_time + (1 * SIMULATION_HOUR)
                self.blocked_spots[(level, spot)] = recovery_time
                cost = random.uniform(*self.incident_costs['light'])
                incidents.append({
                    'type': 'light',
                    'message': f"Light malfunction blocks spot {spot} on level {self.get_level_name(level)} for 1 hour",
                    'cost': cost
                })
                total_cost += cost

        return incidents, total_cost

    def find_parking_spot(self, vehicle):
        """Encuentra un espacio de estacionamiento disponible."""
        with self.lock:
            # Check for collision during entry (3% chance when parking)
            if random.random() < 0.03:
                level = random.randint(0, self.levels - 1)
                spot = random.randint(0, self.spaces_per_level - 1)
                if (level, spot) not in self.blocked_spots:
                    recovery_time = time.time() + (2 * SIMULATION_HOUR)
                    self.blocked_spots[(level, spot)] = recovery_time
                    cost = random.uniform(*self.incident_costs['collision'])
                    return None, None, [{
                        'type': 'collision',
                        'message': f"Vehicle collision during parking attempt blocks spot {spot} on level {self.get_level_name(level)} for 2 hours",
                        'cost': cost
                    }]

            # First try to park electric vehicles in designated spots
            if vehicle.vehicle_type == "electric":
                # Try level -1 (index 0) first for electric vehicles
                if 0 not in self.inaccessible_levels:
                    for spot in range(4):  # First 4 spots reserved for electric
                        if (0, spot) not in self.blocked_spots and self.parking_structure[0][spot] is None:
                            self.parking_structure[0][spot] = vehicle
                            print(f"DEBUG: Assigned electric spot {spot} on level -5 (priority)")
                            return 0, spot, []
                
                # If level -1 is full or inaccessible, try top level
                if 4 not in self.inaccessible_levels:
                    for spot in range(4):
                        if (4, spot) not in self.blocked_spots and self.parking_structure[4][spot] is None:
                            self.parking_structure[4][spot] = vehicle
                            print(f"DEBUG: Assigned electric spot {spot} on level -1 (backup)")
                            return 4, spot, []

            # Regular parking logic for non-electric or if electric spots are full
            for level in range(self.levels):
                if level in self.inaccessible_levels:
                    continue
                
                for spot in range(self.spaces_per_level):
                    # Skip blocked spots and reserved electric spots
                    if (level, spot) in self.blocked_spots:
                        continue
                    if (level == 0 or level == 4) and spot < 4 and vehicle.vehicle_type != "electric":
                        continue
                        
                    if self.parking_structure[level][spot] is None:
                        self.parking_structure[level][spot] = vehicle
                        print(f"DEBUG: Assigned spot {spot} on level {self.get_level_name(level)}")
                        return level, spot, []

            # If no spot found, show detailed parking state
            print(f"\nDEBUG: No spots found. Parking structure state:")
            for level in range(self.levels):
                occupied_spots = sum(1 for spot in self.parking_structure[level] if spot is not None)
                status = "FLOODED" if level in self.inaccessible_levels else "NORMAL"
                blocked_on_level = sum(1 for (l, s) in self.blocked_spots.keys() if l == level)
                electric_reserved = "4 spots reserved for electric" if level == 4 else ""
                print(f"DEBUG: Level {self.get_level_name(level)}: {occupied_spots}/10 spots occupied - Status: {status} - Blocked spots: {blocked_on_level} {electric_reserved}")
            
            return None, None, []

    def retrieve_vehicle(self, level, spot):
        """Retrieve a vehicle from the parking lot."""
        with self.lock:
            # Check for collision during exit (3% chance when leaving)
            if random.random() < 0.03:
                if (level, spot) not in self.blocked_spots:
                    recovery_time = time.time() + (2 * SIMULATION_HOUR)
                    self.blocked_spots[(level, spot)] = recovery_time
                    cost = random.uniform(*self.incident_costs['collision'])
                    incident = {
                        'type': 'collision',
                        'message': f"Vehicle collision during exit blocks spot {spot} on level {self.get_level_name(level)} for 2 hours",
                        'cost': cost
                    }
                    return self.parking_structure[level][spot], [incident]

            vehicle = self.parking_structure[level][spot]
            self.parking_structure[level][spot] = None
            print(f"DEBUG: Freed spot {spot} on level {self.get_level_name(level)}")
            return vehicle, []


class Vehicle:
    def __init__(self, vehicle_id, vehicle_type="gasoline", brand=None):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.brand = brand or random.choice(CAR_BRANDS)
        self.entry_time = time.time()
        self.duration = random.randint(1, 30) * SIMULATION_HOUR

    def __str__(self):
        type_suffix = " (E)" if self.vehicle_type == "electric" else ""
        return f"{self.brand}{type_suffix}"


class Customer:
    def __init__(self, customer_id, vehicle):
        self.customer_id = customer_id
        self.vehicle = vehicle
        self.activities = self._generate_activities()
        self.total_spent = 0
        self.entry_time = time.time()
        self.shopping_history = []
        self.activity_log = []  # New: track all activities with timestamps

    def log_activity(self, message):
        """Add timestamped activity to log"""
        timestamp = time.time()
        sim_hours = (timestamp - self.entry_time) / SIMULATION_HOUR
        self.activity_log.append(f"[{sim_hours:.1f}h] {message}")

    def _generate_activities(self):
        """Genera 1-3 actividades aleatorias para el cliente."""
        num_activities = random.randint(1, 3)
        possible_activities = list(ActivityType)
        selected_activities = random.sample(possible_activities, num_activities)
        return selected_activities

    def __str__(self):
        vehicle_type = "(Electric)" if self.vehicle.vehicle_type == "electric" else "(Gasoline)"
        return f"Customer {self.customer_id} with {self.vehicle.brand} {vehicle_type}"


class Cinema:
    def __init__(self):
        self.capacity = 8
        self.ticket_price = 25
        self.seats = [None] * self.capacity
        self.last_movie = None
        self.daily_revenue = 0
        self.total_revenue = 0
        self.daily_customers = 0
        self.lock = threading.Lock()
        self.current_movie = self.set_next_movie()

    def set_next_movie(self):
        """Selecciona la siguiente película evitando repetición."""
        available_movies = [movie for movie in Movie if movie != self.last_movie]
        self.current_movie = random.choice(available_movies)
        self.last_movie = self.current_movie
        self.seats = [None] * self.capacity
        return self.current_movie

    def try_occupy_seat(self, customer):
        """Intenta ocupar un asiento para el cliente."""
        with self.lock:
            empty_seats = [i for i, seat in enumerate(self.seats) if seat is None]
            if empty_seats:
                seat = random.choice(empty_seats)
                self.seats[seat] = customer
                self.daily_revenue += self.ticket_price
                self.total_revenue += self.ticket_price
                self.daily_customers += 1
                return seat
            return None


class RestaurantManager:
    def __init__(self):
        self.restaurants = {
            restaurant: {
                'capacity': 10,
                'occupied': 0,
                'daily_revenue': 0,
                'total_revenue': 0,
                'daily_customers': 0
            } for restaurant in Restaurant
        }
        self.lock = threading.Lock()

    def try_seat_customer(self, restaurant):
        """Intenta sentar a un cliente en el restaurante especificado."""
        with self.lock:
            if self.restaurants[restaurant]['occupied'] < self.restaurants[restaurant]['capacity']:
                self.restaurants[restaurant]['occupied'] += 1
                spend = random.uniform(5, 25)
                self.restaurants[restaurant]['daily_revenue'] += spend
                self.restaurants[restaurant]['total_revenue'] += spend
                self.restaurants[restaurant]['daily_customers'] += 1
                return spend
            return None

    def customer_leaves(self, restaurant):
        """Registra la salida de un cliente del restaurante."""
        with self.lock:
            if self.restaurants[restaurant]['occupied'] > 0:
                self.restaurants[restaurant]['occupied'] -= 1


class ShopManager:
    def __init__(self):
        self.shops = {
            shop: {
                'daily_revenue': 0,
                'total_revenue': 0,
                'daily_customers': 0
            } for shop in Shop
        }
        self.lock = threading.Lock()

    def process_purchase(self, shop, customer):
        """Procesa una compra en una tienda."""
        with self.lock:
            spend = random.uniform(shop.min_spend, shop.max_spend)
            self.shops[shop]['daily_revenue'] += spend
            self.shops[shop]['total_revenue'] += spend
            self.shops[shop]['daily_customers'] += 1
            return spend


class MallManager:
    def __init__(self):
        self.parking_lot = ParkingLot()
        self.cinema = Cinema()
        self.restaurant_manager = RestaurantManager()
        self.shop_manager = ShopManager()

        # Financial tracking
        self.balance = 10000  # Starting balance
        
        # Daily metrics
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.daily_customer_count = 0
        self.daily_failed_attempts = 0
        self.daily_incidents = 0
        
        # Total/Historical metrics
        self.total_revenue = 0
        self.total_expenses = 0
        self.total_incidents = 0
        self.customer_count = 0
        
        self.day_start_time = time.time()
        self.incident_log = []

        # Time tracking
        self.day_start_time = time.time()

        # Usage counters
        self.customer_count = 0
        self.daily_customer_count = 0
        self.failed_parking_attempts = 0
        self.daily_failed_attempts = 0

        # State and maintenance
        self.mall_condition = 10
        self.daily_incidents = 0
        self.total_incidents = 0
        self.incident_log = []
        self.towed_vehicles = []

        # Thread control
        self.lock = threading.Lock()
        self.active_customers = {}

        # Base operating expenses per hour
        self.hourly_expenses = {
            'electricity': (10, 20),
            'cleaning': (5, 15),
            'staff': (20, 30),
            'maintenance': (15, 25)
        }

        self.visualizer = None

        # Add day counter
        self.current_day = 1

        # Add ThreadPoolExecutor with a reasonable number of workers
        self.customer_executor = ThreadPoolExecutor(max_workers=20)  # Adjust based on your needs

        # Initialize CSV file with headers if it doesn't exist
        if not os.path.exists('mall_stats.csv'):
            with open('mall_stats.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Day',
                    'Daily Revenue',
                    'Daily Expenses',
                    'Daily Customers',
                    'Daily Incidents',
                    'Failed Parking Attempts',
                    'Most Popular Movie',
                    'Top Restaurant',
                    'Top Shop'
                ])

    def start_gui(self):
        """Initialize and start the GUI"""
        self.visualizer = ParkingVisualizer(self, SIMULATION_HOUR, Restaurant)
        self.visualizer.root.mainloop()

    def process_new_customer(self):
        """Procesa la llegada de un nuevo cliente al centro comercial."""
        self.customer_count += 1
        self.daily_customer_count += 1
        customer_id = self.customer_count

        # Create vehicle and customer
        vehicle_type = "electric" if random.random() < 0.3 else "gasoline"
        vehicle = Vehicle(customer_id, vehicle_type=vehicle_type)
        customer = Customer(customer_id, vehicle)

        # Try to park with retries
        max_attempts = 3
        for attempt in range(max_attempts):
            level, spot, incidents = self.parking_lot.find_parking_spot(vehicle)
            if level is not None:
                print(f"\nCustomer {customer_id} arrives at the mall...")
                
                # Register active customer
                self.active_customers[customer_id] = {
                    'customer': customer,
                    'parking': (level, spot),
                    'entry_time': time.time()
                }

                # Submit customer activities to thread pool instead of creating new thread
                self.customer_executor.submit(self.handle_customer_activities, customer_id)
                return
            
            if attempt < max_attempts - 1:
                time.sleep(0.1)
        
        print(f"\nCustomer {customer_id} couldn't find parking and left")
        self.failed_parking_attempts += 1
        self.daily_failed_attempts += 1

    def handle_customer_activities(self, customer_id):
        """Maneja las actividades de un cliente en el centro comercial."""
        customer_data = self.active_customers[customer_id]
        customer = customer_data['customer']
        
        print(f"\n=== {customer} starts their mall visit ===")
        customer.log_activity("Entered mall")
        
        if customer.vehicle.vehicle_type == "electric":
            level, spot = customer_data['parking']
            is_charging = level == 4 and spot < 4
            customer.log_activity(f"Parked at level {self.parking_lot.get_level_name(level)}, spot {spot} "
                                f"{'(Charging spot)' if is_charging else '(Regular spot)'}")
        else:
            level, spot = customer_data['parking']
            customer.log_activity(f"Parked at level {self.parking_lot.get_level_name(level)}, spot {spot}")

        print(f"Planned activities: {[act.value for act in customer.activities]}")
        
        total_time = 0
        for activity in customer.activities:
            time_spent = 0

            if activity == ActivityType.CINEMA:
                if self.cinema.current_movie is None:
                    self.cinema.set_next_movie()
                seat = self.cinema.try_occupy_seat(customer)
                if seat is not None:
                    spend = self.cinema.ticket_price
                    time_spent = 3
                    customer.log_activity(f"Watching {self.cinema.current_movie.value} in seat {seat} - Spent: ${spend}")
                    customer.shopping_history.append((activity, spend))
                    customer.total_spent += spend
                    time.sleep(time_spent * SIMULATION_HOUR)
                else:
                    customer.log_activity("Tried to watch movie but cinema was full")

            elif activity == ActivityType.DINING:
                restaurant = random.choice(list(Restaurant))
                spend = self.restaurant_manager.try_seat_customer(restaurant)
                if spend is not None:
                    time_spent = random.uniform(1, 3)
                    customer.log_activity(f"Eating at {restaurant.value} - Spent: ${spend:.2f}")
                    customer.shopping_history.append((activity, spend))
                    customer.total_spent += spend
                    time.sleep(time_spent * SIMULATION_HOUR)
                    self.restaurant_manager.customer_leaves(restaurant)
                    customer.log_activity(f"Finished meal at {restaurant.value}")
                else:
                    customer.log_activity(f"Tried to eat at {restaurant.value} but it was full")

            elif activity == ActivityType.SHOPPING:
                shop = random.choice(list(Shop))
                spend = self.shop_manager.process_purchase(shop, customer)
                time_spent = random.uniform(1, 3)
                customer.log_activity(f"Shopping at {shop.display_name} - Spent: ${spend:.2f}")
                customer.shopping_history.append((activity, spend))
                customer.total_spent += spend
                time.sleep(time_spent * SIMULATION_HOUR)

            total_time += time_spent

        # Print complete activity log at exit
        print(f"\n=== {customer} completes their visit ===")
        print("Activity Log:")
        for log_entry in customer.activity_log:
            print(f"  {log_entry}")
        print(f"Total time spent: {total_time:.1f} hours")
        print(f"Total money spent: ${customer.total_spent:.2f}")
        
        # Process exit
        self.process_customer_exit(customer_id)

    def process_customer_exit(self, customer_id):
        """Procesa la salida de un cliente del centro comercial."""
        if customer_id not in self.active_customers:
            return

        customer_data = self.active_customers[customer_id]
        customer = customer_data['customer']
        level, spot = customer_data['parking']
        entry_time = customer_data['entry_time']

        # Calcular tiempo total y tarifa de estacionamiento
        total_time = time.time() - entry_time
        parking_fee = self.calculate_parking_fee(customer.vehicle, total_time)

        # Liberar espacio de estacionamiento
        self.parking_lot.retrieve_vehicle(level, spot)

        print(f"\nCustomer {customer_id} leaves the mall after {total_time / SIMULATION_HOUR:.1f} hours")
        print(f"Parking spot {spot} in floor {self.parking_lot.get_level_name(level)} is now free")
        print(f"Total spent in activities: ${customer.total_spent:.2f}")
        print(f"Parking fee: ${parking_fee:.2f}")

        # Actualizar ingresos
        with self.lock:
            self.daily_revenue += parking_fee + customer.total_spent
            self.total_revenue += parking_fee + customer.total_spent
            del self.active_customers[customer_id]

    def calculate_parking_fee(self, vehicle, time_parked):
        """Calcula la tarifa de estacionamiento."""
        hours_parked = time_parked / SIMULATION_HOUR
        rate = 4 if vehicle.vehicle_type == "electric" else 2  # Double the rates
        base_fee = rate * hours_parked

        if hours_parked >= 25:
            self.towed_vehicles.append(vehicle)
            return base_fee * 1.5  # 50% penalty (increased from 25%)
        return base_fee

    def calculate_hourly_expenses(self):
        """Calculate hourly operating expenses"""
        hourly_expenses = 100  # Base operating cost
        self.daily_expenses += hourly_expenses
        return hourly_expenses

    def process_payment(self, amount, payment_type="revenue"):
        """Process a payment, updating both daily and total metrics"""
        if payment_type == "revenue":
            self.daily_revenue += amount
            self.balance += amount
        elif payment_type == "expense":
            self.daily_expenses += amount
            self.balance -= amount

    def reset_daily_stats(self):
        """Reset daily statistics while preserving totals"""
        # Get top performers before reset
        top_restaurant = max(self.restaurant_manager.restaurants.items(), 
            key=lambda x: x[1]['daily_revenue'])
        top_shop = max(self.shop_manager.shops.items(), 
            key=lambda x: x[1]['daily_revenue'])

        # Save to CSV
        with open('mall_stats.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.current_day,
                f"{self.daily_revenue:.2f}",
                f"{self.daily_expenses:.2f}",
                self.daily_customer_count,
                self.daily_incidents,
                self.daily_failed_attempts,
                self.cinema.current_movie.value,
                f"{top_restaurant[0].value}: ${top_restaurant[1]['daily_revenue']:.2f}",
                f"{top_shop[0].display_name}: ${top_shop[1]['daily_revenue']:.2f}"
            ])

        # Accumulate daily values into totals
        self.total_revenue += self.daily_revenue
        self.total_expenses += self.daily_expenses
        
        # Increment day counter
        self.current_day += 1
        print(f"\n=== New Day {self.current_day} ===")
        
        # Reset daily counters
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.daily_customer_count = 0
        self.daily_failed_attempts = 0
        self.daily_incidents = 0
        self.day_start_time = time.time()

    def display_mall_status(self):
        """Muestra el estado actual del centro comercial."""
        print("\n=== MALL STATUS ===")

        # Estado financiero
        print(f"\nFinancial Status:")
        print(f"Daily Revenue: ${self.daily_revenue:.2f}")
        print(f"Total Revenue: ${self.total_revenue:.2f}")
        print(f"Current Balance: ${self.balance:.2f}")

        # Estadsticas de clientes
        print(f"\nCustomer Statistics:")
        print(f"Daily Customers: {self.daily_customer_count}")
        print(f"Total Customers: {self.customer_count}")
        print(f"Failed Parking Attempts Today: {self.daily_failed_attempts}")
        print(f"Total Failed Attempts: {self.failed_parking_attempts}")

        # Estado del parking
        occupied_spots = sum(1 for level in self.parking_lot.parking_structure
                             for spot in level if spot is not None)
        total_spots = self.parking_lot.levels * self.parking_lot.spaces_per_level
        print(f"\nParking Status:")
        print(f"Occupied Spots: {occupied_spots}/{total_spots}")
        print(f"Inaccessible Levels: {list(self.parking_lot.inaccessible_levels)}")

        # Estado de las tiendas
        print("\nShop Status:")
        for shop in Shop:
            print(f"{shop.display_name}:")
            print(f"  Daily Revenue: ${self.shop_manager.shops[shop]['daily_revenue']:.2f}")
            print(f"  Daily Customers: {self.shop_manager.shops[shop]['daily_customers']}")

        # Estado de los restaurantes
        print("\nRestaurant Status:")
        for restaurant in Restaurant:
            rest_data = self.restaurant_manager.restaurants[restaurant]
            print(f"{restaurant.value}:")
            print(f"  Occupied Tables: {rest_data['occupied']}/{rest_data['capacity']}")
            print(f"  Daily Revenue: ${rest_data['daily_revenue']:.2f}")
            print(f"  Daily Customers: {rest_data['daily_customers']}")

        # Estado del cine
        print("\nCinema Status:")
        print(f"Current Movie: {self.cinema.current_movie.value if self.cinema.current_movie else 'None'}")
        occupied_seats = sum(1 for seat in self.cinema.seats if seat is not None)
        print(f"Occupied Seats: {occupied_seats}/{self.cinema.capacity}")
        print(f"Daily Revenue: ${self.cinema.daily_revenue:.2f}")
        print(f"Daily Customers: {self.cinema.daily_customers}")

        # Incidentes
        if self.incident_log:
            print("\nRecent Incidents:")
            for incident in self.incident_log[-5:]:  # Mostrar los últimos 5 incidentes
                print(f"- {incident}")

    def __del__(self):
        """Cleanup thread pool on deletion"""
        if hasattr(self, 'customer_executor'):
            self.customer_executor.shutdown(wait=True)

def run_mall_simulation():
    """Main function to run the mall simulation."""
    mall = MallManager()
    
    def on_closing():
        """Handle window closing event"""
        # Save final stats before closing
        mall.reset_daily_stats()  # This will save to CSV
        mall.root.destroy()
        os._exit(0)  # Force exit all threads
    
    # Start simulation in background thread
    simulation_thread = threading.Thread(target=run_simulation_loop, args=(mall,), daemon=True)
    simulation_thread.start()
    
    # Run GUI on main thread
    mall.start_gui()
    mall.root.protocol("WM_DELETE_WINDOW", on_closing)  # Bind closing event
    mall.root.mainloop()

def run_simulation_loop(mall):
    """Separate function to run the simulation loop"""
    try:
        last_display_time = time.time()
        last_movie_change = time.time()
        last_expense_calculation = time.time()
        day_start_time = time.time()
        last_customer_time = time.time()
        
        while True:
            current_time = time.time()
            hour_of_day = ((current_time - day_start_time) / SIMULATION_HOUR) % 24
            
            # More detailed arrival rates throughout the day
            if 7 <= hour_of_day < 9:  # Early morning commuters
                arrival_rate = 0.5
            elif 9 <= hour_of_day < 11:  # Morning shopping
                arrival_rate = 0.92
            elif 11 <= hour_of_day < 14:  # Lunch rush
                arrival_rate = 0.75
            elif 14 <= hour_of_day < 16:  # Early afternoon
                arrival_rate = 0.6
            elif 16 <= hour_of_day < 19:  # After work/school rush
                arrival_rate = 1.1  # Peak time
            elif 19 <= hour_of_day < 21:  # Dinner time
                arrival_rate = 0.9
            elif 21 <= hour_of_day < 23:  # Late evening
                arrival_rate = 0.5
            elif 23 <= hour_of_day < 24:  # Last hour
                arrival_rate = 0.3
            else:  # Early morning (0-7)
                arrival_rate = 0.1
            
            # Check for new customers more frequently
            if current_time - last_customer_time >= 0.3:  # Reduced from 0.5
                if random.random() < arrival_rate:
                    mall.process_new_customer()
                last_customer_time = current_time

            # Check for incidents
            incidents, total_cost = mall.parking_lot.check_for_incidents()
            if incidents:
                mall.incident_log.extend(incidents)
                mall.daily_incidents += len(incidents)
                mall.total_incidents += len(incidents)
                mall.balance -= total_cost

            # Change movie every 3 simulated hours
            if current_time - last_movie_change >= 3 * SIMULATION_HOUR:
                mall.cinema.set_next_movie()
                last_movie_change = current_time

            # Calculate expenses every simulated hour
            if current_time - last_expense_calculation >= SIMULATION_HOUR:
                expenses = mall.calculate_hourly_expenses()
                mall.balance -= expenses
                last_expense_calculation = current_time

            # Reset daily stats every 24 simulated hours
            if current_time - day_start_time >= 24 * SIMULATION_HOUR:
                mall.reset_daily_stats()
                day_start_time = current_time

            time.sleep(0.1)

    except Exception as e:
        print(f"Simulation error: {e}")

if __name__ == "__main__":
    run_mall_simulation()