import random
import json

# Configuration for dashboard data
num_racks = 46
levels_per_rack = 6
rows_per_level = 58

# Data structure for the dashboard
dashboard_data = {
    "Warehouse ID": "5BTG",
    "Rack Levels": []
}


# Function to calculate percentage
def calculate_percentage(used, total):
    return round((used / total) * 100, 2)


# Function to create rack level data
def create_rack_level_data(used_rows, total_rows):
    return {
        "Used Rows": used_rows,
        "Total Rows": total_rows,
        "Free Rows": total_rows - used_rows,
        "Used Percentage": calculate_percentage(used_rows, total_rows),
        "Free Percentage": calculate_percentage(total_rows - used_rows, total_rows)
    }


# Generate data for racks 1 to 46
for rack_no in range(1, num_racks + 1):
    rack_data = {
        "Rack No": rack_no,
        "Levels": []
    }
    for level_no in range(1, levels_per_rack + 1):
        if rack_no in range(1, 9) or rack_no == 11 or rack_no == 12:  # Racks 1-8, 11-20 are empty
            used_rows = 0
        elif rack_no == 9:
            used_rows = 45  # Example allocation for rack 9
        elif rack_no == 10:
            used_rows = 45  # Example allocation for rack 10
        elif rack_no == 21:
            used_rows = 40  # Example allocation for rack 21
        elif rack_no == 22:
            used_rows = 43  # Example allocation for rack 22
        else:
            used_rows = random.randint(0, rows_per_level)  # Random allocation for racks 23-46

        level_data = create_rack_level_data(used_rows, rows_per_level)
        rack_data["Levels"].append(level_data)

    dashboard_data["Rack Levels"].append(rack_data)

# Calculate the summary for the whole warehouse
total_rows = num_racks * levels_per_rack * rows_per_level
total_used = sum(level["Used Rows"] for rack in dashboard_data["Rack Levels"] for level in rack["Levels"])
total_free = total_rows - total_used
summary_data = {
    "Total Racks": num_racks,
    "Total Levels": num_racks * levels_per_rack,
    "Total Rows": total_rows,
    "Total Used Rows": total_used,
    "Total Free Rows": total_free,
    "Total Used": calculate_percentage(total_used, total_rows),
    "Total Free": calculate_percentage(total_free, total_rows)
}

# Add the summary to the dashboard data
dashboard_data["Summary"] = summary_data

# Convert the dashboard data to a JSON-formatted string for visualization
dashboard_data_string = json.dumps(dashboard_data, indent=4)

# Print the dashboard data
print(dashboard_data_string)
