# Mall Parking & Operations Simulator

A comprehensive multi-threaded simulation of a shopping mall's operations, including parking management, retail activities, and incident handling. Built with Python using threading for parallel processing and Tkinter for real-time visualization.

## 🎯 Project Overview

This simulator models a complex mall environment with:
- Multi-level parking system with dedicated electric vehicle spots
- Real-time business operations (shops, restaurants, cinema)
- Dynamic customer behavior and activity patterns
- Incident management system (flooding, collisions, maintenance)
- Financial tracking and reporting
- Live GUI visualization

## 🚀 Key Features

### Parking Management
- 5 levels with 10 spaces each
- Dedicated EV charging spots
- Different pricing for regular and electric vehicles
- Incident handling (flooding, collisions, light malfunctions)
- Smart spot allocation system

### Business Operations
- Multiple shops with varying price ranges
- Restaurant system with capacity management
- Cinema with movie scheduling
- Dynamic pricing and revenue tracking

### Customer Simulation
- Realistic customer behavior patterns
- Multiple activity sequences
- Time-based arrival rates
- Vehicle type distribution (electric vs. gasoline)

### Real-time Visualization
- Live parking grid display
- Financial metrics dashboard
- Activity and incident logs
- Business status monitoring

## 🔧 Technical Implementation

### Parallel Processing
The simulation leverages Python's threading module to handle multiple concurrent operations:
- Customer activity simulation
- Incident monitoring
- Business operations
- GUI updates

### Key Classes
- `MallManager`: Central coordinator for all operations
- `ParkingLot`: Manages parking infrastructure and incidents
- `Vehicle` & `Customer`: Base entities for simulation
- `ParkingVisualizer`: GUI implementation
- Various business managers (Shop, Restaurant, Cinema)

### Synchronization
- Thread-safe operations using `threading.Lock()`
- Atomic transactions for financial operations
- Coordinated resource management

## 📊 Data Structures
- Nested lists for parking structure
- Dictionaries for active customers and business tracking
- Enums for activity types and business categories
- Queue-like structures for incident logging

## 🛠 Requirements

- Python 3.7+
- tkinter (usually comes with Python)
- Basic packages: threading, time, random, enum

## 📈 Simulation Parameters

You can modify various simulation parameters in `ULTIMATE.py`:
- `SIMULATION_HOUR`: Time scale (default: 2.5 seconds = 1 simulated hour)
- `DISPLAY_INTERVAL`: Update frequency for statistics
- Parking capacity and pricing
- Business parameters (capacity, pricing, etc.)
- Incident probabilities

## 🎮 GUI Interface

The visualization includes:
- Real-time parking grid showing occupied/free spots
- Financial dashboard with revenue/expense tracking
- Activity log showing customer movements
- Incident tracker
- Business status indicators

## 📝 Project Structure

```
mall-simulator/
├── ULTIMATE.py           # Main simulation logic
├── parking_visualizer.py # GUI implementation
└── README.md            # Documentation
```

## 🤝 Contributing

This project was developed as part of a simulation and parallel computing class. Contributions are welcome! Please feel free to submit pull requests or open issues for improvements.

## 🎓 Educational Value

This project demonstrates several key concepts in simulation and parallel computing:
- Multi-threaded application design
- Resource management and synchronization
- Real-time data visualization
- Complex system modeling
- Event-driven programming

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Sofia Serantes
- Celia Sanmartin
- Clementine Mathieu
- Antonio Cabral
- Lucas Losantos 

## 🙏 Acknowledgments

- JOSE ANTONIO GARCÍA ESCANDÓN for guidance and support
- IE University Simulation and Parallel Computing Course

## 🚀 How to Run the Code

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually comes with Python installation)
- Git installed on your system

### Installation & Running
1. Clone the repository:
```bash
git clone https://github.com/lucaslosantos/mallsimulation.git
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install pandas numpy matplotlib seaborn
```

4. Run the main simulation:
```bash
python ULTIMATE.py
```

5. To view statistics (optional):
```bash
python view_stats.py
```

### Managing Dependencies
- The project uses a virtual environment to manage dependencies
- To save the current package state:
```bash
pip freeze > requirements.txt
```
- To install from requirements:
```bash
pip install -r requirements.txt
```

### Important Notes
- Don't commit the `venv` folder to version control
- The `venv` folder is already added to `.gitignore`
- Always activate the virtual environment before running the simulation
- To deactivate the virtual environment when done:
```bash
deactivate
```

### What to Expect
- A GUI window will open showing the mall simulation
- The parking grid shows real-time parking status:
  - White spaces: Empty regular spots
  - Yellow spaces: Empty EV spots
  - Gray spaces: Occupied regular spots
  - Green spaces with ⚡: Occupied EV spots
  - Blue spaces (~~~): Flooded level
  - Red spaces (XXX): Blocked spots
- The right panel shows financial metrics, customer counts, and business status
- Activity and incident logs update in real-time

### Troubleshooting
If you get a "No module named 'tkinter'" error:
- For Ubuntu/Debian: `sudo apt-get install python3-tk`
- For macOS: `brew install python-tk`
- For Windows: Reinstall Python and make sure to check "tcl/tk and IDLE" during installation

