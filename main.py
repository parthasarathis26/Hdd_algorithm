import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

class DiskSchedulingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Disk Scheduling Algorithms")
        self.master.geometry("600x600")

        # Create the UI
        self.create_ui()

        # Initialize variables to store algorithm results
        self.algorithm_results = {}

    def create_ui(self):
        # Heading
        tk.Label(self.master, text="Disk Scheduling Algorithms", font='Arial 20 bold').pack(pady=10)

        # Input fields
        tk.Label(self.master, text="Disk Requests (comma-separated):").pack(pady=5)
        self.requests_entry = tk.Entry(self.master, width=50)
        self.requests_entry.pack(pady=5)

        tk.Label(self.master, text="Initial Head Position:").pack(pady=5)
        self.head_entry = tk.Entry(self.master, width=10)
        self.head_entry.pack(pady=5)

        tk.Label(self.master, text="Previous Request:").pack(pady=5)
        self.previous_request_entry = tk.Entry(self.master, width=10)
        self.previous_request_entry.pack(pady=5)

        tk.Label(self.master, text="Disk Size (Number of Cylinders):").pack(pady=5)
        self.disk_size_entry = tk.Entry(self.master, width=10)
        self.disk_size_entry.pack(pady=5)

        # Algorithm selection
        self.algorithm = tk.StringVar()
        self.algorithm.set("FCFS")

        tk.Label(self.master, text="Select Algorithm:").pack(pady=10)
        algorithms = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
        for algo in algorithms:
            tk.Radiobutton(self.master, text=algo, variable=self.algorithm, value=algo).pack(pady=10)

        # Calculate Button
        tk.Button(self.master, text="Calculate", command=self.calculate).pack(pady=10)

        # Result Label
        self.result_label = tk.Label(self.master, text="", font='Arial 15')
        self.result_label.pack(pady=10)

        # Plot Button
        tk.Button(self.master, text="Plot Results", command=self.plot_results).pack(pady=10)

    def calculate(self):
        try:
            # Get inputs
            requests = list(map(int, self.requests_entry.get().split(',')))
            head_position = int(self.head_entry.get())
            previous_request = int(self.previous_request_entry.get())
            disk_size = int(self.disk_size_entry.get())

            # Ensure requests are valid
            if any(req < 0 or req >= disk_size for req in requests):
                raise ValueError("Disk requests must be within the range of disk size.")

            # Select algorithm
            algorithm = self.algorithm.get()
            if algorithm == "FCFS":
                result, sequence = self.fcfs(requests, head_position)
            elif algorithm == "SSTF":
                result, sequence = self.sstf(requests, head_position)
            elif algorithm == "SCAN":
                result, sequence = self.scan(requests, head_position, previous_request, disk_size)
            elif algorithm == "C-SCAN":
                result, sequence = self.cscan(requests, head_position, previous_request, disk_size)
            elif algorithm == "LOOK":
                result, sequence = self.look(requests, head_position, previous_request)
            elif algorithm == "C-LOOK":
                result, sequence = self.clook(requests, head_position, previous_request)

            # Store result and sequence
            self.algorithm_results[algorithm] = (result, sequence)

            # Display result
            self.result_label.config(text=f"Total Head Movements: {result}")

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_results(self):
        if not self.algorithm_results:
            messagebox.showwarning("No Results", "Please calculate results first.")
            return

        algorithm = self.algorithm.get()
        if algorithm not in self.algorithm_results:
            messagebox.showwarning("No Results", f"No results for the {algorithm} algorithm.")
            return

        # Get the sequence of serviced requests
        result, sequence = self.algorithm_results[algorithm]

        plt.figure(figsize=(10, 6))
        plt.plot(sequence, marker='o', linestyle='-', color='blue')
        plt.title(f'{algorithm} Disk Scheduling')
        plt.xlabel('Sequence of Service')
        plt.ylabel('Cylinder Number')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # Disk scheduling algorithm implementations
    def fcfs(self, requests, head_position):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        for req in requests:
            total_movement += abs(current_position - req)
            current_position = req
            sequence.append(req)
        return total_movement, sequence

    def sstf(self, requests, head_position):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        requests = sorted(requests)
        while requests:
            closest_request = min(requests, key=lambda x: abs(x - current_position))
            total_movement += abs(current_position - closest_request)
            current_position = closest_request
            sequence.append(closest_request)
            requests.remove(closest_request)
        return total_movement, sequence

    def scan(self, requests, head_position, previous_request, disk_size):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        sorted_requests = sorted(requests)

        direction = 'up' if previous_request < head_position else 'down'

        left = [r for r in sorted_requests if r < current_position]
        right = [r for r in sorted_requests if r >= current_position]

        if direction == 'up':
            sequence.extend(right)
            total_movement += self.service_requests(current_position, right)
            current_position = right[-1] if right else current_position
            total_movement += abs(current_position - (disk_size - 1))
            sequence.append(disk_size - 1)
            current_position = disk_size - 1
            if left:
                sequence.extend(left[::-1])
                total_movement += abs(current_position - left[-1])
                total_movement += self.service_requests(left[-1], left[::-1])
        else:
            sequence.extend(left[::-1])
            total_movement += self.service_requests(current_position, left[::-1])
            current_position = left[0] if left else current_position
            total_movement += abs(current_position - 0)
            sequence.append(0)
            current_position = 0
            if right:
                sequence.extend(right)
                total_movement += abs(current_position - right[0])
                total_movement += self.service_requests(right[0], right)

        return total_movement, sequence

    def cscan(self, requests, head_position, previous_request, disk_size):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        sorted_requests = sorted(requests)

        direction = 'up' if previous_request < head_position else 'down'

        if direction == 'up':
            right = [r for r in sorted_requests if r >= current_position]
            sequence.extend(right)
            total_movement += self.service_requests(current_position, right)
            current_position = right[-1] if right else current_position
            total_movement += abs(current_position - (disk_size - 1))
            sequence.append(disk_size - 1)
            current_position = disk_size - 1
            total_movement += current_position
            sequence.append(0)
            current_position = 0
            left = [r for r in sorted_requests if r < head_position]
            sequence.extend(left)
            if left:
                total_movement += self.service_requests(current_position, left)
                current_position = left[-1]
        else:
            left = [r for r in sorted_requests if r < current_position]
            sequence.extend(left[::-1])
            total_movement += self.service_requests(current_position, left[::-1])
            current_position = left[0] if left else current_position
            total_movement += abs(current_position - 0)
            sequence.append(0)
            current_position = 0
            total_movement += disk_size - 1
            sequence.append(disk_size - 1)
            current_position = disk_size - 1
            right = [r for r in sorted_requests if r >= head_position]
            sequence.extend(right[::-1])
            if right:
                total_movement += self.service_requests(current_position, right[::-1])
                current_position = right[0]

        return total_movement, sequence

    def look(self, requests, head_position, previous_request):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        sorted_requests = sorted(requests)

        direction = 'up' if previous_request < head_position else 'down'

        if direction == 'up':
            right = [r for r in sorted_requests if r >= current_position]
            sequence.extend(right)
            total_movement += self.service_requests(current_position, right)
            current_position = right[-1] if right else current_position
            left = [r for r in sorted_requests if r < current_position]
            sequence.extend(left[::-1])
            if left:
                total_movement += abs(current_position - left[-1])
                total_movement += self.service_requests(left[-1], left[::-1])
        else:
            left = [r for r in sorted_requests if r < current_position]
            sequence.extend(left[::-1])
            total_movement += self.service_requests(current_position, left[::-1])
            current_position = left[0] if left else current_position
            right = [r for r in sorted_requests if r >= current_position]
            sequence.extend(right)
            if right:
                total_movement += abs(current_position - right[0])
                total_movement += self.service_requests(right[0], right)

        return total_movement, sequence

    def clook(self, requests, head_position, previous_request):
        total_movement = 0
        current_position = head_position
        sequence = [head_position]
        sorted_requests = sorted(requests)

        # Determine the direction based on the previous request
        direction = 'up' if previous_request < head_position else 'down'

        if direction == 'up':
            # Service the right side first
            right = [r for r in sorted_requests if r >= current_position]
            if right:
                sequence.extend(right)  # Add the right side requests to the sequence
                total_movement += self.service_requests(current_position, right)
                current_position = right[-1]  # Update current position to the last serviced request

            # Move to the smallest request and continue servicing the right side
            left = [r for r in sorted_requests if r < head_position]
            if left:
                total_movement += abs(current_position - left[0])
                sequence.append(left[0])  # Add the move to the smallest request to the sequence
                sequence.extend(left)  # Add the left side requests to the sequence
                total_movement += self.service_requests(left[0], left)
        else:
            # Service the left side first
            left = [r for r in sorted_requests if r < current_position]
            if left:
                sequence.extend(left[::-1])  # Add the left side requests to the sequence in reverse order
                total_movement += self.service_requests(current_position, left[::-1])
                current_position = left[0]  # Update current position to the last serviced request

            # Move to the largest request and continue servicing the left side
            right = [r for r in sorted_requests if r >= head_position]
            if right:
                total_movement += abs(current_position - right[-1])
                sequence.append(right[-1])  # Add the move to the largest request to the sequence
                sequence.extend(right[::-1])  # Add the right side requests to the sequence in reverse order
                total_movement += self.service_requests(right[-1], right[::-1])

        return total_movement, sequence


    

    def service_requests(self, start, requests):
        total = 0
        current = start
        for req in requests:
            total += abs(current - req)
            current = req
        return total

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulingApp(root)
    root.mainloop()
