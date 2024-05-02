import math 
from scapy.all import *
import math


def process_pcap(file_path):
    # Load the pcap file
    packets = rdpcap(file_path)

    # Initialize variables
    time_intervals = {}
    interval_size = 0.01  # 100th of a second
    start_time = packets[0].time

    # Process each packet
    for packet in packets:
        timestamp = packet.time
        elapsed_time = timestamp - start_time
        interval_index = math.floor(elapsed_time / interval_size) * interval_size
        
        # Calculate packet size in bits
        packet_size = len(packet) * 8

        # Add bits to the correct interval
        if interval_index in time_intervals:
            time_intervals[interval_index] += packet_size
        else:
            time_intervals[interval_index] = packet_size

    # Normalize the list to fill gaps
    max_interval = max(time_intervals.keys())
    num_intervals = int(max_interval / interval_size) + 1
    bit_counts = []
    for i in range(num_intervals):
        interval_key = math.floor(i * interval_size)  # rounding to match keys
        bit_counts.append(time_intervals.get(interval_key, 0))

    return bit_counts


file_paths = ["tcp1.pcap","tcp2.pcap", "tcp3.pcap", "tcp4.pcap", "tcp5.pcap",
              "mptcp1.pcap", "mptcp2.pcap", "mptcp3.pcap", "mptcp4.pcap", "mptcp5.pcap",
              "mptcp_h1.pcap","mptcp_h2.pcap","mptcp_h3.pcap","mptcp_h4.pcap","mptcp_h5.pcap",
              "quic1.pcap", "quic2.pcap", "quic3.pcap", "quic4.pcap", "quic5.pcap",
              "mpquic1.pcap", "mpquic2.pcap", "mpquic3.pcap", "mpquic4.pcap", "mpquic5.pcap",
              "mpquic_h1.pcap", "mpquic_h2.pcap", "mpquic_h3.pcap", "mpquic_h4.pcap", "mpquic_h5.pcap"]

output_paths = ["tcp1.txt","tcp2.txt", "tcp3.txt", "tcp4.txt", "tcp5.txt",
              "mptcp1.txt", "mptcp2.txt", "mptcp3.txt", "mptcp4.txt", "mptcp5.txt",
              "mptcp_h1.txt","mptcp_h2.txt","mptcp_h3.txt","mptcp_h4.txt","mptcp_h5.txt",
              "quic1.txt", "quic2.txt", "quic3.txt", "quic4.txt", "quic5.txt",
              "mpquic1.txt", "mpquic2.txt", "mpquic3.txt", "mpquic4.txt", "mpquic5.txt",
              "mpquic_h1.txt", "mpquic_h2.txt", "mpquic_h3.txt", "mpquic_h4.txt", "mpquic_h5.txt"]

for i in range(len(file_paths)):
    file_path = "updated_pcaps/"+file_paths[i]
    
    bits_per_hundredth_second = process_pcap(file_path)
    mmlink_values = []
    ms = 1
    total_sent = 0
    for bits in bits_per_hundredth_second:
        mmlink_packets_to_send = round(bits/12000) 
        total_sent += mmlink_packets_to_send * 12000
        sent_in_this_hundredth = 0
        current_mmlink_values = []
        index = 0
        while(sent_in_this_hundredth < mmlink_packets_to_send):
            current_mmlink_values += [ms+index]
            if index == 9:
                index = 0
            sent_in_this_hundredth += 1
            index += 1
        current_mmlink_values.sort()
        mmlink_values += current_mmlink_values
        if current_mmlink_values:
            ms = max(current_mmlink_values)
        ms += 10    
        
    output_file ="updated_traces3/"+ output_paths[i]
    with open(output_file, 'w') as file:
        for value in mmlink_values:
            file.write(f"{value}\n")

    print(total_sent)



