import tkinter as tk
from tkinter import messagebox, ttk
import socket
import threading
from fpdf import FPDF
from datetime import datetime

class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Auto Port Scanner")
        self.root.geometry("500x550")

        # UI Elements
        tk.Label(root, text="Target IP/Domain:", font=("Arial", 12)).pack(pady=10)
        self.target_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.target_entry.pack()

        self.scan_btn = tk.Button(root, text="Start Scan", command=self.start_scan_thread, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.scan_btn.pack(pady=20)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Result Display Area
        self.result_area = tk.Text(root, height=15, width=55)
        self.result_area.pack(pady=10)

        self.open_ports = []

    def start_scan_thread(self):
        # Scan ko background thread mein chalana taaki GUI freeze na ho
        target = self.target_entry.get()
        if not target:
            messagebox.showerror("Error", "Please enter a target!")
            return
        
        self.result_area.delete('1.0', tk.END)
        self.open_ports = []
        threading.Thread(target=self.run_scanner, args=(target,), daemon=True).start()

    def run_scanner(self, target):
        self.result_area.insert(tk.END, f"Scanning started for {target}...\n")
        ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 443, 3306, 3389] # Common ports
        
        self.progress["maximum"] = len(ports_to_scan)
        
        for i, port in enumerate(ports_to_scan):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((target, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "Unknown"
                self.open_ports.append((port, service))
                self.result_area.insert(tk.END, f"[+] Port {port} is OPEN ({service})\n")
            
            self.progress["value"] = i + 1
            s.close()
        
        self.result_area.insert(tk.END, "\nScan Completed!")
        self.generate_report(target)

    def generate_report(self, target):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Port Scan Report", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Target: {target}", ln=True)
        pdf.cell(200, 10, txt=f"Time: {datetime.now()}", ln=True)
        pdf.ln(10)

        for port, svc in self.open_ports:
            pdf.cell(200, 10, txt=f"Port: {port} - Service: {svc}", ln=True)
        
        filename = f"report_{target.replace('.', '_')}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Success", f"Report saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerGUI(root)
    root.mainloop()
