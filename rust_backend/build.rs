fn main() {
    // Point to Npcap SDK lib directory
    println!("cargo:rustc-link-search=native=C:\\npcap-sdk\\Lib\\ARM64");
    // Link against wpcap instead of pcap
    println!("cargo:rustc-link-lib=wpcap");
}