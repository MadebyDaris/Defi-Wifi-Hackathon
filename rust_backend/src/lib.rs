use serde::{Deserialize, Serialize};
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::ptr;
use std::time::{self, Instant};

mod androidsniffer;

#[no_mangle]

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    fn test_calculate_wifi_distance() {
        // Test with a known signal level and frequency
        let distance = calculate_wifi_distance(-60, 2400.0);
        assert!(distance > 0.0);
    }

    #[test]
    fn test_scan_wifi_desktop() {
        // This test will scan for Wi-Fi networks and check if the result is Ok
        let start_time = Instant::now();
        let result = scan_wifi_desktop(start_time);
        assert!(result.is_ok());
    }
}


#[unsafe(no_mangle)]
pub extern "C" fn rust_hello() -> *const std::os::raw::c_char {
    let msg = std::ffi::CString::new("Hello from Rust!").unwrap();
    match CString::new(msg) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => ptr::null_mut(),
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WiFiNetwork {
    pub ssid: String,
    pub mac: String,
    pub channel: String,
    pub signal_level: i32,
    pub timestamp: u64,
    pub security: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ScanResult {
    pub networks: Vec<WiFiNetwork>,
    pub scan_time: u64,
    pub error: Option<String>,
}

/// function to free memory allocated.
#[no_mangle]
pub extern "C" fn free_rust_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe {
            let _ = CString::from_raw(ptr);
        }
    }
}

fn wifiScan() -> ScanResult {
    let time_start = Instant::now();
    #[cfg(target_os = "android")]
    {
        // Android-specific WiFi scanning

        use crate::androidsniffer::scan_wifi_android;
        scan_wifi_android()
    }

    #[cfg(any(target_os = "linux", target_os = "macos", target_os = "windows"))]
    {
        // Desktop WiFi scanning using wifi-scanner crate
        match scan_wifi_desktop(time_start) {
            Ok(networks) => ScanResult {
                networks,
                scan_time: time_start.elapsed().as_secs(),
                error: None,
            },
            Err(e) => ScanResult {
                networks: vec![],
                scan_time: time_start.elapsed().as_secs(),
                error: Some(format!("Scan failed: {}", e)),
            }
        }
    }
}

pub fn calculate_wifi_distance(signal_dbm: i32, frequency_mhz: f64) -> f64 {
    const TRANSMIT_POWER_DBM: f64 = 23.0;
    let path_loss = TRANSMIT_POWER_DBM - signal_dbm as f64;
    
    // FSPL formula: d = 10^((PL - 27.55 - 20*log10(f))/20)
    let exponent = (path_loss - 27.55 - (20.0 * frequency_mhz.log10())) / 20.0;
    10.0_f64.powf(exponent)
}

#[cfg(any(target_os = "linux", target_os = "macos", target_os = "windows"))]
fn scan_wifi_desktop(time_start: Instant) -> Result<Vec<WiFiNetwork>, Box<dyn std::error::Error>> {
    let scan = wifiscanner::scan().unwrap();
    let scan_time = Instant::now();
    let timestamp = scan_time.duration_since(time_start).as_secs();

    let mut networks = scan.iter().map(|network| {
        WiFiNetwork {
            ssid: network.ssid.clone(),
            mac: network.mac.to_string(),
            channel: network.channel.to_string(),
            signal_level: network.signal_level.parse().unwrap(),
            timestamp: timestamp,
            security: network.security.to_string(),
        }
    }).collect::<Vec<WiFiNetwork>>();
    return Ok(networks);
}