import tkinter as tk
from tkinter import ttk
import time

class ParkingVisualizer:
    """GUI window that displays real-time parking status and mall activities"""
    
    def __init__(self, mall_manager, simulation_hour, Restaurant):
        self.mall = mall_manager
        self.SIMULATION_HOUR = simulation_hour
        self.Restaurant = Restaurant
        self.root = None
        self.parking_labels = []
        self.setup_gui()

    def setup_gui(self):
        """Initialize the main GUI window and its components"""
        self.root = tk.Tk()
        self.root.title("Mall Parking Status")
        self.root.geometry("800x600")
        
        # Setup the three main sections
        self._setup_frames()
        self._setup_parking_grid()
        self.update_display()

    def _setup_frames(self):
        """Create the main sections of the GUI"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights to allow expansion
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Parking and Activity Info
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)  # Make activity log expandable
        self.left_frame.grid_rowconfigure(2, weight=1)  # Make incidents log expandable
        
        # Parking visualization section
        self.parking_frame = ttk.LabelFrame(self.left_frame, text="Parking Status", padding="5")
        self.parking_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Activity log (moved from right)
        self.log_frame = ttk.LabelFrame(self.left_frame, text="Recent Activities", padding="5")
        self.log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.activity_text = tk.Text(self.log_frame, width=40, height=10)
        self.activity_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Incidents log (moved from right)
        self.incidents_frame = ttk.LabelFrame(self.left_frame, text="Recent Incidents", padding="5")
        self.incidents_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.incidents_frame.grid_columnconfigure(0, weight=1)
        self.incidents_frame.grid_rowconfigure(0, weight=1)
        self.incidents_text = tk.Text(self.incidents_frame, width=40, height=5)
        self.incidents_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Parking rates info
        self.rates_frame = ttk.LabelFrame(self.left_frame, text="Parking Rates", padding="5")
        self.rates_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        self.rates_label = ttk.Label(self.rates_frame, text="Regular: $2/hour\nElectric: $4/hour\nPenalty (>24h): +50%")
        self.rates_label.grid(row=0, column=0)
        
        # Add clock display
        self.clock_frame = ttk.LabelFrame(self.left_frame, text="Mall Time", padding="5")
        self.clock_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        self.clock_label = ttk.Label(self.clock_frame, text="00:00", font=('Arial', 14))
        self.clock_label.grid(row=0, column=0)
        
        # Right side - Mall Status
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        # Current mall status
        self.status_frame = ttk.LabelFrame(self.right_frame, text="Mall Status", padding="5")
        self.status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.status_label = ttk.Label(self.status_frame, text="")
        self.status_label.grid(row=0, column=0)

    def _setup_parking_grid(self):
        """Create the visual grid representing parking spots"""
        for level in range(self.mall.parking_lot.levels):
            level_frame = ttk.Frame(self.parking_frame)
            level_frame.grid(row=level, column=0, sticky=(tk.W, tk.E))
            
            # Add level label (e.g., "Level -1")
            level_label = ttk.Label(level_frame, text=f"Level {self.mall.parking_lot.get_level_name(level)}")
            level_label.grid(row=0, column=0, padx=5)
            
            # Create spots for this level
            level_spots = []
            for spot in range(self.mall.parking_lot.spaces_per_level):
                spot_label = ttk.Label(level_frame, width=3, relief="solid")
                spot_label.grid(row=0, column=spot+1, padx=1, pady=1)
                level_spots.append(spot_label)
            self.parking_labels.append(level_spots)

    def update_display(self):
        """Update all display elements with current mall status"""
        self._update_parking_spots()
        self._update_activity_log()
        self._update_summary()
        # Schedule next update
        self.root.after(1000, self.update_display)

    def _update_parking_spots(self):
        """Update the visual state of each parking spot"""
        for level in range(self.mall.parking_lot.levels):
            for spot in range(self.mall.parking_lot.spaces_per_level):
                label = self.parking_labels[level][spot]
                self._update_spot_display(label, level, spot)

    def _update_spot_display(self, label, level, spot):
        """Update individual parking spot display"""
        if level in self.mall.parking_lot.inaccessible_levels.keys():
            label.configure(text="~~~", background="blue")  # Flooded
        elif (level, spot) in self.mall.parking_lot.blocked_spots:
            label.configure(text="XXX", background="red")   # Blocked
        elif level == 4 and spot < 4:  # Electric spots
            vehicle = self.mall.parking_lot.parking_structure[level][spot]
            if vehicle is None:
                label.configure(text="E", background="yellow")  # Empty electric spot
            else:
                label.configure(text="⚡", background="green")  # Occupied electric spot
        else:  # Regular spots
            vehicle = self.mall.parking_lot.parking_structure[level][spot]
            if vehicle is None:
                label.configure(text="___", background="white")  # Empty regular spot
            else:
                text = "⚡" if vehicle.vehicle_type == "electric" else "CAR"
                label.configure(text=text, background="gray")    # Occupied regular spot

    def _update_activity_log(self):
        """Update the activity log with recent events"""
        self.activity_text.delete(1.0, tk.END)
        recent_activities = self._get_recent_activities()
        for activity in recent_activities[-10:]:  # Show last 10 activities
            self.activity_text.insert(tk.END, f"{activity}\n")

    def _get_recent_activities(self):
        """Get sorted list of recent activities"""
        activities = []
        for customer_data in self.mall.active_customers.values():
            activities.extend(customer_data['customer'].activity_log)
        return sorted(activities, key=lambda x: x.split(']')[0])

    def _update_summary(self):
        """Update mall status information"""
        # Financial summary
        occupied = sum(1 for level in self.mall.parking_lot.parking_structure 
                      for spot in level if spot is not None)
        
        # Cinema status
        cinema_occupied = sum(1 for seat in self.mall.cinema.seats if seat is not None)
        current_movie = self.mall.cinema.current_movie.value if self.mall.cinema.current_movie else "None"
        
        # Calculate current time
        current_time = time.time()
        day_start = self.mall.day_start_time
        hour_of_day = ((current_time - day_start) / self.SIMULATION_HOUR) % 24
        minutes = (hour_of_day * 60) % 60
        
        # Update clock
        self.clock_label.configure(text=f"{int(hour_of_day):02d}:{int(minutes):02d}")
        
        status_text = (
            f"=== DAY {self.mall.current_day} ===\n\n"
            f"=== FINANCIAL ===\n"
            f"Daily Revenue: ${self.mall.daily_revenue:.2f}\n"
            f"Daily Expenses: ${self.mall.daily_expenses:.2f}\n"
            f"Daily Net: ${(self.mall.daily_revenue - self.mall.daily_expenses):.2f}\n"
            f"Total Revenue: ${self.mall.total_revenue:.2f}\n"
            f"Total Expenses: ${self.mall.total_expenses:.2f}\n"
            f"Total Net: ${(self.mall.total_revenue - self.mall.total_expenses):.2f}\n"
            f"Current Balance: ${self.mall.balance:.2f}\n\n"
            f"=== CUSTOMERS ===\n"
            f"Currently Active: {len(self.mall.active_customers)}\n"
            f"Total Today: {self.mall.daily_customer_count}\n"
            f"Total All-Time: {self.mall.customer_count}\n\n"
            f"=== PARKING ({occupied}/{self.mall.parking_lot.levels * self.mall.parking_lot.spaces_per_level}) ===\n"
            f"Failed Attempts: {self.mall.daily_failed_attempts}\n\n"
            f"=== RESTAURANTS ===\n"
        )
        
        # Add restaurant information
        for restaurant in self.Restaurant:
            restaurant_data = self.mall.restaurant_manager.restaurants[restaurant]
            status_text += (f"{restaurant.value}: "
                           f"${restaurant_data['daily_revenue']:.2f} "
                           f"({restaurant_data['occupied']}/{restaurant_data['capacity']} seats)\n")
        
        # Add cinema information
        status_text += f"\n=== CINEMA ===\n"
        status_text += (f"Current Movie: {self.mall.cinema.current_movie.value}\n"
                       f"Occupied Seats: {sum(1 for seat in self.mall.cinema.seats if seat is not None)}/{self.mall.cinema.capacity}\n"
                       f"Daily Revenue: ${self.mall.cinema.daily_revenue:.2f}\n")

        # Add shop information
        status_text += f"\n=== SHOPS ===\n"
        for shop in self.mall.shop_manager.shops:
            shop_data = self.mall.shop_manager.shops[shop]
            status_text += f"{shop.display_name}: ${shop_data['daily_revenue']:.2f}\n"
        
        self.status_label.configure(text=status_text)
        
        # Update incidents log
        self.incidents_text.delete(1.0, tk.END)
        for incident in self.mall.incident_log[-5:]:  # Show last 5 incidents
            self.incidents_text.insert(tk.END, f"{incident['message']} (Cost: ${incident['cost']:.2f})\n")
        
        # Update incidents log
        self.incidents_text.delete(1.0, tk.END)
        for incident in self.mall.incident_log[-5:]:  # Show last 5 incidents
            self.incidents_text.insert(tk.END, f"{incident['message']} (Cost: ${incident['cost']:.2f})\n")